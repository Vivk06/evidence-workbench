#!/usr/bin/env python3
"""Read a repository's workbench profile from the YAML frontmatter of its AGENTS.md.

Standard library only. Parses the YAML subset the profile templates use: block mappings,
block lists, single-line flow lists and maps, single- and double-quoted scalars, plain
scalars, comments. Anything else is a ProfileError (plan §3.2).

Usage: python3 profile.py [DIRECTORY]   prints the profile found from DIRECTORY as JSON.
"""
import json
import os
import re
import sys
from pathlib import Path

ARCHETYPES = {'physics', 'code', 'research'}
GIT_MODES = {'read-only', 'normal', 'none'}
KNOWN_KEYS = {
    'schema', 'archetypes', 'activation', 'python', 'git', 'commit_message', 'patches',
    'user_executed', 'agent_allowed', 'frozen_paths', 'read_only_paths', 'run_handoff',
    'authority', 'main_agent_edits_code', 'code_graph', 'codex_delegation',
    'claims_ledger', 'writing', 'test_budget',
}
KEY = re.compile(r'([A-Za-z0-9_][A-Za-z0-9_-]*)\s*:(?:\s+(.*))?$')
INT = re.compile(r'-?[0-9]+$')
DOUBLE_ESCAPES = {'"': '"', '\\': '\\', '/': '/', 'n': '\n', 't': '\t'}


class ProfileError(Exception):
    pass


# ---------------------------------------------------------------- YAML subset parser

def _strip_comment(text, lineno):
    quote = None
    i = 0
    while i < len(text):
        c = text[i]
        if quote == "'":
            if c == "'" and text[i + 1:i + 2] == "'":
                i += 1
            elif c == "'":
                quote = None
        elif quote == '"':
            if c == '\\':
                i += 1
            elif c == '"':
                quote = None
        elif c in '\'"' and (i == 0 or text[i - 1] in ' \t[{,:-'):
            quote = c
        elif c == '#' and (i == 0 or text[i - 1] in ' \t'):
            return text[:i].rstrip()
        i += 1
    if quote:
        raise ProfileError(f'line {lineno}: unterminated {quote} quote')
    return text.rstrip()


def _lines(text):
    out = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        body = raw.lstrip(' ')
        if body.startswith('\t'):
            raise ProfileError(f'line {lineno}: tab indentation')
        content = _strip_comment(body, lineno)
        if content:
            out.append((lineno, len(raw) - len(body), content))
    return out


def _quoted(text, pos, lineno):
    quote = text[pos]
    out = []
    i = pos + 1
    while i < len(text):
        c = text[i]
        if quote == "'" and c == "'":
            if text[i + 1:i + 2] == "'":
                out.append("'")
                i += 2
                continue
            return ''.join(out), i + 1
        if quote == '"' and c == '\\':
            esc = text[i + 1:i + 2]
            if esc not in DOUBLE_ESCAPES:
                raise ProfileError(f'line {lineno}: unsupported escape \\{esc} in double quotes; use single quotes')
            out.append(DOUBLE_ESCAPES[esc])
            i += 2
            continue
        if quote == '"' and c == '"':
            return ''.join(out), i + 1
        out.append(c)
        i += 1
    raise ProfileError(f'line {lineno}: unterminated {quote} quote')


def _plain(text, lineno):
    if text[0] in '&*!|>%@`':
        raise ProfileError(f'line {lineno}: unsupported YAML construct {text[0]!r}')
    if ': ' in text or text.endswith(':'):
        raise ProfileError(f'line {lineno}: unexpected mapping in scalar {text!r}')
    if text in ('null', '~', 'Null', 'NULL'):
        return None
    if text in ('true', 'True', 'TRUE'):
        return True
    if text in ('false', 'False', 'FALSE'):
        return False
    if INT.match(text):
        return int(text)
    return text


def _flow(text, pos, lineno):
    """Parse one flow value starting at pos; return (value, next position)."""
    while pos < len(text) and text[pos] == ' ':
        pos += 1
    if pos >= len(text):
        raise ProfileError(f'line {lineno}: missing value')
    c = text[pos]
    if c in '\'"':
        return _quoted(text, pos, lineno)
    if c in '[{':
        close = ']' if c == '[' else '}'
        items = [] if c == '[' else {}
        pos += 1
        while True:
            while pos < len(text) and text[pos] == ' ':
                pos += 1
            if pos >= len(text):
                raise ProfileError(f'line {lineno}: unclosed {c} (flow collections must fit on one line)')
            if text[pos] == close:
                return items, pos + 1
            if c == '[':
                value, pos = _flow(text, pos, lineno)
                items.append(value)
            else:
                match = re.compile(r'([A-Za-z0-9_][A-Za-z0-9_-]*)\s*:\s').match(text, pos)
                if not match:
                    raise ProfileError(f'line {lineno}: expected "key: value" in flow map')
                if match.group(1) in items:
                    raise ProfileError(f'line {lineno}: duplicate key {match.group(1)!r}')
                value, pos = _flow(text, match.end(), lineno)
                items[match.group(1)] = value
            while pos < len(text) and text[pos] == ' ':
                pos += 1
            if pos < len(text) and text[pos] == ',':
                pos += 1
            elif pos < len(text) and text[pos] != close:
                raise ProfileError(f'line {lineno}: expected "," or {close!r}')
    end = pos
    while end < len(text) and text[end] not in ',]}':
        end += 1
    return _plain(text[pos:end].strip(), lineno), end


def _scalar(text, lineno):
    if text[0] in '\'"[{':
        value, end = _flow(text, 0, lineno)
        if text[end:].strip():
            raise ProfileError(f'line {lineno}: unexpected text after value: {text[end:].strip()!r}')
        return value
    return _plain(text, lineno)


def _block(lines, i, indent):
    if lines[i][2].startswith('- ') or lines[i][2] == '-':
        return _list(lines, i, indent)
    return _mapping(lines, i, indent)


def _nested(lines, i, indent, lineno, allow_same_indent_list):
    """Value on the lines after a 'key:' or '-' with nothing after it."""
    if i < len(lines) and lines[i][1] > indent:
        return _block(lines, i, lines[i][1])
    if allow_same_indent_list and i < len(lines) and lines[i][1] == indent and lines[i][2].startswith('-'):
        return _list(lines, i, indent)
    return None, i


def _mapping(lines, i, indent):
    out = {}
    while i < len(lines) and lines[i][1] == indent and not lines[i][2].startswith('- '):
        lineno, _, content = lines[i]
        match = KEY.match(content)
        if not match:
            raise ProfileError(f'line {lineno}: expected "key: value", got {content!r}')
        key, rest = match.group(1), match.group(2)
        if key in out:
            raise ProfileError(f'line {lineno}: duplicate key {key!r}')
        if rest:
            out[key] = _scalar(rest, lineno)
            i += 1
        else:
            out[key], i = _nested(lines, i + 1, indent, lineno, True)
    if i < len(lines) and lines[i][1] > indent:
        raise ProfileError(f'line {lines[i][0]}: unexpected indentation')
    return out, i


def _list(lines, i, indent):
    out = []
    while i < len(lines) and lines[i][1] == indent and (lines[i][2].startswith('- ') or lines[i][2] == '-'):
        lineno, _, content = lines[i]
        item = content[1:].lstrip(' ')
        if not item:
            value, i = _nested(lines, i + 1, indent, lineno, False)
            out.append(value)
        elif item[0] not in '\'"[{' and KEY.match(item):
            # "- key: value" opens a mapping whose keys align with the text after "- ".
            item_indent = indent + len(content) - len(item)
            value, used = _mapping([(lineno, item_indent, item)] + lines[i + 1:], 0, item_indent)
            out.append(value)
            i += used
        else:
            out.append(_scalar(item, lineno))
            i += 1
    if i < len(lines) and lines[i][1] > indent:
        raise ProfileError(f'line {lines[i][0]}: unexpected indentation')
    return out, i


def parse_yaml(text):
    lines = _lines(text)
    if not lines:
        return None
    if lines[0][1] != 0:
        raise ProfileError(f'line {lines[0][0]}: top level must not be indented')
    value, i = _block(lines, 0, 0)
    if i != len(lines):
        raise ProfileError(f'line {lines[i][0]}: unexpected content')
    return value


# ---------------------------------------------------------------- writer (inverse of parse_yaml)

KEY_ORDER = ['schema', 'archetypes', 'activation', 'python', 'git', 'commit_message', 'patches', 'test_budget',
             'user_executed', 'agent_allowed', 'frozen_paths', 'read_only_paths', 'run_handoff', 'authority',
             'main_agent_edits_code', 'code_graph', 'claims_ledger', 'writing', 'codex_delegation']
PLAIN = re.compile(r'[A-Za-z0-9_./<>@~-]+$')


def _dump_scalar(value):
    if value is None:
        return 'null'
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, int):
        return str(value)
    text = str(value)
    if PLAIN.match(text) and _plain(text, 0) == text:
        return text
    return "'" + text.replace("'", "''") + "'"


def _dump_flow(value):
    if isinstance(value, list):
        return '[' + ', '.join(_dump_flow(v) for v in value) + ']'
    if isinstance(value, dict):
        return '{' + ', '.join(f'{k}: {_dump_flow(v)}' for k, v in value.items()) + '}'
    return _dump_scalar(value)


def _dump_value(key, value, indent):
    pad = ' ' * indent
    if isinstance(value, dict) and value and any(isinstance(v, dict) for v in value.values()):
        lines = [f'{pad}{key}:']
        for k, v in value.items():
            lines += _dump_value(k, v, indent + 2)
        return lines
    if isinstance(value, list) and any(isinstance(v, dict) for v in value):
        return [f'{pad}{key}:'] + [f'{pad}  - {_dump_flow(v)}' for v in value]
    return [f'{pad}{key}: {_dump_flow(value)}']


def dump(profile):
    """YAML text for a `workbench:` block that parse_yaml reads back to the same profile."""
    keys = [k for k in KEY_ORDER if k in profile] + sorted(set(profile) - set(KEY_ORDER))
    lines = ['workbench:']
    for key in keys:
        lines += _dump_value(key, profile[key], 2)
    return '\n'.join(lines) + '\n'


# ---------------------------------------------------------------- profile schema 1

def _strings(profile, key):
    value = profile.get(key, [])
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise ProfileError(f'{key} must be a list of strings')
    return value


def _regex(pattern, where):
    try:
        return re.compile(pattern)
    except re.error as exc:
        raise ProfileError(f'{where}: invalid regex {pattern!r} ({exc})')


def validate(profile):
    """Check a parsed `workbench:` mapping against schema 1; return it with defaults filled."""
    if not isinstance(profile, dict):
        raise ProfileError('workbench must be a mapping')
    unknown = sorted(set(profile) - KNOWN_KEYS)
    if unknown:
        raise ProfileError(f'unknown keys: {", ".join(unknown)}')
    if profile.get('schema') != 1:
        raise ProfileError('schema must be 1')
    archetypes = profile.get('archetypes')
    if not isinstance(archetypes, list) or not archetypes or not set(archetypes) <= ARCHETYPES:
        raise ProfileError(f'archetypes must be a non-empty list from {sorted(ARCHETYPES)}')
    git = profile.setdefault('git', 'normal')
    if git not in GIT_MODES:
        raise ProfileError(f'git must be one of {sorted(GIT_MODES)}')
    for key in ('activation', 'python', 'commit_message', 'patches', 'code_graph', 'claims_ledger'):
        if profile.get(key) is not None and not isinstance(profile[key], str):
            raise ProfileError(f'{key} must be a string')
    for key in ('run_handoff', 'authority', 'writing'):
        if not isinstance(profile.setdefault(key, {}), dict):
            raise ProfileError(f'{key} must be a mapping')
    if not isinstance(profile.setdefault('main_agent_edits_code', True), bool):
        raise ProfileError('main_agent_edits_code must be true or false')
    if profile.get('codex_delegation', 'print-only') != 'print-only':
        raise ProfileError('codex_delegation must be print-only')
    user_executed = profile.setdefault('user_executed', [])
    if not isinstance(user_executed, list):
        raise ProfileError('user_executed must be a list')
    for n, rule in enumerate(user_executed):
        where = f'user_executed[{n}]'
        if not isinstance(rule, dict) or not isinstance(rule.get('pattern'), str) or not isinstance(rule.get('why'), str):
            raise ProfileError(f'{where} needs string pattern and why')
        if set(rule) - {'pattern', 'why', 'codex_prefix'}:
            raise ProfileError(f'{where}: unknown keys {sorted(set(rule) - {"pattern", "why", "codex_prefix"})}')
        prefix = rule.get('codex_prefix')
        if prefix is not None and not (isinstance(prefix, list) and all(isinstance(t, (str, list)) for t in prefix)):
            raise ProfileError(f'{where}: codex_prefix must be a token list')
        _regex(rule['pattern'], where)
    allowed = profile.setdefault('agent_allowed', [])
    if not isinstance(allowed, list):
        raise ProfileError('agent_allowed must be a list')
    for n, entry in enumerate(allowed):
        where = f'agent_allowed[{n}]'
        if isinstance(entry, dict):
            if not isinstance(entry.get('pattern'), str) or set(entry) - {'pattern', 'when'}:
                raise ProfileError(f'{where} must be a string or {{pattern, when}}')
            _regex(entry['pattern'], where)
        elif not isinstance(entry, str):
            raise ProfileError(f'{where} must be a string or {{pattern, when}}')
    budget = profile.get('test_budget')
    if isinstance(budget, dict):
        if set(budget) - {'max', 'paths'} or not isinstance(budget.get('max'), int) or budget['max'] < 1 \
                or not isinstance(budget.get('paths', []), list) or not all(isinstance(p, str) for p in budget.get('paths', [])):
            raise ProfileError('test_budget must be a positive integer or {max, paths}')
    elif budget is not None and (not isinstance(budget, int) or isinstance(budget, bool) or budget < 1):
        raise ProfileError('test_budget must be a positive integer or {max, paths}')
    profile['frozen_paths'] = _strings(profile, 'frozen_paths')
    profile['read_only_paths'] = _strings(profile, 'read_only_paths')
    return profile


# ---------------------------------------------------------------- AGENTS.md lookup

def find_agents_md(project_dir=None, cwd=None):
    if project_dir and (Path(project_dir) / 'AGENTS.md').is_file():
        return Path(project_dir) / 'AGENTS.md'
    here = Path(cwd or os.getcwd()).absolute()
    for directory in (here, *here.parents):
        if (directory / 'AGENTS.md').is_file():
            return directory / 'AGENTS.md'
    return None


def read_profile(agents_md, validated=True):
    """Return the profile in AGENTS.md (validated, or as written), or None when it declares none."""
    text = Path(agents_md).read_text(encoding='utf-8', errors='replace').lstrip('﻿').replace('\r\n', '\n')
    if not text.startswith('---\n'):
        return None
    lines = text.split('\n')
    try:
        end = next(n for n, line in enumerate(lines[1:], 1) if line.rstrip() in ('---', '...'))
    except StopIteration:
        if any(re.match(r'workbench:\s*$', line) for line in lines):
            raise ProfileError('AGENTS.md frontmatter is not closed with ---')
        return None
    frontmatter = '\n'.join(lines[1:end])
    # Other tools' frontmatter may use YAML this parser does not read; only a workbench key opts in.
    if not re.search(r'^workbench:\s*$', frontmatter, re.M):
        return None
    data = parse_yaml(frontmatter)
    if not isinstance(data, dict):
        raise ProfileError('AGENTS.md frontmatter must be a mapping')
    return validate(data['workbench']) if validated else data['workbench']


def load(project_dir=None, cwd=None, validated=True):
    """Return (profile or None, repository root or None). Raises ProfileError."""
    agents_md = find_agents_md(project_dir, cwd)
    if agents_md is None:
        return None, None
    profile = read_profile(agents_md, validated)
    return profile, (agents_md.parent if profile is not None else None)


def main(argv):
    directory = argv[1] if len(argv) > 1 else os.getcwd()
    try:
        profile, root = load(project_dir=directory, cwd=directory)
    except ProfileError as exc:
        print(f'profile error: {exc}', file=sys.stderr)
        return 1
    print(json.dumps({'root': str(root) if root else None, 'profile': profile}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
