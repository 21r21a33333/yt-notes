import json
from pathlib import Path

from yt_notes.metadata import build_metadata_cmd, parse_ytdlp_info

FIX = Path(__file__).parent / "fixtures"


def test_parse_basic_fields():
    info = json.loads((FIX / "ytdlp_info.json").read_text())
    m = parse_ytdlp_info(info)
    assert m.video_id == "dQw4w9WgXcQ"
    assert m.title == "Sample Talk: Intro to X"
    assert m.channel == "Example Channel"
    assert m.duration == 600.0
    assert m.url.endswith("dQw4w9WgXcQ")


def test_parse_chapters():
    info = json.loads((FIX / "ytdlp_info.json").read_text())
    m = parse_ytdlp_info(info)
    assert len(m.chapters) == 2
    assert m.chapters[1].title == "Main" and m.chapters[1].start == 120.0


def test_parse_handles_missing_chapters():
    m = parse_ytdlp_info(
        {"id": "x", "title": "t", "uploader": "u", "duration": 1, "webpage_url": "http://x"}
    )
    assert m.chapters == []


def test_build_metadata_cmd():
    assert build_metadata_cmd("URL") == ["yt-dlp", "-J", "--no-warnings", "URL"]
