#!/usr/bin/env bash
set -euo pipefail
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
case "${1:-}" in
  corpus) exec python3 "$here/build_context.py" "$@" ;;
  repo-search) exec python3 "$here/search_repo_docs.py" "$@" ;;
  *) echo 'usage: documentation-context.sh {corpus|repo-search} ...' >&2; exit 2 ;;
esac
