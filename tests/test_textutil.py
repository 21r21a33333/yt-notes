from yt_notes.textutil import (
    format_timestamp,
    slugify,
    video_id_from_url,
    youtube_deeplink,
)


def test_slugify_basic():
    assert slugify("Intro to RAG: Part 1!") == "intro-to-rag-part-1"


def test_slugify_collapses_and_trims():
    assert slugify("  Hello   World  ") == "hello-world"


def test_format_timestamp_under_hour():
    assert format_timestamp(75) == "1:15"


def test_format_timestamp_over_hour():
    assert format_timestamp(3661) == "1:01:01"


def test_youtube_deeplink_floors_seconds():
    assert youtube_deeplink("abc123", 75.9) == "https://youtu.be/abc123?t=75"


def test_video_id_from_url_forms():
    assert video_id_from_url("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert video_id_from_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10") == "dQw4w9WgXcQ"
    assert video_id_from_url("https://www.youtube.com/shorts/dQw4w9WgXcQ") == "dQw4w9WgXcQ"


def test_video_id_from_url_none_when_absent():
    assert video_id_from_url("http://x") is None
