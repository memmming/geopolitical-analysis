"""
Database Repository for CRUD operations
"""
from typing import List, Optional, Set, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, and_

from src.db.models import Article, Analysis, Report, get_db


class ArticleRepository:
    """Repository for Article operations"""

    @staticmethod
    def create_article(
        db: Session,
        title: str,
        url: str,
        pub_date: Optional[datetime],
        content: str,
        source_domain: str,
        source_name: str,
    ) -> Optional[Article]:
        """Create a new article"""
        try:
            article = Article(
                title=title,
                url=url,
                pub_date=pub_date,
                content=content,
                source_domain=source_domain,
                source_name=source_name,
            )
            db.add(article)
            db.commit()
            db.refresh(article)
            return article
        except Exception as e:
            db.rollback()
            print(f"Error creating article: {e}")
            return None

    @staticmethod
    def get_article_by_url(db: Session, url: str) -> Optional[Article]:
        """Get article by URL"""
        return db.query(Article).filter(Article.url == url).first()

    @staticmethod
    def get_article_by_id(db: Session, article_id: int) -> Optional[Article]:
        """Get article by ID"""
        return db.query(Article).filter(Article.id == article_id).first()

    @staticmethod
    def article_exists(db: Session, url: str) -> bool:
        """Check if article exists by URL"""
        return db.query(Article).filter(Article.url == url).first() is not None

    @staticmethod
    def get_all_urls(db: Session) -> Set[str]:
        """Get all article URLs"""
        articles = db.query(Article.url).all()
        return {url[0] for url in articles if url[0]}

    @staticmethod
    def get_articles_without_analysis(db: Session) -> List[Article]:
        """Get articles that don't have analysis yet"""
        return (
            db.query(Article)
            .outerjoin(Analysis)
            .filter(Analysis.id == None)
            .all()
        )

    @staticmethod
    def get_recent_articles(db: Session, hours: int = 24) -> List[Article]:
        """Get articles from last N hours"""
        cutoff = datetime.utcnow() - datetime.timedelta(hours=hours)
        return (
            db.query(Article)
            .filter(Article.pub_date >= cutoff)
            .order_by(desc(Article.pub_date))
            .all()
        )

    @staticmethod
    def batch_create_articles(db: Session, articles_data: List[Dict[str, Any]]) -> int:
        """Batch create articles"""
        created_count = 0
        for article_data in articles_data:
            # Skip if URL is empty (cannot create unique constraint)
            url = article_data.get("url", "")
            if not url:
                continue

            # Skip if article already exists
            if ArticleRepository.article_exists(db, url):
                continue

            article = Article(
                title=article_data.get("title", ""),
                url=article_data.get("url", ""),
                pub_date=article_data.get("pub_date"),
                content=article_data.get("content", ""),
                source_domain=article_data.get("source_domain", ""),
                source_name=article_data.get("source_name", ""),
            )
            db.add(article)
            created_count += 1

        try:
            db.commit()
            return created_count
        except Exception as e:
            db.rollback()
            print(f"Error batch creating articles: {e}")
            return 0


class AnalysisRepository:
    """Repository for Analysis operations"""

    @staticmethod
    def create_analysis(
        db: Session,
        article_id: int,
        summary: str,
        category: str,
        tags: List[str],
        score: int,
        deep_insight: str,
        impact_level: str,
    ) -> Optional[Analysis]:
        """Create a new analysis"""
        try:
            analysis = Analysis(
                article_id=article_id,
                summary=summary,
                category=category,
                tags=tags,
                score=score,
                deep_insight=deep_insight,
                impact_level=impact_level,
                status="进行中",
            )
            db.add(analysis)
            db.commit()
            db.refresh(analysis)
            return analysis
        except Exception as e:
            db.rollback()
            print(f"Error creating analysis: {e}")
            return None

    @staticmethod
    def get_analysis_by_article_id(db: Session, article_id: int) -> Optional[Analysis]:
        """Get analysis by article ID"""
        return db.query(Analysis).filter(Analysis.article_id == article_id).first()

    @staticmethod
    def get_high_score_analyses(db: Session, min_score: int = 7) -> List[Analysis]:
        """Get analyses with score >= min_score"""
        return (
            db.query(Analysis)
            .filter(Analysis.score >= min_score)
            .order_by(desc(Analysis.score))
            .all()
        )

    @staticmethod
    def update_status(db: Session, article_id: int, status: str) -> bool:
        """Update analysis status"""
        try:
            analysis = (
                db.query(Analysis)
                .filter(Analysis.article_id == article_id)
                .first()
            )
            if analysis:
                analysis.status = status
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            print(f"Error updating status: {e}")
            return False

    @staticmethod
    def batch_update_status(db: Session, article_ids: List[int], status: str) -> int:
        """Batch update analysis status"""
        try:
            updated = (
                db.query(Analysis)
                .filter(Analysis.article_id.in_(article_ids))
                .update({"status": status}, synchronize_session=False)
            )
            db.commit()
            return updated
        except Exception as e:
            db.rollback()
            print(f"Error batch updating status: {e}")
            return 0

    @staticmethod
    def get_analyses_for_report(
        db: Session, min_score: int = 7,
        filter_last_hours: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get analyses with article data for report generation

        Args:
            db: Database session
            min_score: Minimum score threshold
            filter_last_hours: If set, only include articles from last N hours
        """
        query = (
            db.query(Analysis, Article)
            .join(Article, Analysis.article_id == Article.id)
            .filter(Analysis.score >= min_score)
        )

        # Filter by date if specified
        if filter_last_hours:
            cutoff_time = datetime.now() - timedelta(hours=filter_last_hours)
            query = query.filter(Article.pub_date >= cutoff_time)

        results = query.order_by(desc(Analysis.score)).all()

        return [
            {
                "analysis": analysis,
                "article": article,
                "title": article.title,
                "url": article.url,
                "summary": analysis.summary,
                "category": analysis.category,
                "tags": analysis.tags,
                "score": analysis.score,
                "deep_insight": analysis.deep_insight,
                "impact_level": analysis.impact_level,
                "source_domain": article.source_domain,
                "source_name": article.source_name,
            }
            for analysis, article in results
        ]


class ReportRepository:
    """Repository for Report operations"""

    @staticmethod
    def create_report(
        db: Session, report_date: str, markdown_content: str, chart_data: Dict
    ) -> Optional[Report]:
        """Create a new report"""
        try:
            report = Report(
                report_date=report_date,
                markdown_content=markdown_content,
                chart_data=chart_data,
            )
            db.add(report)
            db.commit()
            db.refresh(report)
            return report
        except Exception as e:
            db.rollback()
            print(f"Error creating report: {e}")
            return None

    @staticmethod
    def get_report_by_date(db: Session, report_date: str) -> Optional[Report]:
        """Get report by date"""
        return db.query(Report).filter(Report.report_date == report_date).first()

    @staticmethod
    def report_exists(db: Session, report_date: str) -> bool:
        """Check if report exists for date"""
        return db.query(Report).filter(Report.report_date == report_date).first() is not None

    @staticmethod
    def upsert_report(db: Session, report_date: str, markdown_content: str, chart_data: Dict) -> Optional[Report]:
        """Insert or update a report (upsert)"""
        try:
            report = db.query(Report).filter(Report.report_date == report_date).first()
            if report:
                # Update existing report
                report.markdown_content = markdown_content
                report.chart_data = chart_data
            else:
                # Create new report
                report = Report(
                    report_date=report_date,
                    markdown_content=markdown_content,
                    chart_data=chart_data,
                )
                db.add(report)
            db.commit()
            db.refresh(report)
            return report
        except Exception as e:
            db.rollback()
            print(f"Error upserting report: {e}")
            return None


if __name__ == "__main__":
    # Test the repositories
    from src.db.models import init_db, SessionLocal

    init_db()
    db = SessionLocal()

    # Test article operations
    print("\n=== Testing ArticleRepository ===")
    urls = ArticleRepository.get_all_urls(db)
    print(f"Total articles in database: {len(urls)}")

    # Test analysis operations
    print("\n=== Testing AnalysisRepository ===")
    high_score_analyses = AnalysisRepository.get_high_score_analyses(db, min_score=7)
    print(f"High score analyses (>=7): {len(high_score_analyses)}")

    db.close()
