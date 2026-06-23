import re
from pathlib import Path

REQUIRED_SECTIONS = ["## TL;DR", "## Key Takeaways"]
_IMG = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def validate_note(note_md: str, bundle_path) -> list[str]:
    problems: list[str] = []
    for sec in REQUIRED_SECTIONS:
        if sec not in note_md:
            problems.append(f"Missing required section: {sec}")
    if note_md.count("```") % 2 != 0:
        problems.append("Unbalanced code fences (``` count is odd) — check mermaid blocks")
    bp = Path(bundle_path)
    for ref in _IMG.findall(note_md):
        if ref.startswith(("http://", "https://")):
            continue
        candidate = Path(ref) if Path(ref).is_absolute() else (bp / ref)
        if not candidate.exists():
            problems.append(f"Referenced image does not exist: {ref}")
    return problems
