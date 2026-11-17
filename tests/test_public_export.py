"""A public export contains reviewed current sources and never copies private history."""
import hashlib
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
_spec = importlib.util.spec_from_file_location('prepare_public', ROOT / 'scripts/prepare-public.py')
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)


def test_export_excludes_private_material_and_refuses_existing_paths_and_links(tmp_path, monkeypatch):
    exported = E.prepare(tmp_path / 'public')
    assert not any((exported / p).exists() for p in ('.git', 'docs/decisions.md', 'logs', 'docs/history'))
    assert (exported / 'plugins/workbench-core/scripts/guard.py').read_bytes() == (
        ROOT / 'plugins/workbench-core/scripts/guard.py').read_bytes()
    assert (exported / 'tests/test_guard.py').read_bytes() == (ROOT / 'tests/test_guard.py').read_bytes()
    assert (exported / 'CHANGELOG.md').read_text().count('\n## ') == 1
    for entry in (exported / 'PUBLIC_FILES.sha256').read_text().splitlines():
        digest, name = entry.split('  ', 1)
        assert hashlib.sha256((exported / name).read_bytes()).hexdigest() == digest, name
    with pytest.raises(ValueError, match='already exists'):
        E.prepare(exported)
    monkeypatch.setattr(E, 'ROOT', exported)
    nested_git = exported / 'tests/fixtures/repos/web-app/.git'
    nested_git.mkdir()
    (nested_git / 'private-history').write_text('private history sentinel')
    nested_worktree = exported / 'tests/fixtures/repos/vision-ml/.git'
    nested_worktree.write_text('gitdir: /private/archive')
    clean = E.prepare(tmp_path / 'clean')
    assert not (clean / nested_git.relative_to(exported)).exists()
    assert not (clean / nested_worktree.relative_to(exported)).exists()
    (exported / 'tests/private-link').symlink_to(ROOT / 'docs/decisions.md')
    with pytest.raises(ValueError, match='symlink'):
        E.prepare(tmp_path / 'refused')
    assert not (tmp_path / 'refused').exists()
