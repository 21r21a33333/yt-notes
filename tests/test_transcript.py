from yt_notes.models import Segment
from yt_notes.transcript import build_caption_cmd, render_transcript_md


def test_render_has_heading_and_deeplinks():
    md = render_transcript_md([Segment(0, 2, "Hello"), Segment(75, 80, "World")], "vid123", "My Title")
    assert md.startswith("# Transcript")
    assert "My Title" in md
    assert "[0:00](https://youtu.be/vid123?t=0) Hello" in md
    assert "[1:15](https://youtu.be/vid123?t=75) World" in md


def test_build_caption_cmd_requests_vtt_and_subs():
    cmd = build_caption_cmd("URL", "/tmp/out")
    j = " ".join(cmd)
    assert "yt-dlp" in cmd
    assert "--write-subs" in cmd and "--write-auto-subs" in cmd
    assert "--sub-format" in cmd and "vtt" in j
    assert "--skip-download" in cmd
