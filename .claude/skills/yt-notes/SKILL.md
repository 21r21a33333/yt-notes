---
name: yt-notes
description: Turn a YouTube URL into a complete structured note (summary, sectioned notes, embedded real frames, mermaid diagrams, timestamp deep-links) you read instead of watching. Use when given a YouTube link and asked to take notes, summarize, or "read instead of watch" a video.
---

# yt-notes authoring

You are given a YouTube URL. Produce a complete note the user reads **instead of** watching the video.

Project root (where the CLI lives): `/Users/diwakarmatsaa/Desktop/dev/yt-notes`

## Steps

1. **Ingest** (deterministic, free, local):
   - Run: `cd /Users/diwakarmatsaa/Desktop/dev/yt-notes && uv run yt-notes ingest "<URL>"`
   - It prints the bundle path `<home>/bundles/<video-id>` (default home `~/yt-notes-library`).
   - If it errors about missing dependencies, run `uv run yt-notes doctor` and surface the
     install hints to the user, then stop.

2. **Read the bundle:**
   - `meta.json` — title, channel, duration, **chapters** (use as section anchors).
   - `transcript.md` — timestamped, deep-linked transcript.
   - `frames.json` — timestamped list of frames.
   - **READ the frame PNGs in `frames/` as images.** Actually look at each slide / diagram /
     code frame so you can transcribe code, read diagram labels, and decide which frames are
     worth embedding versus noise.

3. **Author the note** → write to `<home>/notes/<video-id>-<slug>.md` with this structure:
   - `# <Title>` and a one-line source link.
   - `## TL;DR` — 3-6 sentences + estimated read-vs-watch time saved.
   - `## Contents` — a table of contents.
   - One `## <Section>` per chapter (or per logical segment when there are no chapters). In each:
     - prose notes in your own words;
     - embed the most relevant frame(s): `![caption](../bundles/<video-id>/frames/<file>.png)`
       (path is relative to the note in `<home>/notes/`);
     - add a ` ```mermaid ` diagram when a concept / flow / architecture benefits from one;
     - end with `[watch from M:SS](https://youtu.be/<id>?t=<sec>)`.
   - `## Key Takeaways` — bullet list.
   - `## Glossary` — terms → short definitions (omit the section if there are none).

4. **Validate** before finishing:
   - Run: `cd /Users/diwakarmatsaa/Desktop/dev/yt-notes && uv run yt-notes validate "<note-path>" "<bundle-path>"`
   - It prints `OK`, or a list of problems (missing sections, unbalanced mermaid fences, missing
     images). Fix every reported problem, then re-run until it prints `OK`.

## Rules

- Only embed frames that actually exist in the bundle. Prefer slides / diagrams / code frames
  over talking-head frames.
- For long videos, draft section-by-section, then assemble the final note.
- Notes must follow the video's actual flow. Do not invent content unsupported by the
  transcript or frames.
- Tell the user the final note path when done.
