import React from 'react';
import {
  AbsoluteFill, OffthreadVideo, Sequence, staticFile, useCurrentFrame, interpolate, Easing, random,
} from 'remotion';
import tlRaw from './timeline.json';
import headsRaw from './heads.json';

const tl: any = tlRaw;
const heads: any = headsRaw; // per edit frame: [x, top] or null; plus per-shot focus
const FPS = 30;
const W = 1080, H = 1920;
const C = {
  walnut: '#1A100C', plum: '#4B1D5E', orchid: '#A24FC0', lilac: '#E6D2F2', rose: '#E2477F',
  gold: '#E3B04F', goldL: '#F8DE9C', sindoor: '#C4122F', cream: '#EFE6D6',
};
const f = (t: number) => Math.round(t * FPS);
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};

const fontCss = `
@font-face{font-family:Q;src:url(${staticFile('fonts/quicksand-latin-500-normal.woff2')});font-weight:500}
@font-face{font-family:Q;src:url(${staticFile('fonts/quicksand-latin-700-normal.woff2')});font-weight:700}
@font-face{font-family:JThin;src:url(${staticFile('fonts/josefin-sans-latin-100-normal.woff2')})}
@font-face{font-family:GV;src:url(${staticFile('fonts/great-vibes-latin-400-normal.woff2')})}
@font-face{font-family:AntThin;src:url(${staticFile('fonts/antonio-latin-100-normal.woff2')})}
`;

// ---------- shot helpers ----------
const shots: any[] = tl.shots;
const shotAt = (fr: number) => shots.find((s) => fr >= f(s.e_in) && fr < f(s.e_out)) || shots[shots.length - 1];

function shotTransform(s: any, fr: number) {
  const a = f(s.e_in), b = f(s.e_out);
  const p = interpolate(fr, [a, b], [0, 1], {...clamp, easing: Easing.inOut(Easing.sin)});
  let z = s.zoom[0] + (s.zoom[1] - s.zoom[0]) * p;
  let blur = 0;
  if (s.tin === 'whip') {
    const k = interpolate(fr, [a, a + 20], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
    z *= 1.8 - 0.8 * k;
    blur = interpolate(fr, [a, a + 5], [14, 0], clamp);
  }
  // outgoing whip blur on the shot before a whip
  const nxt = shots[shots.indexOf(s) + 1];
  if (nxt && nxt.tin === 'whip') {
    const k = interpolate(fr, [b - 5, b], [0, 1], clamp);
    z *= 1 + 0.35 * k * k;
    blur = Math.max(blur, 16 * k);
  }
  const fx = s.focus ? s.focus[0] : W / 2, fy = s.focus ? s.focus[1] : H / 2;
  const drift = Math.sin((fr - a) / 45) * 6;
  return {z, fx, fy, blur, drift};
}
// screen position of a source point under a shot transform
const toScreen = (x: number, y: number, t: any) => [t.fx + t.z * (x - t.fx) + t.drift, t.fy + t.z * (y - t.fy)];

const Plate: React.FC<{s: any; layer: 'base' | 'subject'}> = ({s, layer}) => {
  const fr = useCurrentFrame() + f(s.e_in);
  const t = shotTransform(s, fr);
  const cw = s.angle.startsWith('CW');
  const src = cw ? staticFile(s.angle === 'CW_idols' ? 'cw_idols.mp4' : 'cw_shiva.mp4')
    : staticFile(layer === 'base' ? 'aroll.mp4' : 'subject.webm');
  return (
    <AbsoluteFill style={{transform: `translateX(${t.drift}px) scale(${t.z})`, transformOrigin: `${t.fx}px ${t.fy}px`,
      filter: `contrast(1.13) brightness(0.92) saturate(1.06)${t.blur > 0.2 ? ` blur(${t.blur}px)` : ''}`}}>
      <OffthreadVideo src={src} startFrom={cw ? 0 : f(s.e_in)} muted transparent={layer === 'subject'}
        style={{width: W, height: H}} />
    </AbsoluteFill>
  );
};

// ---------- captions ----------
const est = (txt: string, px: number) => txt.length * px * 0.5;
const Word: React.FC<{w: any; size: number; hero?: boolean; color?: string; font?: string; weight?: number; glow?: string}> = ({w, size, hero, color, font, weight, glow}) => {
  const fr = useCurrentFrame();
  const st = f(w.s);
  const d = hero ? 8 : 6;
  const p = interpolate(fr, [st, st + d], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const sc = hero ? interpolate(fr, [st, st + 8], [1.12, 1], {...clamp, easing: Easing.out(Easing.back(1.6))}) : 1;
  return (
    <span style={{display: 'inline-block', opacity: p, filter: `blur(${(1 - p) * 25}px)`,
      transform: `translateY(${(1 - p) * 8}px) scale(${sc})`, marginRight: size * 0.22, fontSize: size,
      color: color || 'white', fontFamily: font || 'Q', fontWeight: weight || (hero ? 700 : 500),
      textShadow: glow || '0 0 12px rgba(0,0,0,0.45)'}}>{w.text.replace(/^_$/, '')}</span>
  );
};

const Stack: React.FC<{s: any}> = ({s}) => {
  const fr = useCurrentFrame();
  const endF = s.end == null || s.style === 'cta' ? 99999 : f(s.end);
  const out = interpolate(fr, [endF, endF + 4], [0, 1], clamp);
  if (fr < f(s.start) - 1 || fr > endF + 5) return null;
  const wrap: React.CSSProperties = {opacity: 1 - out, filter: out > 0 ? `blur(${out * 20}px)` : undefined};
  const leadTxt = s.lead.map((w: any) => w.text).join(' ');
  const trailTxt = s.trail.map((w: any) => w.text).join(' ');

  if (s.style === 'depth') return null; // rendered in the behind layer
  if (s.style === 'script') {
    return (
      <div style={{...wrap, position: 'absolute', top: 1150, width: W, textAlign: 'center'}}>
        {s.trail.concat(s.lead).sort((a: any, b: any) => a.s - b.s).map((w: any, i: number) => (
          <Word key={i} w={{...w, text: w.text.charAt(0).toUpperCase() + w.text.slice(1)}} size={104} font="GV" weight={400} color={C.goldL}
            glow={`0 0 18px rgba(227,176,79,0.8), 0 0 4px rgba(0,0,0,0.6)`} />))}
      </div>
    );
  }
  if (s.style === 'cta') {
    const words = [s.hero, ...s.trail];
    return (
      <div style={{...wrap, position: 'absolute', top: 1300, width: W, textAlign: 'center'}}>
        <div style={{marginBottom: 6}}>{s.lead.map((w: any, i: number) => <Word key={i} w={w} size={34} />)}</div>
        <div>
          <Word w={{...words[0], text: '“' + words[0].text}} size={88} hero />
          {words.slice(1).map((w: any, i: number) => <Word key={i} w={{...w, text: w.text + (i === words.length - 2 ? '”' : '')}} size={88} hero />)}
        </div>
      </div>
    );
  }
  const heroSize = s.hero.text.length > 10 ? 118 : 132;
  const hw = est(s.hero.text, heroSize) * 1.1;
  const red = s.style === 'red';
  return (
    <div style={{...wrap, position: 'absolute', left: 0, top: 0, width: W, height: H}}>
      <div style={{position: 'absolute', left: W / 2, top: 1382, transform: 'translate(-50%, -100%)', whiteSpace: 'nowrap', lineHeight: 1}}>
        {s.lead.length > 0 && (
          <div style={{position: 'absolute', bottom: '88%', ...(est(leadTxt, 31) > hw ? {left: '50%', transform: 'translateX(-50%)'} : {right: 0}), whiteSpace: 'nowrap', opacity: 0.92}}>
            {s.lead.map((w: any, i: number) => <Word key={i} w={w} size={31} />)}
          </div>)}
        <Word w={{...s.hero, text: s.hero.text.replace(/[,.?]+$/, '').replace(/^./, (c: string) => c.toUpperCase())}} size={heroSize} hero
          color={red ? C.sindoor : 'white'} glow={red ? '0 0 14px rgba(255,255,255,0.55), 0 0 30px rgba(196,18,47,0.5)' : undefined} />
        {s.trail.length > 0 && (
          <div style={{position: 'absolute', top: '94%', ...(est(trailTxt, 31) > hw ? {left: '50%', transform: 'translateX(-50%)'} : {left: 0}), whiteSpace: 'nowrap', opacity: 0.92}}>
            {s.trail.map((w: any, i: number) => <Word key={i} w={w} size={31} />)}
          </div>)}
      </div>
    </div>
  );
};

// ---------- behind-subject elements ----------
const headAt = (fr: number) => heads.frames[Math.min(Math.max(fr, 0), heads.frames.length - 1)] || [540, 400];

const DepthTitle: React.FC<{s: any}> = ({s}) => {
  const fr = useCurrentFrame();
  const st = f(s.start), endF = f(s.end);
  if (fr < st - 1 || fr > endF + 6) return null;
  const sh = shotAt(fr); const t = shotTransform(sh, fr);
  const [hx, top] = headAt(fr); const [, sy] = toScreen(hx, top, t);
  const wipe = interpolate(fr, [st, st + 10], [0, 100], {...clamp, easing: Easing.out(Easing.cubic)});
  const out = interpolate(fr, [endF, endF + 5], [0, 1], clamp);
  const text = s.hero.text.replace(/[,.?]+$/, '');
  const word = text.charAt(0).toUpperCase() + text.slice(1);
  const size = word.length > 6 ? 250 : 300;
  const cy = Math.max(sy + 40, 330);
  return (
    <AbsoluteFill style={{opacity: 1 - out, filter: out ? `blur(${out * 18}px)` : undefined}}>
      <div style={{position: 'absolute', top: cy - size * 0.55, width: W, textAlign: 'center', lineHeight: 1,
        fontFamily: 'JThin', fontSize: size, letterSpacing: -4,
        background: `linear-gradient(180deg, ${C.orchid} 10%, ${C.lilac} 60%, #FFFFFF 95%)`,
        WebkitBackgroundClip: 'text', color: 'transparent', opacity: 0.88,
        clipPath: `inset(0 ${100 - wipe}% 0 0)`, filter: 'drop-shadow(0 0 1px rgba(227,176,79,0.6))'}}>{word}</div>
      <div style={{position: 'absolute', top: cy - size * 0.62, width: W, textAlign: 'center'}}>
        <div style={{display: 'inline-block', transform: `translateX(${size * 0.9}px)`}}>
          {s.lead.map((w: any, i: number) => <Word key={i} w={w} size={34} />)}</div>
      </div>
      <div style={{position: 'absolute', top: cy + size * 0.42, width: W, textAlign: 'center'}}>
        <div style={{display: 'inline-block', transform: `translateX(${-size * 0.5}px)`}}>
          {s.trail.map((w: any, i: number) => <Word key={i} w={w} size={34} />)}</div>
      </div>
    </AbsoluteFill>
  );
};

const Halo: React.FC = () => {
  const fr = useCurrentFrame();
  const [a, b] = tl.ov.halo.map(f);
  if (fr < a || fr > b + 6) return null;
  const sh = shotAt(fr); const t = shotTransform(sh, fr);
  const [hx, top] = headAt(fr); const [sx, sy] = toScreen(hx, top + 120, t);
  const g = interpolate(fr, [a, a + 15], [0, 1], {...clamp, easing: Easing.out(Easing.back(1.2))});
  const o = interpolate(fr, [b, b + 6], [1, 0], clamp) * 0.62;
  const pulse = 1 + 0.025 * Math.sin(fr / 6);
  const r = 250 * g * pulse * t.z;
  return (
    <AbsoluteFill style={{opacity: o}}>
      <div style={{position: 'absolute', left: sx - r, top: sy - r, width: 2 * r, height: 2 * r, borderRadius: '50%',
        background: `radial-gradient(circle, #FCEBC2 0%, #F8DE9C 48%, rgba(227,176,79,0.9) 58%, rgba(227,176,79,0.35) 66%, rgba(227,176,79,0) 72%)`,
        filter: 'blur(3px)', boxShadow: '0 0 90px 30px rgba(227,176,79,0.35)'}} />
    </AbsoluteFill>
  );
};

// ---------- front overlays ----------
const NeonQ: React.FC = () => {
  const fr = useCurrentFrame();
  const [a, b] = tl.ov.q.map(f);
  if (fr < a || fr > b + 8) return null;
  const sh = shotAt(fr); const t = shotTransform(sh, fr);
  const [hx, top] = headAt(fr); let [sx, sy] = toScreen(hx, top, t);
  sy = Math.max(sy - 150, 230); sx = Math.min(Math.max(sx + 20, 180), 900);
  const k = fr - a;
  const sc = interpolate(k, [0, 6, 10], [0, 1.2, 1], clamp);
  const flick = k < 10 ? ([1, 0.2, 1, 0.1, 1, 1, 0.4, 1, 1, 1][k] ?? 1) : 1;
  const out = interpolate(fr, [b, b + 8], [1, 0], clamp);
  const bob = Math.sin((fr / FPS) * (2 * Math.PI / 1.5)) * 10;
  return (
    <div style={{position: 'absolute', left: sx - 90, top: sy - 120 + bob, width: 180, height: 240,
      transform: `scale(${sc})`, opacity: flick * out, filter: out < 1 ? `blur(${(1 - out) * 15}px)` : undefined}}>
      <svg width="180" height="240" viewBox="0 0 180 240" style={{overflow: 'visible',
        filter: 'drop-shadow(0 0 8px #FF6FB5) drop-shadow(0 0 22px #FF6FB5) drop-shadow(0 0 40px #D6338A)'}}>
        <text x="90" y="200" textAnchor="middle" fontFamily="Q" fontWeight={700} fontSize="230"
          fill="none" stroke="#FFE4F1" strokeWidth="7" strokeLinejoin="round">?</text>
      </svg>
    </div>
  );
};

const Pill: React.FC<{text: string; start: number; end: number; x: number; y: number; size?: number}> = ({text, start, end, x, y, size = 40}) => {
  const fr = useCurrentFrame();
  const a = f(start), b = f(end);
  if (fr < a || fr > b + 5) return null;
  const wipe = interpolate(fr, [a, a + 8], [0, 100], {...clamp, easing: Easing.out(Easing.cubic)});
  const sweep = interpolate(fr, [a + 2, a + 14], [-30, 130], clamp);
  const out = interpolate(fr, [b, b + 5], [1, 0], clamp);
  return (
    <div style={{position: 'absolute', left: x, top: y, opacity: out, clipPath: `inset(0 ${100 - wipe}% 0 0 round 8px)`}}>
      <div style={{position: 'relative', background: C.plum, border: `1px solid ${C.gold}`, borderRadius: 8, padding: `${size * 0.22}px ${size * 0.55}px`,
        fontFamily: 'Q', fontWeight: 700, fontSize: size, color: 'white', overflow: 'hidden', boxShadow: '0 6px 20px rgba(0,0,0,0.35)'}}>
        {text}
        <div style={{position: 'absolute', top: 0, bottom: 0, left: `${sweep}%`, width: '22%', transform: 'skewX(-30deg)',
          background: 'linear-gradient(90deg, rgba(255,255,255,0), rgba(255,255,255,0.55), rgba(255,255,255,0))'}} />
      </div>
    </div>
  );
};

const Tags: React.FC = () => {
  const fr = useCurrentFrame();
  const end = f(tl.ov.halo[1]);
  const target = [400, 1230];
  return (
    <AbsoluteFill>
      {tl.ov.tags.map((tg: any, i: number) => {
        const a = f(tg.t);
        if (fr < a) return null;
        const p = interpolate(fr, [a, a + 8], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
        const out = interpolate(fr, [end - 6, end], [1, 0], clamp);
        const y = 520 + i * 92, x = 70;
        const lx = x + 360, ly = y + 30;
        const lp = interpolate(fr, [a + 4, a + 12], [0, 1], clamp);
        return (
          <React.Fragment key={i}>
            <svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0, opacity: out}}>
              <line x1={lx} y1={ly} x2={lx + (target[0] - lx) * lp} y2={ly + (target[1] - ly) * lp} stroke="white" strokeWidth={1.6} opacity={0.85} />
              {lp >= 1 && <circle cx={target[0]} cy={target[1]} r={6} fill="white" style={{filter: 'drop-shadow(0 0 6px #FF6FB5)'}} />}
            </svg>
            <div style={{position: 'absolute', left: x + (1 - p) * -260, top: y, opacity: p * out, filter: `blur(${(1 - p) * 8}px)`}}>
              <div style={{width: 360, padding: '10px 22px', fontFamily: 'Q', fontWeight: 700, fontSize: 38, color: 'white',
                background: `linear-gradient(90deg, ${C.rose} 0%, rgba(226,71,127,0.85) 60%, rgba(226,71,127,0) 100%)`,
                boxShadow: '0 0 18px rgba(255,111,181,0.55)', borderRadius: 4, textShadow: '0 1px 6px rgba(0,0,0,0.35)'}}>{tg.text}</div>
            </div>
            {/* gold sparkles */}
            {Array.from({length: 5}).map((_, j) => {
              const sp = interpolate(fr, [a, a + 36], [0, 1], clamp);
              if (sp >= 1) return null;
              return <div key={j} style={{position: 'absolute', left: x + 40 + random(`sx${i}${j}`) * 300, top: y + 40 - sp * (60 + random(`sy${i}${j}`) * 90),
                width: 6, height: 6, borderRadius: 3, background: C.goldL, opacity: (1 - sp) * 0.9, boxShadow: `0 0 10px ${C.gold}`}} />;
            })}
          </React.Fragment>
        );
      })}
    </AbsoluteFill>
  );
};

// ---------- transitions ----------
const Trans: React.FC<{tr: any}> = ({tr}) => {
  const fr = useCurrentFrame();
  const T = f(tr.t);
  const k = tr.k;
  if (k === 'cream') return fr >= T && fr < T + 2 ? <AbsoluteFill style={{background: C.cream}} /> : null;
  if (k === 'tint') {
    const o = interpolate(fr, [T, T + 3], [0.55, 0], clamp);
    return fr >= T && fr <= T + 3 ? <AbsoluteFill style={{background: C.rose, opacity: o, mixBlendMode: 'overlay'}} /> : null;
  }
  if (k === 'white') {
    if (fr < T - 2 || fr > T + 11) return null;
    const w = interpolate(fr, [T - 2, T, T + 2, T + 5], [0, 1, 1, 0], clamp);
    const fog = interpolate(fr, [T + 2, T + 4, T + 11], [0, 0.6, 0], clamp);
    return (
      <AbsoluteFill>
        <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 60%, ${C.lilac}, ${C.orchid} 70%)`, opacity: fog, filter: 'blur(30px)'}} />
        <AbsoluteFill style={{background: 'white', opacity: w}}>
          {Array.from({length: 14}).map((_, i) => <div key={i} style={{position: 'absolute', left: random(`dx${T}${i}`) * W, top: random(`dy${T}${i}`) * H,
            width: 2 + random(`ds${T}${i}`) * 5, height: 2 + random(`dz${T}${i}`) * 4, borderRadius: 3, background: '#777', opacity: 0.5}} />)}
        </AbsoluteFill>
      </AbsoluteFill>
    );
  }
  if (k === 'bokeh') {
    if (fr < T - 6 || fr > T + 6) return null;
    const b = interpolate(fr, [T - 6, T - 1, T + 2, T + 6], [0, 1, 0.6, 0], clamp);
    const w = interpolate(fr, [T - 2, T, T + 2, T + 6], [0, 1, 0.8, 0], clamp);
    return (
      <AbsoluteFill>
        <AbsoluteFill style={{opacity: b, mixBlendMode: 'screen'}}>
          {Array.from({length: 22}).map((_, i) => {
            const r = 60 + random(`br${T}${i}`) * 150;
            return <div key={i} style={{position: 'absolute', left: random(`bx${T}${i}`) * W - r, top: random(`by${T}${i}`) * H - r, width: 2 * r, height: 2 * r, borderRadius: '50%',
              background: `radial-gradient(circle, rgba(255,245,220,0.9), rgba(248,222,156,0.55) 55%, rgba(227,176,79,0) 72%)`,
              transform: `scale(${0.6 + 0.4 * b})`}} />;
          })}
        </AbsoluteFill>
        <AbsoluteFill style={{background: '#FFF8EC', opacity: w}} />
      </AbsoluteFill>
    );
  }
  if (k === 'flare') {
    if (fr < T - 10 || fr > T + 6) return null;
    const g = interpolate(fr, [T - 10, T], [0, 1], {...clamp, easing: Easing.in(Easing.quad)});
    const w = interpolate(fr, [T - 2, T, T + 1, T + 6], [0, 1, 1, 0], clamp);
    return (
      <AbsoluteFill>
        <div style={{position: 'absolute', right: -500 + 0, bottom: -500, width: 1000, height: 1000, borderRadius: '50%', transform: `scale(${0.3 + 2.8 * g})`, transformOrigin: '50% 50%',
          background: 'radial-gradient(circle, rgba(255,255,255,1), rgba(255,236,190,0.85) 30%, rgba(227,176,79,0.4) 55%, rgba(227,176,79,0) 70%)', mixBlendMode: 'screen'}} />
        <AbsoluteFill style={{background: 'white', opacity: w}} />
      </AbsoluteFill>
    );
  }
  if (k === 'burn') {
    if (fr < T - 4 || fr > T + 14) return null;
    const p = interpolate(fr, [T - 4, T + 14], [-0.6, 1.4], clamp);
    const o = interpolate(fr, [T - 4, T + 2, T + 14], [0, 1, 0], clamp);
    return <AbsoluteFill style={{mixBlendMode: 'screen', opacity: o,
      background: `linear-gradient(110deg, rgba(0,0,0,0) ${(p - 0.5) * 100}%, rgba(255,140,40,0.85) ${(p - 0.25) * 100}%, rgba(255,230,180,1) ${p * 100}%, rgba(226,71,127,0.75) ${(p + 0.2) * 100}%, rgba(0,0,0,0) ${(p + 0.45) * 100}%)`}} />;
  }
  return null;
};

// ---------- global finish ----------
const Finish: React.FC = () => {
  const fr = useCurrentFrame();
  const total = Math.ceil(tl.total * FPS);
  const fadeOut = interpolate(fr, [total - 7, total - 1], [0, 1], clamp);
  const fadeIn = interpolate(fr, [0, 4], [1, 0], clamp);
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 45%, rgba(26,16,12,0) 50%, rgba(26,16,12,0.55) 100%)`}} />
      <AbsoluteFill style={{opacity: 0.09, mixBlendMode: 'overlay'}}>
        <svg width={W} height={H}><filter id="g"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed={fr % 60} /></filter>
          <rect width={W} height={H} filter="url(#g)" /></svg>
      </AbsoluteFill>
      <AbsoluteFill style={{background: C.walnut, opacity: Math.max(fadeOut, fadeIn)}} />
    </AbsoluteFill>
  );
};

export const Reel: React.FC = () => {
  const depth = tl.stacks.filter((s: any) => s.style === 'depth');
  const needSubject = (s: any) => {
    const a = s.e_in, b = s.e_out;
    const hit = (x: number, y: number) => x < b && y > a;
    return !s.angle.startsWith('CW') && (depth.some((d: any) => hit(d.start, d.end)) || hit(tl.ov.halo[0], tl.ov.halo[1]));
  };
  return (
    <AbsoluteFill style={{background: C.walnut}}>
      <style>{fontCss}</style>
      {shots.map((s, i) => (
        <Sequence key={i} from={f(s.e_in)} durationInFrames={f(s.e_out) - f(s.e_in)}>
          <Plate s={s} layer="base" />
          {needSubject(s) && (
            <AbsoluteFill>
              <Sequence from={-f(s.e_in)} layout="none">
                <Halo />
                {depth.map((d: any, j: number) => <DepthTitle key={j} s={d} />)}
              </Sequence>
              <Plate s={s} layer="subject" />
            </AbsoluteFill>
          )}
        </Sequence>
      ))}
      {/* bottom gradient for captions */}
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(26,16,12,0) 62%, rgba(26,16,12,0.85) 100%)'}} />
      {tl.stacks.map((s: any, i: number) => <Stack key={i} s={s} />)}
      <NeonQ />
      <Pill text="Pushpa ji" start={tl.ov.name[0]} end={tl.ov.name[1]} x={60} y={170} size={40} />
      <Tags />
      {tl.trans.map((tr: any, i: number) => <Trans key={i} tr={tr} />)}
      <Finish />
    </AbsoluteFill>
  );
};
