import importlib
import shutil

_BINARIES = {
    "ffmpeg": "Install with: brew install ffmpeg",
    "yt-dlp": "Install with: uv tool install yt-dlp  (or: brew install yt-dlp)",
}
_MODULES = {
    "faster_whisper": "Provided by project deps: uv sync",
    "PIL": "Provided by project deps (Pillow): uv sync",
    "imagehash": "Provided by project deps (ImageHash): uv sync",
}


def check_dependencies() -> list[dict]:
    out = []
    for name, hint in _BINARIES.items():
        out.append({"name": name, "present": shutil.which(name) is not None, "hint": hint})
    for mod, hint in _MODULES.items():
        try:
            importlib.import_module(mod)
            present = True
        except Exception:
            present = False
        out.append({"name": mod, "present": present, "hint": hint})
    return out
