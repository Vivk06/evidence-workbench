#!/usr/bin/env python3
"""Static test-suite audit: size against a budget, low-value tests, duplicates and overlap.

Standard library only. Reads test files as syntax trees; never imports or runs them, so
it is safe in repositories where running tests is expensive.

Usage:
  python3 audit_tests.py [ROOT] [--paths P ...] [--budget N] [--json] [--check]

ROOT defaults to the current directory. Budget and paths come from the arguments, else
from `test_budget` in the repository profile (AGENTS.md frontmatter), else no budget.
`--check` exits 1 when the suite is over budget or has a high-severity finding
(no assertion, always-true assertion, exact duplicate).
"""
import argparse
import ast
import importlib.util
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

SKIP_DIRS = {'.git', '.hg', '.svn', '.venv', 'venv', 'env', 'node_modules', '__pycache__', 'build',
             'dist', 'site-packages', '.tox', '.nox', '.mypy_cache', '.pytest_cache', 'fixtures'}
HIGH = {'no-assertion', 'tautology', 'duplicate'}
MOCK_ASSERTS = {'assert_called', 'assert_called_once', 'assert_called_with', 'assert_called_once_with',
                'assert_not_called', 'assert_any_call', 'assert_has_calls', 'assert_awaited',
                'assert_awaited_once', 'assert_awaited_with'}
MOCK_ATTRS = {'called', 'call_count', 'call_args', 'call_args_list', 'await_count'}
MISUSE_ERRORS = {'TypeError', 'AttributeError'}
LARGE_PARAMETRIZE = 20
TEST_DEF = re.compile(r'^\s*(?:async\s+)?def\s+test\w*\s*\(', re.M)


# ---------------------------------------------------------------- discovery

def is_test_file(path):
    name = Path(path).name
    return name.endswith('.py') and (name.startswith('test_') or name.endswith('_test.py'))


def discover(root, paths=None):
    root = Path(root)
    starts = [root / p for p in paths] if paths else [root]
    found = []
    for start in starts:
        if start.is_file():
            found.append(start)
            continue
        for directory, dirs, files in os.walk(start):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            found += [Path(directory) / f for f in sorted(files) if is_test_file(f)]
    return found


def count_test_defs(text):
    """Number of test function definitions in source text (for edit-size estimates)."""
    return len(TEST_DEF.findall(text or ''))


# ---------------------------------------------------------------- analysis helpers

def _name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ''


def _dotted(node):
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return '.'.join(reversed(parts))


def _parametrize_cases(decorator):
    """Cases in a pytest.mark.parametrize decorator, or None when not literal."""
    if not (isinstance(decorator, ast.Call) and _dotted(decorator.func).endswith('mark.parametrize')):
        return 1
    if len(decorator.args) < 2:
        return None
    values = decorator.args[1]
    return len(values.elts) if isinstance(values, (ast.List, ast.Tuple)) else None


def _is_trivial(test):
    """An assertion that only checks existence, type, truthiness or non-emptiness."""
    if isinstance(test, (ast.Name, ast.Attribute)):
        return True
    if isinstance(test, ast.Call) and _name(test.func) in ('isinstance', 'hasattr', 'bool', 'callable', 'len'):
        return True
    if isinstance(test, ast.Compare) and len(test.ops) == 1:
        left, right, op = test.left, test.comparators[0], test.ops[0]
        if isinstance(op, ast.IsNot) and isinstance(right, ast.Constant) and right.value is None:
            return True
        if isinstance(left, ast.Call) and _name(left.func) == 'len' and isinstance(right, ast.Constant) \
                and right.value in (0, 1) and isinstance(op, (ast.Gt, ast.GtE, ast.NotEq)):
            return True
        if isinstance(op, ast.NotEq) and isinstance(right, ast.Constant) and right.value in ('', None, [], 0):
            return True
    return False


def _is_tautology(test):
    if isinstance(test, ast.Constant):
        return bool(test.value)
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not) and isinstance(test.operand, ast.Constant):
        return not test.operand.value
    if isinstance(test, ast.Compare) and len(test.ops) == 1 and isinstance(test.ops[0], (ast.Eq, ast.Is)):
        return ast.dump(test.left) == ast.dump(test.comparators[0])
    return False


def _strip_docstring(body):
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
            and isinstance(body[0].value.value, str):
        return body[1:]
    return body


class _Constants(ast.NodeTransformer):
    def visit_Constant(self, node):
        return ast.copy_location(ast.Constant(value='<c>'), node)


def _shape(body):
    tree = ast.Module(body=[ast.parse(ast.unparse(n)).body[0] for n in body], type_ignores=[])
    return ast.dump(_Constants().visit(tree))


def _private_target(call):
    """A patch call that targets a private name: monkeypatch.setattr / patch / patch.object."""
    func = _dotted(call.func)
    if not (func.endswith('setattr') or func.endswith('patch') or func.endswith('patch.object')):
        return None
    for arg in call.args[:2]:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            last = arg.value.rsplit('.', 1)[-1]
            if last.startswith('_') and not last.startswith('__'):
                return arg.value
    return None


# ---------------------------------------------------------------- per-test audit

def audit_test(node, assert_helpers):
    findings = []
    asserts = [n for n in ast.walk(node) if isinstance(n, ast.Assert)]
    calls = [n for n in ast.walk(node) if isinstance(n, ast.Call)]
    raises = [c for c in calls if _dotted(c.func).endswith(('raises', 'warns', 'assertRaises', 'assertWarns'))]
    unittest_asserts = [c for c in calls if _name(c.func).startswith('assert') and _name(c.func) not in MOCK_ASSERTS]
    mock_asserts = [c for c in calls if _name(c.func) in MOCK_ASSERTS]
    helper_calls = [c for c in calls if isinstance(c.func, ast.Name) and c.func.id in assert_helpers]
    if not (asserts or raises or unittest_asserts or mock_asserts or helper_calls):
        findings.append(('no-assertion', 'the test checks nothing'))
    tautologies = [a for a in asserts if _is_tautology(a.test)]
    if tautologies:
        findings.append(('tautology', f'always-true assertion at line {tautologies[0].lineno}'))
    real = [a for a in asserts if not _is_tautology(a.test)]
    if real and not (raises or unittest_asserts or helper_calls) and all(_is_trivial(a.test) for a in real):
        findings.append(('trivial-only', 'only checks existence, type, truthiness or non-emptiness'))
    mock_attr_asserts = [a for a in real if any(isinstance(n, ast.Attribute) and n.attr in MOCK_ATTRS
                                                for n in ast.walk(a.test))]
    if mock_asserts and not (set(real) - set(mock_attr_asserts)) and not (raises or unittest_asserts or helper_calls):
        findings.append(('mock-only', 'asserts only that mocks were called, not on any result'))
    private = [t for t in map(_private_target, calls) if t]
    if private:
        findings.append(('private-patch', f'forces internal state through {private[0]}; check a real caller can reach it'))
    for c in raises:
        if c.args and _name(c.args[0]) in MISUSE_ERRORS:
            findings.append(('type-misuse', f'expects {_name(c.args[0])} from misuse; check a realistic caller can pass that input'))
            break
    if any(_name(c.func) == 'sleep' for c in calls):
        findings.append(('sleep', 'waits on wall-clock time'))
    for dec in getattr(node, 'decorator_list', []):
        cases = _parametrize_cases(dec)
        if cases and cases > LARGE_PARAMETRIZE:
            findings.append(('large-parametrize', f'{cases} cases in one parametrize; keep the distinct ones'))
    return findings


def collected(node):
    """Collected-item estimate: product of literal parametrize sizes (unknown counts as 1)."""
    total, unknown = 1, False
    for dec in getattr(node, 'decorator_list', []):
        cases = _parametrize_cases(dec)
        if cases is None:
            unknown = True
        else:
            total *= cases
    return total, unknown


def _tests_in(tree):
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith('test'):
            yield node.name, node
        elif isinstance(node, ast.ClassDef):
            bases = {_name(b) for b in node.bases}
            if node.name.startswith('Test') or 'TestCase' in bases:
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name.startswith('test'):
                        yield f'{node.name}.{item.name}', item


def audit(root, paths=None, budget=None):
    root = Path(root)
    tests, errors = [], []
    for path in discover(root, paths):
        rel = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
        try:
            tree = ast.parse(path.read_text(encoding='utf-8', errors='replace'))
        except SyntaxError as exc:
            errors.append(f'{rel}: {exc}')
            continue
        helpers = {n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                   and not n.name.startswith('test') and any(isinstance(x, ast.Assert) for x in ast.walk(n))}
        for name, node in _tests_in(tree):
            items, unknown = collected(node)
            body = _strip_docstring(node.body)
            tests.append({
                'id': f'{rel}::{name}', 'line': node.lineno, 'items': items, 'unknown_parametrize': unknown,
                'findings': [{'smell': s, 'detail': d} for s, d in audit_test(node, helpers)],
                '_dump': ast.dump(ast.Module(body=body, type_ignores=[])), '_shape': _shape(body),
            })
    by_dump, by_shape = defaultdict(list), defaultdict(list)
    for t in tests:
        by_dump[t['_dump']].append(t)
        by_shape[t['_shape']].append(t)
    duplicates = [[t['id'] for t in group] for group in by_dump.values() if len(group) > 1]
    for group in by_dump.values():
        for t in group[1:]:
            t['findings'].append({'smell': 'duplicate', 'detail': f'same body as {group[0]["id"]}'})
    same_shape = [[t['id'] for t in group] for group in by_shape.values()
                  if len(group) > 1 and len({t['_dump'] for t in group}) > 1]
    total = sum(t['items'] for t in tests)
    for t in tests:
        del t['_dump'], t['_shape']
    return {
        'root': str(root), 'paths': paths or ['.'], 'test_functions': len(tests), 'collected_estimate': total,
        'unknown_parametrize': sum(t['unknown_parametrize'] for t in tests), 'budget': budget,
        'over_budget': budget is not None and total > budget,
        'findings': [{'test': t['id'], 'line': t['line'], **f} for t in tests for f in t['findings']],
        'duplicates': duplicates, 'same_shape': same_shape, 'parse_errors': errors,
    }


def budget_from_profile(root):
    """(max, paths) from the profile's test_budget, or (None, None)."""
    spec = importlib.util.spec_from_file_location('workbench_profile', Path(__file__).resolve().parent / 'profile.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        profile, _ = module.load(project_dir=root, cwd=root)
    except module.ProfileError:
        return None, None
    value = (profile or {}).get('test_budget')
    if isinstance(value, int):
        return value, None
    if isinstance(value, dict):
        return value.get('max'), value.get('paths')
    return None, None


def render(report):
    lines = [f"{report['test_functions']} test functions, ~{report['collected_estimate']} collected"
             + (f" ({report['unknown_parametrize']} with non-literal parametrize)" if report['unknown_parametrize'] else '')
             + (f"; budget {report['budget']}" + (' — OVER BUDGET' if report['over_budget'] else '') if report['budget'] else '')]
    for f in report['findings']:
        level = 'HIGH' if f['smell'] in HIGH else 'review'
        lines.append(f"{level:6} {f['smell']:17} {f['test']}:{f['line']}  {f['detail']}")
    for group in report['same_shape']:
        lines.append('merge? same shape, different constants: ' + ', '.join(group))
    lines += [f'parse error: {e}' for e in report['parse_errors']]
    return '\n'.join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--paths', nargs='+')
    ap.add_argument('--budget', type=int)
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    budget, paths = args.budget, args.paths
    if budget is None or paths is None:
        profile_budget, profile_paths = budget_from_profile(root)
        budget = budget if budget is not None else profile_budget
        paths = paths if paths is not None else profile_paths
    report = audit(root, paths, budget)
    print(json.dumps(report, indent=2) if args.json else render(report))
    failing = report['over_budget'] or any(f['smell'] in HIGH for f in report['findings']) or report['parse_errors']
    return 1 if args.check and failing else 0


if __name__ == '__main__':
    raise SystemExit(main())
