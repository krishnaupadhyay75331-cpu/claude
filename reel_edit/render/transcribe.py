import sys, json
from faster_whisper import WhisperModel
m = WhisperModel(sys.argv[1], device="cpu", compute_type="int8", cpu_threads=4)
import numpy as np, subprocess
audio = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",sys.argv[2],"-f","s16le","-ac","1","-ar","16000","-"],capture_output=True).stdout, np.int16).astype(np.float32)/32768
out = {}
for lang, prompt in [("hi", "आपका पार्टनर बदल क्यों गया? रिलेशनशिप, प्रॉब्लम, सॉल्यूशन, रेमेडीज़, गाइडेंस, व्हाट्सएप, लिंक"), ("en", "Hinglish: aapka partner badal kyu gaya? relationship mein problem hai, solution, remedies, guidance, whatsapp, link below")]:
    segs, info = m.transcribe(audio, language=lang, word_timestamps=True, beam_size=5, initial_prompt=prompt, vad_filter=False)
    words = []
    for s in segs:
        print(f"[{lang}] {s.start:6.2f}-{s.end:6.2f} {s.text}")
        for w in s.words: words.append((round(w.start,3), round(w.end,3), w.word.strip(), round(w.probability,2)))
    out[lang] = words
json.dump(out, open("words.json","w"), ensure_ascii=False, indent=0)
