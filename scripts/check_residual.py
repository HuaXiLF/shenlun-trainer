# -*- coding: utf-8 -*-
"""
扫描去敏后的文件里是否还有机构名 / 人名残留。

用法
----
    # 默认扫描仓库里的去敏版答案库
    python check_residual.py

    # 指定文件
    python check_residual.py --file path/to/file.md

    # 结果同时写到文件
    python check_residual.py --out build/residual.txt

退出码：0 = 无残留；1 = 有残留（便于接进 CI / 脚本）
"""
import argparse
import re
import sys
from pathlib import Path

# 仓库根 = 本脚本所在目录的上一级（脚本位于 <repo>/scripts/）
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FILE = REPO_ROOT / "corpus" / "22-24国考申论参考答案-多机构去敏版.md"

# 需要检查残留的来源名（机构 + 个人教师 + 网络 ID）
KEYWORDS = [
    # 机构
    "粉笔", "华图", "站长", "中公", "半月谈", "超格", "导氮", "金标尺",
    "李铁", "毕上", "四海飞扬", "四海", "永岸", "成公", "逸学",
    # 个人教师 / 网络 ID
    "袁东", "单淑玲", "刘大师", "宋复法", "杨柳岸", "小马哥", "江牧云",
    "江牡云", "樊政", "程诺", "相丽君", "林宇", "白鹭", "黑魔仙",
    "千寻", "唐棣", "何飞羽", "贺冲", "钟君", "帅神俊", "一眉巫师", "坨坨",
]


def scan(path: Path, context: int = 30, max_ctx: int = 3) -> tuple[list[str], int]:
    """返回 (报告行列表, 残留总次数)"""
    text = path.read_bytes().decode("utf-8", errors="replace")

    lines: list[str] = []
    total = 0
    kinds = 0

    for kw in KEYWORDS:
        n = text.count(kw)
        if not n:
            continue
        kinds += 1
        total += n
        lines.append(f"### {kw}  x{n}")
        shown = 0
        for m in re.finditer(re.escape(kw), text):
            s = max(0, m.start() - context)
            e = min(len(text), m.end() + context)
            lines.append("    ..." + text[s:e].replace("\n", "\\n") + "...")
            shown += 1
            if shown >= max_ctx:
                break

    header = [
        f"文件: {path}",
        f"字节: {len(text.encode('utf-8'))}",
        f"残留关键词种类: {kinds}",
        f"残留总次数: {total}",
        "",
    ]
    return header + lines, total


def main() -> int:
    ap = argparse.ArgumentParser(description="扫描去敏文件的来源名残留")
    ap.add_argument("--file", default=str(DEFAULT_FILE),
                    help=f"待扫描文件（默认 {DEFAULT_FILE.name}）")
    ap.add_argument("--out", default=None,
                    help="把报告写到文件（不给则只打印到终端）")
    args = ap.parse_args()

    path = Path(args.file).expanduser()
    if not path.is_file():
        print(f"[错误] 找不到文件：{path}")
        return 1

    lines, total = scan(path)
    report = "\n".join(lines)

    print(report)
    if args.out:
        out = Path(args.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
        print(f"\n报告已写入：{out}")

    if total == 0:
        print("\n[通过] 无残留。")
        return 0
    print(f"\n[不通过] 发现 {total} 处残留。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
