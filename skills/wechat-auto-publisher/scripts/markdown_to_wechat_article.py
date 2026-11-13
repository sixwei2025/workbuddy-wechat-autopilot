#!/usr/bin/env python3
"""
Markdown → 公众号草稿 JSON 转换器（汇芯红六套骨架版）

2026-11-02 排版切换：正文版式由单一红白模板改为「汇芯红六套骨架」
（来源 sixwei2025/ai-tool-review-wechat-skill 的 themes/），
一套 = 一组主题 token（容器/字号/行高/字距/色板/小标题形态/引用块形态）。
主题专属重装饰模块（开篇卡、头图卡、票据封面等）不在脚本内硬编码，
由排版官按 themes/references/theme-<id>.md 手工替换文章顶部那一块。

用法：
    python3 markdown_to_wechat_article.py --md a.md --title T --out a.json
    python3 markdown_to_wechat_article.py --md a.md --title T --theme journal --out a.json
    python3 markdown_to_wechat_article.py --list-themes
"""
from __future__ import annotations

import argparse
import datetime
import html
import json
import re
from pathlib import Path

FONT_SANS = (
    "-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB',"
    "'Microsoft YaHei',sans-serif"
)
FONT_SERIF = "'Noto Serif SC',Georgia,'Times New Roman','Songti SC',serif"

# ===== 六套骨架 token（数值取自 themes/references/theme-*.md 的「设计变量速查表」）=====
THEMES = {
    "magazine-card": {
        "name": "汇芯红·杂志卡",
        "scene": "教程、测评、清单、工具盘点（高密度卡片）",
        "font": FONT_SANS,
        "title_font": FONT_SANS,
        "body": "14px",
        "lh": "1.9",
        "ls": "0.5px",
        "ink": "#374151",
        "ink_lead": "#111827",
        "ink_title": "#111827",
        "grey": "#9CA3AF",
        "bg": "#ffffff",
        "pad": "20px",
        "red": "#C8102E",
        "red_deep": "#991B1B",
        "red_soft": "#FEF2F2",
        "hair": "#FECACA",
        "card_bg": "#F9FAFB",
        "card_bd": "#E5E7EB",
        "radius": "8px",
        "h2": "pill",
        "quote_bg": "#FEF2F2",
        "quote_bd": "border-left:3px solid {red};",
        "quote_radius": "border-radius:0 8px 8px 0;",
        "img_bd": "#E5E7EB",
        "img_radius": "8px",
        "code_bg": "#F3F4F6",
    },
    "classic-edit": {
        "name": "汇芯红·经典编辑",
        "scene": "深度分析、观点、力量感话题（引言卡＋编号章节）",
        "font": FONT_SANS,
        "title_font": FONT_SANS,
        "body": "15px",
        "lh": "1.8",
        "ls": "0.5px",
        "ink": "#374151",
        "ink_lead": "#1C1917",
        "ink_title": "#1C1917",
        "grey": "#9CA3AF",
        "bg": "#ffffff",
        "pad": "10px",
        "red": "#C8102E",
        "red_deep": "#991B1B",
        "red_soft": "#FEF2F2",
        "hair": "#FECACA",
        "card_bg": "#FAFAFA",
        "card_bd": "#E5E7EB",
        "radius": "6px",
        "h2": "bar",
        "quote_bg": "#FEF2F2",
        "quote_bd": "border-left:4px solid {red};",
        "quote_radius": "border-radius:0 8px 8px 0;",
        "img_bd": "#E5E7EB",
        "img_radius": "6px",
        "code_bg": "#F7F7F7",
    },
    "minimal-line": {
        "name": "汇芯红·极简细线",
        "scene": "设计、科技评论、专业观点（细线＋大留白）",
        "font": FONT_SANS,
        "title_font": FONT_SANS,
        "body": "15px",
        "lh": "1.8",
        "ls": "0.3px",
        "ink": "#52525B",
        "ink_lead": "#27272A",
        "ink_title": "#27272A",
        "grey": "#A1A1AA",
        "bg": "#FFFFFF",
        "pad": "10px",
        "red": "#C8102E",
        "red_deep": "#3F3F46",
        "red_soft": "#FAFAFA",
        "hair": "#E4E4E7",
        "card_bg": "#FAFAFA",
        "card_bd": "#E4E4E7",
        "radius": "4px",
        "h2": "hairline",
        "quote_bg": "#FAFAFA",
        "quote_bd": "border-left:3px solid {hair};",
        "quote_radius": "",
        "img_bd": "#E4E4E7",
        "img_radius": "4px",
        "code_bg": "#FAFAFA",
    },
    "zen-space": {
        "name": "汇芯红·禅意留白",
        "scene": "深度随笔、留白气质稿（衬线金句）",
        "font": FONT_SANS,
        "title_font": FONT_SERIF,
        "body": "15px",
        "lh": "1.9",
        "ls": "0.3px",
        "ink": "#525252",
        "ink_lead": "#2B2B2B",
        "ink_title": "#2B2B2B",
        "grey": "#A3A3A3",
        "bg": "#FFFFFF",
        "pad": "16px",
        "red": "#C8102E",
        "red_deep": "#2B2B2B",
        "red_soft": "#FFFFFF",
        "hair": "#E8E8E8",
        "card_bg": "#FAFAFA",
        "card_bd": "#E8E8E8",
        "radius": "2px",
        "h2": "serif",
        "quote_bg": "",
        "quote_bd": "border-top:1px solid {hair};border-bottom:1px solid {hair};",
        "quote_radius": "",
        "img_bd": "#E8E8E8",
        "img_radius": "2px",
        "code_bg": "#FAFAFA",
    },
    "ticket": {
        "name": "汇芯红·票据",
        "scene": "测评、工具对比（纸感＋硬阴影＋撕票线）",
        "font": FONT_SANS,
        "title_font": FONT_SANS,
        "body": "14px",
        "lh": "1.9",
        "ls": "0.5px",
        "ink": "#555555",
        "ink_lead": "#1a1a1a",
        "ink_title": "#1a1a1a",
        "grey": "#999999",
        "bg": "#fffef8",
        "pad": "20px",
        "red": "#C8102E",
        "red_deep": "#8B0A1F",
        "red_soft": "#FEF2F2",
        "hair": "#FECACA",
        "card_bg": "#FBF7EC",
        "card_bd": "#1a1a1a",
        "radius": "4px",
        "h2": "ticket",
        "quote_bg": "#FBF7EC",
        "quote_bd": "border:1px solid #1a1a1a;",
        "quote_radius": "border-radius:4px;",
        "img_bd": "#1a1a1a",
        "img_radius": "4px",
        "code_bg": "#F3F4F6",
    },
    "journal": {
        "name": "汇芯红·内刊手记",
        "scene": "深度评测、案例复盘、系统性说明（内刊头图）",
        "font": FONT_SANS,
        "title_font": FONT_SANS,
        "body": "14px",
        "lh": "1.9",
        "ls": "0.2px",
        "ink": "#4d4f46",
        "ink_lead": "#23251d",
        "ink_title": "#23251d",
        "grey": "#9ea096",
        "bg": "#fdfdf8",
        "pad": "8px",
        "red": "#C8102E",
        "red_deep": "#8B0A1F",
        "red_soft": "#F7F5EF",
        "hair": "#bfc1b7",
        "card_bg": "#eeefe9",
        "card_bd": "#bfc1b7",
        "radius": "6px",
        "h2": "journal",
        "quote_bg": "#F7F5EF",
        "quote_bd": "border-left:3px solid {red};",
        "quote_radius": "border-radius:0 6px 6px 0;",
        "img_bd": "#bfc1b7",
        "img_radius": "6px",
        "code_bg": "#f0f1ea",
    },
}

# rotation.md：一天一骨架，周一 → 周日
WEEKDAY_ROTATION = [
    "magazine-card",   # 周一
    "classic-edit",    # 周二
    "minimal-line",    # 周三
    "zen-space",       # 周四
    "ticket",          # 周五
    "journal",         # 周六
    "classic-edit",    # 周日：复用更贴题材的一套
]

_T = THEMES["classic-edit"]  # 兜底，main() 里按 --theme 覆盖


def _style(tpl: str) -> str:
    return tpl.format(**_T).strip()


def resolve_theme(name: str) -> str:
    """auto = 按当天星期轮换；其余必须是已注册 id。"""
    if not name or name.lower() == "auto":
        return WEEKDAY_ROTATION[datetime.date.today().weekday()]
    if name not in THEMES:
        raise SystemExit(
            f"unknown theme: {name}\n可选：{', '.join(THEMES)}；或 auto（按当天星期轮换）"
        )
    return name


def p_base() -> str:
    return f"font-family:{_T['font']};"


def inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(
        r"\[([^\]]+)\]\((https?://[^\s)]+)\)",
        rf'<a href="\2" style="color:{_T["red"]};">\1</a>',
        escaped,
    )
    return re.sub(
        r"\*\*(.+?)\*\*",
        rf'<strong style="color:{_T["red"]};font-weight:600;">\1</strong>',
        escaped,
    )


def body_lines(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line.strip() in {"## 正文", "# 正文"}:
            return lines[index + 1 :]
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                return lines[index + 1:]
        raise ValueError("Unclosed YAML frontmatter")
    return lines


# ===== 基础样式（全部按主题 token 取，不写死）=====
def p_style(lead: bool = False) -> str:
    color = _T["ink_lead"] if lead else _T["ink"]
    lh = _T["lh"]
    return (
        f"{p_base()}font-size:{_T['body']};color:{color};line-height:{lh};"
        f"letter-spacing:{_T['ls']};margin:0 {_T['pad']} 16px;"
    )


def h2_wrap_style() -> str:
    pad = _T["pad"]
    if _T["h2"] == "serif":
        return f"margin:64px {pad} 20px;padding:0;text-align:center;"
    return f"margin:40px {pad} 18px;padding:0;"


def key_style() -> str:
    bg = _T["quote_bg"]
    bg_css = f"background:{bg};" if bg else ""
    return (
        f"{p_base()}font-size:{_T['body']};color:{_T['ink']};line-height:1.85;"
        f"margin:20px {_T['pad']} 18px;padding:14px 16px;{bg_css}"
        f"{_style(_T['quote_bd'])}{_T['quote_radius']}"
    )


def card_style() -> str:
    return (
        f"{p_base()}font-size:{_T['body']};color:{_T['ink']};line-height:1.8;"
        f"margin:0 {_T['pad']} 10px;padding:13px 15px;background:{_T['card_bg']};"
        f"border:1px solid {_T['card_bd']};border-radius:{_T['radius']};"
    )


def code_style() -> str:
    mono = "'SF Mono',Consolas,Monaco,monospace"
    return (
        f"margin:20px {_T['pad']};padding:14px;background:{_T['code_bg']};"
        f"border:1px solid {_T['card_bd']};border-radius:{_T['radius']};"
        f"font-family:{mono};font-size:13px;line-height:1.7;color:{_T['ink']};"
        f"white-space:pre-wrap;"
    )


def caption_style() -> str:
    # 图说硬闸：12px + 灰 + 居中，禁止正文字号正文色冒充图注
    return (
        f"{p_base()}font-size:12px;color:{_T['grey']};text-align:center;"
        f"line-height:1.7;margin:8px {_T['pad']} 26px;"
    )


# ===== 组件（::: 容器语法，颜色随主题）=====
def quote_card_html(sentence: str) -> str:
    """引言卡：主题深色底白字金句，锚点层最强强调。"""
    return (
        f'<section style="margin:24px {_T["pad"]};padding:18px 20px;'
        f'background:{_T["red_deep"]};border-radius:{_T["radius"]};">'
        f'<p style="margin:0;{p_base()}font-size:17px;line-height:1.8;color:#ffffff;'
        f'font-weight:700;">{inline(sentence)}</p></section>'
    )


def stat_card_html(num: str, desc: str) -> str:
    return (
        f'<section style="margin:20px {_T["pad"]};padding:18px;background:{_T["card_bg"]};'
        f'border:1px solid {_T["card_bd"]};border-radius:{_T["radius"]};'
        f'display:flex;align-items:baseline;">'
        f'<p style="margin:0;flex:none;white-space:nowrap;{p_base()}font-size:34px;'
        f'font-weight:800;color:{_T["red"]};">'
        f'{inline(num)}</p>'
        f'<p style="margin:0 0 0 12px;{p_base()}font-size:14px;color:{_T["grey"]};'
        f'line-height:1.6;">{inline(desc)}</p></section>'
    )


def tag_card_html(tags: list[str]) -> str:
    spans = "".join(
        f'<span style="display:inline-block;background:{_T["red_soft"]};color:{_T["red"]};'
        f'font-size:13px;font-weight:700;padding:4px 12px;border-radius:20px;'
        f'margin:0 8px 8px 0;">{html.escape(t)}</span>' for t in tags
    )
    return f'<section style="margin:16px {_T["pad"]};{p_base()}">{spans}</section>'


def end_card_html(subtitle: str) -> str:
    return (
        f'<section style="margin:28px {_T["pad"]};padding:20px;background:{_T["ink_lead"]};'
        f'border-radius:{_T["radius"]};text-align:center;">'
        f'<p style="margin:0;{p_base()}font-size:18px;font-weight:800;color:{_T["red"]};'
        f'letter-spacing:2px;">END</p>'
        f'<p style="margin:8px 0 0;{p_base()}font-size:14px;color:#CCCCCC;line-height:1.7;">'
        f'{inline(subtitle)}</p></section>'
    )


def compare_card_html(left: tuple, right: tuple) -> str:
    lt, lc = left if left else ("", "")
    rt, rc = right if right else ("", "")
    return (
        f'<section style="margin:20px {_T["pad"]};display:flex;gap:12px;{p_base()}">'
        f'<section style="flex:1;padding:14px;background:{_T["card_bg"]};'
        f'border:1px solid {_T["card_bd"]};border-radius:{_T["radius"]};">'
        f'<p style="margin:0 0 6px;font-size:14px;font-weight:800;color:{_T["grey"]};">'
        f'{inline(lt)}</p>'
        f'<p style="margin:0;font-size:13px;color:{_T["ink"]};line-height:1.7;">'
        f'{inline(lc)}</p></section>'
        f'<section style="flex:1;padding:14px;background:{_T["red_soft"]};'
        f'border:1px solid {_T["hair"]};border-radius:{_T["radius"]};">'
        f'<p style="margin:0 0 6px;font-size:14px;font-weight:800;color:{_T["red"]};">'
        f'{inline(rt)}</p>'
        f'<p style="margin:0;font-size:13px;color:{_T["ink"]};line-height:1.7;">'
        f'{inline(rc)}</p></section></section>'
    )


def step_card_html(items: list[str]) -> str:
    blocks = []
    for i, item in enumerate(items, 1):
        blocks.append(
            f'<section style="display:flex;align-items:flex-start;margin-bottom:10px;">'
            f'<span style="flex:none;width:26px;height:26px;background:{_T["red"]};'
            f'color:#FFFFFF;font-size:14px;font-weight:800;border-radius:50%;'
            f'text-align:center;line-height:26px;margin-right:12px;{p_base()}">{i}</span>'
            f'<p style="margin:0;flex:1;{p_base()}font-size:{_T["body"]};color:{_T["ink"]};'
            f'line-height:1.7;">{inline(item)}</p></section>'
        )
    return f'<section style="margin:16px {_T["pad"]};{p_base()}">{"".join(blocks)}</section>'


def render_container(ctype: str, lines: list[str]) -> str:
    text = "\n".join(lines).strip()
    if ctype == "quote":
        sentence = " ".join(l.strip() for l in lines if l.strip())
        return quote_card_html(sentence)
    if ctype == "stat":
        first = lines[0].strip() if lines else ""
        num, desc = first.split("|", 1) if "|" in first else (first, "")
        return stat_card_html(num.strip(), desc.strip())
    if ctype == "tag":
        if "#" in text:
            tags = ["#" + t.strip() for t in text.split("#") if t.strip()]
        else:
            tags = [t for t in re.split(r"[\s,，]+", text) if t]
        return tag_card_html(tags)
    if ctype == "end":
        return end_card_html(text)
    if ctype == "compare":
        rows = [l for l in lines if l.strip()]
        left = tuple(x.strip() for x in rows[0].split("|", 1)) if rows and "|" in rows[0] else ("", "")
        right = tuple(x.strip() for x in rows[1].split("|", 1)) if len(rows) >= 2 and "|" in rows[1] else ("", "")
        return compare_card_html(left, right)
    if ctype == "step":
        items = [re.sub(r"^\d+\.\s+", "", l).strip() for l in lines if re.match(r"^\d+\.\s+", l.strip())]
        return step_card_html(items)
    return paragraph_html(text)


def _split_inline_container(inner: str) -> tuple[str, list[str]]:
    m = inner.split(None, 1)
    ctype = m[0].lower() if m else ""
    ctext = m[1] if len(m) > 1 else ""
    if ctype == "compare":
        cols = [c.strip() for c in re.split(r"\s*/\s*", ctext) if c.strip()]
        return ctype, cols
    if ctype == "step":
        items = [it.strip() for it in re.split(r"(?=\d+\.\s+)", ctext) if re.match(r"\d+\.\s+", it.strip())]
        return ctype, items
    return ctype, [ctext]


QUOTE_LINES = {
    "客户买的从来不是软件。",
    "客户买的是“终于有人把这件事给我弄明白了”。",
    "先收资料，后做秩序。",
    "工具再强，如果没有记忆，它也只是一个聪明的陌生人。",
}


# ===== 小标题：按主题形态（pill / bar / hairline / serif / ticket / journal）=====
def h2_html(title: str, index: int) -> str:
    match = re.match(r"^(\d{2})\s*(.+)$", title)
    number, text = match.groups() if match else (f"{index:02d}", title)
    wrap = h2_wrap_style()
    kind = _T["h2"]
    red, deep, soft, hair = _T["red"], _T["red_deep"], _T["red_soft"], _T["hair"]
    size = "16px"

    if kind == "pill":
        label = (
            f'<span style="display:inline-block;background:{soft};color:{deep};'
            f'font-size:12px;font-weight:900;padding:2px 9px;border-radius:5px;'
            f'margin-right:8px;vertical-align:2px;">{html.escape(number)}</span>'
        )
        body = (
            f'<span style="{p_base()}font-size:{size};line-height:1.5;color:{_T["ink_title"]};'
            f'font-weight:800;">{inline(text)}</span>'
        )
    elif kind == "bar":
        label = (
            f'<span style="display:inline-block;width:4px;height:17px;background:{red};'
            f'border-radius:2px;margin-right:10px;vertical-align:-2px;">'
            f'<span leaf=""><br></span></span>'
        )
        body = (
            f'<span style="{p_base()}font-size:17px;line-height:1.5;color:{_T["ink_title"]};'
            f'font-weight:800;">{inline(text)}</span>'
        )
    elif kind == "hairline":
        label = (
            f'<span style="{p_base()}font-size:12px;color:{_T["grey"]};'
            f'letter-spacing:2px;margin-right:10px;">{html.escape(number)}</span>'
        )
        body = (
            f'<span style="{p_base()}font-size:{size};line-height:1.5;color:{_T["ink_title"]};'
            f'font-weight:700;">{inline(text)}</span>'
        )
        wrap = f"margin:56px {_T['pad']} 18px;padding:14px 0 0;border-top:1px solid {hair};"
    elif kind == "serif":
        label = ""
        body = (
            f'<span style="{p_base()}font-family:{_T["title_font"]};font-size:19px;'
            f'line-height:1.6;color:{_T["ink_title"]};font-weight:600;letter-spacing:1px;">'
            f'{inline(text)}</span>'
        )
    elif kind == "ticket":
        label = (
            f'<span style="display:inline-block;background:{_T["ink_title"]};color:#fffef8;'
            f'{p_base()}font-size:12px;font-weight:800;padding:2px 8px;'
            f'border-radius:2px;margin-right:9px;vertical-align:2px;">'
            f'{html.escape(number)}</span>'
        )
        body = (
            f'<span style="{p_base()}font-size:16px;line-height:1.5;color:{_T["ink_title"]};'
            f'font-weight:800;">{inline(text)}</span>'
        )
    else:  # journal
        label = ""
        body = (
            f'<span style="display:inline-block;{p_base()}font-size:18px;line-height:1.5;'
            f'color:{_T["ink_title"]};font-weight:800;border-bottom:2px solid {red};'
            f'padding-bottom:3px;">{inline(text)}</span>'
        )
    return f'<h2 style="{wrap}">{label}{body}</h2>'


def image_html(image: str) -> str:
    escaped = html.escape(image)
    return (
        f'<p style="text-align:center;margin:22px {_T["pad"]} 0;">'
        f'<img src="{escaped}" alt="正文配图" '
        f'style="max-width:100%;height:auto;border-radius:{_T["img_radius"]};display:block;'
        f'margin:0 auto;border:1px solid {_T["img_bd"]};" /></p>'
    )


def paragraph_html(text: str, *, lead: bool = False) -> str:
    return f'<p style="{p_style(lead)}">{inline(text)}</p>'


def quote_html(text: str) -> str:
    return f'<section style="{key_style()}"><p style="margin:0;">{inline(text)}</p></section>'


def bullet_row_html(text: str, margin: str, *, size: str | None = None) -> str:
    size = size or _T["body"]
    return (
        f'<p style="{p_base()}font-size:{size};color:{_T["ink"]};line-height:1.85;'
        f'letter-spacing:{_T["ls"]};margin:{margin};padding-left:18px;text-indent:-18px;">'
        f'<span style="color:{_T["red"]};font-size:11px;font-weight:800;">●</span>&nbsp;'
        f'{inline(text)}</p>'
    )


def bullets_html(items: list[str]) -> str:
    rows = []
    for index, item in enumerate(items):
        top = 14 if index == 0 else 0
        bottom = 0 if index == len(items) - 1 else 8
        rows.append(bullet_row_html(item, f"{top}px {_T['pad']} {bottom}px"))
    return "\n".join(rows)


def quote_block_html(values: list[str]) -> str:
    items: list[str] = []
    for value in values:
        match = re.match(r"^[-*]\s+(.+)$", value.strip())
        if not match:
            items = []
            break
        items.append(match.group(1))
    if items:
        rows = []
        for index, item in enumerate(items):
            bottom = 0 if index == len(items) - 1 else 8
            rows.append(bullet_row_html(item, f"0 0 {bottom}px"))
        return f'<section style="{key_style()}">' + "".join(rows) + "</section>"
    # 引用块内逐行渲染，保留 **加粗** → 品牌红 strong；不再用 pre-wrap 一次性输出
    lines = [v.strip() for v in values if v.strip()]
    rows = []
    for index, line in enumerate(lines):
        bottom = 0 if index == len(lines) - 1 else 12
        rows.append(
            f'<p style="margin:0 0 {bottom}px;{p_base()}font-size:{_T["body"]};'
            f'color:{_T["ink"]};line-height:1.85;">{inline(line)}</p>'
        )
    return f'<section style="{key_style()}">' + "".join(rows) + "</section>"

def _render_takeaway_card(lines: list[str]) -> str | None:
    """将【原件 X · 标题】或【...卡/表/清单】代码块渲染为精致、紧凑的结构化原生卡片，告别臃肿的灰底 pre-wrap 大段折行。"""
    non_empty = [l.strip() for l in lines if l.strip()]
    if not non_empty:
        return None
    first = re.sub(r"^#\s*", "", non_empty[0])
    m_title = re.match(r"^【(.+?)】$", first)
    if not m_title:
        return None

    raw_title = m_title.group(1).strip()
    if "·" in raw_title:
        badge, card_title = [x.strip() for x in raw_title.split("·", 1)]
    else:
        badge, card_title = "可复制卡", raw_title

    body_lines = [l.rstrip() for l in lines[lines.index(next(l for l in lines if l.strip())) + 1 :] if l.strip()]

    has_commands = any(
        not l.strip().startswith(("#", "1", "2", "3", "4", "5", "6", "7", "▸", "✓", "✗", "第"))
        and re.match(r"^[a-zA-Z0-9_./$-]+", l.strip())
        for l in body_lines
    )

    mono = "'SF Mono',Consolas,Monaco,monospace"
    rows_html: list[str] = []

    if has_commands:
        cmd_buf: list[str] = []

        def flush_cmds() -> None:
            if not cmd_buf:
                return
            cmd_ps = []
            for idx_c, c in enumerate(cmd_buf):
                bdr = "border-top:1px solid #334155;padding-top:6px;margin-top:6px;" if idx_c > 0 else ""
                cmd_ps.append(
                    f'<section style="{bdr}font-family:{mono};font-size:12px;line-height:1.55;color:#F8FAFC;word-break:break-all;">'
                    f'<span style="color:#F87171;font-weight:700;margin-right:6px;"><span leaf="">$</span></span>'
                    f'<span leaf="">{html.escape(c)}</span></section>'
                )
            rows_html.append(
                f'<section style="margin:4px 0 6px;padding:10px 12px;background:#1E293B;border-radius:6px;">{"".join(cmd_ps)}</section>'
            )
            cmd_buf.clear()

        for raw_l in body_lines:
            s = raw_l.strip()
            if s.startswith("#"):
                flush_cmds()
                comment = s.lstrip("#").strip()
                if not comment:
                    continue
                rows_html.append(
                    f'<section style="margin:6px 0 2px;font-size:12.5px;line-height:1.6;color:{_T["ink_lead"]};font-weight:700;">'
                    f'<span leaf="">{inline(comment)}</span></section>'
                )
            else:
                cmd_buf.append(s)
        flush_cmds()
    else:
        for raw_l in body_lines:
            s = raw_l.strip()
            m_num = re.match(r"^(?:(\d+)[.、\s]+|(第[一二三四五六七八九十]+步)\s*·?\s*)(.+)$", s)
            if m_num:
                num_tag = m_num.group(1) or m_num.group(2)
                rest = m_num.group(3).strip()
                border_top = "border-top:1px solid #F3F4F6;padding-top:9px;margin-top:9px;" if rows_html else ""
                if "→" in rest:
                    k, v = [x.strip() for x in rest.split("→", 1)]
                    rows_html.append(
                        f'<section style="{border_top}display:flex;align-items:baseline;">'
                        f'<span style="flex:none;display:inline-block;background:{_T["red_soft"]};color:{_T["red"]};'
                        f'font-size:11px;font-weight:800;padding:1px 6px;border-radius:4px;margin-right:7px;">'
                        f'<span leaf="">{html.escape(num_tag)}</span></span>'
                        f'<section style="flex:1;font-size:13px;line-height:1.65;color:{_T["ink"]};">'
                        f'<span style="color:{_T["ink_lead"]};font-weight:700;"><span leaf="">{inline(k)}</span></span>'
                        f'<span style="color:{_T["grey"]};"><span leaf=""> · </span></span>'
                        f'<span leaf="">{inline(v)}</span></section></section>'
                    )
                else:
                    rows_html.append(
                        f'<section style="{border_top}display:flex;align-items:center;margin-bottom:3px;">'
                        f'<span style="flex:none;display:inline-block;background:{_T["red"]};color:#ffffff;'
                        f'font-size:11px;font-weight:800;padding:1px 6px;border-radius:4px;margin-right:7px;">'
                        f'<span leaf="">{html.escape(num_tag)}</span></span>'
                        f'<span style="font-size:13.5px;color:{_T["ink_lead"]};font-weight:800;">'
                        f'<span leaf="">{inline(rest)}</span></span></section>'
                    )
                continue

            if s.startswith(("▸", "✓", "✗", "-", "•")):
                marker = s[0]
                rest = s[1:].strip()
                m_color = _T["red"] if marker in ("▸", "✓") else _T["grey"]
                if "→" in rest:
                    k, v = [x.strip() for x in rest.split("→", 1)]
                    rows_html.append(
                        f'<section style="padding-left:8px;margin-top:3px;font-size:12.5px;line-height:1.65;color:{_T["ink"]};">'
                        f'<span style="color:{m_color};font-weight:800;margin-right:4px;"><span leaf="">{html.escape(marker)}</span></span>'
                        f'<span style="color:{_T["grey"]};"><span leaf="">{inline(k)}：</span></span>'
                        f'<span style="color:{_T["ink_lead"]};font-weight:600;"><span leaf="">{inline(v)}</span></span></section>'
                    )
                else:
                    rows_html.append(
                        f'<section style="padding-left:8px;margin-top:3px;font-size:12.5px;line-height:1.65;color:{_T["ink"]};">'
                        f'<span style="color:{m_color};font-weight:800;margin-right:4px;"><span leaf="">{html.escape(marker)}</span></span>'
                        f'<span leaf="">{inline(rest)}</span></section>'
                    )
                continue

            if "→" in s:
                k, v = [x.strip() for x in s.split("→", 1)]
                border_top = "border-top:1px solid #F3F4F6;padding-top:8px;margin-top:8px;" if rows_html else ""
                rows_html.append(
                    f'<section style="{border_top}font-size:13px;line-height:1.65;color:{_T["ink"]};">'
                    f'<span style="color:{_T["ink_lead"]};font-weight:700;"><span leaf="">{inline(k)}</span></span>'
                    f'<span style="color:{_T["red"]};font-weight:700;"><span leaf=""> → </span></span>'
                    f'<span leaf="">{inline(v)}</span></section>'
                )
            else:
                rows_html.append(
                    f'<section style="margin-top:4px;font-size:12.5px;line-height:1.65;color:{_T["grey"]};">'
                    f'<span leaf="">{inline(s)}</span></section>'
                )

    return (
        f'<section data-takeaway="1" style="margin:18px {_T["pad"]} 22px;background:#ffffff;'
        f'border:1px solid {_T["card_bd"]};border-top:3px solid {_T["red"]};border-radius:8px;'
        f'box-shadow:0 2px 10px rgba(0,0,0,0.03);overflow:hidden;{p_base()}">'
        f'<section style="padding:9px 14px;background:{_T["red_soft"]};border-bottom:1px solid {_T["hair"]};'
        f'display:flex;align-items:center;justify-content:space-between;">'
        f'<section style="display:flex;align-items:center;min-width:0;flex:1;">'
        f'<span style="flex:none;display:inline-block;background:{_T["red"]};color:#ffffff;font-size:10px;font-weight:800;'
        f'padding:2px 7px;border-radius:4px;margin-right:8px;letter-spacing:0.5px;white-space:nowrap;"><span leaf="">{html.escape(badge)}</span></span>'
        f'<span style="font-size:13.5px;color:{_T["ink_title"]};font-weight:800;line-height:1.4;"><span leaf="">{html.escape(card_title)}</span></span>'
        f'</section>'
        f'<span style="flex:none;font-size:10px;color:{_T["grey"]};margin-left:8px;white-space:nowrap;"><span leaf="">可复制</span></span>'
        f'</section>'
        f'<section style="padding:12px 14px;">{"".join(rows_html)}</section>'
        f'</section>'
    )


def code_block_html(values: list[str]) -> str:
    card = _render_takeaway_card(values)
    if card is not None:
        return card
    mono = "'SF Mono',Consolas,Monaco,monospace"
    rows = []
    for raw in values:
        if not raw.strip():
            continue
        s = raw.strip()
        if s.startswith("#"):
            rows.append(
                f'<section style="margin:4px 0 2px;font-family:{mono};font-size:12px;line-height:1.6;color:#94A3B8;">'
                f'<span leaf="">{html.escape(s)}</span></section>'
            )
        else:
            rows.append(
                f'<section style="margin:0;font-family:{mono};font-size:12.5px;line-height:1.65;color:#F8FAFC;word-break:break-all;">'
                f'<span leaf="">{html.escape(raw)}</span></section>'
            )
    return (
        f'<section data-takeaway="1" style="margin:18px {_T["pad"]} 22px;border-radius:8px;overflow:hidden;'
        f'background:#1E293B;border:1px solid #0F172A;">'
        f'<section style="display:flex;align-items:center;justify-content:space-between;padding:7px 12px;background:#0F172A;">'
        f'<section style="display:flex;align-items:center;">'
        f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#FF5F56;margin-right:6px;"><span leaf=""><br></span></span>'
        f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#FFBD2E;margin-right:6px;"><span leaf=""><br></span></span>'
        f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#27C93F;"><span leaf=""><br></span></span>'
        f'</section>'
        f'<span style="font-size:10px;color:#94A3B8;font-family:{mono};"><span leaf="">TERMINAL</span></span>'
        f'</section>'
        f'<section style="padding:10px 14px;">{"".join(rows)}</section>'
        f'</section>'
    )


def card_html(text: str) -> str | None:
    match = re.match(
        r"^(第一|第二|第三|第四|第五|第一个门槛|第二个门槛|第三个门槛|第一档|第二档|第三档)，(.+)$",
        text,
    )
    if not match:
        return None
    label, rest = match.groups()
    return (
        f'<p style="{card_style()}"><span style="color:{_T["red"]};font-weight:800;">'
        f'{html.escape(label)}</span>，{inline(rest)}</p>'
    )


def container_html() -> str:
    return (
        f'<section style="max-width:677px;margin:0 auto;background:{_T["bg"]};'
        f'font-family:{_T["font"]};color:{_T["ink"]};font-size:{_T["body"]};'
        f'line-height:{_T["lh"]};letter-spacing:{_T["ls"]};overflow-x:hidden;">'
    )


def convert_markdown(lines: list[str], images: list[str] | None) -> str:
    parts = [container_html()]
    images = images or []
    section_count = 0
    in_intro = True
    buffer: list[str] = []
    quote: list[str] = []
    code: list[str] = []
    bullets: list[str] = []
    in_code = False
    placed: set[str] = set()
    in_container = False
    container_type: str | None = None
    container_lines: list[str] = []

    def flush() -> None:
        nonlocal buffer
        if not buffer:
            return
        text = "".join(buffer).strip()
        buffer.clear()
        if not text:
            return
        if text == "---":
            parts.append(
                f'<hr style="border:none;border-top:1px solid {_T["hair"]};'
                f'margin:32px {_T["pad"]};">'
            )
            return
        card = card_html(text)
        if card:
            parts.append(card)
        elif text in QUOTE_LINES:
            parts.append(quote_html(text))
        else:
            parts.append(paragraph_html(text, lead=in_intro))

    def flush_quote() -> None:
        if quote:
            parts.append(quote_block_html(quote))
            quote.clear()

    def flush_code() -> None:
        if code:
            parts.append(code_block_html(code))
            code.clear()

    def flush_bullets() -> None:
        if bullets:
            parts.append(bullets_html(bullets))
            bullets.clear()

    def flush_all() -> None:
        flush()
        flush_bullets()
        flush_quote()

    def flush_container() -> None:
        nonlocal container_lines
        if not in_container:
            return
        ctype = container_type
        content = container_lines
        container_lines = []
        rendered = render_container(ctype, content)
        if rendered:
            parts.append(rendered)

    for raw in lines:
        line = raw.strip()
        if line.startswith(":::"):
            if in_container:
                flush_container()
                in_container = False
                container_type = None
                continue
            flush_all()
            if line.rstrip().endswith(":::") and len(line.strip()) > 3:
                ctype, clines = _split_inline_container(line.strip()[3:-3].strip())
                rendered = render_container(ctype, clines)
                if rendered:
                    parts.append(rendered)
                continue
            in_container = True
            container_type = line[3:].strip().lower()
            container_lines = []
            continue
        if in_container:
            container_lines.append(raw)
            continue
        if line.startswith("```"):
            flush_all()
            if in_code:
                flush_code()
            in_code = not in_code
            continue
        if in_code:
            code.append(raw)
            continue
        if line.startswith(">"):
            flush()
            flush_bullets()
            quote.append(line[1:].lstrip())
            continue
        flush_quote()
        pic = re.fullmatch(r"!\[([^\]]*)\]\(([^\s)]+)\)|\[\[img:([^\]]+)\]\]", line)
        if pic:
            flush_all()
            caption, source, legacy = pic.groups()
            source = source or legacy
            if source.startswith(("javascript:", "data:", "file:")):
                raise ValueError("Unsupported image source")
            parts.append(image_html(source))
            placed.add(source)
            if caption:
                parts.append(f'<p style="{caption_style()}">{inline(caption)}</p>')
            continue
        if re.fullmatch(r"（[^）]{2,45}）|\([^)]{2,45}\)", line) and parts:
            if "<img " in parts[-1]:
                cap_txt = line[1:-1].strip()
                parts.append(f'<p style="{caption_style()}">{inline(cap_txt)}</p>')
                continue
            if len(parts) >= 2 and "<img " in parts[-2] and 'text-align:center' in parts[-1]:
                cap_txt = line[1:-1].strip()
                parts[-1] = f'<p style="{caption_style()}">{inline(cap_txt)}</p>'
                continue
        if not line or line.startswith("- ["):
            flush_all()
            continue
        if line.startswith("# "):
            continue
        if line.startswith("## "):
            flush_all()
            in_intro = False
            section_count += 1
            parts.append(h2_html(line[3:].strip(), section_count))
            continue
        if re.match(r"^\d+\.\s+", line):
            flush_all()
            parts.append(f'<p style="{card_style()}">{inline(line)}</p>')
            continue
        if re.match(r"^[-*]\s+", line):
            flush()
            bullets.append(re.sub(r"^[-*]\s+", "", line))
            continue
        buffer.append(line)
    flush_all()
    flush_container()
    if in_container:
        raise ValueError("Unclosed container ::: (missing closing :::)")
    if in_code:
        raise ValueError("Unclosed code fence")
    unplaced = [
        src for src in images
        if src not in placed and Path(src).name not in {Path(p).name for p in placed}
    ]
    if unplaced:
        raise ValueError("Images need explicit Markdown placement: " + ", ".join(unplaced))
    parts.append("</section>")
    return "\n".join(parts)


def print_themes() -> None:
    today = WEEKDAY_ROTATION[datetime.date.today().weekday()]
    print(f"今日默认骨架：{today}（{THEMES[today]['name']}）\n")
    print(f"{'id':<16}{'中文名':<18}{'适用场景'}")
    for tid, t in THEMES.items():
        mark = " ←今日" if tid == today else ""
        print(f"{tid:<16}{t['name']:<18}{t['scene']}{mark}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a public-safe Markdown article into WeChat draft JSON.")
    parser.add_argument("--md")
    parser.add_argument("--title")
    parser.add_argument("--author", default="袁六伟")
    parser.add_argument("--digest", default="")
    parser.add_argument("--source-url", default="")
    parser.add_argument("--content-image", action="append", default=[])
    parser.add_argument("--out")
    parser.add_argument("--theme", default="auto",
                        help="magazine-card | classic-edit | minimal-line | zen-space | ticket | journal | auto（按星期轮换）")
    parser.add_argument("--list-themes", action="store_true", help="打印六套骨架与今日默认，不做转换")
    args = parser.parse_args()

    if args.list_themes:
        print_themes()
        return
    if not args.md or not args.title or not args.out:
        parser.error("--md / --title / --out 必填（或用 --list-themes 只看骨架）")

    global _T
    tid = resolve_theme(args.theme)
    _T = THEMES[tid]

    article = {
        "title": args.title,
        "author": args.author,
        "digest": args.digest[:120],
        "content": convert_markdown(body_lines(Path(args.md)), args.content_image),
        "content_source_url": args.source_url,
        "need_open_comment": 0,
        "only_fans_can_comment": 0,
        "pic_crop_235_1": "0_0_1_1",
        "pic_crop_1_1": "0.287_0_0.713_1",
    }
    Path(args.out).write_text(json.dumps(article, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "theme": tid, "theme_name": _T["name"], "out": args.out}, ensure_ascii=False))


if __name__ == "__main__":
    main()
