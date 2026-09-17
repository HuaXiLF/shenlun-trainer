#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
申论字数核对工具（shenlun-trainer skill 配套）
用法：
    python count_words.py <文件路径>                  # 统计文件字数
    python count_words.py <文件路径> --limit 500      # 带限额校验
    python count_words.py --text "答案文本..." --limit 500

统计口径（与阅卷一致）：
    - 计入：汉字、标点符号、数字、英文字母（每字符 1 字）
    - 不计入：换行、空格
    - 注意：标题、称谓、结语均计入

安全线公式：限额 × 0.92（取整到 5 的倍数）
"""
import re
import sys
import argparse


def count_words(text: str) -> int:
    """按申论阅卷口径统计字数（含标点、不含空格换行）"""
    return len(re.sub(r'[\r\n\s]+', '', text))


def safe_limit(limit: int) -> int:
    """安全线：限额 × 0.92，取整到 5 的倍数"""
    raw = limit * 0.92
    return int(round(raw / 5) * 5)


def main():
    parser = argparse.ArgumentParser(description='申论字数核对工具')
    parser.add_argument('file', nargs='?', help='待统计的文本文件路径')
    parser.add_argument('--text', help='直接传入文本')
    parser.add_argument('--limit', type=int, help='题目字数上限（如 500）')
    parser.add_argument('--label', default='', help='标签，如"参考答案"/"用户答案"')
    args = parser.parse_args()

    if args.text:
        content = args.text
    elif args.file:
        with open(args.file, encoding='utf-8') as f:
            content = f.read()
    else:
        print('错误：请提供 file 或 --text')
        sys.exit(1)

    n = count_words(content)
    label = f"[{args.label}] " if args.label else ""

    if not args.limit:
        print(f'{label}字数：{n}')
        return

    hard = args.limit
    safe = safe_limit(args.limit)
    hanzi = len(re.findall(r'[\u4e00-\u9fff]', content))
    punct = n - hanzi

    print(f'{label}字数统计（含标点、不含空格换行）')
    print(f'  总字数    : {n}')
    print(f'  其中汉字  : {hanzi}')
    print(f'  其中标点等: {punct}')
    print(f'  硬上限    : {hard}')
    print(f'  实战安全线: {safe}  (= {hard} × 0.92)')
    print('-' * 32)

    if n > hard:
        print(f'  ❌ 超硬上限 {n - hard} 字，必须删改重写！')
        sys.exit(2)
    elif n > safe:
        print(f'  ⚠️  超安全线 {n - safe} 字（未超硬上限），建议压缩')
        sys.exit(1)
    else:
        print(f'  ✅ 字数合规（{n}/{hard}，安全线 {safe}）')
        sys.exit(0)


if __name__ == '__main__':
    main()
