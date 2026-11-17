"""Shipped plugin content stays general (D32) and self-contained.

No owner repository names or paths: repository specifics belong in each repository's own
AGENTS.md profile or docs; the known-repository drafts live in tests/fixtures/profiles/.
No internal rule or decision codes (R5, D32, C§4): an installed plugin carries no copy of
docs/, so a skill states the rule itself.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
REPO_TOKENS = re.compile(
    r"SU2_MDO|su2-mdo|su2mdo|\bAMAC\b|[Bb]asilisk|HypOpt|airfoil-surrogate|anomaly-detection-ssvp|"
    r"\bssvp\b|masters-application|/home/vivek|Shape_Optimisation|Masters_Res"
)
INTERNAL_CODES = re.compile(r"\((?:[^()]*[,; ])?[DR]\d{1,2}\b[^()]*\)|C§\d")
# Checker fixtures are recorded sample inputs, not instructions; stop-slop is bundled unmodified.
EXEMPT_PARTS = {"fixtures", "stop-slop"}


def shipped_text_files():
    for path in (ROOT / "plugins").rglob("*"):
        if path.is_file() and not EXEMPT_PARTS & set(path.parts) and path.suffix != ".pyc":
            yield path


def test_shipped_content_is_general_and_self_contained():
    hits = []
    for path in shipped_text_files():
        for n, line in enumerate(path.read_text(errors="ignore").splitlines(), 1):
            if REPO_TOKENS.search(line) or INTERNAL_CODES.search(line):
                hits.append(f"{path.relative_to(ROOT)}:{n}: {line.strip()[:80]}")
    assert not hits, "\n".join(hits)

