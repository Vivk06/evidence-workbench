#!/usr/bin/env python3
"""Read-only derivative evidence audit; no solver execution."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--evidence",required=True,type=Path); ap.add_argument("--profile",default="generic"); a=ap.parse_args(); p=a.evidence.resolve()
    try: data=json.loads(p.read_text())
    except (OSError,json.JSONDecodeError): print(json.dumps({"verdict":"INCONCLUSIVE","evidence":str(p),"reason":"evidence unavailable"})); return 2
    required=("cold_start","independent_adjoint","config_parity","provenance","rows")
    missing=[k for k in required if k not in data]
    failures=[]; notes=[]
    for key in ("cold_start","independent_adjoint","config_parity"):
        if data.get(key) is False: failures.append({"gate":key,"value":False,"evidence":str(p)})
    if not data.get("provenance"): missing.append("provenance value")
    rows=data.get("rows")
    if isinstance(rows,list):
        for i,row in enumerate(rows):
            if not isinstance(row,dict): missing.append(f"row {i}"); continue
            if row.get("tangential") is True: notes.append({"row":i,"limitation":"tangential/chordwise row is not FD-verifiable","evidence":str(p)})
            if row.get("projection_terms") is False: failures.append({"gate":"projection_terms","row":i,"evidence":str(p)})
            band=row.get("band"); error=row.get("relative_error")
            if isinstance(error,(int,float)) and isinstance(band,(int,float)) and (not math.isfinite(error) or error>band): failures.append({"gate":"derivative_band","row":i,"error":error,"band":band,"evidence":str(p)})
            if "relative_error" not in row or "band" not in row: missing.append(f"quantitative band row {i}")
    else: missing.append("rows")
    out={"verdict":"FAIL" if failures else ("INCONCLUSIVE" if missing else "PASS"),"read_only":True,"profile":a.profile,"evidence":str(p),"bands_given":{str(r.get("name",i)):r.get("band") for i,r in enumerate(rows) if isinstance(r,dict)} if isinstance(rows,list) else {},"failures":failures,"missing":sorted(set(missing)),"limitations":notes,"prepared_command":data.get("prepared_command","evidence unavailable")}
    print(json.dumps(out,indent=2,sort_keys=True)); return 0 if out["verdict"]=="PASS" else 1
if __name__ == "__main__": raise SystemExit(main())
