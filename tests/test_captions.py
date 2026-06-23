from pathlib import Path

from yt_notes.captions import merge_segments, parse_srt, parse_vtt
from yt_notes.models import Segment

FIX = Path(__file__).parent / "fixtures"


def test_parse_vtt_counts_and_times():
    segs = parse_vtt((FIX / "sample.vtt").read_text())
    assert len(segs) == 3
    assert segs[0].start == 0.0 and segs[0].end == 2.0
    assert segs[0].text == "Hello and welcome"
    assert segs[2].start == 10.0


def test_parse_srt_comma_millis():
    segs = parse_srt((FIX / "sample.srt").read_text())
    assert len(segs) == 2
    assert segs[1].start == 2.2 and segs[1].text == "to this short video."


def test_merge_joins_close_cues():
    segs = [
        Segment(0, 2, "Hello and welcome"),
        Segment(2.2, 4, "to this short video."),
        Segment(10, 12, "Now a new topic."),
    ]
    merged = merge_segments(segs, max_gap=1.5, max_chars=240)
    assert len(merged) == 2
    assert merged[0].text == "Hello and welcome to this short video."
    assert merged[0].start == 0.0 and merged[0].end == 4.0
    assert merged[1].text == "Now a new topic."


def test_merge_splits_on_max_chars():
    segs = [Segment(0, 1, "a" * 200), Segment(1.1, 2, "b" * 200)]
    merged = merge_segments(segs, max_gap=1.5, max_chars=240)
    assert len(merged) == 2
