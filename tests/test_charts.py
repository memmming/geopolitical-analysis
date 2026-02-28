"""
Tests for Chart Generator Module
"""
import pytest
from src.charts.generator import (
    extract_top_keywords,
    extract_category_distribution,
    extract_impact_distribution,
    extract_source_distribution,
    assemble_chart_data,
    generate_chart_summary,
)


class TestKeywordExtraction:
    """Test keyword extraction"""

    def test_extract_top_keywords(self):
        """Test extracting top keywords"""
        analyses = [
            {"tags": ["Russia", "NATO", "Ukraine"]},
            {"tags": ["Russia", "Oil"]},
            {"tags": ["China", "US", "Semiconductors"]},
        ]
        result = extract_top_keywords(analyses, top_n=3)
        assert "Russia" in result
        assert result["Russia"] == 2

    def test_extract_top_keywords_limit(self):
        """Test limiting number of keywords"""
        analyses = [
            {"tags": ["A", "B", "C", "D", "E", "F"]},
        ]
        result = extract_top_keywords(analyses, top_n=3)
        assert len(result) == 3

    def test_extract_top_keywords_string_tags(self):
        """Test handling string tags instead of list"""
        analyses = [
            {"tags": "Russia"},
            {"tags": ["China", "US"]},
        ]
        result = extract_top_keywords(analyses)
        assert "Russia" in result
        assert "China" in result
        assert "US" in result


class TestCategoryDistribution:
    """Test category distribution extraction"""

    def test_extract_category_distribution(self):
        """Test extracting category distribution"""
        analyses = [
            {"category": "Conflict & Security"},
            {"category": "Conflict & Security"},
            {"category": "Tech War & Cyber"},
        ]
        result = extract_category_distribution(analyses)
        assert result["Conflict & Security"] == 2
        assert result["Tech War & Cyber"] == 1


class TestImpactDistribution:
    """Test impact level distribution extraction"""

    def test_extract_impact_distribution(self):
        """Test extracting impact distribution"""
        analyses = [
            {"impact_level": "High Risk"},
            {"impact_level": "Global Shift"},
            {"impact_level": "High Risk"},
        ]
        result = extract_impact_distribution(analyses)
        assert result["High Risk"] == 2
        assert result["Global Shift"] == 1


class TestSourceDistribution:
    """Test source distribution extraction"""

    def test_extract_source_distribution(self):
        """Test extracting source distribution"""
        analyses = [
            {"source_domain": "example.com", "source_name": "Example"},
            {"source_domain": "example.com", "source_name": "Example"},
            {"source_domain": "test.com", "source_name": "Test"},
        ]
        result = extract_source_distribution(analyses, top_n=5)
        assert result["example.com"] == 2
        assert result["test.com"] == 1


class TestChartSummary:
    """Test chart summary generation"""

    def test_generate_chart_summary(self):
        """Test generating chart summary"""
        chart_data = {
            "top_keywords": {"Russia": 15, "NATO": 12},
            "category_distribution": {"Conflict & Security": 10},
            "impact_radar": {"High Risk": 5},
            "primary_sources": {"example.com": 5},
        }
        summary = generate_chart_summary(chart_data)
        assert "关键涉事方" in summary
        assert "Russia" in summary
        assert "战略领域分布" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
