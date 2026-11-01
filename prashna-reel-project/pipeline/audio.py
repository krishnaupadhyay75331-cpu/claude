import numpy as np, json, subprocess
from edl import keep
SR=48000
a=np.fromfile('src.f32',np.float32).reshape(-1,2)
F=int(0.008*SR); parts=[]
for s,e in keep:
    seg=a[int(s*SR):int(e*SR)].copy(); r=np.linspace(0,1,F)[:,None]
    seg[:F]*=r; seg[-F:]*=r[::-1]; parts.append(seg)
dia=np.concatenate(parts); dia.astype(np.float32).tofile('dia_raw.f32')
tl=json.load(open('../reel/src/timeline.json')); T=tl['total']+0.3; N=int(T*SR); t=np.arange(N)/SR
rng=np.random.default_rng(7)
def env(n,a_,d): x=np.arange(n)/SR; return np.minimum(x/a_,1)*np.exp(-x/d)
# --- music: A minor devotional, tanpura-ish drone + soft piano chords, 66 bpm
mus=np.zeros(N)
def tone(f,dur,amp,decay,harm=(1,.5,.25,.12)):
    n=int(dur*SR); x=np.arange(n)/SR; y=sum(h*np.sin(2*np.pi*f*(k+1)*x*(1+0.0007*k)) for k,h in enumerate(harm))
    return amp*y*env(n,0.01,decay)
drone=0.035*(np.sin(2*np.pi*110*t)+0.6*np.sin(2*np.pi*164.81*t)+0.4*np.sin(2*np.pi*220.4*t))*(0.8+0.2*np.sin(2*np.pi*0.25*t))
mus+=drone
chords=[[220,261.63,329.63],[174.61,220,261.63],[261.63,329.63,392],[196,246.94,293.66]]
def place(at,y):
    st=int(at*SR); e=min(N,st+len(y))
    if st<N: mus[st:e]+=y[:e-st]
beat=60/66; bar=beat*4; k=0; tt=0.0
while tt<T:
    ch=chords[k%4]
    for j,f in enumerate(ch):
        place(tt+j*0.06,tone(f,bar*1.2,0.05,1.6))
    for b in range(4):   # melody arpeggio, soft
        f=ch[(b*2)%3]*2; place(tt+b*beat+beat/2,tone(f,beat*2,0.022,0.9))
    tt+=bar; k+=1
ir=rng.standard_normal(int(1.8*SR))*np.exp(-np.arange(int(1.8*SR))/SR/0.45)*0.02
mus=mus+np.convolve(mus,ir)[:N]*0.8
# swell 21-28s (remedy), lift on ending, fade in/out
g=np.ones(N); g*=np.clip(t/1.5,0,1); g*=np.clip((T-t)/1.2,0,1)
g*=1+0.35*np.exp(-((t-25.5)/2.5)**2)
mus*=g
# --- SFX
sfx=np.zeros(N)
def add(at,y,gain=1.0):
    st=int(at*SR); e=min(N,st+len(y)); 
    if st<N: sfx[st:e]+=gain*y[:e-st]
def bp_noise(n,f0,f1):
    x=rng.standard_normal(n); X=np.fft.rfft(x); fr=np.fft.rfftfreq(n,1/SR)
    fc=np.sqrt(f0*f1); X*=np.exp(-((np.log(fr+1)-np.log(fc))**2)/0.8); return np.fft.irfft(X,n)
def whoosh(d=0.45):
    n=int(d*SR); y=bp_noise(n,300,3000); x=np.arange(n)/n; return y*np.sin(np.pi*x)**2/ (np.abs(y).max()+1e-9)
def hit():
    n=int(0.5*SR); x=np.arange(n)/SR; y=rng.standard_normal(n)*np.exp(-x/0.04)*0.5+np.sin(2*np.pi*70*x)*np.exp(-x/0.12)
    return y/np.abs(y).max()
def ding(f=1568):
    n=int(1.2*SR); x=np.arange(n)/SR; y=sum(a_*np.sin(2*np.pi*f*m*x)*np.exp(-x/(0.5/m)) for a_,m in [(1,1),(.5,2.01),(.25,3.03)]); return y/np.abs(y).max()
def pop():
    n=int(0.08*SR); x=np.arange(n)/SR; return np.sin(2*np.pi*(900-5000*x)*x)*np.exp(-x/0.015)
def bell():
    n=int(2.5*SR); x=np.arange(n)/SR; y=sum(a_*np.sin(2*np.pi*f*x)*np.exp(-x/d) for a_,f,d in [(1,880,1.2),(.6,1386,.9),(.4,2205,.6),(.3,2968,.4)]); return y/np.abs(y).max()
def buzz():
    n=int(0.35*SR); x=np.arange(n)/SR; y=np.sign(np.sin(2*np.pi*120*x))*0.3*(rng.random(n)>0.2); y*=np.exp(-x/0.12); return y
def riser(d=1.2):
    n=int(d*SR); x=np.arange(n)/n; y=bp_noise(n,800,6000)*x**2; return y/np.abs(y).max()
def tick():
    n=int(0.03*SR); x=np.arange(n)/SR; return np.sin(2*np.pi*2500*x)*np.exp(-x/0.004)
for tr in tl['trans']:
    k=tr['k']; at=tr['t']
    add(at-0.22,whoosh(),0.10)
    if k in('white','bokeh','flare'): add(at,hit(),0.07)
    if k=='flare': add(at-1.2,riser(),0.06)
q0=tl['ov']['q'][0]; add(q0,buzz(),0.05); add(q0+0.05,ding(),0.06)
add(tl['ov']['halo'][0],bell(),0.06)
for tg in tl['ov']['tags']: add(tg['t'],pop(),0.12)
add(tl['ov']['name'][0],pop(),0.10)
for s in tl['stacks']:
    if s['hero']: add(s['hero']['s'],tick(),0.03)
mus.astype(np.float32).tofile('mus.f32'); sfx.astype(np.float32).tofile('sfx.f32')
print('dia',len(dia)/SR,'T',T)
