#!/usr/bin/env python3
"""Read-only SU2/Gmsh mesh admission checker."""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path

def json_load(p):
    try: return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError): return None

def su2(path):
    lines = [x.strip() for x in path.read_text(errors="replace").splitlines()]
    out = {"format":"SU2", "dimension":None, "points":None, "elements":None, "markers":[], "orientation": {}}
    for i, line in enumerate(lines):
        if line.startswith("NDIME="): out["dimension"] = int(line.split("=",1)[1])
        if line.startswith("NPOIN="): out["points"] = int(line.split("=",1)[1].split()[0])
        if line.startswith("NELEM="): out["elements"] = int(line.split("=",1)[1].split()[0])
        if line.startswith("NMARKER="): out["nmarker"] = int(line.split("=",1)[1])
        if line.startswith("MARKER_TAG="):
            out["markers"].append(line.split("=",1)[1].strip())
    return out

def gmsh(path):
    lines = [x.strip() for x in path.read_text(errors="replace").splitlines()]
    out = {"format":"Gmsh 2.2", "dimension":None, "points":None, "elements":None, "markers":[], "orientation": {}}
    try:
        ni = lines.index("$Nodes"); out["points"] = int(lines[ni+1])
        ei = lines.index("$Elements"); out["elements"] = int(lines[ei+1])
        # Gmsh element records contain a type and physical tag; preserve tag ids as markers.
        start = ei + 2; count = int(lines[ei+1]); tags = set()
        for row in lines[start:start+count]:
            parts = row.split(); nt = int(parts[2]); tags.update(int(x) for x in parts[3:3+nt])
        out["markers"] = sorted(tags)
    except (ValueError, IndexError): pass
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--mesh", required=True, type=Path); ap.add_argument("--report", type=Path); ap.add_argument("--provenance", type=Path)
    a=ap.parse_args(); mesh=a.mesh.resolve()
    if not mesh.is_file(): print(json.dumps({"verdict":"INCONCLUSIVE","reason":"mesh unavailable","evidence":str(mesh)})); return 2
    try: parsed = gmsh(mesh) if mesh.suffix == ".msh" else su2(mesh)
    except OSError as e: print(json.dumps({"verdict":"INCONCLUSIVE","reason":str(e),"evidence":str(mesh)})); return 2
    report=json_load(a.report.resolve()) if a.report and a.report.is_file() else None
    provenance=json_load(a.provenance.resolve()) if a.provenance and a.provenance.is_file() else None
    digest=hashlib.sha256(mesh.read_bytes()).hexdigest()
    failures=[]; missing=[]
    for key in ("dimension","points","elements"):
        if parsed.get(key) is None: missing.append(key)
    if parsed.get("orientation",{}).get("reoriented",0): failures.append({"gate":"orientation","value":parsed["orientation"],"evidence":str(mesh)})
    if isinstance(report,dict):
        for key,value in report.items():
            if isinstance(value,dict) and value.get("pass") is False: failures.append({"gate":key,"value":value,"evidence":str(a.report.resolve())})
            if isinstance(value,(int,float)) and not math.isfinite(value): failures.append({"gate":key,"value":value,"evidence":str(a.report.resolve())})
    else: missing.append("quality report")
    if provenance is None: missing.append("provenance")
    out={"verdict":"FAIL" if failures else ("INCONCLUSIVE" if missing else "PASS"),"read_only":True,"mesh":str(mesh),"sha256":digest,"structure":parsed,"quality_report":str(a.report.resolve()) if report is not None else "evidence unavailable","provenance":str(a.provenance.resolve()) if provenance is not None else "evidence unavailable","failures":failures,"missing":missing}
    print(json.dumps(out,indent=2,sort_keys=True)); return 0 if out["verdict"]=="PASS" else 1
if __name__ == "__main__": raise SystemExit(main())
