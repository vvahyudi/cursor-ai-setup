#!/usr/bin/env python3
"""Collect YouTube transcripts via Supadata.

Requirements:
  echo "SUPADATA_API_KEY=YOUR_API_KEY" > .env
  pip install requests python-dotenv

This script reads the static video list below and writes transcripts into
/research/youtube-transcripts/*.md, preserving source metadata.
"""
from __future__ import annotations

import os
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Any
import requests
from dotenv import load_dotenv
from requests import HTTPError, RequestException

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "research" / "youtube-transcripts"
load_dotenv(BASE / ".env")

API_KEY = os.getenv("SUPADATA_API_KEY")
SUPADATA_MODE = os.getenv("SUPADATA_MODE", "auto")
CONNECT_TIMEOUT_SECONDS = int(os.getenv("SUPADATA_CONNECT_TIMEOUT_SECONDS", "10"))
READ_TIMEOUT_SECONDS = int(os.getenv("SUPADATA_READ_TIMEOUT_SECONDS", "0") or "0")
if not READ_TIMEOUT_SECONDS:
    READ_TIMEOUT_SECONDS = max(int(os.getenv("SUPADATA_TIMEOUT_SECONDS", "180")), 180)
REQUEST_ATTEMPTS = int(os.getenv("SUPADATA_REQUEST_ATTEMPTS", "3"))
RETRY_BACKOFF_SECONDS = int(os.getenv("SUPADATA_RETRY_BACKOFF_SECONDS", "5"))
POLL_SECONDS = int(os.getenv("SUPADATA_POLL_SECONDS", "1"))
MAX_POLL_ATTEMPTS = int(os.getenv("SUPADATA_MAX_POLL_ATTEMPTS", "120"))
MIN_TRANSCRIPT_CHARS = int(os.getenv("SUPADATA_MIN_TRANSCRIPT_CHARS", "1000"))
OVERWRITE = os.getenv("SUPADATA_OVERWRITE", "").lower() in {"1", "true", "yes"}
RETRY_STATUS_CODES = {408, 425, 429, 500, 502, 503, 504}

VIDEOS = [
    {"slug":"tommy-clark-steal-linkedin-content-strategy", "speaker":"Tommy Clark", "title":"Steal this LinkedIn content strategy for B2B SaaS startups", "id":"DZtWDoRhksQ", "url":"https://www.youtube.com/watch?v=DZtWDoRhksQ"},
    {"slug":"tommy-clark-early-stage-saas-linkedin", "speaker":"Tommy Clark", "title":"The best LinkedIn content strategy for early-stage SaaS", "id":"TZSADGhY-x4", "url":"https://www.youtube.com/watch?v=TZSADGhY-x4"},
    {"slug":"sam-dunning-george-terry-linkedin-lead-gen-2026", "speaker":"Sam Dunning / George Terry", "title":"The Best LinkedIn Lead Generation Strategy for 2026", "id":"yUzKff_6pX0", "url":"https://www.youtube.com/watch?v=yUzKff_6pX0"},
    {"slug":"nick-bennett-b2b-influence-linkedin", "speaker":"Nick Bennett", "title":"Defining B2B Influence on LinkedIn with Nick Bennett", "id":"bPw3qufzUS0", "url":"https://www.youtube.com/watch?v=bPw3qufzUS0"},
    {"slug":"ross-simmonds-b2b-content-distribution", "speaker":"Ross Simmonds", "title":"B2B Content Marketing & Distribution with Ross Simmonds", "id":"7_bFP2iVVN0", "url":"https://www.youtube.com/watch?v=7_bFP2iVVN0"},
    {"slug":"chris-walker-daniel-murray-linkedin-deep-dive", "speaker":"Chris Walker / Daniel Murray", "title":"A Linkedin Deep Dive with Daniel Murray | State of Demand Gen", "id":"O_VoBwHCNGw", "url":"https://www.youtube.com/watch?v=O_VoBwHCNGw"},

    # Additional videos
    {"slug":"justin-welsh-systemizing-content-structure", "speaker":"Justin Welsh", "title":"Systemizing Your Content Structure with Justin Welsh", "id":"SkR3XB6Bvq8", "url":"https://www.youtube.com/watch?v=SkR3XB6Bvq8"},
    {"slug":"justin-welsh-grow-linkedin-2026", "speaker":"Justin Welsh", "title":"How to grow on LinkedIn in 2026 with this 3 step system", "id":"m_AQfKsUAwQ", "url":"https://www.youtube.com/watch?v=m_AQfKsUAwQ"},
    {"slug":"justin-welsh-built-solo-business-linkedin", "speaker":"Justin Welsh", "title":"How Justin Welsh built a $2M solo business on LinkedIn", "id":"7ubiaJ3gmIM", "url":"https://www.youtube.com/watch?v=7ubiaJ3gmIM"},
    {"slug":"saas-linkedin-content-strategy", "speaker":"Unknown / SaaS LinkedIn Creator", "title":"The Best LinkedIn Content Strategy for SaaS", "id":"5lcZl4iEjI0", "url":"https://www.youtube.com/watch?v=5lcZl4iEjI0"},
    {"slug":"founder-led-linkedin-strategy-jess-chilman", "speaker":"Jess Chilman", "title":"How to grow your SaaS business with a founder-led LinkedIn strategy", "id":"WeycaK0PTe4", "url":"https://www.youtube.com/watch?v=WeycaK0PTe4"},
]

def get_json(url: str, **kwargs: Any) -> tuple[dict[str, Any], int]:
    last_error: Exception | None = None
    for attempt in range(1, REQUEST_ATTEMPTS + 1):
        try:
            response = requests.get(
                url,
                timeout=(CONNECT_TIMEOUT_SECONDS, READ_TIMEOUT_SECONDS),
                **kwargs,
            )
            response.raise_for_status()
            return response.json(), response.status_code
        except HTTPError as error:
            last_error = error
            status_code = error.response.status_code if error.response is not None else None
            if status_code not in RETRY_STATUS_CODES or attempt == REQUEST_ATTEMPTS:
                raise
        except RequestException as error:
            last_error = error
            if attempt == REQUEST_ATTEMPTS:
                raise

        delay = RETRY_BACKOFF_SECONDS * attempt
        print(f"request failed ({last_error}); retrying in {delay}s...")
        time.sleep(delay)

    raise RuntimeError(f"request failed after {REQUEST_ATTEMPTS} attempts: {last_error}")


def poll_job(job_id: str) -> dict[str, Any]:
    endpoint = f"https://api.supadata.ai/v1/transcript/{job_id}"
    headers = {"x-api-key": API_KEY}
    for _ in range(MAX_POLL_ATTEMPTS):
        payload, _ = get_json(endpoint, headers=headers)
        status = payload.get("status")
        if status == "completed":
            return payload
        if status == "failed":
            raise RuntimeError(f"Supadata transcript job failed: {payload.get('error', payload)}")
        time.sleep(POLL_SECONDS)
    raise TimeoutError(f"Supadata transcript job did not complete after {MAX_POLL_ATTEMPTS} polls")


def fetch_transcript(video_url: str) -> dict[str, Any]:
    if not API_KEY:
        raise RuntimeError("SUPADATA_API_KEY is not set")
    endpoint = "https://api.supadata.ai/v1/transcript"
    headers = {"x-api-key": API_KEY}
    params = {"url": video_url, "text": "false", "mode": SUPADATA_MODE}
    payload, status_code = get_json(endpoint, headers=headers, params=params)
    if status_code == 202 and payload.get("jobId"):
        return poll_job(str(payload["jobId"]))
    return payload


def normalize_chunks(chunks: list[Any]) -> str:
    lines: list[str] = []
    for item in chunks:
        if isinstance(item, dict):
            text = item.get("text")
            if text:
                lines.append(str(text))
        elif item:
            lines.append(str(item))
    return "\n".join(lines)


def normalize_transcript(payload: dict[str, Any]) -> str:
    # Support common response shapes.
    if isinstance(payload.get("content"), str):
        return payload["content"]
    if isinstance(payload.get("content"), list):
        return normalize_chunks(payload["content"])
    if isinstance(payload.get("transcript"), str):
        return payload["transcript"]
    if isinstance(payload.get("transcript"), list):
        return normalize_chunks(payload["transcript"])
    if isinstance(payload.get("data"), dict):
        data = payload["data"]
        if isinstance(data.get("content"), str):
            return data["content"]
        if isinstance(data.get("content"), list):
            return normalize_chunks(data["content"])
        if isinstance(data.get("transcript"), str):
            return data["transcript"]
        if isinstance(data.get("transcript"), list):
            return normalize_chunks(data["transcript"])
    if payload.get("status") == "completed" and isinstance(payload.get("result"), dict):
        return normalize_transcript(payload["result"])
    return str(payload)


def has_populated_transcript(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    if "TRANSCRIPT_NOT_FETCHED" in text:
        return False
    transcript = text.split("## Transcript", 1)[-1].strip()
    return len(transcript) >= MIN_TRANSCRIPT_CHARS


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    captured_at = datetime.now(timezone.utc).isoformat()
    for video in VIDEOS:
        out_path = OUT / f"{video['slug']}.md"
        if has_populated_transcript(out_path) and not OVERWRITE:
            print(f"skipping {video['slug']}.md (already populated)")
            continue

        print(f"fetching {video['slug']}...")
        payload = fetch_transcript(video["url"])
        transcript = normalize_transcript(payload)
        md = f"""# YouTube Transcript — {video['title']}

- **Speaker / host:** {video['speaker']}
- **Video title:** {video['title']}
- **Video ID:** {video['id']}
- **URL:** {video['url']}
- **Captured at:** {captured_at}
- **Collection method:** Supadata YouTube Transcript API

## Transcript

{transcript}
"""
        out_path.write_text(md, encoding="utf-8")
        print(f"wrote {video['slug']}.md")

if __name__ == "__main__":
    main()
