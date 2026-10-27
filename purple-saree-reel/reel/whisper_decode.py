import sys,json,wave,base64,numpy as np,onnxruntime as ort
M="/root/models/sherpa-onnx-whisper-large-v3/large-v3-"
so=ort.SessionOptions();so.intra_op_num_threads=4
enc=ort.InferenceSession(M+"encoder.int8.onnx",so,providers=['CPUExecutionProvider'])
dec=ort.InferenceSession(M+"decoder.int8.onnx",so,providers=['CPUExecutionProvider'])
meta=enc.get_modelmeta().custom_metadata_map
toks={}
for l in open(M+"tokens.txt",encoding="utf-8"):
    p=l.rstrip("\n").split(" ")
    if len(p)==2: toks[int(p[1])]=base64.b64decode(p[0])
langs=dict(zip(meta['all_language_codes'].split(','),map(int,meta['all_language_tokens'].split(','))))
nonsp=set(map(int,meta['non_speech_tokens'].split(',')))
def mel_filters(sr=16000,n_fft=400,n_mels=128):
    def hz2mel(f):
        f=np.asarray(f,float);m=f/(200/3);lo=1000;lm=lo/(200/3);ls=np.log(6.4)/27
        return np.where(f>=lo,lm+np.log(np.maximum(f,1e-9)/lo)/ls,m)
    def mel2hz(m):
        m=np.asarray(m,float);lo=1000;lm=lo/(200/3);ls=np.log(6.4)/27
        return np.where(m>=lm,lo*np.exp(ls*(m-lm)),(200/3)*m)
    fft=np.linspace(0,sr/2,n_fft//2+1);mp=mel2hz(np.linspace(hz2mel(0),hz2mel(sr/2),n_mels+2))
    fd=np.diff(mp);ramps=mp[:,None]-fft[None,:];W=np.zeros((n_mels,len(fft)))
    for i in range(n_mels):
        W[i]=np.maximum(0,np.minimum(-ramps[i]/fd[i],ramps[i+2]/fd[i+1]))
    W*=(2.0/(mp[2:n_mels+2]-mp[:n_mels]))[:,None];return W
MF=mel_filters()
def logmel(a):
    a=np.concatenate([a,np.zeros(480000-len(a),np.float32)])[:480000]
    a=np.pad(a,200,mode='reflect');win=np.hanning(401)[:-1]
    fr=np.lib.stride_tricks.sliding_window_view(a,400)[::160]*win
    mag=np.abs(np.fft.rfft(fr,axis=1))**2;mag=mag[:-1].T
    lm=np.log10(np.maximum(MF@mag,1e-10));lm=np.maximum(lm,lm.max()-8);return ((lm+4)/4).astype(np.float32)[None]
def decode(a,lang,prompt_ids=None,ts=True):
    ck,cv=enc.run(None,{"mel":logmel(a)})
    sot=[50258,langs[lang],50360]+([] if ts else [50364])
    seq=([50362]+prompt_ids[-200:] if prompt_ids else [])+sot
    sk=np.zeros((32,1,448,1280),np.float32);sv=np.zeros_like(sk)
    out=[];offset=0;cur=seq;last_ts=0
    for step in range(440-len(seq)):
        lg,sk,sv=dec.run(None,{"tokens":np.array([cur],np.int64),"in_n_layer_self_k_cache":sk,"in_n_layer_self_v_cache":sv,"n_layer_cross_k":ck,"n_layer_cross_v":cv,"offset":np.array([offset],np.int64)})
        offset+=len(cur);l=lg[0,-1].astype(np.float64)
        l[list(nonsp)]=-1e9;l[50358:50365]=-1e9;l[50258:50358]=-1e9
        if ts:
            # timestamp rules: pair timestamps, monotonic
            if len(out)>=1 and out[-1]>=50365 and (len(out)<2 or out[-2]>=50365): l[50365:]=-1e9  # after pair, need text
            elif len(out)>=1 and out[-1]>=50365: l[:50257]=-1e9  # unpaired ts must... (allow text)
            if not out: l[:50365]=-1e9; l[50365+51:]=-1e9
            l[50365:50365+last_ts]=-1e9
            lp=l-np.logaddexp.reduce(l);
            if np.logaddexp.reduce(lp[50365:])>lp[:50365].max(): l[:50365]=-1e9
        t=int(np.argmax(l))
        if t==50257: break
        if t>=50365: last_ts=t-50365
        out.append(t);cur=[t]
    return out
def render(out):
    segs=[];txt=b"";st=None
    for t in out:
        if t>=50365:
            tt=(t-50365)*0.02
            if st is None: st=tt
            else:
                segs.append((st,tt,txt.decode('utf-8','replace').strip()));txt=b"";st=None
        elif t<50257: txt+=toks.get(t,b"")
    if txt: segs.append((st or 0,None,txt.decode('utf-8','replace').strip()))
    return segs
if __name__=="__main__":
    w=wave.open(sys.argv[1]);sr=w.getframerate();a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
    wins=json.loads(sys.argv[3]);res=[];prompt=[int(x) for x in sys.argv[4].split(',')] if len(sys.argv)>4 and sys.argv[4] else None
    for s,e in wins:
        o=decode(a[int(s*sr):int(e*sr)],sys.argv[2],prompt)
        for a0,b0,t in render(o):
            print(f"{s+a0:6.2f}-{(s+b0) if b0 is not None else -1:6.2f} | {t}",flush=True); res.append([s+a0,(s+b0) if b0 is not None else e,t])
        prompt=[t for t in o if t<50257]
    json.dump(res,open(sys.argv[5] if len(sys.argv)>5 else "out.json","w"),ensure_ascii=False,indent=1)
