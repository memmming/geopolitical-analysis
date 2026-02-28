#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单验证脚本 - 检查所有模块是否可以正常导入
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("正在测试模块导入...")

try:
    print("1. 配置模块...")
    import src.config
    print("   ✓ src.config")

    print("2. 数据库模块...")
    import src.db.models
    print("   ✓ src.db.models")
    import src.db.repository
    print("   ✓ src.db.repository")

    print("3. RSS 获取模块...")
    import src.feeds.rss_fetcher
    print("   ✓ src.feeds.rss_fetcher")

    print("4. AI 分析模块...")
    import src.ai.analyzers
    print("   ✓ src.ai.analyzers")

    print("5. 图表生成模块...")
    import src.charts.generator
    print("   ✓ src.charts.generator")

    print("6. 飞书发送模块...")
    import src.feishu.sender
    print("   ✓ src.feishu.sender")

    print("7. 主流程模块...")
    import src.main
    print("   ✓ src.main")

    print("\n所有模块导入成功！✅")

    # 测试飞书格式化
    from src.feishu.sender import adapt_markdown_for_feishu
    test_text = "# Test Heading\n> Quote"
    result = adapt_markdown_for_feishu(test_text)
    print(f"\n飞书格式化测试: {test_text} -> {result}")
    assert result == "**Heading**\n**Quote**", "格式化结果不正确"

except ImportError as e:
    print(f"\n❌ 导入失败: {e}")
    sys.exit(1)

except AssertionError as e:
    print(f"\n❌ 测试失败: {e}")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ 意外错误: {e}")
    sys.exit(1)
