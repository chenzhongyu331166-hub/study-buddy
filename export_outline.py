# -*- coding: utf-8 -*-
"""导出《课程大纲.md》(供资料库 / 打印 / GitHub 阅读)。

从 plan.json 生成；路径全部相对脚本所在目录，换台电脑也能直接跑。
使用：python export_outline.py
"""
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
PLAN_PATH = os.path.join(ROOT, "plan.json")
OUT_PATH = os.path.join(ROOT, "课程大纲.md")

plan = json.load(open(PLAN_PATH, encoding="utf-8"))
meta = plan["meta"]
TOTAL = meta.get("total_days") or len(plan["days"])
lines = []
A = lines.append

A("# 学伴 StudyBuddy · 课程大纲")
A("")
A(f"- 计划周期：{meta['start']} 起，共 {TOTAL} 天（D{TOTAL} = 最后一天）")
A("- 节奏：每天若干任务 + 知识点 + 教材资源 + 1 个动手编程作业（自己写代码）")
A(f"- 说明：{meta['note']}")
A("")
A(f"## 阶段一览（共 {len(plan['stages'])} 个阶段）")
A("")
A("| 阶段 | 名称 | 天数 | 目标 |")
A("|---|---|---|---|")
for s in plan["stages"]:
    A(f"| {s['stage']} | {s['name']} | {s['range']} | {s['goal']} |")
A("")
for d in plan["days"]:
    A(f"## D{d['day']} {d['title']}（{d['date']}）")
    A("")
    A("**任务**")
    for i, t in enumerate(d["tasks"], 1):
        A(f"{i}. {t}")
    A("")
    A("**知识点**：" + " / ".join(d["kp"]))
    A("")
    A("**资源**（来源可查）：")
    for r in d["res"]:
        A(f"- [{r['t']}]({r['u']}) —— {r['src']}")
    A("")
    A(f"**作业《{d['hw']['t']}》**")
    A(f"- 要求：{d['hw']['d']}")
    A(f"- 验收：{d['hw']['e']}")
    A("")

open(OUT_PATH, "w", encoding="utf-8").write("\n".join(lines))
print("written", os.path.getsize(OUT_PATH), "bytes ->", OUT_PATH)
