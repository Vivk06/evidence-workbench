#!/usr/bin/env python3
"""Detect what a repository is and propose its workbench setup (repo-setup skill).

Standard library only; works on any repository, with or without git or a profile. It
reads files and never runs project code.

Usage:
  python3 detect_repo.py REPO [--json] [--diff] [--apply]

Default and --json print the detection and the proposal. --diff prints the unified diff
of the files the proposal would write (AGENTS.md, .claude/settings.json,
.codex/rules/workbench.rules) and writes nothing. --apply writes exactly those files; the
repo-setup skill runs it only after the owner approved the diff.
"""
import argparse
import copy
import difflib
import importlib.util
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARKETPLACE = 'evidence-workbench'
SKIP_DIRS = {'.git', '.hg', '.svn', '.venv', 'venv', 'env', 'node_modules', '__pycache__', 'build', 'dist',
             'site-packages', '.tox', '.nox', '.mypy_cache', '.pytest_cache', '.ipynb_checkpoints'}
LANGUAGES = {'.py': 'python', '.c': 'c', '.h': 'c', '.cpp': 'c++', '.cc': 'c++', '.hpp': 'c++', '.f': 'fortran',
             '.f90': 'fortran', '.F90': 'fortran', '.jl': 'julia', '.m': 'matlab', '.js': 'javascript',
             '.ts': 'typescript', '.tsx': 'typescript', '.rs': 'rust', '.go': 'go', '.java': 'java'}
MESH_EXT = {'.su2', '.msh', '.cgns', '.vtu', '.vtk', '.exo', '.mesh', '.stl', '.ugrid', '.foam'}
LAUNCHER = re.compile(r'\b(mpirun|mpiexec|srun|sbatch)\b')
ML_PACKAGES = re.compile(r'\b(torch|tensorflow|jax|scikit-learn|sklearn|xgboost|lightgbm|keras|transformers|timm|'
                         r'open[_-]clip|pytorch-lightning|lightning)\b', re.I)
STALE_AGENTS_LINE = re.compile(r"Claude(?: Code)?\s+(?:does not|doesn't|will not|won't)\s+(?:load|read)[^.\n]*AGENTS\.md", re.I)
RENAMED_SKILLS = {'cfd-run-verdict': 'run-verdict', 'cfd-code-development': 'sim-code-development'}  # renamed at 1.0.0
FROZEN_CANDIDATES = ['reference/', 'docs/archive/', 'third_party/', 'vendor/', 'external/']
MAX_SCAN_BYTES = 200_000


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


P = _load('workbench_profile', 'profile.py')
T = _load('workbench_audit_tests', 'audit_tests.py')


def _files(root):
    for directory, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            yield Path(directory) / name


def _read(path):
    try:
        return path.read_text(encoding='utf-8', errors='replace')[:MAX_SCAN_BYTES] if path.stat().st_size else ''
    except OSError:
        return ''


def _first(root, patterns, max_depth=4):
    """Shallowest match of the first pattern that matches; owning documents live near the top."""
    for pattern in patterns:
        hits = sorted((p for p in root.glob(pattern) if len(p.relative_to(root).parts) <= max_depth
                       and not SKIP_DIRS & set(p.relative_to(root).parts)),
                      key=lambda p: (len(p.parts), str(p)))
        if hits:
            return hits[0]
    return None


def detect(root):
    root = Path(root).resolve()
    files = [p for p in _files(root)]
    rel = lambda p: p.relative_to(root).as_posix()  # noqa: E731
    languages = Counter(LANGUAGES[p.suffix] for p in files if p.suffix in LANGUAGES)
    mesh = sorted(rel(p) for p in files if p.suffix in MESH_EXT)
    launchers = sorted(rel(p) for p in files if p.suffix in ('.sh', '.py', '.bash', '') and p.name != 'AGENTS.md'
                       and (p.suffix or p.name in ('Makefile', 'makefile')) and LAUNCHER.search(_read(p)))
    dependency_text = ' '.join(_read(root / n) for n in ('pyproject.toml', 'requirements.txt', 'environment.yml',
                                                        'setup.py', 'setup.cfg', 'package.json') if (root / n).is_file())
    ml = bool(ML_PACKAGES.search(dependency_text)) or any(p.name in ('train.py', 'training.py') for p in files)
    tex = sorted(rel(p) for p in files if p.suffix in ('.tex', '.bib'))
    pdfs = [p for p in files if p.suffix == '.pdf']
    markdown = [p for p in files if p.suffix == '.md']
    ledgers = sorted((rel(p) for p in files if re.match(r'claims[-_]ledger.*\.csv$', p.name)),
                     key=lambda r: (r.count('/'), r))
    code_files = sum(languages.values())
    test_report = T.audit(root)
    test_files = T.discover(root)
    test_dirs = sorted({rel(p).split('/')[0] if '/' in rel(p) else '.' for p in test_files})
    package = {}
    if (root / 'package.json').is_file():
        try:
            package = json.loads(_read(root / 'package.json'))
        except json.JSONDecodeError:
            package = {}
    test_entry = [e for e, ok in [('verify.sh', (root / 'verify.sh').is_file()),
                                  ('pytest', bool(test_files) and languages['python'] > 0),
                                  ('npm test', 'test' in package.get('scripts', {})),
                                  ('make test', re.search(r'^test:', _read(root / 'Makefile'), re.M) is not None)] if ok]
    signals = {
        'physics': bool(mesh or launchers or (root / 'cases').is_dir()),
        'code': code_files >= 2,
        'research': bool(tex or ledgers or (root / 'papers').is_dir() or len(pdfs) >= 3
                         or (markdown and code_files == 0)),
    }
    archetypes = [a for a in ('physics', 'code', 'research') if signals[a]] or ['code']
    instruction = {n: (root / n).is_file() for n in ('AGENTS.md', 'CLAUDE.md', 'CLAUDE.local.md')}
    try:
        # Only the repository's own AGENTS.md counts; never a parent directory's.
        existing = None
        if instruction['AGENTS.md'] and P.read_profile(root / 'AGENTS.md') is not None:
            existing = P.read_profile(root / 'AGENTS.md', validated=False)
        profile_error = None
    except P.ProfileError as exc:
        existing, profile_error = None, str(exc)
    activation, python = None, None
    if (root / 'activate.sh').is_file():
        activation = 'source activate.sh'
    elif (root / 'environment.yml').is_file():
        name = re.search(r'^name:\s*(\S+)', _read(root / 'environment.yml'), re.M)
        activation = f'conda activate {name.group(1)}' if name else None
    elif (root / '.venv/bin/python').exists():
        python = '.venv/bin/python'
    authority = {}
    decisions = _first(root, ['docs/decisions', 'docs/adr', 'adr', 'decisions'])
    if decisions and decisions.is_dir():
        text = ' '.join(_read(p) for p in decisions.glob('*.md'))
        style = 'current-decision' if 'Rejected options' in text and 'Amendment' not in text else 'append-only'
        authority['decisions'] = {'path': rel(decisions) + '/', 'style': style}
    anti = _first(root, ['docs/**/anti[_-]patterns*.md', 'anti[_-]patterns*.md', 'ANTIPATTERNS*'])
    if anti:
        text = _read(anti)
        scheme = re.search(r'^\|\s*\**([A-Z]{1,3})-(\d+)', text, re.M) or re.search(r'^[-*]?\s*\**([A-Z]{1,3})-(\d+)', text, re.M)
        authority['anti_patterns'] = {'path': rel(anti), 'id': f'{scheme.group(1)}-N' if scheme else 'ID-N'}
    for key, patterns in [('roadmap', ['docs/**/roadmap*.md', 'ROADMAP.md', 'roadmap.md']),
                          ('status', ['docs/**/project_status*.md', 'STATUS.md'])]:
        hit = _first(root, patterns)
        if hit:
            authority[key] = rel(hit)
    warnings, renames = [], []
    if instruction['CLAUDE.md'] or instruction['CLAUDE.local.md']:
        warnings.append('CLAUDE.md or CLAUDE.local.md exists, so Claude Code reads it instead of AGENTS.md; '
                        'add an @AGENTS.md line to CLAUDE.md or move its rules into AGENTS.md')
    for path in [root / 'AGENTS.md', root / 'CLAUDE.md'] + sorted(root.glob('docs/**/*.md')):
        if not path.is_file():
            continue
        for n, line in enumerate(_read(path).splitlines(), 1):
            if path.name == 'AGENTS.md' and STALE_AGENTS_LINE.search(line):
                warnings.append(f'{rel(path)}:{n}: says Claude Code does not read AGENTS.md; that is no longer true')
            for old, new in RENAMED_SKILLS.items():
                if old in line:
                    renames.append({'path': rel(path), 'line': n, 'old': old, 'new': new})
    if profile_error:
        warnings.append(f'existing profile is invalid: {profile_error}')
    return {
        'root': str(root), 'git': (root / '.git').exists(), 'instruction_files': instruction,
        'existing_profile': existing, 'languages': dict(languages), 'mesh_files': mesh[:10],
        'launcher_files': launchers[:10], 'ml': ml, 'latex': tex[:10], 'claims_ledgers': ledgers,
        'test_entry_points': test_entry, 'test_dirs': [d for d in test_dirs if d != '.'],
        'tests_collected': test_report['collected_estimate'], 'signals': signals, 'archetypes': archetypes,
        'activation': activation, 'python': python, 'authority': authority,
        'frozen_candidates': [c for c in FROZEN_CANDIDATES if (root / c).is_dir()],
        'code_graph': 'graphify' if (root / 'graphify-out').is_dir() else None,
        'warnings': warnings, 'renames': renames,
    }


def _detected_additions(found, archetypes):
    """Facts detection can add to a profile: environment, tests, frozen dirs, authority, tools."""
    add = {}
    if found['activation']:
        add['activation'] = found['activation']
    elif found['python']:
        add['python'] = found['python']
    if found['frozen_candidates']:
        add['frozen_paths'] = found['frozen_candidates']
    if found['authority']:
        add['authority'] = found['authority']
    if found['code_graph']:
        add['code_graph'] = found['code_graph']
    if found['claims_ledgers'] and 'research' in archetypes:
        add['claims_ledger'] = found['claims_ledgers'][0]
    return add


def propose(found):
    """Proposed profile, enabled plugins and Codex rules for a detection result."""
    existing = found['existing_profile']
    if existing:
        # Keep the owner's profile as written; add only detected facts it lacks.
        profile = copy.deepcopy(existing)
        for key, value in _detected_additions(found, profile['archetypes']).items():
            if key == 'authority':
                current = profile.get('authority', {})
                profile['authority'] = {**current, **{k: v for k, v in value.items() if k not in current}}
            elif key not in profile and not (key in ('activation', 'python') and ('activation' in profile or 'python' in profile)):
                profile[key] = value
    else:
        template = P.parse_yaml((HERE.parent / 'profiles/templates' / f"{found['archetypes'][0]}.yaml").read_text())['workbench']
        profile = copy.deepcopy(template)
        profile['archetypes'] = found['archetypes']
        profile.pop('activation', None)
        profile['git'] = profile.get('git', 'normal') if found['git'] else 'none'
        if not found['git']:
            profile.pop('commit_message', None)
            profile.pop('patches', None)
        if 'research' not in found['archetypes']:
            profile.pop('writing', None)
        profile.update(_detected_additions(found, found['archetypes']))
        profile = {k: v for k, v in profile.items() if v not in ([], {}, None)}
    P.validate(copy.deepcopy(profile))
    archetypes = profile['archetypes']
    plugins = ['workbench-core'] + [p for p, on in [('sim-validity', 'physics' in archetypes),
                                                    ('ml-validity', found['ml'] and 'code' in archetypes),
                                                    ('research-writing', 'research' in archetypes)] if on]
    rules = []
    for rule in profile.get('user_executed', []):
        if rule.get('codex_prefix'):
            justification = (rule['why'] + '. Print the command for the user instead.').replace('"', "'")
            rules.append(f'prefix_rule(pattern={json.dumps(rule["codex_prefix"])}, decision="forbidden", '
                         f'justification="{justification}")')
    return {'profile': profile, 'plugins': plugins, 'codex_rules': rules}


# ---------------------------------------------------------------- files

def agents_md_text(root, profile):
    path = Path(root) / 'AGENTS.md'
    block = P.dump(profile)
    if not path.is_file():
        return f'---\n{block}---\n# Agent instructions\n\nRepository rules for coding agents go here.\n'
    text = path.read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        return f'---\n{block}---\n{text}'
    lines = text.split('\n')
    end = next((n for n, line in enumerate(lines[1:], 1) if line.rstrip() in ('---', '...')), None)
    if end is None:
        return f'---\n{block}---\n{text}'
    front = lines[1:end]
    start = next((n for n, line in enumerate(front) if re.match(r'workbench:\s*$', line)), None)
    if start is not None:
        stop = next((n for n in range(start + 1, len(front)) if front[n] and not front[n].startswith(' ')), len(front))
        front = front[:start] + front[stop:]
    return '\n'.join(['---'] + front + block.rstrip('\n').split('\n') + lines[end:])


def settings_text(root, plugins, profile):
    path = Path(root) / '.claude/settings.json'
    settings = json.loads(path.read_text()) if path.is_file() else {}
    enabled = settings.setdefault('enabledPlugins', {})
    for plugin in plugins:
        enabled[f'{plugin}@{MARKETPLACE}'] = True
    allow = settings.setdefault('permissions', {}).setdefault('allow', [])
    for entry in profile.get('agent_allowed', []):
        rule = f'Bash({entry} *)' if isinstance(entry, str) else None
        if rule and rule not in allow:
            allow.append(rule)
    if not allow:
        del settings['permissions']['allow']
        if not settings['permissions']:
            del settings['permissions']
    return json.dumps(settings, indent=2) + '\n'


def rules_text(rules):
    if not rules:
        return None
    return ('# Generated by repo-setup from the workbench profile (codex_prefix); reserved commands go to the user.\n'
            + '\n'.join(rules) + '\n')


def planned_files(root, proposal):
    files = {'AGENTS.md': agents_md_text(root, proposal['profile']),
             '.claude/settings.json': settings_text(root, proposal['plugins'], proposal['profile'])}
    rules = rules_text(proposal['codex_rules'])
    if rules:
        files['.codex/rules/workbench.rules'] = rules
    return files


def diff(root, files):
    out = []
    for name, new in files.items():
        path = Path(root) / name
        old = path.read_text(encoding='utf-8') if path.is_file() else ''
        if old != new:
            out += difflib.unified_diff(old.splitlines(True), new.splitlines(True),
                                        fromfile=f'a/{name}' if old else '/dev/null', tofile=f'b/{name}')
    return ''.join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('repo')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--diff', action='store_true')
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args(argv)
    root = Path(args.repo).resolve()
    if not root.is_dir():
        print(f'not a directory: {root}', file=sys.stderr)
        return 2
    found = detect(root)
    proposal = propose(found)
    files = planned_files(root, proposal)
    if args.apply:
        for name, text in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8')
            print(f'wrote {name}')
        return 0
    if args.diff:
        print(diff(root, files) or 'no changes')
        return 0
    print(json.dumps({'detected': found, 'proposal': proposal}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
