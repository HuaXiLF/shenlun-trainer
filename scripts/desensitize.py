# -*- coding: utf-8 -*-
"""
机构/人名去敏脚本
-----------------
把「22-24国考申论参考答案（多机构文本版）.md」中的来源标签
统一替换为通行拼音缩写或匿名编号。

用法
----
    # --src 指向【未去敏】的原始文件（不在本仓库中，需自备）
    python desensitize.py --src "22-24国考申论参考答案（多机构文本版）.md"

    # 可选参数
    python desensitize.py --src "原始.md" --dst corpus/xxx.md --report build/r.json

策略：
  1. 只处理【xxx】形式的来源标签，不动正文
  2. 长标签优先匹配（避免「粉笔单淑玲」被「粉笔」先吃掉）
  3. 机构 -> 通行拼音缩写（用户指定）
  4. 个人老师 / 网络ID -> 匿名编号（T01, T02...）
  5. 非来源标签（纯数字、摘要、答案一等）-> 保持不变
"""
import argparse
import json
import re
import sys
from pathlib import Path

# 仓库根 = 本脚本所在目录的上一级（脚本位于 <repo>/scripts/）
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DST = REPO_ROOT / "corpus" / "22-24国考申论参考答案-多机构去敏版.md"
DEFAULT_REPORT = REPO_ROOT / "build" / "desens_report.json"

# ============================================================
# 一、机构 -> 通行拼音缩写
# ============================================================
INSTITUTION = {
    "粉笔": "FB",
    "华图": "HT",
    "中公": "ZG",
    "站长": "ZZ",
    "四海飞扬": "SH",
    "四海": "SH",
    "半月谈": "BYT",
    "超格": "CG",
    "导氮": "DN",
    "金标尺": "JBC",
    "李铁教育": "LT",
    "毕上教育": "BSJY",
    "成公申论": "CGS L".replace(" ", ""),
    "逸学公考": "YXGK",
    "跃跃公考": "YYGK",
    "大帅公考": "DSGK",
    "自立公考老大哥": "ZLGK",
    "先申夺人": "XSSR",
    "永岸": "YA",
    "尚书大魔王": "SSDMW",
}

# ============================================================
# 二、个人老师 / 网络ID -> 匿名编号
#    同一人不同写法归到同一编号
# ============================================================
PERSON = {
    # T01 袁东
    "袁东": "T01",
    # T02 刘大师
    "刘大师": "T02",
    # T03 单淑玲（含多种写法）
    "单淑玲": "T03",
    "粉笔单淑玲": "T03",
    "单淑玲（先申夺人）": "T03",
    "单淑玲-先申夺人": "T03",
    "大锤单淑玲": "T03",
    "先申夺人 单淑玲": "T03",
    # T04 蒋春旭
    "粉笔蒋春旭": "T04",
    # T05 宋复法
    "宋复法": "T05",
    "B站宋复法": "T05",
    "阅卷人宋复法老师": "T05",
    "申论宋复法老师": "T05",
    # T06 杨柳岸
    "杨柳岸": "T06",
    "B站杨柳岸": "T06",
    # T07 小张（申论）
    "小张": "T07",
    "小张申论": "T07",
    "B站 小张申论": "T07",
    "B站申论小张": "T07",
    "爱写申论的小张": "T07",
    "B站 爱写申论的小张": "T07",
    "不在水里的小张": "T07",
    # T08 林宇
    "小红书林宇": "T08",
    "林宇答案": "T08",
    # T09 江牧云
    "江牧云": "T09",
    "公考江牡云": "T09",
    "公考江牧云": "T09",
    # T10 半月谈白鹭 / 白鹭
    "半月谈白鹭": "T10",
    "白鹭": "T10",
    # T11 半月谈一一老师 / 一一
    "半月谈一一老师": "T11",
    "半月谈一一": "T11",
    "一一": "T11",
    # T12 半月谈其他（大罗/初心）
    "半月谈大罗": "T12",
    "半月谈-初心老师": "T12",
    "补充11：半月谈初心": "T12",
    # T13 樊政
    "樊政": "T13",
    "樊政范文": "T13",
    # T14 程诺
    "程诺": "T14",
    # T15 相丽君
    "相丽君": "T15",
    # T16 人须在事上磨
    "人须在事上磨": "T16",
    "人须磨": "T16",
    # T17 B站小马哥
    "B站小马哥": "T17",
    # T18 折线阳
    "折线阳（b站）": "T18",
    # T19 槲叶明栀
    "槲叶明栀（B站）": "T19",
    # T20 黑魔仙
    "网友：黑魔仙": "T20",
    "网友黑魔仙": "T20",
    # T21 不鸣则已kk
    "不鸣则已kk（b站）": "T21",
    # T22 dhpolitzer
    "B站dhpolitzer": "T22",
    # T23 体制内的笔杆子
    "B站，体制内的笔杆子": "T23",
    # T24 坨坨必成公
    "坨坨必成公": "T24",
    # T25 吃宵夜考公
    "吃宵夜考公": "T25",
    # T26 帅神俊
    "帅神俊": "T26",
    # T27 一眉巫师
    "一眉巫师": "T27",
    # T28 千寻
    "千寻": "T28",
    # T29 木木
    "木木": "T29",
    # T30 唐棣
    "唐棣": "T30",
    # T31 何飞羽
    "何飞羽": "T31",
    # T32 贺冲
    "贺冲": "T32",
    # T33 钟君
    "钟君": "T33",
    # T34 四海陶易
    "四海陶易": "T34",
    # T35 裕鑫（四海）
    "裕鑫（四海）": "T35",
    # T36 qx / QY
    "qx": "T36",
    "QY": "T36",
    # T37 小红书实战80+
    "小红书实战80+": "T37",
    # T38 上岸c
    "上岸c": "T38",
    # T39 美女丹本人
    "美女丹本人": "T39",
    # T40 高分大神
    "高分大神": "T40",
    # T41 知乎
    "知乎": "T41",
    # T42 中国经济网
    "中国经济网": "T42",
    # T43 某公考机构
    "某公考机构": "T43",
    # T44 姚（如出现）
    "飞扬": "T44",
    # T45 尚书大魔王（已上岸部委）已并入机构；此处保留残余写法
    "尚书大魔王 （已上岸部委）": "T45",
    "公考尚书": "T45",
}

# ============================================================
# 三、非来源标签 —— 必须原样保留
# ============================================================
KEEP_AS_IS = {
    "摘要", "整合", "答案", "答案一", "答案二", "z",
    "知乎总结：总结式", "知乎总结：引入式",
}

# 纯数字 / 页码区间类标签的正则
NUMERIC_LIKE = re.compile(r"^\s*\d+(\s*[-–]\s*\d+)?\s*$")


def build_mapping():
    """合并映射，长键优先"""
    m = {}
    m.update(INSTITUTION)
    m.update(PERSON)
    # 按 key 长度降序，保证「粉笔单淑玲」先于「粉笔」匹配
    return sorted(m.items(), key=lambda kv: -len(kv[0]))


def classify(label):
    """返回 (new_label, category)"""
    s = label.strip()
    if s in KEEP_AS_IS or NUMERIC_LIKE.match(s):
        return label, "keep"
    return None, "unknown"


def main():
    ap = argparse.ArgumentParser(description="机构/人名去敏")
    ap.add_argument("--src", required=True,
                    help="未去敏的原始文件路径（必填）")
    ap.add_argument("--dst", default=str(DEFAULT_DST),
                    help=f"输出去敏文件路径（默认 {DEFAULT_DST.name}）")
    ap.add_argument("--report", default=str(DEFAULT_REPORT),
                    help="去敏报告输出路径")
    args = ap.parse_args()

    SRC = Path(args.src).expanduser()
    DST = Path(args.dst).expanduser()
    REPORT = Path(args.report).expanduser()

    if not SRC.is_file():
        print(f"[错误] 找不到源文件：{SRC}")
        return 1

    text = SRC.read_text(encoding="utf-8", errors="replace")

    mapping = build_mapping()
    changed = {}          # 原标签 -> 新标签
    unknown = {}          # 未识别的标签

    def repl(match):
        raw = match.group(1)
        s = raw.strip()

        # 保留类
        if s in KEEP_AS_IS or NUMERIC_LIKE.match(s):
            return match.group(0)

        # 精确映射（全等）
        for k, v in mapping:
            if s == k:
                changed[k] = v
                return f"【{v}】"

        # 前缀映射（处理「粉笔XXX」这类未穷举的复合标签）
        for k, v in mapping:
            if s.startswith(k) and len(s) > len(k):
                suffix = s[len(k):].strip("-— 　")
                if suffix:
                    new = f"{v}-{suffix}"
                else:
                    new = v
                changed[s] = new
                return f"【{new}】"

        unknown[s] = unknown.get(s, 0) + 1
        return match.group(0)

    new_text = re.sub(r"【([^】]{1,30})】", repl, text)

    # 写入
    DST.parent.mkdir(parents=True, exist_ok=True)
    DST.write_text(new_text, encoding="utf-8")

    # 报告
    report = {
        "src": str(SRC),
        "dst": str(DST),
        "src_bytes": len(text.encode("utf-8")),
        "dst_bytes": len(new_text.encode("utf-8")),
        "changed_count": len(changed),
        "changed": changed,
        "unknown_count": len(unknown),
        "unknown": unknown,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"完成：映射 {len(changed)} 个标签，未识别 {len(unknown)} 个")
    print(f"  输出：{DST}")
    print(f"  报告：{REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
