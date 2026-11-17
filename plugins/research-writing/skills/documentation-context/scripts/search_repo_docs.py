#!/usr/bin/env python3
"""Return a bounded documentation packet for an explicitly supplied repository."""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

NAMES = {'README', 'AGENTS.md', 'CLAUDE.md', 'CONTRIBUTING.md', 'ARCHITECTURE.md'}
EXTS = {'.md', '.markdown', '.rst', '.txt', '.yaml', '.yml', '.toml', '.json', '.py', '.sh', '.c', '.h', '.cpp'}
SKIP = {'.git', '.venv', 'node_modules', '__pycache__', 'build', 'dist', 'out', 'cache', 'caches'}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['repo-search']); parser.add_argument('--repo', required=True)
    parser.add_argument('--question', required=True); parser.add_argument('--max-tokens', type=int, default=1200)
    parser.add_argument('--lean', action='store_true'); args = parser.parse_args()
    if args.max_tokens < 100 or args.max_tokens > 10000:
        parser.error('--max-tokens must be 100..10000')
    root = Path(args.repo).expanduser()
    if not root.is_dir():
        print(f'ERROR: explicit repository root is not a directory: {args.repo}', file=sys.stderr); return 2
    terms = {word.lower() for word in re.findall(r'[A-Za-z_][A-Za-z0-9_-]{2,}', args.question)}
    hits = []
    for path in sorted(root.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in EXTS or any(x in SKIP for x in path.parts): continue
        if path.name not in NAMES and not any(x in path.parts for x in ('docs', 'examples', 'tests', 'config')): continue
        try: lines = path.read_text(errors='replace').splitlines()
        except OSError: continue
        for number, line in enumerate(lines, 1):
            overlap = sum(term in line.lower() for term in terms)
            if overlap: hits.append((overlap, str(path), number, line.strip()[:240]))
    hits = sorted(hits, key=lambda hit: (-hit[0], hit[1], hit[2]))
    bounded, used = [], 0
    for hit in hits:
        cost = len(hit[3]) + 80
        if bounded and used + cost > args.max_tokens * 4: break
        bounded.append(hit); used += cost
    hits = bounded[:60]
    citations = [{'path': hit[1], 'line_start': hit[2], 'line_end': hit[2], 'authority': 'repository-documentation',
                  'confidence': 'medium' if hit[0] > 1 else 'low'} for hit in hits]
    packet = {'schema_version': 1, 'mode': 'repo-search', 'query': args.question,
              'sources': citations, 'claims': [hit[3] for hit in hits], 'definitions': [],
              'assumptions': ['Search was bounded to documentation, examples, tests, config references, and instruction files.',
                              'No source was edited and no command was executed.'], 'interfaces': [], 'examples': [],
              'failure_modes': [], 'citations': citations,
              'unresolved_questions': ['Confirm the highest-authority source for each claim.'],
              'recommended_next_reads': [hit[1] for hit in hits[:5]]}
    print(json.dumps(packet, indent=2)); return 0

if __name__ == '__main__':
    raise SystemExit(main())
