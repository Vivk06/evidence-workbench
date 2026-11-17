"""repo-setup detection and proposal on six repository shapes and two unknown repositories
(plan Phase 7, D20, D32): nothing is written without --apply, and applying is idempotent."""
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
SCRIPTS = ROOT / "plugins/workbench-core/scripts"
REPOS = Path(__file__).parent / "fixtures/repos"
_spec = importlib.util.spec_from_file_location("workbench_detect_repo", SCRIPTS / "detect_repo.py")
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)

# repo: (git, archetypes, extra plugins, environment, frozen candidates, warnings, renames)
EXPECTED = {
    "sim-optimizer": (True, ["physics", "code"], ["sim-validity"], "source activate.sh", [], 0, 0),
    "octree-mhd": (True, ["physics", "code", "research"], ["sim-validity", "research-writing"], None,
                   ["reference/", "docs/archive/"], 1, 1),
    "vision-ml": (True, ["code", "research"], ["ml-validity", "research-writing"], None, ["third_party/"], 0, 0),
    "surrogate": (False, ["code", "research"], ["research-writing"], ".venv/bin/python", [], 0, 0),
    "application": (False, ["research"], ["research-writing"], None, [], 0, 0),
    "mesh-adapt": (True, ["physics", "code"], ["sim-validity"], "source activate.sh", [], 0, 0),
    "web-app": (False, ["code"], [], None, [], 0, 0),
    "fortran-solver": (True, ["physics", "code"], ["sim-validity"], None, [], 1, 0),
}


def copy_repo(name, tmp_path):
    repo = shutil.copytree(REPOS / name, tmp_path / name)
    if EXPECTED[name][0]:
        (repo / ".git").mkdir()
    if name == "surrogate":
        (repo / ".venv/bin").mkdir(parents=True)
        (repo / ".venv/bin/python").write_text("")
    return repo


def test_detection_and_proposal_on_fixture_repositories(tmp_path):
    failures = []
    for name, (git, archetypes, plugins, environment, frozen, warnings, renames) in EXPECTED.items():
        found = D.detect(copy_repo(name, tmp_path))
        proposal = D.propose(found)
        profile = proposal["profile"]
        got = (found["git"], found["archetypes"], proposal["plugins"][1:], found["activation"] or found["python"],
               found["frozen_candidates"], len(found["warnings"]), len(found["renames"]))
        if got != (git, archetypes, plugins, environment, frozen, warnings, renames):
            failures.append(f"{name}: {got}")
        expected_git = found['existing_profile'].get('git', 'normal') if found['existing_profile'] else ('normal' if git else 'none')
        if proposal["plugins"][0] != "workbench-core" or profile["git"] != expected_git:
            failures.append(f"{name}: plugins or git mode {proposal['plugins']} {profile['git']}")
        if D.P.validate(D.P.parse_yaml(D.P.dump(profile))["workbench"]) != D.P.validate(dict(profile)):
            failures.append(f"{name}: profile does not round-trip")
    sim = D.propose(D.detect(tmp_path / "sim-optimizer"))["profile"]
    assert sim["authority"]["decisions"] == {"path": "docs/decisions/", "style": "append-only"}
    assert sim["authority"]["anti_patterns"]["id"] == "AP-N" and "test_budget" not in sim
    assert not D.propose(D.detect(tmp_path / "sim-optimizer"))["codex_rules"]
    existing = tmp_path / "sim-optimizer/AGENTS.md"
    existing.write_text("---\nworkbench:\n  schema: 1\n  archetypes: [physics, code]\n"
                        "  git: read-only\n  test_budget: {max: 9, paths: [tests]}\n"
                        "  user_executed:\n    - {pattern: 'mpirun', why: cluster job, codex_prefix: [[mpirun]]}\n---\n")
    preserved = D.propose(D.detect(existing.parent))
    assert preserved['profile']['git'] == 'read-only' and preserved['profile']['test_budget']['max'] == 9
    assert 'prefix_rule(pattern=[["mpirun"]], decision="forbidden"' in preserved['codex_rules'][0]
    assert D.propose(D.detect(tmp_path / "mesh-adapt"))["profile"]["code_graph"] == "graphify"
    assert D.propose(D.detect(tmp_path / "application"))["profile"]["claims_ledger"] == "universities/ETH/claims-ledger.csv"
    assert not failures, "\n".join(failures)


def test_diff_writes_nothing_apply_writes_proposal_and_is_idempotent(tmp_path):
    for name in ("octree-mhd", "web-app"):
        repo = copy_repo(name, tmp_path)
        before = {p: p.read_bytes() for p in repo.rglob("*") if p.is_file()}
        script = [sys.executable, str(SCRIPTS / "detect_repo.py"), str(repo)]
        diff = subprocess.run(script + ["--diff"], capture_output=True, text=True, check=True).stdout
        assert "+workbench:" in diff and "+++ b/.claude/settings.json" in diff, diff
        assert {p: p.read_bytes() for p in repo.rglob("*") if p.is_file()} == before
        subprocess.run(script + ["--apply"], capture_output=True, text=True, check=True)
        profile = D.P.read_profile(repo / "AGENTS.md", validated=False)
        assert profile == D.propose(D.detect(repo))["profile"]
        settings = json.loads((repo / ".claude/settings.json").read_text())
        assert settings["enabledPlugins"]["workbench-core@evidence-workbench"] is True
        assert subprocess.run(script + ["--diff"], capture_output=True, text=True).stdout.strip() == "no changes"
    agents = (tmp_path / "octree-mhd/AGENTS.md").read_text()
    assert agents.startswith("---\nworkbench:\n") and "Use `cfd-run-verdict` for run checks." in agents
    assert not (tmp_path / "octree-mhd/.codex/rules/workbench.rules").exists()
    # Explicit restrictions still create rules and stay stable after applying.
    profile['user_executed'] = [{'pattern': 'mpirun', 'why': 'cluster job', 'codex_prefix': [['mpirun']]}]
    (repo / 'AGENTS.md').write_text(D.agents_md_text(repo, profile))
    subprocess.run(script + ['--apply'], capture_output=True, text=True, check=True)
    assert (repo / '.codex/rules/workbench.rules').read_text().count('prefix_rule(') == 1
    assert subprocess.run(script + ['--diff'], capture_output=True, text=True, check=True).stdout.strip() == 'no changes'


def test_mcp_check_reports_gaps_and_finishes_codex_project_servers(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("workbench_mcp_check", SCRIPTS / "mcp_check.py")
    M = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(M)
    repo, home, bin_dir = copy_repo("vision-ml", tmp_path), tmp_path / "home", tmp_path / "bin"
    (home / ".codex").mkdir(parents=True)
    bin_dir.mkdir()
    for program in ("zotero-mcp", "markitdown-mcp", "serena"):
        (bin_dir / program).write_text("#!/bin/sh\n")
        (bin_dir / program).chmod(0o755)
    for name in ("CLAUDE_CONFIG_DIR", "CODEX_HOME"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("PATH", str(bin_dir))
    (home / ".claude.json").write_text(json.dumps({
        "mcpServers": {"zotero": {"command": "zotero-mcp", "env": {"ZOTERO_LOCAL": "true"}}},
        "projects": {str(repo): {"mcpServers": {"serena": {"command": "serena"}}}}}))
    # A Zotero API key in Codex gives the agent write access to the library.
    (home / ".codex/config.toml").write_text(
        '[mcp_servers.zotero]\ncommand = "zotero-mcp"\nenv = { ZOTERO_LOCAL = "true", ZOTERO_API_KEY = "k" }\n')
    versions = {"zotero-mcp-server": "0.15.1", "markitdown-mcp": "0.0.1a8", "serena-agent": "2.1.0"}
    status = lambda: {t["tool"]: t for t in M.check(repo, ["code", "research"], home, versions)["tools"]}  # noqa: E731
    before = status()
    assert before["zotero"]["status"] == "FAIL" and "read-only" in before["zotero"]["missing"][0]
    assert before["markitdown"]["commands"] == ["claude mcp add markitdown --scope user -- markitdown-mcp",
                                                "codex mcp add markitdown -- markitdown-mcp"]
    assert before["serena"]["status"] == "PASS" and before["playwright"]["status"] == "OPTIONAL"
    script = [sys.executable, str(SCRIPTS / "mcp_check.py"), str(repo), "--codex-project", "serena"]
    assert "+[mcp_servers.serena]" in subprocess.run(script + ["--diff"], capture_output=True, text=True).stdout
    assert not (repo / ".codex/config.toml").exists()
    subprocess.run(script + ["--apply"], capture_output=True, text=True, check=True)
    assert subprocess.run(script + ["--diff"], capture_output=True, text=True).stdout.strip() == "no changes"
    assert status()["serena"]["missing"] == ["Codex trust for this folder"]
    with (home / ".codex/config.toml").open("a") as config:
        config.write(f'\n[projects."{repo}"]\ntrust_level = "trusted"\n')
    assert status()["serena"]["notes"][:2] == ["Claude Code: local", "Codex: project"]
    # A plugin turned off for this folder stays off, even when the user turned it on everywhere.
    (home / ".claude").mkdir()
    (home / ".claude/settings.json").write_text(json.dumps({"enabledPlugins": {"session-report@claude-plugins-official": True}}))
    (repo / ".claude").mkdir(exist_ok=True)
    (repo / ".claude/settings.local.json").write_text(json.dumps({"enabledPlugins": {"session-report@claude-plugins-official": False}}))
    assert status()["session-report"]["status"] == "FAIL"
    # A server the owner wrote with a quoted key is found, so --apply adds no second copy.
    (repo / ".codex/config.toml").write_text('[mcp_servers."serena"]\ncommand = "serena"\n')
    old, new = M.codex_project_text(repo, ["serena"])
    assert old == new
    # A collaborator's .mcp.json that names a server "serena" but runs another program fails.
    (repo / ".mcp.json").write_text(json.dumps({"mcpServers": {"serena": {"command": "bash", "args": ["-c", "x"]}}}))
    assert any('runs "bash"' in item for item in status()["serena"]["missing"])
