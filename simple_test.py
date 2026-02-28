#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单的测试验证 - 直接在项目目录运行
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== 测试验证 ===\n")

print("1. 导入配置模块...")
try:
    import src.config
    print("   ✓ src.config")
except Exception as e:
    print(f"   ✗ src.config: {e}")
    sys.exit(1)

print("\n2. 导入数据库模块...")
try:
    import src.db.models
    print("   ✓ src.db.models")
except Exception as e:
    print(f"   ✗ src.db.models: {e}")
    sys.exit(1)

print("\n3. 导入RSS模块...")
try:
    import src.feeds.rss_fetcher
    print("   ✓ src.feeds.rss_fetcher")
except Exception as e:
    print(f"   ✗ src.feeds.rss_fetcher: {e}")
    sys.exit(1)

print("\n4. 导入AI模块...")
try:
    import src.ai.analyzers
    print("   ✓ src.ai.analyzers")
except Exception as e:
    print(f"   ✗ src.ai.analyzers: {e}")
    sys.exit(1)

print("\n5. 导入图表模块...")
try:
    import src.charts.generator
    print("   ✓ src.charts.generator")
except Exception as e:
    print(f"   ✗ src.charts.generator: {e}")
    sys.exit(1)

print("\n6. 导入飞书模块...")
try:
    import src.feishu.sender
    print("   ✓ src.feishu.sender")
except Exception as e:
    print(f"   ✗ src.feishu.sender: {e}")
    sys.exit(1)

print("\n7. 测试飞书格式化...")
try:
    from src.feishu.sender import adapt_markdown_for_feishu
    text = "# Heading\n> Quote"
    result = adapt_markdown_for_feishu(text)
    print(f"   输入: {text}")
    print(f"   输出: {result}")
    expected = "**Heading**\n**Quote**"
    if result == expected:
        print("   ✓ 格式化测试通过")
    else:
        print(f"   ✗ 预期: {expected}")
except Exception as e:
    print(f"   ✗ 格式化测试失败: {e}")
    sys.exit(1)

print("\n=== 所有模块导入成功！ ===\n")
print("项目已就绪，可以开始使用。")
print("\n运行完整工作流: python run.py --run")
print("\n验证RSS源: python run.py --validate-rss")
