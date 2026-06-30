#!/usr/bin/env bash
set -euo pipefail

# Free fallback for videos with public subtitles/captions.
# Requires: yt-dlp and ffmpeg installed locally.
# Run from Git Bash, WSL, macOS, or Linux.
# This downloads auto subtitles only, skips video download, and saves files in /research/youtube-transcripts/raw-vtt.

for tool in yt-dlp ffmpeg; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "Missing required command: $tool" >&2
    exit 1
  fi
done

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/research/youtube-transcripts/raw-vtt"
mkdir -p "$OUT"

VIDEOS=(
  "https://www.youtube.com/watch?v=DZtWDoRhksQ"
  "https://www.youtube.com/watch?v=TZSADGhY-x4"
  "https://www.youtube.com/watch?v=yUzKff_6pX0"
  "https://www.youtube.com/watch?v=bPw3qufzUS0"
  "https://www.youtube.com/watch?v=7_bFP2iVVN0"
  "https://www.youtube.com/watch?v=O_VoBwHCNGw"
  "https://www.youtube.com/watch?v=SkR3XB6Bvq8"
  "https://www.youtube.com/watch?v=m_AQfKsUAwQ"
  "https://www.youtube.com/watch?v=7ubiaJ3gmIM"
  "https://www.youtube.com/watch?v=5lcZl4iEjI0"
  "https://www.youtube.com/watch?v=WeycaK0PTe4"

)

failures=0
for url in "${VIDEOS[@]}"; do
  yt-dlp \
    --skip-download \
    --write-auto-sub \
    --write-sub \
    --sub-langs "en.*" \
    --convert-subs vtt \
    -o "$OUT/%(id)s.%(ext)s" \
    "$url" || failures=$((failures + 1))
done

if (( failures > 0 )); then
  echo "$failures video(s) failed to download subtitles" >&2
  exit 1
fi
