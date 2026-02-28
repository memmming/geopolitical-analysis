# 地缘政治情报分析系统 (Geopolitical Intelligence Analysis System)

基于 n8n 工作流重构的本地化地缘政治情报分析系统，用于自动生成每日战略情报简报。

## 功能特性

- **RSS订阅聚合**: 从10个国际关系/安全源自动获取新闻
- **AI智能分析**: 使用 DeepSeek API 进行地缘政治分析
- **数据去重**: 自动过滤已处理文章
- **日报生成**: 自动合成高价值情报为战略报告
- **飞书推送**: 通过 Webhook 自动推送日报到飞书群
- **本地存储**: SQLite 数据库存储历史数据

## 技术栈

| 组件 | 技术 |
|------|------|
| 后端 | Python (FastAPI + asyncio) |
| 数据库 | SQLite |
| AI模型 | DeepSeek Reasoner |
| 图表 | Plotly |
| 报告推送 | 飞书 Webhook |

## 项目结构

```
geopolitical-analysis/
├── src/
│   ├── ai/                 # AI分析模块
│   │   ├── analyzers.py    # DeepSeek API集成
│   │   └── prompts/        # 系统提示词
│   ├── charts/             # 图表生成
│   │   └── generator.py    # Plotly图表生成器
│   ├── db/                 # 数据库
│   │   ├── models.py       # SQLAlchemy模型
│   │   └── repository.py   # 数据仓库
│   ├── feeds/              # RSS订阅
│   │   └── rss_fetcher.py  # RSS获取与解析
│   ├── feishu/             # 飞书推送
│   │   └── sender.py       # Webhook发送器
│   ├── config.py           # 配置文件
│   └── main.py             # 主流程编排
├── tests/                  # 测试文件
├── data/                   # 数据目录
│   └── geopolitical.db     # SQLite数据库
├── requirements.txt        # Python依赖
├── .env                    # 环境变量
├── run.py                  # 快速启动脚本
└── README.md              # 本文件
```

## 安装步骤

### 1. 克隆项目

```bash
cd C:\proj\ datamining\info_dyzz\geopolitical-analysis
```

### 2. 创建虚拟环境

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

创建 `.env` 文件（不会被提交到Git）：

```env
DEEPSEEK_API_KEY=你的DeepSeek_API密钥
DEEPSEEK_MODEL=deepseek-reasoner
FEISHU_WEBHOOK_URL=你的飞书Webhook_URL
```

> **注意**: `.env` 文件包含敏感信息，已在 `.gitignore` 中排除，不会提交到GitHub。

## 使用方法

### 验证RSS源

```bash
python run.py --validate-rss
# 或
python -m src.main --validate-rss
```

### 运行完整工作流

```bash
python run.py --run
# 或
python -m src.main --run
```

### 分析单篇文章

```bash
python run.py --analyze-one <article_id>
# 或
python -m src.main --analyze-one 1
```

### 运行测试

```bash
pytest tests/ -v
```

## 配置定时任务 (Windows)

### 方法一：使用任务计划程序

1. 打开 "任务计划程序" (Task Scheduler)
2. 创建基本任务:
   - 名称: `地缘政治情报日报`
   - 触发器: 每天运行 (建议时间: 12:00)
   - 操作: 启动程序
     - 程序: `python.exe`
     - 起始于: `C:\proj\ datamining\info_dyzz\geopolitical-analysis`
     - 参数: `run.py --run`

### 方法二：使用批处理文件

创建 `run_daily.bat`:

```batch
@echo off
cd /d "C:\proj\ datamining\info_dyzz\geopolitical-analysis"
call venv\Scripts\activate
python run.py --run
```

然后使用任务计划程序定期执行该批处理文件。

## 数据库说明

数据库位于 `data/geopolitical.db`，包含以下表：

### articles 表
- `id`: 文章ID
- `title`: 标题
- `url`: 链接 (唯一)
- `pub_date`: 发布日期
- `content`: 内容
- `source_domain`: 来源域名
- `source_name`: 来源名称
- `created_at`: 创建时间

### analyses 表
- `id`: 分析ID
- `article_id`: 关联文章ID
- `summary`: 摘要
- `category`: 分类
- `tags`: 标签 (JSON)
- `score`: 评分 (1-10)
- `deep_insight`: 深度洞察
- `impact_level`: 影响级别
- `status`: 状态 (进行中/完成)
- `created_at`: 创建时间
- `updated_at`: 更新时间

### reports 表
- `id`: 报告ID
- `report_date`: 报告日期
- `markdown_content`: Markdown内容
- `chart_data`: 图表数据 (JSON)
- `created_at`: 创建时间

## RSS源列表

1. Al Jazeera - https://www.aljazeera.com/xml/rss/all.xml
2. Foreign Affairs - https://www.foreignaffairs.com/rss.xml
3. Foreign Policy - https://foreignpolicy.com/feed/
4. Project Syndicate - https://www.project-syndicate.org/rss
5. The Conversation - https://theconversation.com/global/articles.atom
6. Eurasia Review - https://www.eurasiareview.com/feed/
7. War on the Rocks - https://warontherocks.com/feed/
8. Chatham House - https://www.chathamhouse.org/rss.xml
9. Defense One - https://www.defenseone.com/rss/all/
10. The Diplomat - https://thediplomat.com/feed/

## AI分析说明

### 分析器1：单篇文章分析
- **模型**: DeepSeek Reasoner
- **身份**: Stratfor/RAND 地缘政治情报官
- **输出**: summary, category, tags, score (1-10), deep_insight, impact_level

### 分析器2：日报生成
- **模型**: DeepSeek Reasoner
- **身份**: CICIR/CASS 智库研究员
- **输出**: Markdown报告 + 图表数据

### 评分标准
- **10分**: 战争爆发、核威慑、大国断交、脱钩制裁
- **8-9分**: 军事对峙、资源禁运、国际组织决议、恐怖袭击
- **5-7分**: 外交峰会、贸易协定、军售、领导人讲话
- **1-4分**: 例行外交祝贺、礼节性活动

只有评分 >= 7 的文章会进入每日报告。

## 常见问题

### Q: 如何修改RSS源？
A: 编辑 `src/config.py` 中的 `RSS_SOURCES` 列表。

### Q: 如何修改飞书Webhook URL？
A: 编辑 `src/config.py` 中的 `FEISHU_WEBHOOK_URL` 或 `.env` 文件。

### Q: 如何查看数据库内容？
A: 使用 SQLite 工具:
```bash
sqlite3 data/geopolitical.db
.tables
SELECT * FROM articles LIMIT 10;
```

### Q: 如何重置数据库？
A: 删除 `data/geopolitical.db` 文件，系统会自动重新创建。

### Q: RSS源无法访问怎么办？
A: 某些RSS源可能在国内无法直接访问，可以使用代理或更换RSS源。

## 日志

系统运行日志会输出到控制台，包含：
- RSS获取状态
- 文章分析进度
- 报告生成状态
- 飞书推送结果

## 许可

本项目基于原有 n8n 工作流重构，仅供学习和研究使用。
