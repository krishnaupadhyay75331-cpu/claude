# Reel edit: rebuilding

The reel is cut entirely from the presenter's single take: WIDE / MEDIUM / CLOSE punch-ins, with no B-roll.

To rebuild it, run `render/build.sh /path/to/source.mov work/`. The work directory also needs `models/selfie_multiclass.tflite` from the MediaPipe model storage.

`render/` contains:
- `plan.py`: corrected transcript, onset refinement, tightening and the time map
- `segment.py`: presenter matte
- `render.py`: the compositor
- `audio.py`: voice chain, music and SFX synthesis, and mastering
- `gen_docs.py`: CSV, SRT and EDL
- `qc.py`: automated checks
