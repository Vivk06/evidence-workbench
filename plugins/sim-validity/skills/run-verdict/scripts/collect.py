#!/usr/bin/env python3
"""Read-only, layout-tolerant CFD run evidence collector."""
from __future__ import annotations
import argparse, csv, hashlib, json, math
from pathlib import Path

REQUIRED = ("status", "provenance", "config", "history", "residual", "gates")

def load(path: Path):
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None

def first(root: Path, names):
    for name in names:
        p = root / name
        if p.is_file():
            return p
    return None

def evidence(root: Path, key, names):
    p = first(root, names)
    return {"key": key, "path": str(p) if p else None, "value": load(p) if p else None,
            "evidence": str(p) if p else "evidence unavailable"}

def csv_summary(p: Path | None):
    if not p: return None
    try:
        with p.open(newline="") as fh:
            rows = list(csv.DictReader(fh))
        if not rows: return {"rows": 0}
        numeric = {}
        for k in rows[-1]:
            vals = []
            for row in rows:
                try: vals.append(float(row[k]))
                except (ValueError, TypeError, KeyError): pass
            if vals: numeric[k] = {"first": vals[0], "last": vals[-1], "finite": all(math.isfinite(x) for x in vals)}
        return {"rows": len(rows), "last": numeric}
    except (OSError, csv.Error):
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True, type=Path)
    ap.add_argument("--baseline", type=Path)
    args = ap.parse_args(); root = args.run_dir.resolve()
    if not root.is_dir():
        print(json.dumps({"verdict":"INCONCLUSIVE", "reason":"run directory unavailable", "evidence":str(root)})); return 2
    out = {"run_dir": str(root), "read_only": True, "artifacts": {}}
    specs = {
        "status": ("status.json", "run_status.json"),
        "provenance": ("provenance.json", "solver_manifest.json", "manifest.json"),
        "config": ("resolved_config.json", "config.json", "resolved.toml"),
        "gates": ("gates.json", "convergence_report.json", "mesh_report.json"),
    }
    for key, names in specs.items(): out["artifacts"][key] = evidence(root, key, names)
    hist = first(root, ("history.csv", "history.json", "adaptation_history.json"))
    out["artifacts"]["history"] = {"path":str(hist) if hist else None, "evidence":str(hist) if hist else "evidence unavailable",
                                     "summary": csv_summary(hist) if hist and hist.suffix == ".csv" else (load(hist) if hist else None)}
    log = first(root, ("stdout.log", "stderr.log", "run.log", "solver.log"))
    out["artifacts"]["residual"] = {"path":str(log) if log else None, "evidence":str(log) if log else "evidence unavailable"}
    missing = [k for k in REQUIRED if out["artifacts"].get(k, {}).get("path") is None]
    gate_values = out["artifacts"]["gates"].get("value") or {}
    failed = []
    if isinstance(gate_values, dict):
        for key, value in gate_values.items():
            if isinstance(value, dict) and value.get("pass") is False: failed.append({"gate":key, "value":value, "evidence":out["artifacts"]["gates"]["path"]})
            elif isinstance(value, bool) and not value: failed.append({"gate":key, "value":value, "evidence":out["artifacts"]["gates"]["path"]})
    baseline = load(args.baseline.resolve()) if args.baseline and args.baseline.is_file() else None
    out["baseline"] = {"path":str(args.baseline.resolve()) if args.baseline else None, "value":baseline,
                       "evidence":str(args.baseline.resolve()) if baseline is not None else "evidence unavailable"}
    out["failed_gates"] = failed
    out["verdict"] = "FAIL" if failed else ("INCONCLUSIVE" if missing else "PASS")
    out["missing_artifacts"] = missing
    out["next_actions"] = [f"supply {k} artifact" for k in missing] + (["user review of failed gates"] if failed else [])
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if out["verdict"] == "PASS" else 1

if __name__ == "__main__": raise SystemExit(main())
