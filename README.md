# 日期项目检索系统 📊

一个强大的日期自动检索和筛选项目的系统，支持多个数据源（GitHub、Gitee等），基于关键词进行智能匹配和排名。

## 功能特性 ✨

- ✅ **多数据源支持**: 集成GitHub和Gitee项目检索
- ✅ **智能关键词匹配**: 支持多层级关键词系统
  - 核心高频关键词
  - 细分业务关键词
  - 行业+场景+类型关键词
  - 招标类型关键词
  - 地域关键词
- ✅ **项目筛选**: 基于星标、更新时间、关键词匹配度等多维度筛选
- ✅ **智能排名**: 综合考虑项目热度、新鲜度、匹配度进行排名
- ✅ **定时任务**: 支持每日自动定时执行
- ✅ **多格式报告**: 生成Markdown和JSON格式报告
- ✅ **详细日志**: 完整的操作日志记录

## 项目结构 📁

```
.
├── daily_project_scraper.py    # 主程序，包含爬虫、筛选、排名、报告生成
├── keywords.json               # 关键词配置文件
├── config.py                   # 系统配置文件
├── requirements.txt            # Python依赖
├── README.md                   # 本文件
└── reports/                    # 报告输出目录
    ├── report_2026-04-29.md
    └── report_2026-04-29.json
```

## 安装 🚀

### 1. 克隆或下载项目

```bash
git clone <repository-url>
cd project-scraper
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置关键词

编辑 `keywords.json` 文件，添加你需要的关键词。系统支持以下关键词类型：

#### 核心高频关键词（必须组合用）
- 创业类: 创业、融资、创办
- 产品类: APP、网站、小程序、应用
- 技术类: 技术、算法、开发、编程
- 设计类: 设计、UI设计、视觉设计、交互
- 数据类: 数据库、大数据、数据分析、数据处理
- 运营类: 运营、市场、品牌、增长

#### 细分业务关键词（精准对中求）
- 融资方向: 融资计划书、融资方案、商业计划
- 设计工程类: 设计工程、工程设计方案
- 数字化应用系统: 数字化应用系统、云计算应用
- 建筑类: 建筑设计、景观设计、CAD图

#### 行业+场景+类型关键词（精准锁项目）
- 文娱类: 电影、视频、动漫、直播、游戏
- 医疗类: 医疗、医药、生物制药
- 电商类: 电商、O2O、社交电商、内容电商
- 教育类: 教育、在线教育、K12

#### 地域关键词（你的重点区域）
- 浙江: 浙江、杭州、宁波、绍兴、嘉兴
- 江苏: 江苏、南京、苏州
- 上海: 上海

### 4. 配置环境变量（可选）

创建 `.env` 文件：

```env
GITHUB_TOKEN=your_github_token_here
GITEE_TOKEN=your_gitee_token_here
GITHUB_API_TIMEOUT=10
GITEE_API_TIMEOUT=10
```

> **提示**: 使用认证令牌可以获得更高的API速率限制。

## 使用 💻

### 立即执行一次

```bash
python daily_project_scraper.py
```

### 启用定时任务

在 `daily_project_scraper.py` 中修改 `main()` 函数：

```python
# 注释掉立即执行
# scheduler.daily_task(core_keywords[:5])

# 启用定时任务，每天09:00执行
scheduler.schedule_daily(core_keywords, run_time="09:00")
```

然后运行：

```bash
python daily_project_scraper.py
```

### 自定义关键词搜索

```python
from daily_project_scraper import *

# 初始化
keyword_matcher = KeywordMatcher('keywords.json')
scraper = ProjectScraper(keyword_matcher)
project_filter = ProjectFilter(keyword_matcher)
scheduler = DailyScheduler(keyword_matcher, scraper, project_filter)

# 自定义关键词
custom_keywords = ['人工智能', '机器学习', '深度学习']

# 执行任务
scheduler.daily_task(custom_keywords, output_dir="custom_reports")
```

## 工作原理 🔄

### 1. 关键词匹配
系统从配置文件加载所有关键词，创建一个关键词集合。

### 2. 项目爬取
- 从GitHub API搜索匹配的项目
- 从Gitee API搜索匹配的项目
- 记录项目的基本信息（标题、URL、描述、星标等）

### 3. 项目筛选
基于以下条件进行筛选：
- 最小星标数（默认5）
- 最少关键词匹配数（默认1个）
- 最近更新时间（默认30天内）

### 4. 项目排名
综合考虑多个因素进行排名：
- **星标数** (50% 权重): 项目热度指标
- **更新新鲜度** (30% 权重): 项目活跃度指标
- **关键词匹配度** (20% 权重): 与搜索条件的相关性

### 5. 报告生成
生成两种格式的报告：
- **Markdown报告**: 易读的格式，包含完整的项目信息
- **JSON报告**: 结构化数据，便于进一步处理

## 配置说明 ⚙️

### config.py 主要配置项

```python
# 筛选配置
FILTER_CONFIG = {
    'min_stars': 5,        # 最小星标数
    'min_matches': 1,      # 最少关键词匹配数
    'max_days_old': 30     # 最多多少天没更新
}

# 排名权重配置
RANKING_WEIGHTS = {
    'stars': 0.5,      # 星标权重
    'recency': 0.3,    # 更新时间权重
    'matches': 0.2     # 关键词匹配度权重
}

# 调度配置
SCHEDULER_CONFIG = {
    'enabled': True,
    'run_time': '09:00',  # 每日运行时间
    'timezone': 'UTC'
}
```

## 输出示例 📋

### Markdown报告示例

```markdown
# 日期项目检索报告

**生成时间**: 2026-04-29 10:30:45

**发现项目总数**: 25

## GitHub (15个项目)

### 1. awesome-ai-project

- **URL**: https://github.com/user/awesome-ai-project
- **描述**: A comprehensive AI project collection
- **星标**: 1250
- **语言**: Python
- **更新时间**: 2026-04-28T15:30:00Z
- **匹配类别**: 
  - 核心高频关键词/产品类: 应用
  - 行业+场景+类型关键词/industries: 电影
```

### JSON报告示例

```json
{
  "generated_at": "2026-04-29T10:30:45.123456",
  "total_projects": 25,
  "projects": [
    {
      "source": "GitHub",
      "title": "awesome-ai-project",
      "url": "https://github.com/user/awesome-ai-project",
      "description": "A comprehensive AI project collection",
      "keyword": "应用",
      "stars": 1250,
      "language": "Python",
      "updated_at": "2026-04-28T15:30:00Z",
      "matched_categories": {
        "核心高频关键词/产品类": ["应用"]
      }
    }
  ]
}
```

## API限制 ⚠️

- **GitHub API**: 未认证用户60请求/小时，认证用户5000请求/小时
- **Gitee API**: 60请求/小时

建议配置API令牌以获得更高的限制。

## 日志 📝

系统会生成详细的日志文件 `project_scraper.log`，记录所有操作和错误。

```
2026-04-29 09:00:00 - INFO - 开始执行每日项目检索任务
2026-04-29 09:00:01 - INFO - 正在从GitHub搜索关键词: 创业
2026-04-29 09:00:02 - INFO - 从GitHub获取了12个项目
...
```

## 常见问题 ❓

### Q: 如何增加搜索结果数量？
A: 修改 `SCRAPER_CONFIG` 中的 `per_page` 值，或增加关键词数量。

### Q: 如何自定义筛选条件？
A: 在 `config.py` 中修改 `FILTER_CONFIG` 或在代码中传入自定义参数。

### Q: 如何更改排名权重？
A: 在 `config.py` 中修改 `RANKING_WEIGHTS` 字典。

### Q: 如何在云服务器上运行定时任务？
A: 
1. 使用 `systemd` service（Linux）
2. 使用 `cron` 任务（Linux/Mac）
3. 使用 `Task Scheduler`（Windows）

## 扩展建议 🎯

- [ ] 添加更多数据源支持（GitLab、Bitbucket等）
- [ ] 实现数据库存储历史数据
- [ ] 构建Web界面查看报告
- [ ] 添加邮件通知功能
- [ ] 支持自定义筛选规则
- [ ] 集成通知系统（钉钉、企业微信等）

## 许可证 📄

MIT License

## 贡献 🤝

欢迎提交Issue和Pull Request！

## 联系方式 📧

如有问题或建议，欢迎联系我们。

---

**最后更新**: 2026-04-29

祝你使用愉快！🎉
