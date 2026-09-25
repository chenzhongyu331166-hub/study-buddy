# -*- coding: utf-8 -*-
"""学习台 StudyBuddy — 本地轻量学习服务
运行: venv\\Scripts\\python.exe app.py   ->  http://127.0.0.1:5000
"""
import json
import os
import re
import datetime
import threading
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
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default if default is not None else {}


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
    resp = {
        "date": now,
        "day": n,
        "plan_day": DAYS.get(n),
        "entry": entry,
        "stats": stats,
        "achievements": achievement_cards(st, stats),
        "earned_now": earned(st, stats),
    }
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

_AI_CACHE = {}


def ai_config():
    if _AI_CACHE:
        return _AI_CACHE
    raw = OPencode_CFG.read_text(encoding="utf-8-sig")
    raw = "\n".join(l for l in raw.splitlines() if not l.strip().startswith("//"))
    cfg = json.loads(raw)
    opts = cfg["provider"]["modelscope"]["options"]
    model_full = cfg.get("model", "")
    model = model_full.split("/", 1)[1] if model_full.startswith("modelscope/") else model_full
    base = opts["baseURL"].rstrip("/")
    key = opts["apiKey"]
    # 配置里的模型可能已下线，向 /models 校验并按偏好回退
    prefer = [model,
              "Qwen/Qwen3.5-397B-A17B", "Qwen/Qwen3.5-122B-A10B",
              "deepseek-ai/DeepSeek-V4-Pro", "MiniMax/MiniMax-M1-80k"]
    try:
        r = req.get(base + "/models", headers={"Authorization": "Bearer " + key}, timeout=20)
        ids = [m.get("id") for m in r.json().get("data", [])]
        if ids:
            model = next((c for c in prefer if c and c in ids), ids[0])
    except Exception:
        pass
    _AI_CACHE.update(base=base, key=key, model=model)
    return _AI_CACHE


def ai_chat(messages, system=None, temperature=0.7, max_tokens=2048, thinking=False):
    cfg = ai_config()
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.extend(messages)
    payload = {"model": cfg["model"], "messages": msgs,
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
    return jsonify({"reply": reply, "usage": usage, "model": ai_config()["model"]})


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
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
