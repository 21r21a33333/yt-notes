# yt-notes

**Read YouTube videos instead of watching them.**

`yt-notes` turns a YouTube URL into a complete, structured markdown note: a summary, sectioned
notes that follow the video's flow, **real frames** pulled from the video (slides / diagrams /
code), **mermaid diagrams** for the concepts, key takeaways, a glossary, and **timestamp
deep-links** back to the exact moment in the source.

Everything mechanical runs **locally and free** — [`yt-dlp`](https://github.com/yt-dlp/yt-dlp)
for transcript + video, [`ffmpeg`](https://ffmpeg.org/) for frames,
[`faster-whisper`](https://github.com/SYSTRAN/faster-whisper) as a transcription fallback. The
note itself is authored by **[Claude Code](https://claude.com/claude-code)**, which reads the
transcript and *looks at* the extracted frames (so it can transcribe code, read diagram labels,
and pick which frames are worth embedding). No paid API, no cloud pipeline.

> Think of it as a local, do-it-yourself NotebookLM focused on one job: a great read-instead-of-watch note.

## Example

Run it on a 5:50 IBM lightboard talk and you get a note with a TL;DR, chapter-aligned
sections, embedded whiteboard frames, two mermaid diagrams, key takeaways, a glossary, and
`?t=` deep-links — readable in ~3 minutes:

```
## 2. What a transformer is: encoder + decoder
... A transformer is something that transforms one sequence into another ...

  [embedded lightboard frame: I → Encoder → Decoder → O]

  ```mermaid
  flowchart LR
      I["Input sequence"] --> E["Encoder"]
      E -- "encodings" --> D["Decoder"]
      D --> O["Output sequence"]
  ```

[watch from 1:40](https://youtu.be/ZXiruGOCn9s?t=100)
```

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

The clean split is the whole idea: **Python does the mechanical, reproducible work** (and
caches it); **Claude does the reasoning and writing**. Every frame and transcript line carries
a timestamp, so the right screenshot lands next to the right section.

## Requirements

- [`uv`](https://github.com/astral-sh/uv) (manages Python 3.12 + all Python deps for you)
- `ffmpeg` — `brew install ffmpeg` (macOS) · `sudo apt install ffmpeg` (Debian/Ubuntu)
- [Claude Code](https://claude.com/claude-code) — for the note-authoring step

## Install

```bash
git clone <your-repo-url> yt-notes
cd yt-notes
uv sync                 # provisions Python 3.12 + yt-dlp, faster-whisper, Pillow, imagehash
uv run yt-notes doctor  # ✓/✗ checklist; prints install commands for anything missing
```

## Use it

### Via Claude Code (the drop-in "read instead of watch" path)

Install the skill once by symlinking it into your personal skills directory, then **restart
Claude Code** so it's discovered:

```bash
ln -s "$(pwd)/.claude/skills/yt-notes" ~/.claude/skills/yt-notes
```

> The skill's `SKILL.md` runs the CLI from this project directory — if you cloned somewhere
> other than the path shown in `.claude/skills/yt-notes/SKILL.md`, update that path.

Then, from any directory:

```
/yt-notes https://youtu.be/<id>
```

Claude ingests the video, reads the bundle, and writes the note.

#### Steering the note with instructions

Append free-form instructions after the URL and the note is tailored to them:

```
/yt-notes https://youtu.be/<id> capture every key point — be exhaustive
/yt-notes https://youtu.be/<id> this is a DSA lecture — also list LeetCode practice problems for the topic
```

When you include instructions, the skill **asks 1–3 quick clarifying questions first** (depth,
audience, which external sources, format) so it nails what you want, then writes. If the
guidance calls for outside material (e.g. practice problems, reference links), it does a **web
search and verifies the links** before adding them in a clearly-labeled section. Plain
`/yt-notes <url>` with no instructions skips the questions and writes the standard note.

### Standalone (mechanical part only — produces the bundle, not the note)

```bash
uv run yt-notes ingest "https://youtu.be/<id>"   # prints the bundle path
uv run yt-notes ingest "<url>" --force            # re-ingest, ignore the cache
uv run yt-notes ingest "<url>" --model small      # larger Whisper model (only used when a video has no captions)
uv run yt-notes validate "<note-path>"            # check a note's structure
```

## Where things land

```
~/yt-notes-library/          # override with $YT_NOTES_HOME
  notes/                     # the finished markdown you read
  bundles/<video-id>/        # transcript + frames + metadata per video
```

Notes use **relative image links**, so they render in Obsidian, GitHub, or any markdown viewer
as long as `notes/` and `bundles/` stay side-by-side.

## Development

```bash
uv run pytest          # full unit suite (no network)
# optional end-to-end smoke (hits the network, needs ffmpeg + yt-dlp):
YT_NOTES_E2E=1 YT_NOTES_E2E_URL="<short Creative-Commons clip>" uv run pytest tests/test_smoke_e2e.py
```

The deterministic core is fully unit-tested: caption parsing, segment merging, perceptual-hash
frame dedup, manifest/caching, note validation, and ingest orchestration.

## Roadmap

- **v1 (now):** single video → readable note.
- **Designed-for, not built:** playlists / batch + a cross-note index, Q&A chat over the
  content (local RAG), audio overview (local TTS), study aids (flashcards / quiz).

## License

MIT — see [LICENSE](LICENSE).
