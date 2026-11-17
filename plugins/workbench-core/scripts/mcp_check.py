#!/usr/bin/env python3
"""Check the optional MCP servers and tool plugins for one repository (repo-setup skill).

Standard library only. It reads the repository's files, the Claude Code and Codex
configuration files that decide which servers are on in this folder, and `uv tool list`.
It never starts a server and never prints environment values. Commands and pinned
versions come from the repo-setup skill's references/tools.md.

Usage:
  python3 mcp_check.py REPO [--json]
  python3 mcp_check.py REPO --codex-project serena,playwright [--diff | --apply]

The report gives one status per tool: PASS (set up as recommended), FAIL (a needed part
is missing or unsafe), OPTIONAL (not set up here, which is fine) or INCONCLUSIVE (a
configuration file could not be read). Each line that is not PASS names the commands
that finish it. --codex-project adds the named per-project servers to the repository's
.codex/config.toml: --diff shows the change, and --apply writes it after the owner
approved the diff. Claude Code's per-project servers live in the user's own
configuration, so the report prints their commands for the owner to run.
"""
import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python before 3.11
    tomllib = None

HERE = Path(__file__).resolve().parent
TOOLS_MD = HERE.parent / 'skills/repo-setup/references/tools.md'
# name: (archetypes it serves, where it belongs, package that provides the program, program)
CATALOG = {
    'zotero': ({'research'}, 'everywhere', 'zotero-mcp-server', 'zotero-mcp'),
    'markitdown': ({'research'}, 'everywhere', 'markitdown-mcp', 'markitdown-mcp'),
    'serena': ({'code'}, 'project', 'serena-agent', 'serena'),
    'playwright': ({'research'}, 'on demand', None, 'npx'),
    'pyright-lsp': ({'code'}, 'project', 'pyright', 'pyright-langserver'),
    'session-report': ({'physics', 'code', 'research'}, 'everywhere', None, None),
}
PLUGINS = {'pyright-lsp', 'session-report'}
WRITE_KEYS = re.compile(r'API_KEY|TOKEN|SECRET', re.I)


def load_detect():
    spec = importlib.util.spec_from_file_location('workbench_detect_repo', HERE / 'detect_repo.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reference(path=TOOLS_MD):
    """Commands, pins and Codex tables from tools.md, keyed by tool name."""
    text = path.read_text(encoding='utf-8')
    found = {name: {'install': None, 'claude': None, 'codex': None, 'plugin': None, 'toml': None}
             for name in CATALOG}
    packages = {pkg: name for name, (_, _, pkg, _) in CATALOG.items() if pkg}
    for line in text.splitlines():
        line = line.strip()
        m = re.match(r'uv tool install (?:-p \S+ )?(\S+)==\S+$', line)
        if m and m.group(1) in packages:
            found[packages[m.group(1)]]['install'] = line
        m = re.match(r'(claude|codex) mcp add (\S+) ', line)
        if m and m.group(2) in found:
            found[m.group(2)][m.group(1)] = line
        m = re.match(r'claude plugin install (\S+)@\S+', line)
        if m and m.group(1) in found:
            found[m.group(1)]['plugin'] = line
    for block in re.findall(r'```toml\n(.*?)```', text, re.S):
        for table in re.split(r'\n(?=\[mcp_servers\.)', block.strip()):
            m = re.match(r'\[mcp_servers\.([\w-]+)\]', table)
            if m and m.group(1) in found:
                found[m.group(1)]['toml'] = table.strip() + '\n'
    pins = dict(re.findall(r'([\w-]+)==([\w.]+)', text))
    playwright = re.search(r'@playwright/mcp@([\d.]+)', text)
    return found, pins, playwright.group(1) if playwright else None


def read_json(path):
    if not path.is_file():
        return {}, None
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, f'{path}: {exc}'
    return (data, None) if isinstance(data, dict) else ({}, f'{path}: not a JSON object')


def read_toml(path):
    if not path.is_file():
        return {}, None
    if tomllib is None:
        return {}, f'{path}: reading TOML needs Python 3.11 or later'
    try:
        return tomllib.loads(path.read_text(encoding='utf-8')), None
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return {}, f'{path}: {exc}'


def project_folders(root):
    """The repository root and its parents up to the folder that holds .git."""
    folders = [root]
    if not (root / '.git').exists():
        for parent in root.parents:
            folders.append(parent)
            if (parent / '.git').exists():
                break
        else:
            folders = [root]
    return folders


def installed_versions():
    if not shutil.which('uv'):
        return None
    try:
        out = subprocess.run(['uv', 'tool', 'list'], capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    return dict(re.findall(r'^(\S+) v(\S+)', out, re.M))


def state(root, home=None):
    """Which servers and plugins are on for this folder, read from the configuration files.

    Precedence follows the clients. In Claude Code a local server beats a project one,
    which beats a user one, and a nearer `.mcp.json` beats an outer one. In Codex a
    project's nearer `.codex/config.toml` beats an outer one, which beats the global file;
    a project file in a folder that is not trusted is ignored, as Codex ignores it.
    """
    home = Path(home or Path.home())
    config_dir = Path(os.environ['CLAUDE_CONFIG_DIR']) if os.environ.get('CLAUDE_CONFIG_DIR') else None
    claude_json = config_dir / '.claude.json' if config_dir else home / '.claude.json'
    codex_home = Path(os.environ.get('CODEX_HOME') or home / '.codex')
    errors = []

    def load(reader, path):
        data, err = reader(path)
        errors.extend([err] if err else [])
        return data

    claude = load(read_json, claude_json)
    project_entry = (claude.get('projects') or {}).get(str(root)) or {}
    settings = [(scope, load(read_json, path)) for scope, path in (
        ('user', (config_dir or home / '.claude') / 'settings.json'),
        ('project', root / '.claude/settings.json'), ('local', root / '.claude/settings.local.json'))]
    approved = set(project_entry.get('enabledMcpjsonServers') or [])
    rejected = set(project_entry.get('disabledMcpjsonServers') or [])
    approve_all = bool(project_entry.get('enableAllProjectMcpServers'))
    for _, data in settings:
        approved |= set(data.get('enabledMcpjsonServers') or [])
        rejected |= set(data.get('disabledMcpjsonServers') or [])
        approve_all = approve_all or bool(data.get('enableAllProjectMcpServers'))
    servers = {'claude': {}, 'codex': {}}
    for name, cfg in (claude.get('mcpServers') or {}).items():
        servers['claude'][name] = ('user', cfg)
    # Every server a repository file defines, so the owner can inspect it before approving it.
    defined = []
    for folder in reversed(project_folders(root)):  # outermost first, so the nearest file wins
        for name, cfg in (load(read_json, folder / '.mcp.json').get('mcpServers') or {}).items():
            defined.append(('Claude Code', str(folder / '.mcp.json'), name, cfg))
            if name in rejected:
                servers['claude'][name] = ('project, rejected at the approval prompt', cfg)
            else:
                servers['claude'][name] = ('project' if approve_all or name in approved
                                           else 'project, waiting for approval', cfg)
    for name, cfg in (project_entry.get('mcpServers') or {}).items():
        servers['claude'][name] = ('local', cfg)
    codex = load(read_toml, codex_home / 'config.toml')
    for name, cfg in (codex.get('mcp_servers') or {}).items():
        servers['codex'][name] = ('everywhere', cfg)
    trusted = any(((codex.get('projects') or {}).get(str(f)) or {}).get('trust_level') == 'trusted'
                  for f in project_folders(root))
    untrusted = {}
    for folder in reversed(project_folders(root)):
        for name, cfg in (load(read_toml, folder / '.codex/config.toml').get('mcp_servers') or {}).items():
            defined.append(('Codex', str(folder / '.codex/config.toml'), name, cfg))
            if trusted:
                servers['codex'][name] = ('project', cfg)
            else:
                untrusted[name] = cfg
    plugins = {}
    for scope, data in settings:  # user, then project, then local: a narrower scope can turn a plugin off
        for key, on in (data.get('enabledPlugins') or {}).items():
            if on:
                plugins[key.split('@')[0]] = scope
            else:
                plugins.pop(key.split('@')[0], None)
    return {'servers': servers, 'untrusted': untrusted, 'defined': defined, 'plugins': plugins,
            'trusted': trusted, 'errors': errors, 'codex_home': str(codex_home)}


def runs(cfg):
    """The program a server entry starts, and its arguments; never its environment."""
    cfg = cfg if isinstance(cfg, dict) else {}
    args = cfg.get('args') if isinstance(cfg.get('args'), list) else []
    return Path(str(cfg.get('command') or '')).name, [str(a) for a in args]


def unexpected(name, cfg, program):
    """True when a repository file defines a catalogue server that runs something else."""
    command, args = runs(cfg)
    if name == 'playwright':
        return command != 'npx' or not any(a.startswith('@playwright/mcp@') for a in args)
    return command != program


def check(root, archetypes, home=None, versions=None):
    ref, pins, playwright_pin = reference()
    found = state(root, home)
    versions = installed_versions() if versions is None else versions
    rows = []
    for name, (serves, level, package, program) in CATALOG.items():
        if not serves & set(archetypes):
            continue
        r = ref[name]
        everywhere = level == 'everywhere'
        missing, commands, notes = [], [], []

        def gap(item, command, required=True):
            # A required gap fails the tool; an optional one is reported with its command.
            if required:
                missing.append(item)
                commands.append(command)
            else:
                notes.append(f'{item}; to add it: {command}')

        if name in PLUGINS:
            scope = found['plugins'].get(name)
            on = scope is not None
            if on:
                notes.append(f'Claude Code plugin: {scope}')
            else:
                gap('Claude Code plugin', r['plugin'] if everywhere else f'(from {root}) {r["plugin"]}',
                    required=everywhere)
        else:
            claude = found['servers']['claude'].get(name)
            if claude and 'rejected' in claude[0]:
                notes.append(f'Claude Code: {claude[0]}; it does not start until you approve it')
                claude = None
            codex = found['servers']['codex'].get(name)
            ignored = name in found['untrusted']
            on = bool(claude or codex or ignored)
            if claude and 'waiting' in claude[0]:
                gap('Claude Code approval', f'start claude in {root} and approve {name} when it asks')
            elif claude:
                notes.append(f'Claude Code: {claude[0]}')
            else:
                gap('Claude Code registration', r['claude'] if everywhere else f'(from {root}) {r["claude"]}',
                    required=everywhere)
            trust = (f'start codex in {root} and trust the folder, or add [projects."{root}"] with '
                     f'trust_level = "trusted" to {found["codex_home"]}/config.toml')
            if codex:
                notes.append(f'Codex: {codex[0]}')
                if ignored:
                    notes.append(f'Codex ignores the project entry until the folder is trusted: {trust}')
            elif ignored:
                gap('Codex trust for this folder', trust)
            else:
                gap('Codex registration', r['codex'] if everywhere else
                    f'python3 {Path(__file__).resolve()} {root} --codex-project {name} --diff, then --apply',
                    required=everywhere)
            # A repository file can name a server after a catalogue tool but run anything; such an
            # entry must never be approved or trusted on this report's word.
            for client, path, defined_name, cfg in found['defined']:
                if defined_name == name and unexpected(name, cfg, program):
                    gap(f'{client} entry in {path} runs "{runs(cfg)[0]}", not {program}',
                        f'inspect {path} and remove or correct the entry before you approve or trust it')
            for client, entry, key in (('Claude Code', claude, 'claude'), ('Codex', codex, 'codex')):
                env = (entry[1].get('env') or {}) if entry and isinstance(entry[1], dict) else {}
                if name == 'zotero' and entry and (any(WRITE_KEYS.search(k) for k in env)
                                                   or str(env.get('ZOTERO_LOCAL', '')).lower() != 'true'):
                    gap(f'{client} Zotero entry is not in read-only local mode',
                        f'{key} mcp remove zotero, then: {r[key]}')
        if program and not shutil.which(program):
            gap(f'program {program} not on PATH',
                r['install'] or 'install Node.js 18 or later', required=everywhere or on)
        elif package and versions is not None and package in pins:
            have = versions.get(package)
            if have is None:
                gap(f'{package} not installed with uv', r['install'], required=everywhere or on)
            elif have != pins[package]:
                notes.append(f'{package} {have} installed; the pinned version is {pins[package]}')
        if name == 'playwright' and on:
            notes.append(f'remove it when you are done (pinned @playwright/mcp@{playwright_pin})')
        if found['errors'] and not on:
            status = 'INCONCLUSIVE'
        elif missing:
            status = 'FAIL'
        else:
            status = 'PASS' if on else 'OPTIONAL'
        rows.append({'tool': name, 'level': level, 'status': status, 'missing': missing,
                     'commands': [c for c in commands if c], 'notes': notes})
    known = set(CATALOG)
    others = {client: sorted(n for n in found['servers'][client] if n not in known) for client in ('claude', 'codex')}
    statuses = {row['status'] for row in rows}
    verdict = 'FAIL' if 'FAIL' in statuses else 'INCONCLUSIVE' if 'INCONCLUSIVE' in statuses else 'PASS'
    return {'verdict': verdict, 'archetypes': list(archetypes), 'tools': rows, 'other_servers': others,
            'codex_trusted': found['trusted'], 'errors': found['errors'],
            'project_servers': [{'client': c, 'file': f, 'name': n, 'command': runs(cfg)[0]}
                                for c, f, n, cfg in found['defined']],
            'uv': 'not found' if versions is None else 'found'}


def codex_project_text(root, names):
    ref, _, _ = reference()
    path = root / '.codex/config.toml'
    # Write only a regular file inside the repository, never through a link to another file.
    if (root / '.codex').is_symlink() or path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise SystemExit(f'{path} is a link or leads outside the repository, so it was not changed')
    old = path.read_text(encoding='utf-8') if path.is_file() else ''
    # Parse the file, so a server written as a quoted, dotted or inline key is found too.
    if old and tomllib is None:
        raise SystemExit(f'{path} exists; changing it safely needs Python 3.11 or later')
    try:
        present = set((tomllib.loads(old).get('mcp_servers') or {}) if old else ())
    except tomllib.TOMLDecodeError as exc:
        raise SystemExit(f'{path} is not valid TOML, so it was not changed: {exc}')
    unknown = [n for n in names if not ref.get(n, {}).get('toml')]
    if unknown:
        raise SystemExit(f'no Codex table in tools.md for: {", ".join(unknown)}')
    new = old
    for name in names:
        if name not in present:
            new += ('\n' if new and not new.endswith('\n\n') else '') + ref[name]['toml']
    return old, new


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('repo')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--codex-project', help='comma-separated per-project servers for .codex/config.toml')
    ap.add_argument('--diff', action='store_true')
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args(argv)
    root = Path(args.repo).resolve()
    if not root.is_dir():
        print(f'not a directory: {root}', file=sys.stderr)
        return 2
    if args.codex_project:
        names = [n.strip() for n in args.codex_project.split(',') if n.strip()]
        old, new = codex_project_text(root, names)
        if args.apply:
            if new != old:
                (root / '.codex').mkdir(exist_ok=True)
                (root / '.codex/config.toml').write_text(new, encoding='utf-8')
                print('wrote .codex/config.toml; trust this folder in Codex so it reads the file')
            else:
                print('no changes')
            return 0
        print(load_detect().diff(root, {'.codex/config.toml': new}) or 'no changes')
        return 0
    detect = load_detect()
    # The profile's archetypes are enough; scan the repository only when there is no profile.
    try:
        profile = detect.P.read_profile(root / 'AGENTS.md', validated=False) if (root / 'AGENTS.md').is_file() else None
    except detect.P.ProfileError:
        profile = None
    archetypes = (profile or {}).get('archetypes') or detect.detect(root)['archetypes']
    report = check(root, archetypes)
    if args.json:
        print(json.dumps(report, indent=2))
        return 0 if report['verdict'] != 'FAIL' else 1
    print(f'MCP servers and tools for {root} (archetypes: {", ".join(archetypes)})')
    for row in report['tools']:
        print(f'{row["status"]:<12} {row["tool"]} ({row["level"]})')
        for item in row['missing']:
            print(f'  missing: {item}')
        for note in row['notes']:
            print(f'  {note}')
        for command in row['commands'] if row['status'] != 'PASS' else []:
            print(f'  run: {command}')
    for client, names in report['other_servers'].items():
        if names:
            print(f'other {client} servers on here: {", ".join(names)}')
    if report['project_servers']:
        print('servers the repository files define (check each before you approve or trust it):')
        for s in report['project_servers']:
            print(f'  {s["client"]}: {s["name"]} runs {s["command"] or "(no command)"} ({s["file"]})')
    for error in report['errors']:
        print(f'could not read: {error}')
    if report['uv'] == 'not found':
        print('uv not found: versions not checked; install uv first')
    print(f'verdict: {report["verdict"]}')
    return 0 if report['verdict'] != 'FAIL' else 1


if __name__ == '__main__':
    raise SystemExit(main())
