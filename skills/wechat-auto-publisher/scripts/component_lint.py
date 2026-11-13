#!/usr/bin/env python3
from __future__ import annotations
"""组件库源头检查器（借鉴 gzh-design-skill 的 component_lint.py）

扫描 references/*.md 里的 ```html 组件块，检测会导致公众号排版问题的反模式，
作为 wechat-formatter 双关卡校验的「源头关」——组件库本身干净，转换器产物才干净。

与 validate_wechat_article.py 的「产物关」配合构成闭环：
  改 references/组件库.md → 本脚本扫源头 → 转换器生成产物 → validate_wechat_article.py 扫产物

用法:
    component_lint.py [skill-root]   # 默认脚本所在 skill 根目录
退出码: 1 = 有 ERROR; 0 = 通过
"""

import glob
import os
import re
import sys

# (正则, 级别, 说明) —— 在每个 ```html 组件块内检查
CHECKS = [
    (re.compile(r"white-space\s*:\s*pre", re.I), "ERROR",
     "用了 white-space:pre —— 代码块应每行一个 <p style=\"margin:0\">，缩进用全角空格"),
    (re.compile(r"</?div[\s>]", re.I), "ERROR", "出现 <div>，应用 <section>"),
    (re.compile(r"\sclass\s*=", re.I), "ERROR", "出现 class 属性（公众号会剥离）"),
    (re.compile(r"\sid\s*=", re.I), "ERROR", "出现 id 属性"),
    (re.compile(r"<style[\s>]", re.I), "ERROR", "出现 <style> 标签"),
    (re.compile(r"position\s*:\s*(fixed|absolute|sticky)", re.I), "ERROR",
     "position fixed/absolute/sticky 不被支持"),
    (re.compile(r"display\s*:\s*grid", re.I), "ERROR", "display:grid 不被支持，请用 flex"),
    (re.compile(r"var\s*\(\s*--", re.I), "ERROR", "用了 CSS 变量 var(--x)"),
    (re.compile(r"@(media|keyframes|import)", re.I), "ERROR", "@media/@keyframes/@import 不被支持"),
    (re.compile(r"url\s*\(\s*['\"]?https?://[^)]*\.(woff2?|ttf|otf|eot)", re.I),
     "ERROR", "外部字体不被支持"),
    (re.compile(r"float\s*:", re.I), "ERROR", "float 不被支持"),
    (re.compile(r"(linear|radial|conic)-gradient", re.I), "ERROR",
     "禁用渐变（2026-11-02 乱码硬闸），浅装饰改纯色"),
]

# 规范/笔记类文档不是组件库，其 HTML 示例可能含反例说明，跳过避免误报。
EXCLUDE = {"editorial-contract.md", "publishing-notes.md"}


def lint_file(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    name = os.path.basename(path)
    found = []  # (level, msg)
    seen = set()

    def add(level, msg):
        if msg not in seen:
            seen.add(msg)
            found.append((level, msg))

    for m in re.finditer(r"```html\s*\n(.*?)```", text, re.S):
        html = m.group(1)
        for rx, level, msg in CHECKS:
            if rx.search(html):
                add(level, msg)
    return name, found


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    refs = sorted(glob.glob(os.path.join(root, "references", "*.md")))
    refs = [p for p in refs if os.path.basename(p) not in EXCLUDE]
    if not refs:
        print(f"未找到 {root}/references/ 下可扫描的组件库 .md")
        sys.exit(1)

    total_err = total_warn = clean = 0
    print(f"📐 组件库源头检查：{len(refs)} 个库\n")
    for path in refs:
        name, found = lint_file(path)
        if not found:
            clean += 1
            continue
        errs = [m for lv, m in found if lv == "ERROR"]
        warns = [m for lv, m in found if lv == "WARN"]
        total_err += len(errs)
        total_warn += len(warns)
        print(f"── {name} ──")
        for m in errs:
            print(f"   ❌ {m}")
        for m in warns:
            print(f"   ⚠️  {m}")

    print(f"\n汇总：{clean}/{len(refs)} 个库干净，ERROR×{total_err}，WARN×{total_warn}")
    if total_err == 0 and total_warn == 0:
        print("✅ 全部组件库源头无反模式")
    sys.exit(1 if total_err else 0)


if __name__ == "__main__":
    main()
