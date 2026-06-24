# yt-notes

Turn a YouTube video into a complete, structured note you read **instead of watching** —
summary, sectioned notes that follow the video's flow, embedded real frames (slides /
diagrams / code), Claude-generated mermaid diagrams, key takeaways, and timestamp deep-links
back to the source.

Everything mechanical runs **locally and free** (yt-dlp + ffmpeg + Whisper). The note is
authored by **Claude Code**, which reads the transcript and *looks at* the extracted frames.

## How it works

```
/yt-notes <url>          ← one Claude Code command (a skill)
   │
   ▼
yt-notes ingest <url>    ← deterministic Python, no LLM, cacheable
   │   metadata (yt-dlp) · transcript (captions → Whisper fallback) · frames (ffmpeg scene-detect + dedup)
   ▼
bundles/<video-id>/      ← meta.json · transcript.md · frames/*.png · manifest.json
   │
   ▼
Claude reads the bundle (and sees the frames) → authors the note
   ▼
notes/<video-id>-<slug>.md   ← read this instead of watching
```

## One-time setup

```bash
# 1. system tool (free, OSS)
brew install ffmpeg

# 2. python env (uv provisions Python 3.12 and all deps; faster-whisper, yt-dlp, Pillow, imagehash)
cd /Users/diwakarmatsaa/Desktop/dev/yt-notes
uv sync

# 3. verify everything is present
uv run yt-notes doctor
```

`doctor` prints a ✓/✗ checklist and the exact install command for anything missing.

## Usage

**Via Claude Code (recommended):** in a Claude Code session, run

```
/yt-notes https://youtu.be/<id>
```

The `yt-notes` skill ingests the video, reads the bundle, and writes the note. To make the
command available from any directory, symlink the skill into your global skills dir:

```bash
ln -s /Users/diwakarmatsaa/Desktop/dev/yt-notes/.claude/skills/yt-notes ~/.claude/skills/yt-notes
```

**Standalone (ingest only, no note authoring):**

```bash
uv run yt-notes ingest "https://youtu.be/<id>"   # prints the bundle path
uv run yt-notes ingest "<url>" --force            # re-ingest, ignore cache
uv run yt-notes ingest "<url>" --model small       # larger Whisper model for the fallback
```

## Where things land

- Library home: `$YT_NOTES_HOME` (default `~/yt-notes-library`)
- Bundles: `~/yt-notes-library/bundles/<video-id>/`
- Notes: `~/yt-notes-library/notes/<video-id>-<slug>.md`

Notes use relative image links, so they render in Obsidian, GitHub, or any markdown viewer as
long as the `bundles/` and `notes/` folders stay side-by-side.

## Validating a note

```bash
uv run yt-notes validate "<note-path>"
```

Checks required sections, balanced mermaid fences, and that every referenced image exists
(image paths are resolved relative to the note's own directory).

## Development

```bash
uv run pytest          # full unit suite (no network)
YT_NOTES_E2E=1 YT_NOTES_E2E_URL="<short CC clip>" uv run pytest tests/test_smoke_e2e.py
```

## Status / roadmap

- **v1 (now):** single video → readable note.
- **Future add-ons (designed for, not built):** playlists/batch + cross-note index, Q&A chat
  over the content (local RAG), audio overview (local TTS), study aids (flashcards/quiz).
