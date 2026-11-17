#!/usr/bin/env python3
"""Profile-driven guard hook for Claude Code and Codex.

Usage (from hooks/hooks.json): python3 guard.py pre-tool-use|session-start  < hook JSON

PreToolUse on a shell command: the command is split into simple commands (`;`, `&&`,
`||`, `|`, `&`, newlines, subshells, `$(...)`, backticks, `bash -c '...'`), and wrappers
(`env X=1`, `sudo`, `nohup`, `time`, `timeout`, `nice`, `stdbuf`, `taskset`, `exec`,
leading `$(...)`) are removed. A simple command matching `agent_allowed` passes; one
matching a `user_executed` pattern is denied with a hand-over message. When the
working directory changed through `cd`, patterns also see `cd <dir>/ && <command>`.
Text tools (grep, cat, echo, ...) and git are not matched against `user_executed`, so
searching for or printing a reserved command is not blocked. With `git: read-only`, a
git write aimed at the profile's repository is denied; git in other directories,
such as a shadow repository in /tmp, is allowed.

PreToolUse on a file edit (Edit, Write, NotebookEdit; Codex apply_patch): a target under
`frozen_paths` or `read_only_paths` is denied. An edit that adds tests beyond the profile's
`test_budget` gets a reminder in the agent's context, never a denial.

SessionStart: states the profile's archetypes, activation and guards, never AGENTS.md
content, or reports a malformed profile.

No profile: no output. Malformed profile or any guard failure: a warning on stderr and
the tool call is allowed; guards are a safety net, the rules stay in AGENTS.md.
"""
import importlib.util
import json
import os
import re
import shlex
import sys
from pathlib import Path



def _load(name, filename):
    # Loaded by path: the name `profile` would otherwise collide with the standard library.
    spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parent / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


workbench_profile = _load('workbench_profile', 'profile.py')

SHELL_TOOLS = {'Bash', 'Monitor'}
EDIT_TOOLS = {'Edit', 'Write', 'NotebookEdit', 'apply_patch'}
SHELLS = {'bash', 'sh', 'zsh', 'dash', 'ksh'}
TEXT_TOOLS = {
    'grep', 'egrep', 'fgrep', 'rg', 'ag', 'ack', 'find', 'fd', 'locate', 'cat', 'bat', 'less',
    'more', 'head', 'tail', 'wc', 'ls', 'tree', 'file', 'stat', 'echo', 'printf', 'diff', 'cmp',
    'which', 'whereis', 'type', 'man', 'sort', 'uniq', 'cut', 'awk', 'sed', 'jq', 'yq', 'column',
}
GIT_WRITES = {'commit', 'push', 'rm', 'mv', 'reset', 'merge', 'rebase', 'cherry-pick', 'revert',
              'am', 'pull', 'add'}
GIT_OPTIONS_WITH_VALUE = {'-c', '--namespace', '--exec-path', '--config-env'}
CONTEXT_LIMIT = 1500
PATCH_TARGET = re.compile(r'^\*\*\* (?:Add File|Update File|Delete File|Move to): (.+?)\s*$', re.M)
ASSIGNMENT = re.compile(r'[A-Za-z_][A-Za-z0-9_]*=')


# ---------------------------------------------------------------- shell splitting

def _closing(text, start, open_char, close_char):
    """Index of the bracket closing text[start] (an open_char), skipping quotes."""
    depth, i, quote = 0, start, None
    while i < len(text):
        c = text[i]
        if quote:
            if c == '\\' and quote == '"':
                i += 1
            elif c == quote:
                quote = None
        elif c in '\'"':
            quote = c
        elif c == '\\':
            i += 1
        elif c == open_char:
            depth += 1
        elif c == close_char:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return len(text) - 1


def split_shell(command):
    """Return items ('cmd', raw, without_substitutions, substitutions), ('open',) or ('close',)."""
    items, raw, bare, subs = [], [], [], []
    i, quote, heredocs = 0, None, []

    def flush():
        text = ''.join(raw).strip()
        if text:
            items.append(('cmd', text, ''.join(bare).strip(), list(subs)))
        raw.clear(), bare.clear(), subs.clear()

    while i < len(command):
        c = command[i]
        if quote == "'":
            raw.append(c), bare.append(c)
            if c == "'":
                quote = None
        elif c == '$' and command[i + 1:i + 2] == '(':
            end = _closing(command, i + 1, '(', ')')
            subs.append(command[i + 2:end])
            raw.append(command[i:end + 1])
            i = end
        elif c == '`':
            end = command.find('`', i + 1)
            end = len(command) if end < 0 else end
            subs.append(command[i + 1:end])
            raw.append(command[i:end + 1])
            i = end
        elif quote == '"':
            raw.append(c), bare.append(c)
            if c == '\\':
                raw.append(command[i + 1:i + 2]), bare.append(command[i + 1:i + 2])
                i += 1
            elif c == '"':
                quote = None
        elif c in '\'"':
            quote = c
            raw.append(c), bare.append(c)
        elif c == '\\':
            raw.append(command[i:i + 2]), bare.append(command[i:i + 2])
            i += 1
        elif c == '&' and (command[i - 1:i] in '<>' and i > 0 or command[i + 1:i + 2] == '>'):
            raw.append(c), bare.append(c)  # redirections such as 2>&1 and &>file
        elif c == '<' and command[i:i + 2] == '<<' and command[i + 2:i + 3] != '<':
            match = re.compile(r'<<(-?)\s*([\'"]?)([A-Za-z0-9_.-]+)\2').match(command, i)
            if match:
                heredocs.append((match.group(3), bool(match.group(1))))
                raw.append(match.group(0)), bare.append(match.group(0))
                i = match.end() - 1
            else:
                raw.append(c), bare.append(c)
        elif c == '\n' and heredocs:
            flush()
            # A heredoc body is data, not commands: skip it up to its delimiter line.
            for word, strip_tabs in heredocs:
                while True:
                    end = command.find('\n', i + 1)
                    line = command[i + 1:end if end >= 0 else len(command)]
                    i = end if end >= 0 else len(command)
                    if (line.lstrip('\t') if strip_tabs else line) == word or end < 0:
                        break
            heredocs.clear()
        elif c in ';&|\n':
            flush()
            if command[i + 1:i + 2] == c and c in '&|':
                i += 1
        elif c == '(' and not ''.join(raw).strip():
            items.append(('open',))
        elif c == ')':
            flush()
            items.append(('close',))
        else:
            raw.append(c), bare.append(c)
        i += 1
    flush()
    return items


def _tokens(text):
    try:
        return shlex.split(text)
    except ValueError:
        return text.split()


def strip_wrappers(tokens):
    """Drop leading assignments and wrapper programs; return the tokens of the real command."""
    t = list(tokens)
    while t:
        word = os.path.basename(t[0])
        if ASSIGNMENT.match(t[0]):
            t.pop(0)
        elif word == 'env':
            t.pop(0)
            while t and (t[0].startswith('-') or ASSIGNMENT.match(t[0])):
                if t.pop(0) in ('-u', '--unset', '-C', '--chdir', '-S') and t:
                    t.pop(0)
        elif word in ('sudo', 'nohup', 'time', 'exec', 'command', 'builtin', 'xargs'):
            t.pop(0)
            while t and t[0].startswith('-'):
                t.pop(0)
        elif word == 'nice':
            t.pop(0)
            if t and t[0] == '-n':
                t[:2] = []
            elif t and re.match(r'-\d+$', t[0]):
                t.pop(0)
        elif word == 'timeout':
            t.pop(0)
            while t and t[0].startswith('-'):
                if t.pop(0) in ('-k', '--kill-after', '-s', '--signal') and t:
                    t.pop(0)
            if t:
                t.pop(0)
        elif word == 'stdbuf':
            t.pop(0)
            while t and t[0].startswith('-'):
                t.pop(0)
        elif word == 'taskset':
            t.pop(0)
            while t and t[0].startswith('-'):
                if t.pop(0) in ('-c', '--cpu-list') and t:
                    t.pop(0)
            if t and not t[0].startswith('-'):
                t.pop(0)
        else:
            break
    return t


def _shell_script(tokens):
    """The script of `bash -c '...'`-style wrappers, else None."""
    if not tokens or os.path.basename(tokens[0]) not in SHELLS:
        return None
    for n, tok in enumerate(tokens[1:], 1):
        if re.match(r'-[a-zA-Z]*c[a-zA-Z]*$', tok):
            return tokens[n + 1] if n + 1 < len(tokens) else None
        if not tok.startswith('-'):
            return None
    return None


# ---------------------------------------------------------------- decisions

def _resolve(path, base):
    path = Path(os.path.expanduser(str(path)))
    return Path(os.path.realpath(path if path.is_absolute() else Path(base) / path))


def _inside(path, base):
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def _git_target_and_write(tokens, cwd):
    """For a git command, return (directory it acts on, whether it writes)."""
    target, i = cwd, 1
    while i < len(tokens) and tokens[i].startswith('-'):
        opt = tokens[i]
        if opt == '-C' and i + 1 < len(tokens):
            target = _resolve(tokens[i + 1], target)
            i += 1
        elif opt.startswith('--work-tree=') or opt.startswith('--git-dir='):
            target = _resolve(opt.split('=', 1)[1], target)
        elif opt in GIT_OPTIONS_WITH_VALUE:
            i += 1
        i += 1
    if i >= len(tokens):
        return target, False
    sub, args = tokens[i], tokens[i + 1:]
    positional = [a for a in args if not a.startswith('-')]
    if sub in GIT_WRITES:
        return target, True
    if sub == 'tag':
        return target, not {'-l', '--list'} & set(args) and bool(positional or {'-d', '-a', '-s', '-f', '--delete'} & set(args))
    if sub == 'branch':
        return target, bool({'-d', '-D', '-m', '-M', '-c', '-C', '-f', '--delete', '--move', '--copy', '--force'} & set(args)) or (
            bool(positional) and not {'-l', '--list', '--contains', '--merged', '--no-merged', '--points-at'} & set(args))
    if sub == 'stash':
        return target, not args or args[0] not in ('list', 'show')
    if sub == 'restore':
        return target, any(a in ('--staged', '-S') or re.match(r'-[A-Za-z]*S', a) for a in args)
    if sub == 'checkout':
        return target, '--' in args
    if sub == 'apply':
        return target, bool({'--cached', '--index'} & set(args))
    return target, False


class ShellGuard:
    def __init__(self, profile, root, command):
        self.profile, self.root, self.command = profile, root, command
        self.notes = []
        self.rules = [(re.compile(r['pattern']), r['why']) for r in profile['user_executed']]
        self.allowed = []
        for entry in profile['agent_allowed']:
            if isinstance(entry, dict):
                self.allowed.append(('regex', re.compile(entry['pattern']), entry.get('when')))
            else:
                self.allowed.append(('prefix', entry, ' '.join(strip_wrappers(_tokens(entry)))))

    def check(self, text, cwd, start):
        """Return a deny reason for the shell text run in cwd, or None."""
        stack = [cwd]
        for item in split_shell(text):
            if item[0] == 'open':
                stack.append(stack[-1])
                continue
            if item[0] == 'close':
                if len(stack) > 1:
                    stack.pop()
                continue
            _, raw, bare, subs = item
            for inner in subs:
                reason = self.check(inner, stack[-1], start)
                if reason:
                    return reason
            tokens = strip_wrappers(_tokens(bare))
            if not tokens:
                continue
            script = _shell_script(tokens)
            if script is not None:
                reason = self.check(script, stack[-1], start)
                if reason:
                    return reason
                continue
            program = os.path.basename(tokens[0])
            if program in ('cd', 'pushd'):
                if len(tokens) == 1 or tokens[1] == '~':
                    stack[-1] = Path(os.path.expanduser('~'))
                elif tokens[1] != '-':
                    stack[-1] = _resolve(tokens[1], stack[-1])
                continue
            reason = self._simple(raw, tokens, program, stack[-1], start)
            if reason:
                return reason
        return None

    def _simple(self, raw, tokens, program, cwd, start):
        norm = ' '.join(tokens)
        for kind, pattern, extra in self.allowed:
            if kind == 'prefix' and (raw.startswith(pattern) or (extra and norm.startswith(extra))):
                return None
            if kind == 'regex' and (pattern.search(raw) or pattern.search(norm)):
                if extra:
                    self.notes.append(f'Profile note for `{norm}`: {extra}')
                return None
        if program == 'git':
            target, writes = _git_target_and_write(tokens, cwd)
            if writes and self.profile['git'] == 'read-only' and _inside(target, self.root):
                message = self.profile.get('commit_message') or 'logs/commit_<topic>.txt'
                return (f'Git is read-only for the agent in this repository. Write the commit message '
                        f'to {message} and print this exact command for the user instead: {self.command}')
            return None
        if program in TEXT_TOOLS:
            return None
        views = [norm] + ([f'cd {cwd}/ && {norm}'] if cwd != start else [])
        for pattern, why in self.rules:
            if any(pattern.search(view) for view in views):
                return f'Reserved for the user ({why}). Print this exact command for the user instead: {self.command}'
        return None


def edit_targets(tool, tool_input):
    if tool == 'apply_patch':
        return PATCH_TARGET.findall(tool_input.get('command') or tool_input.get('patch') or '')
    path = tool_input.get('file_path') or tool_input.get('notebook_path')
    return [path] if isinstance(path, str) else []


def check_edit(profile, root, tool, tool_input, cwd):
    route = (profile['authority'].get('decisions') or {})
    route = route.get('path') if isinstance(route, dict) else route
    route_text = f'a decision record in {route}' if route else 'a recorded decision (ADR)'
    for raw in edit_targets(tool, tool_input):
        target = _resolve(raw, cwd)
        for entry in profile['frozen_paths']:
            if _inside(target, _resolve(entry.rstrip('/'), root)):
                return (f'{raw} is frozen in this repository profile (frozen_paths: {entry}). Change it only '
                        f'through {route_text}: propose the change and hand it to the user.')
        for entry in profile['read_only_paths']:
            if _inside(target, _resolve(entry.rstrip('/'), root)):
                return f'{raw} is read-only for the agent (read_only_paths: {entry}); do not edit it from this repository.'
    return None


def _budget(profile):
    value = profile.get('test_budget')
    if isinstance(value, dict):
        return value['max'], value.get('paths') or None
    return (value, None) if isinstance(value, int) else (None, None)


def test_budget_note(profile, root, tool, tool_input, cwd):
    """A reminder when an edit adds tests beyond the profile's test budget; never a denial."""
    maximum, paths = _budget(profile)
    if maximum is None:
        return None
    audit_tests = _load('workbench_audit_tests', 'audit_tests.py')
    added = 0
    if tool == 'apply_patch':
        patch = tool_input.get('command') or ''
        added = sum(1 for line in patch.splitlines() if audit_tests.TEST_DEF.match(line[1:]) and line.startswith('+')) \
            - sum(1 for line in patch.splitlines() if audit_tests.TEST_DEF.match(line[1:]) and line.startswith('-'))
    else:
        target = edit_targets(tool, tool_input)
        if not target or not audit_tests.is_test_file(target[0]):
            return None
        if tool == 'Write':
            path = _resolve(target[0], cwd)
            old = path.read_text(errors='replace') if path.is_file() else ''
            added = audit_tests.count_test_defs(tool_input.get('content')) - audit_tests.count_test_defs(old)
        else:
            added = audit_tests.count_test_defs(tool_input.get('new_string')) - audit_tests.count_test_defs(tool_input.get('old_string'))
    if added <= 0:
        return None
    current = audit_tests.audit(root, paths)['collected_estimate']
    if current + added <= maximum:
        return None
    return (f'Test budget: this edit adds {added} test(s) to a suite of about {current} with a budget of '
            f'{maximum} (profile test_budget). Extend an existing table-driven test or merge overlapping tests '
            f'instead, and name the realistic failure each new test catches (test-value-audit skill).')


def session_context(profile, root):
    parts = [f'Workbench profile in {root}/AGENTS.md: archetypes {", ".join(profile["archetypes"])}.']
    if profile.get('activation'):
        parts.append(f'Activation: {profile["activation"]}.')
    elif profile.get('python'):
        parts.append(f'Python: {profile["python"]}.')
    guards = []
    if profile['user_executed']:
        guards.append(f'{len(profile["user_executed"])} reserved command patterns are denied and handed to the user')
    if profile['git'] == 'read-only':
        guards.append(f'git writes are denied (commit message goes to {profile.get("commit_message") or "logs/commit_<topic>.txt"})')
    if profile['frozen_paths']:
        guards.append('frozen paths: ' + ', '.join(profile['frozen_paths']))
    if profile['read_only_paths']:
        guards.append('read-only paths: ' + ', '.join(profile['read_only_paths']))
    maximum, _ = _budget(profile)
    if maximum is not None:
        guards.append(f'test budget {maximum} collected tests (reminder, not a block)')
    parts.append(('Guards: ' + '; '.join(guards) + '.') if guards else 'Guards: none configured.')
    if profile['main_agent_edits_code'] is False:
        parts.append('The main agent does not edit code; code edits go to a surgical-editor subagent.')
    parts.append('Codex runs are print-only.')
    text = ' '.join(parts)
    return text if len(text) <= CONTEXT_LIMIT else text[:CONTEXT_LIMIT - 3] + '...'


# ---------------------------------------------------------------- entry point

def emit(event, **fields):
    print(json.dumps({'hookSpecificOutput': {'hookEventName': event, **fields}}))


def run(mode, payload, env):
    cwd = payload.get('cwd') or os.getcwd()
    project_dir = env.get('CLAUDE_PROJECT_DIR')
    try:
        profile, root = workbench_profile.load(project_dir=project_dir, cwd=cwd)
    except (workbench_profile.ProfileError, OSError) as exc:
        agents_md = workbench_profile.find_agents_md(project_dir, cwd)
        message = f'Workbench profile in {agents_md} is invalid ({exc}); its guards are off until it is fixed.'
        print(f'workbench guard: {message}', file=sys.stderr)
        if mode == 'session-start':
            emit('SessionStart', additionalContext=message)
        return
    if profile is None:
        return
    root = Path(os.path.realpath(root))
    if mode == 'session-start':
        emit('SessionStart', additionalContext=session_context(profile, root))
        return
    tool = payload.get('tool_name')
    tool_input = payload.get('tool_input') or {}
    if tool in SHELL_TOOLS and isinstance(tool_input.get('command'), str):
        start = Path(os.path.realpath(cwd))
        guard = ShellGuard(profile, root, tool_input['command'])
        reason = guard.check(tool_input['command'], start, start)
        if reason:
            emit('PreToolUse', permissionDecision='deny', permissionDecisionReason=reason)
        elif guard.notes:
            emit('PreToolUse', additionalContext=' '.join(guard.notes))
    elif tool in EDIT_TOOLS:
        reason = check_edit(profile, root, tool, tool_input, cwd)
        if reason:
            emit('PreToolUse', permissionDecision='deny', permissionDecisionReason=reason)
            return
        note = test_budget_note(profile, root, tool, tool_input, cwd)
        if note:
            emit('PreToolUse', additionalContext=note)


def main(argv):
    mode = argv[1] if len(argv) > 1 else ''
    if mode not in ('pre-tool-use', 'session-start'):
        print('usage: guard.py pre-tool-use|session-start < hook JSON', file=sys.stderr)
        return 0
    try:
        run(mode, json.load(sys.stdin), os.environ)
    except Exception as exc:  # a guard failure must never block work
        print(f'workbench guard: internal error ({exc!r}); tool call allowed', file=sys.stderr)
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
