# scripts/ 工具说明

本目录有两类脚本：**日常用的**和**语料处理用的**。

> ⚠️ 本目录的脚本用 **Python** 编写（不用 PowerShell），
> 因为 PowerShell 5.1 读取无 BOM 的 UTF-8 脚本会把中文搞乱（实测踩过）。

---

## 一、日常用

### `sync_to_skills.py` —— 把仓库同步到 skills 目录 ⭐

**本仓库是 shenlun-trainer 的唯一真相源。** 所有修改都改在仓库里，
然后用这个脚本同步到实际被加载的 skills 目录。

```bash
python scripts/sync_to_skills.py            # 完整同步（自己用，推荐）
python scripts/sync_to_skills.py --lite     # 精简同步（排除 corpus/docs，便于分享）
python scripts/sync_to_skills.py --dry-run  # 只显示会动什么，不复制
python scripts/sync_to_skills.py --yes      # 跳过删除确认
```

> **为什么需要它？**
> 2026-09-17 发生过一次事故：仓库和已装目录各自被改，两边分叉了 ——
> 已装版有新内容、仓库版有修复，最后不得不做人工合并。
> **从此只改仓库，然后同步。不要直接改 skills 目录。**

### `count_words.py` —— 申论字数核对 ⭐

按阅卷口径统计字数（含标点、不含空格换行），自动判定硬上限与实战安全线。

```bash
python scripts/count_words.py 答案.txt --limit 500
python scripts/count_words.py --text "……" --limit 300 --label "参考答案"
```

退出码：`0` 合规 ｜ `1` 超安全线 ｜ `2` 超硬上限。

**安全线 = 限额 × 0.92**（500 字题 → 460 字）。原因：申论答题卡每格 1 字、
标点独立占格、手写字体偏大。**禁止目测字数。**

---

## 二、语料处理用（作者侧工具）

这一组是当初整理 `corpus/` 答案库时用的。**它们需要「去敏前的原始文件」才能跑**，
而那个原始文件因版权原因不在本仓库中。所以对你来说它们主要是**参考实现**，
用来了解语料是怎么处理的。

| 脚本 | 作用 | 是否需要外部输入 |
|:---|:---|:---|
| `desensitize.py` | 来源标签去敏（机构→拼音缩写，人名→匿名编号） | **需要** `--src` 原始文件 |
| `check_residual.py` | 扫描去敏后是否还有来源名残留 | 不需要（默认扫仓库文件） |
| `fix_brackets.py` | 修掉漏网的全角/半角方括号标签 | 不需要 |
| `verify_accuracy.py` | 比对去敏前后正文是否逐字一致 | **需要** `--src` 原始文件 |

### 用法

```bash
# 去敏（--src 必填）
python scripts/desensitize.py --src "22-24国考申论参考答案（多机构文本版）.md"

# 残留扫描（默认扫仓库里的去敏版答案库）
python scripts/check_residual.py
python scripts/check_residual.py --file corpus/xxx.md --out build/residual.txt

# 方括号修复（先 dry-run 看会改什么）
python scripts/fix_brackets.py --dry-run
python scripts/fix_brackets.py

# 准确性核验（--src 必填）
python scripts/verify_accuracy.py --src "原始文件.md" --out build/accuracy.txt
```

### 去敏规则（`desensitize.py`）

1. 只处理 `【xxx】` 形式的来源标签，**不改动答案正文**
2. **长标签优先匹配** —— 避免「粉笔单淑玲」被「粉笔」先吃掉
3. 机构 → 通行拼音缩写：`粉笔→FB`、`华图→HT`、`站长→ZZ`、`中公→ZG` …
4. 个人教师 / 网络 ID → 匿名编号 `T01`、`T02` …（同一人不同写法归入同一编号）
5. 非来源标签（题号、页码、编辑标记）→ **原样保留**

> ⚠️ **诚实说明**：拼音缩写是**公开通行**的对应关系，熟悉公考的人可以还原。
> 去敏的**实际作用**是降低搜索引擎命中率、表明"非官方转载"立场、避免直接使用机构商标。
> **它不等于匿名化。** 完整映射见 [`../corpus/来源对照表.md`](../corpus/来源对照表.md)。

---

## 三、当前状态

最近一次核验（2026-09-17）：

| 检查项 | 结果 |
|:---|:---|
| 来源名残留（`check_residual.py`） | **0 处** ✅ |
| 半角方括号残留（`fix_brackets.py`） | **0 处** ✅ |
| 去敏前后正文一致性（`verify_accuracy.py`） | 正文逐字一致，差异仅标签替换 ✅ |
| 字数工具（`count_words.py`） | 退出码 0/1/2 均正常 ✅ |

---

## 四、依赖

**无第三方依赖**，只用 Python 标准库（`argparse` / `pathlib` / `re` / `json` / `shutil`）。
Python 3.9+ 即可（用到了 `tuple[list[str], int]` 类型标注，3.9+ 支持）。
