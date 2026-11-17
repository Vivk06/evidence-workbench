"""Checker scripts give their recorded verdicts on their fixtures (free, deterministic)."""
import json
import subprocess
import sys
from pathlib import Path

SKILLS = Path(__file__).parents[1] / "plugins/sim-validity/skills"
WRITING = Path(__file__).parents[1] / "plugins/research-writing/skills"
TEXTS = Path(__file__).parent / "fixtures/writing"


def test_checker_verdicts_on_fixtures():
    run_dir = SKILLS / "run-verdict/scripts"
    audit = SKILLS / "derivative-audit/scripts"
    mesh = SKILLS / "mesh-admission/scripts"
    cases = [
        ([run_dir / "collect.py", "--run-dir", run_dir / "fixtures/valid"], "PASS"),
        ([run_dir / "collect.py", "--run-dir", run_dir / "fixtures/invalid"], "FAIL"),
        ([audit / "audit.py", "--evidence", audit / "fixtures/valid.json"], "PASS"),
        ([audit / "audit.py", "--evidence", audit / "fixtures/invalid.json"], "FAIL"),
        ([mesh / "check.py", "--mesh", mesh / "fixtures/mesh.su2", "--report", mesh / "fixtures/report.json",
          "--provenance", mesh / "fixtures/provenance.json"], "PASS"),
        ([WRITING / "plain-language/scripts/check.py", "--json", TEXTS / "agent-note.md"], "FAIL"),
        ([WRITING / "plain-language/scripts/check.py", "--json", TEXTS / "distilled.md"], "PASS"),
        ([WRITING / "evidence-map/scripts/check_map.py", TEXTS / "map-valid.md", "--ledger", TEXTS / "ledger.csv"], "PASS"),
        ([WRITING / "evidence-map/scripts/check_map.py", TEXTS / "map-invalid.md", "--ledger", TEXTS / "ledger.csv"], "FAIL"),
    ]
    failures = []
    for args, expected in cases:
        done = subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, timeout=60)
        verdict = json.loads(done.stdout)["verdict"]
        if verdict != expected:
            failures.append(f"{args[0].name} {args[-1]}: {verdict} != {expected}")
    assert not failures, "\n".join(failures)
    report = json.loads(subprocess.run([sys.executable, str(audit / "audit.py"), "--evidence", str(audit / "fixtures/valid.json")],
                                       capture_output=True, text=True).stdout)
    assert "authority_bands" not in report and report["bands_given"] == {"alpha": 0.0001, "shape_0": 0.001}
    inventory = json.loads(subprocess.run([sys.executable, str(WRITING / "reader-distill/scripts/doc_inventory.py"), str(TEXTS), "--json"],
                                          capture_output=True, text=True).stdout)
    flags = {Path(row["path"]).name: row["flags"] for row in inventory["files"]}
    assert inventory["summary"]["working_files"] == 1 and "does not exist" in flags["map-valid.md"][0]
    assert flags["distilled.md"] == [] and any("must-fix" in flag for flag in flags["agent-note.md"])
