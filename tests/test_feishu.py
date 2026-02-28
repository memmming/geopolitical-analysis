"""
Tests for Feishu Sender Module
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock

from src.feishu.sender import (
    format_report_for_feishu,
    format_error_message,
    format_success_summary,
    adapt_markdown_for_feishu,
    get_feishu_format_guide,
)


class TestFeishuFormatting:
    """Test Feishu message formatting"""

    def test_format_report_for_feishu(self):
        """Test formatting report for Feishu"""
        report_content = "# Test Report\n\nThis is a test."
        chart_summary = "Test Summary"
        report_date = "2024-02-24"

        message = format_report_for_feishu(report_content, chart_summary, report_date)

        assert "2024-02-24" in message
        assert "**Test Report**" in message  # After adaptation, # becomes **
        assert "Test Summary" in message
        assert "全球地缘政治与安全战略日报" in message

    def test_format_error_message(self):
        """Test formatting error message"""
        error = "Test error occurred"
        message = format_error_message(error)

        assert "red" in message  # Using <font color='red'> instead of emoji
        assert "Test error occurred" in message
        assert "地缘政治情报日报生成失败" in message

    def test_format_success_summary(self):
        """Test formatting success summary"""
        summary = format_success_summary(total_articles=10, high_value_articles=5)

        assert "10" in summary
        assert "5" in summary
        assert "高价值情报条数" in summary

    def test_markdown_adaptation(self):
        """Test markdown adaptation for Feishu"""
        from src.feishu.sender import adapt_markdown_for_feishu

        # Test # heading conversion
        text = "# Heading"
        result = adapt_markdown_for_feishu(text)
        assert result == "**Heading**"

        # Test blockquote removal (should remove > and leading space)
        text = "> Quote"
        result = adapt_markdown_for_feishu(text)
        assert result == "Quote"

        # Test cleanup of multiple newlines (3 newlines -> 2 newlines)
        text = "A\n\n\n\nB"
        result = adapt_markdown_for_feishu(text)
        # Result should have at most 2 consecutive newlines
        assert "\n\n\n" not in result

    def test_feishu_format_guide_exists(self):
        """Test that feishu format guide exists"""
        from src.feishu.sender import get_feishu_format_guide
        guide = get_feishu_format_guide()
        assert "supported" in guide
        assert "prompt" in guide


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
