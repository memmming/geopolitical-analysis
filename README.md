# 地缘政治情报分析系统

自动化每日战略情报简报生成工具。

## 功能

- RSS 订阅聚合（10个国际关系/安全源）
- DeepSeek AI 智能分析
- 自动生成战略日报
- 飞书 Webhook 推送

## 快速开始

```bash
# 1. 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量 (.env)
DEEPSEEK_API_KEY=你的API密钥
FEISHU_WEBHOOK_URL=你的飞书Webhook

# 4. 运行
python run.py --run
```

## 常用命令

| 命令 | 说明 |
|------|------|
| `python run.py --run` | 运行完整工作流 |
| `python run.py --validate-rss` | 验证 RSS 源 |
| `python run.py --run --score 8` | 只分析高评分(≥8)文章 |
| `python run.py --run --filter-hours 24` | 24小时内文章 |
| `pytest tests/ -v` | 运行测试 |

## 项目结构

```
src/
├── config.py          # 配置（RSS源、阈值等）
├── main.py            # 主流程
├── ai/analyzers.py    # DeepSeek API
├── feeds/rss_fetcher.py
├── db/repository.py
├── charts/generator.py
└── feishu/sender.py
```

## 配置

修改 `src/config.py` 或 `.env`：
- `RSS_SOURCES` - RSS 源列表
- `HIGH_SCORE_THRESHOLD` - 进入日报的评分阈值（默认7）
- `ARTICLE_TIME_FILTER_HOURS` - 文章时间过滤（默认24）

## 定时任务 (Windows)

创建 `run_daily.bat`:
```batch
@echo off
cd /d "你的项目路径"
venv\Scripts\python.exe run.py --run
```
添加到任务计划程序。

## 评分标准

- 10分：战争爆发、核威慑、大国断交
- 8-9分：军事对峙、资源禁运
- 5-7分：外交峰会、贸易协定
- 1-4分：例行外交活动

评分 ≥7 的文章进入每日报告。
