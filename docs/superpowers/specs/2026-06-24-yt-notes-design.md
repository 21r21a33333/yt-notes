# yt-notes — Design Spec

**Date:** 2026-06-24
**Status:** Approved (design); pending implementation plan
**Location:** `/Users/diwakarmatsaa/Desktop/dev/yt-notes` (own git repo, unrelated to `bit-ponder`)

## Goal

A local, free pipeline that turns a YouTube video into a complete, structured note you
read **instead of watching the video**. The note contains a summary, sectioned notes that
follow the video's flow, real embedded frames (slides / diagrams / code), Claude-generated
mermaid diagrams for concepts, key takeaways, a glossary, and timestamp deep-links back to
the source moments.

**v1 is one video at a time**, designed with clean seams so a playlist/batch loop can wrap
it later.

## Constraints

- **No paid service.** Every mechanical step uses free, open-source tooling and runs
  locally/offline. The only cloud dependency is Claude Code itself, which the user already
  has; it is the note-authoring "brain."
- **Works out of the box** after a one-time dependency install (with a `doctor` check that
  prints exact install commands for anything missing).

## Key Decisions (from brainstorming)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Note "brain" | **Claude Code (agentic)** | Highest-quality reasoning, cross-referencing, and diagram authoring; reads frames as images. Uses the user's existing Claude Code — no extra paid service. |
| Scope | **One video now; extensible to playlists later** | Build the single-video unit cleanly; a loop wraps it later. |
| Transcript | **Captions-first, Whisper fallback** | YouTube captions are free/instant; local Whisper covers videos without captions. Handles every video. |
| Frames | **Scene-change detection + perceptual-hash dedup** | Captures distinct visuals (slides/diagrams/code), drops redundant talking-head frames. Best signal-to-noise. |
| Capabilities (v1) | **Structured readable note only** | YAGNI. Q&A chat, audio overview, study aids are explicitly future add-ons. |
| Invocation | **One Claude Code command** (`/yt-notes <url>`) | Feels like a single drop-in tool replacing "watch a video." |

## Architecture

Clean split between **mechanical work (Python, deterministic, free, offline)** and
**judgment (Claude Code, agentic)**.

```
/yt-notes <url>   ← one Claude Code command (a skill)
        │
        ▼
┌─────────────────────────────┐
│ ingest.py  (no LLM)         │   deterministic, cacheable
│  1. metadata   (yt-dlp)     │
│  2. transcript (captions →  │
│       Whisper fallback)     │
│  3. frames     (ffmpeg      │
│       scene-detect + dedup) │
└─────────────┬───────────────┘
              ▼
   bundles/<video-id>/         ← the "evidence bundle"
     meta.json, transcript.md,
     frames/*.png, manifest.json
              │
              ▼
┌─────────────────────────────┐
│ Claude (the skill body)     │   reads transcript + SEES the frames,
│  → authors the note         │   aligns visuals to sections,
└─────────────┬───────────────┘   writes mermaid diagrams
              ▼
   notes/<video-id>-<slug>.md  ← the drop-in "read instead of watch" doc
```

**The crux:** every frame and every transcript line carries a timestamp, so Claude can place
the right screenshot next to the right section. Because Claude Code can *read images*, it
looks at each slide/diagram/code frame — transcribing code, reading diagram labels, deciding
which frames are worth embedding vs. noise.

## Components

### 1. Ingestion core — `ingest.py` (deterministic, no LLM)

| Step | Tool (free/OSS) | Output |
|------|-----------------|--------|
| Metadata | `yt-dlp` | id, title, channel, duration, description, **chapters** (section anchors) → `meta.json` |
| Transcript | `yt-dlp` → `faster-whisper` | Prefer manual captions, then auto-captions; parse VTT/SRT into timestamped segments. No captions → download audio (`yt-dlp -x`), transcribe locally with `faster-whisper` (fast on Apple Silicon, model auto-downloads free) → `transcript.json` + `transcript.md` |
| Frames | `ffmpeg` + `imagehash`/`Pillow` | Download a **low-res stream (≤480p — plenty for slides)**, run scene-change detection, then perceptual-hash **dedup** to keep distinct visuals → `frames/<timestamp>.png` + `frames.json` |
| Bundle | — | `manifest.json` ties everything together. **Idempotent**: re-running a known video reuses existing artifacts (cache by video id). |

**Bundle layout:**
```
bundles/<video-id>/
  meta.json          # video metadata + chapters
  transcript.json    # [{start, end, text}], + source: captions|whisper
  transcript.md      # human-readable timestamped transcript
  frames/            # <seconds>.png, one per distinct visual
  frames.json        # [{timestamp, path, phash}]
  manifest.json      # version, source url, status of each step, paths
```

### 2. The skill + authoring — `/yt-notes`

A Claude Code skill. On `/yt-notes <url>`:
1. Run `ingest.py <url>` (via `uv`), producing the bundle.
2. Read `manifest.json`, `transcript.md`, and the frames (Claude reads images visually).
3. Author the note (see output format).
4. Save to `notes/<video-id>-<slug>.md`.

**Long videos:** process section-by-section (chunked by chapters, or N-minute windows when
no chapters), then assemble — keeps within context and improves quality.

### 3. Output doc — `notes/<id>-<slug>.md`

A single markdown file, readable top-to-bottom, renders anywhere (Obsidian / GitHub / VS Code):

- **TL;DR** + estimated read-vs-watch time saved
- **Table of contents**
- **Sections** following the video's chapters/flow — each with:
  - prose notes
  - the relevant embedded **real frame(s)** (relative image links)
  - a **mermaid diagram** where a concept/flow benefits
  - a **timestamp deep-link** (`https://youtu.be/<id>?t=<sec>`) to the source moment
- **Key takeaways**
- **Glossary** of terms

Images stored alongside the note (relative links) so it renders in any markdown viewer.

## Dependencies (all free / OSS)

- `yt-dlp` — captions, metadata, audio/video (via `uv`)
- `ffmpeg` — scene detection, frame extraction, audio extraction (brew)
- `faster-whisper` — local transcription fallback (via `uv`); model auto-downloads free
- `imagehash` + `Pillow` — perceptual dedup (via `uv`)
- Python managed by `uv` (`pyproject.toml` + lockfile)

A `doctor` subcommand verifies each dependency and prints exact install commands for anything
missing.

## Error Handling

- Missing `ffmpeg` / Whisper detected up front with install hints (via `doctor`).
- Private / age-restricted / region-blocked videos: surface yt-dlp's error clearly.
- Very long videos: warn before proceeding.
- Idempotent / resumable: bundle steps write incrementally; re-runs reuse existing artifacts.

## Testing

- **Unit tests (deterministic core):** VTT/SRT parsing, transcript segment merging, frame
  dedup logic, manifest schema — with small fixtures (a sample VTT, a few sample frames).
- **Smoke test (optional, network-gated):** one short Creative-Commons clip end-to-end.
- **Authoring validation:** given a fixed small bundle, the produced note contains the
  required sections, valid mermaid, and only references frames that exist on disk.

## Out of Scope (v1) — future add-ons

- Q&A chat over the content (local RAG / embeddings)
- Audio overview (local TTS "podcast")
- Study aids (flashcards / quiz)
- Playlist / batch / managed library + cross-note index

## Future Extensibility Notes

- Single-video path is the reusable unit; a playlist loop iterates URLs and reuses the bundle
  cache.
- Bundle format (`manifest.json`) is the stable interface between ingestion and authoring;
  add-ons (RAG, TTS, study aids) consume the same bundle + note.
