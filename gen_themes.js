// gen_themes.js - rebuild theme blocks in static/index.html from real-world palettes
// and verify every text pair against WCAG AA (4.5:1, non-bold text).
// Usage:  node gen_themes.js            (verify + splice)
//         node gen_themes.js --check    (verify only, no write)
//         node gen_themes.js -v         (verbose pair report)
// All console output is ASCII (PS 5.1 console mangles CJK).
'use strict';
const fs = require('fs'), path = require('path');
const FILE = path.join(__dirname, 'static', 'index.html');
const CHECK = process.argv.includes('--check');
const VERBOSE = process.argv.includes('-v');
const MIN = 4.5;
const EMIN = 4.55;                               // engine margin: hex rounding must not drop below MIN

// ---------- color utils ----------
const hx = h => { h = h.replace('#', ''); return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)]; };
const h6 = c => '#' + c.map(v => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, '0')).join('');
const lum = c => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); };
const cr = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
const mix = (a, b, p) => a.map((v, i) => v + (b[i] - v) * p);
const DARK = hx('#0b0d10'), WHITE = hx('#ffffff');
const rgba = (c, a) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;

// ---------- palettes + strongly tinted surfaces ----------
// Accents/semantic colors from official palettes (Catppuccin Mocha/Macchiato/Frappe,
// Nord, Everforest, GitHub Primer Dark, Gruvbox, Dracula, Solarized).
// SURFACES (bg/panel/panel2/line) are deliberately pushed hard toward each theme's
// hue (hand-tinted, low luminance) so skins read as clearly COLORED, not gray.
// Dark-surface semantic colors are pre-baked light enough to pass 4.5:1 so the
// engine never gray-washes them. bg2 = full-page radial glow + header gradient.
const SPECS = {
  root: { label: 'MochaViolet', bg: '#131022', panel: '#1c1833', panel2: '#282045', line: '#3d3468', fg: '#e9e4ff', dim: '#aaa2d8', acc: '#89b4fa', acc2: '#cba6f7', btnFg: '#131022', ok: '#a6e3a1', warn: '#f9e2af', bad: '#f38ba8', h2a: '#ff8a3c', h2b: '#ff7089', codeBg: '#100d1d', glowA: 0.42 },
  deepblue: { label: 'NordNavy', bg: '#081228', panel: '#0c1b3a', panel2: '#122752', line: '#20406f', fg: '#dce8ff', dim: '#9db1d6', acc: '#88c0d0', acc2: '#5e81ac', btnFg: '#081228', ok: '#a3be8c', warn: '#ebcb8b', bad: '#ff8585', h2a: '#8fbcbb', h2b: '#88c0d0', glowA: 0.42 },
  inkgreen: { label: 'Forest', bg: '#0c1610', panel: '#11241a', panel2: '#183426', line: '#2a5038', fg: '#e0f2dd', dim: '#a6bfa8', acc: '#a7c080', acc2: '#7fbbb3', btnFg: '#0c1610', ok: '#83c092', warn: '#dbbc7f', bad: '#ef8a8e', h2a: '#a7c080', h2b: '#7fbbb3', glowA: 0.42 },
  lavender: { label: 'Violet', bg: '#151129', panel: '#1e1940', panel2: '#2b2360', line: '#433a85', fg: '#e8e2ff', dim: '#aea6dd', acc: '#b7bdf8', acc2: '#c6a0f6', btnFg: '#151129', ok: '#a6da95', warn: '#eed49f', bad: '#ed8796', h2a: '#b7bdf8', h2b: '#f5bde6', glowA: 0.42 },
  morandi: { label: 'DustyBlue', bg: '#1b1d2c', panel: '#252840', panel2: '#313454', line: '#474b7e', fg: '#d8dcf7', dim: '#aab0d8', acc: '#8caaee', acc2: '#ca9ee6', btnFg: '#1b1d2c', ok: '#a6d189', warn: '#e5c890', bad: '#f09390', h2a: '#8caaee', h2b: '#ca9ee6', glowA: 0.40 },
  mono: { label: 'Neutral', bg: '#0a0c10', panel: '#13171d', panel2: '#1d232c', line: '#2f3743', fg: '#f1f4f8', dim: '#a6aeb8', acc: '#f0f6fc', acc2: '#8b949e', btnFg: '#0a0c10', ok: '#3fb950', warn: '#d29922', bad: '#f85149', h2a: '#f0f6fc', h2b: '#a8b0ba', codeBg: '#07090c', glowA: 0.20 },
  gold: { label: 'GoldenBrown', bg: '#171004', panel: '#231a08', panel2: '#32250d', line: '#52401a', fg: '#f8e9c2', dim: '#c9b687', acc: '#fabd2f', acc2: '#fe8019', btnFg: '#171004', ok: '#b8bb26', warn: '#d79921', bad: '#ff7d68', h2a: '#fabd2f', h2b: '#fe8019', codeBg: '#120c03', glowA: 0.45 },
  wine: { label: 'WineRed', bg: '#190a0e', panel: '#250f16', panel2: '#35151f', line: '#5c2632', fg: '#ffe4e7', dim: '#d3a0a6', acc: '#ff5555', acc2: '#ff79c6', btnFg: '#190a0e', ok: '#50fa7b', warn: '#f1fa8c', bad: '#ff8585', h2a: '#ff6b6b', h2b: '#ff79c6', codeBg: '#140809', glowA: 0.42 },
  champagne: { label: 'GoldenCream', bg: '#f7f0d7', panel: '#fffbee', panel2: '#f2e9cd', line: '#dccca0', fg: '#3f3423', dim: '#665a40', acc: '#b08d57', acc2: '#d4b483', btnFg: '#2a2113', ok: '#42634a', warn: '#75601f', bad: '#9c4a3e', h2a: '#6f5b3a', h2b: '#7d5a2c', codeBg: '#fdfaf1', glowA: 0.40 }
};

// ---------- engine ----------
function build(key, sp) {
  const fixes = [];
  const S = {};
  for (const k in sp) S[k] = k === 'glowA' ? sp[k] : hx(sp[k]);
  const bg = S.bg, fg = S.fg;
  const lightSurface = lum(bg) >= 0.35;          // light theme -> darken toward fg, dark theme -> lighten toward white
  const anchor = lightSurface ? fg : WHITE;
  const okPass = (t, b) => cr(t, b) >= EMIN;

  const fix = (name, color, surfs) => {           // binary-search min anchor-mix until all surfaces pass
    if (surfs.every(s => okPass(color, s))) return color;
    let lo = 0, hi = 1, best = null;
    for (let i = 0; i < 24; i++) {
      const p = (lo + hi) / 2, c = mix(color, anchor, p);
      if (surfs.every(s => okPass(c, s))) { best = c; hi = p; } else lo = p;
    }
    if (!best) throw new Error(`${key}: cannot fix ${name}`);
    fixes.push(`${name} ${h6(color)}->${h6(best)}`);
    return best;
  };
  const pick = (cands, surfs) => {
    for (const c of cands) if (surfs.every(s => okPass(c, s))) return c;
    throw new Error(`${key}: no candidate passes`);
  };
  const surf = (make, p0) => {                    // derived bg: shrink mix (binary-search max p) until fg readable
    if (okPass(fg, make(p0))) return make(p0);
    let lo = 0, hi = p0, best = null;
    for (let i = 0; i < 24; i++) {
      const p = (lo + hi) / 2, c = make(p);
      if (okPass(fg, c)) { best = c; lo = p; } else hi = p;
    }
    if (!best) throw new Error(`${key}: fg fails on derived surface`);
    fixes.push(`surface p=${lo.toFixed(2)}`);
    return best;
  };

  // a) static + liveBg (small acc mix: keeps surface dark so red text stays vivid)
  S.codeBg = S.codeBg || bg;
  S.liveBg = surf(p => mix(bg, S.acc, p), 0.07);
  const TXT = [bg, S.panel, S.panel2, S.codeBg, S.liveBg];

  // b) semantic text colors first (later surfaces depend on them)
  S.ok = fix('ok', S.ok, TXT);
  S.warn = fix('warn', S.warn, TXT);
  S.bad = fix('bad', S.bad, TXT);

  // c) remaining derived surfaces (fg must stay >= 4.5 on each)
  S.bg2 = surf(p => mix(bg, S.acc, p), 0.22);     // page glow + header gradient wash
  S.partialBg = surf(p => mix(bg, S.acc, p), 0.30);
  S.exerBg = surf(p => mix(mix(S.panel, S.panel2, 0.5), S.acc, p), 0.08);
  S.msgMe = surf(p => mix(S.panel2, S.acc, p), 0.28);
  S.msgAiBg = surf(p => mix(S.panel2, S.ok, p), 0.16);
  S.achGotBg = surf(p => mix(S.panel2, S.ok, p), 0.16);
  S.toastBg = surf(p => mix(bg, S.ok, p), 0.20);
  S.hintBg = surf(p => mix(bg, S.acc, p), 0.15);
  S.wboxBg = surf(p => mix(bg, S.warn, p), 0.16);
  S.dayrowHover = surf(p => mix(S.panel2, fg, p), 0.07);
  S.starterBg = S.codeBg;

  // d) dim / h2 gradient text (brand text sits on header bg2 wash)
  const DIM_S = [bg, S.panel, S.panel2, S.codeBg, S.liveBg, S.dayrowHover, S.exerBg, S.bg2];
  S.dim = fix('dim', S.dim, DIM_S);
  S.h2a = fix('h2a', S.h2a, [S.panel, bg, S.bg2]);
  S.h2b = fix('h2b', S.h2b, [S.panel, bg, S.bg2]);

  // e) borders / tints
  S.exerLine = mix(S.line, S.acc, 0.35);
  S.hintLine = mix(S.line, S.acc, 0.50);
  S.msgAiLine = mix(S.line, S.ok, 0.50);
  S.wboxLine = mix(S.line, S.warn, 0.55);
  S.liveLine = mix(S.line, S.acc, 0.45);
  S.hwglow = S.warn;
  S.glow = rgba(S.acc, S.glowA);

  // f) accent-as-text (links etc) - only surfaces where links actually appear
  //    (NOT partialBg/starterBg: calendar cells and code blocks hold no links,
  //     including them would gray-wash accText through the 4.55 margin)
  const ACC_S = [bg, S.panel, S.panel2, S.codeBg, S.liveBg, S.dayrowHover, S.exerBg, S.msgMe, S.msgAiBg, S.hintBg, S.wboxBg, S.toastBg, S.achGotBg, S.bg2];
  S.accText = fix('accText', S.acc, ACC_S);

  // g) specialty text colors (chain ends at fg where fg is guaranteed on that surface)
  S.partialFg = fg;
  S.toastFg = fg;
  S.exerFg = pick([S.acc, mix(S.acc, fg, 0.5), fg], [S.exerBg]);
  S.starterFg = pick([S.ok, mix(S.ok, fg, 0.4), mix(S.ok, fg, 0.7), fg], [S.starterBg]);
  S.hintFg = pick([S.acc, mix(S.acc, fg, 0.5), fg], [S.hintBg]);
  S.wboxFg = pick([S.warn, mix(S.warn, fg, 0.5), fg], [S.wboxBg]);
  S.fullFg = pick([DARK, WHITE, fg], [S.ok]);
  S.outOk = pick([S.ok, mix(S.ok, fg, 0.4), fg], [S.codeBg]);
  S.outErr = pick([S.bad, mix(S.bad, fg, 0.4), fg], [S.codeBg]);

  // h) button labels
  const btnFgOk = [S.acc, S.acc2].every(s => okPass(S.btnFg, s));
  if (!btnFgOk) {
    const alt = [DARK, WHITE, fg].find(c => [S.acc, S.acc2].every(s => okPass(c, s)));
    if (!alt) throw new Error(`${key}: btn-fg unusable`);
    fixes.push(`btnFg ${h6(S.btnFg)}->${h6(alt)}`);
    S.btnFg = alt;
  }
  S.btnGoodFg = pick([DARK, WHITE, fg], [S.ok]);

  // round-trip through hex (emission precision) so reported ratios match what ships
  for (const k of Object.keys(S)) if (Array.isArray(S[k])) S[k] = hx(h6(S[k]));

  // i) pair report
  const pairs = [];
  const add = (name, t, b) => pairs.push({ name, t, b, r: cr(t, b) });
  const FG_S = [bg, S.panel, S.panel2, S.codeBg, S.liveBg, S.dayrowHover, S.exerBg, S.starterBg, S.msgMe, S.msgAiBg, S.achGotBg, S.partialBg, S.toastBg, S.hintBg, S.wboxBg, S.bg2];
  FG_S.forEach((s, i) => add(`fg@s${i}`, fg, s));
  DIM_S.forEach((s, i) => add(`dim@s${i}`, S.dim, s));
  ACC_S.forEach((s, i) => add(`accText@s${i}`, S.accText, s));
  TXT.forEach((s, i) => { add(`ok@s${i}`, S.ok, s); add(`warn@s${i}`, S.warn, s); add(`bad@s${i}`, S.bad, s); });
  add('h2a@panel', S.h2a, S.panel); add('h2b@panel', S.h2b, S.panel);
  add('btnFg@acc', S.btnFg, S.acc); add('btnFg@acc2', S.btnFg, S.acc2);
  add('btnGoodFg@ok', S.btnGoodFg, S.ok); add('fullFg@ok', S.fullFg, S.ok);
  add('partialFg@partialBg', S.partialFg, S.partialBg);
  add('exerFg@exerBg', S.exerFg, S.exerBg); add('starterFg@starterBg', S.starterFg, S.starterBg);
  add('hintFg@hintBg', S.hintFg, S.hintBg); add('wboxFg@wboxBg', S.wboxFg, S.wboxBg);
  add('outOk@codeBg', S.outOk, S.codeBg); add('outErr@codeBg', S.outErr, S.codeBg);
  return { key, S, pairs, fixes };
}

// ---------- CSS emission ----------
const ORDER = ['bg', 'bg2', 'panel', 'panel2', 'line', 'fg', 'dim', 'acc', 'acc2', 'btnFg', 'accText', 'ok', 'warn', 'bad', 'btnGoodFg', 'glow', 'h2a', 'h2b', 'codeBg', 'partialBg', 'partialFg', 'fullFg', 'exerBg', 'exerLine', 'exerFg', 'starterBg', 'starterFg', 'msgMe', 'msgAiBg', 'msgAiLine', 'achGotBg', 'toastBg', 'toastFg', 'hintBg', 'hintLine', 'hintFg', 'wboxBg', 'wboxLine', 'wboxFg', 'liveBg', 'liveLine', 'hwglow', 'dayrowHover', 'outOk', 'outErr'];
const CSSN = { btnFg: 'btn-fg', accText: 'acc-text', btnGoodFg: 'btn-good-fg', codeBg: 'code-bg', partialBg: 'partial-bg', partialFg: 'partial-fg', fullFg: 'full-fg', exerBg: 'exer-bg', exerLine: 'exer-line', exerFg: 'exer-fg', starterBg: 'starter-bg', starterFg: 'starter-fg', msgMe: 'msg-me', msgAiBg: 'msg-ai-bg', msgAiLine: 'msg-ai-line', achGotBg: 'ach-got-bg', toastBg: 'toast-bg', toastFg: 'toast-fg', hintBg: 'hint-bg', hintLine: 'hint-line', hintFg: 'hint-fg', wboxBg: 'wbox-bg', wboxLine: 'wbox-line', wboxFg: 'wbox-fg', liveBg: 'live-bg', liveLine: 'live-line', hwglow: 'hwglow', dayrowHover: 'dayrow-hover', outOk: 'out-ok', outErr: 'out-err' };

function emit(results) {
  const lines = ['/* ==== THEME-START (generated by gen_themes.js - do not edit by hand) ==== */'];
  for (const r of results) {
    const sel = r.key === 'root' ? ':root' : `html[data-theme="${r.key}"]`;
    lines.push(sel + '{');
    for (let i = 0; i < ORDER.length; i += 4) {
      const row = ORDER.slice(i, i + 4).map(n => { const v = r.S[n]; return `--${CSSN[n] || n}:${Array.isArray(v) ? h6(v) : v};`; }).join(' ');
      lines.push('  ' + row);
    }
    lines.push('}');
  }
  lines.push('/* ==== THEME-END ==== */');
  return lines.join('\n');
}

// ---------- main ----------
try {
  const results = Object.keys(SPECS).map(k => build(k, SPECS[k]));
  let failed = 0, total = 0, minAll = 99;
  for (const r of results) {
    const fails = r.pairs.filter(p => p.r < MIN);
    const min = Math.min(...r.pairs.map(p => p.r));
    minAll = Math.min(minAll, min);
    total += r.pairs.length;
    const pad = (r.key + ' (' + SPECS[r.key].label + ')').padEnd(24);
    if (fails.length === 0) console.log(`${pad} ${r.pairs.length} pairs OK   min=${min.toFixed(2)}  fixes=${r.fixes.length}`);
    else {
      failed += fails.length;
      console.log(`${pad} ${fails.length} FAIL of ${r.pairs.length}`);
      for (const f of fails) console.log(`    FAIL ${f.name} ${h6(f.t)} on ${h6(f.b)} = ${f.r.toFixed(2)}`);
    }
    for (const fx of r.fixes) console.log(`    fix: ${fx}`);
    if (VERBOSE) for (const p of r.pairs) console.log(`    ${p.name} ${h6(p.t)} on ${h6(p.b)} = ${p.r.toFixed(2)}`);
  }
  console.log(`TOTAL ${total} pairs, failing=${failed}, global min=${minAll.toFixed(2)}`);
  if (failed > 0) process.exit(1);

  const block = emit(results);
  if (CHECK) { console.log('check mode: no write'); process.exit(0); }

  let html = fs.readFileSync(FILE, 'utf8');
  const S_MARK = '/* ==== THEME-START', E_MARK = '/* ==== THEME-END ==== */';
  let out;
  if (html.includes(S_MARK)) {
    const i = html.indexOf(S_MARK), j = html.indexOf(E_MARK);
    if (j < i) throw new Error('bad markers');
    out = html.slice(0, i) + block + html.slice(j + E_MARK.length);
  } else {
    const re = /:root\{[\s\S]*?html\[data-theme="champagne"\]\{[\s\S]*?\n\}/;
    if (!re.test(html)) throw new Error('theme block not found');
    out = html.replace(re, block);
  }
  const n = (out.match(/--btn-good-fg:/g) || []).length;
  const m = (out.match(/--acc-text:/g) || []).length;
  if (n !== 9 || m !== 9) throw new Error(`emission incomplete (btn-good-fg=${n} acc-text=${m})`);
  if (/--[\w-]+:\d+,\d+,\d+/.test(out)) throw new Error('raw rgb leaked into emission');
  fs.writeFileSync(FILE, out);
  console.log(`spliced ${path.relative(process.cwd(), FILE)} (${html.length} -> ${out.length} bytes, 9 themes x ${ORDER.length} vars)`);
} catch (e) {
  console.error('ERROR: ' + e.message);
  process.exit(1);
}
