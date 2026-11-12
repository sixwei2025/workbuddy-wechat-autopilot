# Tavily 查询模板速查

本文档收录袁六伟账号常用的 Tavily 查询组合，直接复制即可用。

## 一、按账号定位分类

### 一人公司 / 一人AI公司

```python
Tavily:tavily_search(
    query="一人公司 AI 智能体 实战",
    include_domains=["zhuanlan.zhihu.com", "mp.weixin.qq.com"],
    search_depth="advanced",
    time_range="week",
    max_results=8
)
```

### 智能体 / Agent / OpenClaw

```python
Tavily:tavily_search(
    query="AI Agent 智能体 落地 案例",
    include_domains=["zhuanlan.zhihu.com", "mp.weixin.qq.com", "36kr.com"],
    search_depth="advanced",
    time_range="week"
)
```

### AI副业 / 赚钱 / 月入

```python
Tavily:tavily_search(
    query="AI 副业 月入 实战",
    include_domains=["zhuanlan.zhihu.com", "xiaohongshu.com", "mp.weixin.qq.com"],
    search_depth="advanced",
    time_range="week"
)
```

### AI模型 / Claude / GPT / 前沿

```python
Tavily:tavily_search(
    query="Claude GPT 新模型 评测 对比",
    include_domains=["x.com", "news.ycombinator.com", "reddit.com", "zhuanlan.zhihu.com"],
    search_depth="advanced",
    time_range="week"
)
```

## 二、按平台分类

### 知乎专栏（最强情报源）

```python
Tavily:tavily_search(
    query="[关键词]",
    include_domains=["zhuanlan.zhihu.com"],
    search_depth="advanced",
    time_range="week",
    max_results=10,
    include_raw_content=True  # 抓全文
)
```

### 公众号文章

```python
Tavily:tavily_search(
    query="[关键词]",
    include_domains=["mp.weixin.qq.com"],
    search_depth="advanced",
    time_range="week",
    max_results=8
)
```

### 小红书（只能拿到博主主页+标题列表）

```python
Tavily:tavily_search(
    query="AI 工具 [场景]",
    include_domains=["xiaohongshu.com"],
    search_depth="advanced",
    max_results=5
)
# 注意：不要对单篇笔记URL用 extract，会返回"页面不见了"
# 正确用法：抓博主主页做画像分析
```

### 海外：X / HN / Reddit

```python
Tavily:tavily_search(
    query="[英文关键词]",
    include_domains=["x.com", "news.ycombinator.com", "reddit.com"],
    search_depth="advanced",
    time_range="week",
    max_results=5
)
```

## 三、深度挖取模板

当 TOP 内容需要全文时：

```python
Tavily:tavily_extract(
    urls=["URL1", "URL2", "URL3"],
    extract_depth="advanced",
    format="markdown",
    query="[用于相关性重排的查询词]"
)
```

## 四、竞品对标模板

```python
# 抓特定竞品公众号最近文章
Tavily:tavily_search(
    query="[竞品名] AI",
    include_domains=["mp.weixin.qq.com"],
    search_depth="advanced",
    time_range="month"
)

# 或用 tavily_crawl 抓博主主页
Tavily:tavily_crawl(
    url="https://zhuanlan.zhihu.com/people/[用户ID]",
    max_depth=2,
    limit=20,
    instructions="只抓取近期发布的AI相关专栏文章"
)
```

## 五、tavily_research 深度研究模式

当需要系统性调研一个话题（不仅仅找选题）时：

```python
Tavily:tavily_research(
    input="2026年Q1 AI智能体行业的关键事件、核心玩家动态、主要产品发布、投融资情况，重点关注对一人公司/个人开发者的影响",
    model="pro"  # pro 适合宽泛主题，mini 适合窄主题
)
```

这个模式自动多轮搜索、聚合、去重，直接给一份综合报告。**适合做周报/月报的底稿**。

## 六、避坑要点

1. **不要** 对小红书笔记单页 URL 用 `tavily_extract` → 大概率"页面不见了"
2. **不要** 对抖音/视频号页面用 Tavily → 客户端渲染内容拿不到
3. **不要** 把 `max_results` 设太高（>15）→ 相关性会迅速下降
4. **一定要** 用 `search_depth="advanced"` → basic 太浅
5. **一定要** 控制时间范围 → `time_range="week"` 或 `"day"`，避免翻到陈年老帖

## 七、信号强度评分速查

当拿到搜索结果后，快速评估信号：

| 信号 | 强度 | 说明 |
|------|------|------|
| Tavily score > 0.7 | ⭐⭐⭐⭐⭐ | 高度相关，优先读 |
| Tavily score 0.5-0.7 | ⭐⭐⭐⭐ | 相关，值得看 |
| Tavily score 0.3-0.5 | ⭐⭐⭐ | 参考 |
| Tavily score < 0.3 | ⭐⭐ | 大概率噪声 |
| 同话题跨3+平台 | ⭐⭐⭐⭐⭐ | 真爆款外溢 |
| 知乎正文 >3000字 | ⭐⭐⭐⭐ | 深度内容 |
| 标题含具体数字 | ⭐⭐⭐⭐ | 爆款基因 |
