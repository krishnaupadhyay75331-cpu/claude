# Writes the caption plan table (source + output times) from plan.py
import plan as P
segs=[];o=0.0
for s,e in P.KEEP:
    segs.append((s,e,o));o+=e-s
def s2o(t):
    for s,e,oo in segs:
        if t<s: return oo
        if t<=e: return oo+t-s
    return o
def tc(t): return f"{int(t//60)}:{t%60:05.2f}"
shots=P.SHOTS
def shot_for(t):
    for sh in shots:
        t1=99 if sh["t1"]=="END" else sh["t1"]
        if sh["t0"]<=t<t1: return sh
    return shots[-1]
def desc(sh):
    return f"B-roll #{sh['n']}" if sh["type"]=="broll" else {"wide":"A-roll wide","med":"A-roll medium 1.20×","close":"A-roll close 1.35×","tight":"A-roll (post-reframe) 1.05→1.08"}[sh["frame"]]
rows=[]
for st in P.STACKS:
    ws=st["words"];h=st["hero"]
    t0=ws[0][1];speech=" ".join(x[0] for x in ws)
    comp=" ".join(x[0] for i,x in enumerate(ws) if i!=h)
    tr="word stack"+(" · SINDOOR RED hero" if st.get("red") else "")+(" · top 25%" if st.get("y")==0.25 else "")
    if t0 in P.BUMPS or ws[h][1] in P.BUMPS: tr+=" · micro-shake"
    rows.append((t0,speech,ws[h][0],comp,tr,desc(shot_for(t0))))
names={"words":"script line (Great Vibes)","depth":"depth title (Josefin Thin, orchid→lilac→white)","stat":"stat title (Antonio Thin) + gold script","pill":"pill label","tags":"rani-pink callout tags","cta":"CTA line (Quicksand 80, curly quotes)","qmark":"neon “?”","phones":"B&W phone cut-outs (behind her)","bubble":"watercolour memory bubble","halo":"gold halo","wall_leak":"wall light leak","sparkle":"gold namaste sparkle","depth_words":"depth-title companion words"}
for e in P.EVENTS:
    k=e["kind"]
    if k=="words": txt=" ".join(x[0] for x in e["words"]); rows.append((e["t"],txt,txt,"",names[k],desc(shot_for(e["t"]))))
    elif k=="depth": rows.append((e["t"],"pyaar aur vishwas ka dharmik vrat hai",e["text"],"pyaar aur · ka dharmik · vrat hai",names[k],desc(shot_for(e["t"]))))
    elif k=="stat": rows.append((e["t"],"jo pyaar aur barabari ki",e["text"],e.get("script",""),names[k]+" — no number spoken, fallback word",desc(shot_for(e["t"]))))
    elif k=="pill": rows.append((e["t"],e["text"],e["text"],e.get("script",""),names[k],desc(shot_for(e["t"]))))
    elif k=="tags": rows.append((e["t"],"(values she names in S11–S12)"," / ".join(x[0] for x in e["tags"]),"",names[k],desc(shot_for(e["t"]))))
    elif k=="cta": rows.append((e["t"],"(on the end freeze)"," ".join(e["words"]),"",names[k],"freeze-frame + push 100→104%"))
rows.sort(key=lambda r:r[0])
out=["| Src | Out | Speech (Hinglish) | HERO | Companion words | Treatment | Picture |","|---|---|---|---|---|---|---|"]
for t0,sp,hero,comp,tr,pic in rows:
    out.append(f"| {tc(t0)} | {tc(s2o(t0))} | {sp} | **{hero}** | {comp} | {tr} | {pic} |")
print("\n".join(out))
