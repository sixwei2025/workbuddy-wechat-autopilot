# 主号视觉宪章 · 高客单价版

> 🔴 **2026-11-03 起排版脚本变更**：`md2wechat_layout.py` / `md2wechat_v3.py` / `md2wechat_v2_card.py`
> 三个旧脚本已归档到 `~/.workbuddy/skills-archive/排版旧方案-20261103/`，**本文中提到它们的地方一律作废**。
> 现行方案：`wechat-formatter` 六套骨架按发布日轮换 → 转换用
> `wechat-ops-team/skills/wechat-auto-publisher/scripts/markdown_to_wechat_article.py --theme <id>`。
> 骨架：周一 magazine-card / 周二 classic-edit / 周三 minimal-line / 周四 zen-space / 周五 ticket / 周六 journal。


> ⚠️ **优先级说明（2026-09-12）**：本文件与
> `references/editorial-contract.md`
> 冲突时，**以后者为准**。已确认的冲突点：
> ① 文末**不加**署名 / 身份介绍 / 品牌落款（本文件第三节「签名：袁六伟 · 一人AI公司」作废）；
> ② 封面默认通道已更新，见第二节补充；
> ③ 配图要求已从「每章一张」改为「大量真实截图 + 小黑图组合」，具体见第四节。

> 目标：让点进文章的人在第 3 秒判断「这个博主很贵，客单价很高」。
> 方法论一句话：**贵 = 克制。**

详细设计与禁用清单见 `wechat-formatter/references/design-system.md` 与 `wechat-cover-generator/references/style_system.md`。本文件只做流程层面的统一约定。

---

## 一、视觉宪法（每篇都适用）

| 维度 | 规则 |
|---|---|
| 强调色 | 正文强调色为品牌红 `#C7352D`（2026-09-15 起，覆盖旧蓝/琥珀），每篇**只有 1 个**，且出现 ≤ 8 处。琥珀 `#C99A4E` / 绛红 `#8A2E1F` 仅保留给封面主题。 |
| 字体 | 标题一律**衬线宋体**，正文无衬线。绝无衬线粗体大字撑场（抖音感）。 |
| 留白 | 章节间距 72px、段间距 16px、左右各 20px 安全边距。**留白主导版面**。 |
| 分隔 | 1px hairline，不用色块、圆角矩形、圆形徽章。 |
| 配图 | 描边卡片或纯文字，**无实心亮色块**。背景纯色（NOIR #0B0C0E / IVORY #FBFAF7），禁渐变发光。 |
| Emoji | 全文不出现。封面与配图都不出现。 |
| 配色总量 | 一篇 ≤ 3 色（底 + 文 + 强调）。旧版的"蓝+金+青+紫"四色同框是便宜感来源。 |

**自检一句话**：把文章缩到 25% 看一眼。看到「一堆色块和亮色」= 便宜；看到「大面积留白 + 一条细线 + 一行安静的字」= 贵。

---

## 二、统一的封面通道（解决三套并存冲突）

旧版有**三套封面流程并存**，各说各话，导致每篇封面气质都不一样：

1. `社媒爆款封面` skill：imagegen 背景 + 高级后期
2. `wechat-cover-gewechat-cover-generator-gold` 等 4 套：霓虹光条蓝金风
3. `wechat-formwechat-formatter套杂志风 HTML：ECONOMIST / MONOCLE / WIRED 等按星期轮换

**V6.0 统一规则**：

| 场景 | 唯一通道 |
|---|---|
| **所有主号新文章封面（默认）** | `wechat-cover-generator/scriptswechat-cover-generator.py` |
| 用户明确点名"蓝金""紫金""赛博" | `wechat-cover-generator/scripts/render_wechat_wechat-cover-generator |
| 用户明确点名"杂志 ECONOMIST 风格" | `公众号排版` V6 的wechat-formatter杂志风封面时） |
| 用户明确要求走 covcover-pop | `cover-cover-popl（保留作为可选节点，不默认走） |

**封面的两个 PRESTIGE 主题**：
- `noir-amber`：暗夜琥珀，主号默认
- `ivory-ink`：象牙墨，深度长文 / 用户要求白底时

**禁止再做的事**：
- 不要再用 7 套杂志风 HTML 封面（V5.x 按星期轮换）作为默认
- 不要再用 cover-popcover-pop 重画袁总的脸——人像必须走 `render_prestige_cover.py` 的合成通道（身份锁）

### ⚠️ ref-clone「在位擦字」的自动检测有已知缺陷（2026-09-29 实测）

`wechat-cover-generator/scripts/render_brand_cover.py` 的自动擦除矩wechat-cover-generator信任**，实测两个坑：

1. **矩形余量小于脚本的 14px 羽化半径**：自动矩形各留 8–10px，旧字的抗锯齿边缘正好落在羽化区内被保留。
   底部卖点条更严重——旧字真实下沿在 y=848，自动矩形只到 845，**整行下沿漏擦**（把图提亮 3.2× 可见残影）。
2. **整行通擦会伤背景**：一路擦到 x≈1457 会把底图右侧的结构（如手机卡片）一起插值，擦出一块发糊的暗带。

**正确做法**：先 `--detect` 看行区间，再**逐行实测旧字墨迹范围，左右各留 ~20px、上下各留 ~22px**，手写 `erase` 矩形传给脚本，让羽化落在干净背景上。

**验收判据（缺一不可）**：
- 逐像素比对新旧图，确认 **x ≥ 擦除区右界之外的区域与原图最大差值 = 0.0**（证明背景与人像一像素未动）
- 四条旧字带与原图的相关性是否降到接近 0（证明无结构化残影）
- 把新图提亮 2–3 倍放大目检标题右端、第二行下方、卖点条右侧，看有无残影/发糊带
- 仍须实际打开 200px 缩略图逐项确认（脚本跑完 ≠ 审美通过）

---

## 三、统一的正文排版通道

主号正文**只走** `公众号排版` V6.0。

- 章节：H2 wechat-formatter）+ 衬线宋体
- 段落：16px 行距 1.9 段距 16px，按 2–3 行（约 40–60 字）切短段落，禁一句一段的短视频字幕式排版
- 强调：全文 ≤ 8 处，品牌红 `#C7352D`
- 配图：每章一张，900×506，三种布局（对比两栏 / 三栏要点 / 金句图），描边卡片或纯文字
- 金句：上下细线夹住，18px 衬线，**不用色块、不用左边框色条**
- 签名：底部细线 + 「袁六伟 · 一人AI公司」

详见 `wechat-formatter/references/design-system.mdwechat-formatter

---

## 四、正文配图策略（不变，保留为原则）

默认优先级：

1. 真实截图（WorkBuddy 实测操作、客户案例）—— 6-10 张
2. 官方页面/报告/数据图 —— 0-2 张
3. 小黑配图（`小黑风正文配图`，解释抽象关系）—— 2-4 张
4. 禁止 AI 概念图伪装截图

每章一张配图，配图在正文之前。

**配图本身也要遵守视觉宪法**：纯色底、描边卡片或纯文字、无渐变、无亮色实心块。**不能再用 V5.x 的深蓝 `#0f1e3d` + 亮蓝 `#3b82f6` 实心卡片**——那是便宜感的最大单一来源。

---

## 五、桌面成品封面与 PRESTIGE 渲染的关系

```
桌面 07 封面文件 / 04_个人IP视觉资产/封面文件夹
   ↓（视觉参考）
PRESTIGE 渲染器的设计锚点
```

- 桌面成品作为**风格样张**（配色、构图、人像姿势的参考），不直接挪用（避免与历史文章撞脸）
- 风格样张里如果有完美匹配的成品（标题、主题、人物都一致），可直接复制到 `assets/cover.<ext>` 使用
- 否则用 PRESTIGE 渲染器生成新封面——它已经按桌面成品的高水准做了设计（衬线、克制、留白、细线、暖色琥珀）

---

## 六、交付前自检（一次性 checklist）

- [ ] 封面与正文主题一致（都是 noir-amber 或都是 ivory-ink）
- [ ] 全文强调色 ≤ 8 处，标题全衬线、正文全无衬线
- [ ] 无 emoji、无渐变、无发光、无阴影
- [ ] 段距 16px、章节距 72px（不是模板默认 20/35）
- [ ] 每个 H2 编号在标题上方独立行
- [ ] 配图是描边卡片或纯文字，无实心亮色块
- [ ] 缩到 25% 看一眼：留白主导，安静不吵
- [ ] 封面文件单独输出，2.35:1，200px 缩略自检图生成
- [ ] 输出到 `~/Desktop/公众号排版输出/`，**不是 `/mnt`**

---

## 七、真实截图获取：窗口级截图法（2026-09-12 实测可用）

主号要求「真实截图为主体证据」，但很多素材躺在**已登录的浏览器**里（知识星球、公众号后台等）。
AppleScript 控制 Chrome 会被系统自动化权限拒绝（错误码 `-10004`），**改用窗口级截图**：

```bash
# 1) 后台打开目标页（-g 不抢焦点，不打断用户当前操作）
open -g -a "Google Chrome" "https://wx.zsxq.com/"

# 2) 用 Quartz 找窗口，取 kCGWindowNumber
python3 -c "
import Quartz
wl = Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionAll, Quartz.kCGNullWindowID)
for w in wl:
    if w.get('kCGWindowOwnerName') == 'Google Chrome':
        b = w.get('kCGWindowBounds') or {}
        if b.get('Width', 0) > 1200:
            print(w.get('kCGWindowNumber'), w.get('kCGWindowName'), b)
"

# 3) 按窗口 ID 截图（2x 视网膜：1470×923 窗口 → 2940×1846）
screencapture -l <kCGWindowNumber> -x -o /tmp/shot.png
```

**必守规则**：

- `-g` 打开的新标签**不激活**，窗口显示的仍是原标签 → 只能截「当前已是目标页」的界面；
  想切页面需先让用户切，或换别的方式取证
- 截到非目标页（例如其他标签的私人对话）**一律不得使用**
- 使用前必须裁掉：浏览器地址栏（可能含 GROUP_ID 等内部标识）、左侧无关列表、他人个人信息
- 引用他人公开内容时保留作者身份与出处；涉及学员作业、聊天记录须先脱敏

---

## 八、兜底：headless 截图法（2026-09-28 实测可用）

**触发场景**：`Quartz` 模块在本机不可用（系统 python3 无 pyobjc，`import Quartz` 直接 `ModuleNotFoundError`），窗口级截图法走不通；或目标页是**公开网页**、不需要登录态。

```bash
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CH" --headless=new --no-sandbox --disable-gpu --hide-scrollbars \
  --virtual-time-budget=12000 --screenshot=/tmp/shot.png \
  --window-size=1440,1400 "https://目标网址"
```

**必守规则**：

- **`--no-sandbox` 不可省**：省略会报 `GPU process isn't usable. Goodbye.` 直接退出。
- `--virtual-time-budget=10000~15000` 用于等 JS 渲染的页面（微信开放文档、SPA 官网必加），否则容易截到空白。
- **用窄窗口（780–900px）截响应式页面**：多数官网会切成单列布局，天然去掉左侧导航，省掉裁图麻烦。
- ⚠️ **headless 有最小窗口宽度（2026-09-29 实测）**：直接传 `--window-size=375,H` **不会**得到 375px 版心——
  实际布局宽度被撑到约 500px，截图仍按 375px 输出，**结果是右侧被静默裁掉**，文字看着"少字"，
  但源 HTML/.json 内容其实是完整的（很容易误判成转换器丢字）。
  要真实手机版心必须**在页面里注入** `html,body{width:375px!important;overflow-x:hidden}.page-wrap{width:375px!important}`
  后再截图；判据：截图里文字换行点与源文本一致。
- ⚠️ **预览 HTML 必须放在图片同级目录**：`md2wechat_layout.py` 输出的 `src` 是 basename，预览 HTML 写进 `/tmp`
  会让 `src="xxx.png"` 全部 404（图上只显示空框）。做本地视觉预览时把 HTML 落在项目目录（或把 src 重写为 `assets/xxx.png`）。
- 截完必须**实际看图**确认命中目标章节、无无关广告块，再裁剪进 `assets/`。
- 微信指数 `index.weixin.qq.com` **本机不可达**（`ERR_CONNECTION_CLOSED`）。需要微信指数数据时改用其他取证方式，**不得编造数字或实测口径**。
- 只适用于**公开页面**；需登录态的页面（公众号后台、知识星球）仍走窗口级截图法。

### 文档类「真实文件内容」截图的手机可读性（2026-09-29 实测）

截真实 `.md`/表格当正文证据时，**渲染宽度决定生死**：

- 900px 宽 + 15px 字 → 在 375px 手机上正文只剩约 6px 高，**等于不可读**。
- 正确参数：**窄幅 760px + 正文 26px + 表格 23px**（`--force-device-scale-factor=2` 输出 2 倍图）。
  换算：23px × 2 ÷ (1444/375) ≈ 12px 实际显示高度，手机可直接读。
- 宽表只取与论点相关的列（单元格文字保持原文），比硬塞整表可读得多。
- 需要 viewer 时用「读取真实文件字节 → 原文渲染 → 截图」，**不要重写、不要增删文字**；
  成图性质是「真实文件内容证据」，不是产品界面截图，正文里不能当 UI 证据用。
