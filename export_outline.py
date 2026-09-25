# -*- coding: utf-8 -*-
"""导出《84天课程大纲.md》(供 ima 资料库 / 打印 / GitHub 阅读)"""
import json

PLAN_PATH = r"D:\VibeBuddy\study-buddy\plan.json"
OUT_PATH = r"D:\VibeBuddy\study-buddy\84天课程大纲.md"

plan = json.load(open(PLAN_PATH, encoding="utf-8"))
meta = plan["meta"]
lines = []
A = lines.append

A("# 84天Vibecoding学习大纲")
A("")
A(f"- 起止：{meta['start']} 起，共 {meta['total_days']} 天（D84 = 最后一天）")
A("- 主线：AI应用开发 | 副线：数据分析 | 备份：408考研基础")
A("- 节奏：每天3个任务 + 知识点 + 教材资源 + 1个动手编程作业（自己写代码）")
A(f"- 说明：{meta['note']}")
A("")
A("## 十二阶段一览")
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
import os
print("written", os.path.getsize(OUT_PATH), "bytes")
