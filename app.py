# -*- coding: utf-8 -*-
"""学习台 StudyBuddy — 本地轻量学习服务
运行: venv\\Scripts\\python.exe app.py   ->  http://127.0.0.1:5000
"""
import json
import os
import re
import codecs
import datetime
import threading
import time
import sys
import subprocess
import uuid
import traceback
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

ROOT = Path(__file__).resolve().parent
PLAN_PATH = ROOT / "plan.json"
STATE_PATH = ROOT / "data" / "state.json"
RES_DIR = ROOT / "resources"
OPencode_CFG = Path.home() / ".config" / "opencode" / "opencode.jsonc"

app = Flask(__name__, static_folder="static", static_url_path="")

_LOCK = threading.Lock()


# ---------- 基础工具 ----------
def load_json(path, default=None):
    d = default if default is not None else {}
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except FileNotFoundError:
        return d
    except Exception:
        # 文件损坏(如带BOM/写坏)：备份原文件再回落，避免下一次保存把数据覆盖没
        try:
            os.replace(path, str(path) + ".corrupt")
        except Exception:
            pass
        return d


def save_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


PLAN = load_json(PLAN_PATH)
assert PLAN, "plan.json 缺失，请先运行 build_plan.py"

DAYS = {d["day"]: d for d in PLAN["days"]}
STAGES = PLAN["stages"]
START = datetime.date.fromisoformat(PLAN["meta"]["start"])
TOTAL = PLAN["meta"]["total_days"]

# URL -> 出现过的所有天号(跨天重复资源标记用)
_URL_DAYS = {}
for _d in PLAN["days"]:
    for _r in _d.get("res", []):
        _URL_DAYS.setdefault(_r["u"], set()).add(_d["day"])


def day_index(date_str):
    """日期 -> 第几天(1..84)，不在范围内返回 None"""
    try:
        d = datetime.date.fromisoformat(date_str)
    except Exception:
        return None
    n = (d - START).days + 1
    return n if 1 <= n <= TOTAL else None


def get_state():
    return load_json(STATE_PATH, {"checkins": {}, "ai": {"count": 0, "log": []}, "fetch": {}})


def save_state(st):
    save_json(STATE_PATH, st)


def day_entry(st, date_str):
    return st["checkins"].setdefault(
        date_str, {"tasks": [False, False, False], "hw": False, "hw_note": "", "updated": ""}
    )


# ---------- 进度与成就 ----------
def compute_stats(st):
    total_tasks = TOTAL * 3
    done_tasks = 0
    perfect_task_days = 0
    full_days = 0
    hw_done = 0
    for date_str, e in st["checkins"].items():
        t = sum(1 for x in e.get("tasks", []) if x)
        done_tasks += t
        if t == 3:
            perfect_task_days += 1
        if e.get("hw"):
            hw_done += 1
        if t == 3 and e.get("hw"):
            full_days += 1

    # 连续天数(以任务全完成为准，允许今天未打卡)
    def _day_ok(d):
        e = st["checkins"].get(d.isoformat())
        return bool(e) and all(e.get("tasks", []))

    streak = 0
    d = datetime.date.today()
    if not _day_ok(d):
        d -= datetime.timedelta(days=1)
    while _day_ok(d):
        streak += 1
        d -= datetime.timedelta(days=1)

    max_day = 0
    for date_str in st["checkins"]:
        n = day_index(date_str)
        if n and any(st["checkins"][date_str].get("tasks", [])):
            max_day = max(max_day, n)

    # 各阶段完成度
    stage_pct = {}
    for s in STAGES:
        lo, hi = (int(x) for x in s["range"][1:].split("-"))
        pts, got = 0, 0
        for n in range(lo, hi + 1):
            e = st["checkins"].get(DAYS[n]["date"], {})
            pts += 3
            got += sum(1 for x in e.get("tasks", []) if x)
        stage_pct[s["stage"]] = round(got * 100 / pts) if pts else 0

    return {
        "done_tasks": done_tasks,
        "total_tasks": total_tasks,
        "percent": round(done_tasks * 100 / total_tasks),
        "perfect_task_days": perfect_task_days,
        "full_days": full_days,
        "hw_done": hw_done,
        "streak": streak,
        "max_day": max_day,
        "ai_calls": st.get("ai", {}).get("count", 0),
        "fetched_days": len(st.get("fetch", {})),
        "runs": st.get("run", {}).get("count", 0),
        "interactive": st.get("run", {}).get("interactive", 0),
        "subs": sum(len(v) for v in st.get("subs", {}).values()),
        "digests": len(st.get("digest", {})),
        "stage_pct": stage_pct,
    }


ACHIEVEMENTS = [
    {"id": "first_step", "name": "第一步", "desc": "完成第一个任务打卡", "cond": lambda s, st: s["done_tasks"] >= 1},
    {"id": "day1_clear", "name": "开学第一天", "desc": "D1 任务+作业全完成", "cond": lambda s, st: _day_full(st, 1)},
    {"id": "streak3", "name": "三日不辍", "desc": "连续3天完成全部任务", "cond": lambda s, st: s["streak"] >= 3},
    {"id": "streak7", "name": "周周不断", "desc": "连续7天完成全部任务", "cond": lambda s, st: s["streak"] >= 7},
    {"id": "streak21", "name": "习惯养成", "desc": "连续21天完成全部任务", "cond": lambda s, st: s["streak"] >= 21},
    {"id": "tasks50", "name": "五十而立", "desc": "累计完成50个任务", "cond": lambda s, st: s["done_tasks"] >= 50},
    {"id": "tasks200", "name": "两百公里", "desc": "累计完成200个任务", "cond": lambda s, st: s["done_tasks"] >= 200},
    {"id": "hw10", "name": "动手十次", "desc": "完成10次编程作业", "cond": lambda s, st: s["hw_done"] >= 10},
    {"id": "hw40", "name": "代码如流", "desc": "完成40次编程作业", "cond": lambda s, st: s["hw_done"] >= 40},
    {"id": "perfect10", "desc": "10天任务+作业全部完成", "name": "十全十美", "cond": lambda s, st: s["full_days"] >= 10},
    {"id": "half_way", "name": "行至半程", "desc": "学习进度过半(D42以后打卡)", "cond": lambda s, st: s["max_day"] >= 42},
    {"id": "ai_first", "name": "初次求教", "desc": "第一次使用AI老师", "cond": lambda s, st: s["ai_calls"] >= 1},
    {"id": "ai_partner", "name": "AI搭档", "desc": "与AI老师交流30次", "cond": lambda s, st: s["ai_calls"] >= 30},
    {"id": "scout", "name": "明日侦察兵", "desc": "首次抓取明天的学习资源", "cond": lambda s, st: s["fetched_days"] >= 1},
    {"id": "stage2", "name": "阶段通关", "desc": "第一个阶段(7天)任务全清", "cond": lambda s, st: s["stage_pct"].get(1) == 100},
    {"id": "half_stage", "name": "六阶段毕业", "desc": "前6个阶段全部100%", "cond": lambda s, st: all(s["stage_pct"].get(i) == 100 for i in range(1, 7))},
    {"id": "graduate", "name": "84天毕业", "desc": "完成D84毕业日", "cond": lambda s, st: _day_full(st, TOTAL)},
    {"id": "run_first", "name": "初次运行", "desc": "第一次点运行跑通代码", "cond": lambda s, st: s["runs"] >= 1},
    {"id": "run20", "name": "跑它二十遍", "desc": "累计运行代码20次", "cond": lambda s, st: s["runs"] >= 20},
    {"id": "run100", "name": "百次试炼", "desc": "累计运行代码100次", "cond": lambda s, st: s["runs"] >= 100},
    {"id": "chat_stdin", "name": "对话式输入", "desc": "运行中给程序喂过一次输入", "cond": lambda s, st: s["interactive"] >= 1},
    {"id": "sub_first", "name": "首次交卷", "desc": "第一次提交作业给AI老师批改", "cond": lambda s, st: s["subs"] >= 1},
    {"id": "sub5", "name": "五次打磨", "desc": "提交作业批改5次", "cond": lambda s, st: s["subs"] >= 5},
    {"id": "sub15", "name": "精雕细琢", "desc": "提交作业批改15次", "cond": lambda s, st: s["subs"] >= 15},
    {"id": "digest_first", "name": "汇总开张", "desc": "第一次生成AI教程汇总", "cond": lambda s, st: s["digests"] >= 1},
    {"id": "digest7", "name": "七日汇总", "desc": "生成AI教程汇总7天", "cond": lambda s, st: s["digests"] >= 7},
    {"id": "streak14", "name": "半月连击", "desc": "连续14天完成全部任务", "cond": lambda s, st: s["streak"] >= 14},
    {"id": "streak30", "name": "满月战神", "desc": "连续30天完成全部任务", "cond": lambda s, st: s["streak"] >= 30},
    {"id": "full7", "name": "七日全勤", "desc": "累计7天任务+作业全完成", "cond": lambda s, st: s["full_days"] >= 7},
    {"id": "full30", "name": "三十全勤", "desc": "累计30天任务+作业全完成", "cond": lambda s, st: s["full_days"] >= 30},
    {"id": "fetch5", "name": "资料仓库", "desc": "累计抓取5天学习资料", "cond": lambda s, st: s["fetched_days"] >= 5},
]


def _day_full(st, day_no):
    e = st["checkins"].get(DAYS[day_no]["date"], {})
    return all(e.get("tasks", [])) and e.get("hw")


def earned(st, stats):
    return [a["id"] for a in ACHIEVEMENTS if a["cond"](stats, st)]


def achievement_cards(st, stats):
    got = set(earned(st, stats))
    return [
        {"id": a["id"], "name": a["name"], "desc": a["desc"], "got": a["id"] in got}
        for a in ACHIEVEMENTS
    ]


# ---------- 页面与只读接口 ----------
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/plan")
def api_plan():
    return jsonify(PLAN)


@app.route("/api/state")
def api_state():
    st = get_state()
    stats = compute_stats(st)
    return jsonify({"state": st, "stats": stats, "achievements": achievement_cards(st, stats)})


@app.route("/api/today")
def api_today():
    st = get_state()
    now = datetime.date.today().isoformat()
    n = day_index(now)
    entry = day_entry(st, now)
    stats = compute_stats(st)
    plan_day = DAYS.get(n)
    resp = {
        "date": now,
        "day": n,
        "plan_day": plan_day,
        "entry": entry,
        "stats": stats,
        "achievements": achievement_cards(st, stats),
        "earned_now": earned(st, stats),
    }
    if plan_day:
        # 每条资源标出还在哪些天出现过(跨天重复 -> 可略读，看汇总即可)
        for i, r in enumerate(plan_day["res"]):
            plan_day["res"][i] = {**r,
                                  "dup_days": sorted(_URL_DAYS.get(r["u"], set()) - {n})}
        # 当天是否已生成教程汇总
        resp["digest_ready"] = _digest_path(now).exists()
    if n and n < TOTAL:
        resp["tomorrow"] = DAYS[n + 1]
        resp["tomorrow_fetched"] = now in st.get("fetch", {})
    save_state(st)  # 初始化今天的空条目
    return jsonify(resp)


# ---------- 打卡 ----------
@app.route("/api/checkin", methods=["POST"])
def api_checkin():
    body = request.get_json(force=True, silent=True) or {}
    date_str = body.get("date") or datetime.date.today().isoformat()
    if day_index(date_str) is None:
        return jsonify({"error": "日期不在84天计划内"}), 400
    st = get_state()
    before = set(earned(st, compute_stats(st)))
    with _LOCK:
        e = day_entry(st, date_str)
        if "idx" in body:
            idx = int(body["idx"])
            if not 0 <= idx < 3:
                return jsonify({"error": "idx须为0-2"}), 400
            e["tasks"][idx] = bool(body.get("done"))
        if "hw" in body:
            e["hw"] = bool(body.get("hw"))
        if "hw_note" in body:
            e["hw_note"] = str(body.get("hw_note"))[:2000]
        e["updated"] = datetime.datetime.now().isoformat(timespec="seconds")
        save_state(st)
    stats = compute_stats(st)
    after = set(earned(st, stats))
    return jsonify({
        "entry": st["checkins"][date_str],
        "stats": stats,
        "new_achievements": [
            {"id": a["id"], "name": a["name"], "desc": a["desc"]}
            for a in ACHIEVEMENTS if a["id"] in after - before
        ],
        "achievements": achievement_cards(st, stats),
    })


# ---------- AI 老师 (魔搭 OpenAI 兼容接口) ----------
import html as html_mod
import requests as req

_AI_CACHE = {}   # base, key, ids, cfg_model, ts —— key只在内存，绝不写入state/GitHub

AI_PREFER = ["Qwen/Qwen3.5-397B-A17B", "Qwen/Qwen3.5-122B-A10B",
             "deepseek-ai/DeepSeek-V4-Pro", "MiniMax/MiniMax-M1-80k"]


def ai_meta():
    """读opencode.jsonc并向魔搭拉可用模型列表(/models)，10分钟缓存。"""
    now = time.time()
    if _AI_CACHE and now - _AI_CACHE.get("ts", 0) < 600:
        return _AI_CACHE
    raw = OPencode_CFG.read_text(encoding="utf-8-sig")
    raw = "\n".join(l for l in raw.splitlines() if not l.strip().startswith("//"))
    cfg = json.loads(raw)
    opts = cfg["provider"]["modelscope"]["options"]
    model_full = cfg.get("model", "")
    cfg_model = model_full.split("/", 1)[1] if model_full.startswith("modelscope/") else model_full
    base = opts["baseURL"].rstrip("/")
    key = opts["apiKey"]
    ids = []
    try:
        r = req.get(base + "/models", headers={"Authorization": "Bearer " + key}, timeout=20)
        ids = [m.get("id") for m in r.json().get("data", []) if m.get("id")]
    except Exception:
        pass
    _AI_CACHE.update(base=base, key=key, ids=ids, cfg_model=cfg_model, ts=now)
    return _AI_CACHE


def current_model():
    """当前模型：用户下拉选过的 > 配置默认(在线时) > 偏好回退 > 列表第一个"""
    m = ai_meta()
    ids = m["ids"]
    saved = None
    try:
        with _LOCK:
            saved = (get_state().get("ai") or {}).get("model")
    except Exception:
        saved = None
    if saved and (not ids or saved in ids):
        return saved
    prefer = [m.get("cfg_model")] + AI_PREFER
    if ids:
        return next((c for c in prefer if c in ids), ids[0])
    return next((c for c in prefer if c), "Qwen/Qwen3.5-397B-A17B")


def ai_chat(messages, system=None, temperature=0.7, max_tokens=2048, thinking=False):
    cfg = ai_meta()
    model = current_model()
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.extend(messages)
    payload = {"model": model, "messages": msgs,
               "temperature": temperature, "max_tokens": max_tokens,
               "enable_thinking": bool(thinking)}
    r = req.post(cfg["base"] + "/chat/completions",
                 json=payload,
                 headers={"Authorization": "Bearer " + cfg["key"],
                          "Content-Type": "application/json"},
                 timeout=180)
    if r.status_code != 200:
        raise RuntimeError(f"AI接口 {r.status_code}: {r.text[:300]}")
    data = r.json()
    content = data["choices"][0]["message"]["content"]
    return content, data.get("usage", {})


@app.route("/api/ai", methods=["POST"])
def api_ai():
    body = request.get_json(force=True, silent=True) or {}
    messages = body.get("messages") or []
    if not isinstance(messages, list) or not messages:
        return jsonify({"error": "messages不能为空"}), 400
    for m in messages:
        if not isinstance(m, dict) or m.get("role") not in ("user", "assistant"):
            return jsonify({"error": "消息格式错误"}), 400
    try:
        reply, usage = ai_chat(
            messages,
            system=body.get("system"),
            temperature=float(body.get("temperature", 0.7)),
            max_tokens=int(body.get("max_tokens", 2048)),
            thinking=bool(body.get("thinking", False)),
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 502
    with _LOCK:
        st = get_state()
        ai = st.setdefault("ai", {"count": 0, "log": []})
        ai["count"] += 1
        first_user = next((m.get("content", "") for m in messages if m["role"] == "user"), "")
        ai["log"] = (ai.get("log") or [])[-49:] + [
            {"t": datetime.datetime.now().isoformat(timespec="seconds"),
             "q": first_user[:80]}
        ]
        save_state(st)
    return jsonify({"reply": reply, "usage": usage, "model": current_model()})


# ---------- 代码练习：会话式真实运行(可边跑边喂输入) ----------
RUN_DIR = ROOT / "data" / "run"
RUN_IDLE_KILL = 120      # 无任何输入输出的秒数上限
RUN_MAX_LIVE = 600       # 单会话最长存活秒数
RUN_BUF_CAP = 512 * 1024 # 输出缓冲上限(防死循环刷屏)
RUN_KEEP = 300           # 进程退出后再保留结果的秒数

_RUNS = {}
_RUN_LOCK = threading.Lock()

SITECUSTOMIZE = '''# study-buddy: 把 input() 的提示染成灰色(ANSI 90)，输出本身不受影响
import builtins as _b
import sys as _s
_orig_input = _b.input
def _gray_input(*_a, **_kw):
    if len(_a) > 1 or _kw:
        # 多参数：透传给原生 input，让真正的 TypeError 原样报出来
        return _orig_input(*_a, **_kw)
    prompt = _a[0] if _a else ''
    if prompt:
        try:
            _s.stdout.write('\\x1b[90m' + str(prompt) + '\\x1b[0m')
            _s.stdout.flush()
        except Exception:
            pass
        return _orig_input()
    return _orig_input()
_b.input = _gray_input
'''

HINT_RULES = [
    ("EOFError: EOF when reading a line",
     "程序还想再读一行输入，但已经没有了：①运行前把输入填满(每行一个) ②在下方输入行打字回车接着喂 ③点【结束输入】告诉程序没有更多输入"),
    ("input expected at most 1 argument",
     "input() 只接受一个提示字符串参数：写成 input('请输入：')，多传的参数会报 TypeError"),
    ("invalid literal for int()",
     "input() 拿到的是字符串：转数字用 int(输入)，转之前可先 .isdigit() 判断是不是纯数字"),
    ("could not convert string to float",
     "input() 拿到的是字符串：转小数用 float(输入)，输入非数字会报这个错"),
    ("can only concatenate str",
     "字符串不能直接和数字相加：先 int()/float() 转成数字再算"),
    ("SyntaxError: invalid syntax",
     "语法错误：看 traceback 里 ^^^^ 指向的位置，常见是漏了冒号/括号/引号，或中英文符号混用"),
    ("IndentationError", "缩进错误：同一层级的代码左边空格数要一致(推荐4个空格)，不能混用Tab和空格"),
    ("TabError", "缩进错误：Tab和空格混用了，全部改成4个空格"),
    ("is not defined", "变量不存在：检查拼写是否前后一致，或还没赋值就拿来用"),
    ("KeyError", "字典里没有这个键：先用 d.keys() 看看有哪些键"),
    ("list index out of range", "下标超出范围：列表下标从0开始，最后一个元素是 len(list)-1"),
    ("division by zero", "除数是0了：除之前先判断它不为0"),
    ("RecursionError", "递归没有出口：函数会无限调用自己，需要加停止条件"),
]


def _lint_input_calls(code):
    """运行前 lint：找 input() 的两类高频错误，返回中文警告(不拦截运行)"""
    warns = []
    i = 0
    while True:
        m = re.compile(r"\binput\s*\(").search(code, i)
        if not m:
            break
        # 从左括号后扫描到配对右括号，数顶层逗号(跳过字符串)
        j, depth, quote, esc, commas = m.end() - 1, 0, None, False, 0
        while j < len(code):
            c = code[j]
            if quote:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == quote:
                    quote = None
            elif c in "\"'":
                quote = c
            elif c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    break
            elif c == "," and depth == 1:
                commas += 1
            j += 1
        if commas >= 1:
            warns.append("input() 只接受一个提示字符串参数，多余的参数会报 TypeError：写成 input('请输入：')")
        i = j + 1
    # 整个 input(...) 被包成字符串字面量：如 x = "input(身高)"
    for m in re.finditer(r"(['\"])(.*?)(?<!\\)\1", code):
        inner = m.group(2).strip()
        if re.fullmatch(r"input\s*\(.*\)", inner, re.S):
            warns.append('检测到 input(...) 被写成了字符串(外面多套了一层引号)，它不会执行输入——去掉最外层引号')
            break
    seen, out = set(), []
    for w in warns:
        if w not in seen:
            seen.add(w)
            out.append(w)
    return out


def _hints_for(text):
    """运行后：按输出里的错误类型给中文贴士"""
    hints = []
    for key, tip in HINT_RULES:
        if key in text and tip not in hints:
            hints.append(tip)
    return hints[:4]


def _pump(stream, tag, sess, dec):
    try:
        while True:
            data = stream.read(4096)
            if not data:
                break
            text = dec.decode(data)
            if not text:
                continue
            with _RUN_LOCK:
                if sum(len(c[1]) for c in sess["chunks"]) > RUN_BUF_CAP:
                    if not sess.get("capped"):
                        sess["capped"] = True
                        sess["chunks"].append(("err", "\n[输出超过512KB，已停止收集——多半是死循环]\n"))
                    continue
                sess["chunks"].append((tag, text))
                sess["last_io"] = time.time()
    except Exception:
        pass
    finally:
        try:
            stream.close()
        except Exception:
            pass


def _watchdog():
    while True:
        time.sleep(1)
        now = time.time()
        with _RUN_LOCK:
            for sid in list(_RUNS):
                s = _RUNS[sid]
                p = s["proc"]
                rc = p.poll()
                if rc is not None and s["exit"] is None:
                    s["exit"] = rc
                    s["ended"] = time.time()
                if s["exit"] is None:
                    if now - s["last_io"] > RUN_IDLE_KILL:
                        s["chunks"].append(("err", f"\n[已等待{RUN_IDLE_KILL}秒无输入输出，强制结束——程序多半卡在 input() 等你输入]\n"))
                        s["idle_kill"] = True
                        try:
                            p.kill()
                        except Exception:
                            pass
                        s["exit"] = p.poll() if p.poll() is not None else -1
                        s["ended"] = time.time()
                    elif now - s["started"] > RUN_MAX_LIVE:
                        s["chunks"].append(("err", f"\n[运行超过{RUN_MAX_LIVE}秒，强制结束]\n"))
                        try:
                            p.kill()
                        except Exception:
                            pass
                        s["exit"] = p.poll() if p.poll() is not None else -1
                        s["ended"] = time.time()
                elif now - s["ended"] > RUN_KEEP:
                    _DROP.append(sid)
            for sid in _DROP:
                s = _RUNS.pop(sid, None)
                if s:
                    try:
                        s["file"].unlink()
                    except Exception:
                        pass
            _DROP.clear()


_DROP = []
threading.Thread(target=_watchdog, daemon=True).start()


def _ensure_session_lint(body):
    code = body.get("code") or ""
    stdin = body.get("stdin") or ""
    if not code.strip():
        return None, None, (json.dumps({"error": "代码是空的"}), 400)
    if len(code) > 20000:
        return None, None, (json.dumps({"error": "代码太长(上限2万字符)"}), 400)
    if len(stdin) > 10000:
        return None, None, (json.dumps({"error": "输入太长"}), 400)
    return code, stdin, None


@app.route("/api/run", methods=["POST"])
def api_run():
    """会话式真实运行：可预填输入，跑起来后还能在输入行继续喂(终端式)"""
    body = request.get_json(force=True, silent=True) or {}
    code, stdin, err = _ensure_session_lint(body)
    if err:
        return jsonify(json.loads(err[0])), err[1]
    warnings = _lint_input_calls(code)

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    # 清掉7天前的残留脚本
    for old in RUN_DIR.glob("s_*.py"):
        try:
            if time.time() - old.stat().st_mtime > 7 * 86400:
                old.unlink()
        except Exception:
            pass
    (RUN_DIR / "sitecustomize.py").write_text(SITECUSTOMIZE, encoding="utf-8")
    f = RUN_DIR / f"s_{os.getpid()}_{uuid.uuid4().hex[:8]}.py"
    f.write_text(code, encoding="utf-8")

    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1",
           "PYTHONPATH": str(RUN_DIR) + os.pathsep + os.environ.get("PYTHONPATH", "")}
    try:
        p = subprocess.Popen(
            [sys.executable, "-X", "utf8", str(f)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=str(RUN_DIR), env=env)
    except Exception as e:
        try:
            f.unlink()
        except Exception:
            pass
        return jsonify({"error": str(e)}), 500

    now = time.time()
    sess = {"proc": p, "file": f, "chunks": [], "exit": None,
            "started": now, "last_io": now, "ended": None, "capped": False}
    sid = uuid.uuid4().hex[:12]
    with _RUN_LOCK:
        # 超过4个活跃会话：杀最旧的
        live = sorted((s for s in _RUNS.values() if s["exit"] is None),
                      key=lambda s: s["started"])
        while len(live) >= 4:
            old = live.pop(0)
            try:
                old["proc"].kill()
            except Exception:
                pass
        _RUNS[sid] = sess

    # 预填输入：按行喂进去，但**不关stdin**，程序还能继续要
    if stdin:
        try:
            p.stdin.write(stdin.encode("utf-8"))
            if not stdin.endswith("\n"):
                p.stdin.write(b"\n")
            p.stdin.flush()
        except Exception:
            pass

    dec_out = codecs.getincrementaldecoder("utf-8")(errors="replace")
    dec_err = codecs.getincrementaldecoder("utf-8")(errors="replace")
    threading.Thread(target=_pump, args=(p.stdout, "out", sess, dec_out), daemon=True).start()
    threading.Thread(target=_pump, args=(p.stderr, "err", sess, dec_err), daemon=True).start()

    with _LOCK:
        st = get_state()
        before = set(earned(st, compute_stats(st)))
        run = st.setdefault("run", {"count": 0, "interactive": 0})
        run["count"] += 1
        save_state(st)
        after = set(earned(st, compute_stats(st)))
        stats = compute_stats(st)
    return jsonify({
        "sid": sid, "running": True, "warnings": warnings,
        "new_achievements": [
            {"id": a["id"], "name": a["name"], "desc": a["desc"]}
            for a in ACHIEVEMENTS if a["id"] in after - before
        ],
        "stats": stats,
    })


@app.route("/api/run/<sid>")
def api_run_poll(sid):
    with _RUN_LOCK:
        s = _RUNS.get(sid)
        if not s:
            return jsonify({"error": "会话不存在或已过期"}), 404
        chunks = list(s["chunks"])
        running = s["exit"] is None
        exit_code = s["exit"]
        capped = s["capped"]
    text = "".join(t for _, t in chunks)
    hints = _hints_for(text) if not running else []
    return jsonify({
        "chunks": [{"s": tag, "t": t} for tag, t in chunks],
        "running": running, "exit": exit_code, "capped": capped,
        "hints": hints,
    })


@app.route("/api/run/<sid>/input", methods=["POST"])
def api_run_input(sid):
    body = request.get_json(force=True, silent=True) or {}
    line = body.get("line", "")
    with _RUN_LOCK:
        s = _RUNS.get(sid)
        if not s:
            return jsonify({"error": "会话不存在或已过期"}), 404
        p = s["proc"]
        if s["exit"] is not None:
            return jsonify({"error": "程序已经结束了"}), 400
        try:
            p.stdin.write((line + "\n").encode("utf-8"))
            p.stdin.flush()
        except Exception:
            return jsonify({"error": "写不进去了(程序可能已关闭输入)"}), 400
        s["last_io"] = time.time()
    with _LOCK:
        st = get_state()
        run = st.setdefault("run", {"count": 0, "interactive": 0})
        run["interactive"] += 1
        save_state(st)
    return jsonify({"ok": True})


@app.route("/api/run/<sid>/eof", methods=["POST"])
def api_run_eof(sid):
    with _RUN_LOCK:
        s = _RUNS.get(sid)
        if not s:
            return jsonify({"error": "会话不存在或已过期"}), 404
        try:
            s["proc"].stdin.close()
        except Exception:
            pass
        s["last_io"] = time.time()
    return jsonify({"ok": True})


@app.route("/api/run/<sid>/kill", methods=["POST"])
def api_run_kill(sid):
    with _RUN_LOCK:
        s = _RUNS.get(sid)
        if not s:
            return jsonify({"error": "会话不存在或已过期"}), 404
        try:
            s["proc"].kill()
        except Exception:
            pass
        s["chunks"].append(("err", "\n[已手动停止]\n"))
        if s["exit"] is None:
            s["exit"] = s["proc"].poll()
            s["ended"] = time.time()
    return jsonify({"ok": True})


# ---------- 作业提交区：贴码直通AI老师深度批改 ----------
@app.route("/api/hw/submit", methods=["POST"])
def api_hw_submit():
    body = request.get_json(force=True, silent=True) or {}
    code = (body.get("code") or "").strip()
    if not code:
        return jsonify({"error": "还没有代码可提交"}), 400
    if len(code) > 8000:
        return jsonify({"error": "代码太长(上限8000字符)，先精简或分段提交"}), 400
    now = datetime.date.today()
    n = day_index(now.isoformat())
    pd = DAYS.get(n)
    if not pd:
        return jsonify({"error": "今天不在84天计划内，找不到要批改的作业"}), 400
    system = (
        f"你是学习台的AI老师，正在批改学生D{n}《{pd['title']}》的课后编程作业。"
        f"作业要求【{pd['hw']['t']}】：{pd['hw']['d']}（期望：{pd['hw']['e']}）。\n"
        "批改格式(严格按此结构，中文)：\n"
        "1) 完成度：对照作业要求逐条判断做到了没有(✅/❌)\n"
        "2) 问题清单：按严重程度列出每处错误/隐患，指出具体行或片段\n"
        "3) 改法：每处问题给出怎么改的思路(教学优先，引导自己改，不直接甩完整成品；"
        "但如果学生完全卡死，可以给出关键片段)\n"
        "4) 得分：X/10\n"
        "5) 一句鼓励\n"
        "原则：不编造教材内容；学生没问的别展开；简洁直接。"
    )
    try:
        reply, usage = ai_chat(
            [{"role": "user", "content": "我的作业代码：\n```python\n" + code + "\n```"}],
            system=system, temperature=0.4, max_tokens=3000,
            thinking=bool(body.get("thinking", True)))
    except Exception as e:
        return jsonify({"error": str(e)}), 502

    model = current_model()  # 内部会取锁，必须在 _LOCK 外面调
    with _LOCK:
        st = get_state()
        before = set(earned(st, compute_stats(st)))
        subs = st.setdefault("subs", {})
        day_list = subs.setdefault(now.isoformat(), [])
        day_list.append({
            "t": datetime.datetime.now().isoformat(timespec="seconds"),
            "day": n, "code": code, "feedback": reply,
            "model": model,
        })
        del day_list[:-10]  # 每天最多留10份
        save_state(st)
        after = set(earned(st, compute_stats(st)))
        stats = compute_stats(st)
    return jsonify({
        "feedback": reply, "usage": usage, "stats": stats,
        "new_achievements": [
            {"id": a["id"], "name": a["name"], "desc": a["desc"]}
            for a in ACHIEVEMENTS if a["id"] in after - before
        ],
        "achievements": achievement_cards(st, stats),
    })


@app.route("/api/hw/submissions")
def api_hw_submissions():
    st = get_state()
    return jsonify({"subs": st.get("subs", {})})


# ---------- AI教程汇总：读已抓取正文，按知识点分节+嵌练习题 ----------
DIGEST_DIR = ROOT / "data" / "digests"


def _extract_json(text):
    """从AI输出里抠出JSON对象(剥```json围栏/前后废话)"""
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z]*\s*", "", t)
        t = re.sub(r"\s*```$", "", t)
    start = t.find("{")
    if start < 0:
        raise ValueError("AI输出里没有JSON")
    depth, in_str, esc = 0, False, False
    for i in range(start, len(t)):
        c = t[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return json.loads(t[start:i + 1])
    raise ValueError("JSON没闭合")


def _digest_path(date_str):
    return DIGEST_DIR / f"digest_{date_str}.json"


@app.route("/api/digest", methods=["POST"])
def api_digest_generate():
    body = request.get_json(force=True, silent=True) or {}
    date_str = body.get("date") or datetime.date.today().isoformat()
    force = bool(body.get("force"))
    n = day_index(date_str)
    if n is None:
        return jsonify({"error": "日期不在84天计划内"}), 400
    cpath = _digest_path(date_str)
    if cpath.exists() and not force:
        return jsonify({"cached": True, **load_json(cpath)})
    md = RES_DIR / f"D{n}_{date_str}.md"
    if not md.exists():
        # 抓取存档文件名可能带不同日期，按天号兜底找
        cands = sorted(RES_DIR.glob(f"D{n}_*.md"))
        md = cands[-1] if cands else None
    if not md or not md.exists():
        return jsonify({"error": "今天还没有抓取正文，先去资源页点抓取，再来生成汇总"}), 400

    pd = DAYS[n]
    src = md.read_text(encoding="utf-8", errors="replace")[:14000]
    system = (
        "你是学习台的教程整理老师，把学生抓取的教材正文整理成「今日教程汇总」。\n"
        "输出必须是纯JSON(不要任何多余文字、不要markdown围栏)，结构：\n"
        '{"sections":[{"kp":"知识点名","summary":"2-4句通俗讲解(基于抓取正文，不许编造)",'
        '"points":["要点1","要点2","要点3"],"exercises":[{"q":"练习题题目","a":"参考答案",'
        '"starter":"#可直接载入练习区的起手代码(可空字符串)"}]}],'
        '"note":"一句话学习建议"}\n'
        "要求：sections 与学生当天知识点一一对应(按给定顺序)；"
        "每个 section 给 1-2 道练习题，题目要能用当天抓取正文里的知识解决，"
        "starter 必须是能直接放进编辑器运行的 Python 片段(没有合适题时给空串)；"
        "语言全中文；总长控制在1500字以内。"
    )
    user = (f"D{n}《{pd['title']}》\n当天知识点：{'、'.join(pd['kp'])}\n"
            f"作业：{pd['hw']['t']}——{pd['hw']['d']}\n\n"
            f"以下是抓取的教材正文：\n{src}")
    last_err = None
    for attempt, temp in enumerate((0.3, 0.2)):
        try:
            reply, _u = ai_chat([{"role": "user", "content": user}],
                                system=system, temperature=temp,
                                max_tokens=4000, thinking=True)
            data = _extract_json(reply)
            if not isinstance(data.get("sections"), list) or not data["sections"]:
                raise ValueError("sections为空")
            data["_meta"] = {"date": date_str, "day": n,
                             "generated": datetime.datetime.now().isoformat(timespec="seconds"),
                             "source_file": md.name}
            save_json(cpath, data)
            with _LOCK:
                st = get_state()
                before = set(earned(st, compute_stats(st)))
                st.setdefault("digest", {})[date_str] = True
                save_state(st)
                after = set(earned(st, compute_stats(st)))
                stats = compute_stats(st)
            return jsonify({
                "cached": False, **data, "stats": stats,
                "new_achievements": [
                    {"id": a["id"], "name": a["name"], "desc": a["desc"]}
                    for a in ACHIEVEMENTS if a["id"] in after - before
                ],
            })
        except Exception as e:
            last_err = e
            if attempt == 0:
                continue
            return jsonify({"error": f"生成失败：{last_err}"}), 502


@app.route("/api/digest")
def api_digest_get():
    date_str = request.args.get("date") or datetime.date.today().isoformat()
    cpath = _digest_path(date_str)
    if not cpath.exists():
        return jsonify({"cached": False, "sections": []})
    return jsonify({"cached": True, **load_json(cpath)})


@app.route("/api/models")
def api_models():
    """像chatbox一样：实时拉魔搭可用模型列表供前端下拉选择"""
    m = ai_meta()
    return jsonify({"models": m["ids"], "current": current_model(),
                    "cfg_default": m.get("cfg_model"), "online": bool(m["ids"])})


@app.route("/api/model", methods=["POST"])
def api_model():
    body = request.get_json(force=True, silent=True) or {}
    model = (body.get("model") or "").strip()
    if not model:
        return jsonify({"error": "缺少model"}), 400
    m = ai_meta()
    if m["ids"] and model not in m["ids"]:
        return jsonify({"error": "该模型不在可用列表", "models": m["ids"]}), 400
    with _LOCK:
        st = get_state()
        st.setdefault("ai", {})["model"] = model
        save_state(st)
    return jsonify({"current": model})


# ---------- 明天的资源：确认后抓取存档 ----------
def extract_text(html, limit=6000):
    html = re.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", html)
    html = re.sub(r"(?s)<!--.*?-->", " ", html)
    html = re.sub(r"(?i)<(br|/p|/div|/li|/h[1-6]|/tr)[^>]*>", "\n", html)
    text = re.sub(r"(?s)<[^>]+>", " ", html)
    text = html_mod.unescape(text)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text).strip()
    return text[:limit]


@app.route("/api/fetch-next", methods=["POST"])
def api_fetch_next():
    body = request.get_json(force=True, silent=True) or {}
    if body.get("date"):
        date_str = body["date"]
        n = day_index(date_str)
    else:
        n = day_index(datetime.date.today().isoformat()) + 1
        date_str = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
    if n is None or n > TOTAL:
        return jsonify({"error": "没有更晚的计划日了(已到D84)"}), 400
    plan_day = DAYS[n]
    RES_DIR.mkdir(parents=True, exist_ok=True)
    items = []
    lines = [f"# D{n} {plan_day['title']} 学习资料存档",
             f"- 计划日期: {plan_day['date']}",
             f"- 抓取时间: {datetime.datetime.now().isoformat(timespec='seconds')}",
             "> 本文由学习台自动抓取，供本地阅读核对；若与教材原文不符，以链接原文为准。\n"]
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0"}
    for i, r in enumerate(plan_day["res"], 1):
        url = r["u"]
        try:
            resp = req.get(url, headers=headers, timeout=20, allow_redirects=True)
            if resp.encoding in (None, "ISO-8859-1"):
                resp.encoding = resp.apparent_encoding or "utf-8"
            ok = resp.status_code == 200
            body_text = extract_text(resp.text) if ok else ""
            items.append({"title": r["t"], "url": url, "src": r["src"],
                          "status": resp.status_code, "chars": len(body_text)})
            lines.append(f"\n## {i}. {r['t']}\n- 来源: {r['src']}\n- 链接: {url}\n- 状态: HTTP {resp.status_code}\n")
            lines.append(body_text or "(抓取失败，请直接打开链接阅读)")
        except Exception as e:
            items.append({"title": r["t"], "url": url, "src": r["src"],
                          "status": 0, "chars": 0, "error": str(e)[:120]})
            lines.append(f"\n## {i}. {r['t']}\n- 链接: {url}\n- 抓取失败: {str(e)[:120]}\n(请直接打开链接阅读)")
    out = RES_DIR / f"D{n}_{date_str}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    with _LOCK:
        st = get_state()
        st.setdefault("fetch", {})[date_str] = {
            "day": n,
            "time": datetime.datetime.now().isoformat(timespec="seconds"),
            "ok": sum(1 for x in items if x["status"] == 200),
            "fail": sum(1 for x in items if x["status"] != 200),
        }
        save_state(st)
    return jsonify({"day": n, "file": out.name, "items": items})


@app.route("/api/resources")
def api_resources():
    RES_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(RES_DIR.glob("*.md"), reverse=True)
    return jsonify([
        {"name": f.name, "size": f.stat().st_size,
         "mtime": datetime.datetime.fromtimestamp(f.stat().st_mtime).isoformat(timespec="seconds")}
        for f in files
    ])


@app.errorhandler(404)
def _404(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "接口不存在"}), 404
    return send_from_directory(app.static_folder, "index.html")


@app.errorhandler(500)
def _500(e):
    traceback.print_exc()
    return jsonify({"error": "服务器内部错误"}), 500


if __name__ == "__main__":
    print("StudyBuddy -> http://127.0.0.1:5000")
    import time
    for attempt in range(6):
        try:
            app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
            break
        except OSError as e:
            # 端口被旧实例占着(如开机时序竞态)：等它退干净再试
            if attempt == 5:
                raise
            print(f"port 5000 busy ({e})，3秒后重试 {attempt + 1}/5")
            time.sleep(3)
