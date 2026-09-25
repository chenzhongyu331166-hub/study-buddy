# -*- coding: utf-8 -*-
"""学习台每日提醒 — 右下角常驻弹窗
未完成打勾关不掉；只留“5分钟后再来”；全部完成后变绿可关闭。
直接读写 data/state.json，不依赖服务是否在跑。
"""
import json
import os
import sys
import datetime
import subprocess
import webbrowser
from pathlib import Path

import tkinter as tk

ROOT = Path(__file__).resolve().parent
PLAN_PATH = ROOT / "plan.json"
STATE_PATH = ROOT / "data" / "state.json"
SITE = "http://127.0.0.1:5000"

BG = "#171a21"
FG = "#e6e9ef"
DIM = "#98a1b0"
OK = "#39c07a"
ACC = "#4f8cff"


def load_json(p, default):
    try:
        with open(p, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except FileNotFoundError:
        return default
    except Exception:
        try:
            os.replace(p, str(p) + ".corrupt")
        except Exception:
            pass
        return default


def save_json(p, obj):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def day_index(plan, date_str):
    try:
        d = datetime.date.fromisoformat(date_str)
        start = datetime.date.fromisoformat(plan["meta"]["start"])
    except Exception:
        return None
    n = (d - start).days + 1
    return n if 1 <= n <= plan["meta"]["total_days"] else None


class Reminder:
    def __init__(self):
        self.plan = load_json(PLAN_PATH, None)
        self.today = datetime.date.today().isoformat()
        self.n = day_index(self.plan, self.today) if self.plan else None
        self.pd = None
        if self.n:
            self.pd = next((d for d in self.plan["days"] if d["day"] == self.n), None)

        self.root = tk.Tk()
        self.root.title("学习台提醒")
        self.root.configure(bg=BG)
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)
        self.done_auto_close = False

        self.vars = []
        self.build()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.place_bottom_right()

    # ---------- UI ----------
    def build(self):
        r = self.root
        pad = {"padx": 14, "pady": 6}
        head = tk.Frame(r, bg=BG)
        head.pack(fill="x", **pad)
        title = f"D{self.n} {self.pd['title']}" if self.pd else "学习台"
        tk.Label(head, text=title, bg=BG, fg=FG, font=("Microsoft YaHei", 12, "bold"),
                 wraplength=330, justify="left").pack(anchor="w")
        stage = ""
        if self.pd:
            for s in self.plan["stages"]:
                lo, hi = (int(x) for x in s["range"][1:].split("-"))
                if lo <= self.n <= hi:
                    stage = f"{s['range']} 阶段{self.stage_no(s)} {s['name']}"
        tk.Label(head, text=f"{self.today} · {stage}", bg=BG, fg=DIM,
                 font=("Microsoft YaHei", 9)).pack(anchor="w")

        self.body = tk.Frame(r, bg=BG)
        self.body.pack(fill="both", expand=True, **pad)

        if not self.pd:
            tk.Label(self.body, text="今天不在84天计划内\n(休息日或已毕业)", bg=BG, fg=DIM,
                     font=("Microsoft YaHei", 10)).pack(pady=20)
            self.closable = True
        else:
            self.closable = False
            st = load_json(STATE_PATH, {"checkins": {}})
            entry = st.setdefault("checkins", {}).setdefault(
                self.today, {"tasks": [False] * 3, "hw": False, "hw_note": ""})
            self.entry = entry
            for i, task in enumerate(self.pd["tasks"]):
                self.add_check(f"任务{i+1}  {task}", bool(entry["tasks"][i]),
                               lambda i=i, v=None: self.toggle_task(i))
            hw_txt = f"作业  {self.pd['hw']['t']}"
            self.add_check(hw_txt, bool(entry.get("hw")), lambda: self.toggle_hw())

        btns = tk.Frame(r, bg=BG)
        btns.pack(fill="x", padx=14, pady=(0, 12))
        tk.Button(btns, text="5分钟后再来", bg="#2a2f3a", fg=FG, relief="flat",
                  command=self.snooze, font=("Microsoft YaHei", 9)).pack(side="left")
        tk.Button(btns, text="打开学习台", bg=ACC, fg="white", relief="flat",
                  command=self.open_site, font=("Microsoft YaHei", 9)).pack(side="left", padx=8)
        self.close_btn = tk.Button(btns, text="关闭", bg="#2a2f3a", fg=DIM, relief="flat",
                                   command=self.on_close, font=("Microsoft YaHei", 9))
        self.close_btn.pack(side="right")

        self.status = tk.Label(r, text="未完成打勾前关不掉哦", bg=BG, fg=DIM,
                               font=("Microsoft YaHei", 9), anchor="w")
        self.status.pack(fill="x", padx=14, pady=(0, 8))
        if self.pd:
            self.refresh_body_state()

    def stage_no(self, s):
        return s["stage"]

    def add_check(self, text, checked, cb):
        var = tk.BooleanVar(value=checked)
        self.vars.append((var, cb))
        row = tk.Frame(self.body, bg="#1e222b")
        row.pack(fill="x", pady=4)
        tk.Checkbutton(row, variable=var, command=cb, bg="#1e222b", fg=FG,
                       selectcolor="#0f1115", activebackground="#1e222b",
                       activeforeground=FG, anchor="w",
                       font=("Microsoft YaHei", 10)).pack(side="left", padx=8, pady=6)
        tk.Label(row, text=text, bg="#1e222b", fg=FG, font=("Microsoft YaHei", 9),
                 wraplength=290, justify="left", anchor="w").pack(side="left", padx=(0, 8),
                                                                  pady=6, fill="x")

    def all_done(self):
        if not self.pd:
            return True
        return all(self.entry["tasks"]) and self.entry.get("hw")

    def refresh_body_state(self):
        if self.all_done():
            self.closable = True
            self.status.config(text="今天全部完成，可以关掉啦！", fg=OK)
            self.close_btn.config(bg=OK, fg="#062")
            self.root.configure(bg="#14231b")
        else:
            self.closable = False
            left = 3 - sum(self.entry["tasks"])
            extra = "" if self.entry.get("hw") else "，还差作业"
            self.status.config(text=f"还差{left}个任务{extra}，打完勾才能关", fg="#e0a63c")
            self.close_btn.config(bg="#2a2f3a", fg=DIM)

    # ---------- 状态持久化 ----------
    def _save(self):
        save_json(STATE_PATH, load_json(STATE_PATH, {"checkins": {}}))

    def toggle_task(self, i):
        st = load_json(STATE_PATH, {"checkins": {}})
        e = st.setdefault("checkins", {}).setdefault(
            self.today, {"tasks": [False] * 3, "hw": False, "hw_note": ""})
        if len(e.setdefault("tasks", [False] * 3)) < 3:
            e["tasks"] = (e["tasks"] + [False] * 3)[:3]
        e["tasks"][i] = bool(self.vars[i][0].get())
        e["updated"] = datetime.datetime.now().isoformat(timespec="seconds")
        save_json(STATE_PATH, st)
        self.entry = e
        self.refresh_body_state()

    def toggle_hw(self):
        idx = 3 if self.pd else -1
        st = load_json(STATE_PATH, {"checkins": {}})
        e = st.setdefault("checkins", {}).setdefault(
            self.today, {"tasks": [False] * 3, "hw": False, "hw_note": ""})
        e["hw"] = bool(self.vars[idx][0].get())
        e["updated"] = datetime.datetime.now().isoformat(timespec="seconds")
        save_json(STATE_PATH, st)
        self.entry = e
        self.refresh_body_state()

    # ---------- 行为 ----------
    def place_bottom_right(self):
        self.root.update_idletasks()
        w = self.root.winfo_width() or 380
        h = self.root.winfo_height() or 340
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = sw - w - 24
        y = sh - h - 64
        self.root.geometry(f"+{max(x,0)}+{max(y,0)}")

    def on_close(self):
        if self.all_done():
            self.root.destroy()
        else:
            self.status.config(text="还没打完勾，关不掉的～(全完成才可关闭)", fg="#e05c5c")
            self.root.bell()

    def snooze(self):
        self.root.withdraw()
        self.root.after(300000, self.wake)

    def wake(self):
        try:
            self.root.deiconify()
            self.place_bottom_right()
        except Exception:
            pass

    def open_site(self):
        try:
            # 服务没起就顺手拉起来
            import socket
            s = socket.socket()
            s.settimeout(0.4)
            up = s.connect_ex(("127.0.0.1", 5000)) == 0
            s.close()
            if not up:
                subprocess.Popen(
                    [str(ROOT / "venv" / "Scripts" / "pythonw.exe"), str(ROOT / "app.py")],
                    cwd=str(ROOT), creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            webbrowser.open(SITE)
        except Exception:
            webbrowser.open(SITE)

    def run(self):
        self.root.mainloop()


def main():
    auto = "--auto" in sys.argv
    try:
        pop = Reminder()
        if auto:
            # 定时/开机自动弹：已完成或不在计划内就静默退出
            if pop.all_done():
                pop.root.destroy()
                return
        pop.run()
    except Exception as e:
        print("popup error:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
