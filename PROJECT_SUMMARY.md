# 地缘政治情报分析系统 - 项目完成总结

## 项目概述

成功实现了一个独立的本地化地缘政治情报分析系统，基于 n8n 工作流重构，并参考 TrendRadar 项目改进了飞书推送功能。

## 项目位置

```
C:\proj datamining\info_dyzz\geopolitical-analysis\
```

## 已实现功能

### 1. RSS 订阅获取模块
- 并发获取 10 个国际关系/安全源的 RSS 订阅
- 自动过滤 24 小时内的文章
- URL 去重功能（检查数据库）
- RSS 数据完整性验证
- 源验证功能

### 2. AI 分析引擎
- 使用 DeepSeek API 进行文章分析（Stratfor/RAND 身份）
- 使用 DeepSeek API 生成日报（CICIR 智库身份）
- 批量分析支持（并发处理）
- JSON 响应解析（支持 Markdown 代码块）

### 3. 数据库层
- SQLite 数据库存储（articles, analyses, reports 表）
- 完整的 CRUD 操作封装
- 状态跟踪（进行中 → 完成）
- 批量操作支持

### 4. 图表生成模块
- 使用 Plotly 生成本地图表
- 4 种图表类型：
  - 关键涉事方（横向条形图）
  - 战略领域分布（圆环图）
  - 安全等级（半圆仪表）
  - 情报源分布（条形图）
- 文本摘要生成

### 5. 飞书推送模块（基于 TrendRadar 改进）
- ✅ 支持飞书卡片 Markdown 格式优化
- ✅ 自动适配 Markdown 内容（移除不支持的 # 标题和 > 引用）
- ✅ 使用飞书颜色标签增强可读性
- ✅ 同步和异步发送函数
- ✅ 批次处理支持（预留接口）
- **飞书格式化策略**：
  - 用 `**粗体**` 作小标题和重点词
  - 用 `<font color='red'>红色</font>` 标记紧急/重要内容
  - 用 `<font color='grey'>灰色</font>` 标记辅助信息
  - 用 `---` 分割不同主题区域
  - 将 `# 标题` 自动转换为 `**粗体**`

### 6. 主流程编排
- 完整的每日工作流：
  1. 获取 RSS 订阅
  2. 过滤 + 去重
  3. AI 分析（单篇）
  4. 生成日报（高价值文章）
  5. 生成图表
  6. 飞书推送
  7. 更新状态
- 命令行界面支持
- 单篇文章分析功能
- RSS 源验证功能

### 7. 虚拟环境
- 已创建虚拟环境 `venv/`
- 所有依赖已安装
- 36/36 测试全部通过

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
│   │   └── rss_fetcher.py        # RSS 获取与验证
│   ├── feishu/
│   │   └── sender.py            # 飞书 Webhook 发送（改进版）
│   ├── config.py                 # 配置文件
│   └── main.py                   # 主流程编排
├── tests/                        # 测试文件
├── data/
│   └── geopolitical.db           # SQLite 数据库（已创建）
├── venv/                         # 虚拟环境（已创建）
├── requirements.txt              # Python 依赖
├── .env                          # 环境变量
├── README.md                     # 使用文档
├── run.py                        # 快速启动脚本
├── run_daily.bat                 # Windows 定时任务脚本（使用 venv）
├── setup_task.ps1                # PowerShell 任务设置脚本
└── PROJECT_SUMMARY.md          # 本文件
```

## 测试结果

```
======================= 36 passed in 155.13s ========================
```

所有测试全部通过，包括：
- RSS 获取与验证 (15 tests)
- 图表生成 (7 tests)
- 飞书发送 (5 tests)
- AI 分析 (3 tests)
- RSS 源验证 (6 tests)

## 使用方法

### 安装依赖
```bash
cd C:\proj datamining\info_dyzz\geopolitical-analysis
pip install -r requirements.txt
```

### 激活虚拟环境
```bash
venv\Scripts\activate
```

### 验证 RSS 源
```bash
python run.py --validate-rss
# 或
venv\Scripts\python.exe run.py --validate-rss
```

### 运行完整工作流
```bash
python run.py --run
# 或
venv\Scripts\python.exe run.py --run
```

### 分析单篇文章
```bash
python run.py --analyze-one <article_id>
# 或
venv\Scripts\python.exe run.py --analyze-one 1
```

### 运行测试
```bash
pytest tests/ -v
# 或
venv\Scripts\python.exe -m pytest tests/ -v
```

## 配置 Windows 定时任务

### 方法一：使用批处理文件
1. `run_daily.bat` 已配置为使用虚拟环境中的 Python
2. 使用任务计划程序定期执行该文件

### 方法二：使用 PowerShell 脚本
1. 以管理员身份运行 PowerShell
2. 执行: `.\setup_task.ps1`
3. 输入凭据完成配置

## 配置文件

### DeepSeek API
- API Key: `REDACTED_API_KEY`
- 模型: `deepseek-reasoner`

### 飞书 Webhook
- URL: `REDACTED_WEBHOOK`
- 消息类型: `text`

## 与原 n8n 工作流的对比

| 组件 | n8n 工作流 | 本地应用 | TrendRadar 改进 |
|------|-----------|---------|---------------|
| AI 模型 | DeepSeek + Gemini | 仅 DeepSeek | N/A |
| 报告推送 | Gmail | 飞书 Webhook | 飞书格式优化 |
| 数据存储 | Notion API | SQLite 本地数据库 | 批次处理 |
| 图表生成 | QuickChart.io | Plotly 本地生成 | N/A |
| 任务调度 | n8n 调度器 | Windows 任务计划程序 | N/A |
| 部署方式 | 云端/本地 | 纯本地 | N/A |

## TrendRadar 改进点

参考 TrendRadar 项目，在飞书推送模块中实现了以下改进：

1. **Markdown 格式适配器**
   - 自动将 `# 标题` 转换为 `**粗体**`
   - 自动移除 `> 引用` 语法
   - 限制连续空行数量

2. **飞书颜色标签**
   - 红色：`<font color='red'>` - 标记紧急/重要
   - 灰色：`<font color='grey'>` - 标记辅助信息
   - 橙色：`<font color='orange'>` - 标记警告
   - 绿色：`<font color='green'>` - 标记成功信息

3. **格式化指南**
   - 提供完整的飞书格式化策略文档
   - 支持查询格式指南

4. **同步和异步支持**
   - 提供 `send_to_feishu()` 同步版本
   - 提供 `send_to_feishu_async()` 异步版本
   - 自动适配格式

## 已知问题

### RSS 源访问
验证结果显示大部分 RSS 源由于网络连接问题无法访问（可能是国内网络限制）：
- 只有 Defense One 可以正常访问
- 其他 9 个源显示 SSL 连接错误

**解决方案**：
- 部署到可访问外部网络的环境
- 或配置代理
- 或更换国内可访问的 RSS 源

### 飞书消息内容
用户反馈消息收到但内容不显示，可能原因：
- 飞书机器人需要特定权限
- Webhook URL 配置可能有问题
- 内容格式可能不被飞书完全支持

**建议**：
- 检查飞书机器人权限设置
- 验证 Webhook URL 是否正确
- 考虑使用更简单的文本格式

## 技术栈

| 组件 | 技术 |
|------|------|
| 后端 | Python 3.10 + FastAPI + asyncio |
| 数据库 | SQLite + SQLAlchemy |
| AI 模型 | DeepSeek Reasoner |
| 图表 | Plotly |
| 报告推送 | 飞书 Webhook |
| 任务队列 | 本地异步处理 |
| 测试 | pytest + pytest-asyncio |

## 下一步建议

1. **网络配置**
   - 添加代理支持
   - 添加超时和重试机制

2. **RSS 源优化**
   - 更换为国内可访问的源
   - 添加源可用性监控

3. **飞书推送优化**
   - 尝试不同的消息格式
   - 考虑使用飞书机器人 API 而不是 Webhook
   - 添加消息发送重试机制

4. **功能增强**
   - 添加 Web 管理界面
   - 添加历史数据查询功能
   - 添加手动触发报告生成功能
   - 支持多个飞书群推送

## 许可

本项目基于原有 n8n 工作流重构，参考 TrendRadar 项目的飞书推送实现，仅供学习和研究使用。

---

**项目完成日期**: 2024-02-24
**测试状态**: ✅ 36/36 测试通过
**虚拟环境**: ✅ 已创建并配置
**部署状态**: ⚠️ 部分 RSS 源无法访问，飞书推送需进一步验证
