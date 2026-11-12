#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
袁氏改写判别标准 · 机械预检
================================
七条判别维度里，「代码能判」的四条由本脚本判；剩下三条（判断前有无担保、
抽象后有无生活类比、可拿走密度升降）需要语义理解，交模型。

⚠️ 权威源是 `wechat-auto-publisher/references/editorial-contract.md`。
   本脚本服从它，尤其这两条：
   ① 契约禁止「不用'95分''爆款概率'等无数据分数自我验收」→ 本脚本**不输出任何分数或通过率**，
      只输出待改清单。
   ② 契约规定「来源、真实性说明、内部审稿备注一律写在 `## 正文` 之前」→
      元信息检测只扫 `## 正文` 之后，不误伤合法的来源说明。

用法：
    python3 check_yuan_style.py <稿子.md> [<稿子2.md> ...]
    python3 check_yuan_style.py --compare <改前.md> <改后.md>

设计依据：../references/袁氏改写判别标准.md
核心原则：判决权归代码，不归模型。
"""
import sys, os, re

# ---------------- 词表 ----------------

# 维度①：抽象主语开头（AI 版典型开头）
ABSTRACT_SUBJ = ["很多人", "大多数人", "不少人", "许多人", "读者", "大家", "我们",
                 "众所周知", "随着", "在当今", "越来越多的人", "一直以来"]

# 维度⑤：正文里的"关于这篇文章"元信息（只扫 `## 正文` 之后）
META_PATTERNS = [
    (r"可信度\s*[:：]?\s*[SABsab]\s*级", "可信度分级"),
    (r"^来源\s*[:：]", "来源标注"),
    (r"选题来源|选题判断|选题卡", "选题判断"),
    (r"事实底|文风\s*DNA", "内部事实底"),
    (r"配图清单|配图索引|配图素材清单", "配图清单"),
    (r"风险自查|降风险|风险与", "风险自查"),
    (r"未采用角度|内部锋利判断", "内部锋利判断"),
    (r"内部草稿|内部打磨稿|内部版|内部保留", "内部稿标记"),
    (r"修改记录|重写指令", "修改记录"),
    (r"发布前检查|public-safe\s*检查", "发布检查清单"),
    (r"待填|占位符|TODO", "占位符"),
]

# 维度⑥：书面词 → 口语词。只收误报率低的几组。
# 「完全」「最后」已剔除——"完全相同的提问""写在最后"都是合理用法。
COLLOQUIAL = {
    "因此": "所以",
    "进行": "做",
    "使用": "用",
    "此外": "另外",
    "具有": "有",
    "是否": "是不是",
}

# 维度⑥：情绪化形容（强度高、信息量低）
EMOTIVE = ["荒诞", "震惊", "炸裂", "疯狂", "逆天", "史诗级", "颠覆性", "令人惊叹", "不可思议"]

# 功能性小标题，不算"名词标签"
FUNC_HEADS = {"正文", "开头", "结尾", "正文开始", "最后", "写在最后",
              "总结", "小结", "先看结论", "写在前面"}

# 维度②：小标题里的判断信号（有这些 = 自带判断）
JUDGE_MARKERS = ["是", "不是", "没有", "要", "别", "该", "怎么", "为什么", "凭什么",
                 "第一", "第二", "第三", "意外", "差在", "根本", "其实", "才是",
                 "值得", "不能", "只会", "真相", "误区", "靠", "看", "不"]


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def strip_front(s):
    if s.startswith("---"):
        parts = s.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return s.strip()


def main_body(s):
    """
    取「正文」。
    优先按契约的 `## 正文` 标记切分——契约要求来源与非公开备注写在它之前，转换脚本只取之后的部分。
    所以只有 `## 正文` 之后出现的元信息才是真问题，之前的是合规的。
    没有该标记时，退回"剥掉第一个 H1 + 所有引用块"。
    """
    m = re.search(r"^##\s*正文\s*$", s, re.M)
    if m:
        return s[m.end():]
    out, seen_h1 = [], False
    for l in s.splitlines():
        if l.startswith("# ") and not seen_h1:
            seen_h1 = True
            continue
        if l.startswith(">"):
            continue
        out.append(l)
    return "\n".join(out)


def han(s):
    return len(re.findall(r"[\u4e00-\u9fff]", s))


def leading_paras(s, n=3):
    """取正文开头 n 段。成稿常把场景放在第二段，只看第一段会误判。"""
    out = []
    for blk in re.split(r"\n\s*\n", s):
        t = blk.strip()
        if not t or t.startswith(("#", ">", "|", "![", "```", "---")):
            continue
        out.append(t)
        if len(out) >= n:
            break
    return out


def subheads(s):
    return [re.sub(r"^#+\s*", "", l.strip()) for l in s.splitlines()
            if re.match(r"^#{2,3}\s+", l)]


def quote_count(s):
    return len(re.findall(r"[「『“][^」』”]{4,}[」』”]", s))


def check(text, name):
    s = strip_front(text)
    body = main_body(s)
    todo, passed, info = [], [], []

    # ---------- ① 开篇 ----------
    leads = leading_paras(body, 3)
    p0 = leads[0] if leads else ""
    blob = "\n".join(leads)
    abs_hit = [w for w in ABSTRACT_SUBJ if p0.startswith(w)]
    if abs_hit:
        todo.append(f"① 开篇以抽象主语「{abs_hit[0]}」起句 —— 换成现场动作或引号里的原话")
    elif quote_count(blob) > 0:
        passed.append("① 开篇有直接引语")
    elif re.search(r"我(正在|刚|昨天|上周|这两周|后台|身边|在给|把|自己)", blob):
        passed.append("① 开篇有第一人称现场")
    elif re.search(r"(昨天|前天|上周|前几天|上个月|这两天)", blob) \
            and re.search(r"(我|一个|有个|朋友|学员|客户|博主|老板|腾讯|官方)", blob):
        passed.append("① 开篇有具象场景（时间锚 + 具体主体）")
    else:
        todo.append("① 开篇看不出场景 —— 需人工确认（标准：有一个具体的人在做具体的事）")

    # ---------- ② 小标题 ----------
    hs = [h for h in subheads(body) if h not in FUNC_HEADS]
    if hs:
        weak = [t for t in hs
                if not any(m in t for m in JUDGE_MARKERS) and len(t) <= 12
                and not re.search(r"[0-9]", t)]
        if weak:
            todo.append(f"② {len(weak)} 个小标题像名词标签（{'、'.join(weak[:4])}）—— 改成自带判断的短句")
        else:
            passed.append(f"② {len(hs)} 个小标题都自带判断")
        long_h = [t for t in hs if len(t) > 25]
        if long_h:
            info.append(f"② 有 {len(long_h)} 个小标题超 25 字（自带判断就不算问题）")
    else:
        info.append("② 无二级小标题（单段短文可忽略）")

    # ---------- ⑤ 元信息残留 ----------
    meta_hits = sorted({label for pat, label in META_PATTERNS if re.search(pat, body, re.M)})
    if meta_hits:
        todo.append(f"⑤ 正文残留元信息：{'、'.join(meta_hits)} —— "
                    f"内部判断类直接删；来源说明类挪到 `## 正文` 之前")
    else:
        passed.append("⑤ 正文无元信息残留")

    # ---------- ⑥ 用词 ----------
    coll_hits = [f"{w}→{b}" for w, b in COLLOQUIAL.items() if w in body]
    if coll_hits:
        todo.append(f"⑥ 书面词可换口语：{'、'.join(coll_hits)}")
    else:
        passed.append("⑥ 无待换书面词")
    emo = [w for w in EMOTIVE if w in body]
    if emo:
        todo.append(f"⑥ 情绪化形容建议换事实陈述：{'、'.join(emo)}")

    # ---------- 信息项（不计入待改清单）----------
    n = han(body)
    blocks = len(re.findall(r"```", body)) // 2
    lists = len(re.findall(r"^\s*(\d+\.|[-*])\s+", body, re.M))
    info.append(f"⑦ 正文 {n} 字｜代码/配置块 {blocks}｜清单条目 {lists}｜直接引语 {quote_count(body)} 处")

    return {"name": name, "todo": todo, "passed": passed, "info": info,
            "han": n, "density": blocks + lists, "quotes": quote_count(body), "heads": len(hs)}


def report(r):
    print("=" * 78)
    print(f"【{os.path.basename(r['name'])}】待改 {len(r['todo'])} 项")
    print("-" * 78)
    for x in r["passed"]:
        print(f"  通过  {x}")
    for x in r["todo"]:
        print(f"  待改  {x}")
    for x in r["info"]:
        print(f"  ·     {x}")
    print()


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    if args[0] == "--compare" and len(args) >= 3:
        ra, rb = check(read(args[1]), args[1]), check(read(args[2]), args[2])
        report(ra)
        report(rb)
        print("=" * 78)
        print(f"待改项：{len(ra['todo'])} → {len(rb['todo'])}")
        print(f"字数：{ra['han']} → {rb['han']}（{rb['han'] - ra['han']:+d}）"
              f"｜直接引语：{ra['quotes']} → {rb['quotes']}")
        print()
        print("⚠️ 这是待改清单，不是验收结论——契约禁止用无数据分数自我验收。")
        print("   剩下 3 条仍需过一遍：③ 判断前有无身份担保　④ 抽象后有无生活类比")
        print("   　　　　　　　　　　　　　⑤+ 读者的收获是多了还是少了（看内容，不比字数）")
    else:
        for p in args:
            if os.path.exists(p):
                report(check(read(p), p))
            else:
                print(f"跳过（不存在）：{p}")
