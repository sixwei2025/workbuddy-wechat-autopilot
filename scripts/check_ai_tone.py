#!/usr/bin/env python3
"""中文稿「AI 味」检测，只出报告不改稿。

依据：X @btc5767 2026-11-12《AI 味到底是什么》（520 万字配对语料实验自述）。
指标是统计倾向，不是判决书；命中不等于要改，看同一篇里的密度叠加。
用法: python3 check_ai_tone.py <稿.md> [--section 正文] [--json 报告.json]
"""
import argparse, json, re, statistics, sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('file'); ap.add_argument('--section', default='正文'); ap.add_argument('--json', default='')
a = ap.parse_args()
t = Path(a.file).read_text(encoding='utf-8')
if '## '+a.section in t: t = t.split('## '+a.section, 1)[1]
body = '\n'.join(l for l in t.split('\n') if not l.startswith(('!','#','```','D1','D2','D3','D4','D5','D6','D7','1 ','2 ','3 ','4 ')))
paras = [p.strip() for p in body.split('\n\n') if len(p.strip())>8]

flip = [m.group(0).strip() for m in re.finditer(r'不是[^。！？\n]{1,40}[，,][^。！？\n]{0,12}(?:而是|是)[^\n]{0,20}', body)]
colon = [m.group(0).strip()[:60] for m in re.finditer(r'[^。！？\n]{0,22}：[^\n]{0,40}', body)
         if not re.search(r'(给谁看|要解决|结果物|数字从哪来|做完怎么算对|http|____)', m.group(0))]
enum  = [m.group(0).strip()[:80] for m in re.finditer(r'[^。！？\n]*、[^。！？\n]*', body) if m.group(0).count('、')>=2]
heads = re.findall(r'^## .*', body, flags=re.M)
lens  = [len(p) for p in paras]
report = {
 '依据':'X @btc5767 2026-11-12 配对语料实验（作者自述，未第三方复现）；指标是统计倾向不是判决书',
 '段落数':len(paras), '段长均值':round(statistics.mean(lens),1) if lens else 0,
 '段长标准差':round(statistics.pstdev(lens),1) if len(lens)>1 else 0,
 '① 不是A而是B（AI 3.4x）':{'count':len(flip),'items':flip},
 '② 结论提示冒号（AI 2.1~4x）':{'count':len(colon),'items':colon[:20]},
 '③ 顿号三项以上（AI 1.8x）':{'count':len(enum),'items':enum[:12]},
 '④ 小标题数':len(heads),
 '⑤ 破折号数':body.count('——'),
 '⑥ 用词避重复':{'机器':body.count('机器'),'工具':body.count('工具'),'程序':body.count('程序'),'它':body.count('它')},
 '判读':'单条命中不用改；同一篇里 ①≥3 或 ②≥8 或 ③≥6 属高密度叠加，按最小改动原则只改命中句。个人风格指南优先。',
}
print(json.dumps(report,ensure_ascii=False,indent=2))
if a.json: Path(a.json).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
