# -*- coding: utf-8 -*-
"""准确性核验：比对原文件与去敏文件的内容一致性"""
import re
from pathlib import Path

SRC = Path(r"D:\study\考公\申论\小作文刷题\22-24国考申论参考答案（多机构文本版）.md")
DST = Path(r"D:\xiazai\aiwork\workbuddy\2026-09-14-20-35-15\shenlun-trainer\corpus\22-24国考申论参考答案-多机构去敏版.md")

src = SRC.read_text(encoding="utf-8", errors="replace")
dst = DST.read_text(encoding="utf-8", errors="replace")

log = []

# 1. 剥离所有【】标签后，正文应当一致（去敏不改正文）
def strip_tags(t):
    return re.sub(r"【[^】]{1,30}】", "", t)

# 去掉新加的免责声明头（前 30 行左右）
dst_body = dst.split("## 2022年国家公考《申论》题（副省级）", 1)
src_body = src.split("## 2022年国家公考《申论》题（副省级）", 1)

s = strip_tags(src_body[1]) if len(src_body) > 1 else ""
d = strip_tags(dst_body[1]) if len(dst_body) > 1 else ""

# 规范化空白后比较
def norm(t):
    return re.sub(r"\s+", "", t)

sn, dn = norm(s), norm(d)
log.append(f"原文件正文长度(去空白): {len(sn)}")
log.append(f"去敏版正文长度(去空白): {len(dn)}")
log.append(f"正文完全一致: {sn == dn}")

if sn != dn:
    # 找第一处差异
    for i, (a, b) in enumerate(zip(sn, dn)):
        if a != b:
            log.append(f"首处差异 @ {i}")
            log.append(f"  原文: ...{sn[max(0,i-40):i+40]}...")
            log.append(f"  新文: ...{dn[max(0,i-40):i+40]}...")
            break
    log.append(f"长度差: {len(dn) - len(sn)}")

# 2. 题目数量核验
log.append("")
log.append("=== 题目/答案块统计 ===")
src_q = re.findall(r"【(\d)】", src)
dst_q = re.findall(r"【(\d)】", dst)
log.append(f"原文件 题号标签数: {len(src_q)}")
log.append(f"去敏版 题号标签数: {len(dst_q)}")

# 3. 来源标签总数
src_tags = re.findall(r"【([^】]{1,30})】", src)
dst_tags = re.findall(r"【([^】]{1,30})】", dst)
log.append(f"原文件 标签总数: {len(src_tags)}")
log.append(f"去敏版 标签总数: {len(dst_tags)}")

# 4. 套卷/章节数
src_sec = re.findall(r"^## .+$", src, re.M)
dst_sec = re.findall(r"^## .+$", dst, re.M)
log.append(f"原文件 套卷章节数: {len(src_sec)}")
log.append(f"去敏版 套卷章节数: {len(dst_sec)}")
log.append("原文件章节:")
for x in src_sec:
    log.append(f"  {x}")
log.append("去敏版章节:")
for x in dst_sec:
    log.append(f"  {x}")

Path(r"C:\Users\LCH\AppData\Local\Temp\accuracy.txt").write_text("\n".join(log), encoding="utf-8")
print("ok")
