"""开关 GitHub Pages（study-buddy 仓的 /docs 目录）。

用法：
    venv\\Scripts\\python.exe pages\\enable_pages.py off    # 关掉公网（网址失效）
    venv\\Scripts\\python.exe pages\\enable_pages.py on     # 再开回来
    venv\\Scripts\\python.exe pages\\enable_pages.py status # 只看状态

代码全部留在仓库里，随时可以开回来；关掉只是停掉对外服务。
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

REPO = "chenzhongyu331166-hub/study-buddy"
API = "https://api.github.com/repos/%s/pages" % REPO


def token():
    raw = open(os.path.expanduser("~/.git-credentials"), encoding="utf-16-le",
               errors="replace").read()
    return re.search(r"https://[^:]+:([^@]+)@github\.com", raw).group(1)


def headers():
    return {"Authorization": "Bearer " + token(),
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "study-buddy-pages"}


def call(req):
    try:
        r = urllib.request.urlopen(req, timeout=25)
        return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"raw": body[:200]}


def main():
    action = (sys.argv[1] if len(sys.argv) > 1 else "status").lower()
    if action == "off":
        code, d = call(urllib.request.Request(API, headers=headers(), method="DELETE"))
        if code == 204:
            print("已关闭 GitHub Pages：那个网址现在打不开了。代码还在仓库里，"
                  "想开回来跑 on 就行。")
        elif code == 404:
            print("本来就没开。")
        else:
            print("HTTP", code, d)
        return
    if action == "on":
        body = json.dumps({"source": {"branch": "main", "path": "/docs"},
                           "build_type": "legacy"}).encode()
        h = headers()
        h["Content-Type"] = "application/json"
        code, d = call(urllib.request.Request(API, data=body, headers=h, method="POST"))
        if code in (201, 409):
            print("已开启：%s（第一次要等 1-3 分钟构建）" % d.get("html_url", ""))
        else:
            print("HTTP", code, d)
        return
    code, d = call(urllib.request.Request(API, headers=headers()))
    if code == 404:
        print("GitHub Pages：未开启")
    else:
        print("GitHub Pages：status=%s  url=%s" % (d.get("status"), d.get("html_url")))


if __name__ == "__main__":
    main()