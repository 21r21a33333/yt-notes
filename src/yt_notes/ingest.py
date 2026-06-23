import glob
import json
import subprocess
import tempfile
from pathlib import Path

from . import bundle
from .frames import extract_frames
from .metadata import fetch_metadata
from .models import Manifest
from .textutil import video_id_from_url
from .transcript import fetch_transcript, render_transcript_md


def download_video(url: str, work_dir: str) -> str:
    # Lowest-res mp4 that is still legible for slides (<=480p).
    out = f"{work_dir}/video.%(ext)s"
    cmd = [
        "yt-dlp",
        "-f",
        "bv*[height<=480]+ba/b[height<=480]/b",
        "--merge-output-format",
        "mp4",
        "-o",
        out,
        url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"yt-dlp video download failed: {proc.stderr[-500:]}")
    vids = sorted(glob.glob(f"{work_dir}/video.*"))
    if not vids:
        raise RuntimeError("Video download produced no file.")
    return vids[0]


def ingest(url: str, home=None, force: bool = False, model: str = "base") -> Path:
    home = Path(home) if home else bundle.home_dir()
    # Cheap cache check first: derive the id from the URL so a cache hit needs no network.
    if not force:
        vid = video_id_from_url(url)
        if vid and bundle.is_cached(bundle.bundle_dir(home, vid)):
            return bundle.bundle_dir(home, vid)
    meta = fetch_metadata(url)
    bp = bundle.bundle_dir(home, meta.video_id)
    if not force and bundle.is_cached(bp):
        return bp
    bp.mkdir(parents=True, exist_ok=True)
    (bp / "meta.json").write_text(json.dumps(meta.to_dict(), indent=2))

    with tempfile.TemporaryDirectory() as work:
        segs, source = fetch_transcript(url, work, model_size=model)
        (bp / "transcript.json").write_text(json.dumps([s.to_dict() for s in segs], indent=2))
        (bp / "transcript.md").write_text(render_transcript_md(segs, meta.video_id, meta.title))

        frames_dir = bp / "frames"
        video_path = download_video(url, work)
        frames = extract_frames(video_path, str(frames_dir))
        (bp / "frames.json").write_text(json.dumps([f.to_dict() for f in frames], indent=2))

    manifest = Manifest(
        version=1,
        video_id=meta.video_id,
        url=meta.url,
        transcript_source=source,
        steps={"metadata": "ok", "transcript": "ok", "frames": "ok"},
        paths={
            "meta": "meta.json",
            "transcript_md": "transcript.md",
            "transcript_json": "transcript.json",
            "frames_json": "frames.json",
            "frames_dir": "frames",
        },
    )
    bundle.write_manifest(bp, manifest)
    return bp
