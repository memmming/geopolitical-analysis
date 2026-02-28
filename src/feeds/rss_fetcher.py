"""
RSS Feed Fetcher Module
Handles fetching, parsing, filtering, and validating RSS feeds
"""
import asyncio
import aiohttp
import feedparser
from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta
from urllib.parse import urlparse
import logging

from src.config import (
    RSS_SOURCES,
    RSS_FETCH_TIMEOUT,
    ARTICLE_TIME_FILTER_HOURS,
    MAX_CONCURRENT_FETCHES,
    PROXY_URL,
    USE_PROXY,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Article:
    """Represents a news article from RSS feed"""

    def __init__(
        self,
        title: str,
        url: str,
        pub_date: Optional[datetime],
        content: str,
        source_domain: str,
        source_name: str,
    ):
        self.title = title
        self.url = url
        self.pub_date = pub_date
        self.content = content
        self.source_domain = source_domain
        self.source_name = source_name

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "url": self.url,
            "pub_date": self.pub_date.isoformat() if self.pub_date else None,
            "content": self.content,
            "source_domain": self.source_domain,
            "source_name": self.source_name,
        }


def validate_article_data(article: Dict) -> bool:
    """
    Validate RSS article data integrity

    Args:
        article: Parsed article dictionary

    Returns:
        bool: True if article has all required fields
    """
    required_fields = ["title", "link"]
    content_fields = [
        "content",
        "description",
        "contentSnippet",
        "summary",
        "content:encoded",
    ]

    # Check required fields
    if not all(field in article and article.get(field) for field in required_fields):
        return False

    # Check for at least one content field
    has_content = any(article.get(field) for field in content_fields)
    if not has_content:
        return False

    # Validate URL format
    try:
        url = article["link"]
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def parse_feed_data(feed_data: feedparser.FeedParserDict, source_name: str) -> List[Dict]:
    """
    Parse feedparser data and extract articles

    Args:
        feed_data: Parsed RSS feed data
        source_name: Name of the RSS source

    Returns:
        List of article dictionaries
    """
    articles = []
    parsed_domain = urlparse(feed_data.get("feed", {}).get("link", "")).netloc

    for entry in feed_data.get("entries", []):
        # Extract basic fields
        title = entry.get("title", "")
        link = entry.get("link", "")

        # Extract publication date
        pub_date = None
        if "published_parsed" in entry and entry["published_parsed"]:
            pub_date = datetime(*entry["published_parsed"][:6])
        elif "updated_parsed" in entry and entry["updated_parsed"]:
            pub_date = datetime(*entry["updated_parsed"][:6])

        # Extract content (try multiple fields)
        content = ""
        content_fields = ["content", "description", "contentSnippet", "summary"]
        for field in content_fields:
            if field in entry:
                content_value = entry[field]
                if isinstance(content_value, list) and content_value:
                    content_value = content_value[0]
                if isinstance(content_value, dict) and "value" in content_value:
                    content_value = content_value["value"]
                if content_value:
                    content = str(content_value)
                    break

        # Validate and add article
        article_data = {
            "title": title,
            "url": link,  # Use 'url' as the primary field for database storage
            "link": link,
            "pub_date": pub_date,
            "content": content,
            "source_domain": parsed_domain or urlparse(link).netloc,
            "source_name": source_name,
        }

        if validate_article_data(article_data):
            articles.append(article_data)
        else:
            logger.warning(f"Invalid article data from {source_name}: {title[:50]}...")

    return articles


async def fetch_single_feed(
    session: aiohttp.ClientSession, source_name: str, source_url: str
) -> List[Dict]:
    """
    Fetch and parse a single RSS feed

    Args:
        session: aiohttp session
        source_name: Name of the RSS source
        source_url: URL of the RSS feed

    Returns:
        List of parsed article dictionaries
    """
    # 添加浏览器级别的User-Agent请求头，避免403错误
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        async with session.get(source_url, headers=headers, timeout=aiohttp.ClientTimeout(total=RSS_FETCH_TIMEOUT)) as response:
            if response.status != 200:
                logger.error(f"Failed to fetch {source_name}: HTTP {response.status}")
                return []

            content = await response.text()

            # Parse RSS content
            feed_data = feedparser.parse(content)
            articles = parse_feed_data(feed_data, source_name)

            logger.info(f"Fetched {len(articles)} articles from {source_name}")
            return articles

    except asyncio.TimeoutError:
        logger.error(f"Timeout fetching {source_name}")
        return []
    except Exception as e:
        logger.error(f"Error fetching {source_name}: {str(e)}")
        return []


async def fetch_feeds(feed_urls: List[tuple] = None) -> List[Dict]:
    """
    Fetch all RSS feeds concurrently

    Args:
        feed_urls: List of (name, url) tuples. If None, uses RSS_SOURCES from config.

    Returns:
        List of all parsed article dictionaries
    """
    if feed_urls is None:
        feed_urls = RSS_SOURCES

    all_articles = []

    # Create semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_FETCHES)

    async def fetch_with_semaphore(session, name, url):
        async with semaphore:
            return await fetch_single_feed(session, name, url)

    # Create session with proxy support if enabled
    # Use environment variables for proxy (aiohttp supports HTTP_PROXY/HTTPS_PROXY)
    session_kwargs = {"trust_env": True}
    if USE_PROXY and PROXY_URL:
        import os
        os.environ["HTTP_PROXY"] = PROXY_URL
        os.environ["HTTPS_PROXY"] = PROXY_URL
    async with aiohttp.ClientSession(**session_kwargs) as session:
        tasks = [fetch_with_semaphore(session, name, url) for name, url in feed_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Fetch error: {str(result)}")

    logger.info(f"Total articles fetched: {len(all_articles)}")
    return all_articles


def filter_by_date(articles: List[Dict], hours: int = ARTICLE_TIME_FILTER_HOURS) -> List[Dict]:
    """
    Filter articles by publication date

    Args:
        articles: List of article dictionaries
        hours: Number of hours to keep articles from

    Returns:
        Filtered list of articles
    """
    cutoff_time = datetime.now() - timedelta(hours=hours)
    filtered = []

    for article in articles:
        pub_date = article.get("pub_date")
        if pub_date and pub_date > cutoff_time:
            filtered.append(article)

    logger.info(f"Filtered to {len(filtered)} articles (last {hours} hours)")
    return filtered


def deduplicate_by_url(
    articles: List[Dict], existing_urls: Optional[Set[str]] = None
) -> List[Dict]:
    """
    Deduplicate articles by URL

    Args:
        articles: List of article dictionaries
        existing_urls: Set of URLs to exclude (already processed)

    Returns:
        Deduplicated list of articles
    """
    if existing_urls is None:
        existing_urls = set()

    seen_urls = set(existing_urls)
    unique_articles = []

    for article in articles:
        url = article.get("url", article.get("link", ""))
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_articles.append(article)

    logger.info(
        f"Deduplicated: {len(articles)} -> {len(unique_articles)} articles "
        f"(removed {len(articles) - len(unique_articles)} duplicates)"
    )
    return unique_articles


def validate_feed_data(feed_data: Dict) -> bool:
    """
    Validate RSS feed data completeness

    Args:
        feed_data: Parsed feed data

    Returns:
        bool: True if feed data is valid
    """
    required_keys = ["feed", "entries"]
    if not all(key in feed_data for key in required_keys):
        return False

    # Check if feed has entries
    if not feed_data.get("entries"):
        logger.warning("Feed has no entries")
        return False

    return True


async def validate_all_sources() -> Dict[str, Dict]:
    """
    Validate all RSS sources and report results

    Returns:
        Dictionary with validation results for each source
    """
    logger.info("Starting RSS source validation...")

    validation_results = {}

    # Set proxy environment variables if enabled
    session_kwargs = {"trust_env": True}
    if USE_PROXY and PROXY_URL:
        import os
        os.environ["HTTP_PROXY"] = PROXY_URL
        os.environ["HTTPS_PROXY"] = PROXY_URL
    async with aiohttp.ClientSession(**session_kwargs) as session:
        for source_name, source_url in RSS_SOURCES:
            try:
                async with session.get(
                    source_url, timeout=aiohttp.ClientTimeout(total=RSS_FETCH_TIMEOUT)
                ) as response:
                    if response.status != 200:
                        validation_results[source_name] = {
                            "status": "failed",
                            "error": f"HTTP {response.status}",
                        }
                        continue

                    content = await response.text()
                    feed_data = feedparser.parse(content)

                    if not validate_feed_data(feed_data):
                        validation_results[source_name] = {
                            "status": "failed",
                            "error": "Invalid feed data structure",
                        }
                        continue

                    articles = parse_feed_data(feed_data, source_name)
                    validation_results[source_name] = {
                        "status": "success",
                        "articles_count": len(articles),
                        "sample_article": articles[0] if articles else None,
                    }

            except Exception as e:
                validation_results[source_name] = {
                    "status": "error",
                    "error": str(e),
                }

    return validation_results


if __name__ == "__main__":
    # Test the module
    async def main():
        print("Validating RSS sources...")
        results = await validate_all_sources()

        print("\nValidation Results:")
        print("=" * 80)
        for source, result in results.items():
            status = result["status"]
            print(f"\n{source}: {status.upper()}")

            if status == "success":
                print(f"  Articles fetched: {result['articles_count']}")
                if result.get("sample_article"):
                    article = result["sample_article"]
                    print(f"  Sample title: {article.get('title', 'N/A')[:60]}...")
                    print(f"  Sample URL: {article.get('link', 'N/A')[:60]}...")
            else:
                print(f"  Error: {result.get('error', 'Unknown error')}")

    asyncio.run(main())
