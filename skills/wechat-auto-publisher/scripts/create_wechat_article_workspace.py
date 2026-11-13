#!/usr/bin/env python3
from __future__ import annotations
import argparse
import os
import re
from datetime import datetime
from pathlib import Path


# 工作台根目录：优先环境变量，其次 ~/wechat-auto-workspace。
# 想沿用 Obsidian 目录就把 WECHAT_WORKSPACE_ROOT 指向你的 vault 子目录。
ROOT = Path(os.environ.get("WECHAT_WORKSPACE_ROOT", str(Path.home() / "wechat-auto-workspace")))
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
WORKBENCH_DIR = ROOT / "07-发布工作台"
INDEX_FILE = ROOT / "00-入口" / "公众号自动化工作流总索引.md"


def slugify(text: str) -> str:
    cleaned = re.sub(r"[\\/:*?\"<>|#\[\]\n\r\t]", "-", text)
    cleaned = re.sub(r"\s+", "", cleaned)
    cleaned = re.sub(r"-+", "-", cleaned).strip("-")
    return cleaned[:48] or "未命名选题"


def write_file(path: Path, content: str) -> None:
    if path.exists():
        return
    path.write_text(content.strip() + "\n", encoding="utf-8")


def update_index(title: str, folder: Path) -> None:
    if not INDEX_FILE.exists():
        return
    content = INDEX_FILE.read_text(encoding="utf-8")
    rel = folder.relative_to(ROOT).as_posix()
    line = f"- [[../{rel}/00-选题卡|{title}]]"
    if line in content:
        return
    marker = "## 最近工作台\n\n"
    if marker not in content:
        content += "\n\n## 最近工作台\n\n"
        marker = "## 最近工作台\n\n"
    content = content.replace("暂无。用脚本创建后，在这里手动补充链接。\n", "")
    content = content.replace(marker, marker + line + "\n", 1)
    INDEX_FILE.write_text(content, encoding="utf-8")


def create_workspace(title: str, brief: str = "") -> Path:
    today = datetime.now().strftime("%Y-%m-%d")
    folder = WORKBENCH_DIR / f"{today}-{slugify(title)}"
    folder.mkdir(parents=True, exist_ok=True)

    write_file(
        folder / "00-选题卡.md",
        f"""
# {title} - 选题卡

创建时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}
状态：待补资料

## 初始想法

{brief or "待补充"}

{(ASSETS_DIR / "topic-card-template.md").read_text(encoding="utf-8")}
""",
    )

    write_file(
        folder / "01-资料包.md",
        f"""
# {title} - 资料包

## 内部材料

| 材料 | 路径/链接 | 用法 | 是否可公开 |
|---|---|---|---|
|  |  |  |  |

## 真实截图/图片

| 图片 | 来源 | 用在第几段 | 处理要求 |
|---|---|---|---|
|  |  |  |  |

## 外部来源

| 来源 | 链接 | 可信度 S/A/B | 可引用结论 |
|---|---|---|---|
|  |  |  |  |

## 不可公开内容

- 客户隐私：
- 未公开数据：
- 内部锋利判断：
- 需要降风险的表述：
""",
    )

    write_file(
        folder / "02-草稿.md",
        f"""
# {title}

> 这是内部草稿，可以先完整表达判断。不要直接发布，发布前必须整理到 `03-public-safe发布稿.md`。

## 开头


## 01


## 02


## 03


## 结尾

""",
    )

    write_file(
        folder / "03-public-safe发布稿.md",
        f"""
# {title}

> 这是公众号可发布版本。写完后按 `04-public-safe发布稿/public-safe检查清单.md` 检查。

## 发布前检查

- [ ] 身份和背书安全
- [ ] 收益和结果表达安全
- [ ] 来源和截图安全
- [ ] 平台敏感内容安全
- [ ] 标题不过度承诺

## 正文

""",
    )

    write_file(
        folder / "04-配图素材清单.md",
        f"""
# {title} - 配图素材清单

按统一交付标准使用真实截图和小黑解释图；数量是起点，不用无关图凑数。

## 整篇视觉规划

- 阅读顺序：封面承诺 → 开头核心信息 → 证据 → 解释 → 可带走成果 → 结尾。
- 本篇重点及统一强调色、图注、标注方式：
- 每张图解决的读者问题、证据/示意属性及对应正文：
- 375px正文实屏验收记录（无预览则记未完成）：
- 200px封面检查记录：
- 审稿：点击理由 / 信息增量 / 实际可用性 / 视觉可读性 / 可信与分享价值。
- 每项的具体修改或通过依据：

| 顺序 | 配图位置 | 图片来源 | 处理动作 | 状态 |
|---|---|---|---|---|
| 1 | 开头后 |  | 打码/裁剪/标注 | 待准备 |
| 2 | 第一节 |  | 打码/裁剪/标注 | 待准备 |
| 3 | 第二节 |  | 打码/裁剪/标注 | 待准备 |
| 4 | 第三节 |  | 打码/裁剪/标注 | 待准备 |

## 封面

- 默认走 `cover-pop` + `imagegen` + 真实头像本地合成。
- 桌面封面文件夹只作为质量参考；只有用户明确指定成品或同题高匹配成品时，才直接使用。
- 头像路径：`assets/owner_portrait.jpg`
- 不要让图片模型重绘袁六伟的脸。
- 必须生成并查看 `assets/cover-200px-check.png`，不达桌面质量线不进草稿箱。
""",
    )

    write_file(
        folder / "05-草稿箱发布记录.md",
        f"""
# {title} - 草稿箱发布记录

## 文章信息

- public-safe 稿：`03-public-safe发布稿.md`
- 配图素材清单：`04-配图素材清单.md`
- 排版 HTML：
- 封面图：

## 发布前确认

- [ ] public-safe 检查已完成。
- [ ] 标题没有夸大承诺。
- [ ] 封面没有错误文字和身份问题。
- [ ] 正文图片已打码。
- [ ] 已确认可以写入公众号后台草稿箱。
- [ ] 不自动点击群发。

## 草稿箱操作记录

- 操作时间：
- 使用方式：手动 / Chrome 自动化辅助 / 其他
- 公众号后台状态：
- 草稿标题：
- 草稿预览：
- 是否保存成功：

## 后台检查

- [ ] 标题显示正常。
- [ ] 封面显示正常。
- [ ] 正文排版没有错位。
- [ ] 图片没有丢失。
- [ ] 手机预览已看过。
""",
    )

    write_file(
        folder / "06-发布复盘.md",
        f"""
# {title} - 发布复盘

{(ASSETS_DIR / "review-template.md").read_text(encoding="utf-8")}
""",
    )

    update_index(title, folder)
    return folder


def main() -> None:
    parser = argparse.ArgumentParser(description="创建公众号文章发布工作台")
    parser.add_argument("title", help="文章标题或选题名")
    parser.add_argument("--brief", default="", help="初始想法/背景")
    args = parser.parse_args()

    folder = create_workspace(args.title, args.brief)
    print(folder)


if __name__ == "__main__":
    main()
