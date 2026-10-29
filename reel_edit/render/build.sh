#!/usr/bin/env bash
# Rebuild the reel. Usage: ./build.sh /path/to/source.mov [workdir]
# Needs: ffmpeg, python3 with numpy opencv-python-headless pillow scipy mediapipe faster-whisper,
# fonts Poppins / Antonio / Great Vibes in ~/.fonts, and models/selfie_multiclass.tflite in the workdir.
set -euo pipefail
SRC=$(realpath "$1"); WD=${2:-./work}; HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$WD/chunks" "$WD/frames"; cd "$WD"
ln -sf "$SRC" src.mov
[ -f plan.json ] || python3 "$HERE/plan.py"
[ -f src_rgb.raw ] || ffmpeg -v error -y -i src.mov -f rawvideo -pix_fmt rgb24 src_rgb.raw
[ -f matte.npy ] || python3 "$HERE/segment.py"
N=$(python3 -c "import json;print(json.load(open('plan.json'))['total'])")
for i in 0 1 2 3; do python3 "$HERE/render.py" . $((i*N/4)) $(((i+1)*N/4)) chunks/c$i.mp4 & done; wait
python3 "$HERE/audio.py" .
printf "file 'chunks/c%d.mp4'\n" 0 1 2 3 > chunks.txt
ffmpeg -v error -y -f concat -safe 0 -i chunks.txt -i mix_master.wav -map 0:v -map 1:a \
  -c:v libx264 -profile:v high -preset slow -b:v 18M -maxrate 22M -bufsize 36M -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 320k -ar 48000 -ac 2 -movflags +faststart -shortest "$HERE/../deliverables/reel_final.mp4"
python3 "$HERE/gen_docs.py" . "$HERE/../deliverables"
echo "done -> $HERE/../deliverables/reel_final.mp4"
