# -*- coding: utf-8 -*-
"""
准确性核验：比对「去敏前的原文件」与「去敏后的文件」内容是否一致。

核验思路
--------
去敏只应替换来源标签，**不应改动答案正文**。因此：
  1. 把两边的【标签】都剥掉，剩余正文（去空白后）应逐字相同
  2. 题号标签数、来源标签总数、套卷章节数应保持可解释的关系

用法
----
    # --src 指向【去敏前】的原文件（不在本仓库中，需自备）
    python verify_accuracy.py --src "22-24国考申论参考答案（多机构文本版）.md"

    python verify_accuracy.py --src "原文件.md" --dst corpus/xxx.md --out build/acc.txt

退出码：0 = 正文一致；1 = 有差异（需人工核查）
"""
import argparse
import re
import sys
from pathlib import Path

# 仓库根 = 本脚本所在目录的上一级（脚本位于 <repo>/scripts/）
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DST = REPO_ROOT / "corpus" / "22-24国考申论参考答案-多机构去敏版.md"

# 去敏版在文件头部额外加了说明块，比对正文时从这里切开
SPLIT_MARKER = "## 2022年国家公考《申论》题（副省级）"

TAG_RE = re.compile(r"【([^】]{1,30})】")
NUM_TAG_RE = re.compile(r"【(\d)】")
SEC_RE = re.compile(r"^## .+$", re.M)


def strip_tags(t: str) -> str:
    return TAG_RE.sub("", t)


def norm(t: str) -> str:
    return re.sub(r"\s+", "", t)


def main() -> int:
    ap = argparse.ArgumentParser(description="去敏准确性核验")
    ap.add_argument("--src", required=True, help="去敏前的原文件路径（必填）")
    ap.add_argument("--dst", default=str(DEFAULT_DST),
                    help=f"去敏后的文件（默认 {DEFAULT_DST.name}）")
    ap.add_argument("--out", default=None, help="报告输出路径（可选）")
    args = ap.parse_args()

    SRC = Path(args.src).expanduser()
    DST = Path(args.dst).expanduser()
    for p, label in ((SRC, "源文件"), (DST, "去敏文件")):
        if not p.is_file():
            print(f"[错误] 找不到{label}：{p}")
            return 1

    src = SRC.read_text(encoding="utf-8", errors="replace")
    dst = DST.read_text(encoding="utf-8", errors="replace")

    log: list[str] = []
    ok = True

    # ---- 1. 正文逐字比对
    s_parts = src.split(SPLIT_MARKER, 1)
    d_parts = dst.split(SPLIT_MARKER, 1)
    s_body = strip_tags(s_parts[1]) if len(s_parts) > 1 else ""
    d_body = strip_tags(d_parts[1]) if len(d_parts) > 1 else ""
    sn, dn = norm(s_body), norm(d_body)

    log.append("=== 1. 正文一致性（剥离标签 + 去空白后逐字比对）===")
    log.append(f"原文件正文长度  : {len(sn)}")
    log.append(f"去敏版正文长度  : {len(dn)}")
    log.append(f"正文完全一致    : {sn == dn}")
    if sn != dn:
        ok = False
        for i, (a, b) in enumerate(zip(sn, dn)):
            if a != b:
                log.append(f"首处差异 @ {i}")
                log.append(f"  原文: ...{sn[max(0, i - 40):i + 40]}...")
                log.append(f"  新文: ...{dn[max(0, i - 40):i + 40]}...")
                break
        log.append(f"长度差: {len(dn) - len(sn)}")
        log.append("  → 若差异仅为个别「方括号标签」替换，属预期；否则需人工核查。")

    # ---- 2. 题号标签
    log.append("")
    log.append("=== 2. 题号标签数 ===")
    sq, dq = NUM_TAG_RE.findall(src), NUM_TAG_RE.findall(dst)
    log.append(f"原文件: {len(sq)}   去敏版: {len(dq)}   {'一致' if len(sq) == len(dq) else '不一致'}")
    if len(sq) != len(dq):
        ok = False

    # ---- 3. 来源标签总数
    log.append("")
    log.append("=== 3. 来源标签总数 ===")
    st, dt = TAG_RE.findall(src), TAG_RE.findall(dst)
    log.append(f"原文件: {len(st)}   去敏版: {len(dt)}")
    log.append("（去敏版可能因头部说明块新增标签而略多，属正常）")

    # ---- 4. 套卷章节
    log.append("")
    log.append("=== 4. 套卷章节 ===")
    ss, ds = SEC_RE.findall(src), SEC_RE.findall(dst)
    log.append(f"原文件: {len(ss)}   去敏版: {len(ds)}   {'一致' if len(ss) == len(ds) else '不一致'}")
    if len(ss) != len(ds):
        ok = False
    for x in ds:
        log.append(f"  {x}")

    report = "\n".join(log)
    print(report)

    if args.out:
        out = Path(args.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
        print(f"\n报告已写入：{out}")

    print("\n[结论] " + ("通过：正文一致，仅标签被替换。" if ok else "不通过：存在差异，请人工核查。"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
