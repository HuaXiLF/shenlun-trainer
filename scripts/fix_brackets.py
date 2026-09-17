# -*- coding: utf-8 -*-
"""
修掉去敏后残留的「方括号」形式来源标签。

背景：去敏脚本 desensitize.py 只处理【全角方括号】形式的标签，
但原始文件里少数来源用的是 [半角方括号]，会被漏掉。
本脚本把这些漏网的补上。

用法
----
    python fix_brackets.py                          # 处理仓库默认文件
    python fix_brackets.py --file path/to/file.md
    python fix_brackets.py --file xxx.md --out build/fix_report.txt
    python fix_brackets.py --dry-run                # 只看会改什么

退出码：0 = 无残留；1 = 仍有残留
"""
import argparse
import sys
from pathlib import Path

# 仓库根 = 本脚本所在目录的上一级（脚本位于 <repo>/scripts/）
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FILE = REPO_ROOT / "corpus" / "22-24国考申论参考答案-多机构去敏版.md"

# 半角方括号标签 -> 去敏后的全角标签
FIXES = [
    ("[金标尺答案]", "【JBC】"),
    ("[粉笔]", "【FB】"),
    ("[华图]", "【HT】"),
    ("[中公]", "【ZG】"),
    ("[站长]", "【ZZ】"),
]

# 修完后复查用
CHECK_KEYWORDS = [
    "粉笔", "华图", "站长", "中公", "半月谈", "金标尺", "超格",
    "导氮", "李铁", "毕上", "四海飞扬",
]


def main() -> int:
    ap = argparse.ArgumentParser(description="修复残留的半角方括号来源标签")
    ap.add_argument("--file", default=str(DEFAULT_FILE),
                    help=f"待处理文件（默认 {DEFAULT_FILE.name}）")
    ap.add_argument("--out", default=None, help="报告输出路径（可选）")
    ap.add_argument("--dry-run", action="store_true",
                    help="只显示会改什么，不写回文件")
    args = ap.parse_args()

    path = Path(args.file).expanduser()
    if not path.is_file():
        print(f"[错误] 找不到文件：{path}")
        return 1

    text = path.read_text(encoding="utf-8", errors="replace")

    log: list[str] = []
    changed_any = False
    for old, new in FIXES:
        n = text.count(old)
        if n:
            text = text.replace(old, new)
            log.append(f"{old} -> {new}  x{n}")
            changed_any = True

    if args.dry_run:
        print("DRY-RUN，未写回文件。")
    elif changed_any:
        path.write_text(text, encoding="utf-8")
        print(f"已更新：{path}")
    else:
        print("无需修改。")

    for line in log:
        print("  " + line)
    if not log:
        print("  （没有发现半角方括号标签）")

    # 复查残留
    resid = [f"{kw} x{text.count(kw)}" for kw in CHECK_KEYWORDS if text.count(kw)]
    print("\n--- 残留复查 ---")
    if resid:
        for r in resid:
            print("  " + r)
    else:
        print("  无")

    if args.out:
        out = Path(args.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            "\n".join(log + ["---残留---"] + (resid or ["无"])),
            encoding="utf-8",
        )
        print(f"\n报告已写入：{out}")

    return 1 if resid else 0


if __name__ == "__main__":
    sys.exit(main())
