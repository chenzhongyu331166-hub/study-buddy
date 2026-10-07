"""把「你实际学到第几天 + 哪些天已完成」发布到静态页（docs/progress.json）并推 GitHub。

为什么需要：公司电脑的浏览器是空的，看不到你家里的勾选记录，
纯靠静态页自己的 localStorage 会退回 D1。所以由这个脚本把真实进度发出去，
静态页读它从正确的那天开始。

不需要重启学习台：它自己 import app 都不碰，只读 data/state.json。
服务器开着或关着都能跑。

用法：双击 导回打卡码.bat 旁边那个「发布进度.bat」，或
      venv\\Scripts\\python.exe 发布进度.py
"""
import datetime
import json
import os
import subprocess
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(ROOT, "data", "state.json")
OUT = os.path.join(ROOT, "docs", "progress.json")


def die(m):
    print("\n[失败] " + m)
    sys.exit(1)


def main():
    with open(os.path.join(ROOT, "plan.json"), encoding="utf-8") as fh:
        plan = json.load(fh)
    days = plan.get("days") or []
    if not days:
        die("plan.json 里没有 days")
    if not os.path.exists(STATE):
        die("找不到 data/state.json，学习台还没跑过？")
    with open(STATE, encoding="utf-8") as fh:
        st = json.load(fh)
    ci = st.get("checkins") or {}

    done, cur = [], 1
    for i, d in enumerate(days, 1):
        e = ci.get(d.get("date") or "")
        t = (e or {}).get("tasks") or []
        # 全做完 = 作业交了 且 任务没有 False（任务条数会随计划/路线变，不写死）
        finished = bool((e or {}).get("hw")) and bool(t) and all(t)
        if finished:
            done.append(i)
        else:
            if cur == i or (i == 1):
                cur = i
            if finished is False and i == 1:
                cur = 1
    # cur = 第一个没做完的天；全做完了就停在最后一天
    first_undone = len(days)
    for i in range(1, len(days) + 1):
        if i not in done:
            first_undone = i
            break
    cur = first_undone

    payload = {
        "done": done,
        "current": cur,
        "total": len(days),
        "date": datetime.date.today().isoformat(),
        "updated": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    txt = json.dumps(payload, ensure_ascii=False, indent=1)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    old = None
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as fh:
            old = fh.read()
    if old == txt:
        print("进度没变（已经是最新的），没改动。current=D%d" % cur)
        return
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(txt)
    print("已写 docs/progress.json：学到 D%d，完成的天：%s"
          % (cur, ",".join("D%d" % x for x in done) or "（无）"))

    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    try:
        for cmd in (["git", "add", "docs/progress.json"],
                    ["git", "commit", "-m", "publish progress: current D%d" % cur],
                    ["git", "push", "origin", "HEAD"]):
            r = subprocess.run(cmd, cwd=ROOT, env=env, timeout=90,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if r.returncode != 0:
                if cmd[1] == "commit":
                    print("（没有需要提交的改动）")
                    return
                print("（%s 失败：可能 github 被掐。不影响本地，下次再跑一次即可）" % cmd[1])
                return
    except Exception as e:
        print("（推送失败 %s，不影响本地）" % e)
        return
    print("已推到 GitHub，静态页刷新后自动跟到 D%d" % cur)


if __name__ == "__main__":
    main()