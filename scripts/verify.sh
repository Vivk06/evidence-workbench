#!/usr/bin/env bash
# Static checks of the marketplace: required files, manifests, Codex compatibility,
# plugin metadata, licenses, skill frontmatter, a secret scan, and claude plugin validate.
# Reads files only; never touches user configuration (AGENTS.md, Boundaries).
set -euo pipefail
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
(($# == 0)) || { echo "usage: $0 (no options)" >&2; exit 2; }
fail=0
pass() { echo "PASS $1"; }
bad() { echo "FAIL $1"; fail=1; }
plugins=(workbench-core sim-validity ml-validity research-writing workbench)
for f in VERSION LICENSE manifest/policy.yaml .claude-plugin/marketplace.json CHANGELOG.md hooks/pre-push; do
  if [[ -f "$root/$f" ]]; then pass "file $f"; else bad "missing file $f"; fi
done
python3 "$root/scripts/validate-manifest.py" --root "$root" --admission >/dev/null && pass "policy manifest, Codex compatibility, external-tool admission" || bad "policy manifest, Codex compatibility, or external-tool admission"
if python3 - "$root" "${plugins[@]}" <<'PY'
import json, pathlib, re, subprocess, sys
root=pathlib.Path(sys.argv[1]); names=sys.argv[2:]
version=(root/'VERSION').read_text().strip()
market=json.loads((root/'.claude-plugin/marketplace.json').read_text())
assert market['name']=='evidence-workbench' and [p['name'] for p in market['plugins']]==names
for name in names:
    plugin_root=root/'plugins'/name
    plugin=json.loads((plugin_root/'.claude-plugin/plugin.json').read_text())
    assert plugin['name']==name and plugin['version']==version and plugin['license']=='MIT', name
    assert (plugin_root/'LICENSE').read_bytes()==(root/'LICENSE').read_bytes(), name
for p in root.glob('plugins/*/skills/*/SKILL.md'):
    text=p.read_text(); assert text.startswith('---\n'), p
    if not (p.parent/'LICENSE').is_file():  # bundled third-party skills keep their upstream frontmatter
        assert 'metadata:' in text and 'tags: [lean]' in text, p
for p in root.glob('plugins/*/agents/*.md'): assert p.read_text().startswith('---\n'), p
# The shipped tool pins must match the optional-tools guide.
pins=set(re.findall(r'[\w-]+==[\w.]+|@[\w-]+/[\w-]+@[\d.]+', (root/'plugins/workbench-core/skills/repo-setup/references/tools.md').read_text()))
readme=(root/'docs/optional-tools.md').read_text()
assert pins and not [p for p in pins if p not in readme], sorted(p for p in pins if p not in readme)
deny=re.compile(r'(BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|password\s*[:=]\s*\S+|api[_-]?key\s*[:=]\s*[A-Za-z0-9_\-]{12,})', re.I)
try:
    files=[root/f for f in subprocess.run(['git','-C',str(root),'ls-files'],capture_output=True,text=True,check=True).stdout.splitlines()]
except Exception:
    files=[p for p in root.rglob('*') if '.git' not in p.parts]
for p in files:
    if p.is_file() and p.name != 'SHA256SUMS' and p.suffix not in {'.gz'} and p.stat().st_size < 2_000_000:
        assert not deny.search(p.read_text(errors='ignore')), p
PY
then pass "plugin metadata, licenses, frontmatter, pinned tool versions, and secret scan"; else bad "plugin metadata, licenses, frontmatter, pinned tool versions, or secret scan"; fi
if command -v claude >/dev/null 2>&1; then
  for target in . "${plugins[@]/#/plugins/}"; do
    claude plugin validate --strict "$root/$target" >/dev/null 2>&1 && pass "claude plugin validate --strict $target" || bad "claude plugin validate --strict $target (run it for details)"
  done
else
  echo "SKIPPED claude plugin validate --strict (claude not on PATH); run it on $root and on each $root/plugins/<name>"
fi
exit "$fail"
