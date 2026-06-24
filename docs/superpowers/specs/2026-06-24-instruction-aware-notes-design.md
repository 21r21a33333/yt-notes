# Instruction-aware `/yt-notes` — Design Spec

**Date:** 2026-06-24
**Status:** Approved (design); pending implementation
**Scope:** Enhancement to the `yt-notes` Claude Code skill. **Prompt-only — no CLI/Python changes.**

## Goal

Let the user append free-form instructions after the URL (`/yt-notes <url> <instructions>`) and
have the skill treat them as authoring guidelines. Before writing, the skill **always asks 1–3
targeted clarifying questions** (when instructions are present) to fully capture intent, and may
**do web research** when the instructions call for outside material (e.g. LeetCode practice
problems). The note is then tailored — general adaptive, no hardcoded domains.

## Key Decisions (from brainstorming)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| When to ask counter-questions | **Always ask 1–3** when instructions are present | User wants full intent captured before writing. Plain `/yt-notes <url>` (no instructions) skips clarifying and writes the standard note. |
| Web research | **Yes, when instructions ask** | Needed for the DSA practice-problem case; uses Claude Code web search, links verified. |
| Tailoring | **General adaptive** | No hardcoded domains/presets. Infer intent from instruction + video; add/reshape sections to fit. Zero maintenance, works for any subject. |
| Implementation surface | **`SKILL.md` only** | The skill already receives the full user message; ingestion is URL-only. No code change. |

## Flow

```
ingest <url>  (unchanged, URL only)  →  read bundle  (unchanged)
   → [NEW] if instructions present: ALWAYS ask 1–3 targeted counter-questions; wait for answers
   → [NEW] if instructions/answers call for external material: web-search + VERIFY links resolve
   → author note (base structure + guidelines applied)  →  validate  →  report path
```

## Behavior details

### Instruction parsing
The user's message contains a YouTube URL plus optional free-form text. Extract the URL
(`youtube.com` / `youtu.be` link); treat the remainder as **authoring guidelines**. The `ingest`
CLI is still called with the URL only.

### Clarifying step (always, when instructions present)
Ask 1–3 focused questions covering the highest-value unknowns — depth/length, audience level,
must-include scope, which external sources (if any), grouping/format. **Do not re-ask anything
the instruction already states.** Wait for answers before authoring. If no instructions were
given, skip this step entirely.

### Web research (conditional)
When the agreed guidance needs outside material (practice problems, references, related links):
- use Claude Code web search to find relevant, real resources;
- **verify each link resolves** (fetch) — never emit hallucinated URLs;
- keep web-sourced content in clearly-labeled sections, attributed and linked, **separate from
  video-grounded content**.

### Authoring (general adaptive)
On top of the base note (TL;DR · Contents · per-chapter sections with frames + mermaid · Key
Takeaways · Glossary), **add or reshape sections to fit** the guidance — e.g. a `## Practice
Problems` section for a DSA topic, a `## Commands` cheatsheet for a CLI tutorial, exhaustive
point-by-point capture when completeness is requested. Add one transparency line near the top:
`_Tailored to your request: <one-line paraphrase>._`

Core sections (TL;DR, Key Takeaways) are preserved and added-to. If the user *explicitly* asks
to drop one, comply and note the expected `validate` warning rather than fighting the request.

### Guardrails
- Never invent video content unsupported by transcript/frames.
- Web material is clearly separated from video content and link-verified.
- Existing `validate` still runs; for default-shaped notes it passes unchanged.

## Worked example (DSA)

`/yt-notes <url> this is a DSA lecture — capture all key points and list practice problems`

1. Ingest the lecture → bundle.
2. Clarify (always): e.g. *"Which platforms (LeetCode only or also NeetCode/GfG)?"*,
   *"Difficulty range / interview-focused?"*, *"Group problems by pattern or one flat list?"*
3. Research: search the lecture's specific topic, verify links.
4. Author: full structured lecture notes (complete, as requested) **plus** a `## Practice
   Problems` section grouped per the answer — `- [name](verified-link) — difficulty — why it fits`
   — and a short complexity recap.
5. Validate → report note path.

## Testing / verification

Prompt behavior, so verified by dry-run rather than unit tests:
- Run both example invocations; confirm the clarify-then-author flow triggers when instructions
  are present and is skipped when absent.
- Confirm web-sourced sections contain verified links and are clearly separated from video
  content.
- Confirm the existing `uv run yt-notes validate <note>` still passes on the produced note.

## Out of scope

- Named domain presets / mode keywords (rejected in favor of general adaptive).
- Any change to ingestion, the bundle format, or the validator.
- Persisting per-user instruction preferences across runs.
