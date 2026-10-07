"""生成「今日任务」静态页（GitHub Pages 免费托管，任何设备浏览器打开即用）。

产出 pages/index.html：
  - 内嵌全部计划日的任务/作业/知识点/资源链接（约 60KB，无外部依赖）
  - 勾选状态存浏览器 localStorage，并按日期自动切天
  - 一键生成「打卡码」，回家粘回学习台即可回写 state.json
  - 【问AI】在能连到家里学习台时直接调 /api/ask，否则提示回家/用手机问

只读本项目的 plan.json，不碰 data/。改完计划重跑一次即可。
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "plan.json"
OUT = ROOT / "pages" / "index.html"


def start_date():
    m = re.search(r"(\d{4}-\d{2}-\d{2})", json.dumps(
        json.load(open(PLAN, encoding="utf-8")).get("meta", {}), ensure_ascii=False))
    return m.group(1) if m else "2026-09-26"


def build():
    plan = json.load(open(PLAN, encoding="utf-8"))
    days = []
    for i, d in enumerate(plan.get("days", []), 1):
        hw = d.get("hw") or {}
        days.append({
            "n": i,
            "t": d.get("title") or "",
            "k": d.get("tasks") or [],
            "hw": {"t": hw.get("t", ""), "d": hw.get("d", ""), "e": hw.get("e", "")},
            "kp": d.get("kp") or [],
            "r": [{"title": x.get("title", ""), "url": x.get("url", "")}
                  for x in (d.get("resources") or [])],
            "prod": (d.get("product") or "") if isinstance(d.get("product"), str) else "",
        })
    payload = json.dumps(days, ensure_ascii=False, separators=(",", ":"))
    html = TEMPLATE.replace("/*__DATA__*/[]", payload) \
                   .replace("__START__", start_date()) \
                   .replace("__MAXDAY__", str(len(days)))
    OUT.write_text(html, encoding="utf-8")
    # GitHub Pages 只接受 / 或 /docs 作为发布目录，这里同步一份到 docs/
    docs = ROOT / "docs"
    docs.mkdir(exist_ok=True)
    (docs / "index.html").write_text(html, encoding="utf-8")
    nj = docs / ".nojekyll"
    if not nj.exists():
        nj.write_text("", encoding="utf-8")
    print("wrote %s + docs/index.html (%d days, %.1f KB)"
          % (OUT, len(days), len(html) / 1024))


TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>今日任务 · 学习台</title>
<style>
:root{--bg:#0f1117;--panel:#181b24;--line:#2b3040;--fg:#e8eaf0;--dim:#98a0b3;--acc:#6aa5e8;--ok:#4caf7d;--warn:#e0a44c}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.7 system-ui,"Microsoft YaHei",sans-serif;padding:14px}
.wrap{max-width:760px;margin:0 auto}
h1{font-size:20px;margin:6px 0 2px}
h2{font-size:16px;margin:18px 0 8px;color:var(--acc)}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin-bottom:12px}
.muted{color:var(--dim);font-size:13px}
.big{font-size:26px;font-weight:700}
.nav{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:10px}
button{background:var(--panel);color:var(--fg);border:1px solid var(--line);border-radius:8px;padding:8px 12px;font-size:14px;cursor:pointer}
button.p{background:var(--acc);color:#0b1220;border-color:var(--acc);font-weight:700}
button:active{transform:translateY(1px)}
.task{display:flex;gap:10px;align-items:flex-start;padding:10px 0;border-bottom:1px dashed var(--line)}
.task:last-child{border-bottom:0}
.tick{flex:0 0 26px;height:26px;border:2px solid var(--line);border-radius:7px;background:transparent;color:transparent;font-size:15px;line-height:1;cursor:pointer;margin-top:2px}
.tick.on{background:var(--ok);border-color:var(--ok);color:#04140b;font-weight:900}
.task.done .txt{color:var(--dim);text-decoration:line-through}
.txt{flex:1}
a{color:var(--acc)}
.pill{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:1px 9px;font-size:12px;color:var(--dim);margin:2px 4px 2px 0}
.kp{background:#131722;border:1px solid var(--line);border-radius:6px;padding:6px 8px;font-size:14px;margin-bottom:4px}
textarea{width:100%;min-height:70px;background:#131722;color:var(--fg);border:1px solid var(--line);border-radius:8px;padding:8px;font:14px/1.6 inherit}
pre{white-space:pre-wrap;word-break:break-word;background:#131722;border:1px solid var(--line);border-radius:8px;padding:10px;font:14px/1.6 inherit;max-height:50vh;overflow:auto}
.hint{background:#1b2430;border-left:3px solid var(--acc);padding:8px 10px;border-radius:0 8px 8px 0;font-size:13px}
.ok{color:var(--ok);font-weight:700}
</style></head><body><div class="wrap">
<h1>今日任务</h1>
<div class="muted" id="sub">加载中…</div>

<div class="nav" style="margin-top:10px">
  <button onclick="go(-1)">‹ 前一天</button>
  <button class="p" onclick="go(0)">今天</button>
  <button onclick="go(1)">后一天 ›</button>
  <span style="flex:1"></span>
  <button onclick="showAll()">全部天</button>
</div>
<div class="card" style="padding:10px 14px">
  <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
    <span class="muted">手动钉住学习日</span>
    <input id="pinBox" type="number" min="1" max="__MAXDAY__" style="width:80px;background:#131722;color:var(--fg);border:1px solid var(--line);border-radius:8px;padding:6px">
    <button onclick="pin(parseInt(document.getElementById('pinBox').value,10)||0)">设定</button>
    <button onclick="pin(0)">恢复自动</button>
  </div>
  <div class="muted" style="margin-top:6px" id="dayTag"></div>
  <div class="muted" style="margin-top:6px">Dn = 第一个还没做完的天（跟学习台一致：今天没做完就顺延到明天，不跳天）。空浏览器自动读学习台推上来的 progress.json 从正确那天开始；只读不对才用这里手动钉。</div>
</div>

<div id="box"></div>

<div class="card">
  <h2 style="margin-top:0">✅ 打卡 · 把完成情况带回家</h2>
  <div class="muted" style="margin-bottom:8px">在这台设备勾完，点下面按钮复制「打卡码」，微信发给自己。回家双击 <b>导入打卡码.bat</b>（在 D:\VibeBuddy\study-buddy 里）把它粘进去，学习台记录就更新了 —— 不用重启任何东西。</div>
  <button class="p" onclick="makeCode()">📋 生成打卡码并复制</button>
  <textarea id="code" placeholder="打卡码会出现在这里；复制它，回家用「导入打卡码.bat」写回学习台" readonly style="margin-top:8px"></textarea>
</div>

<div class="card">
  <h2 style="margin-top:0">🤖 问 AI</h2>
  <div class="hint" id="aiHint">正在探测能不能连上家里的学习台…</div>
  <textarea id="q" placeholder="例如：unittest 里的 assertEqual 到底怎么用？" style="margin-top:8px"></textarea>
  <div style="margin-top:8px;display:flex;gap:8px;flex-wrap:wrap">
    <button class="p" onclick="ask()">问</button>
    <button onclick="location.href='#'+cur()">刷新连接状态</button>
  </div>
  <pre id="ans" style="display:none"></pre>
</div>

<script>
var DAYS=/*__DATA__*/[];
var START="__START__";
var KEY="sb_tasks_v1";
var off=0, home=null;
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){
  return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function todayStr(){var d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');}
function idxOf(ds){return Math.round((new Date(ds+'T00:00:00')-new Date(START+'T00:00:00'))/864e5);}
/* 学习台用「缺勤自动顺延」，日历日期未必等于当天学的 Dn。
   所以支持 ?day=N 手动钉住学习日，并记住（学习台首页也有同一个 ?day= 入口）。 */
function pinned(){try{var v=localStorage.getItem('sb_pin_day');return v?parseInt(v,10):0;}catch(e){return 0;}}
function pin(n){
  if(n){localStorage.setItem('sb_pin_day',String(n));}
  else{localStorage.removeItem('sb_pin_day');}
  off=0;render();
}
/* 学习日 Dn 和日历日期无关 —— 跟学习台一样：
   Dn = 「第一个还没做完的天」。今天没做完，明天就还是这一天（顺延，不跳天）。
   全部做完了才停在最后一天。localStorage 里按 Dn 存，所以勾完自动前进。 */
function recAt(i){var s=load(),r=s['D'+(i+1)]||{};
  if(!Array.isArray(r.t))r.t=[];      // 第一次打开没有记录，必须兜住，否则 .filter/.slice 报错整页白屏
  if(!r.h)r.h=0;
  return r;}
function setRecAt(i,r){var s=load();s['D'+(i+1)]=r;save(s);}
function totalOf(d){return d.k.length+(d.hw.t?1:0);}
function doneAt(i){var d=DAYS[i];if(!d)return 0;var r=recAt(i);
  return r.t.filter(Boolean).length+(r.h?1:0);}
function fullAt(i){var d=DAYS[i];if(!d)return false;var n=totalOf(d);
  if(PROG&&PROG.done&&PROG.done.indexOf(i+1)>=0)return true;  /* 学习台说已完成的天 */
  return n>0&&doneAt(i)>=n;
}
function autoDay(){
  for(var i=0;i<DAYS.length;i++){if(!fullAt(i))return i;}
  return DAYS.length-1;
}
/* 公司电脑是空的，本地勾选记录没有。progress.json 是学习台自己的脚本
   把「你实际做到第几天」推上来的，空浏览器读他从正确那天开始。 */
var PROG=null;
function fetchProg(){
  fetch('progress.json?r='+Date.now(),{cache:'no-store'}).then(function(r){
    if(!r.ok)throw 0;return r.json();}).then(function(j){
    if(j&&j.current){PROG=j;render();}}).catch(function(){});
}
function base(){var p=pinned();
  if(p)return p-1;
  if(PROG&&PROG.current)return PROG.current-1;   /* 学习台真实进度优先 */
  return autoDay();
}
function dn(){var i=base()+off;return i<0?0:(i>DAYS.length-1?DAYS.length-1:i);}
function load(){try{return JSON.parse(localStorage.getItem(KEY)||'{}');}catch(e){return {};}}
function save(s){localStorage.setItem(KEY,JSON.stringify(s));}
function rec(){return recAt(dn());}
function setRec(r){setRecAt(dn(),r);}
function go(d){off=(d===0?0:off+d);render();}
function tick(i){var r=rec(),a=r.t.slice();if(a[i])a[i]=0;else a[i]=1;r.t=a;setRec(r);render();}
function tickHw(){var r=rec();r.h=r.h?0:1;setRec(r);render();}
function prog(r){var d=DAYS[dn()];if(!d)return '';
  return r.t.filter(Boolean).length+(r.h?1:0)+'/'+totalOf(d);}
function render(){
  var i=dn(), d=DAYS[i], box=document.getElementById('box');
  var sub=document.getElementById('sub');
  sub.textContent='学习日 D'+(i+1)+' · 今天 '+todayStr()+'（共'+DAYS.length+'天）'+
                  (off?' · 翻看 '+off+' 天':'');
  var t=document.getElementById('dayTag');
  if(t)t.textContent=pinned()?('已手动钉在 D'+pinned())
    :(PROG&&PROG.current?('学习台同步：正在学 D'+PROG.current+'（截至 '+esc(PROG.date)+'）')
      :('自动：学到 D'+(autoDay()+1)+'（没做完就顺延）'));
  if(!d){box.innerHTML='<div class="card">这一天不在计划内（计划共 '+DAYS.length+' 天，D1 起于 '+START+'）。</div>';return;}
  var r=rec(), h='';
  h+='<div class="card"><div class="big">D'+(i+1)+' '+esc(d.t)+'</div>';
  h+='<div class="muted" style="margin-top:4px">进度 '+prog(r)+'</div>';
  if(d.kp.length) h+='<div style="margin-top:10px">'+
    d.kp.map(function(k){return '<span class="pill">'+esc(k)+'</span>';}).join('')+'</div>';
  h+='</div>';
  h+='<div class="card"><h2 style="margin-top:0">任务</h2>';
  d.k.forEach(function(t,n){
    h+='<div class="task'+(r.t[n]?' done':'')+'"><button class="tick'+(r.t[n]?' on':'')+'" onclick="tick('+n+')">✓</button>'+
       '<div class="txt">'+esc(t)+'</div></div>';
  });
  if(d.hw.t){
    h+='<div class="task'+(r.h?' done':'')+'"><button class="tick'+(r.h?' on':'')+'" onclick="tickHw()">✓</button>'+
       '<div class="txt"><b>'+esc(d.hw.t)+'</b><br><span class="muted">'+esc(d.hw.d)+'</span>'+
       (d.hw.e?'<br><span class="muted">期望：'+esc(d.hw.e)+'</span>':'')+'</div></div>';
  }
  h+='</div>';
  if(d.r.length){
    h+='<div class="card"><h2 style="margin-top:0">今天要读的原文</h2>';
    d.r.forEach(function(x){h+='<div style="margin-bottom:6px">· <a href="'+esc(x.url)+'" target="_blank" rel="noopener">'+esc(x.title)+'</a></div>';});
    h+='<div class="muted" style="margin-top:6px">不想读原文也行——回家让学习台生成「今日教程汇总」，那里面 AI 已经按知识点讲过了。</div></div>';
  }
  if(d.prod) h+='<div class="card"><h2 style="margin-top:0">产品任务</h2><div>'+esc(d.prod)+'</div></div>';
  box.innerHTML=h;
  /* 打卡码：Dn + 今天的日历日期 + 位数。位数必须等于当天任务条数，
     没勾的补 0，否则导入端会拒收。Dn 与日历日期无关，两个都带上，导入端都验。 */
  var c=document.getElementById('code'), n=d.k.length, bits='';
  for(var q=0;q<n;q++){bits+=(r.t[q]?'1':'0');}
  c.value='SB1 D'+(i+1)+' '+todayStr()+' '+n+' '+bits+' '+(r.h?'1':'0');
}
function makeCode(){
  render();                                  // 先按当前勾选刷新打卡码
  var c=document.getElementById('code'); c.focus(); c.select();
  var ok=false;
  try{ ok=document.execCommand('copy'); }catch(e){}
  if(!ok&&navigator.clipboard){navigator.clipboard.writeText(c.value).then(
    function(){c.setSelectionRange(0,0);alert('打卡码已复制，微信发给自己即可');});return;}
  if(ok){c.setSelectionRange(0,0);alert('打卡码已复制，微信发给自己即可');}
  else{alert('请手动全选复制下面的打卡码');}
}
function showAll(){
  var h='<div class="card"><h2 style="margin-top:0">全部 '+DAYS.length+' 天</h2>';
  DAYS.forEach(function(d,i){
    var n=totalOf(d), c=doneAt(i), fin=(n>0&&c>=n);
    h+='<div class="task'+(fin?' done':'')+'"><button class="tick'+(fin?' on':'')+
       '" onclick="jump('+i+')">✓</button><div class="txt">D'+(i+1)+' '+esc(d.t)+
       '<br><span class="muted">'+c+'/'+n+'</span></div></div>';
  });
  h+='<button style="margin-top:10px" onclick="pin(0);render()">回到自动（跟着学习日走）</button></div>';
  document.getElementById('box').innerHTML=h;
}
function jump(i){pin(i+1);window.scrollTo(0,0);}
function ask(){
  var q=document.getElementById('q').value.trim(); if(!q)return;
  var a=document.getElementById('ans'); a.style.display='block'; a.textContent='…';
  fetch(home+'/api/chat/ask',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({message:q,date:todayStr()})})
   .then(function(r){return r.json();})
   .then(function(j){a.textContent=j.reply||j.error||JSON.stringify(j);})
   .catch(function(e){a.textContent='连不上家里的学习台（'+e+'）。\n可以微信发给自己，回家在学习台的 AI 老师页问；或者用手机打开学习台。';});
}
function probe(){
  var h=document.getElementById('aiHint');
  if(location.protocol==='file:'){h.textContent='这是本地文件，问AI用不了；把网址存到浏览器书签、联网时用公网地址打开即可。';return;}
  h.textContent='正在探测学习台…';
  home=location.origin;
  fetch('/api/today',{cache:'no-store'}).then(function(r){ return r.ok?r.json():Promise.reject(0);})
   .then(function(){h.innerHTML='<span class="ok">已连上学习台</span>，可以直接问。';})
   .catch(function(){home=null;h.innerHTML='没连上学习台（这台设备访问不到家里的电脑）。看任务、打勾、打卡码<b>照常可用</b>；问 AI 请微信发给自己，回家或用手机问。';});
}
render(); probe(); fetchProg();
</script></body></html>
"""

if __name__ == "__main__":
    build()