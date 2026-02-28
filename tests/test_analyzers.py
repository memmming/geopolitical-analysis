"""
Tests for AI Analyzers Module
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
import json


class TestArticleAnalysis:
    """Test article analysis functionality"""

    @pytest.mark.asyncio
    async def test_analyze_article(self):
        """Test analyzing a single article"""
        from src.ai.analyzers import analyze_article

        # Mock the OpenAI client response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "summary": "Test summary",
            "category": "Conflict & Security",
            "tags": ["Russia", "NATO"],
            "importance_score": 8,
            "deep_insight": "Test insight",
            "impact_level": "High Risk"
        })

        with patch('src.ai.analyzers.client.chat.completions.create', new=AsyncMock(return_value=mock_response)):
            result = await analyze_article(
                title="Test Article",
                url="https://example.com/article",
                content="Test content",
                pub_date="2024-02-24"
            )

            assert result is not None
            assert result["summary"] == "Test summary"
            assert result["category"] == "Conflict & Security"
            assert result["importance_score"] == 8

    @pytest.mark.asyncio
    async def test_analyze_article_with_code_blocks(self):
        """Test parsing response with markdown code blocks"""
        from src.ai.analyzers import analyze_article

        # Mock response with markdown code blocks
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''```json
{
    "summary": "Test summary",
    "category": "Conflict & Security",
    "tags": ["Russia"],
    "importance_score": 7,
    "deep_insight": "Test insight",
    "impact_level": "Moderate"
}
```'''

        with patch('src.ai.analyzers.client.chat.completions.create', new=AsyncMock(return_value=mock_response)):
            result = await analyze_article(
                title="Test Article",
                url="https://example.com/article",
                content="Test content",
            )

            assert result is not None
            assert result["summary"] == "Test summary"


class TestBatchAnalysis:
    """Test batch article analysis"""

    @pytest.mark.asyncio
    async def test_analyze_articles_batch(self):
        """Test analyzing multiple articles"""
        from src.ai.analyzers import analyze_articles_batch

        # Mock response
        async def mock_create(**kwargs):
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps({
                "summary": "Test summary",
                "category": "Conflict & Security",
                "tags": ["Test"],
                "importance_score": 5,
                "deep_insight": "Test insight",
                "impact_level": "Moderate"
            })
            return mock_response

        with patch('src.ai.analyzers.client.chat.completions.create', new=mock_create):
            articles_data = [
                {
                    "title": "Article 1",
                    "url": "https://example.com/1",
                    "content": "Content 1",
                },
                {
                    "title": "Article 2",
                    "url": "https://example.com/2",
                    "content": "Content 2",
                }
            ]

            results = await analyze_articles_batch(articles_data)

            assert len(results) == 2
            assert results[0]["analysis"]["summary"] == "Test summary"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
