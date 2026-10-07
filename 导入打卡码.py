"""把「今日任务」静态页生成的打卡码写回学习台真实记录（data/state.json）。

设计要点：
- **不需要重启服务器**：app.py 的 get_state() 每次请求都从磁盘重读，
  所以外部直接改 state.json 是安全的（正在跑的练习会话不会丢）。
- **铁律**：改之前一定先备份到 data/backups/state_<时间戳>.json。
- 打卡码格式（静态页生成，见 pages/build_pages.py）：
      SB1 D<学习日号> <日历日期> <当天任务条数> <若干位0/1> <作业位0/1>
  例：SB1 D11 2026-10-07 3 101 1
  注意 Dn 和日历日期无关（缺勤顺延），两个都验但互不要求相等。
"""
import datetime
import json
import os
import re
import shutil
import sys

try:                                   # PS 控制台是 GBK，✔ 会炸
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(ROOT, "data", "state.json")
BACKUP_DIR = os.path.join(ROOT, "data", "backups")
PAT = re.compile(r"^SB1\s+D(\d+)\s+(\d{4}-\d{2}-\d{2})\s+(\d+)\s+([01]+)\s+([01])$")


def die(msg):
    print("\n[失败] " + msg)
    sys.exit(1)


def main():
    code = ""
    if len(sys.argv) > 1:
        code = sys.argv[1]
    else:
        try:
            import win32clipboard as wc      # 一般没有，走下一招
        except Exception:
            wc = None
        if wc is not None:
            wc.OpenClipboard()
            code = wc.GetClipboardData() or ""
            wc.CloseClipboard()
        if not code.strip():
            print("用法一：把打卡码作为参数传进来")
            print("       导入打卡码.bat \"SB1 D11 2026-10-07 3 101 1\"")
            print("用法二：先复制打卡码，再运行本脚本（自动读剪贴板）")
            die("没有读到打卡码（剪贴板里没有 SB1 开头的内容）")
    code = code.strip()

    m = PAT.match(code)
    if not m:
        die("打卡码格式不对。应该是：SB1 D11 2026-10-07 3 101 1\n"
            "（SB1 + 学习日号 + 日期 + 任务条数 + 每条一位0/1 + 作业位）")
    day_no, date_str, n_task, bits, hw = (int(m.group(1)), m.group(2), int(m.group(3)),
                                          m.group(4), m.group(5))

    with open(os.path.join(ROOT, "plan.json"), encoding="utf-8") as fh:
        plan = json.load(fh)
    days = plan.get("days") or []
    if not 1 <= day_no <= len(days):
        die("学习日 D%d 不在计划内（计划共 %d 天）" % (day_no, len(days)))
    if len(bits) != n_task:
        die("打卡码里写了 %d 位任务，但 D%d 当天是 %d 条任务" % (len(bits), day_no, n_task))

    # 校验日期在计划区间内（不要求日期对应的天数 == Dn，因为 Dn 是顺延的）
    start = plan.get("meta", {}).get("start")
    if start:
        d0 = datetime.date.fromisoformat(start)
        d1 = d0 + datetime.timedelta(days=len(days) - 1)
        try:
            dd = datetime.date.fromisoformat(date_str)
        except ValueError:
            die("日期格式不对：%s" % date_str)
        if not (d0 <= dd <= d1):
            die("日期 %s 不在计划区间（%s ~ %s）内" % (date_str, d0, d1))

    # 1) 备份（铁律：先备份再改）
    os.makedirs(BACKUP_DIR, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = os.path.join(BACKUP_DIR, "state_%s_importcode.json" % stamp)
    if os.path.exists(STATE):
        shutil.copy2(STATE, bak)
        print("已备份 -> %s" % os.path.relpath(bak, ROOT))

    # 2) 读 → 改 → 原子写
    with open(STATE, encoding="utf-8") as fh:
        st = json.load(fh)
    before_checkins = len(st.get("checkins") or {})
    e = (st.setdefault("checkins", {})).setdefault(
        date_str, {"tasks": [], "hw": False, "hw_note": "", "updated": ""})
    e["tasks"] = [c == "1" for c in bits]
    e["hw"] = hw == "1"
    e["updated"] = datetime.datetime.now().isoformat(timespec="seconds")
    e["from"] = "static-page"

    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, STATE)

    done = sum(e["tasks"]) + (1 if e["hw"] else 0)
    print("\n[成功] D%d · %s · 完成 %d/%d" % (day_no, date_str, done, n_task + 1))
    print("       任务：%s" % " ".join(
        "%d.%s" % (i + 1, "OK" if v else "--") for i, v in enumerate(e["tasks"])))
    print("       作业：%s" % ("OK 已交" if e["hw"] else "未交"))
    print("       打卡日期数：%d -> %d" % (before_checkins, len(st["checkins"])))
    print("\n刷新学习台页面就能看到。不用重启。")


if __name__ == "__main__":
    main()