import re
import subprocess
from pathlib import Path

import imagehash
from PIL import Image

from .models import Frame


def build_scene_detect_cmd(video_path: str, out_dir: str, threshold: float = 0.3) -> list[str]:
    # Emit a frame whenever the scene-change score exceeds threshold; showinfo logs timestamps.
    return [
        "ffmpeg",
        "-i",
        video_path,
        "-vf",
        f"select='gt(scene,{threshold})',showinfo",
        "-vsync",
        "vfr",
        f"{out_dir}/frame-%05d.png",
    ]


def phash_image(path) -> str:
    with Image.open(path) as im:
        return str(imagehash.phash(im))


def dedup_frames(frames: list[Frame], max_hamming: int = 5) -> list[Frame]:
    kept: list[Frame] = []
    kept_hashes: list[imagehash.ImageHash] = []
    for f in frames:
        h = imagehash.hex_to_hash(f.phash)
        if all((h - kh) > max_hamming for kh in kept_hashes):
            kept.append(f)
            kept_hashes.append(h)
    return kept


_SHOWINFO_TS = re.compile(r"pts_time:([0-9.]+)")


def extract_frames(video_path: str, out_dir: str, threshold: float = 0.3) -> list[Frame]:
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        build_scene_detect_cmd(video_path, out_dir, threshold),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg frame extraction failed: {proc.stderr[-500:]}")
    timestamps = [float(t) for t in _SHOWINFO_TS.findall(proc.stderr)]
    files = sorted(Path(out_dir).glob("frame-*.png"))
    frames: list[Frame] = []
    for i, fp in enumerate(files):
        ts = timestamps[i] if i < len(timestamps) else float(i)
        frames.append(Frame(timestamp=ts, path=fp.name, phash=phash_image(fp)))
    deduped = dedup_frames(frames)
    kept_names = {f.path for f in deduped}
    for fp in files:  # remove discarded frame files
        if fp.name not in kept_names:
            fp.unlink(missing_ok=True)
    return deduped
