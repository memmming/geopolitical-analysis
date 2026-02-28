"""
Chart Generator Module - Plotly-based Chart Generation
"""
import logging
from typing import Dict, List, Any, Optional
from collections import Counter
import json

from src.config import CHART_KEYWORD_COUNT, CHART_SOURCE_COUNT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_top_keywords(analyses: List[Dict[str, Any]], top_n: int = CHART_KEYWORD_COUNT) -> Dict[str, int]:
    """
    Extract top keywords from analyses

    Args:
        analyses: List of analysis dictionaries
        top_n: Number of top keywords to return

    Returns:
        Dictionary of keyword -> count
    """
    keyword_counts = Counter()

    for item in analyses:
        tags = item.get("tags", [])
        if tags:
            if isinstance(tags, list):
                keyword_counts.update(tags)
            elif isinstance(tags, str):
                keyword_counts.update([tags])

    return dict(keyword_counts.most_common(top_n))


def extract_category_distribution(analyses: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Extract category distribution from analyses

    Args:
        analyses: List of analysis dictionaries

    Returns:
        Dictionary of category -> count
    """
    category_counts = Counter()

    for item in analyses:
        category = item.get("category", "Unknown")
        category_counts[category] += 1

    return dict(category_counts)


def extract_impact_distribution(analyses: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Extract impact level distribution from analyses

    Args:
        analyses: List of analysis dictionaries

    Returns:
        Dictionary of impact level -> count
    """
    impact_counts = Counter()

    for item in analyses:
        impact = item.get("impact_level", "Unknown")
        impact_counts[impact] += 1

    return dict(impact_counts)


def extract_source_distribution(analyses: List[Dict[str, Any]], top_n: int = CHART_SOURCE_COUNT) -> Dict[str, int]:
    """
    Extract top sources from analyses

    Args:
        analyses: List of analysis dictionaries
        top_n: Number of top sources to return

    Returns:
        Dictionary of source -> count
    """
    source_counts = Counter()

    for item in analyses:
        source_domain = item.get("source_domain", "Unknown")
        source_name = item.get("source_name", "Unknown")

        # Prefer domain, fall back to source name
        if source_domain and source_domain != "Unknown":
            source = source_domain
        else:
            source = source_name

        source_counts[source] += 1

    return dict(source_counts.most_common(top_n))


def generate_charts_html(chart_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Generate Plotly charts as HTML strings

    Args:
        chart_data: Dictionary containing chart data from analysis

    Returns:
        Dictionary with chart names as keys and HTML strings as values
    """
    try:
        import plotly.graph_objects as go
        import plotly.express as px
    except ImportError:
        logger.error("Plotly not installed. Install with: pip install plotly")
        return {}

    charts = {}

    # 1. Keywords Bar Chart (Horizontal)
    if "top_keywords" in chart_data:
        keywords = chart_data["top_keywords"]
        if keywords:
            fig = go.Figure(go.Bar(
                x=list(keywords.values()),
                y=list(keywords.keys()),
                orientation='h',
                marker_color='#1e3a8a'  # Navy blue
            ))
            fig.update_layout(
                title="🎯 关键涉事方 (Key Players)",
                xaxis_title="提及次数",
                yaxis_title="",
                height=300,
                margin=dict(l=10, r=10, t=40, b=10),
                font=dict(size=12)
            )
            charts['keywords'] = fig.to_html(include_plotlyjs='cdn', full_html=False)

    # 2. Categories Doughnut Chart
    if "category_distribution" in chart_data:
        categories = chart_data["category_distribution"]
        if categories:
            fig = go.Figure(data=[go.Pie(
                labels=list(categories.keys()),
                values=list(categories.values()),
                hole=0.4,
                marker=dict(colors=['#1e3a8a', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe', '#dc2626'])
            )])
            fig.update_layout(
                title="📊 战略领域分布 (Strategic Focus)",
                height=300,
                margin=dict(l=10, r=10, t=40, b=10),
                font=dict(size=12)
            )
            charts['categories'] = fig.to_html(include_plotlyjs='cdn', full_html=False)

    # 3. Impact Semicircle Chart
    if "impact_radar" in chart_data:
        impacts = chart_data["impact_radar"]
        if impacts:
            # Convert to list for Plotly
            labels = list(impacts.keys())
            values = list(impacts.values())

            # Create a pie chart with custom colors and make it look like a gauge
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.6,
                marker=dict(colors=['#dc2626', '#f97316', '#3b82f6'])  # Red, Orange, Blue
            )])
            fig.update_layout(
                title="⚡ 安全等级 (Security Alert)",
                height=300,
                margin=dict(l=10, r=10, t=40, b=10),
                font=dict(size=12)
            )
            charts['impact'] = fig.to_html(include_plotlyjs='cdn', full_html=False)

    # 4. Sources Bar Chart
    if "primary_sources" in chart_data:
        sources = chart_data["primary_sources"]
        if sources:
            fig = go.Figure(go.Bar(
                x=list(sources.keys()),
                y=list(sources.values()),
                marker_color='#475569'  # Slate gray
            ))
            fig.update_layout(
                title="📡 情报源分布 (Intel Sources)",
                yaxis_title="文章数量",
                height=300,
                margin=dict(l=10, r=10, t=40, b=10),
                font=dict(size=12)
            )
            fig.update_xaxes(tickangle=45)
            charts['sources'] = fig.to_html(include_plotlyjs='cdn', full_html=False)

    return charts


def generate_chart_summary(chart_data: Dict[str, Any]) -> str:
    """
    Generate a text summary of chart data for Feishu message

    Args:
        chart_data: Dictionary containing chart data

    Returns:
        Markdown formatted summary
    """
    summary_lines = ["\n📊 今日数据统计：\n"]

    # Keywords
    if "top_keywords" in chart_data:
        keywords = chart_data["top_keywords"]
        if keywords:
            summary_lines.append("**关键涉事方:**")
            for kw, count in keywords.items():
                summary_lines.append(f"  • {kw}: {count}")

    # Categories
    if "category_distribution" in chart_data:
        categories = chart_data["category_distribution"]
        if categories:
            summary_lines.append("\n**战略领域分布:**")
            for cat, count in categories.items():
                summary_lines.append(f"  • {cat}: {count}")

    # Impact
    if "impact_radar" in chart_data:
        impacts = chart_data["impact_radar"]
        if impacts:
            summary_lines.append("\n**安全等级分布:**")
            for impact, count in impacts.items():
                summary_lines.append(f"  • {impact}: {count}")

    # Sources
    if "primary_sources" in chart_data:
        sources = chart_data["primary_sources"]
        if sources:
            summary_lines.append("\n**主要情报源:**")
            for src, count in sources.items():
                summary_lines.append(f"  • {src}: {count}")

    return "\n".join(summary_lines)


def assemble_chart_data(analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Assemble all chart data from analyses

    Args:
        analyses: List of analysis dictionaries

    Returns:
        Dictionary with all chart data
    """
    return {
        "top_keywords": extract_top_keywords(analyses),
        "category_distribution": extract_category_distribution(analyses),
        "impact_radar": extract_impact_distribution(analyses),
        "primary_sources": extract_source_distribution(analyses),
    }


if __name__ == "__main__":
    # Test chart generation
    test_analyses = [
        {
            "tags": ["Russia", "NATO", "Ukraine"],
            "category": "Conflict & Security",
            "impact_level": "High Risk",
            "source_domain": "foreignaffairs.com",
        },
        {
            "tags": ["China", "US", "Semiconductors"],
            "category": "Tech War & Cyber",
            "impact_level": "Global Shift",
            "source_domain": "aljazeera.com",
        },
        {
            "tags": ["Russia", "Oil"],
            "category": "Energy & Resources",
            "impact_level": "High Risk",
            "source_domain": "eurasiareview.com",
        },
    ]

    print("Testing chart generation...")
    chart_data = assemble_chart_data(test_analyses)
    print("Chart data:")
    print(json.dumps(chart_data, indent=2))

    print("\nTesting chart HTML generation...")
    charts_html = generate_charts_html(chart_data)
    print(f"Generated {len(charts_html)} charts")

    print("\nTesting chart summary...")
    summary = generate_chart_summary(chart_data)
    print(summary)
