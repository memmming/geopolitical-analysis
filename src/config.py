"""
Configuration file for Geopolitical Intelligence Analysis System
"""
import os
from dataclasses import dataclass
from typing import List, Tuple
from pathlib import Path

# RSS Sources - 10 international relations/security sources
RSS_SOURCES: List[Tuple[str, str]] = [
    ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml"),
    ("Foreign Affairs", "https://www.foreignaffairs.com/rss.xml"),
    ("Foreign Policy", "https://foreignpolicy.com/feed/"),
    ("Project Syndicate", "https://www.project-syndicate.org/rss"),
    ("The Conversation", "https://theconversation.com/global/articles.atom"),
    ("Eurasia Review", "https://www.eurasiareview.com/feed/"),
    ("War on the Rocks", "https://warontherocks.com/feed/"),
    ("Chatham House", "https://www.chathamhouse.org/rss.xml"),
    ("Defense One", "https://www.defenseone.com/rss/all/"),
    ("The Diplomat", "https://thediplomat.com/feed/"),
]

# DeepSeek API Configuration
DEEPSEEK_API_KEY = "REDACTED_API_KEY"
DEEPSEEK_MODEL = "deepseek-reasoner"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

# Database Configuration
DATABASE_PATH = Path(__file__).parent.parent / "data" / "geopolitical.db"

# Feishu Webhook Configuration
FEISHU_WEBHOOK_URL = "REDACTED_WEBHOOK"
FEISHU_MESSAGE_TYPE = "text"

# Analysis Thresholds
HIGH_SCORE_THRESHOLD = 7  # Only articles with score >= 7 enter daily report
ARTICLE_TIME_FILTER_HOURS = 24  # Only articles from last N hours

# Request Configuration
RSS_FETCH_TIMEOUT = 30  # seconds
AI_REQUEST_TIMEOUT = 300  # seconds (5 minutes for analysis)
MAX_CONCURRENT_FETCHES = 5  # Max parallel RSS fetches

# Chart Configuration
CHART_KEYWORD_COUNT = 5  # Top N keywords for chart
CHART_SOURCE_COUNT = 5  # Top N sources for chart

# 代理配置
# 本地开发：USE_PROXY = True（使用本地代理）
# GitHub Actions：通过环境变量 USE_PROXY=false 覆盖
PROXY_URL = os.getenv("PROXY_URL", "")
USE_PROXY = os.getenv("USE_PROXY", "true").lower() == "true"  # 默认开启代理
