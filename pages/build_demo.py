# -*- coding: utf-8 -*-
"""生成「完整界面在线体验版」docs/app.html。

做法：把真实的 static/index.html 原样复制，只在 <body> 后注入一段
demo-shim：拦截所有 /api/* 请求，用抓取的真实快照（pages/demo-snapshot.json）
当数据；写操作返回本地模拟结果；AI 走访客自己填的 OpenAI 兼容接口。

不修改 static/index.html 本身。改完界面重跑本脚本即可。
"""
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "static" / "index.html"
SNAP = ROOT / "pages" / "demo-snapshot.json"
TMP_CAPTURE = Path(os.environ.get(
    "STBUDDY_DEMO_CAPTURE",
    os.path.join(os.environ.get("TEMP", "."), "opencode", "demo-data.json")))
OUT = ROOT / "docs" / "app.html"


_SAMPLE_SUBS = {
    "2026-09-27": [
        {"day": 2, "t": "2026-09-27T20:12:00", "model": "示例模型",
         "code": 'radius = float(input("请输入半径："))\narea = 3.14159 * radius ** 2\nprint(f"面积约为 {area:.2f}")\n',
         "feedback": "1) 完成度：\n- 读取半径 ✅\n- 公式正确 ✅\n- 格式化输出 ✅\n\n2) 问题清单：\n- 建议：给常量起个名字，如 PI = 3.14159，避免魔法数字。\n\n3) 改法：\n- PI = 3.14159\n- area = PI * radius ** 2\n\n4) 得分：9/10\n\n5) 一句鼓励：公式与格式化都对了，再讲究一点常量命名就更好。"},
        {"day": 2, "t": "2026-09-27T20:40:00", "model": "示例模型",
         "code": 'for i in range(1, 6):\n    print(i, "的平方是", i * i)\n',
         "feedback": "1) 完成度：\n- 循环写法 ✅\n- 输出平方 ✅\n\n2) 问题清单：\n- 建议：用 f-string 让输出更整齐。\n\n3) 改法：\n- print(f\"{i} 的平方是 {i * i}\")\n\n4) 得分：8/10\n\n5) 一句鼓励：循环已经用得很顺了。"},
    ],
    "2026-09-29": [
        {"day": 4, "t": "2026-09-29T21:05:00", "model": "示例模型",
         "code": 'def c_to_f(c):\n    return c * 9 / 5 + 32\n\nprint(c_to_f(25))\n',
         "feedback": "1) 完成度：\n- 定义函数 ✅\n- 返回换算结果 ✅\n\n2) 问题清单：\n- 建议：加一句注释说明输入单位。\n\n3) 改法：\n- # 摄氏转华氏\n\n4) 得分：9/10\n\n5) 一句鼓励：函数封装思路清晰。"},
    ],
}


def _sanitize(data):
    """演示页脱敏：只保留结构与统计，去掉一切私密正文（聊天/作业代码/笔记）。"""
    data["chat"] = {"messages": [], "profile": ""}
    data["mysave"] = {"saves": {}}
    data["runfiles"] = {"dir": "", "files": []}
    data["submissions"] = {"subs": {k: [dict(x) for x in v] for k, v in _SAMPLE_SUBS.items()}}
    today = data.get("today")
    if isinstance(today, dict) and isinstance(today.get("entry"), dict):
        today["entry"]["hw_note"] = ""
    st = (data.get("state") or {}).get("state")
    if isinstance(st, dict):
        st["subs"] = {k: [] for k in (st.get("subs") or {})}
        ai = st.get("ai")
        if isinstance(ai, dict):
            ai["log"] = []
        ck = st.get("checkins")
        if isinstance(ck, dict):
            for v in ck.values():
                if isinstance(v, dict):
                    v["hw_note"] = ""
    return data


def load_snapshot():
    if TMP_CAPTURE.exists():
        data = json.load(open(TMP_CAPTURE, encoding="utf-8"))
        data = _sanitize(data)
        # 隐私：聊天记录不公开
        data["chat"] = {"messages": [], "profile": ""}
        # 精简作业批改：只留最近 3 天、每天最多 3 条
        subs = (data.get("submissions") or {}).get("subs") or {}
        keys = list(subs.keys())[-3:]
        data["submissions"] = {"subs": {k: subs[k][:3] for k in keys}}
        json.dump(data, open(SNAP, "w", encoding="utf-8"), ensure_ascii=False)
        print("snapshot refreshed from live server")
    data = json.load(open(SNAP, encoding="utf-8"))
    return data


SHIM = r"""<script>
(function(){
var DATA = __DATA__;
var LS = 'sb_demo_ai';
function cfg(){try{return JSON.parse(localStorage.getItem(LS)||'{}')}catch(e){return{}}}
var of = window.fetch.bind(window);
function resp(obj, ok){ ok=(ok===undefined?true:ok);
  return Promise.resolve({ok:ok,status:ok?200:400,
    json:function(){return Promise.resolve(obj)}, text:function(){return Promise.resolve(JSON.stringify(obj))}});}
function q(p){return p.split('?')[0];}
async function aiCall(body){
  var c=cfg();
  if(!c.base||!c.key||!c.model){
    return resp({reply:'（在线体验版未接入 AI）\n\n点左下角「⚙ AI 设置」，填入你自己的 OpenAI 兼容接口 base_url / key / 模型名，就能在这里真实提问。\n完全免费的做法：用魔搭社区(ModelScope)的免费额度。',model:'',usage:{}});
  }
  try{
    var msgs=(body.system?[{role:'system',content:body.system}]:[]).concat(body.messages||[]);
    var r=await of(c.base.replace(/\/+$/,'')+'/chat/completions',{method:'POST',
      headers:{'Authorization':'Bearer '+c.key,'Content-Type':'application/json'},
      body:JSON.stringify({model:c.model,messages:msgs,temperature:0.7,max_tokens:1024})});
    var j=await r.json();
    if(!r.ok)throw new Error((j.error&&j.error.message)||('HTTP '+r.status));
    var txt=(j.choices&&j.choices[0]&&j.choices[0].message&&j.choices[0].message.content)||'(空回复)';
    return resp({reply:txt,model:c.model,usage:j.usage||{}});
  }catch(err){
    return resp({reply:'调用失败：'+(err&&err.message||err)+'\n\n常见原因：该接口不允许浏览器跨域(CORS)。可换支持 CORS 的接口，或本地运行完整版。',model:c.model,usage:{}});
  }
}
window.fetch=function(input,init){
  var url=(typeof input==='string')?input:(input&&input.url)||'';
  var path=url.replace(/^https?:\/\/[^\/]+/,'');
  if(path.indexOf('/api/')!==0)return of(input,init);
  var method=((init&&init.method)||'GET').toUpperCase();
  var p=q(path), body={};
  try{if(init&&init.body)body=JSON.parse(init.body);}catch(e){}
  if(p==='/api/plan')return resp(DATA.plan);
  if(p==='/api/today')return resp(DATA.today);
  if(p==='/api/state')return resp(DATA.state);
  if(p==='/api/hw/submissions')return resp(DATA.submissions);
  if(p==='/api/resources')return resp(DATA.resources);
  if(p==='/api/models')return resp(DATA.models);
  if(p==='/api/runfiles')return resp(DATA.runfiles);
  if(p==='/api/work/config')return method==='POST'?resp({ok:true}):resp(DATA.work_config);
  if(p==='/api/chat')return resp(DATA.chat);
  if(p==='/api/mysave')return method==='POST'?resp({ok:true}):resp(DATA.mysave);
  if(p==='/api/digest')return method==='POST'?resp(DATA.digest):resp(DATA.digest);
  if(p==='/api/run'&&method==='POST')return resp({sid:'demo',warnings:[],new_achievements:[]});
  if(p.indexOf('/api/run/')===0){
    if(method==='POST')return resp({ok:true});
    return resp({chunks:[{t:'[在线体验版] 这里不会执行真实代码。\n完整版会把你的代码在本机真跑，输出与报错原样显示，还能边跑边喂输入。\n',s:'out'}],hints:[],running:false,exit:0,capped:false});
  }
  if(p==='/api/checkin'&&method==='POST'){
    var e=DATA.today.entry;
    if(typeof body.idx==='number'){e.tasks[body.idx]=!!body.done;}
    if('hw' in body){e.hw=!!body.hw;}
    if('hw_note' in body){e.hw_note=body.hw_note;}
    return resp({entry:e,stats:DATA.today.stats,new_achievements:[]});
  }
  if(p==='/api/checkin/import')return resp({day:DATA.today.day||1,date:DATA.today.date||'',done:'',new_achievements:[]});
  if(p==='/api/track')return resp({ok:true});
  if(p==='/api/model')return resp({current:body.model||''});
  if(p==='/api/chat/clear')return resp({ok:true});
  if(p==='/api/fetch-next')return resp({ok:true});
  if(p==='/api/work/files')return resp({files:[],skipped:[],dir:'',total:0});
  if(p==='/api/work/review')return resp({reply:'（在线体验版不调用真实 AI。\n本地运行时，这里会把整个项目文件对照当天作业要求逐条审阅——需求对照 / 结构问题 / 亮点 / 下一步，并给可照抄的修正片段。）',project:body.project||'',files:[],total:0,model:''});
  if(p==='/api/hw/submit')return resp({feedback:'（在线体验版不调用真实 AI。）\n\n本地运行时，这里会贴出 AI 老师对这份作业的逐条批改：完成度 / 问题清单 / 改法建议 / 得分，并存入批改记录。',new_achievements:[]});
  if(p==='/api/ai'&&method==='POST')return aiCall(body);
  return resp({ok:true});
};
function bar(){
  var b=document.createElement('button');
  b.textContent='⚙ AI 设置';
  b.style.cssText='position:fixed;left:14px;bottom:14px;z-index:99999;background:linear-gradient(90deg,#6a8cff,#b06cff);color:#0b1020;border:0;border-radius:9px;padding:9px 13px;font-weight:700;cursor:pointer;box-shadow:0 4px 16px rgba(0,0,0,.45);font-size:13px';
  b.onclick=function(){
    var c=cfg();
    var base=prompt('1/3 模型接口 base_url（OpenAI 兼容）\n例：https://api-inference.modelscope.cn/v1', c.base||'');
    if(base===null)return;
    var key=prompt('2/3 API Key', c.key||'');
    if(key===null)return;
    var model=prompt('3/3 模型名\n例：Qwen/Qwen3.5-397B-A17B', c.model||'');
    if(model===null)return;
    localStorage.setItem(LS,JSON.stringify({base:base.trim(),key:key.trim(),model:model.trim()}));
    alert('已保存。现在去「AI老师」页提问，会直连你填的接口。');
  };
  document.body.appendChild(b);
  var tip=document.createElement('div');
  tip.style.cssText='position:fixed;right:12px;bottom:14px;z-index:99999;background:rgba(20,24,36,.92);color:#98a0b3;border:1px solid #2b3040;border-radius:8px;padding:7px 11px;font-size:12px';
  tip.innerHTML='<a href="./index.html" style="color:#6a8cff;text-decoration:none">← 产品介绍</a> · 在线演示（数据为示例，改动只存本机）';
  document.body.appendChild(tip);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',bar);else bar();
})();
</script>
"""


def build():
    data = load_snapshot()
    html = SRC.read_text(encoding="utf-8")
    html = html.replace("<title>学伴 StudyBuddy · 学习台</title>",
                        "<title>学伴 StudyBuddy · 在线体验（完整界面）</title>")
    shim = SHIM.replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    html = html.replace("<body>", "<body>\n" + shim, 1)
    (ROOT / "docs").mkdir(exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    # 练习区用到 polyglot.json（走原生 fetch 直连同目录）
    poly = ROOT / "static" / "polyglot.json"
    if poly.exists():
        (ROOT / "docs" / "polyglot.json").write_text(poly.read_text(encoding="utf-8"), encoding="utf-8")
    print("wrote %s (%.1f KB)" % (OUT, len(html) / 1024))


if __name__ == "__main__":
    build()
