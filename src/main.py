"""
Main Workflow Orchestrator for Geopolitical Intelligence Analysis System
"""
import asyncio
import logging
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from src.config import (
    DATABASE_PATH,
    HIGH_SCORE_THRESHOLD,
    ARTICLE_TIME_FILTER_HOURS,
)
from src.db.models import init_db, SessionLocal
from src.db.repository import ArticleRepository, AnalysisRepository, ReportRepository
from src.feeds.rss_fetcher import fetch_feeds, filter_by_date, deduplicate_by_url
from src.ai.analyzers import analyze_articles_batch, generate_daily_report
from src.charts.generator import assemble_chart_data
from src.feishu.sender import send_report_to_feishu, send_notification_to_feishu, format_error_message

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_input_with_timeout(prompt: str, timeout: int = 5, default: Any = None) -> Any:
    """
    Get user input with a timeout. Returns default value if timeout occurs.

    Args:
        prompt: The prompt to display to the user
        timeout: Timeout in seconds
        default: Default value to return if timeout occurs

    Returns:
        User input or default value
    """
    result = {"value": default}
    interrupt_event = threading.Event()

    def input_thread():
        try:
            result["value"] = input(prompt)
        except EOFError:
            pass
        except Exception:
            pass
        finally:
            interrupt_event.set()

    input_thread_handle = threading.Thread(target=input_thread, daemon=True)
    input_thread_handle.start()
    input_thread_handle.join(timeout=timeout)

    if not interrupt_event.is_set():
        # Timeout occurred
        return default
    return result["value"]


async def run_daily_workflow(score_threshold: Optional[int] = None, filter_last_hours: Optional[int] = None):
    """
    Execute the complete daily workflow:
    1. Fetch RSS feeds
    2. Filter and deduplicate
    3. Analyze articles with DeepSeek
    4. Generate daily report from high-value articles
    5. Send to Feishu
    """
    # Use custom threshold or default from config
    threshold = score_threshold if score_threshold is not None else HIGH_SCORE_THRESHOLD

    run_date = datetime.now().strftime("%Y-%m-%d")
    logger.info(f"Starting daily workflow for {run_date}")
    logger.info(f"Using score threshold: {threshold} (default: {HIGH_SCORE_THRESHOLD})")
    if filter_last_hours:
        logger.info(f"Filtering articles from last {filter_last_hours} hours")

    # Initialize database
    init_db()
    db = SessionLocal()

    try:
        # Step 1: Fetch RSS feeds
        logger.info("Step 1: Fetching RSS feeds...")
        all_articles = await fetch_feeds()
        logger.info(f"Fetched {len(all_articles)} articles from all sources")

        # Step 2: Filter by date
        logger.info(f"Step 2: Filtering articles from last {ARTICLE_TIME_FILTER_HOURS} hours...")
        filtered_articles = filter_by_date(all_articles, hours=ARTICLE_TIME_FILTER_HOURS)
        logger.info(f"Filtered to {len(filtered_articles)} articles")

        # Step 3: Deduplicate
        logger.info("Step 3: Deduplicating articles...")
        existing_urls = ArticleRepository.get_all_urls(db)
        new_articles = deduplicate_by_url(filtered_articles, existing_urls)
        logger.info(f"Found {len(new_articles)} new articles")

        # Track stored analyses count
        stored_analyses_count = 0

        if not new_articles:
            logger.info("No new articles to process, but will continue to generate report from existing articles")
        else:
            # Step 4: Store new articles in database
            logger.info("Step 4: Storing articles in database...")
            created_count = ArticleRepository.batch_create_articles(db, new_articles)
            logger.info(f"Created {created_count} articles in database")

            # Step 5: Analyze articles with DeepSeek
            logger.info("Step 5: Analyzing articles with DeepSeek...")
            analyses_results = await analyze_articles_batch(new_articles)

            # Store analyses in database
            stored_analyses = []
            for result in analyses_results:
                article_data = result["article_data"]
                analysis = result["analysis"]

                if analysis:
                    # Get article from database
                    article = ArticleRepository.get_article_by_url(db, article_data.get("url", ""))
                    if article:
                        # Create analysis record
                        analysis_record = AnalysisRepository.create_analysis(
                            db=db,
                            article_id=article.id,
                            summary=analysis.get("summary", ""),
                            category=analysis.get("category", ""),
                            tags=analysis.get("tags", []),
                            score=analysis.get("importance_score", 0),
                            deep_insight=analysis.get("deep_insight", ""),
                            impact_level=analysis.get("impact_level", ""),
                        )

                        if analysis_record:
                            stored_analyses.append(analysis_record)

            stored_analyses_count = len(stored_analyses)
            logger.info(f"Analyzed and stored {stored_analyses_count} articles")

        # Step 6: Get high-value articles for report
        logger.info(f"Step 6: Getting high-value articles (score >= {threshold})...")
        high_value_data = AnalysisRepository.get_analyses_for_report(
            db, min_score=threshold, filter_last_hours=filter_last_hours
        )
        logger.info(f"Found {len(high_value_data)} high-value articles")

        if not high_value_data:
            logger.info("No high-value articles for report")
            await send_notification_to_feishu(
                f"今日 ({run_date}) 处理了 {stored_analyses_count} 篇文章，但没有高价值情报 (score >= {threshold})"
            )
            return

        # Step 7: Generate daily report with DeepSeek
        logger.info("Step 7: Generating daily report with DeepSeek...")
        report_result = await generate_daily_report(high_value_data, run_date)

        if not report_result:
            logger.error("Failed to generate daily report")
            await send_notification_to_feishu(
                f"日报生成失败 ({run_date})。请检查系统日志。"
            )
            return

        report_content = report_result.get("raw_article", "")
        chart_data = report_result.get("chart_data", {})

        # Use AI-generated chart data or fallback to local calculation
        if not chart_data or not all(chart_data.values()):
            logger.warning("AI chart data incomplete, falling back to local calculation")
            chart_data = assemble_chart_data(high_value_data)

        logger.info("Daily report generated successfully")

        # Step 8: Send report to Feishu
        logger.info("Step 8: Sending report to Feishu...")
        send_success = send_report_to_feishu(
            report_content=report_content,
            chart_data=chart_data,
            report_date=run_date,
            total_articles=stored_analyses_count,
            high_value_articles=len(high_value_data),
        )

        if send_success:
            logger.info("Report sent to Feishu successfully")

            # Update status of high-value articles
            high_value_ids = [item["article"].id for item in high_value_data]
            updated = AnalysisRepository.batch_update_status(db, high_value_ids, "完成")
            logger.info(f"Updated status to '完成' for {updated} high-value articles")

            # Store report in database (upsert to handle duplicate runs)
            ReportRepository.upsert_report(
                db=db,
                report_date=run_date,
                markdown_content=report_content,
                chart_data=chart_data,
            )
            logger.info("Report cached in database")
        else:
            logger.error("Failed to send report to Feishu")

        logger.info(f"Daily workflow completed for {run_date}")

    except Exception as e:
        logger.error(f"Error in daily workflow: {e}", exc_info=True)
        await send_notification_to_feishu(format_error_message(str(e)))
    finally:
        db.close()


async def analyze_single_article(article_id: int):
    """
    Analyze a single article by ID

    Args:
        article_id: Article ID in database
    """
    init_db()
    db = SessionLocal()

    try:
        article = ArticleRepository.get_article_by_id(db, article_id)
        if not article:
            logger.error(f"Article with ID {article_id} not found")
            return

        logger.info(f"Analyzing article: {article.title}")

        # Check if already analyzed
        existing_analysis = AnalysisRepository.get_analysis_by_article_id(db, article_id)
        if existing_analysis:
            logger.info(f"Article already analyzed: {existing_analysis}")
            return

        # Analyze with DeepSeek
        result = await analyze_articles_batch([
            {
                "title": article.title,
                "url": article.url,
                "content": article.content,
                "pub_date": article.pub_date.isoformat() if article.pub_date else None,
            }
        ])

        if result:
            analysis_data = result[0]["analysis"]
            AnalysisRepository.create_analysis(
                db=db,
                article_id=article.id,
                summary=analysis_data.get("summary", ""),
                category=analysis_data.get("category", ""),
                tags=analysis_data.get("tags", []),
                score=analysis_data.get("importance_score", 0),
                deep_insight=analysis_data.get("deep_insight", ""),
                impact_level=analysis_data.get("impact_level", ""),
            )
            logger.info(f"Analysis completed for article {article_id}")
        else:
            logger.error(f"Analysis failed for article {article_id}")

    except Exception as e:
        logger.error(f"Error analyzing article: {e}", exc_info=True)
    finally:
        db.close()


async def validate_rss_sources():
    """
    Validate all RSS sources and report results
    """
    from src.feeds.rss_fetcher import validate_all_sources

    logger.info("Validating RSS sources...")
    results = await validate_all_sources()

    success_count = sum(1 for r in results.values() if r["status"] == "success")
    total_count = len(results)

    logger.info(f"RSS validation complete: {success_count}/{total_count} sources working")

    # Print detailed results
    for source, result in results.items():
        status = result["status"].upper()
        logger.info(f"  {source}: {status}")
        if status == "SUCCESS":
            logger.info(f"    Articles: {result['articles_count']}")
        else:
            logger.info(f"    Error: {result.get('error', 'Unknown')}")

    return results


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Geopolitical Intelligence Analysis System")
    parser.add_argument("--validate-rss", action="store_true", help="Validate RSS sources")
    parser.add_argument("--analyze-one", type=int, help="Analyze a single article by ID")
    parser.add_argument("--run", action="store_true", help="Run the full daily workflow")
    parser.add_argument("--score", type=int, help="Minimum score threshold for high-value articles (default: 7)")
    parser.add_argument("--filter-hours", type=int, help="Only include articles from last N hours in report (default: include all)")

    args = parser.parse_args()

    # If --run is specified, prompt for score threshold if not provided via argument
    score_threshold = args.score
    if args.run and score_threshold is None:
        print("\n" + "=" * 50)
        print("目标分数阈值设置 (默认: 7)")
        print("=" * 50)
        print("请输入要筛选的文章分数阈值 (5-10之间的数字)")
        print(f"若在5秒内不输入，将使用默认值 {HIGH_SCORE_THRESHOLD}")
        print("=" * 50)

        user_input = get_input_with_timeout(
            prompt=f"请输入分数阈值 (直接回车使用默认值 {HIGH_SCORE_THRESHOLD}): ",
            timeout=5,
            default=None
        )

        if user_input is not None and user_input.strip():
            try:
                score_threshold = int(user_input.strip())
                if score_threshold < 1 or score_threshold > 10:
                    print(f"分数必须在1-10之间，将使用默认值 {HIGH_SCORE_THRESHOLD}")
                    score_threshold = HIGH_SCORE_THRESHOLD
                else:
                    print(f"已设置分数阈值为: {score_threshold}")
            except ValueError:
                print(f"输入无效，将使用默认值 {HIGH_SCORE_THRESHOLD}")
                score_threshold = HIGH_SCORE_THRESHOLD
        else:
            print(f"超时未输入，将使用默认值 {HIGH_SCORE_THRESHOLD}")
            score_threshold = HIGH_SCORE_THRESHOLD
        print("=" * 50 + "\n")

    if args.validate_rss:
        await validate_rss_sources()
    elif args.analyze_one:
        await analyze_single_article(args.analyze_one)
    elif args.run:
        await run_daily_workflow(score_threshold=score_threshold, filter_last_hours=args.filter_hours)
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
