from pathlib import Path

import yt_notes.ingest as ing
from yt_notes.models import Frame, Segment, VideoMeta


def test_ingest_writes_bundle(tmp_path, monkeypatch):
    meta = VideoMeta("vid", "T", "Chan", 10, "d", "http://x", [])
    monkeypatch.setattr(ing, "fetch_metadata", lambda url: meta)
    monkeypatch.setattr(
        ing, "fetch_transcript", lambda url, wd, model_size="base": ([Segment(0, 2, "hi")], "captions")
    )

    def fake_extract(video, out, threshold=0.3):
        Path(out).mkdir(parents=True, exist_ok=True)
        (Path(out) / "frame-1.png").write_bytes(b"x")
        return [Frame(1.0, "frame-1.png", "abcd")]

    monkeypatch.setattr(ing, "extract_frames", fake_extract)
    monkeypatch.setattr(ing, "download_video", lambda url, wd: str(Path(wd) / "v.mp4"))

    bp = ing.ingest("http://x", home=tmp_path)
    assert (bp / "manifest.json").exists()
    assert (bp / "transcript.md").exists()
    assert (bp / "frames.json").exists()
    from yt_notes.bundle import read_manifest

    assert read_manifest(bp).transcript_source == "captions"


def test_ingest_uses_cache(tmp_path, monkeypatch):
    # Real youtu.be URL whose id matches the (mocked) metadata id, mirroring reality
    # where the URL id IS the video id.
    url = "https://youtu.be/dQw4w9WgXcQ"
    meta = VideoMeta("dQw4w9WgXcQ", "T", "Chan", 10, "d", url, [])
    calls = {"n": 0}

    def counting_meta(u):
        calls["n"] += 1
        return meta

    monkeypatch.setattr(ing, "fetch_metadata", counting_meta)
    monkeypatch.setattr(
        ing, "fetch_transcript", lambda url, wd, model_size="base": ([Segment(0, 2, "hi")], "captions")
    )
    monkeypatch.setattr(ing, "extract_frames", lambda v, o, threshold=0.3: [])
    monkeypatch.setattr(ing, "download_video", lambda url, wd: "v.mp4")
    ing.ingest(url, home=tmp_path)
    ing.ingest(url, home=tmp_path)  # second call hits cache with zero network calls
    assert calls["n"] == 1
