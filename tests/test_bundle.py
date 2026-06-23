from yt_notes import bundle
from yt_notes.models import Manifest


def _mk(steps):
    return Manifest(1, "vid", "http://x", "captions", steps, {})


def test_home_dir_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv("YT_NOTES_HOME", str(tmp_path))
    assert bundle.home_dir() == tmp_path


def test_write_read_roundtrip(tmp_path):
    bp = bundle.bundle_dir(tmp_path, "vid")
    bp.mkdir(parents=True)
    bundle.write_manifest(bp, _mk({"metadata": "ok"}))
    m = bundle.read_manifest(bp)
    assert m.video_id == "vid" and m.steps["metadata"] == "ok"


def test_is_cached_true_when_all_ok(tmp_path):
    bp = bundle.bundle_dir(tmp_path, "vid")
    bp.mkdir(parents=True)
    bundle.write_manifest(bp, _mk({"metadata": "ok", "transcript": "ok", "frames": "ok"}))
    assert bundle.is_cached(bp) is True


def test_is_cached_false_when_incomplete(tmp_path):
    bp = bundle.bundle_dir(tmp_path, "vid")
    bp.mkdir(parents=True)
    bundle.write_manifest(bp, _mk({"metadata": "ok", "transcript": "failed"}))
    assert bundle.is_cached(bp) is False


def test_is_cached_false_when_missing(tmp_path):
    assert bundle.is_cached(bundle.bundle_dir(tmp_path, "nope")) is False
