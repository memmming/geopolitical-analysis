"""
Quick start script for Geopolitical Intelligence Analysis System
"""
import asyncio
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))


async def main():
    print("Geopolitical Intelligence Analysis System")
    print("=" * 60)
    print("\nAvailable commands:")
    print("  python run.py --validate-rss     Validate RSS sources")
    print("  python run.py --run              Run full daily workflow")
    print("  python run.py --run --score 5    Run with custom score threshold")
    print("  python run.py --analyze-one ID   Analyze single article")
    print("\nOr run directly:")
    print("  python -m src.main --validate-rss")
    print("  python -m src.main --run")
    print("  python -m src.main --run --score 5")
    print("  python -m src.main --analyze-one 1")
    print("\n" + "=" * 60)

    # Import main function
    from src.main import main as cli_main

    # Pass through any arguments
    await cli_main()


if __name__ == "__main__":
    asyncio.run(main())
