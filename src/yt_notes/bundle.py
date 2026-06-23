import json
import os
from pathlib import Path

from .models import Manifest

MANIFEST_NAME = "manifest.json"


def home_dir() -> Path:
    env = os.environ.get("YT_NOTES_HOME")
    return Path(env).expanduser() if env else (Path.home() / "yt-notes-library")


def bundle_dir(home, video_id: str) -> Path:
    return Path(home) / "bundles" / video_id


def notes_dir(home) -> Path:
    return Path(home) / "notes"


def write_manifest(bundle_path: Path, manifest: Manifest) -> None:
    bundle_path = Path(bundle_path)
    bundle_path.mkdir(parents=True, exist_ok=True)
    (bundle_path / MANIFEST_NAME).write_text(json.dumps(manifest.to_dict(), indent=2))


def read_manifest(bundle_path):
    p = Path(bundle_path) / MANIFEST_NAME
    if not p.exists():
        return None
    return Manifest.from_dict(json.loads(p.read_text()))


def is_cached(bundle_path) -> bool:
    m = read_manifest(bundle_path)
    if not m or not m.steps:
        return False
    return all(v == "ok" for v in m.steps.values())
