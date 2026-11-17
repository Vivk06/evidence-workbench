#!/usr/bin/env python3
"""Inventory the Markdown documents under explicit paths and show which need distilling.

Usage: doc_inventory.py <path> [<path> ...] [--depth N] [--json]

Each path is a file or a folder; folders are searched to --depth levels (default 3),
skipping hidden folders. A file whose first line is
`<!-- working file: conclusions in <path> -->` is a working file: agent state that a
reader document distils. The path is relative to the working file's folder or to a
folder above it, up to the repository root. Every other file is a reader document.

For each file it reports words, the share of words in sentences of running text (the
rest is headings, list items and table cells), and the plain-language checker's
must-fix and consider counts, with undefined abbreviations and codes counted apart. It
flags reader documents that are mostly fragments or have must-fix findings, and
working files that point to a reader document that does not exist. Reads files only.
"""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "plain-language" / "scripts"))
from check import findings, load_rules  # noqa: E402
from prose import count_words, prose_units  # noqa: E402

WORKING = re.compile(r"^\s*<!--\s*working file:\s*conclusions in\s+(\S+?)\s*-->")
MOSTLY_FRAGMENTS = 0.4  # below this share of running text, a reader document reads as notes
MIN_WORDS = 150  # shorter files are too small to judge by share


def markdown_files(paths, depth):
    found = []
    for raw in paths:
        path = Path(raw).expanduser().resolve()
        if path in (Path.home().resolve(), Path("/")):
            raise SystemExit(f"refusing to scan {path}: name the folder that holds the documents")
        if path.is_file():
            found.append(path)
            continue
        if not path.is_dir():
            raise SystemExit(f"no such file or folder: {raw}")
        for folder, dirs, files in os.walk(path):
            level = len(Path(folder).relative_to(path).parts)
            dirs[:] = sorted(d for d in dirs if not d.startswith(".") and level < depth)
            found.extend(Path(folder) / f for f in sorted(files) if f.endswith(".md"))
    return sorted(set(found))


def inspect(path, rules):
    text = path.read_text(encoding="utf-8", errors="replace")
    first = next((line for line in text.splitlines() if line.strip()), "")
    marker = WORKING.match(first)
    pieces = prose_units(text)
    words = sum(count_words(piece.text) for piece in pieces)
    running = sum(count_words(piece.text) for piece in pieces if piece.kind == "paragraph")
    found = findings(text, rules)
    row = {
        "path": str(path),
        "role": "working" if marker else "reader",
        "words": words,
        "running_text": round(running / words, 2) if words else 0.0,
        "must_fix": sum(1 for f in found if f["severity"] == "block"),
        "consider": sum(1 for f in found if f["severity"] == "advise"),
        "undefined_terms": sum(1 for f in found if f["id"] == "undefined-abbreviation"),
        "flags": [],
    }
    if marker:
        # The path is relative to the working file's folder or to any folder above it, up to
        # the repository root, so "docs/report.md" works from logs/ as well as from the root.
        folders = [path.parent]
        for folder in path.parent.parents:
            if (folders[-1] / ".git").exists():
                break
            folders.append(folder)
        if not any((folder / marker.group(1)).is_file() for folder in folders):
            row["flags"].append(f"points to a reader document that does not exist: {marker.group(1)}")
    else:
        if words >= MIN_WORDS and row["running_text"] < MOSTLY_FRAGMENTS:
            row["flags"].append("mostly fragments: fine for a reference table, not for a report or explanation")
        if row["must_fix"]:
            row["flags"].append(f"{row['must_fix']} must-fix plain-language findings")
        if row["undefined_terms"]:
            row["flags"].append(f"{row['undefined_terms']} abbreviations or codes never spelled out")
    return row


def main(argv):
    as_json = "--json" in argv
    depth = 3
    args = [a for a in argv if a != "--json"]
    if "--depth" in args:
        i = args.index("--depth")
        depth = int(args[i + 1])
        del args[i : i + 2]
    if not args:
        raise SystemExit(__doc__.split("\n\n")[1])
    rules = load_rules()
    rows = [inspect(path, rules) for path in markdown_files(args, depth)]
    readers = [r for r in rows if r["role"] == "reader"]
    summary = {
        "reader_documents": len(readers),
        "working_files": len(rows) - len(readers),
        "words": sum(r["words"] for r in rows),
        "flagged": sum(1 for r in rows if r["flags"]),
    }
    if as_json:
        print(json.dumps({"summary": summary, "files": rows}, indent=2))
        return 0
    for r in rows:
        print(f"{r['path']}  {r['role']}  {r['words']} words  running text {r['running_text']:.0%}  "
              f"must fix {r['must_fix']}  consider {r['consider']}")
        for flag in r["flags"]:
            print(f"  - {flag}")
    print(f"{summary['reader_documents']} reader documents, {summary['working_files']} working files, "
          f"{summary['words']} words, {summary['flagged']} flagged.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
