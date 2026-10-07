import json
import os
import re
import sys
import urllib.error
import urllib.request

cred = open(os.path.expanduser("~/.git-credentials"), encoding="utf-16-le",
            errors="replace").read()
tk = re.search(r"https://[^:]+:([^@]+)@github\.com", cred).group(1)
repo = "chenzhongyu331166-hub/study-buddy"
body = json.dumps({"source": {"branch": "main", "path": "/docs"},
                   "build_type": "legacy"}).encode()
req = urllib.request.Request(
    "https://api.github.com/repos/%s/pages" % repo, data=body, method="POST",
    headers={"Authorization": "Bearer " + tk,
             "Accept": "application/vnd.github+json",
             "X-GitHub-Api-Version": "2022-11-28",
             "User-Agent": "py", "Content-Type": "application/json"})
try:
    r = urllib.request.urlopen(req, timeout=25)
    d = json.load(r)
    print("OK", d.get("html_url"), d.get("status"))
except urllib.error.HTTPError as e:
    print("HTTP", e.code, e.read().decode("utf-8", "replace")[:600])