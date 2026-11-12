#!/usr/bin/env python3
import argparse
import json
import re
import sys
from html import unescape
from pathlib import Path


# 2026-09-15 用户明确更新：2–3 行短段落口径，80 字提示过密（旧的 180 字长段落口径作废）。
DEFAULT_MAX_PARAGRAPH = 80
METHODOLOGY_TERMS = (
    "WorkBuddy",
    "Codex",
    "Claude",
    "Kimi",
    "Agent",
    "智能体",
    "迁移",
    "工作流",
    "流程",
    "方法",
    "清单",
    "复盘",
)


def strip_tags(html: str) -> str:
    return unescape(re.sub(r"<[^>]+>", "", html))


def image_sources(content: str) -> list[str]:
    return re.findall(r'<img[^>]+src="([^"]+)"', content)


def local_image_exists(article_path: Path, src: str) -> bool:
    if src.startswith(("http://", "https://")):
        return True
    candidates = [
        article_path.parent / src,
        article_path.parent / "assets" / Path(src).name,
        Path(src),
    ]
    return any(path.exists() for path in candidates)


def requires_xiaohei(title: str, content_text: str) -> bool:
    # 2026-11-12 袁总拍板：自动化公众号配图不再使用小黑图 / AI 插画，
    # 尽量全部用真实截图。默认不再要求小黑图；确需恢复时显式传 --require-xiaohei。
    return False


# 2026-11-02 排版切换为「汇芯红六套骨架」后新增乱码硬闸（来源 themes/README.md）：
# 双重转义、残留反引号、渐变禁用，一次扫完；图说样式与标红密度只提示不拦。
CAPTION_HINTS = ("（", "(", "—", "图", "示意", "截图", "录屏", "实测")


def gate_warnings(content: str) -> list[str]:
    """软检查：不拦上传，但要在交付说明里交代清楚。"""
    warns: list[str] = []
    if "&quot;" in content:
        warns.append("正文含转义引号 &quot;，硬闸建议改真引号 \"（不影响渲染，但推箱前应清）")

    for m in re.finditer(r"<img\b", content):
        tail = content[m.end(): m.end() + 400]
        pm = re.search(r"<p([^>]*)>(.*?)</p>", tail, re.S)
        if not pm:
            continue
        attrs, inner = pm.group(1), pm.group(2)
        txt = strip_tags(inner).strip()
        if not txt or len(txt) > 60 or not txt.startswith(CAPTION_HINTS):
            continue
        fs = re.search(r"font-size\s*:\s*(\d+)px", attrs)
        if not fs or int(fs.group(1)) > 13:
            warns.append(f"图说字号不是 12–13px：{txt[:20]}")
        if "text-align:center" not in attrs.replace(" ", ""):
            warns.append(f"图说未居中：{txt[:20]}")

    anchors = len(re.findall(r'<strong style="color:', content))
    if anchors == 0:
        warns.append("未见标红锚点（建议 3–6 处，只点关键判断）")
    elif anchors > 12:
        warns.append(f"标红 {anchors} 处偏多（建议 3–6 处，红多了等于没有重点）")
    return warns


def validate(article_path: Path, max_paragraph: int, require_xiaohei: bool | None, min_images: int | None = None) -> tuple[list[str], list[str]]:
    article = json.loads(article_path.read_text(encoding="utf-8"))
    title = article.get("title", "").strip()
    content = article.get("content", "")
    text = strip_tags(content)
    errors: list[str] = []

    if not title:
        errors.append("missing article title")
    if "<h1" in content.lower():
        errors.append("content contains <h1>; WeChat title must stay only in title field")
    if any(re.fullmatch(r"\d{1,2}", strip_tags(h).strip()) for h in re.findall(r"<h2[^>]*>(.*?)</h2>", content, re.S | re.I)):
        errors.append("section heading contains only a number")
    if re.search(r"\[\[img:|【(?:任务说明|套餐示例)(?:开始|结束)】|\bTODO\b|图片占位符", text):
        errors.append("content contains unfinished editorial markers")
    if title and title in text:
        errors.append("content repeats the article title")
    if re.search(r"/Users/|file://|work/", content):
        errors.append("content contains local filesystem path")

    # 第二关：样式层双关卡校验（借鉴 gzh-design-skill 的 forbidden-tags + 半角标点）
    # 代码块内部为等宽示例，其半角符号 / 标签属正常，先将其内部文本清空再检查。
    masked = re.sub(
        r'(<section style="[^"]*white-space:pre-wrap[^"]*">).*?(</section>)',
        r"\1\2", content, flags=re.S,
    )
    _FORBIDDEN = [
        (re.compile(r"</?div[\s>]", re.I), "禁止使用 <div>，请改用 <section>"),
        (re.compile(r"\sclass\s*=", re.I), "存在 class 属性（公众号会剥离，请改用内联 style）"),
        (re.compile(r"\sid\s*=", re.I), "存在 id 属性（公众号会剥离）"),
        (re.compile(r"<style[\s>]", re.I), "<style> 标签会被过滤"),
        (re.compile(r"<script[\s>]", re.I), "<script> 标签会被过滤"),
        (re.compile(r"<link[\s>]", re.I), "外部 <link> 会被过滤"),
        (re.compile(r"position\s*:\s*(fixed|absolute|sticky)", re.I), "position fixed/absolute/sticky 不被支持"),
        (re.compile(r"float\s*:", re.I), "float 不被支持"),
        (re.compile(r"@media", re.I), "@media 不被支持"),
        (re.compile(r"@keyframes", re.I), "@keyframes 不被支持"),
        (re.compile(r"@import", re.I), "@import 不被支持"),
        (re.compile(r"display\s*:\s*grid", re.I), "display:grid 不被支持"),
        (re.compile(r"var\s*\(\s*--", re.I), "CSS 变量 var(--x) 不被支持"),
        (re.compile(r"url\s*\(\s*['\"]?https?://[^)]*\.(woff2?|ttf|otf|eot)", re.I), "外部字体不被支持"),
        (re.compile(r"expression\s*\(", re.I), "expression() 不被支持"),
        # 乱码硬闸：六套骨架明令禁用渐变，浅装饰改纯色
        (re.compile(r"(linear|radial|conic)-gradient", re.I), "禁用渐变（linear/radial/conic-gradient），浅装饰改纯色"),
    ]
    for rx, msg in _FORBIDDEN:
        if rx.search(masked):
            errors.append("style: " + msg)
    _half = re.compile(r"[一-鿿㐀-䶿][,;!?]")
    _masked_text = strip_tags(masked)
    _half_hits = list(_half.finditer(_masked_text))
    if _half_hits:
        _samples = " / ".join(_masked_text[h.start():h.start() + 6] for h in _half_hits[:3])
        errors.append(f"style: 正文存在半角标点（中文后跟 , ; ! ?），应改全角。例：{_samples}")

    # 乱码硬闸（hard）：双重转义与残留 Markdown 反引号，推箱前必须清掉
    if "&amp;quot;" in content or "&amp;#" in content:
        errors.append("乱码硬闸：正文存在双重转义（&amp;quot; / &amp;#…），推箱前必须改成正常字符")
    if "`" in _masked_text:
        errors.append("乱码硬闸：正文文本节点残留 Markdown 反引号 `，应改为行内代码组件或去掉")

    paragraphs = [
        strip_tags(match).strip()
        for match in re.findall(r"<p[^>]*>(.*?)</p>", content, flags=re.S | re.I)
    ]
    long_paragraphs = [
        (idx + 1, len(p), p[:40])
        for idx, p in enumerate(paragraphs)
        if len(p) > max_paragraph
    ]
    if long_paragraphs:
        preview = "; ".join(f"p{idx}={length} chars: {head}" for idx, length, head in long_paragraphs[:5])
        errors.append(f"paragraphs exceed {max_paragraph} Chinese chars: {preview}")

    # 2026-11-12 硬闸：长文必须已装配主题专属外壳（组件库带 <span leaf=""> 占位）。
    # 转换器只出「基础版式」，漏跑 apply_theme_shell.py 会把六套骨架排成同一套普通正文。
    if len(text) >= 1500 and content.count('<span leaf="">') < 6:
        errors.append("missing theme shell: 主题专属开篇/目录/章节/END 未装配，跑 apply_theme_shell.py 后再发")

    imgs = image_sources(content)
    missing = [src for src in imgs if not local_image_exists(article_path, src)]
    if missing:
        errors.append("missing local content images: " + ", ".join(missing[:8]))

    need_xiaohei = requires_xiaohei(title, text) if require_xiaohei is None else require_xiaohei
    if need_xiaohei:
        xiaohei_count = sum("xiaohei" in Path(src).name.lower() or "小黑" in Path(src).name for src in imgs)
        if xiaohei_count < 1:
            errors.append("method/workflow article requires at least one xiaohei illustration image")

    # Count is an editorial default for full-length articles, not all documents.
    minimum = min_images if min_images is not None else (3 if len(text) >= 1500 else 0)
    if len(imgs) < minimum:
        errors.append(f"article requires at least {minimum} relevant body images; revise or document the user's explicit exception")

    return errors, gate_warnings(masked)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Yuan Liuwei WeChat draft JSON before upload.")
    parser.add_argument("--article", required=True)
    parser.add_argument("--max-paragraph", type=int, default=DEFAULT_MAX_PARAGRAPH)
    parser.add_argument("--min-images", type=int, help="Explicit editorial exception only; default is 3 for full-length text")
    parser.add_argument("--strict-warnings", action="store_true", help="软检查也当作失败（默认只提示）")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--require-xiaohei", action="store_true")
    group.add_argument("--no-require-xiaohei", action="store_true")
    args = parser.parse_args()

    require_xiaohei = None
    if args.require_xiaohei:
        require_xiaohei = True
    elif args.no_require_xiaohei:
        require_xiaohei = False

    errors, warnings = validate(Path(args.article), args.max_paragraph, require_xiaohei, args.min_images)
    if errors or (args.strict_warnings and warnings):
        payload = {"ok": False, "errors": errors}
        if warnings:
            payload["warnings"] = warnings
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2
    payload = {"ok": True}
    if warnings:
        payload["warnings"] = warnings
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
