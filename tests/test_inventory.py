"""Every skill sits in exactly one plugin, in its planned plugin, under its D22 name (plan §2.1)."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[1]
OWNER = {
    "workbench-core": {"plan-forge", "phase-exec", "surgical-edit", "token-lean", "lean-output",
                       "repository-health-audit", "test-value-audit", "workstation-bootstrap", "handoff",
                       "codex-delegate", "run-handoff", "anti-pattern-capture", "decision-record",
                       "conflict-ledger", "docs-distill", "authority-router", "repo-setup"},
    "sim-validity": {"run-verdict", "sim-code-development", "inspect-run", "mesh-admission", "derivative-audit",
                     "verify-fast", "solution-verification", "code-verification", "conservation-audit",
                     "solver-health", "validation-comparison"},
    "ml-validity": {"ml-experiment-audit", "results-provenance", "third-party-audit", "multifidelity-data-audit"},
    "research-writing": {"documentation-context", "research-preview", "research-router", "stop-slop",
                         "claims-ledger", "application-dossier", "latex-check", "analysis-note",
                         "plain-language", "reader-distill", "evidence-map"},
}


def test_skill_inventory():
    skills = list(ROOT.glob("plugins/*/skills/*/SKILL.md"))
    found = {}
    for skill_md in skills:
        found.setdefault(skill_md.parts[-4], set()).add(skill_md.parent.name)
        assert skill_md.read_text().startswith(f"---\nname: {skill_md.parent.name}\n"), skill_md
    assert found == {plugin: names for plugin, names in OWNER.items()}, found
    assert not [name for name, n in Counter(p.parent.name for p in skills).items() if n > 1]
    assert not list(ROOT.glob("plugins/*/skills/cfd-*")) and not (ROOT / "skills").exists()  # D22, no aliases

    writing = json.loads((ROOT / "plugins/research-writing/.claude-plugin/plugin.json").read_text())
    assert writing['dependencies'] == ['workbench-core']
    market = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())
    assert not market.get('allowCrossMarketplaceDependenciesOn')
