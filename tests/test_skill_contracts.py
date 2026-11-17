"""Deterministic skill contracts (D34 replaced model-run eval suites with free checks).

Each skill except token-lean and research-router (long references by design) and the
bundled stop-slop states its command class, has a refusal or INCONCLUSIVE
path, keeps a no-profile path when it reads a profile (D32), links only reference files
that exist, and keeps a short description and body (always-on and on-invoke cost).
"""
import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
CONTRACT_SKILLS = {
    "workbench-core": ["handoff", "codex-delegate", "run-handoff", "anti-pattern-capture",
                       "decision-record", "conflict-ledger", "docs-distill", "authority-router", "test-value-audit", "repo-setup",
                       "lean-output", "workstation-bootstrap", "surgical-edit", "phase-exec", "plan-forge",
                       "repository-health-audit"],
    "sim-validity": ["solution-verification", "code-verification", "conservation-audit", "solver-health",
                     "validation-comparison", "run-verdict", "mesh-admission", "derivative-audit",
                     "sim-code-development", "inspect-run", "verify-fast"],
    "ml-validity": ["ml-experiment-audit", "results-provenance", "third-party-audit", "multifidelity-data-audit"],
    "research-writing": ["claims-ledger", "application-dossier", "latex-check", "analysis-note",
                         "documentation-context", "research-preview", "plain-language", "reader-distill",
                         "evidence-map"],
}
SKILLS = [(plugin, name) for plugin, names in CONTRACT_SKILLS.items() for name in names]


def split(path):
    text = path.read_text()
    end = text.index("\n---\n", 4)
    return text[4:end], text[end + 5:]


def test_skill_contracts():
    failures = []
    for plugin, name in SKILLS:
        try:
            check_skill(plugin, name)
        except AssertionError as exc:
            failures.append(f"{plugin}/{name}: {exc}")
    assert not failures, "\n".join(failures)


def check_skill(plugin, name):
    folder = ROOT / "plugins" / plugin / "skills" / name
    head, body = split(folder / "SKILL.md")
    description = re.search(r"^description: (.*)$", head, re.M).group(1).strip('"')
    assert re.search(rf"^name: {name}$", head, re.M)
    assert "tags: [lean]" in head
    assert len(description) <= 200, len(description)
    assert len(body.strip().splitlines()) <= 70
    assert re.search(r"Command class: `(read-only|safe-local|user-execution)`", body)
    assert "## Refusals" in body or "INCONCLUSIVE" in body
    if "profile.py" in body:
        assert re.search(r"[Oo]therwise|[Ww]ithout a profile|no profile|None found", body)
    for ref in re.findall(r"(?<![\w./-])(references/[\w.-]+\.md)", body):
        assert (folder / ref).is_file(), ref
