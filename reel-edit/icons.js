const { chromium } = require('playwright');
const S = process.argv[2];
const tiles = [
  ['diya', '🪔', '#7a0f22', '#3d0410', '#c2185b'],
  ['gift', '🎁', '#ffd36b', '#d98e04', '#fff1c4'],
  ['moon', '🌙', '#6a1b6e', '#1e0b3a', '#c2185b'],
  ['coin', '🪙', '#ffe08a', '#c47a00', '#fff6d8'],
  ['pin',  '📍', '#ffffff', '#ffd8c2', '#ffffff'],
];
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 420, height: 420 }, deviceScaleFactor: 1 });
  for (const [name, emo, c1, c2, rim] of tiles) {
    await p.setContent(`<html><head><style>
      @font-face{font-family:E;src:url(file://${S}/fonts/Noto_Color_Emoji.ttf);}
      html,body{margin:0;background:transparent}
      .t{position:absolute;left:60px;top:50px;width:300px;height:300px;border-radius:84px;
        background:radial-gradient(120% 90% at 30% 15%, ${c1} 0%, ${c2} 75%);
        box-shadow: 0 26px 40px rgba(42,5,8,.45), 0 8px 14px rgba(42,5,8,.35),
          inset 0 6px 0 rgba(255,255,255,.55), inset 0 -10px 18px rgba(0,0,0,.35),
          inset 0 0 0 3px ${rim}55;}
      .g{position:absolute;inset:0;border-radius:84px;
        background:linear-gradient(170deg,rgba(255,255,255,.62) 0%,rgba(255,255,255,.18) 38%,rgba(255,255,255,0) 52%);}
      .s{position:absolute;left:34px;top:22px;width:110px;height:56px;border-radius:50%;
        background:radial-gradient(closest-side,rgba(255,255,255,.95),rgba(255,255,255,0));transform:rotate(-24deg)}
      .e{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
        font-family:E;font-size:178px;line-height:1;filter:drop-shadow(0 10px 8px rgba(0,0,0,.35));}
    </style></head><body><div class="t"><div class="e">${emo}</div><div class="g"></div><div class="s"></div></div></body></html>`);
    await p.waitForTimeout(300);
    await p.screenshot({ path: `${S}/work/sprites/icon_${name}.png`, omitBackground: true });
  }
  await b.close();
})();
