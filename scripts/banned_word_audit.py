#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
禁用词与数字口径审计器（三轮分级版）
—— 2026-09-02 交付线巡检中沉淀，避免每周重写。

用途：按「袁六伟项目事实基线 v2」扫描 Obsidian 子目录，输出可执行的整改清单。
关键价值：原始正则会把「第一期/第一课」这类序数全算成极限词（本次 281 命中里 168 是噪音），
         本脚本三轮分级后只留真实需改项，避免老板被假警报淹没。

用法：
  python3 banned_word_audit.py                    # 用内置默认范围（交付线资产）
  python3 banned_word_audit.py 子目录1 子目录2 ...   # 指定相对 vault 根的子目录

分级逻辑：
  🔴 真实需改   → 对外广告语境的禁用词，必须改
  ⚪ 元语境     → 该行本身在教「别用禁用词」（如合规检查清单），免改
  ⚫ 术语误报   → 「唯一事实源」「绝对路径」等内部技术表述，不改
  🟢 低风险     → 序数（第一期/第一课）、叙述（最大的问题）、否定式（不能保证），不阻断
"""
import os, re, sys, json, subprocess
from collections import defaultdict

# ── 事实基线口径（v2 / 2026-08-29 袁总拍板）────────────────────────────
BASELINE = {
    "学员数": "5000+",
    "服务客户数": "100+",          # 废止：80+ / 90+
    "商业课正式价": "99元",
    "商业课首发价": "19.9元",      # 废止：49元
    "履历口径": "几乎没打过工",     # 禁：在XX公司工作过/被裁员/前公司
}

BANNED = {
    "承诺类": ["保证", "承诺", "必赚", "必成", "一定能", "包过", "包学会"],
    "绝对化": ["100%", "百分百", "绝对", "完全免费"],
    "极限词": ["第一", "唯一", "最好", "最强", "最优", "最低", "最高", "最快",
               "最有用", "最大", "顶级", "极致", "史无前例"],
    "权威滥用": ["国家级", "官方指定", "驰名商标"],
}

NUM_PATTERNS = {
    "❌客户数废止口径80+": r"(?:服务)?客户\s*80\s*\+|80\+\s*(?:家|企业|客户)",
    "❌客户数废止口径90+": r"(?:服务)?客户\s*90\s*\+|90\+\s*(?:家|企业|客户)",
    "⚠️学员数非5000口径": r"学员\s*(?!5000)([0-9]{3,4})\s*\+",
    "⚠️课程价格口径": r"(?:¥|￥)?\s*(?:19\.9|49|50|99|299|699|1999|2499|2999|3499)\s*元",
}

DEFAULT_SCOPE = [
    "IP知识库/交付案例",
    "IP知识库/04-项目案例",
    "IP知识库/21-课程开发工作台/2026-08-01-WorkBuddy一人公司商业实战课/06-运营包",
    "公司运营",
]

# ── 分级判据 ──────────────────────────────────────────────────────────
ORDINAL_OK = re.compile(
    r"第一(?:期|课|节|个|天|周|版|步|篇|次|条|轮|人称|句|模块|阶段|年|批|讲|"
    r"部分|时间|章|层|眼|页|位|行|单|站|类|块|波|印象|性原理|梯队|笔|段|支|门)"
)
NARRATIVE = re.compile(
    r"最大的(?:问题|卡点|认知误区|坑|障碍|难题|阻力|差异|收获)|最高频|最有用的是|"
    r"[「\"“].*最.*[」\"”]"
)
NEGATED = re.compile(r"(不能|不会|无法|难以|别指望|不可能|不做任何|零)\s*[^。；]{0,10}(保证|承诺|100%|绝对)")
META = re.compile(
    r"禁用词|违禁词|合规检查|绝对化表达|绝对化承诺|绝对化用语|广告法|"
    r"是否有[\"“']?保证|搜索[\"“']?保证|删除绝对化|零绝对化|全文未使用|等绝对化"
)
JARGON = re.compile(r"唯一事实源|Single Source of Truth|全链唯一|绝对路径|唯一入口|唯一标识")


def locate_vault():
    """禁止写死 iCloud 路径（外层快照名含日期会变），一律用 obsidian.py locate"""
    out = subprocess.run(
        ["python3", os.path.expanduser("~/.workbuddy/skills/obsidian-vault/scripts/obsidian.py"), "locate"],
        capture_output=True, text=True,
    )
    return out.stdout.strip()


def grade(word, cat, text):
    """返回 (等级, 说明)"""
    if JARGON.search(text):
        return "术语误报", "内部技术术语（唯一事实源/绝对路径等），非广告"
    if META.search(text):
        return "元语境", "该行本身在教「别用禁用词」，属教学示例"
    if word == "第一":
        if "第一" not in ORDINAL_OK.sub("", text):
            return "低风险", "序数/固定搭配（第一期/第一课等）"
        return "真实需改", "疑似「行业第一/第一人」式极限表述"
    if word in ("最好", "最强", "最优", "最低", "最高", "最快", "最有用", "最大"):
        if NARRATIVE.search(text):
            return "低风险", "叙述或客户引语语境，非广告承诺"
        return "真实需改", "极限词，对外物料需改写"
    if word in ("保证", "承诺", "100%", "绝对"):
        if NEGATED.search(text):
            return "低风险", "否定式使用，基线明示合规"
        return "真实需改", f"{cat}，广告法红线"
    if word == "唯一":
        return "真实需改", "极限词，建议改为「少见的/我目前只用这一种」"
    return "真实需改", f"{cat} 禁用词"


def main():
    args = sys.argv[1:]
    file_targets = [a for a in args if os.path.isfile(a)]
    root = ""
    if not file_targets:
        root = locate_vault()
        if not root or not os.path.isdir(root):
            sys.exit("❌ 请传入要审计的 Markdown 文件路径（如: python3 scripts/banned_word_audit.py 03-public-safe发布稿.md），或配置本地 Obsidian Vault。")
    scope = args or DEFAULT_SCOPE

    buckets = defaultdict(list)
    numbers = []
    scanned = 0

    def scan_file(fp, relp):
        nonlocal scanned
        try:
            lines = open(fp, encoding="utf-8", errors="ignore").read().splitlines()
        except Exception:
            return
        scanned += 1
        for i, line in enumerate(lines, 1):
            for cat, words in BANNED.items():
                for w in words:
                    if w in line:
                        lv, why = grade(w, cat, line)
                        buckets[lv].append(
                            {"file": relp, "line": i, "cat": cat, "word": w,
                             "text": line.strip()[:120], "why": why}
                        )
            for label, pat in NUM_PATTERNS.items():
                for m in re.finditer(pat, line):
                    numbers.append({"file": relp, "line": i, "label": label,
                                    "match": m.group(0), "text": line.strip()[:120]})

    if file_targets:
        for fp in file_targets:
            scan_file(fp, fp)
    else:
        for rel in scope:
            base = os.path.join(root, rel) if not os.path.isdir(rel) else rel
            if not os.path.isdir(base):
                print(f"⚠️ 跳过不存在的范围：{rel}")
                continue
            for dirpath, _, files in os.walk(base):
                for fn in files:
                    if fn.endswith(".md"):
                        fp = os.path.join(dirpath, fn)
                        relp = os.path.relpath(fp, root) if root else fp
                        scan_file(fp, relp)

    real = buckets["真实需改"]
    print(f"扫描 {scanned} 文件 | 🔴真实需改 {len(real)} / ⚪元语境 {len(buckets['元语境'])} "
          f"/ ⚫术语误报 {len(buckets['术语误报'])} / 🟢低风险 {len(buckets['低风险'])}")
    print(f"数字口径命中 {len(numbers)} 处\n")

    print("=" * 72)
    print("【🔴 真实需改·按文件】")
    byf = defaultdict(list)
    for r in real:
        byf[r["file"]].append(r)
    for f in sorted(byf, key=lambda x: -len(byf[x])):
        wc = defaultdict(int)
        for r in byf[f]:
            wc[r["word"]] += 1
        print(f"{len(byf[f]):>3} 处 | {f}")
        print("        " + " / ".join(f"{k}×{v}" for k, v in sorted(wc.items(), key=lambda x: -x[1])))
        for r in byf[f][:3]:
            print(f"        L{r['line']}: {r['text']}")

    print("\n" + "=" * 72)
    print(f"【数字口径命中】基线：客户 {BASELINE['服务客户数']} / "
          f"正式价 {BASELINE['商业课正式价']} / 首发 {BASELINE['商业课首发价']}")
    for n in numbers:
        print(f"{n['label']} {n['file']} L{n['line']} → {n['match']}")
        print(f"     {n['text']}")

    out_dir = os.path.expanduser("~/.config/wechat-autopilot")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "banned_word_audit_last.json")
    json.dump({"scanned": scanned, "buckets": dict(buckets), "numbers": numbers},
              open(out, "w"), ensure_ascii=False, indent=1)
    print(f"\n>>> 明细已存 {out}")


if __name__ == "__main__":
    main()
