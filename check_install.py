"""
Quick installation check without running full tests
"""
import sys
from pathlib import Path

def check_structure():
    """Check if all necessary files exist"""
    print("检查项目结构...")

    required_files = [
        "src/config.py",
        "src/main.py",
        "src/ai/analyzers.py",
        "src/ai/prompts/article_analysis_system.txt",
        "src/ai/prompts/report_generation_system.txt",
        "src/db/models.py",
        "src/db/repository.py",
        "src/feeds/rss_fetcher.py",
        "src/charts/generator.py",
        "src/feishu/sender.py",
        "run.py",
        "requirements.txt",
        ".env",
        "README.md",
    ]

    base_path = Path(__file__).parent
    missing = []

    for file in required_files:
        full_path = base_path / file
        if full_path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} (缺失)")
            missing.append(file)

    return len(missing) == 0


def check_modules():
    """Check if Python modules can be imported"""
    print("\n检查Python模块导入...")

    modules = [
        ("sys", "系统模块"),
        ("pathlib", "路径处理"),
        ("asyncio", "异步支持"),
    ]

    optional_modules = [
        ("sqlalchemy", "数据库 ORM"),
        ("feedparser", "RSS解析"),
        ("aiohttp", "HTTP客户端"),
        ("openai", "AI API"),
        ("plotly", "图表生成"),
    ]

    all_required_ok = True
    for module, desc in modules:
        try:
            __import__(module)
            print(f"  ✓ {module} ({desc})")
        except ImportError:
            print(f"  ✗ {module} ({desc})")
            all_required_ok = False

    print("\n检查可选模块 (需运行 setup.py 安装):")
    for module, desc in optional_modules:
        try:
            __import__(module)
            print(f"  ✓ {module} ({desc})")
        except ImportError:
            print(f"  ⚠ {module} ({desc}) - 未安装")

    return all_required_ok


def check_config():
    """Check configuration files"""
    print("\n检查配置文件...")

    base_path = Path(__file__).parent

    # Check .env
    env_file = base_path / ".env"
    if env_file.exists():
        print("  ✓ .env 文件存在")
        content = env_file.read_text()
        if "DEEPSEEK_API_KEY" in content:
            print("  ✓ DeepSeek API Key 已配置")
        else:
            print("  ⚠ DeepSeek API Key 未配置")
        if "FEISHU_WEBHOOK_URL" in content:
            print("  ✓ 飞书 Webhook URL 已配置")
        else:
            print("  ⚠ 飞书 Webhook URL 未配置")
    else:
        print("  ✗ .env 文件不存在")

    # Check data directory
    data_dir = base_path / "data"
    if data_dir.exists():
        print(f"  ✓ 数据目录存在: {data_dir}")
    else:
        print(f"  ℹ 数据目录将自动创建: {data_dir}")


def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║     地缘政治情报分析系统 - 安装检查工具                      ║
║     Installation Check Tool                                 ║
╚════════════════════════════════════════════════════════════╝
    """)

    structure_ok = check_structure()
    modules_ok = check_modules()
    check_config()

    print("\n" + "="*60)
    if structure_ok and modules_ok:
        print("✅ 基础检查通过!")
        print("\n下一步:")
        print("  1. 安装依赖: python setup.py")
        print("  2. 验证RSS源: python run.py --validate-rss")
        print("  3. 运行工作流: python run.py --run")
    else:
        print("⚠️  部分检查未通过，请查看上述详细信息")
    print("="*60)


if __name__ == "__main__":
    main()
