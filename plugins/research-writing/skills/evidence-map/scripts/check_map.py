#!/usr/bin/env python3
"""Check an evidence map: one position, claims linked to it, evidence with sources.

Usage: check_map.py <map.md> [--ledger <claims-ledger.csv>]

The map is the first Markdown table in the file with the columns
ID | Kind | Statement | Links | Source (format in references/map-format.md).
Prints JSON with a PASS or FAIL verdict and each finding; exits 1 on FAIL.
Reads files only.
"""
import csv
import json
import re
import sys
from pathlib import Path

KINDS = {"position", "claim", "evidence", "unknown"}
LINK_TYPES = {"supports", "contradicts", "qualifies", "missing"}
COLUMNS = ["id", "kind", "statement", "links", "source"]
LINK = re.compile(r"^(\w+)\s+(\S+)$")


def read_table(text):
    rows, header = [], None
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip().startswith("|"):
            if header:
                break
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
        elif not re.fullmatch(r"[\s:|-]+", line):
            rows.append((number, dict(zip(header, cells))))
    return header, rows


def read_ledger(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return {row["id"].strip(): row for row in csv.DictReader(handle) if row.get("id", "").strip()}


def check(text, ledger=None):
    found = []

    def report(severity, line, message):
        found.append({"severity": severity, "line": line, "message": message})

    header, rows = read_table(text)
    if header is None or header[: len(COLUMNS)] != COLUMNS:
        report("must fix", 0, "No table with the columns ID | Kind | Statement | Links | Source.")
        return found
    nodes, links = {}, []
    for line, row in rows:
        node, kind = row.get("id", ""), row.get("kind", "").lower()
        if not node or node in nodes:
            report("must fix", line, f"ID {node!r} is empty or used twice.")
            continue
        if kind not in KINDS:
            report("must fix", line, f"{node}: kind {kind!r} is not one of {sorted(KINDS)}.")
        if not row.get("statement"):
            report("must fix", line, f"{node}: the statement is empty.")
        nodes[node] = {"kind": kind, "line": line, "source": row.get("source", "")}
        for part in filter(None, (p.strip() for p in row.get("links", "").split(","))):
            match = LINK.match(part)
            if not match or match.group(1) not in LINK_TYPES:
                report("must fix", line, f"{node}: link {part!r} is not '<{'|'.join(sorted(LINK_TYPES))}> <ID>'.")
                continue
            links.append((node, match.group(1), match.group(2), line))

    positions = [n for n, v in nodes.items() if v["kind"] == "position"]
    if len(positions) != 1:
        report("must fix", 0, f"The map needs exactly one position; it has {len(positions)}.")
    outgoing = {n: [] for n in nodes}
    incoming = {n: [] for n in nodes}
    for source, kind, target, line in links:
        if target not in nodes:
            report("must fix", line, f"{source}: links to {target}, which is not in the map.")
            continue
        outgoing[source].append((kind, target))
        incoming[target].append((kind, source))
        if nodes[target]["kind"] not in {"position", "claim"}:
            report("must fix", line, f"{source}: links to {target}, a {nodes[target]['kind']}; link to a claim or the position.")
        if (kind == "missing") != (nodes[source]["kind"] == "unknown"):
            report("must fix", line, f"{source}: only an unknown uses 'missing', and an unknown uses only 'missing'.")

    for node, info in nodes.items():
        kind, line = info["kind"], info["line"]
        if kind == "position" and outgoing[node]:
            report("must fix", line, f"{node}: the position links to nothing; claims link to it.")
        if kind in {"claim", "evidence", "unknown"} and not outgoing[node]:
            report("must fix", line, f"{node}: a {kind} must link to a claim or the position.")
        if kind == "claim" and not incoming[node]:
            report("must fix", line, f"{node}: no evidence, sub-claim or unknown bears on this claim.")
        if kind == "evidence":
            source = info["source"]
            if not source:
                report("must fix", line, f"{node}: evidence needs a source (ledger:<id>, a URL with its access date, or path:line).")
            elif source.startswith("ledger:") and ledger is not None:
                row = ledger.get(source[len("ledger:"):])
                if row is None:
                    report("must fix", line, f"{node}: {source} is not a row of the ledger.")
                elif row.get("status") == "contradicted" and any(k == "supports" for k, _ in outgoing[node]):
                    report("must fix", line, f"{node}: {source} is marked contradicted but is used as support.")
                elif row.get("status") in {"unverified", "stale"}:
                    report("consider", line, f"{node}: {source} is {row['status']}; say so where the reader sees it.")

    if positions:
        reached, todo = set(), [positions[0]]
        while todo:
            node = todo.pop()
            for _, source in incoming.get(node, []):
                if source not in reached:
                    reached.add(source)
                    todo.append(source)
        for node in nodes:
            if node != positions[0] and node not in reached:
                report("must fix", nodes[node]["line"], f"{node}: no chain of links reaches the position.")
        if not any(k == "supports" for k, _ in incoming[positions[0]]):
            report("must fix", nodes[positions[0]]["line"], "Nothing supports the position.")
    if not any(v["kind"] == "unknown" for v in nodes.values()):
        report("consider", 0, "The map lists no unknowns; if nothing open could change the position, say so in the reader document.")
    return found


def main(argv):
    args = list(argv)
    ledger = None
    if "--ledger" in args:
        i = args.index("--ledger")
        ledger = read_ledger(args[i + 1])
        del args[i : i + 2]
    if len(args) != 1:
        raise SystemExit(__doc__.split("\n\n")[1])
    found = check(Path(args[0]).read_text(encoding="utf-8"), ledger)
    verdict = "FAIL" if any(f["severity"] == "must fix" for f in found) else "PASS"
    print(json.dumps({"verdict": verdict, "map": args[0], "findings": found}, indent=2))
    return 1 if verdict == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
