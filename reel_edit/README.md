# Reel edit: swapping in the real B-roll

1. Generate the stills listed in `deliverables/ai_prompts.md` and save them in `assets/` with these exact names: `S1.png`, `S2.png`, `S3.png`, `S4.png`, `S5a.png`, `S5b.png` and `couple.png` (white background is fine), plus `bubble.png`, and either `S6.mp4` (preferred) or `S6.png`. JPGs also work.
2. Run `render/build.sh /path/to/source.mov work/`. The work directory also needs `models/selfie_multiclass.tflite` from the MediaPipe model storage.

   Alternatively, attach the assets in a new Claude session on this branch and ask for a re-render.

The renderer handles the rest automatically:
- Real stills are cover-fitted and amber-graded, and get the same Ken Burns moves, overlays and timings.
- In S4, the client is segmented so the halo sits behind her head.
- The couple cut-out is keyed and converted to B&W.

Missing files fall back to the labelled placeholders.

`render/` contains:
- `plan.py`: corrected transcript, onset refinement, tightening and the time map
- `segment.py`: presenter matte
- `render.py`: the compositor
- `audio.py`: voice chain, music and SFX synthesis, and mastering
- `gen_docs.py`: CSV, SRT and EDL
- `qc.py`: automated checks
