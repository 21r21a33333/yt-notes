import glob
import subprocess
from pathlib import Path

from .captions import merge_segments, parse_vtt
from .models import Segment
from .textutil import format_timestamp, youtube_deeplink


def render_transcript_md(segs: list[Segment], video_id: str, title: str) -> str:
    lines = ["# Transcript", "", f"_{title}_", ""]
    for s in segs:
        link = youtube_deeplink(video_id, s.start)
        lines.append(f"- [{format_timestamp(s.start)}]({link}) {s.text}")
    return "\n".join(lines) + "\n"


def build_caption_cmd(url: str, out_template: str) -> list[str]:
    return [
        "yt-dlp",
        "--skip-download",
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs",
        "en.*,en",
        "--sub-format",
        "vtt",
        "-o",
        out_template,
        url,
    ]


def build_audio_cmd(url: str, out_template: str) -> list[str]:
    return ["yt-dlp", "-x", "--audio-format", "mp3", "-o", out_template, url]


def _load_caption_file(work_dir: str):
    """Return (segments, source) from downloaded VTTs, or (None, None) if none found.

    Prefers a manual track over an auto-generated one. yt-dlp names auto subs with an
    ".auto." marker in the filename (e.g. ``caps.en.auto.vtt``).
    """
    vtts = sorted(glob.glob(f"{work_dir}/*.vtt"))
    if not vtts:
        return None, None
    manual = [v for v in vtts if ".auto." not in Path(v).name]
    if manual:
        chosen, source = manual[0], "captions"
    else:
        chosen, source = vtts[0], "captions-auto"
    segs = merge_segments(parse_vtt(Path(chosen).read_text()))
    return segs, source


def run_whisper(audio_path: str, model_size: str = "base") -> list[Segment]:
    from faster_whisper import WhisperModel

    model = WhisperModel(model_size, device="auto", compute_type="int8")
    segments, _ = model.transcribe(audio_path)
    return merge_segments(
        [Segment(start=s.start, end=s.end, text=s.text.strip()) for s in segments]
    )


def fetch_transcript(url: str, work_dir: str, model_size: str = "base"):
    Path(work_dir).mkdir(parents=True, exist_ok=True)
    subprocess.run(build_caption_cmd(url, f"{work_dir}/caps"), capture_output=True, text=True)
    segs, source = _load_caption_file(work_dir)
    if segs:
        return segs, source
    # Fallback: download audio + local Whisper transcription.
    subprocess.run(build_audio_cmd(url, f"{work_dir}/audio.%(ext)s"), capture_output=True, text=True)
    audio = next(iter(sorted(glob.glob(f"{work_dir}/audio.*"))), None)
    if not audio:
        raise RuntimeError("No captions and audio download failed; cannot transcribe.")
    return run_whisper(audio, model_size), "whisper"
