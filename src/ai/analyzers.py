"""
AI Analyzers Module - DeepSeek API Integration
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from openai import AsyncOpenAI
from src.config import DEEPSEEK_API_KEY, DEEPSEEK_MODEL, DEEPSEEK_BASE_URL, AI_REQUEST_TIMEOUT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load prompts
PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt(filename: str) -> str:
    """Load prompt from file"""
    prompt_path = PROMPTS_DIR / filename
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


# Initialize DeepSeek client
client = AsyncOpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
)


async def analyze_article(
    title: str,
    url: str,
    content: str,
    pub_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Analyze a single article using DeepSeek

    Args:
        title: Article title
        url: Article URL
        content: Article content
        pub_date: Publication date

    Returns:
        Dictionary with analysis results
    """
    system_prompt = load_prompt("article_analysis_system.txt")

    # Build user prompt with article data
    user_prompt = f"""Title: {title}
Link: {url}
PubDate: {pub_date or 'N/A'}
Content Source: {content}

(Instruction: If content is truncated, infer the strategic implication from the title. Focus on: Who gains power? Who faces security risks? What is the geopolitical impact?)"""

    try:
        response = await client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            timeout=AI_REQUEST_TIMEOUT,
        )

        # Parse the JSON response
        response_text = response.choices[0].message.content.strip()

        # Try to extract JSON from response (handle potential markdown code blocks)
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = response_text

        result = json.loads(json_str)

        # Validate required fields
        required_fields = ["summary", "category", "tags", "importance_score", "deep_insight", "impact_level"]
        for field in required_fields:
            if field not in result:
                logger.warning(f"Missing field in analysis: {field}")
                result[field] = None

        return result

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        logger.error(f"Response text: {response_text}")
        return None
    except Exception as e:
        logger.error(f"Error analyzing article: {e}")
        return None


async def generate_daily_report(analyses_data: List[Dict[str, Any]], run_date: str) -> Optional[Dict[str, Any]]:
    """
    Generate daily report from high-value articles using DeepSeek

    Args:
        analyses_data: List of analysis dictionaries with article data
        run_date: Report date in YYYY-MM-DD format

    Returns:
        Dictionary with report content and chart data
    """
    system_prompt = load_prompt("report_generation_system.txt")

    # Build context from high-value articles
    report_context_parts = []
    for item in analyses_data:
        context = f"""---
Title: {item['title']}
Link: {item['url']}
Score: {item['score']}
Category: {item['category']}
Tags: {', '.join(item.get('tags', []))}
Impact Level: {item['impact_level']}
Summary: {item['summary']}
Deep Insight: {item['deep_insight']}
Source: {item['source_name']}
---
"""
        report_context_parts.append(context)

    report_context = "\n".join(report_context_parts)

    # Build user prompt
    user_prompt = f"""Run Date: {run_date}

**Geopolitical Intelligence Context:**
请根据以下素材撰写战略报告。**请注意：每条素材都包含了原始链接 (Link)，在写报告时必须严格引用这些链接！**

{report_context}

(Instruction: Synthesize the report in professional Chinese (Think Tank style). MUST include Markdown links for key events.)"""

    try:
        response = await client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.5,
            timeout=AI_REQUEST_TIMEOUT,
        )

        # Parse the JSON response
        response_text = response.choices[0].message.content.strip()

        # Try to extract JSON from response
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = response_text

        result = json.loads(json_str)

        # Validate required fields
        if "raw_article" not in result:
            logger.warning("Missing 'raw_article' field in report response")
            result["raw_article"] = ""

        if "chart_data" not in result:
            logger.warning("Missing 'chart_data' field in report response")
            result["chart_data"] = {}

        return result

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        logger.error(f"Response text: {response_text}")
        return None
    except Exception as e:
        logger.error(f"Error generating daily report: {e}")
        return None


async def analyze_articles_batch(article_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analyze multiple articles concurrently

    Args:
        article_data_list: List of article dictionaries

    Returns:
        List of analysis results
    """
    tasks = [
        analyze_article(
            title=item.get("title", ""),
            url=item.get("url", ""),
            content=item.get("content", ""),
            pub_date=item.get("pub_date"),
        )
        for item in article_data_list
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    analyses = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Error analyzing article {i}: {str(result)}")
        elif result is not None:
            analyses.append({
                "article_data": article_data_list[i],
                "analysis": result,
            })

    return analyses


if __name__ == "__main__":
    # Test the analyzers
    async def test_analyze():
        test_article = {
            "title": "测试标题：某国宣布新的制裁措施",
            "url": "https://example.com/article",
            "content": "这是测试内容，描述了某国对另一个国家实施新的经济制裁措施。",
            "pub_date": "2024-02-24T10:00:00Z",
        }

        print("Testing article analysis...")
        result = await analyze_article(**test_article)
        if result:
            print("Analysis result:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("Analysis failed")

    asyncio.run(test_analyze())
