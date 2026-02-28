"""
Setup script for Geopolitical Intelligence Analysis System
Run this to install dependencies and initialize the system
"""
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and display results"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"⚠️  Warning: {description} returned non-zero exit code")
        return False
    return True


def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║          地缘政治情报分析系统 - 安装向导                      ║
║     Geopolitical Intelligence Analysis System - Setup       ║
╚════════════════════════════════════════════════════════════╝
    """)

    # Step 1: Install dependencies
    print("\n[1/3] 安装Python依赖...")
    run_command("pip install -r requirements.txt", "Installing dependencies")

    # Step 2: Initialize database
    print("\n[2/3] 初始化数据库...")
    run_command("python -m src.db.models", "Initializing database")

    # Step 3: Verify installation
    print("\n[3/3] 验证安装...")
    print("\n检查模块导入...")

    modules_to_check = [
        "sqlalchemy",
        "feedparser",
        "aiohttp",
        "openai",
        "plotly",
    ]

    all_ok = True
    for module in modules_to_check:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError:
            print(f"  ✗ {module} (未安装)")
            all_ok = False

    if all_ok:
        print("\n" + "="*60)
        print("✅ 安装完成!")
        print("="*60)
        print("\n下一步:")
        print("  1. 验证RSS源: python run.py --validate-rss")
        print("  2. 运行工作流: python run.py --run")
        print("  3. 配置定时任务: 参考 README.md")
        print("\n如需帮助，请查看 README.md")
    else:
        print("\n⚠️  部分依赖未安装成功，请手动运行:")
        print("  pip install -r requirements.txt")

    print()


if __name__ == "__main__":
    main()
