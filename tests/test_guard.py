"""Guard behavior for recorded Claude Code and Codex hook payload shapes.

Tables exercise reserved commands, git policy, protected paths and profile errors.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
GUARD = ROOT / "plugins/workbench-core/scripts/guard.py"
TEMPLATE_DIRS = [ROOT / "plugins/workbench-core/profiles/templates", Path(__file__).parent / "fixtures/profiles"]
FIXTURES = Path(__file__).parent / "fixtures/hooks"
HEREDOC_SCRIPT = "cat > logs/run_x.sh <<'EOF'\nmpirun -np 4 SU2_CFD a.cfg\npytest\nEOF\nchmod +x logs/run_x.sh"


def make_repo(directory, template=None, frontmatter=None):
    directory.mkdir(parents=True, exist_ok=True)
    if template:
        source = next(d / f"{template}.yaml" for d in TEMPLATE_DIRS if (d / f"{template}.yaml").is_file())
        frontmatter = "".join(line for line in source.read_text().splitlines(True) if not line.startswith("#"))
    if frontmatter is not None:
        (directory / "AGENTS.md").write_text(f"---\n{frontmatter}---\n# Instructions\n")
    return directory


def run(fixture, repo, *, command=None, path=None, project_env=True, mode="pre-tool-use", env_extra=None, **fields):
    payload = json.loads((FIXTURES / fixture).read_text())
    payload["cwd"] = str(repo)
    tool_input = payload.get("tool_input", {})
    if command is not None:
        tool_input["command"] = command
    if path is not None:
        tool_input["notebook_path" if "notebook_path" in tool_input else "file_path"] = path
    tool_input.update(fields)
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
    env.update(env_extra or {})
    if project_env:
        env["CLAUDE_PROJECT_DIR"] = str(repo)
    done = subprocess.run([sys.executable, str(GUARD), mode], input=json.dumps(payload),
                          capture_output=True, text=True, env=env, timeout=30)
    assert done.returncode == 0, done.stderr
    return (json.loads(done.stdout)["hookSpecificOutput"] if done.stdout.strip() else None), done.stderr


def decision(output):
    return output.get("permissionDecision") if output else None


def check(failures, label, condition, detail=""):
    if not condition:
        failures.append(f"{label}: {detail}")


def test_reserved_commands_are_denied_with_hand_over_in_both_clients(tmp_path):
    solver = make_repo(tmp_path / "solver-project", "solver-project")
    commands = [
        "mpirun -np 4 python run/optimize.py cases/x/input/configs/opt_a.toml",
        "env OMP_NUM_THREADS=1 mpirun -np 4 SU2_CFD a.cfg",
        "$(bash tools/bind_cores.sh 4) mpirun -np 4 SU2_CFD a.cfg",
        "source activate.sh && pytest -q tests",
        "bash verify.sh --lane fast; python -m pytest",
        "bash -c 'cd cases && SU2_CFD a.cfg'",
        "timeout 600 bash verify.sh 4 --lane solver",
        "(cd cases/x && python ../../run/mesh.py a.toml)",
        "echo start && nohup python run/optimize.py a.toml > out.log 2>&1 &",
        "cat > a.txt <<EOF\nnotes\nEOF\nmpirun -np 2 SU2_CFD a.cfg",
    ]
    failures = []
    for fixture in ("claude-bash.json", "codex-bash.json"):
        for command in commands:
            output, _ = run(fixture, solver, command=command, project_env=fixture.startswith("claude"))
            reason = (output or {}).get("permissionDecisionReason", "")
            check(failures, f"{fixture} {command!r}", decision(output) == "deny"
                  and reason.startswith("Reserved for the user (") and reason.endswith(command), output)
    assert not failures, "\n".join(failures)


def test_ordinary_work_passes(tmp_path):
    solver = make_repo(tmp_path / "solver-project", "solver-project")
    failures = []
    for command in ["bash verify.sh --lane fast", "source activate.sh && bash verify.sh --lane fast --group derivatives",
                    "python tools/compare_revisions.py cfg --base HEAD~1 > logs/compare_cfg_x.txt",
                    "grep -rn mpirun src/ docs/", "rg 'SU2_CFD|pytest' docs", "echo 'mpirun -np 4 SU2_CFD a.cfg'",
                    "git log --oneline -5 --grep pytest", "git status && git diff --stat",
                    "ls cases/*/output 2>&1 | head", HEREDOC_SCRIPT]:
        output, stderr = run("claude-bash.json", solver, command=command)
        check(failures, repr(command), decision(output) is None, (output, stderr))
    output, _ = run("claude-edit.json", solver, path=str(solver / "src/simopt/solver/aero_comp_helpers.py"))
    check(failures, "ordinary edit", output is None, output)
    assert not failures, "\n".join(failures)


def test_git_writes_denied_only_in_the_profiled_repository(tmp_path):
    solver = make_repo(tmp_path / "solver-project", "solver-project")
    shadow = tmp_path / "shadow"
    shadow.mkdir()
    failures = []
    writes = ["git commit -m 'solver: fix'", "git add -A && git commit -F logs/commit_x.txt", "git push origin main",
              "git -c user.name=x tag v1", "git rm old.py", "git restore --staged a.py", "git checkout -- a.py",
              "git stash", "git branch -D old", "cd src && git commit -am x",
              f"(cd {shadow} && git commit -m x); git commit -m y"]
    for command in writes:
        output, _ = run("claude-bash.json", solver, command=command)
        reason = (output or {}).get("permissionDecisionReason", "")
        check(failures, f"write {command!r}", decision(output) == "deny" and reason.startswith(
            "Git is read-only for the agent in this repository.") and "logs/commit_<topic>.txt" in reason, output)
    for command in ["git tag -l", "git branch -a", "git stash list", "git restore a.py",
                    f"git -C {shadow} commit -F msg.txt", f"cd {shadow} && git apply --cached p.patch && git commit -F m"]:
        output, _ = run("claude-bash.json", solver, command=command)
        check(failures, f"allowed {command!r}", decision(output) is None, output)
    assert not failures, "\n".join(failures)


def test_frozen_and_read_only_paths_in_both_clients(tmp_path, monkeypatch):
    solver = make_repo(tmp_path / "solver-project", "solver-project")
    failures = []
    for fixture, path in [("claude-edit.json", "src/simopt/solver/aero_comp.py"),
                          ("claude-edit.json", "src/simopt/solver/standalone/run.py"),
                          ("claude-notebookedit.json", "docs/reference/solver_api.md")]:
        for target in (str(solver / path), path):
            output, _ = run(fixture, solver, path=target)
            reason = (output or {}).get("permissionDecisionReason", "")
            check(failures, f"{fixture} {target}", decision(output) == "deny" and "frozen" in reason
                  and "docs/decisions/" in reason, output)
    patch = "*** Begin Patch\n*** Update File: src/simopt/solver/builder.py\n@@\n-a\n+b\n*** End Patch\n"
    output, _ = run("codex-apply-patch.json", solver, command=patch, project_env=False)
    check(failures, "apply_patch frozen", decision(output) == "deny", output)
    patch = "*** Begin Patch\n*** Add File: src/simopt/new_module.py\n+x = 1\n*** End Patch\n"
    output, _ = run("codex-apply-patch.json", solver, command=patch, project_env=False)
    check(failures, "apply_patch ordinary", decision(output) is None, output)
    home = tmp_path / "home"
    other = make_repo(home / "projects/solver-project")
    surrogate = make_repo(home / "surrogate-project", "surrogate-project")
    monkeypatch.setenv("HOME", str(home))
    output, _ = run("claude-edit.json", surrogate, path=str(other / "src/x.py"))
    check(failures, "read-only path", decision(output) == "deny" and "read-only" in output["permissionDecisionReason"], output)
    assert not failures, "\n".join(failures)


def test_repository_specific_rules_from_each_profile(tmp_path, monkeypatch):
    failures = []
    adaptive_project = make_repo(tmp_path / "adaptive-project", "adaptive-project")
    output, _ = run("claude-bash.json", adaptive_project, command="python run/configAdaptive.py --threads 4 --iters 12")
    check(failures, "adaptive-project allowed note", decision(output) is None and "scratch copy only" in output["additionalContext"], output)
    for command in ["python run/configCase.py", "python -m tests.tools.bench"]:
        output, _ = run("claude-bash.json", adaptive_project, command=command)
        check(failures, f"adaptive-project {command}", decision(output) == "deny", output)
    output, _ = run("claude-bash.json", adaptive_project, command="python -m unittest discover tests")
    check(failures, "adaptive-project unittest", output is None, output)
    case_project = make_repo(tmp_path / "case-project", "case-project")
    for command in ["./hartmann", "cd cases/hunt && ./hunt 2> log", "bash -ic './shercliff'"]:
        output, _ = run("claude-bash.json", case_project, command=command)
        check(failures, f"case_project {command}", decision(output) == "deny", output)
    output, _ = run("claude-bash.json", case_project, command="bash -ic 'bash compile.sh'")
    check(failures, "case_project compile", decision(output) is None and "compile only" in output["additionalContext"], output)
    output, _ = run("claude-edit.json", case_project, path=str(case_project / "reference/hartmann.c"))
    check(failures, "case_project reference/", decision(output) == "deny", output)
    home = tmp_path / "home"
    make_repo(home / "projects/solver-project")
    surrogate = make_repo(home / "surrogate-project", "surrogate-project")
    monkeypatch.setenv("HOME", str(home))
    output, _ = run("claude-bash.json", surrogate, command="cd ~/projects/solver-project && bash verify.sh")
    check(failures, "surrogate cross-repo run", decision(output) == "deny", output)
    output, _ = run("claude-bash.json", surrogate, command="git commit -m x")
    check(failures, "surrogate git: none", output is None, output)
    experiment = make_repo(tmp_path / "experiment", "ml-project")
    output, _ = run("claude-bash.json", experiment, command='CUDA_VISIBLE_DEVICES="" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/pytest -q')
    check(failures, "experiment allowed with env", output is None, output)
    output, _ = run("claude-bash.json", experiment, command=".venv/bin/python scripts/pipelines/train.py --epochs 3")
    check(failures, "experiment training", decision(output) == "deny", output)
    assert not failures, "\n".join(failures)


def test_session_start_no_profile_malformed_profile_and_failures(tmp_path):
    failures = []
    adaptive_project = make_repo(tmp_path / "adaptive-project", "adaptive-project")
    output, _ = run("claude-session-start.json", adaptive_project, mode="session-start")
    text = (output or {}).get("additionalContext", "")
    check(failures, "session start", len(text) <= 1500 and "archetypes physics, code, research" in text
          and "source activate.sh" in text and "3 reserved command patterns" in text and "surgical-editor" in text
          and "# Instructions" not in text, text)
    plain = make_repo(tmp_path / "plain")
    for fixture, kwargs, mode in [("claude-bash.json", {"command": "mpirun -np 4 x"}, "pre-tool-use"),
                                  ("claude-edit.json", {"path": str(plain / "a.py")}, "pre-tool-use"),
                                  ("claude-session-start.json", {}, "session-start")]:
        output, stderr = run(fixture, plain, mode=mode, **kwargs)
        check(failures, f"no profile {fixture}", output is None and stderr == "", (output, stderr))
    broken = make_repo(tmp_path / "broken", frontmatter="workbench:\n  schema: 1\n  archetypes: [code]\n  gti: none\n")
    output, stderr = run("claude-bash.json", broken, command="mpirun -np 4 x")
    check(failures, "malformed allows", output is None and "unknown keys: gti" in stderr, (output, stderr))
    output, _ = run("claude-session-start.json", broken, mode="session-start")
    check(failures, "malformed reported", "guards are off" in (output or {}).get("additionalContext", ""), output)
    done = subprocess.run([sys.executable, str(GUARD), "pre-tool-use"], input="not json", capture_output=True,
                          text=True, env={**os.environ, "CLAUDE_PROJECT_DIR": str(adaptive_project)})
    check(failures, "internal failure allows", done.returncode == 0 and done.stdout == "" and "internal error" in done.stderr,
          done.stderr)
    assert not failures, "\n".join(failures)
