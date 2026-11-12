import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).parent
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec); spec.loader.exec_module(result)
    return result
fmt=module('formatter',ROOT/'markdown_to_wechat_article.py')
validator=module('validator',ROOT/'validate_wechat_article.py')

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)
    def article(self,body,title='文章测试'):
        p=self.p/'article.json'; p.write_text(json.dumps(dict(title=title,content=body)))
        return p
    def test_first_paragraph_is_preserved(self):
        p=self.p/'text.md'; p.write_text('第一段不能丢\n\n第二段')
        self.assertEqual(fmt.body_lines(p)[0],'第一段不能丢')
    def test_frontmatter_removed(self):
        p=self.p/'text.md'; p.write_text('---\ntitle: internal\n---\n# 标题\n正文')
        self.assertEqual(fmt.body_lines(p),['# 标题','正文'])
    def test_quotes_grouped_and_not_lost(self):
        s=fmt.convert_markdown(['> 第一项','> 第二项','普通正文'],[])
        self.assertIn('第一项\n第二项',s)
        self.assertIn('普通正文',s)
    def test_code_escaped(self):
        s=fmt.convert_markdown(['```','<script>alert(1)</script>','```'],[])
        self.assertNotIn('<script>',s)
        self.assertIn('&lt;script&gt;',s)
    def test_unclosed_code_rejected(self):
        with self.assertRaises(ValueError): fmt.convert_markdown(['```','unfinished'],[])
    def test_links_and_images(self):
        s=fmt.convert_markdown(['[来源](https://example.com/a)','![局部截图](real.png)'],['real.png'])
        self.assertIn('href="https://example.com/a"',s)
        self.assertIn('src="real.png"',s)
        self.assertIn('局部截图',s)
    def test_unplaced_images_rejected(self):
        with self.assertRaises(ValueError): fmt.convert_markdown(['正文'],['missing.png'])
    def test_title_long_para_and_markers_blocked(self):
        p=self.article('<h1>文章测试</h1><h2>01</h2><p>'+('长'*66)+'</p><p>[[img:foo]]</p>')
        errors,_=validator.validate(p,65,False)
        self.assertGreaterEqual(len(errors),4)
    def test_missing_images_blocked(self):
        p=self.article('<img src="missing.png">')
        self.assertTrue(any('missing local' in e for e in validator.validate(p,65,False)[0]))
    def test_full_article_needs_visuals(self):
        p=self.article(''.join('<p>'+('短段'*25)+'</p>' for _ in range(32)))
        self.assertTrue(any('at least 3' in e for e in validator.validate(p,65,False)[0]))
        self.assertEqual(validator.validate(p,65,False,min_images=0)[0],[])
    def test_valid_body(self):
        for n in ['real.png','xiaohei.png','sample.png']: (self.p/n).write_bytes(b'fixture')
        body=''.join('<p>'+('短段'*25)+'</p>' for _ in range(32))
        body+=''.join(f'<img src="{n}">' for n in ['real.png','xiaohei.png','sample.png'])
        self.assertEqual(validator.validate(self.article(body),65,True)[0],[])
    def test_six_themes_render_distinct(self):
        outs={}
        for tid in fmt.THEMES:
            fmt._T=fmt.THEMES[tid]
            outs[tid]=fmt.convert_markdown(['## 01 判断句','正文一段','> 重点条'],[])
        self.assertEqual(len({v for v in outs.values()}),len(fmt.THEMES))
        self.assertIn('#C8102E',outs['journal'])
    def test_gradient_and_backtick_blocked(self):
        p=self.article('<p><span style="background:linear-gradient(180deg,#fff,#000)">x</span></p><p>残留 `code` 反引号</p><p>&amp;quot;双重转义&amp;quot;</p>')
        errors,_=validator.validate(p,65,False,min_images=0)
        joined=' | '.join(errors)
        self.assertIn('渐变',joined); self.assertIn('反引号',joined); self.assertIn('双重转义',joined)
    def test_fixed_ip_gate_precedes_network(self):
        path=Path('skills/wechat-auto-publisher/scripts/publish_via_fixed_ip.py')
        if not path.exists(): self.skipTest('local publisher not installed')
        pub=module('fixed_ip',path)
        article=self.article('<p>invalid fixture</p>'); thumb=self.p/'thumb.jpg'; thumb.write_bytes(b'fixture')
        key=self.p/'test-key'; key.write_bytes(b'fixture')
        settings=dict(key=key,host='invalid.example',user='none',remote_root='/tmp',remote_env='/tmp/not-used')
        argv=['publish','--mode','add','--article',str(article),'--thumb',str(thumb),'--out',str(self.p/'out.json')]
        with patch.object(sys,'argv',argv),patch.object(pub,'load_settings',return_value=settings),patch.object(pub,'run',side_effect=subprocess.CalledProcessError(2,['validator'])) as runner:
            with self.assertRaises(subprocess.CalledProcessError): pub.main()
            self.assertEqual(runner.call_count,1)
            self.assertIn('validate_wechat_article.py',runner.call_args.args[0][1])

if __name__=='__main__': unittest.main(verbosity=2)
