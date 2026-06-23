import json
import subprocess

from .models import Chapter, VideoMeta


def build_metadata_cmd(url: str) -> list[str]:
    return ["yt-dlp", "-J", "--no-warnings", url]


def parse_ytdlp_info(info: dict) -> VideoMeta:
    chapters = [
        Chapter(title=c.get("title", ""), start=float(c.get("start_time", 0)))
        for c in (info.get("chapters") or [])
    ]
    return VideoMeta(
        video_id=info["id"],
        title=info.get("title", ""),
        channel=info.get("uploader", "") or info.get("channel", ""),
        duration=float(info.get("duration") or 0),
        description=info.get("description", "") or "",
        url=info.get("webpage_url", "") or f"https://www.youtube.com/watch?v={info['id']}",
        chapters=chapters,
    )


def fetch_metadata(url: str) -> VideoMeta:
    proc = subprocess.run(build_metadata_cmd(url), capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"yt-dlp metadata failed: {proc.stderr.strip()}")
    return parse_ytdlp_info(json.loads(proc.stdout))
