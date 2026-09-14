# -*- coding: utf-8 -*-
"""扫描去敏后文件里是否还有机构名/人名残留"""
import re
from pathlib import Path
from collections import Counter

DST = Path(r"D:\xiazai\aiwork\workbuddy\2026-09-14-20-35-15\shenlun-trainer\corpus\22-24国考申论参考答案-多机构去敏版.md")
raw = DST.read_bytes()
text = raw.decode("utf-8", errors="replace")

KEYWORDS = [
    "粉笔", "华图", "站长", "中公", "半月谈", "超格", "导氮", "金标尺",
    "李铁", "毕上", "四海飞扬", "四海", "袁东", "单淑玲", "刘大师",
    "宋复法", "杨柳岸", "小马哥", "江牧云", "江牡云", "樊政", "程诺",
    "相丽君", "林宇", "白鹭", "黑魔仙", "千寻", "唐棣", "何飞羽",
    "贺冲", "钟君", "帅神俊", "一眉巫师", "坨坨", "永岸", "成公", "逸学",
]

report = []
total = 0
for kw in KEYWORDS:
    n = text.count(kw)
    if n:
        total += n
        # 找上下文
        ctxs = []
        for m in re.finditer(re.escape(kw), text):
            s = max(0, m.start() - 30)
            e = min(len(text), m.end() + 30)
            ctxs.append(text[s:e].replace("\n", "\\n"))
            if len(ctxs) >= 3:
                break
        report.append(f"### {kw}  x{n}")
        for c in ctxs:
            report.append(f"    ...{c}...")

out = []
out.append(f"残留关键词种类: {len(report) and sum(1 for r in report if r.startswith('###'))}")
out.append(f"残留总次数: {total}")
out.append("")
out.extend(report)
Path(r"C:\Users\LCH\AppData\Local\Temp\residual.txt").write_text("\n".join(out), encoding="utf-8")
print("done")
