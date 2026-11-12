#!/usr/bin/env python3
"""把 markdown_to_wechat_article.py 产出的「基础版式」补成完整骨架。

转换器只负责 token 化版式；主题专属的开篇封面 / 目录 / 章节标题 / END
必须按 theme-<id>.md 组件装配。本脚本支持全部 6 套汇芯红骨架：
  magazine-card | classic-edit | minimal-line | zen-space | ticket | journal

用法:
  python3 scripts/apply_theme_shell.py --article <json> --theme <id> --out <json>
"""
import argparse, json, re, sys
from pathlib import Path

LEAF = '<span leaf="">'
THEMES = ('magazine-card', 'classic-edit', 'minimal-line', 'zen-space', 'ticket', 'journal')


def cover_magazine(date, parts, *, eyebrow='三个月的实操复盘', strike='装个工具就能撒手不管',
                   black='把活', red1='交出去', red2='把判断留下来',
                   meta='1800 多份 · 13 张真图 · 三张能带走的纸',
                   foot='一人公司 · 三个月实操', tag1='复盘', tag2='可带走'):
    toc = []
    for i, (short, sub) in enumerate(parts):
        first = i == 0
        bg = '#C8102E' if first else '#fff'
        bd = 'none' if first else '1px solid #E5E7EB'
        c1 = 'rgba(255,255,255,0.7)' if first else '#9CA3AF'
        c2 = '#fff' if first else '#111827'
        c3 = 'rgba(255,255,255,0.7)' if first else '#9CA3AF'
        label = 'PART %02d' % (i + 1) if i < len(parts) - 1 else 'PART ///'
        toc.append(
            f'<section style="display:inline-block;white-space:normal;vertical-align:top;width:128px;background:{bg};border:{bd};border-radius:12px;padding:12px;margin-right:8px;box-shadow:0 2px 6px rgba(0,0,0,0.04);">'
            f'<p style="font-size:9px;font-weight:700;color:{c1};letter-spacing:1px;margin:0 0 5px;">{LEAF}{label}</span></p>'
            f'<p style="font-size:13px;font-weight:800;color:{c2};margin:0 0 3px;">{LEAF}{short}</span></p>'
            f'<p style="font-size:10px;color:{c3};margin:0;">{LEAF}{sub}</span></p></section>'
        )
    return (
        '<section style="margin:0 0 28px;background:#fff;border:1.5px solid rgba(200,16,46,0.15);border-radius:20px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.06);width:100%;">'
        '<section style="padding:28px 26px 24px;">'
        '<section style="display:flex;align-items:center;gap:8px;margin-bottom:24px;">'
        f'<span style="width:6px;height:6px;background:#C8102E;border-radius:50%;">{LEAF}<br></span></span>'
        f'<span style="font-size:11px;font-weight:700;letter-spacing:3px;color:#C8102E;">{LEAF}{eyebrow}</span></span>'
        f'<section style="flex:1;height:1px;overflow:hidden;background:#FEE2E2;">{LEAF}<br></span></section>'
        f'<span style="font-size:10px;color:#D1D5DB;font-weight:600;">{LEAF}{date}</span></span></section>'
        '<p style="font-size:15px;color:#D1D5DB;margin:0 0 6px;text-decoration:line-through;letter-spacing:0.5px;">'
        f'{LEAF}{strike}</span></p>'
        '<p style="font-size:24px;font-weight:900;color:#111827;margin:0;line-height:1.05;letter-spacing:-2px;">'
        f'{LEAF}{black}</span><span style="color:#C8102E;">{LEAF}{red1}</span></span></p>'
        '<p style="font-size:24px;font-weight:900;color:#C8102E;margin:0 0 14px;line-height:1.05;letter-spacing:-2px;">'
        f'{LEAF}{red2}</span></p>'
        f'<section style="width:48px;height:3px;background:#C8102E;border-radius:2px;margin-bottom:12px;">{LEAF}<br></span></section>'
        '<p style="font-size:13px;color:#9CA3AF;margin:0;line-height:1.7;letter-spacing:0.5px;">'
        f'{LEAF}{meta}</span></p></section>'
        '<section style="background:#C8102E;padding:12px 26px;display:flex;align-items:center;justify-content:space-between;">'
        f'<p style="font-size:12px;color:#fff;margin:0;font-weight:600;letter-spacing:0.5px;">{LEAF}{foot}</span></p>'
        f'<section style="display:flex;gap:4px;"><span style="background:rgba(255,255,255,0.2);padding:1px 6px;border-radius:3px;font-size:8px;color:#fff;font-weight:600;">{LEAF}{tag1}</span></span>'
        f'<span style="background:rgba(255,255,255,0.2);padding:1px 6px;border-radius:3px;font-size:8px;color:#fff;font-weight:600;">{LEAF}{tag2}</span></span></section></section></section>'
        + '<section style="margin:0 20px 30px;">'
        + '<section style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">'
        + f'<p style="font-size:10px;color:#9CA3AF;margin:0;text-transform:uppercase;letter-spacing:2px;font-weight:600;">{LEAF}{max(1, len(parts)-1)} Parts + Conclusion</span></p>'
        + f'<p style="font-size:10px;color:#9CA3AF;margin:0;">{LEAF}滑动</span></p></section>'
        + '<section style="overflow-x:scroll;-webkit-overflow-scrolling:touch;white-space:nowrap;padding-bottom:8px;">'
        + ''.join(toc) + '</section></section>'
    )


def cover_classic_edit(parts, *, black='把活', red1='交出去', red2='把判断留下来', eyebrow='三个月的实操复盘'):
    top3 = parts[:3] if len(parts) >= 3 else (parts + [('核心看点', '01'), ('实战拆解', '02'), ('交付清单', '03')])[:3]
    cards = []
    for i, (short, _) in enumerate(top3):
        mr = 'margin-right:8px;' if i < 2 else ''
        cards.append(
            f'<section style="flex:1;background:#FEF2F2;border-radius:10px;padding:16px 12px;{mr}text-align:center;border:1px solid #FEE2E2;">'
            f'<p style="display:inline-block;background:#C8102E;color:#FFFFFF;font-size:12px;font-weight:800;padding:2px 10px;border-radius:4px;margin:0 0 8px;">{LEAF}0{i+1}</span></p>'
            f'<p style="font-size:13px;font-weight:700;color:#1C1917;margin:0;">{LEAF}{short}</span></p></section>'
        )
    return (
        '<section style="margin:10px 10px 32px;background:#ffffff;border-radius:12px;box-shadow:0 4px 24px -4px rgba(200,16,46,0.15);padding:28px 24px 22px;overflow:hidden;">'
        f'<p style="font-size:42px;color:#C8102E;font-weight:900;margin:0;line-height:0.6;">{LEAF}"</span></p>'
        '<p style="font-size:16px;font-weight:800;color:#1C1917;margin:12px 0 8px;line-height:1.75;padding-left:4px;">'
        f'<span style="background:#C8102E;color:#FFFFFF;padding:2px 8px;border-radius:4px;margin-right:6px;">{LEAF}{black}{red1}</span></span>'
        f'{LEAF}{red2}。</span></p>'
        f'<p style="text-align:right;font-size:12px;color:#9CA3AF;margin:8px 0 0;letter-spacing:1px;">{LEAF}— {eyebrow}</span></p></section>'
        '<section style="padding:0 10px 32px;">'
        f'<p style="font-size:13px;color:#9CA3AF;margin:0 0 14px;letter-spacing:1px;">{LEAF}本文看点</span></p>'
        '<section style="display:flex;justify-content:space-between;">' + ''.join(cards) + '</section></section>'
    )


def cover_minimal_line(parts, *, black='把活', red1='交出去', red2='把判断留下来', eyebrow='极简细线'):
    top3 = parts[:3] if len(parts) >= 3 else (parts + [('结构保留', '01'), ('关键判断', '02'), ('极简锚点', '03')])[:3]
    cards = []
    for i, (short, _) in enumerate(top3):
        mr = 'margin-right:8px;' if i < 2 else ''
        cards.append(
            f'<section style="flex:1;background:#FAFAFA;border-top:1px solid #E4E4E7;padding:18px 12px 16px;{mr}">'
            f'<p style="font-size:11px;color:#A1A1AA;font-weight:500;margin:0 0 8px;letter-spacing:1px;">{LEAF}0{i+1}</span></p>'
            f'<p style="font-size:13px;font-weight:700;color:#27272A;margin:0;line-height:1.5;">{LEAF}{short}</span></p></section>'
        )
    return (
        '<section style="margin:10px 10px 40px;padding:32px 24px 24px;border-top:1px solid #E4E4E7;border-bottom:1px solid #E4E4E7;background:#FFFFFF;">'
        f'<p style="font-size:11px;color:#A1A1AA;letter-spacing:2px;margin:0 0 18px;font-weight:400;">{LEAF}QUOTE / MINIMAL-LINE</span></p>'
        '<p style="font-size:18px;font-weight:700;color:#27272A;margin:0 0 8px;line-height:1.7;letter-spacing:0.5px;">'
        f'{LEAF}{black}{red1}，</span><span style="border-bottom:2px solid #C8102E;">{LEAF}{red2}</span></span>{LEAF}。</span></p>'
        f'<p style="text-align:right;font-size:12px;color:#A1A1AA;margin:16px 0 0;letter-spacing:1px;">{LEAF}— {eyebrow}</span></p></section>'
        '<section style="padding:0 10px 40px;">'
        f'<p style="font-size:11px;color:#A1A1AA;margin:0 0 16px;letter-spacing:2px;">{LEAF}LOOK AHEAD</span></p>'
        '<section style="display:flex;justify-content:space-between;">' + ''.join(cards) + '</section></section>'
    )


def cover_zen_space(parts, *, black='把活', red1='交出去', red2='把判断留下来', eyebrow='禅意留白'):
    top3 = parts[:3] if len(parts) >= 3 else (parts + [('第一要点', '01'), ('第二要点', '02'), ('第三要点', '03')])[:3]
    rows = []
    for i, (short, _) in enumerate(top3):
        rows.append(f'<p style="font-size:13px;color:#2B2B2B;margin:0 0 10px;line-height:1.6;">{LEAF}0{i+1} {short}</span></p>')
    return (
        '<section style="margin:32px 16px 48px;padding:40px 24px;border-top:1px solid #E8E8E8;border-bottom:1px solid #E8E8E8;text-align:center;">'
        '<p style="font-family:\'Noto Serif SC\',Georgia,serif;font-size:20px;font-weight:700;color:#2B2B2B;margin:0 0 20px;line-height:1.85;letter-spacing:0.8px;">'
        f'{LEAF}{black}{red1}，{red2}。</span></p>'
        f'<section style="width:40px;height:1px;background:#C8102E;margin:0 auto 14px;">{LEAF}<br></span></section>'
        f'<p style="font-size:12px;color:#A3A3A3;margin:0;letter-spacing:1.5px;">{LEAF}{eyebrow}</span></p></section>'
        '<section style="padding:0 16px 40px;">'
        f'<p style="font-size:10px;color:#C8102E;font-weight:700;margin:0 0 14px;letter-spacing:3px;">{LEAF}CONTENTS</span></p>'
        + ''.join(rows) + '</section>'
    )


def cover_ticket(*, black='把活', red1='交出去', red2='把判断留下来', eyebrow='三个月的实操复盘', meta='1800 多份 · 13 张真图', tag1='实战', tag2='可带走'):
    return (
        '<section style="background:#fffef8;border:2px solid #1a1a1a;box-shadow:4px 4px 0 #1a1a1a;margin:0 10px 32px;">'
        '<section style="background:#C8102E;padding:12px 20px;display:flex;justify-content:space-between;align-items:center;">'
        f'<section style="color:#fffef8;font-size:11px;letter-spacing:4px;font-weight:700;">{LEAF}HUIXIN PASS</span></section>'
        f'<section style="color:#fffef8;font-size:11px;letter-spacing:2px;">{LEAF}★★★★★</span></section></section>'
        '<section style="display:flex;">'
        '<section style="flex:1;padding:24px 20px;border-right:2px dashed #FECACA;">'
        f'<section style="font-size:22px;font-weight:900;color:#1a1a1a;letter-spacing:0.5px;margin-bottom:6px;">{LEAF}{black}{red1} · {red2}</span></section>'
        f'<section style="font-size:13px;color:#666;letter-spacing:1px;margin-bottom:18px;">{LEAF}{eyebrow}</span></section>'
        f'<section style="border-top:1px dashed #FECACA;margin-bottom:16px;">{LEAF}<br></span></section>'
        '<section style="font-size:13px;color:#555;line-height:1.8;padding:12px;background:#FEF2F2;border:1px solid #FECACA;">'
        f'{LEAF}{meta}</span></section>'
        '<section style="display:flex;gap:8px;margin-top:16px;">'
        f'<section style="font-size:10px;color:#C8102E;border:1px solid #C8102E;padding:4px 10px;font-weight:700;">{LEAF}#{tag1}</span></section>'
        f'<section style="font-size:10px;color:#C8102E;border:1px solid #C8102E;padding:4px 10px;font-weight:700;">{LEAF}#{tag2}</span></section></section></section>'
        '<section style="width:48px;padding:14px 4px;display:flex;flex-direction:column;align-items:center;justify-content:space-between;background:#FEF2F2;">'
        f'<section style="text-align:center;"><section style="font-size:8px;color:#999;">{LEAF}NO.</span></section><section style="font-size:16px;font-weight:900;color:#C8102E;">{LEAF}01</span></section></section>'
        f'<section style="writing-mode:vertical-rl;font-size:9px;color:#888;letter-spacing:2px;">{LEAF}VALID PASS</span></section>'
        f'<section style="text-align:center;"><section style="font-size:8px;color:#999;">{LEAF}GRADE</span></section><section style="font-size:14px;font-weight:900;color:#C8102E;">{LEAF}A</span></section></section></section></section>'
        '<section style="padding:10px 20px;border-top:2px dashed #FECACA;display:flex;justify-content:space-between;align-items:center;">'
        f'<section style="font-size:10px;color:#999;letter-spacing:1px;">{LEAF}VALID FOR ONE READ</span></section>'
        f'<section style="font-size:10px;color:#999;letter-spacing:1px;">{LEAF}ADMIT ONE</span></section></section></section>'
    )


def cover_journal(date, *, eyebrow='汇芯内刊', strike='装个工具就能撒手不管', black='把活交出去', red2='把判断留下来', meta='1800 多份 · 13 张真图', tag1='JOURNAL', tag2='HUIXIN'):
    return (
        '<section style="margin:0 10px 28px;background:#fdfdf8;border:1px solid #bfc1b7;border-radius:6px;overflow:hidden;">'
        '<section style="padding:26px 22px 20px;">'
        '<section style="display:flex;align-items:center;gap:8px;margin-bottom:20px;">'
        f'<span style="width:8px;height:8px;background:#1e1f23;border-radius:50%;display:inline-block;">{LEAF}<br></span></span>'
        f'<span style="font-size:11px;font-weight:700;letter-spacing:3px;color:#65675e;">{LEAF}{eyebrow}</span></span>'
        f'<section style="flex:1;height:1px;background:#bfc1b7;">{LEAF}<br></span></section>'
        f'<span style="font-size:10px;color:#9ea096;font-weight:500;">{LEAF}{date}</span></span></section>'
        f'<p style="font-size:13px;color:#9ea096;margin:0 0 8px;text-decoration:line-through;">{LEAF}{strike}</span></p>'
        '<p style="font-size:22px;font-weight:900;color:#23251d;margin:0 0 10px;line-height:1.25;">'
        f'{LEAF}{black} · </span><span style="border-bottom:3px solid #C8102E;">{LEAF}{red2}</span></span></p>'
        f'<p style="font-size:13px;color:#65675e;margin:0;line-height:1.7;">{LEAF}{meta}</span></p></section>'
        '<section style="background:#1e1f23;padding:11px 22px;display:flex;align-items:center;justify-content:space-between;">'
        f'<p style="font-size:11px;color:rgba(255,255,255,0.92);margin:0;font-weight:600;letter-spacing:1px;">{LEAF}ISSUE · FIELD REPORT</span></p>'
        '<section style="display:flex;gap:6px;">'
        f'<span style="background:#e5e7e0;color:#23251d;padding:2px 8px;border-radius:4px;font-size:9px;font-weight:700;">{LEAF}{tag1}</span></span>'
        f'<span style="background:#e5e7e0;color:#23251d;padding:2px 8px;border-radius:4px;font-size:9px;font-weight:700;">{LEAF}{tag2}</span></span></section></section></section>'
    )


def chapter_for_theme(theme, num, title, is_last=False):
    if theme == 'magazine-card':
        badge = 'PART ///' if is_last else f'PART {num:02d}'
        return (
            '<section style="margin:38px 20px 18px;">'
            '<section style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">'
            f'<span style="background:#C8102E;color:#fff;font-size:10px;font-weight:800;padding:3px 8px;border-radius:4px;letter-spacing:1px;">{LEAF}{badge}</span></span>'
            f'<section style="flex:1;height:1px;background:#E5E7EB;">{LEAF}<br></span></section></section>'
            f'<p style="font-size:21px;font-weight:900;color:#111827;line-height:1.4;margin:0;">{LEAF}{title}</span></p></section>'
        )
    if theme == 'classic-edit':
        badge = '∞' if is_last else f'{num:02d}'
        return (
            '<section style="margin:42px 10px 22px;padding-bottom:12px;border-bottom:3px solid #C8102E;display:flex;align-items:center;">'
            f'<span style="display:inline-block;background:#C8102E;color:#FFFFFF;font-size:16px;font-weight:900;padding:4px 12px;border-radius:6px;margin-right:12px;">{LEAF}{badge}</span></span>'
            '<section>'
            f'<p style="font-size:10px;color:#C8102E;font-weight:700;letter-spacing:3px;margin:0 0 2px;">{LEAF}CHAPTER</span></p>'
            f'<p style="font-size:18px;font-weight:800;color:#1C1917;margin:0;">{LEAF}{title}</span></p></section></section>'
        )
    if theme == 'minimal-line':
        badge = '∞' if is_last else f'{num:02d}'
        return (
            '<section style="margin:48px 10px 24px;padding-bottom:16px;border-bottom:1px solid #E4E4E7;">'
            f'<p style="font-size:42px;font-weight:900;color:#E4E4E7;margin:0 0 4px;line-height:1;">{LEAF}{badge}</span></p>'
            f'<p style="font-size:19px;font-weight:800;color:#27272A;margin:0;line-height:1.4;">{LEAF}{title}</span></p></section>'
        )
    if theme == 'zen-space':
        badge = 'POSTSCRIPT' if is_last else f'CHAPTER {num:02d}'
        return (
            '<section style="margin:52px 16px 26px;">'
            f'<p style="font-size:10px;color:#C8102E;font-weight:700;letter-spacing:3px;margin:0 0 8px;">{LEAF}{badge}</span></p>'
            f'<p style="font-family:\'Noto Serif SC\',Georgia,serif;font-size:21px;font-weight:700;color:#2B2B2B;margin:0 0 14px;line-height:1.4;">{LEAF}{title}</span></p>'
            f'<section style="width:36px;height:2px;background:#C8102E;">{LEAF}<br></span></section></section>'
        )
    if theme == 'ticket':
        badge = f'CHAPTER {num:02d}'
        return (
            '<section style="margin:34px 10px 20px;padding:14px 16px;background:#fffef8;border:2px solid #1a1a1a;box-shadow:3px 3px 0 #1a1a1a;">'
            f'<p style="font-size:10px;color:#C8102E;font-weight:800;letter-spacing:2px;margin:0 0 6px;">{LEAF}{badge}</span></p>'
            f'<p style="font-size:18px;font-weight:900;color:#1a1a1a;margin:0;">{LEAF}{title}</span></p></section>'
        )
    # journal
    badge = f'{num:02d}'
    return (
        '<section style="margin:34px 10px 18px;display:flex;align-items:center;gap:12px;">'
        '<section style="text-align:center;flex-shrink:0;">'
        f'<p style="margin:0;font-size:22px;font-weight:900;color:#23251d;line-height:1;">{LEAF}{badge}</span></p>'
        f'<p style="margin:2px 0 0;font-size:8px;font-weight:700;color:#9ea096;letter-spacing:2px;">{LEAF}PART</span></p></section>'
        f'<section style="width:1px;height:32px;background:#bfc1b7;">{LEAF}<br></span></section>'
        f'<p style="margin:0;font-size:18px;font-weight:800;color:#23251d;line-height:1.35;">{LEAF}{title}</span></p></section>'
    )


END = (
    '<section style="margin:44px 20px 0;text-align:center;">'
    '<section style="display:flex;align-items:center;justify-content:center;gap:12px;">'
    f'<span style="width:40px;height:1px;background:#D1D5DB;">{LEAF}<br></span></span>'
    f'<span style="font-size:10px;color:#C8102E;font-weight:700;letter-spacing:4px;">{LEAF}END</span></span>'
    f'<span style="width:40px;height:1px;background:#D1D5DB;">{LEAF}<br></span></span>'
    '</section></section>'
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--article', required=True)
    ap.add_argument('--theme', default='magazine-card', choices=THEMES)
    ap.add_argument('--out', required=True)
    ap.add_argument('--date', default='2026.11.12')
    ap.add_argument('--eyebrow', default='三个月的实操复盘')
    ap.add_argument('--strike', default='装个工具就能撒手不管')
    ap.add_argument('--cover-black', default='把活')
    ap.add_argument('--cover-red1', default='交出去')
    ap.add_argument('--cover-red2', default='把判断留下来')
    ap.add_argument('--cover-meta', default='1800 多份 · 13 张真图 · 三张能带走的纸')
    ap.add_argument('--cover-foot', default='一人公司 · 三个月实操')
    ap.add_argument('--tag1', default='复盘')
    ap.add_argument('--tag2', default='可带走')
    ap.add_argument('--parts-short', default='', help='目录短标签，用 | 分隔；留空则从章标题截取')
    a = ap.parse_args()
    art = json.loads(Path(a.article).read_text(encoding='utf-8'))
    c = art['content']
    if ('PART 01' in c or 'CHAPTER' in c or 'HUIXIN PASS' in c) and 'END' in c:
        print('已装配过，跳过')
        return 0

    raw_titles = [
        re.sub(r'^\d+[\s、.]*', '', re.sub(r'<[^>]+>', '', m.group(2)).strip())
        for m in re.finditer(r'(<h2[^>]*>)(.*?)(</h2>)', c, flags=re.S)
    ]
    total_h2 = len(raw_titles)
    idx_counter = [0]

    def repl(m):
        idx_counter[0] += 1
        i = idx_counter[0]
        t = raw_titles[i - 1] if i <= len(raw_titles) else '章节'
        return chapter_for_theme(a.theme, i, t, is_last=(i == total_h2 and total_h2 > 1))

    c, n = re.subn(r'(<h2[^>]*>)(.*?)(</h2>)', repl, c, flags=re.S)

    if a.parts_short.strip():
        shorts = [x.strip() for x in a.parts_short.split('|') if x.strip()]
        while len(shorts) < len(raw_titles):
            shorts.append('要点')
        parts = [(s, '%02d' % (i + 1)) for i, s in enumerate(shorts)]
    else:
        parts = [(re.sub(r'^[\d\s、.]+', '', x)[:6] or '小节', '%02d' % (i + 1)) for i, x in enumerate(raw_titles)]

    if a.theme == 'magazine-card':
        shell = cover_magazine(
            a.date, parts, eyebrow=a.eyebrow, strike=a.strike,
            black=a.cover_black, red1=a.cover_red1, red2=a.cover_red2,
            meta=a.cover_meta, foot=a.cover_foot, tag1=a.tag1, tag2=a.tag2,
        )
    elif a.theme == 'classic-edit':
        shell = cover_classic_edit(parts, black=a.cover_black, red1=a.cover_red1, red2=a.cover_red2, eyebrow=a.eyebrow)
    elif a.theme == 'minimal-line':
        shell = cover_minimal_line(parts, black=a.cover_black, red1=a.cover_red1, red2=a.cover_red2, eyebrow=a.eyebrow)
    elif a.theme == 'zen-space':
        shell = cover_zen_space(parts, black=a.cover_black, red1=a.cover_red1, red2=a.cover_red2, eyebrow=a.eyebrow)
    elif a.theme == 'ticket':
        shell = cover_ticket(black=a.cover_black, red1=a.cover_red1, red2=a.cover_red2, eyebrow=a.eyebrow, meta=a.cover_meta, tag1=a.tag1, tag2=a.tag2)
    else:
        shell = cover_journal(a.date, eyebrow=a.eyebrow, strike=a.strike, black=a.cover_black + a.cover_red1, red2=a.cover_red2, meta=a.cover_meta, tag1=a.tag1, tag2=a.tag2)

    m = re.match(r'(<section[^>]*>)', c)
    if not m:
        print('找不到全局容器', file=sys.stderr)
        return 2
    c = m.group(1) + shell + c[m.end():]
    idx = c.rfind('</section>')
    c = c[:idx] + END + c[idx:]
    art['content'] = c
    Path(a.out).write_text(json.dumps(art, ensure_ascii=False), encoding='utf-8')
    print(f'装配完成 [{a.theme}]: {n} 个章节标题 / 开篇封面 + 目录 + END / leaf={c.count(LEAF)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
