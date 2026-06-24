---
name: yt-notes
description: Turn a YouTube URL into a complete structured note (summary, sectioned notes, embedded real frames, mermaid diagrams, timestamp deep-links) you read instead of watching. Accepts optional free-form instructions after the URL (e.g. "capture every key point", "this is a DSA topic — also list LeetCode practice problems") and tailors the note to them. Use when given a YouTube link and asked to take notes, summarize, "read instead of watch", or shape a video into notes a particular way.
---

# yt-notes authoring

You are given a YouTube URL, optionally followed by free-form **instructions**. Produce a
complete note the user reads **instead of** watching the video, tailored to those instructions.

Project root (where the CLI lives): `/Users/diwakarmatsaa/Desktop/dev/yt-notes`

## Step 0 — Parse the request

The user's message has a **YouTube URL** plus optional **instructions** (everything that isn't
the URL). Extract the `youtube.com` / `youtu.be` link. Treat the rest as **authoring
guidelines** — what to emphasize, what to include, format, external resources, etc.

- **No instructions** → write the standard note (skip Step 3's clarifying questions).
- **Instructions present** → follow every step below, including the clarifying round.

## Step 1 — Ingest (deterministic, free, local)

- Run: `cd /Users/diwakarmatsaa/Desktop/dev/yt-notes && uv run yt-notes ingest "<URL>"`
- It prints the bundle path `<home>/bundles/<video-id>` (default home `~/yt-notes-library`).
- If it errors about missing dependencies, run `uv run yt-notes doctor`, surface the install
  hints to the user, then stop.

(Ingestion uses the URL only — instructions never change this step.)

## Step 2 — Read the bundle

- `meta.json` — title, channel, duration, **chapters** (use as section anchors).
- `transcript.md` — timestamped, deep-linked transcript.
- `frames.json` — timestamped list of frames.
- **READ the frame PNGs in `frames/` as images.** Actually look at each slide / diagram / code
  frame so you can transcribe code, read diagram labels, and decide which frames are worth
  embedding versus noise.

## Step 3 — Clarify (ALWAYS, when instructions are present)

Before writing, **always ask the user 1–3 targeted clarifying questions** to fully capture
intent. Make them count — cover the highest-value unknowns, and **never re-ask anything the
instruction already states**. Good things to clarify:

- **Depth / length** — exhaustive vs. concise; every point vs. highlights.
- **Audience / level** — beginner, interview prep, expert refresher.
- **Must-include scope** — specific subtopics, definitions, proofs, examples, gotchas.
- **External resources** — if they want outside material, *which* sources and *how much*
  (e.g. LeetCode only vs. also NeetCode / GeeksforGeeks / Codeforces; difficulty range).
- **Format / grouping** — flat list vs. grouped by pattern/subtopic; tables; checklists.

Wait for the answers. If instructions were given but are already fully specific, still ask at
least one confirming question (e.g. scope or format) before proceeding. Skip this step only when
no instructions were provided.

## Step 4 — Web research (only when the agreed guidance needs outside material)

When the user wants external resources (practice problems, reference docs, related reading):

- Use web search to find relevant, real resources for the **video's specific topic**.
- **Verify every link resolves** (fetch it) — never emit a guessed or hallucinated URL. Drop
  links you cannot verify.
- Keep web-sourced content in **clearly-labeled, separate sections** (e.g. `## Practice
  Problems`, `## Further Resources`), attributed and linked, so it is never confused with what
  the video actually said.

If no external material is needed, skip this step.

## Step 5 — Author the note

Write to `<home>/notes/<video-id>-<slug>.md`. Start from the base structure and **adapt it to
the guidance** (general adaptive — no fixed domain templates):

Base structure:
- `# <Title>` and a one-line source link.
- If instructions were applied, add one line: `_Tailored to your request: <one-line paraphrase>._`
- `## TL;DR` — 3-6 sentences + estimated read-vs-watch time saved.
- `## Contents` — a table of contents.
- One `## <Section>` per chapter (or per logical segment when there are no chapters). In each:
  prose notes in your own words; embed the most relevant frame(s)
  `![caption](../bundles/<video-id>/frames/<file>.png)` (path relative to the note in
  `<home>/notes/`); a ` ```mermaid ` diagram when a concept/flow benefits; end with
  `[watch from M:SS](https://youtu.be/<id>?t=<sec>)`.
- `## Key Takeaways` — bullet list.
- `## Glossary` — terms → short definitions (omit if none).

Apply the guidance on top: **add or reshape sections to fit** — e.g. a `## Practice Problems`
section (grouped per the user's answer, each `- [name](verified-link) — difficulty — why it
fits`) plus a short complexity recap for DSA; a `## Commands` cheatsheet for a CLI tutorial;
exhaustive point-by-point capture when completeness was requested.

Preserve the core sections (TL;DR, Key Takeaways) and add to them. Only if the user *explicitly*
asks to drop a core section, comply — and tell them the `validate` "missing section" warning is
expected, rather than re-adding it.

## Step 6 — Validate & report

- Run: `cd /Users/diwakarmatsaa/Desktop/dev/yt-notes && uv run yt-notes validate "<note-path>"`
- It prints `OK`, or problems (missing sections, unbalanced mermaid fences, missing images —
  image paths checked relative to the note's directory). Fix every problem, then re-run until
  `OK` (or until only an explicitly-requested missing core section remains).
- Tell the user the final note path when done.

## Rules

- Only embed frames that actually exist in the bundle. Prefer slides / diagrams / code frames
  over talking-head frames.
- For long videos, draft section-by-section, then assemble.
- Notes must follow the video's actual flow. Do not invent content unsupported by the
  transcript or frames; web-sourced material is separate and link-verified.
- Tell the user the final note path when done.
