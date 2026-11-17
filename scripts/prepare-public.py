#!/usr/bin/env python3
"""Copy selected current files to a new directory, without git metadata or private docs.

This is a local preparation step. Review the output before publishing; no git or network
operation is performed. Existing destinations, symlinks and unknown file types are refused.
"""
import argparse
import hashlib
import os
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent
FILES = (
    '.claude-plugin/marketplace.json', '.gitignore', 'AGENTS.md', 'LICENSE', 'README.md', 'VERSION',
    'manifest/policy.yaml', 'manifest/external-plugin-admission.yaml', 'hooks/pre-push',
    'scripts/check.sh', 'scripts/verify.sh', 'scripts/validate-manifest.py', 'scripts/print-install.sh',
    'scripts/prepare-public.py',
    'docs/getting-started.md', 'docs/skills.md', 'docs/optional-tools.md', 'docs/workflow.md',
    'docs/maintaining.md', 'docs/principles.md',
)
TREES = ('plugins', 'tests')
SKIP = {'__pycache__', '.pytest_cache', '.git', '.hg', '.svn'}


def public_files():
    paths = [ROOT / name for name in FILES]
    for name in TREES:
        base = ROOT / name
        if not base.is_dir() or base.is_symlink():
            raise ValueError(f'missing or linked source tree: {base}')
        for directory, dirs, files in os.walk(base, followlinks=False):
            for child in dirs:
                if (Path(directory) / child).is_symlink():
                    raise ValueError(f'symlink in export source: {Path(directory) / child}')
            dirs[:] = sorted(d for d in dirs if d not in SKIP)
            paths.extend(Path(directory) / f for f in sorted(files) if f not in SKIP and not f.endswith('.pyc'))
    for path in paths:
        if path.is_symlink() or any(p.is_symlink() for p in path.parents if p != ROOT.parent):
            raise ValueError(f'symlink in export source: {path}')
        if not path.is_file():
            raise ValueError(f'missing or unsupported source: {path}')
    return sorted(paths)


def prepare(destination):
    # Resolve parent links before writing and refuse any existing destination.
    destination = Path(destination).absolute()
    if destination.exists() or destination.is_symlink():
        raise ValueError(f'destination already exists: {destination}')
    parent = destination.parent.resolve(strict=True)
    destination = parent / destination.name
    if destination == ROOT or ROOT in destination.parents:
        raise ValueError('destination must be outside the private working tree')
    paths = public_files()  # Validate all sources before creating output.
    changelog = (ROOT / 'CHANGELOG.md').read_text()
    current = changelog[changelog.index('## '):].split('\n## ', 1)[0]
    destination.mkdir()
    for source in paths:
        target = destination / source.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    (destination / 'CHANGELOG.md').write_text('# Changelog\n\n'+current.rstrip()+'\n')
    entries = []
    for path in sorted(p for p in destination.rglob('*') if p.is_file()):
        entries.append(f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(destination).as_posix()}')
    (destination / 'PUBLIC_FILES.sha256').write_text('\n'.join(entries)+'\n')
    print(f'Prepared {len(entries)} current files at {destination}')
    print('Review PUBLIC_FILES.sha256 and the exported files before publishing.')
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    try:
        prepare(args.destination)
    except (ValueError, OSError) as exc:
        parser.exit(1, f'{exc}\n')


if __name__ == '__main__':
    main()
