import random

from PIL import Image

from yt_notes.frames import build_scene_detect_cmd, dedup_frames, phash_image
from yt_notes.models import Frame


def _make_noise(p, seed: int):
    # Seeded random-noise image: rich frequency content so pHash is meaningful and
    # deterministic. Same seed -> identical hash; different seed -> large hamming distance.
    # (Solid/low-detail images are pathological for pHash.)
    rng = random.Random(seed)
    im = Image.new("RGB", (64, 64))
    im.putdata([(rng.randint(0, 255),) * 3 for _ in range(64 * 64)])
    im.save(p)


def test_build_scene_detect_cmd_combines_triggers():
    # The select filter must capture frames on THREE conditions so it works for both
    # slide decks (hard scene cuts) and continuous-camera video (no cuts):
    #   1. the very first frame            -> eq(n,0)
    #   2. a hard scene change             -> gt(scene,<threshold>)
    #   3. a periodic floor every N seconds -> gte(t-prev_selected_t,<interval>)
    cmd = build_scene_detect_cmd("/v.mp4", "/out", threshold=0.4, interval=12)
    assert cmd[0] == "ffmpeg"
    joined = " ".join(cmd)
    assert "eq(n,0)" in joined
    assert "gt(scene,0.4)" in joined
    assert "gte(t-prev_selected_t,12)" in joined
    assert "/out" in joined


def test_phash_stable(tmp_path):
    p = tmp_path / "a.png"
    _make_noise(p, seed=1)
    assert phash_image(p) == phash_image(p)


def test_dedup_drops_near_duplicates(tmp_path):
    a = tmp_path / "a.png"
    _make_noise(a, seed=1)
    a2 = tmp_path / "a2.png"
    _make_noise(a2, seed=1)  # same seed -> identical -> dup
    b = tmp_path / "b.png"
    _make_noise(b, seed=2)  # different seed -> clearly distinct
    frames = [
        Frame(0.0, str(a), phash_image(a)),
        Frame(1.0, str(a2), phash_image(a2)),
        Frame(2.0, str(b), phash_image(b)),
    ]
    kept = dedup_frames(frames, max_hamming=5)
    kept_ts = sorted(f.timestamp for f in kept)
    assert kept_ts == [0.0, 2.0]
