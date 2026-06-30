# B2B SaaS LinkedIn Organic Research

## Overview

This repository started as a Cursor IDE setup exercise and has progressed into a research workspace for building a playbook on **LinkedIn organic content strategy for B2B SaaS**.

The current corpus focuses on practitioner-led sources: LinkedIn post queues, YouTube transcripts, expert metadata, methodology notes, and early synthesis themes.

## Current Progress

- Cursor IDE, Claude Code, Codex, and GitHub setup is complete.
- Research topic selected: LinkedIn organic content strategy for B2B SaaS.
- Expert roster created with 10 practitioners and source links.
- Source index captured in `research/sources.md`.
- 11 YouTube transcript files collected via the Supadata YouTube Transcript API.
- 10 LinkedIn author files created with post URLs and fields for compliant manual capture.
- Methodology, platform context, and synthesis seed notes added under `research/other/`.
- Python requirements and collection scripts added.

## Repository Structure

```text
.
|-- data/
|   |-- experts.json
|   `-- source_schema.json
|-- research/
|   |-- linkedin-posts/
|   |-- other/
|   |-- sources.md
|   `-- youtube-transcripts/
|-- scripts/
|   |-- collect_linkedin_manual.md
|   |-- collect_youtube_supadata.py
|   `-- collect_youtube_ytdlp.sh
|-- requirements.txt
`-- README.md
```

## Key Files

- `data/experts.json` stores the expert roster and primary links.
- `data/source_schema.json` defines the intended metadata shape for experts and sources.
- `research/sources.md` is the human-readable source index.
- `research/linkedin-posts/*.md` contains LinkedIn post URLs and capture templates.
- `research/youtube-transcripts/*.md` contains collected transcript markdown.
- `research/other/methodology.md` explains inclusion criteria and collection rules.
- `research/other/platform-context.md` tracks LinkedIn platform-level context.
- `research/other/synthesis-seeds.md` stores early themes to validate.

## Setup

Create and activate a Python environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a local `.env` file for transcript collection:

```text
SUPADATA_API_KEY=your_api_key_here
```

`.env`, `.venv/`, Python cache files, raw VTT subtitle output, and archived research exports are ignored by git.

## YouTube Transcript Collection

Primary collection uses Supadata:

```powershell
python scripts/collect_youtube_supadata.py
```

The script reads a static list of 11 YouTube videos, skips already populated transcript files by default, and writes markdown files to `research/youtube-transcripts/`.

Useful optional environment variables:

- `SUPADATA_OVERWRITE=true` to refresh existing transcript files.
- `SUPADATA_REQUEST_ATTEMPTS` to control retry attempts.
- `SUPADATA_TIMEOUT_SECONDS` to control read timeout.
- `SUPADATA_MIN_TRANSCRIPT_CHARS` to decide whether an existing transcript is populated.

Fallback subtitle collection is available for environments with `yt-dlp` and `ffmpeg`:

```bash
bash scripts/collect_youtube_ytdlp.sh
```

That fallback writes raw subtitle files to `research/youtube-transcripts/raw-vtt/`.

## LinkedIn Collection

LinkedIn collection is intentionally manual/compliant because full post access can depend on login state, visibility, and platform restrictions.

Use `scripts/collect_linkedin_manual.md` as the capture protocol. For each queued LinkedIn post, add:

- posted date/time
- capture date/time
- full post body
- media type
- engagement snapshot
- notable comments, if visible
- core claim/framework
- playbook implication

Do not bypass access controls or mass scrape LinkedIn.

## Current Research Themes

The initial synthesis notes identify six working themes:

- Founder-led content beats company-page-only content early.
- Zero-click value increases trust and native reach.
- Distribution is a system, not a last step.
- LinkedIn should influence pipeline, not just create last-click conversions.
- Creator-led and relationship-led GTM is replacing faceless distribution.
- Strategy starts with what you want to be known for.

These are hypotheses to validate against the full source corpus before turning them into final recommendations.

## Next Steps

1. Manually capture full LinkedIn post text and metadata for the queued post URLs.
2. Normalize source records into the schema in `data/source_schema.json`.
3. Summarize each transcript into claims, frameworks, examples, and quotable evidence.
4. Cross-check early synthesis themes against the captured sources.
5. Draft the final B2B SaaS LinkedIn organic playbook.
