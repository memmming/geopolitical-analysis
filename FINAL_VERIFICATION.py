#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最终验证脚本 - 检查所有核心功能
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("地缘政治情报分析系统 - 最终验证")
print("=" * 60)

# 测试 1: 配置
print("\n[1/6] 检查配置模块...")
try:
    from src.config import RSS_SOURCES, DEEPSEEK_API_KEY, FEISHU_WEBHOOK_URL
    print("  ✓ RSS_SOURCES: {} 个源".format(len(RSS_SOURCES)))
    print("  ✓ DeepSeek API Key: {}".format("..." + DEEPSEEK_API_KEY[-4:]))
    print("  ✓ 飞书 Webhook URL: {}".format("..." + FEISHU_WEBHOOK_URL[-10:]))
    print("  ✓ 所有配置已加载")
except Exception as e:
    print("  ✗ 配置检查失败: {}".format(str(e)))
    sys.exit(1)

# 测试 2: 数据库
print("\n[2/6] 检查数据库模块...")
try:
    from src.db.models import init_db, DATABASE_PATH
    init_db()
    import os.path
    db_exists = os.path.exists(DATABASE_PATH)
    print("  ✓ 数据库初始化")
    print("  ✓ 数据库路径: {}".format(str(DATABASE_PATH)))
    print("  ✓ 数据库存在: {}".format("是" if db_exists else "否"))
except Exception as e:
    print("  ✗ 数据库检查失败: {}".format(str(e)))
    sys.exit(1)

# 测试 3: RSS 获取
print("\n[3/6] 检查RSS获取模块...")
try:
    from src.feeds.rss_fetcher import (
        fetch_feeds,
        filter_by_date,
        deduplicate_by_url,
        validate_article_data,
        adapt_markdown_for_feishu,
    )
    print("  ✓ RSS获取函数导入")
    print("  ✓ 文章数据验证")
    print("  ✓ Markdown格式化函数")
    # 测试验证
    test_article = {
        "title": "Test Article",
        "link": "https://example.com/article",
        "content": "Test content here",
        "pub_date": None,
    }
    assert validate_article_data(test_article) is True
    print("  ✓ 文章数据验证测试通过")
    # 测试格式化
    result = adapt_markdown_for_feishu("# Test Heading")
    assert result == "**Test Heading**"
    print("  ✓ Markdown格式化测试通过")
except Exception as e:
    print("  ✗ RSS模块检查失败: {}".format(str(e)))
    sys.exit(1)

# 测试 4: AI 分析
print("\n[4/6] 检查AI分析模块...")
try:
    from src.ai.analyzers import (
        analyze_article,
        generate_daily_report,
    )
    print("  ✓ AI分析器导入")
    # 注意：不实际调用API（避免消耗配额）
except Exception as e:
    print("  ✗ AI模块检查失败: {}".format(str(e)))
    sys.exit(1)

# 测试 5: 图表生成
print("\n[5/6] 检查图表生成模块...")
try:
    from src.charts.generator import (
        extract_top_keywords,
        extract_category_distribution,
        generate_chart_summary,
    )
    print("  ✓ 图表生成器导入")
    # 测试数据提取
    test_data = [
        {"tags": ["Russia", "NATO"], "category": "Conflict & Security"},
        {"tags": ["China", "US"], "category": "Tech War & Cyber"},
    ]
    keywords = extract_top_keywords(test_data, top_n=5)
    assert len(keywords) > 0
    print("  ✓ 关键词提取: {} 个".format(len(keywords)))
    categories = extract_category_distribution(test_data)
    assert len(categories) > 0
    print("  ✓ 分类分布: {} 个".format(len(categories)))
except Exception as e:
    print("  ✗ 图表模块检查失败: {}".format(str(e)))
    sys.exit(1)

# 测试 6: 飞书推送
print("\n[6/6] 检查飞书推送模块...")
try:
    from src.feishu.sender import (
        send_to_feishu,
        format_report_for_feishu,
        format_error_message,
        format_success_summary,
        get_feishu_format_guide,
    )
    print("  ✓ 飞书发送器导入")
    print("  ✓ 格式化函数导入")
    print("  ✓ 消息格式化函数导入")
    # 测试格式化
    report = format_report_for_feishu("Test content", "Summary", "2024-02-24")
    assert "2024-02-24" in report
    print("  ✓ 报告格式化测试通过")
    # 获取格式指南
    guide = get_feishu_format_guide()
    assert "supported" in guide
    print("  ✓ 飞书格式指南获取")
except Exception as e:
    print("  ✗ 飞书模块检查失败: {}".format(str(e)))
    sys.exit(1)

# 测试 7: 主流程
print("\n[7/7] 检查主流程模块...")
try:
    from src.main import run_daily_workflow
    print("  ✓ 主流程函数导入")
except Exception as e:
    print("  ✗ 主流程检查失败: {}".format(str(e)))
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ 所有模块检查通过！")
print("\n下一步:")
print("  1. 运行完整工作流: python run.py --run")
print("  2. 验证RSS源: python run.py --validate-rss")
print("  3. 运行单元测试: pytest tests/ -v")
print("\n项目位置: C:\\proj datamining\\info_dyzz\\geopolitical-analysis\\")
print("\n文档位置: README.md 和 PROJECT_SUMMARY.md")
