#!/usr/bin/env bash
# Prints installation commands only; does not install or change settings.
set -euo pipefail
client=all
plugin=workbench-core
papers=false
usage() { echo "usage: $0 [--client claude|codex|all] [--plugin workbench-core|sim-validity|ml-validity|research-writing|workbench] [--papers]"; }
while (($#)); do
  case "$1" in
    --client) client=${2:?missing client}; shift 2;;
    --plugin) plugin=${2:?missing plugin}; shift 2;;
    --papers) papers=true; shift;;
    -h|--help) usage; exit 0;;
    *) usage >&2; exit 2;;
  esac
done
case "$client" in claude|codex|all) ;; *) usage >&2; exit 2;; esac
case "$plugin" in workbench-core|sim-validity|ml-validity|research-writing|workbench) ;; *) usage >&2; exit 2;; esac
if [[ $client == claude || $client == all ]]; then
  echo 'claude plugin marketplace add Vivk06/evidence-workbench'
  echo "claude plugin install $plugin@evidence-workbench --scope user"
  case "$plugin" in
    sim-validity|ml-validity|research-writing) echo "claude plugin enable $plugin@evidence-workbench --scope project";;
    workbench) echo '# Keep the install-only bundle disabled. Enable domain plugins per project.';;
  esac
  if $papers; then
    echo 'claude plugin marketplace add ctoth/research-papers-plugin#v4.8.1'
    echo 'claude plugin install research-papers@research-papers-marketplace --scope user'
  fi
fi
if [[ $client == codex || $client == all ]]; then
  echo 'codex plugin marketplace add Vivk06/evidence-workbench'
  echo 'codex plugin add workbench-core@evidence-workbench'
  case "$plugin" in
    workbench) for domain in sim-validity ml-validity research-writing; do echo "codex plugin add $domain@evidence-workbench"; done;;
    workbench-core) ;;
    *) echo "codex plugin add $plugin@evidence-workbench";;
  esac
  if $papers; then
    echo 'codex plugin marketplace add ctoth/research-papers-plugin --ref v4.8.1'
    echo 'codex plugin add research-papers@research-papers-marketplace'
  fi
fi
