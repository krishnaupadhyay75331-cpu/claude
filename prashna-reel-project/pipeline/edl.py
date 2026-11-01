# source gaps (start,end) from silencedetect -22dB; remove middle of gaps > 0.28s keeping 0.08s each side
gaps=[(4.21,4.60),(7.16,7.63),(9.07,9.32),(13.20,13.43),(14.92,15.40),(19.51,19.81),(20.28,20.53),(23.59,23.81),(26.11,26.52),(29.20,29.88)]
SRC_END=36.2; START=0.18
keep=[]; cur=START
for a,b in gaps:
    if b-a>0.28:
        keep.append((cur,a+0.08)); cur=b-0.08
keep.append((cur,SRC_END))
def s2e(t):
    e=0
    for a,b in keep:
        if t<a: return e
        if t<=b: return e+(t-a)
        e+=b-a
    return e
if __name__=="__main__":
    import json
    tot=sum(b-a for a,b in keep); print(keep, round(tot,3))
    json.dump({"keep":keep,"total":tot},open("edl.json","w"))
