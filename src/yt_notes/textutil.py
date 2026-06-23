import re


def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def format_timestamp(seconds: float) -> str:
    total = int(seconds)
    h, rem = divmod(total, 3600)
    m, sec = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{sec:02d}"
    return f"{m}:{sec:02d}"


def youtube_deeplink(video_id: str, seconds: float) -> str:
    return f"https://youtu.be/{video_id}?t={int(seconds)}"


_ID_PATTERNS = [
    re.compile(r"youtu\.be/([A-Za-z0-9_-]{11})"),
    re.compile(r"[?&]v=([A-Za-z0-9_-]{11})"),
    re.compile(r"/embed/([A-Za-z0-9_-]{11})"),
    re.compile(r"/shorts/([A-Za-z0-9_-]{11})"),
]


def video_id_from_url(url: str) -> str | None:
    """Extract the 11-char YouTube video id from common URL forms, or None.

    Lets the cache be checked without any network call.
    """
    for pat in _ID_PATTERNS:
        m = pat.search(url)
        if m:
            return m.group(1)
    return None
