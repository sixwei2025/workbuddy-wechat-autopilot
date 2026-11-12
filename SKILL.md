---
name: wechat-autopilot
description: 公众号全流程自动化总控。把一句话需求跑成主号草稿箱里的成品：热点选题 → 选题决策 → public-safe 写稿 → 真实截图配图 → 封面 → 六套骨架排版 → 三重校验 → 草稿箱投递 → 复盘。用户说「写篇文章」「今日日报」「发草稿箱」「做封面」「配个图」「复盘一下」时使用。内置唯一编辑标准、九个子技能、十个校验/发布脚本。默认只进草稿箱，绝不群发。
---

# 公众号全流程自动化总控

一句话：**把选题跑成草稿箱里的成品，中间不让用户补步骤、不让他点按钮、不让他核数据。**

这篇 SKILL.md 是总控。下面九个子技能是各段的专业执行者，不要绕过它们自己写。

---

## 一、开工三条铁律

1. **先读标准**：`references/editorial-contract.md` 是本工作流唯一的编辑规范来源。本文件任何摘要与它冲突，以它为准；用户当次最新要求又高于它。
2. **事实锁死**：身份、数字、履历、客户结果只从 `assets/fact-baseline.example.md` 对应的事实基线文件取，读不到就标「待确认」，不凭记忆编。
3. **只进草稿**：默认终点是草稿箱预览，不群发、不发布已上线文章。用户没说「发」，就不要上传。

---

## 二、五条视觉硬指标（2026-11 定版，优先于任何旧默认）

| 项 | 标准 |
|---|---|
| 配图优先级 | **真实截图 > 真实录屏 > 自绘可视化图**。有真图用真图，拿不到才画 |
| AI 插画 | 自动化公众号**不用小黑图、不用 AI 插画**；抽象关系只用少量数据卡补位 |
| 正文色 | 主色 `#C8102E`，红只点锚点 3–6 处；正文 15–16px，宽 677px |
| 段落 | 每段 ≤80 字（通常 40–60 字），按完整意思分段，不按句号碎切 |
| 封面 | 2.35:1；真人照片**绝不做黑白**；人像整个头必须完整，只让身体底部出血 |

---

## 三、九步流水线

每一步都写明「谁做 / 用什么 / 出什么 / 过什么闸」。闸不过就停在这一步，不许带病往下走。

### 第 1 步 · 选题与日报

- **口令**：「今日日报」「今天写什么」「帮我定选题」
- **用**：`skills/aihot`（24 小时 AI 资讯）→ `skills/ai-trending-topics`（真实爆款拆解）→ `skills/content-planner`（选题决策与标题）
- **出**：3 个有材料支撑的候选方向 + Top1 推荐 + 每个 6 个标题候选 + 一句风险
- **闸**：选题卡只写结论，不写长篇策划报告；资料不足先缩承诺，不许靠标题补救

### 第 2 步 · 建发布工作台

- **用**：`skills/wechat-auto-publisher/scripts/create_wechat_article_workspace.py`
- **出**：工作台目录（01 选题卡 / 02 资料包 / 03 发布稿 / 04 配图 / 05 发布记录 / 06 复盘）
- **闸**：改稿走原目录，不新建；只碰本任务相关材料

### 第 3 步 · 写 public-safe 正文

- **用**：`skills/yuanliuwei-writer`（第一人称实战派文风 v3）
- **出**：`03-public-safe发布稿.md`（纯正文，`# 标题` 开头）
- **闸**：
  - 开头两个自然段说清「与我什么关系、值得看什么、依据是什么」，不用履历和行业空话开场
  - 每篇给一个**能带走的东西**（清单 / 对照表 / 任务说明 / 判断框架），关键答案写在正文里，不藏进图片或私域
  - 别人的案例一律「我有一个朋友」开场；不能把外部案例写成自己战绩
  - 广告法禁用词（保证 / 一定 / 100% / 最 / 第一 / 唯一）零命中
  - 正文零引流：不贴二维码、不写加微信进群领资料

### 第 4 步 · 真实配图

- **用**：`skills/article-illustrator`（配图清单与位置规划）+ 真实界面截图（浏览器 / 终端 / 产品页现截现用）
- **出**：8–14 张真实截图（长文 ≥8），文件名进正文 `assets/xxx.png`
- **闸**：
  - 截图卡先裁掉价格、半截卡片、左侧任务列表等噪音再上舞台
  - 隐私红线：「数据管理」「记忆与进化」等会露未发布内容的页面一律弃用或裁掉
  - 每张图必须回答一个具体读者问题；只有输入没有输出的截图不算证据
  - 出图后必读实际像素确认没破图——上传回执 13/13 不等于没破图

### 第 5 步 · 封面

- **用**：`skills/wechat-cover-skill`（brief 驱动，HTML + headless Chrome 渲染）
- **出**：2350×1000 母版 → 900×383 横封面 + 带完整脸的 1:1 方图 + `cover_sheet.png` 缩略图总览
- **闸**：脚本自带几何硬闸（压脸 / 出血 / 超宽 / 1:1 缺脸 → exit 2），不过就改 brief 重渲，不许绕；必须亲眼看 200px 缩略图

### 第 6 步 · 排版（六套骨架）

- **用**：`skills/wechat-formatter` + `skills/wechat-auto-publisher/scripts/markdown_to_wechat_article.py --theme <id>`
- **出**：`article.local-images.json`（HTML + 草稿 JSON）
- **闸**：
  - 六套骨架 `magazine-card / classic-edit / minimal-line / zen-space / ticket / journal` **按内容结构、长度、框架选，不按星期轮换**；一篇一套，不许混搭
  - 不要求用户选骨架，自己判断
  - 转换后**必须**跑装配：`python3 scripts/apply_theme_shell.py --article <json> --theme <id> --out <json>`（主题专属开篇 / 目录 / 章节 / END 靠它补，缺了校验器直接拦）
  - 正文不重复标题，不留本地路径和占位符

### 第 7 步 · 三重校验

按顺序跑，三个都过才允许投递：

```bash
# ① 文章结构闸（段落长度 / 图片数 / 重复标题 / 本地路径 / 占位符）
python3 skills/wechat-auto-publisher/scripts/validate_wechat_article.py \
  --article article.local-images.json --max-paragraph 80

# ② AI 味检测（只出报告不改稿）
python3 scripts/check_ai_tone.py 03-public-safe发布稿.md --json ai-tone.json

# ③ 广告法禁用词审计
python3 scripts/banned_word_audit.py 03-public-safe发布稿.md
```

- **闸**：AI 味报告先给人看，人点头后只改命中句、最小改动、改完复测。判据：翻案句 ≤2、结论冒号 ≤6、顿号连排 ≤4

### 第 8 步 · 投草稿箱

- **用**：`skills/wechat-auto-publisher/scripts/` 或 `scripts/publish_wechat_via_ssh.py`（固定 IP 服务器出口）
- **顺序**：`find_draft_via_fixed_ip.py` 查重 → 有同标题草稿就 `update`，没有就 `add` → 多条同名或结果冲突立刻停
- **闸**：
  - 大 payload 被腾讯 WAF 501 拦时，改「先 `draft/delete` 旧稿 + 重 `add`」
  - 上传回执 ok 之后**必须**验 `media_id` + 回读 CDN 图片，回执 ok ≠ 成功
  - 不打印密钥，不改网络和服务器配置

### 第 9 步 · 记录与复盘

- **出**：`05-草稿箱发布记录.md`（账号 / media_id / 校对结果 / 时间）
- **复盘**：只有用户要求且拿到真实后台数据才做，填 `06-发布复盘.md`；缺数据写「不可得」，不填 0，不把草稿回执当阅读表现

---

## 四、五个口令（用户只需要说这几个词）

| 口令 | 动作 |
|---|---|
| **今日日报** | 只做选题和日报，不写稿不上传 |
| **写文章** | 跑完 1–7 步，出可投递成品，停 |
| **发主号草稿箱** | 跑完 1–8 步，落草稿箱。这句本身就是授权，不再追问 |
| **修改这篇** | 读现有成品，更新原 `media_id`，保留旧版，不新增重复草稿 |
| **复盘一下** | 第 9 步，需真实数据 |

---

## 五、目录地图

```
SKILL.md                       ← 本文件，总控
references/
  editorial-contract.md        ← 唯一编辑标准（冲突以它为准）
  publishing-notes.md          ← 发布服务器与封面规范
  typography.md                ← 排版细则
  visual-policy.md             ← 视觉与配图政策
  public-safety.md             ← 对外安全口径
  roles/                       ← 六个角色定义（可选：多角色编排时加载）
scripts/
  apply_theme_shell.py         ← 六套骨架装配（第 6 步必跑）
  check_ai_tone.py             ← AI 味检测（第 7 步）
  banned_word_audit.py         ← 广告法禁用词审计（第 7 步）
  publish_wechat_via_ssh.py    ← SSH 固定 IP 投递（第 8 步）
assets/
  fact-baseline.example.md     ← 事实基线模板（第一件事：抄一份填成你自己的）
  topic-card-template.md       ← 选题卡模板
  source-pack-template.md      ← 资料包模板
  public-safe-checklist.md     ← 对外安全检查清单
  draft-record-template.md     ← 发布记录模板
  review-template.md           ← 复盘模板
  wechat.env.example           ← 公众号 API 凭证模板
  ending-poster-product.jpg    ← 文末产品海报（不带二维码）
  owner_portrait.jpg           ← 封面人像底板
skills/                        ← 九个子技能，各段执行者
  aihot/                       ← 24 小时 AI 资讯
  ai-trending-topics/          ← 爆款选题挖掘
  content-planner/             ← 选题决策与标题
  yuanliuwei-writer/           ← 第一人称实战派文风
  article-illustrator/         ← 配图清单规划
  wechat-cover-skill/          ← 封面渲染
  wechat-formatter/            ← 六套骨架 + 主题定义
  wechat-auto-publisher/       ← 转换 / 校验 / 投递脚本
  ian-xiaohei-illustrations/   ← 手绘解释图（本工作流默认关闭，保留备用）
```

---

## 六、首次使用（只做一次）

```bash
bash install.sh                       # 建配置目录、拷凭证模板
cp assets/fact-baseline.example.md ~/.config/wechat-autopilot/fact-baseline.md
$EDITOR ~/.config/wechat-autopilot/fact-baseline.md   # 填你自己的身份与数字
$EDITOR ~/.config/wechat-autopilot/wechat.env         # 填 AppID / AppSecret / 白名单 IP
```

凭证只放 `~/.config/wechat-autopilot/wechat.env`，**永不进仓库、永不打印**。

---

## 七、环境依赖

- Python 3 + Pillow / numpy / scipy / PyYAML（封面渲染）
- Chrome 或 Chromium（`CHROME_BIN` 可指定）
- 超粗中文字体（思源黑体 Heavy / Noto Sans CJK SC Black；仓库已带 `NotoSansCJKsc-Black.otf`，OFL 许可）
- 公众号主号 AppID / AppSecret + IP 白名单服务器（API 只接受白名单 IP 出口）
- 图像生成能力、浏览器或 Computer Use（实时截图）、Web 搜索（选题）

---

## 八、边界

- 不承诺阅读量、原创标记、收益或封面满分。目标是争取 2–5 万阅读，这是目标不是承诺。
- 不虚构客户、朋友、交易、实测成功和现场。实时操作没跑通就如实报告未完成。
- 不用无数据支撑的分数（「95 分」「爆款概率 80%」）自我验收。
- 不擅自建定时任务、不索要账号密码、不在文末加署名落款。
- 修改 skill 本身不等于授权更新历史草稿。
