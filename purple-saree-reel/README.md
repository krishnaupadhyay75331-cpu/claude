# Purple-saree Karwa Chauth reel: edit project

A 9:16 Hinglish reel cut from the raw talking-head clip (`copy_08F0E26B-…-compressed.mov`, 756×1344, 58.87 s). The edit is built entirely in code (Python + OpenCV + Pillow + ffmpeg), following the custom edit prompt in `../custom-edit-prompt-purple-saree.md`.

## Deliverables

| File | What it is |
|---|---|
| `purple-saree-reel.mp4` | Final export: H.264, 1080×1920, 30 fps, ~15 Mbps VBR, AAC 320 kbps stereo, Rec.709, −14 LUFS |
| `CAPTION-PLAN.md` | Transcript plus the caption plan table (source and output time · speech · HERO · companions · treatment · picture) |
| `PLACEHOLDERS.md` | Everything for you to confirm or fill in |
| `B-ROLL-PROMPTS.md` | B-roll briefs, adapted to her actual topic |
| `reel/` | Project source. Re-render after you add B-roll or change any wording |

## Re-rendering

```bash
pip install numpy opencv-python-headless pillow onnxruntime
# 1. person matte (once): u2net_human_seg.onnx from the rembg releases page in ~/.u2net/
python3 reel/seg.py SOURCE.mov work/masks.npy 2
# 2. picture (can be split into ranges and run in parallel: last two args = output seconds)
REEL_FONTS=reel/fonts python3 reel/render.py SOURCE.mov work/masks.npy work/video.mp4
# 3. sound: voice clean-up, music bed, SFX, ducking, loudness
python3 reel/mix.py SOURCE.mov work/mix.wav
# 4. mux + final encode
ffmpeg -i work/video.mp4 -i work/mix.wav -c:v libx264 -b:v 15M -maxrate 16M -bufsize 30M -pix_fmt yuv420p \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -c:a aac -b:a 320k -movflags +faststart purple-saree-reel.mp4
```

- **Captions and timings:** `reel/plan.py`. Every caption is built from `reel/words.json` (her words with aligned timestamps), so to change a word, edit it there or in the stack.
- **B-roll:** drop `b1.jpg` … `b7.jpg` and `memory.jpg` into `reel/broll/`. Missing files render as labelled slates.
- **Fonts** (all OFL, from Google Fonts): Quicksand, Great Vibes, Josefin Sans, Antonio, Bebas Neue.

## How the parts were made

- **Transcript:** Whisper large-v3 (the ONNX export from sherpa-onnx), run locally with a custom greedy decoder, with Hindi output romanised by hand to phonetic Hinglish. Word timings: syllable-weighted spread inside each pause-bounded chunk, snapped to spectral-flux onsets (`reel/align.py`).
- **Pauses:** the 14 S-block gaps are cut to 0.18 s, so the A-roll runs 53.8 s. A 2.0 s freeze for the CTA brings the total to 55.8 s.
- **A-roll:** Lanczos upscale to 1080×1920 plus an unsharp mask. There's no AI upscaler here, so punch-ins are capped at 1.35×. The person matte comes from U²-Net human segmentation, feathered about 6 px. Background: −1.2 EV, −40 % saturation, plum-lifted shadows, 8 px blur. Subject: highlight roll-off, whites −10, purple saturation −5 %, skin vibrance, +3 warm. Plum-tinted vignette, plum bottom gradient, 8 % grain.
- **Graphics and transitions:** all procedural (`reel/gfx.py`): word stacks, neon "?", phone cut-outs composited behind her via the matte, watercolour bubble, depth title, halo, callout tags, pills, stat title, CTA, paper-white flash with lilac haze, cream flash, tint pops, bokeh, film burn, pink leak, zoom-blur whip and light-burst flare.
- **Sound** (`reel/sound.py`, `reel/mix.py`): the voice chain is HPF 80 Hz, light denoise, de-esser, 3:1 compression. The music is a synthesized piano, pad and flute bed in D minor that resolves to F major on the happy-ending cut. It sits about 20 dB below the voice and ducks a further −8 dB whenever she speaks. The SFX are synthesized too (whooshes, flash hits, neon buzz and shimmer, temple bell, sparkles, pops, bloops, swell, riser, sub-boom, tape-whip). The mix goes through two-pass loudnorm to −14 LUFS and is limited to under −1 dBTP.
