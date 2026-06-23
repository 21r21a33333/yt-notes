import os
import shutil

import pytest

from yt_notes.ingest import ingest

NEEDS = shutil.which("ffmpeg") and shutil.which("yt-dlp")


@pytest.mark.skipif(
    not os.environ.get("YT_NOTES_E2E") or not NEEDS,
    reason="set YT_NOTES_E2E=1 and install ffmpeg+yt-dlp to run",
)
def test_short_cc_video(tmp_path):
    url = os.environ["YT_NOTES_E2E_URL"]  # a short Creative-Commons clip
    bp = ingest(url, home=tmp_path)
    assert (bp / "manifest.json").exists()
    assert (bp / "transcript.md").read_text().startswith("# Transcript")
