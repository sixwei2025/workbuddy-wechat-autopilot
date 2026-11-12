#!/usr/bin/env bash
# 公众号自动化 skill · 一键安装
# 用法：bash install.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONF="$HOME/.config/wechat-autopilot"

echo "==> skill 目录：$ROOT"
echo "==> 配置目录：$CONF"

mkdir -p "$CONF"

# 凭证模板
if [ ! -f "$CONF/wechat.env" ]; then
  cp "$ROOT/assets/wechat.env.example" "$CONF/wechat.env"
  chmod 600 "$CONF/wechat.env"
  echo "    已创建 $CONF/wechat.env（请填 AppID / AppSecret / 白名单 IP）"
else
  echo "    $CONF/wechat.env 已存在，跳过"
fi

# 事实基线
if [ ! -f "$CONF/fact-baseline.md" ]; then
  cp "$ROOT/assets/fact-baseline.example.md" "$CONF/fact-baseline.md"
  echo "    已创建 $CONF/fact-baseline.md（请填你自己的身份与数字）"
else
  echo "    $CONF/fact-baseline.md 已存在，跳过"
fi

# Python 依赖
echo "==> 检查 Python 依赖"
python3 - <<'PY' || echo "    ⚠️ 依赖不全，封面渲染可能失败：pip3 install pillow numpy scipy pyyaml"
mods = []
for m in ("PIL", "numpy", "scipy", "yaml"):
    try:
        __import__(m)
        mods.append(f"{m} ok")
    except Exception:
        mods.append(f"{m} MISSING")
print("    " + "  ".join(mods))
PY

# 字体检查
if [ -f "$ROOT/skills/wechat-cover-skill/assets/fonts/NotoSansCJKsc-Black.otf" ]; then
  echo "    超粗中文字体：已随包提供（OFL 许可）"
else
  echo "    ⚠️ 缺 NotoSansCJKsc-Black.otf，封面字重会偏轻"
fi

echo ""
echo "==> 完成。下一步："
echo "    1) 编辑 $CONF/fact-baseline.md 填身份与数字"
echo "    2) 编辑 $CONF/wechat.env 填公众号凭证"
echo "    3) 在对话里说「今日日报」或「写篇文章，发草稿箱」"
