"""Profiles retain selected policies and reject malformed configuration."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
CORE = ROOT / "plugins/workbench-core"
GENERIC = CORE / "profiles/templates"
REPOS = Path(__file__).parent / "fixtures/profiles"
TEMPLATES = sorted(GENERIC.glob("*.yaml")) + sorted(REPOS.glob("*.yaml"))
_spec = importlib.util.spec_from_file_location("workbench_profile", CORE / "scripts/profile.py")
P = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P)


def agents_md(directory, frontmatter, body="# Repository instructions\n"):
    (directory / "AGENTS.md").write_text(f"---\n{frontmatter}---\n{body}")
    return directory


def template_frontmatter(path):
    return "".join(line for line in path.read_text().splitlines(True) if not line.startswith("#"))


def test_templates_load_and_values_survive(tmp_path):
    assert {p.stem for p in GENERIC.glob("*.yaml")} == {"physics", "code", "research"}
    assert {p.stem for p in REPOS.glob("*.yaml")} == {
        "solver-project", "adaptive-project", "case-project", "surrogate-project", "ml-project", "writing-project",
    }
    for template in TEMPLATES:
        directory = tmp_path / template.stem
        directory.mkdir()
        agents_md(directory, template_frontmatter(template))
        profile, root = P.load(project_dir=directory)
        assert root == directory and profile["schema"] == 1 and set(profile["archetypes"]) <= P.ARCHETYPES, template
    solver = P.validate(P.parse_yaml(template_frontmatter(REPOS / "solver-project.yaml"))["workbench"])
    assert len(solver["user_executed"]) == 6
    assert solver["user_executed"][0]["pattern"] == r"(^|[;&|]\s*)(mpirun|mpiexec)\b"
    assert solver["run_handoff"] == {"prefix": "$(bash tools/bind_cores.sh <np>)",
                                  "output": "cases/<case>/output/<run_id>/", "tee": False}
    assert solver["authority"]["decisions"] == {"path": "docs/decisions/", "style": "append-only"}
    adaptive_project = P.validate(P.parse_yaml(template_frontmatter(REPOS / "adaptive-project.yaml"))["workbench"])
    assert adaptive_project["main_agent_edits_code"] is False
    assert adaptive_project["agent_allowed"][-1] == {"pattern": r"run/configAdaptive\.py .*--threads 4",
                                         "when": "scratch copy only, small fixture case"}
    experiment = P.validate(P.parse_yaml(template_frontmatter(REPOS / "ml-project.yaml"))["workbench"])
    assert experiment["agent_allowed"][0] == 'CUDA_VISIBLE_DEVICES="" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/pytest -q'
    app = P.validate(P.parse_yaml(template_frontmatter(REPOS / "writing-project.yaml"))["workbench"])
    assert app["writing"] == {"style": "stop-slop", "voice": "first-person", "latex": "sop-tex/"} and app["git"] == "none"
    subset = P.parse_yaml("""workbench:
  schema: 1          # comment
  archetypes:
    - physics
  git: 'read-only'
  activation: null
  test_budget: {max: 20, paths: [tests]}
  user_executed:
    - pattern: 'a''b'
      why: "say \\"hi\\""
  frozen_paths: []
  authority: {decisions: {path: docs/decisions/, style: current-decision}}
""")["workbench"]
    assert subset["schema"] == 1 and subset["archetypes"] == ["physics"] and subset["activation"] is None
    assert subset["user_executed"] == [{"pattern": "a'b", "why": 'say "hi"'}]
    assert P.validate(subset)["test_budget"] == {"max": 20, "paths": ["tests"]}


MALFORMED = [
    "workbench:\n\tschema: 1\n",                                        # tab indentation
    "workbench:\n  schema: 1\n  archetypes: [physics,\n    code]\n",    # multi-line flow
    "workbench:\n  schema: 1\n   archetypes: [physics]\n",              # bad indentation
    "workbench:\n  why: \"a\\sb\"\n",                                   # unsupported escape
    "workbench:\n  why: 'open\n",                                       # unterminated quote
    "workbench:\n  schema: 1\n  schema: 1\n",                           # duplicate key
    "workbench:\n  activation: |\n    source x\n",                      # block scalar
    "workbench:\n  schema: 2\n  archetypes: [physics]\n",               # wrong schema
    "workbench:\n  schema: 1\n  archetypes: [chemistry]\n",             # unknown archetype
    "workbench:\n  schema: 1\n  archetypes: [code]\n  gti: none\n",     # unknown key
    "workbench:\n  schema: 1\n  archetypes: [code]\n  git: sometimes\n",
    "workbench:\n  schema: 1\n  archetypes: [code]\n  user_executed:\n    - {pattern: '(unclosed', why: x}\n",
    "workbench:\n  schema: 1\n  archetypes: [code]\n  user_executed:\n    - {pattern: 'x'}\n",
    "workbench:\n  schema: 1\n  archetypes: [code]\n  codex_delegation: run\n",
]


def test_malformed_profiles_raise(tmp_path):
    failures = []
    for n, frontmatter in enumerate(MALFORMED + [
        "workbench:\n  schema: 1\n  archetypes: [code]\n  test_budget: 0\n",
        "workbench:\n  schema: 1\n  archetypes: [code]\n  test_budget: {max: 5, depth: 2}\n",
    ]):
        directory = tmp_path / f"case{n}"
        directory.mkdir()
        agents_md(directory, frontmatter)
        try:
            P.load(project_dir=directory)
            failures.append(repr(frontmatter))
        except P.ProfileError:
            pass
    (tmp_path / "AGENTS.md").write_text("---\nworkbench:\n  schema: 1\n# Title\n")
    try:
        P.load(project_dir=tmp_path)
        failures.append("unclosed frontmatter")
    except P.ProfileError:
        pass
    assert not failures, "accepted malformed profiles:\n" + "\n".join(failures)


def test_no_profile_and_lookup(tmp_path):
    for n, content in enumerate(["# No frontmatter\n",
                                 "---\ntitle: other tool\nitems:\n  - |\n    block scalar the parser does not read\n---\n# Body\n"]):
        directory = tmp_path / f"plain{n}"
        directory.mkdir()
        (directory / "AGENTS.md").write_text(content)
        assert P.load(project_dir=directory) == (None, None)
    repo = tmp_path / "repo"
    nested = repo / "src" / "pkg"
    nested.mkdir(parents=True)
    agents_md(repo, "workbench:\n  schema: 1\n  archetypes: [code]\n")
    profile, root = P.load(project_dir=None, cwd=nested)
    assert root == repo and profile["git"] == "normal"
    assert P.load(project_dir=None, cwd=Path("/")) == (None, None)
