"""Test management (audit_tests.py and the guard's test-budget reminder), checked on a sample
suite and on this repository itself (profile test_budget: 20)."""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
SCRIPTS = ROOT / "plugins/workbench-core/scripts"
_spec = importlib.util.spec_from_file_location("workbench_audit_tests", SCRIPTS / "audit_tests.py")
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)

SAMPLE = '''import time
import pytest
from unittest import mock
from app import parse, Client

def check(x):
    assert x == 3

def test_nothing():
    parse("a")

def test_true():
    assert True

def test_exists():
    r = parse("a")
    assert r is not None
    assert len(r) > 0

def test_mock_only():
    c = mock.Mock()
    Client(c).send()
    c.post.assert_called_once()

def test_private(monkeypatch):
    monkeypatch.setattr("app._cache", None)
    assert parse("a") == {"a": 1}

def test_misuse():
    with pytest.raises(TypeError):
        parse(None)

def test_slow():
    time.sleep(1)
    assert parse("a") == {"a": 1}

def test_a():
    assert parse("x=1") == {"x": 1}

def test_b():
    assert parse("y=2") == {"y": 2}

def test_c():
    assert parse("x=1") == {"x": 1}

def test_helper():
    check(parse("n"))

@pytest.mark.parametrize("v", [1, 2, 3])
def test_table(v):
    assert parse(str(v)) == {}
'''


def test_detectors_flag_each_low_value_pattern_and_nothing_else(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests/test_sample.py").write_text(SAMPLE)
    report = A.audit(tmp_path, ["tests"], budget=10)
    found = {(f["test"].split("::")[1], f["smell"]) for f in report["findings"]}
    assert found == {("test_nothing", "no-assertion"), ("test_true", "tautology"), ("test_exists", "trivial-only"),
                     ("test_mock_only", "mock-only"), ("test_private", "private-patch"),
                     ("test_misuse", "type-misuse"), ("test_slow", "sleep"), ("test_c", "duplicate")}
    assert report["test_functions"] == 12 and report["collected_estimate"] == 14 and report["over_budget"]
    assert ["tests/test_sample.py::test_a", "tests/test_sample.py::test_b", "tests/test_sample.py::test_c"] in report["same_shape"]
    done = subprocess.run([sys.executable, str(SCRIPTS / "audit_tests.py"), str(tmp_path), "--paths", "tests",
                           "--budget", "20", "--check"], capture_output=True, text=True)
    assert done.returncode == 1 and "HIGH   no-assertion" in done.stdout


def test_this_repository_stays_within_budget_and_the_guard_reminds(tmp_path):
    done = subprocess.run([sys.executable, str(SCRIPTS / "audit_tests.py"), str(ROOT), "--check", "--json"],
                          capture_output=True, text=True)
    report = json.loads(done.stdout)
    assert done.returncode == 0, done.stdout
    assert report["budget"] == 20 and report["collected_estimate"] <= 20 and report["unknown_parametrize"] == 0
    assert not report["findings"] and not report["same_shape"]
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / "AGENTS.md").write_text("---\nworkbench:\n  schema: 1\n  archetypes: [code]\n"
                                    "  test_budget: {max: 2, paths: [tests]}\n---\n")
    (repo / "tests/test_a.py").write_text("def test_one():\n    assert 1 + 1 == 2\n\ndef test_two():\n    assert 2 * 2 == 4\n")

    def guard(tool, tool_input):
        payload = {"hook_event_name": "PreToolUse", "cwd": str(repo), "tool_name": tool, "tool_input": tool_input}
        out = subprocess.run([sys.executable, str(SCRIPTS / "guard.py"), "pre-tool-use"], input=json.dumps(payload),
                             capture_output=True, text=True, env={**os.environ, "CLAUDE_PROJECT_DIR": str(repo)}).stdout
        return json.loads(out)["hookSpecificOutput"].get("additionalContext", "") if out.strip() else ""

    new_test = "\n\ndef test_three():\n    assert 3 - 1 == 2\n"
    assert "Test budget: this edit adds 1 test(s)" in guard("Edit", {"file_path": str(repo / "tests/test_a.py"),
                                                                    "old_string": "", "new_string": new_test})
    assert "Test budget" in guard("apply_patch", {"command": "*** Begin Patch\n*** Update File: tests/test_a.py\n"
                                                             "+def test_three():\n+    assert 3 - 1 == 2\n*** End Patch\n"})
    assert guard("Edit", {"file_path": str(repo / "tests/test_a.py"), "old_string": "def test_two",
                          "new_string": "def test_two"}) == ""
    assert guard("Write", {"file_path": str(repo / "src/app.py"), "content": "def test_like():\n    pass\n"}) == ""
