#!/usr/bin/env python3
"""把 markdown_to_wechat_article.py 产出的「基础版式」补成完整骨架。

转换器只负责 token 化版式；主题专属的开篇封面 / 目录 / 章节标题 / END
必须按 theme-<id>.md 组件手工装配。本脚本把这一步自动化，避免漏做。
用法: python3 apply_theme_shell.py --article <json> --theme magazine-card --out <json>
"""
import argparse, json, re, sys
from pathlib import Path

LEAF = '<span leaf="">'

def cover_magazine(quote, date, parts, *, eyebrow='三个月的实操复盘', strike='装个工具就能撒手不管',
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
          f'<p style="font-size:10px;color:{c3};margin:0;">{LEAF}{sub}</span></p></section>')
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
      + f'<p style="font-size:10px;color:#9CA3AF;margin:0;text-transform:uppercase;letter-spacing:2px;font-weight:600;">{LEAF}{len(parts)-1} Parts + Conclusion</span></p>'
      + f'<p style="font-size:10px;color:#9CA3AF;margin:0;">{LEAF}滑动</span></p></section>'
      + '<section style="overflow-x:scroll;-webkit-overflow-scrolling:touch;white-space:nowrap;padding-bottom:8px;">'
      + ''.join(toc) + '</section></section>')

def chapter(num, title):
    return ('<section style="margin:38px 20px 18px;">'
            '<section style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">'
            f'<span style="background:#C8102E;color:#fff;font-size:10px;font-weight:800;padding:3px 8px;border-radius:4px;letter-spacing:1px;">{LEAF}PART {num:02d}</span></span>'
            f'<section style="flex:1;height:1px;background:#E5E7EB;">{LEAF}<br></span></section></section>'
            f'<p style="font-size:21px;font-weight:900;color:#111827;line-height:1.4;margin:0;">{LEAF}{title}</span></p></section>')

END = ('<section style="margin:44px 20px 0;text-align:center;">'
       '<section style="display:flex;align-items:center;justify-content:center;gap:12px;">'
       f'<span style="width:40px;height:1px;background:#D1D5DB;">{LEAF}<br></span></span>'
       f'<span style="font-size:10px;color:#9CA3AF;letter-spacing:4px;">{LEAF}END</span></span>'
       f'<span style="width:40px;height:1px;background:#D1D5DB;">{LEAF}<br></span></span>'
       '</section></section>')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--article', required=True)
    ap.add_argument('--theme', default='magazine-card')
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
    if 'PART 01' in c and 'END' in c:
        print('已装配过，跳过'); return 0
    if a.theme != 'magazine-card':
        print('暂只实现 magazine-card 外壳，请用 --theme magazine-card', file=sys.stderr); return 2

    titles = []
    def repl(m):
        t = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        t = re.sub(r'^\d+\s*', '', t)
        titles.append(t)
        return chapter(len(titles), t)
    c, n = re.subn(r'(<h2[^>]*>)(.*?)(</h2>)', repl, c, flags=re.S)
    # 结语章节用 /// 标记
    if titles:
        c = c.replace('PART %02d' % len(titles), 'PART ///', 1)
    if a.parts_short.strip():
        shorts = [x.strip() for x in a.parts_short.split('|') if x.strip()]
        while len(shorts) < len(titles):
            shorts.append('...')
        parts = [(s, '%02d' % (i + 1)) for i, s in enumerate(shorts)]
    else:
        parts = [(re.sub(r'^[\d\s、.]+', '', x)[:6] or '小节', '%02d' % (i + 1))
                 for i, x in enumerate(titles)]
    shell = cover_magazine('', a.date, parts, eyebrow=a.eyebrow, strike=a.strike,
                           black=a.cover_black, red1=a.cover_red1, red2=a.cover_red2,
                           meta=a.cover_meta, foot=a.cover_foot, tag1=a.tag1, tag2=a.tag2)
    # 插到最外层开标签之后
    m = re.match(r'(<section[^>]*>)', c)
    if not m:
        print('找不到全局容器', file=sys.stderr); return 2
    c = m.group(1) + shell + c[m.end():]
    c = c.replace('</section>', END + '</section>', 1) if False else c
    # END 放在最后一个 </section> 之前
    idx = c.rfind('</section>')
    c = c[:idx] + END + c[idx:]
    art['content'] = c
    Path(a.out).write_text(json.dumps(art, ensure_ascii=False), encoding='utf-8')
    print(f'装配完成: {n} 个章节标题 / 开篇封面 + 目录 + END / leaf={c.count(LEAF)}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
