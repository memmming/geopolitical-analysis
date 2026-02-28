"""
Tests for RSS Validation
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from src.feeds.rss_fetcher import (
    validate_all_sources,
    validate_article_data,
    parse_feed_data,
)


class TestRSSValidation:
    """Test RSS source validation"""

    @pytest.mark.asyncio
    async def test_validate_all_sources(self):
        """Test validating all RSS sources"""
        # This is more of an integration test
        # For unit tests, we'd mock the HTTP responses
        results = await validate_all_sources()

        # Check that results were returned for all sources
        from src.config import RSS_SOURCES
        assert len(results) == len(RSS_SOURCES)

        # Check each result has required keys
        for source_name, result in results.items():
            assert "status" in result
            assert result["status"] in ["success", "failed", "error"]


class TestArticleDataValidation:
    """Test article data validation"""

    def test_validate_complete_article(self):
        """Test validation of complete article data"""
        article = {
            "title": "Test Article",
            "link": "https://example.com/article",
            "pub_date": "2024-02-24",
            "content": "Test content here",
        }
        assert validate_article_data(article) is True

    def test_validate_missing_title(self):
        """Test validation fails without title"""
        article = {
            "link": "https://example.com/article",
            "content": "Test content",
        }
        assert validate_article_data(article) is False

    def test_validate_missing_link(self):
        """Test validation fails without link"""
        article = {
            "title": "Test Article",
            "content": "Test content",
        }
        assert validate_article_data(article) is False

    def test_validate_missing_all_content_fields(self):
        """Test validation fails without any content fields"""
        article = {
            "title": "Test Article",
            "link": "https://example.com/article",
        }
        assert validate_article_data(article) is False

    def test_validate_with_description_field(self):
        """Test validation with description field instead of content"""
        article = {
            "title": "Test Article",
            "link": "https://example.com/article",
            "description": "Test description",
        }
        assert validate_article_data(article) is True

    def test_validate_with_content_snippet(self):
        """Test validation with contentSnippet field"""
        article = {
            "title": "Test Article",
            "link": "https://example.com/article",
            "contentSnippet": "Test snippet",
        }
        assert validate_article_data(article) is True

    def test_validate_invalid_url_format(self):
        """Test validation with invalid URL"""
        article = {
            "title": "Test Article",
            "link": "not-a-valid-url",
            "content": "Test content",
        }
        assert validate_article_data(article) is False

    def test_validate_empty_url(self):
        """Test validation with empty URL"""
        article = {
            "title": "Test Article",
            "link": "",
            "content": "Test content",
        }
        assert validate_article_data(article) is False


class TestFeedDataParsing:
    """Test feed data parsing"""

    def test_parse_feed_data_basic(self):
        """Test basic feed data parsing"""
        feed_data = {
            "feed": {"link": "https://example.com"},
            "entries": [
                {
                    "title": "Test Article",
                    "link": "https://example.com/article",
                    "published_parsed": (2024, 2, 24, 10, 0, 0, 0, 0, 0),
                    "description": "Test description",
                }
            ],
        }

        articles = parse_feed_data(feed_data, "Test Source")

        assert len(articles) == 1
        assert articles[0]["title"] == "Test Article"
        assert articles[0]["link"] == "https://example.com/article"
        assert articles[0]["source_name"] == "Test Source"

    def test_parse_feed_data_no_entries(self):
        """Test parsing feed with no entries"""
        feed_data = {
            "feed": {"link": "https://example.com"},
            "entries": [],
        }

        articles = parse_feed_data(feed_data, "Test Source")
        assert len(articles) == 0

    def test_parse_feed_data_missing_fields(self):
        """Test parsing with missing optional fields"""
        feed_data = {
            "feed": {"link": "https://example.com"},
            "entries": [
                {
                    "title": "Test Article",
                    "link": "https://example.com/article",
                }
            ],
        }

        articles = parse_feed_data(feed_data, "Test Source")
        # Should return empty list because validation fails (no content)
        assert len(articles) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
