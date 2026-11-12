#!/usr/bin/env bash
# WorkBuddy 公众号全链路自动化 Skill (`wechat-autopilot`) · 一键安装与环境自检
# 用法：
#   bash install.sh           # 初始化配置 + 自检 + 自动挂载到已安装的 Agent 目录
#   bash install.sh --doctor  # 仅执行环境与依赖诊断
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONF="$HOME/.config/wechat-autopilot"
MODE="${1:-install}"

echo "=================================================================="
echo "  WorkBuddy 公众号全链路自动化 Skill (wechat-autopilot)"
echo "=================================================================="
echo "==> 仓库路径：$ROOT"
echo "==> 配置路径：$CONF"
echo ""

mkdir -p "$CONF"

if [ "$MODE" != "--doctor" ]; then
  echo "[1/4] 初始化本地私有配置（不覆盖已有文件）..."
  if [ ! -f "$CONF/wechat.env" ]; then
    cp "$ROOT/assets/wechat.env.example" "$CONF/wechat.env"
    chmod 600 "$CONF/wechat.env"
    echo "  ✅ 已创建 $CONF/wechat.env（请填入公众号 AppID / AppSecret / 白名单 IP）"
  else
    echo "  ⏭️  $CONF/wechat.env 已存在，保留原配置"
  fi

  if [ ! -f "$CONF/fact-baseline.md" ]; then
    cp "$ROOT/assets/fact-baseline.example.md" "$CONF/fact-baseline.md"
    echo "  ✅ 已创建 $CONF/fact-baseline.md（请填入你的身份、真实业务数字与口径红线）"
  else
    echo "  ⏭️  $CONF/fact-baseline.md 已存在，保留原配置"
  fi
  echo ""
fi

echo "[2/4] 检查 Python 3 与核心依赖..."
python3 - <<'PY' || echo "  ⚠️ 依赖不全，建议运行：pip3 install pillow numpy scipy pyyaml"
import sys
print(f"  🐍 Python {sys.version.split()[0]}")
mods = []
for m, pkg in (("PIL", "Pillow"), ("numpy", "numpy"), ("scipy", "scipy"), ("yaml", "PyYAML")):
    try:
        __import__(m)
        mods.append(f"✅ {pkg}")
    except Exception:
        mods.append(f"❌ {pkg}(缺失)")
print("  " + "  ".join(mods))
PY
echo ""

echo "[3/4] 检查渲染引擎（Chrome / 字体 / 校验脚本）..."
CHROME_FOUND=""
for c in "${CHROME_BIN:-}" \
         "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
         "/Applications/Chromium.app/Contents/MacOS/Chromium" \
         "$(command -v google-chrome 2>/dev/null || true)" \
         "$(command -v chromium 2>/dev/null || true)"; do
  if [ -n "$c" ] && [ -x "$c" ]; then
    CHROME_FOUND="$c"
    break
  fi
done
if [ -n "$CHROME_FOUND" ]; then
  echo "  ✅ 无头浏览器：$CHROME_FOUND"
else
  echo "  ⚠️ 未检测到 Chrome/Chromium（封面与数据卡渲染需要，可通过 CHROME_BIN 指定）"
fi

if [ -f "$ROOT/skills/wechat-cover-skill/assets/fonts/NotoSansCJKsc-Black.otf" ]; then
  echo "  ✅ 开源超粗黑体：NotoSansCJKsc-Black.otf（已内置，SIL OFL 1.1）"
else
  echo "  ⚠️ 缺少 NotoSansCJKsc-Black.otf，封面渲染将回退系统字体"
fi
echo ""

if [ "$MODE" != "--doctor" ]; then
  echo "[4/4] 检查并挂载 Agent Skills 目录..."
  for agent_dir in "$HOME/.workbuddy/skills" "$HOME/.claude/skills" "$HOME/.codex/skills" "$HOME/.agents/skills"; do
    parent_dir="$(dirname "$agent_dir")"
    if [ -d "$parent_dir" ]; then
      mkdir -p "$agent_dir"
      target="$agent_dir/wechat-autopilot"
      if [ ! -e "$target" ]; then
        ln -s "$ROOT" "$target"
        echo "  🔗 已软链挂载 → $target"
      else
        echo "  ✅ 已存在挂载 → $target"
      fi
    fi
  done
  echo ""
fi

echo "=================================================================="
echo "🎉 准备就绪！首次使用只需 2 步："
echo "  1) 编辑唯一事实源：\$EDITOR $CONF/fact-baseline.md"
echo "  2) 编辑公众号凭证：\$EDITOR $CONF/wechat.env（仅推草稿箱时需要）"
echo ""
echo "💬 然后直接对 Agent 说以下任意口令："
echo "  • 「今日日报」       —— 抓热点、过三门槛、出 3 个候选选题与标题"
echo "  • 「写文章」         —— 跑完 1–7 步，本地生成正文 + 配图 + 封面 + 排版 + 三重校验"
echo "  • 「发主号草稿箱」   —— 一路跑通并推入微信公众号草稿箱"
echo "  • 「修改这篇」       —— 在原目录修改并更新原 media_id 草稿"
echo "  • 「复盘一下」       —— 基于真实后台数据做同窗口复盘"
echo "=================================================================="
