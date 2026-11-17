#!/usr/bin/env python3
"""Check manifest/policy.yaml exists, the marketplace stays loadable by Codex, and
manifest/external-plugin-admission.yaml follows its schema (--admission)."""
import argparse
import json
import pathlib
import re
import sys

ADMISSION_KEYS = ['schema_version', 'research_record', 'archetypes', 'decisions', 'default', 'rules', 'evidence_required', 'tools']
ADMISSION_RULES = ['archetype_scoped', 'free_only', 'default_reject', 'no_metered_usage']
DECISIONS = {'dependency', 'bundle', 'recommend', 'borrow', 'reject'}
ARCHETYPES = {'physics', 'code', 'research'}

def check_admission(path):
    # Stdlib-only reader for the fixed two-level layout of the admission file.
    errors, top, rules, tools, tool, section = [], {}, set(), {}, None, None
    for line in path.read_text().splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        match = re.match(r'^( *)([A-Za-z0-9_-]+):\s*(.*)$', line)
        if not match:
            continue
        indent, key, value = len(match.group(1)), match.group(2), match.group(3)
        if indent == 0:
            top[key], section = value, key
        elif indent == 2 and section == 'rules':
            rules.add(key)
        elif indent == 2 and section == 'tools':
            tool = tools.setdefault(key, {})
        elif indent == 4 and section == 'tools' and tool is not None:
            tool[key] = value
    errors += [f'{path}: missing top-level key {key}' for key in ADMISSION_KEYS if key not in top]
    errors += [f'{path}: missing rule {key}' for key in ADMISSION_RULES if key not in rules]
    if top.get('default') != 'reject':
        errors.append(f'{path}: default must be reject')
    for name, fields in tools.items():
        decision = fields.get('decision')
        if decision not in DECISIONS:
            errors.append(f'{path}: {name}: decision {decision!r} not in {sorted(DECISIONS)}')
        for key in ('source', 'reason'):
            if not fields.get(key):
                errors.append(f'{path}: {name}: missing {key}')
        if decision in {'dependency', 'bundle', 'recommend'}:
            archetypes = set(re.findall(r'[a-z]+', fields.get('archetypes', '')))
            if not archetypes or not archetypes <= ARCHETYPES:
                errors.append(f'{path}: {name}: {decision} needs archetypes from {sorted(ARCHETYPES)}')
    if not tools:
        errors.append(f'{path}: no tools listed')
    return errors

CODEX_SOURCE_TYPES = {'local', 'url', 'git-subdir', 'npm'}
CODEX_SHADOW_FILES = ['.codex-plugin/plugin.json', '.agents/plugins/marketplace.json', '.agents/plugins/api_marketplace.json']
PATH_KEYS = ['skills', 'commands', 'hooks', 'mcpServers', 'apps']

def check_codex_compat(root, marketplace):
    # Codex reads .claude-plugin files unless a Codex file shadows them (D30; docs/maintaining.md, Codex).
    errors = [f'{root / rel}: Codex would read this instead of the .claude-plugin file (D30)'
              for rel in CODEX_SHADOW_FILES if (root / rel).exists()]
    for entry in marketplace.get('plugins', []):
        name, source = entry.get('name'), entry.get('source')
        if isinstance(source, dict):
            if source.get('source') not in CODEX_SOURCE_TYPES:
                errors.append(f'{name}: source type {source.get("source")!r} is not loadable by Codex')
            continue
        if not isinstance(source, str) or not (source in ('.', './') or source.startswith('./')):
            errors.append(f'{name}: relative source {source!r} must be "./" or start with "./"')
            continue
        manifest_path = root / source / '.claude-plugin/plugin.json'
        if not manifest_path.is_file():
            errors.append(f'{name}: {manifest_path} missing')
            continue
        manifest = json.loads(manifest_path.read_text())
        if manifest.get('name') != name:
            errors.append(f'{name}: marketplace entry name differs from plugin.json name {manifest.get("name")!r}')
        for key in PATH_KEYS:
            values = manifest.get(key, [])
            values = [values] if isinstance(values, str) else values
            if isinstance(values, list):
                errors += [f'{name}: {key} path {value!r} must start with "./"'
                           for value in values if isinstance(value, str) and not value.startswith('./')]
    return errors

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=pathlib.Path, required=True)
    parser.add_argument('--admission', action='store_true', help='also check manifest/external-plugin-admission.yaml')
    args = parser.parse_args()
    root = args.root.resolve()
    required = [root / 'manifest/policy.yaml', root / '.claude-plugin/marketplace.json']
    missing = [str(path) for path in required if not path.is_file()]
    parsed = {}
    for manifest in required[1:]:
        try:
            parsed[manifest.name] = json.loads(manifest.read_text())
        except Exception as exc:
            missing.append(f'{manifest}: invalid JSON ({exc})')
    if 'marketplace.json' in parsed:
        missing += check_codex_compat(root, parsed['marketplace.json'])
    if args.admission:
        admission = root / 'manifest/external-plugin-admission.yaml'
        missing += check_admission(admission) if admission.is_file() else [f'{admission}: missing']
    if missing:
        print('\n'.join(missing), file=sys.stderr)
        return 1
    print('PASS manifest files, Codex compatibility' + (' and external-plugin admission' if args.admission else ''))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
