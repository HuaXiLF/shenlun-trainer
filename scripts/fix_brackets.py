# -*- coding: utf-8 -*-
"""修掉去敏后的残余方括号标签"""
from pathlib import Path

DST = Path(r"D:\xiazai\aiwork\workbuddy\2026-09-14-20-35-15\shenlun-trainer\corpus\22-24国考申论参考答案-多机构去敏版.md")
text = DST.read_text(encoding="utf-8", errors="replace")

fixes = [
    ("[金标尺答案]", "【JBC】"),
    ("[粉笔]", "【FB】"),
    ("[华图]", "【HT】"),
    ("[中公]", "【ZG】"),
    ("[站长]", "【ZZ】"),
]
log = []
for old, new in fixes:
    n = text.count(old)
    if n:
        text = text.replace(old, new)
        log.append(f"{old} -> {new}  x{n}")

DST.write_text(text, encoding="utf-8")

# 复查
resid = []
for kw in ["粉笔", "华图", "站长", "中公", "半月谈", "金标尺", "超格", "导氮", "李铁", "毕上", "四海飞扬"]:
    c = text.count(kw)
    if c:
        resid.append(f"{kw} x{c}")
Path(r"C:\Users\LCH\AppData\Local\Temp\fix_br.txt").write_text(
    "\n".join(log + ["---残留---"] + (resid or ["无"])), encoding="utf-8")
print("ok")
