import numpy as np, subprocess, json
FPS=30
# Corrected Hinglish words with whisper-small (en pass) start/end, source seconds
W = """kya 0.00 0.50|aapke 0.50 0.74|mind 0.74 0.94|mein 0.94 1.06|bhi 1.06 1.22|shaadi 1.22 1.66|career 1.66 2.14|ya 2.18 2.30|future 2.30 2.48|ko 2.48 2.72|lekar 2.72 2.88|koi 2.88 3.12|aisa 3.12 3.42|sawaal 3.42 3.74|hai 3.74 3.80|jiska 3.84 4.06|jawab 4.06 4.30|aap 4.30 4.32|kaafi 4.32 4.74|time 4.74 4.90|se 4.90 5.04|dhoondh 5.04 5.26|rahe 5.26 5.42|ho 5.42 5.54|kabhi 5.88 6.10|kabhi 6.10 6.30|zaroorat 6.30 6.58|hoti 6.58 6.84|hai 6.84 6.92|humein 6.98 7.16|apni 7.16 7.40|situation 7.40 7.66|ko 7.66 8.06|ek 8.06 8.14|naye 8.14 8.42|perspective 8.42 8.96|se 8.96 9.10|samajhne 9.10 9.52|ki 9.52 9.70|jiske 10.04 10.30|liye 10.30 10.50|aap 10.50 10.64|mil 10.64 10.74|sakte 10.74 11.10|hain 11.10 11.20|Pushpa 11.30 11.58|Upadhyay 11.58 11.94|ji 11.94 12.10|se 12.10 12.26|jinhe 12.42 12.62|Jyotish 12.62 13.06|ki 13.06 13.20|field 13.20 13.42|mein 13.42 13.58|21 13.58 13.86|saal 13.86 14.14|ka 14.14 14.24|experience 14.24 14.54|hai 14.54 14.88|chahe 15.18 15.44|aapko 15.44 15.78|kundli 15.78 16.16|vishleshan 16.16 16.66|face 16.98 17.18|reading 17.18 17.56|prashna 18.18 18.50|kundli 18.50 18.88|ya 18.88 19.26|vastu 19.26 19.56|se 19.56 19.70|related 19.70 19.92|guidance 19.92 20.38|chahiye 20.38 20.58|Maa 20.72 21.04|Chamunda 21.04 21.36|Jyotish 21.36 21.80|mein 21.80 21.92|aap 21.92 22.16|apni 22.16 22.36|zaroorat 22.36 22.70|ke 22.70 22.86|according 22.86 23.06|consultation 23.06 23.70|ke 23.70 23.96|baare 23.96 24.16|mein 24.16 24.26|jaan 24.26 24.52|sakte 24.52 24.82|hain 24.82 24.92|agar 25.14 25.40|aap 25.40 25.66|bhi 25.66 25.74|consultation 25.74 26.08|lena 26.08 26.50|chahte 26.50 26.88|hain 26.88 26.98|toh 27.10 27.26|abhi 27.26 27.38|hume 27.38 27.62|DM 27.62 27.80|mein 27.80 27.92|consultation 27.92 28.26|likhkar 28.26 28.78|bhejiye 28.78 29.08|hamari 29.34 29.68|team 29.68 29.86|aapko 29.86 30.16|appointment 30.16 30.56|aur 30.56 30.86|consultation 30.86 31.26|process 31.26 31.88|ki 31.88 32.02|poori 32.02 32.28|details 32.28 32.54|share 32.54 32.86|kar 32.86 33.06|degi 33.06 33.20|Maa 33.86 34.34|Chamunda 34.34 34.64|Jyotish 34.64 35.00|aapke 35.16 35.40|sawaal 35.40 35.70|ko 35.70 35.82|samajhne 35.82 36.26|ki 36.26 36.44|ek 36.44 36.60|nayi 36.60 36.78|shuruaat 36.78 37.12"""
words=[dict(w=a.split()[0],s=float(a.split()[1]),e=float(a.split()[2])) for a in W.split("|")]
SIL=[(0,0.457),(5.495,5.913),(9.705,10.005),(14.832,15.183),(17.748,18.225),(29.085,29.380),(33.065,34.081),(37.124,38.03)]
# --- onset refinement on log-energy derivative
aud=np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i","src.mov","-ac","1","-ar","16000","-f","s16le","-"],capture_output=True).stdout,np.int16).astype(np.float32)/32768
hop=80; fr=np.lib.stride_tricks.sliding_window_view(aud,400)[::hop]
le=10*np.log10((fr**2).mean(1)+1e-9); le=np.convolve(le,np.ones(3)/3,'same'); d=np.diff(le,prepend=le[0])
def refine(t):
    for a,b in SIL:
        if a+0.05<=t<b: return b-0.01
    i0,i1=int((t-0.10)*200),int((t+0.08)*200)
    i0=max(i0,0); seg=d[i0:i1]
    return (i0+int(np.argmax(seg)))/200 if len(seg) else t
prev=-1
words[0]["s"]=0.45
for w in words:
    r=max(refine(w["s"]),prev+0.05); w["s_ref"]=round(r,3); prev=r
# --- tightening: silence >0.25s -> keep 0.25s (0.10 tail + 0.15 head); the jump-cut pause resumes exactly on the
#     first post-jump frame (34.034s) so the source jump and the tightening cut are one shot change
cuts=[]
for a,b in SIL[1:-1]:
    if (a,b)==(33.065,34.081): cuts.append((33.30,34.034)); continue
    L=b-a
    if L-0.25>=0.09: cuts.append((a+0.10,b-0.15))
START,END=0.40,37.244
f=lambda t:int(round(t*FPS))
segs=[]; cur=f(START)
for a,b in cuts: segs.append((cur,f(a))); cur=f(b)
segs.append((cur,f(END)))
def s2o(t):  # source seconds -> output frame
    fs=t*FPS; acc=0
    for a,b in segs:
        if fs<a: return acc
        if fs<b: return acc+int(round(fs-a))
        acc+=b-a
    return acc
total=sum(b-a for a,b in segs)
for w in words: w["of"]=s2o(w["s_ref"]); w["oe"]=s2o(w["e"])
json.dump(dict(segs=segs,total=total,words=words,cuts=cuts),open("plan.json","w"),indent=1)
print("segments",segs,"total frames",total,"=",total/FPS,"s")
print(" ".join(f"{w['w']}@{w['s']:.2f}->{w['s_ref']:.2f}/f{w['of']}" for w in words))
