# WorkBuddy 公众号自动化 · 全链路 Skill

把一个选题跑成微信公众号草稿箱里的成品。选题、写稿、配图、封面、排版、校验、投递、复盘，一条流水线全包。

不是提示词模板。是**能跑的工程**：22 个脚本、9 个子技能、1 套唯一编辑标准。

---

## 它解决什么

以前写一篇公众号：开六个窗口、复制粘贴、手动排版、逐张传图、后台点二十次。
现在：说一句「写篇关于 XX 的文章，发草稿箱」，然后看它跑完。

真正省掉的不是打字时间，是**每次都要重新讲一遍的那些规矩**——段落多长、红标在哪、封面人像怎么摆、哪句话不能写、投递前必须验什么。这些规矩现在写在文件里，不写在人脑里。

---

## 九步流水线

| 步 | 环节 | 执行者 | 关键闸门 |
|---|---|---|---|
| 1 | 选题与日报 | `skills/aihot` → `ai-trending-topics` → `content-planner` | 3 个有材料的候选，标题逐一核对正文能否兑现 |
| 2 | 建发布工作台 | `create_wechat_article_workspace.py` | 改稿走原目录，不新建 |
| 3 | 写 public-safe 正文 | `skills/yuanliuwei-writer` | 能带走的东西写进正文；广告法禁用词零命中；正文零引流 |
| 4 | 真实配图 | `skills/article-illustrator` + 现截现用 | 8–14 张真图；每张回答一个读者问题；隐私先打码 |
| 5 | 封面 | `skills/wechat-cover-skill` | 几何硬闸不过就重渲；人像头部必须完整 |
| 6 | 六套骨架排版 | `skills/wechat-formatter` + `apply_theme_shell.py` | 一篇一套骨架；装配漏了校验器直接拦 |
| 7 | 三重校验 | `validate` + `check_ai_tone` + `banned_word_audit` | 三个都过才允许投递 |
| 8 | 投草稿箱 | `publish_wechat_via_ssh.py` | 先查重再 add/update；回执 ok 后必验 media_id 与 CDN 图 |
| 9 | 记录与复盘 | 记录模板 | 缺数据写「不可得」，不填 0 |

---

## 五个口令

说这几个词就够了，不用解释流程：

- **今日日报** — 只出选题，不写稿
- **写文章** — 跑完 1–7 步，出可投递成品
- **发主号草稿箱** — 一路到草稿箱（这句本身就是授权）
- **修改这篇** — 更新原 media_id，保留旧版
- **复盘一下** — 第 9 步，要真实数据

---

## 安装

```bash
git clone <this-repo> wechat-autopilot
cd wechat-autopilot
bash install.sh
```

然后填两个文件：

1. `~/.config/wechat-autopilot/fact-baseline.md` — 你的身份、数字、口径红线（**唯一事实源**）
2. `~/.config/wechat-autopilot/wechat.env` — AppID / AppSecret / 白名单 IP

最后把整个目录放进你的技能目录（如 `~/.workbuddy/skills/`），或在支持 skill 的智能体平台里上传本仓库。

---

## 环境依赖

- Python 3 + Pillow / numpy / scipy / PyYAML
- Chrome 或 Chromium（`CHROME_BIN` 可指定）
- 超粗中文字体：仓库自带 `NotoSansCJKsc-Black.otf`（SIL OFL 1.1，可随包分发）
- 公众号 AppID / AppSecret + IP 白名单（API 只接受白名单 IP 出口，所以要走固定 IP 服务器）
- 图像生成、浏览器操作、Web 搜索（选题阶段）

---

## 不含什么

- **不含任何账号密钥**。凭证模板是占位符，真实值只在你本机 `~/.config/`。
- **不含你的事实基线**。模板是空的，身份和数字得自己填——这也是唯一必须自己做的事。
- 不承诺阅读量、原创标记、收益或封面满分。目标是争取 2–5 万阅读，是目标不是承诺。

---

## 目录

```
SKILL.md                      总控（九步流水线）
references/editorial-contract.md   唯一编辑标准（冲突以它为准）
references/roles/             六个角色定义（可选多角色编排）
scripts/                      装配 / AI 味检测 / 禁用词审计 / SSH 投递
assets/                       模板、海报、人像、凭证示例
skills/                       九个子技能
```

---

## 许可

本仓库内容归作者所有。第三方组件许可：

- `wechat-formatter` 六套骨架：源自 `sixwei2025/ai-tool-review-wechat-skill`（MIT）
- `wechat-cover-skill`：源自 `sixwei2025/wechat-cover-skill`（MIT）
- `NotoSansCJKsc-Black.otf`：SIL Open Font License 1.1
