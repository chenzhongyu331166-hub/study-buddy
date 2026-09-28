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

// ---------- palettes (hex from official sources) ----------
// Catppuccin Mocha / Nord(dev) / Everforest Dark / Catppuccin Macchiato /
// Catppuccin Frappe / GitHub Primer Dark / Gruvbox Dark / Dracula / Solarized-warm light
const SPECS = {
  root: { label: 'default Mocha', bg: '#181825', panel: '#1e1e2e', panel2: '#313244', line: '#45475a', fg: '#cdd6f4', dim: '#a6adc8', acc: '#89b4fa', acc2: '#cba6f7', btnFg: '#11111b', ok: '#a6e3a1', warn: '#f9e2af', bad: '#f38ba8', h2a: '#ff8a3c', h2b: '#e8355a', codeBg: '#11111b', glowA: 0.38 },
  deepblue: { label: 'Nord', bg: '#2e3440', panel: '#353b49', panel2: '#3b4252', line: '#4c566a', fg: '#d8dee9', dim: '#9aa5b5', acc: '#88c0d0', acc2: '#81a1c1', btnFg: '#2e3440', ok: '#a3be8c', warn: '#ebcb8b', bad: '#bf616a', h2a: '#8fbcbb', h2b: '#88c0d0', glowA: 0.40 },
  inkgreen: { label: 'Everforest', bg: '#232a2e', panel: '#2d353b', panel2: '#343f44', line: '#475258', fg: '#d3c6aa', dim: '#a6b0a6', acc: '#a7c080', acc2: '#7fbbb3', btnFg: '#232a2e', ok: '#83c092', warn: '#dbbc7f', bad: '#ef8a8e', h2a: '#a7c080', h2b: '#7fbbb3', glowA: 0.40 },
  lavender: { label: 'Macchiato', bg: '#181926', panel: '#24273a', panel2: '#363a4f', line: '#494d64', fg: '#cad3f5', dim: '#a5adcb', acc: '#b7bdf8', acc2: '#c6a0f6', btnFg: '#181926', ok: '#a6da95', warn: '#eed49f', bad: '#ed8796', h2a: '#b7bdf8', h2b: '#f5bde6', glowA: 0.40 },
  morandi: { label: 'Frappe', bg: '#232634', panel: '#303446', panel2: '#414559', line: '#51576d', fg: '#c6d0f5', dim: '#a5adce', acc: '#8caaee', acc2: '#ca9ee6', btnFg: '#232634', ok: '#a6d189', warn: '#e5c890', bad: '#e78284', h2a: '#8caaee', h2b: '#ca9ee6', glowA: 0.38 },
  mono: { label: 'PrimerDark', bg: '#0d1117', panel: '#161b22', panel2: '#21262d', line: '#30363d', fg: '#e6edf3', dim: '#8b949e', acc: '#f0f6fc', acc2: '#8b949e', btnFg: '#0d1117', ok: '#3fb950', warn: '#d29922', bad: '#f85149', h2a: '#f0f6fc', h2b: '#8b949e', codeBg: '#010409', glowA: 0.22 },
  gold: { label: 'Gruvbox', bg: '#282828', panel: '#32302f', panel2: '#3c3836', line: '#504945', fg: '#ebdbb2', dim: '#a89984', acc: '#fabd2f', acc2: '#fe8019', btnFg: '#1d2021', ok: '#b8bb26', warn: '#d79921', bad: '#fb4934', h2a: '#fabd2f', h2b: '#fe8019', codeBg: '#1d2021', glowA: 0.40 },
  wine: { label: 'Dracula', bg: '#21222c', panel: '#282a36', panel2: '#343746', line: '#44475a', fg: '#f8f8f2', dim: '#6272a4', acc: '#ff5555', acc2: '#ff79c6', btnFg: '#0b0d10', ok: '#50fa7b', warn: '#f1fa8c', bad: '#ff5555', h2a: '#ff5555', h2b: '#ff79c6', codeBg: '#191a21', glowA: 0.40 },
  champagne: { label: 'SolarizedWarm', bg: '#f4f0d9', panel: '#fdf6e3', panel2: '#efebd4', line: '#ddd2b8', fg: '#3a332a', dim: '#8a7f6c', acc: '#b08d57', acc2: '#d4b483', btnFg: '#2a2113', ok: '#4a7350', warn: '#8a6d1f', bad: '#ab4f42', h2a: '#b08d57', h2b: '#a67c3d', codeBg: '#fdfbf6', glowA: 0.35 }
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

  // a) static + liveBg
  S.codeBg = S.codeBg || bg;
  S.liveBg = surf(p => mix(bg, S.acc, p), 0.12);
  const TXT = [bg, S.panel, S.panel2, S.codeBg, S.liveBg];

  // b) semantic text colors first (later surfaces depend on them)
  S.ok = fix('ok', S.ok, TXT);
  S.warn = fix('warn', S.warn, TXT);
  S.bad = fix('bad', S.bad, TXT);

  // c) remaining derived surfaces (fg must stay >= 4.5 on each)
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

  // d) dim / h2 gradient text
  const DIM_S = [bg, S.panel, S.panel2, S.codeBg, S.liveBg, S.dayrowHover, S.exerBg];
  S.dim = fix('dim', S.dim, DIM_S);
  S.h2a = fix('h2a', S.h2a, [S.panel, bg]);
  S.h2b = fix('h2b', S.h2b, [S.panel, bg]);

  // e) borders / tints
  S.exerLine = mix(S.line, S.acc, 0.35);
  S.hintLine = mix(S.line, S.acc, 0.50);
  S.msgAiLine = mix(S.line, S.ok, 0.50);
  S.wboxLine = mix(S.line, S.warn, 0.55);
  S.liveLine = mix(S.line, S.acc, 0.45);
  S.hwglow = S.warn;
  S.glow = rgba(S.acc, S.glowA);

  // f) accent-as-text (links etc) - must pass on every surface it can appear on
  const ACC_S = [bg, S.panel, S.panel2, S.codeBg, S.liveBg, S.dayrowHover, S.exerBg, S.msgMe, S.msgAiBg, S.hintBg, S.wboxBg, S.toastBg, S.achGotBg, S.partialBg, S.starterBg];
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
  const FG_S = [bg, S.panel, S.panel2, S.codeBg, S.liveBg, S.dayrowHover, S.exerBg, S.starterBg, S.msgMe, S.msgAiBg, S.achGotBg, S.partialBg, S.toastBg, S.hintBg, S.wboxBg];
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
const ORDER = ['bg', 'panel', 'panel2', 'line', 'fg', 'dim', 'acc', 'acc2', 'btnFg', 'accText', 'ok', 'warn', 'bad', 'btnGoodFg', 'glow', 'h2a', 'h2b', 'codeBg', 'partialBg', 'partialFg', 'fullFg', 'exerBg', 'exerLine', 'exerFg', 'starterBg', 'starterFg', 'msgMe', 'msgAiBg', 'msgAiLine', 'achGotBg', 'toastBg', 'toastFg', 'hintBg', 'hintLine', 'hintFg', 'wboxBg', 'wboxLine', 'wboxFg', 'liveBg', 'liveLine', 'hwglow', 'dayrowHover', 'outOk', 'outErr'];
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
