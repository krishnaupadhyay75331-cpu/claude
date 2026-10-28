#!/usr/bin/env bash
# Render video track, then audio + mux.  usage: ./build.sh SOURCE.mov
set -euo pipefail
cd "$(dirname "$0")"
SRC="$1"
mkdir -p build out
python3 render.py "$SRC" build/video_only.mp4
python3 audio.py "$SRC" build/video_only.mp4 out/reel_prashna_kundli_v1.mp4
