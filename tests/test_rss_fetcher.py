"""
Tests for RSS Fetcher Module
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from src.feeds.rss_fetcher import (
    fetch_feeds,
    filter_by_date,
    deduplicate_by_url,
    validate_article_data,
    parse_feed_data,
)


class TestArticleValidation:
    """Test article data validation"""

    def test_validate_article_data_complete(self):
        """Test validation of complete article data"""
        article = {
            "title": "Test Article",
            "link": "https://example.com/article",
            "pub_date": "2024-02-24T10:00:00Z",
            "content": "Test content",
        }
        assert validate_article_data(article) is True

    def test_validate_article_data_missing_title(self):
        """Test validation fails when title is missing"""
        article = {
            "link": "https://example.com/article",
            "content": "Test content",
        }
        assert validate_article_data(article) is False

    def test_validate_article_data_missing_link(self):
        """Test validation fails when link is missing"""
        article = {
            "title": "Test Article",
            "content": "Test content",
        }
        assert validate_article_data(article) is False

    def test_validate_article_data_missing_content(self):
        """Test validation fails when all content fields are missing"""
        article = {
            "title": "Test Article",
            "link": "https://example.com/article",
        }
        assert validate_article_data(article) is False

    def test_validate_article_data_invalid_url(self):
        """Test validation fails with invalid URL"""
        article = {
            "title": "Test Article",
            "link": "not-a-valid-url",
            "content": "Test content",
        }
        assert validate_article_data(article) is False


class TestDateFiltering:
    """Test date-based filtering"""

    def test_filter_by_date_all_recent(self):
        """Test filtering keeps all recent articles"""
        from datetime import datetime, timedelta

        now = datetime.now()
        articles = [
            {"title": "Article 1", "pub_date": now - timedelta(hours=1)},
            {"title": "Article 2", "pub_date": now - timedelta(hours=12)},
            {"title": "Article 3", "pub_date": now - timedelta(hours=23)},
        ]
        filtered = filter_by_date(articles, hours=24)
        assert len(filtered) == 3

    def test_filter_by_date_old_articles(self):
        """Test filtering removes old articles"""
        from datetime import datetime, timedelta

        now = datetime.now()
        articles = [
            {"title": "Recent", "pub_date": now - timedelta(hours=1)},
            {"title": "Old", "pub_date": now - timedelta(hours=25)},
        ]
        filtered = filter_by_date(articles, hours=24)
        assert len(filtered) == 1
        assert filtered[0]["title"] == "Recent"

    def test_filter_by_date_no_date(self):
        """Test filtering removes articles without dates"""
        articles = [
            {"title": "No Date", "content": "Content"},
        ]
        filtered = filter_by_date(articles, hours=24)
        assert len(filtered) == 0


class TestDeduplication:
    """Test URL-based deduplication"""

    def test_deduplicate_by_url(self):
        """Test basic deduplication"""
        articles = [
            {"url": "https://example.com/1", "title": "Article 1"},
            {"url": "https://example.com/2", "title": "Article 2"},
            {"url": "https://example.com/1", "title": "Duplicate of 1"},
        ]
        filtered = deduplicate_by_url(articles)
        assert len(filtered) == 2

    def test_deduplicate_with_existing_urls(self):
        """Test deduplication against existing URLs"""
        articles = [
            {"url": "https://example.com/1", "title": "Article 1"},
            {"url": "https://example.com/2", "title": "Article 2"},
        ]
        existing_urls = {"https://example.com/1"}
        filtered = deduplicate_by_url(articles, existing_urls)
        assert len(filtered) == 1
        assert filtered[0]["url"] == "https://example.com/2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
