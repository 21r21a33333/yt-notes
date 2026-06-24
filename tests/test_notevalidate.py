from yt_notes.notevalidate import validate_note


def _bundle(tmp_path):
    (tmp_path / "frames").mkdir()
    (tmp_path / "frames" / "frame-1.png").write_bytes(b"x")
    return tmp_path


def test_valid_note(tmp_path):
    b = _bundle(tmp_path)
    md = (
        "## TL;DR\nx\n![f](frames/frame-1.png)\n"
        "```mermaid\ngraph TD; A-->B\n```\n## Key Takeaways\n- a"
    )
    assert validate_note(md, b) == []


def test_missing_section_flagged(tmp_path):
    b = _bundle(tmp_path)
    md = "## TL;DR\nonly"
    problems = validate_note(md, b)
    assert any("Key Takeaways" in p for p in problems)


def test_unbalanced_mermaid_flagged(tmp_path):
    b = _bundle(tmp_path)
    md = "## TL;DR\n```mermaid\ngraph TD; A-->B\n## Key Takeaways\n- a"
    problems = validate_note(md, b)
    assert any("mermaid" in p.lower() or "fence" in p.lower() for p in problems)


def test_missing_image_flagged(tmp_path):
    b = _bundle(tmp_path)
    md = "## TL;DR\n![f](frames/missing.png)\n## Key Takeaways\n- a"
    problems = validate_note(md, b)
    assert any("missing.png" in p for p in problems)


def test_resolves_images_relative_to_note_dir(tmp_path):
    # Real layout: note in <home>/notes/, frames in <home>/bundles/<id>/frames/.
    # Image refs are relative to the NOTE's directory, so the base dir must be notes/.
    notes = tmp_path / "notes"
    notes.mkdir()
    frames = tmp_path / "bundles" / "vid" / "frames"
    frames.mkdir(parents=True)
    (frames / "f.png").write_bytes(b"x")
    md = "## TL;DR\n![f](../bundles/vid/frames/f.png)\n## Key Takeaways\n- a"
    assert validate_note(md, notes) == []
