# -*- coding: utf-8 -*-
"""
把 shenlun-trainer 仓库同步到 WorkBuddy 的 skills 目录。

为什么需要这个脚本
------------------
本仓库是 shenlun-trainer 的【唯一真相源】。
所有修改都改在仓库里，再用本脚本同步到实际被加载的 skills 目录。

惨痛教训（2026-09-17）：仓库和已装目录各自被改过，两边分叉了 ——
已装版有新内容、仓库版有修复，不得不花时间做人工合并。
**从此只改仓库，然后同步。不要直接改 skills 目录。**

用法
----
    python sync_to_skills.py                    # 完整同步（自己用，推荐）
    python sync_to_skills.py --lite             # 精简同步（排除 corpus/docs，便于分享）
    python sync_to_skills.py --dry-run          # 只显示会动什么，不实际复制
    python sync_to_skills.py --target <路径>    # 指定目标目录
    python sync_to_skills.py --yes              # 跳过删除确认

注意：本脚本用 Python 而非 PowerShell 编写，因为 PowerShell 5.1
读取无 BOM 的 UTF-8 脚本会把中文搞乱（实测踩过这个坑）。
"""
from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

# ---------------------------------------------------------------- 常量
# 不同步的目录名（任何层级）
EXCLUDE_DIRS = {
    ".git", "__pycache__", ".venv", "venv", "env",
    "node_modules", ".idea", ".vscode", ".pytest_cache",
}
# 不同步的文件名后缀 / 文件名
EXCLUDE_SUFFIXES = {".bak", ".tmp", ".log", ".pyc", ".swp", ".swo"}
EXCLUDE_NAMES = {"Thumbs.db", ".DS_Store", "desktop.ini"}

# 精简模式额外排除
LITE_EXTRA_DIRS = {"corpus", "docs"}

# 默认目标
DEFAULT_TARGET = Path.home() / ".workbuddy" / "skills" / "shenlun-trainer"


def repo_root() -> Path:
    """仓库根 = 本脚本所在目录的上一级"""
    return Path(__file__).resolve().parent.parent


def should_skip(rel: Path, lite: bool) -> bool:
    """判断相对路径是否应跳过"""
    parts = rel.parts
    if any(p in EXCLUDE_DIRS for p in parts):
        return True
    if lite and any(p in LITE_EXTRA_DIRS for p in parts):
        return True
    if rel.suffix.lower() in EXCLUDE_SUFFIXES:
        return True
    if rel.name in EXCLUDE_NAMES:
        return True
    return False


def collect(root: Path, lite: bool) -> dict[Path, Path]:
    """收集要同步的文件：相对路径 -> 绝对路径"""
    result: dict[Path, Path] = {}
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if should_skip(rel, lite):
            continue
        result[rel] = p
    return result


def fmt_size(n: int) -> str:
    return f"{n / 1024:.1f} KB"


def main() -> int:
    ap = argparse.ArgumentParser(
        description="把 shenlun-trainer 仓库同步到 skills 目录",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--target", default=str(DEFAULT_TARGET),
                    help=f"目标目录（默认 {DEFAULT_TARGET}）")
    ap.add_argument("--lite", action="store_true",
                    help="精简模式：排除 corpus/ 与 docs/")
    ap.add_argument("--dry-run", action="store_true",
                    help="只显示将要进行的操作，不实际复制")
    ap.add_argument("--yes", action="store_true",
                    help="跳过删除确认")
    args = ap.parse_args()

    root = repo_root()
    target = Path(args.target).expanduser().resolve()

    # ---------------- 安全检查
    if not (root / "SKILL.md").is_file():
        print(f"[错误] 仓库根目录找不到 SKILL.md：{root}")
        print("       本脚本必须放在仓库的 scripts/ 目录下。")
        return 1

    try:
        target.relative_to(root)
        print(f"[错误] 目标目录位于仓库内部，会造成递归复制/误删：{target}")
        return 1
    except ValueError:
        pass  # 正常：目标不在仓库内

    # ---------------- 收集
    src_files = collect(root, args.lite)
    src_bytes = sum(p.stat().st_size for p in src_files.values())

    print("shenlun-trainer 同步")
    print(f"  源（真相源）: {root}")
    print(f"  目标        : {target}")
    print(f"  模式        : {'精简（不含 corpus/docs）' if args.lite else '完整'}")
    print(f"  源文件      : {len(src_files)} 个，{fmt_size(src_bytes)}")
    if args.dry_run:
        print("  ** DRY-RUN：只显示，不复制 **")
    print()

    # ---------------- 计算差异
    to_add, to_update, same = [], [], 0
    for rel, sp in sorted(src_files.items()):
        dp = target / rel
        if not dp.exists():
            to_add.append(rel)
        elif dp.stat().st_size != sp.stat().st_size or not filecmp.cmp(sp, dp, shallow=False):
            to_update.append(rel)
        else:
            same += 1

    to_delete: list[Path] = []
    if target.is_dir():
        for dp in target.rglob("*"):
            if not dp.is_file():
                continue
            rel = dp.relative_to(target)
            if should_skip(rel, args.lite):
                continue
            if rel not in src_files:
                to_delete.append(rel)

    print(f"  新增 {len(to_add)} 个 | 更新 {len(to_update)} 个 | "
          f"未变 {same} 个 | 多余待删 {len(to_delete)} 个")
    if to_add:
        print("\n  [新增]")
        for r in to_add:
            print(f"    + {r}")
    if to_update:
        print("\n  [更新]")
        for r in to_update:
            print(f"    ~ {r}")
    if to_delete:
        print("\n  [多余，将被删除]")
        for r in to_delete:
            print(f"    - {r}")

    if not (to_add or to_update or to_delete):
        print("\n已是最新，无需同步。")
        return 0

    if args.dry_run:
        print("\nDRY-RUN 结束，未做任何改动。")
        return 0

    # ---------------- 删除确认
    if to_delete and not args.yes:
        print(f"\n将删除目标目录中 {len(to_delete)} 个源仓库没有的文件（见上「多余，将被删除」）。")
        try:
            answer = input("确认继续？(y/N) ").strip().lower()
        except EOFError:
            answer = "n"
        if answer not in {"y", "yes"}:
            print("已取消。")
            return 0

    # ---------------- 执行复制
    target.mkdir(parents=True, exist_ok=True)
    for rel in to_add + to_update:
        dp = target / rel
        dp.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_files[rel], dp)

    for rel in to_delete:
        dp = target / rel
        try:
            dp.unlink()
        except OSError as e:
            print(f"  [警告] 删除失败 {rel}: {e}")

    # 清理空目录
    if target.is_dir():
        for d in sorted((p for p in target.rglob("*") if p.is_dir()),
                        key=lambda p: len(p.parts), reverse=True):
            try:
                if not any(d.iterdir()):
                    d.rmdir()
            except OSError:
                pass

    print(f"\n同步完成：新增 {len(to_add)}，更新 {len(to_update)}，删除 {len(to_delete)}。")
    print("提示：WorkBuddy 可能需要重启会话才会重新加载 skill。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
