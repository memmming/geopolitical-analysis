# 地缘政治情报分析系统 - 实施总结

## 项目概述

本项目基于 n8n 工作流重构，构建了一个独立的本地化地缘政治情报分析系统，实现了从 RSS 订阅聚合到 AI 智能分析，再到日报生成和飞书推送的完整工作流。

## 已实现的功能

### 1. RSS 订阅获取模块 (`src/feeds/rss_fetcher.py`)
- ✅ 并发获取 10 个国际关系/安全源的 RSS 订阅
- ✅ 自动过滤 24 小时内的文章
- ✅ URL 去重功能（检查数据库）
- ✅ RSS 数据完整性验证（title, link, content）
- ✅ 源验证功能（`validate_all_sources`）

### 2. AI 分析引擎 (`src/ai/analyzers.py`)
- ✅ 仅使用 DeepSeek API 进行文章分析
- ✅ 分析器1：单篇文章分析（Stratfor/RAND 身份）
- ✅ 分析器2：日报生成（CICIR 智库身份）
- ✅ 批量分析支持（并发处理）
- ✅ JSON 响应解析（支持 Markdown 代码块）

### 3. 数据库层 (`src/db/models.py`, `src/db/repository.py`)
- ✅ SQLite 数据库存储
- ✅ 三个核心表：articles, analyses, reports
- ✅ 完整的 CRUD 操作封装
- ✅ 状态跟踪（进行中 → 完成）
- ✅ 批量操作支持

### 4. 图表生成模块 (`src/charts/generator.py`)
- ✅ 使用 Plotly 生成本地图表
- ✅ 4 种图表类型：
  - 关键涉事方（横向条形图）
  - 战略领域分布（圆环图）
  - 安全等级（半圆仪表）
  - 情报源分布（条形图）
- ✅ 文本摘要生成（用于飞书消息）

### 5. 飞书推送模块 (`src/feishu/sender.py`)
- ✅ Webhook 消息发送
- ✅ Markdown 格式支持
- ✅ 错误消息格式化
- ✅ 成功摘要格式化

### 6. 主流程编排 (`src/main.py`)
- ✅ 完整的每日工作流：
  1. 获取 RSS 订阅
  2. 过滤 + 去重
  3. AI 分析（单篇）
  4. 生成日报（高价值文章）
  5. 生成图表
  6. 飞书推送
  7. 更新状态
- ✅ 命令行界面支持
- ✅ 单篇文章分析功能
- ✅ RSS 源验证功能

## 项目结构

```
geopolitical-analysis/
├── src/
│   ├── ai/
│   │   ├── analyzers.py          # DeepSeek API 集成
│   │   └── prompts/              # 系统提示词
│   ├── charts/
│   │   └── generator.py          # Plotly 图表生成
│   ├── db/
│   │   ├── models.py             # SQLAlchemy 模型
│   │   └── repository.py         # 数据仓库
│   ├── feeds/
│   │   └── rss_fetcher.py        # RSS 获取与解析
│   ├── feishu/
│   │   └── sender.py             # 飞书 Webhook 发送
│   ├── config.py                 # 配置文件
│   └── main.py                   # 主流程编排
├── tests/                        # 测试文件
├── data/
│   └── geopolitical.db           # SQLite 数据库
├── requirements.txt              # Python 依赖
├── .env                          # 环境变量
├── README.md                     # 使用文档
├── run.py                        # 快速启动脚本
├── run_daily.bat                 # Windows 定时任务脚本
├── setup_task.ps1                # PowerShell 任务设置脚本
├── setup.py                      # 安装脚本
└── check_install.py              # 安装检查工具
```

## 配置说明

### RSS 源（10个）
1. Al Jazeera
2. Foreign Affairs
3. Foreign Policy
4. Project Syndicate
5. The Conversation
6. Eurasia Review
7. War on the Rocks
8. Chatham House
9. Defense One
10. The Diplomat

### DeepSeek API
- API Key: `REDACTED_API_KEY`
- 模型: `deepseek-reasoner`
- 基础 URL: `https://api.deepseek.com/v1`

### 飞书 Webhook
- URL: `REDACTED_WEBHOOK`
- 消息类型: `text`

### 评分阈值
- 高价值文章: score >= 7
- 时间过滤: 24 小时内

## 使用方法

### 安装依赖
```bash
pip install -r requirements.txt
# 或运行
python setup.py
```

### 验证 RSS 源
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

### 配置 Windows 定时任务

**方法一：使用批处理文件**
1. 编辑 `run_daily.bat`（已预配置）
2. 使用任务计划程序定期执行该文件

**方法二：使用 PowerShell 脚本**
1. 以管理员身份运行 PowerShell
2. 执行: `.\setup_task.ps1`
3. 输入凭据完成配置

## 测试

### 运行所有测试
```bash
pytest tests/ -v
```

### 运行特定测试文件
```bash
pytest tests/test_rss_fetcher.py -v
pytest tests/test_charts.py -v
pytest tests/test_feishu.py -v
pytest tests/test_analyzers.py -v
pytest tests/test_rss_validation.py -v
```

## 与原 n8n 工作流的差异

| 组件 | n8n 工作流 | 本地应用 |
|------|-----------|---------|
| AI 模型 | DeepSeek + Gemini | 仅 DeepSeek |
| 报告推送 | Gmail | 飞书 Webhook |
| 数据存储 | Notion API | SQLite 本地数据库 |
| 图表生成 | QuickChart.io | Plotly 本地生成 |
| 任务调度 | n8n 调度器 | Windows 任务计划程序 |
| 部署方式 | 云端/本地 | 纯本地 |

## 技术优势

1. **完全本地化**: 数据存储在本地 SQLite，无需依赖 Notion
2. **成本更低**: 仅使用 DeepSeek API，无需 Gemini
3. **部署简单**: 单机运行，无需 n8n 服务器
4. **易于维护**: Python 代码，便于修改和扩展
5. **图表可控**: Plotly 本地生成，样式可定制

## 未来改进方向

1. **增加 RSS 源**: 支持更多国际关系/安全源
2. **Web 界面**: 使用 FastAPI + Vue.js 构建 Web 管理界面
3. **多语言支持**: 支持英文、中文双语言报告
4. **历史分析**: 支持查询历史数据和趋势分析
5. **自定义通知**: 支持邮件、微信等多种推送方式
6. **代理支持**: 为 RSS 源添加代理配置

## 注意事项

1. **RSS 源访问**: 部分 RSS 源可能需要代理才能访问
2. **API 配额**: DeepSeek API 有调用限制，请注意配额使用
3. **数据库备份**: 建议定期备份 `data/geopolitical.db`
4. **错误处理**: 网络错误或 API 错误会记录在日志中
5. **字符编码**: Windows 控制台可能无法正确显示 Unicode 字符

## 文件清单

### 核心代码（12个文件）
- `src/config.py` - 配置文件
- `src/main.py` - 主流程编排
- `src/ai/analyzers.py` - AI 分析器
- `src/ai/prompts/article_analysis_system.txt` - 文章分析提示词
- `src/ai/prompts/report_generation_system.txt` - 日报生成提示词
- `src/db/models.py` - 数据库模型
- `src/db/repository.py` - 数据仓库
- `src/feeds/rss_fetcher.py` - RSS 获取器
- `src/charts/generator.py` - 图表生成器
- `src/feishu/sender.py` - 飞书发送器

### 测试文件（5个文件）
- `tests/test_rss_fetcher.py` - RSS 测试
- `tests/test_rss_validation.py` - RSS 验证测试
- `tests/test_charts.py` - 图表测试
- `tests/test_feishu.py` - 飞书测试
- `tests/test_analyzers.py` - AI 分析测试

### 配置和脚本（7个文件）
- `requirements.txt` - Python 依赖
- `.env` - 环境变量
- `README.md` - 使用文档
- `run.py` - 快速启动脚本
- `run_daily.bat` - Windows 定时任务脚本
- `setup_task.ps1` - PowerShell 任务设置脚本
- `setup.py` - 安装脚本

## 总结

本项目成功实现了从 n8n 工作流到独立本地应用的迁移，保留了原有的核心功能（RSS 聚合、AI 分析、日报生成），同时简化了技术栈（仅使用 DeepSeek，改用 SQLite 和飞书），提高了系统的可控性和可维护性。系统已准备就绪，可以部署使用。

---

**实现日期**: 2024-02-24
**项目路径**: `C:\proj datamining\info_dyzz\geopolitical-analysis`
