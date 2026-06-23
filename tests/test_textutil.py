from yt_notes.textutil import slugify, format_timestamp, youtube_deeplink


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
