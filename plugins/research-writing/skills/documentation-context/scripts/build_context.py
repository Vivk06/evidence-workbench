#!/usr/bin/env python3
"""Build a bounded, cited context from explicitly approved documentation paths."""
from __future__ import annotations
import argparse, datetime as dt, json, re, sys
from pathlib import Path

ALLOWED = {'.md', '.markdown', '.rst', '.txt', '.adoc', '.yaml', '.yml', '.json', '.toml'}
SECRET = re.compile(r'(?i)(bearer\s+)[A-Za-z0-9._-]+|(api[_-]?key|password|secret|token)\s*[:=]\s*[^\s,;]+|-----BEGIN [^-]+ PRIVATE KEY-----')
SKIP_NAMES = {'.git', '.venv', 'node_modules', '__pycache__', '.secrets', 'credentials', 'transcripts', 'caches', 'papers'}
PERSONAL_NAMES = {'personal', 'private', '.ssh', '.local', '.config', 'memories', 'notes'}

def redact(value):
    return SECRET.sub('[REDACTED]', value)

def files_for(raw, allow_personal):
    out = []
    for item in raw:
        path = Path(item).expanduser()
        if not path.exists():
            raise ValueError(f'source does not exist: {item}')
        if not allow_personal and any(part in PERSONAL_NAMES for part in path.parts):
            raise ValueError(f'personal source requires --personal-data allowlisted: {item}')
        if path.is_dir():
            for file in sorted(path.rglob('*')):
                if file.is_file() and file.suffix.lower() in ALLOWED and not any(x in SKIP_NAMES for x in file.parts):
                    out.append(file)
        elif path.suffix.lower() in ALLOWED and path.name not in SKIP_NAMES:
            out.append(path)
    return list(dict.fromkeys(out))

def build(args):
    paths = files_for([item for item in args.sources.split(',') if item], args.personal_data == 'allowlisted')
    if not paths:
        raise ValueError('approved source scope contains no supported documentation files')
    claims, citations, inventory = [], [], []
    budget = args.max_tokens * 4
    for path in paths:
        text = redact(path.read_text(errors='replace'))
        lines = text.splitlines()
        inventory.append({'path': str(path), 'bytes': path.stat().st_size,
                          'modified': dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc).isoformat()})
        for number, line in enumerate(lines, 1):
            if line.strip() and (args.function.lower() in line.lower() or line.lstrip().startswith(('#', '-', '*'))):
                claims.append(line.strip())
                citations.append({'path': str(path), 'line_start': number, 'line_end': number,
                                  'authority': 'explicit-source', 'confidence': 'medium'})
                if sum(map(len, claims)) > budget:
                    break
    return {'schema_version': 1, 'mode': 'corpus', 'query': args.function, 'sources': inventory,
            'claims': claims[:100], 'definitions': [], 'assumptions': ['Only explicitly supplied sources were read.'],
            'interfaces': [], 'examples': [], 'failure_modes': [], 'citations': citations[:100],
            'unresolved_questions': ['Which uncited details require authoritative confirmation?'],
            'recommended_next_reads': [str(path) for path in paths[:5]]}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['corpus'])
    parser.add_argument('--sources', required=True, help='comma-separated explicit files/directories')
    parser.add_argument('--function', required=True)
    parser.add_argument('--max-tokens', type=int, default=1200)
    parser.add_argument('--personal-data', choices=['deny', 'allowlisted'], default='deny')
    parser.add_argument('--lean', action='store_true')
    parser.add_argument('--write')
    args = parser.parse_args()
    if args.max_tokens < 100 or args.max_tokens > 10000:
        parser.error('--max-tokens must be 100..10000')
    if args.lean and args.write:
        parser.error('--lean and --write are mutually exclusive')
    try:
        result = build(args)
    except (OSError, ValueError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 2
    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.write:
        Path(args.write).parent.mkdir(parents=True, exist_ok=True)
        Path(args.write).write_text(output + '\n')
        print(f'WROTE {args.write}')
    else:
        print(output)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
