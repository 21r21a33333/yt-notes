import re

from .models import Segment

_VTT_TS = re.compile(r"(\d{2}):(\d{2}):(\d{2})[.,](\d{3})")


def _ts_to_seconds(h, m, s, ms) -> float:
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def _parse_blocks(text: str) -> list[Segment]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    segs: list[Segment] = []
    for block in re.split(r"\n\s*\n", text):
        lines = [ln for ln in block.split("\n") if ln.strip()]
        ts_idx = next((i for i, ln in enumerate(lines) if "-->" in ln), None)
        if ts_idx is None:
            continue
        m = list(_VTT_TS.finditer(lines[ts_idx]))
        if len(m) < 2:
            continue
        start = _ts_to_seconds(*m[0].groups())
        end = _ts_to_seconds(*m[1].groups())
        body = " ".join(lines[ts_idx + 1:]).strip()
        body = re.sub(r"<[^>]+>", "", body)  # strip inline VTT tags
        if body:
            segs.append(Segment(start=start, end=end, text=body))
    return segs


def parse_vtt(text: str) -> list[Segment]:
    return _parse_blocks(text)


def parse_srt(text: str) -> list[Segment]:
    return _parse_blocks(text)


def merge_segments(segs, max_gap: float = 1.5, max_chars: int = 240):
    if not segs:
        return []
    out = [Segment(segs[0].start, segs[0].end, segs[0].text)]
    for s in segs[1:]:
        cur = out[-1]
        gap = s.start - cur.end
        joined_len = len(cur.text) + 1 + len(s.text)
        if gap <= max_gap and joined_len <= max_chars:
            cur.text = f"{cur.text} {s.text}".strip()
            cur.end = s.end
        else:
            out.append(Segment(s.start, s.end, s.text))
    return out
