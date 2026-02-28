# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a local geopolitical intelligence analysis system that generates daily strategic intelligence briefings. It aggregates RSS feeds from international relations and security sources, analyzes them using DeepSeek AI, and delivers reports via Feishu (飞书) webhook.

## Architecture

### Data Flow Pipeline

1. **RSS Ingestion** (10 sources):
   - Al Jazeera, Foreign Affairs, Foreign Policy, Project Syndicate
   - The Conversation, Eurasia Review, War on the Rocks
   - Chatham House, Defense One, The Diplomat

2. **Data Processing**:
   - Time filtering: Keeps articles from last 24 hours
   - Deduplication: Removes articles already in SQLite database

3. **AI Analysis Pipeline**:
   - **First AI Agent**: Analyzes each article with DeepSeek Reasoner
     - Extracts: summary, category, tags, importance_score, deep_insight, impact_level
     - System prompt: Stratfor/RAND style geopolitical analyst
   - **Second AI Agent**: Synthesizes high-value (score>=7) articles into daily report
     - Outputs: Markdown report + chart data (keywords, categories, impact radar, sources)

4. **Output**:
   - SQLite: Stores analyzed articles with status tracking
   - Feishu: Sends HTML report via Webhook

## Common Commands

```bash
# Navigate to project directory (Unix-style path)
cd /c/"proj datamining/info_dyzz/geopolitical-analysis"

# Activate virtual environment (Windows CMD)
venv\Scripts\activate

# Or run Python directly without activation (works in bash)
./venv/Scripts/python.exe run.py --run
./venv/Scripts/python.exe -m src.main --run

# Run full daily workflow (recommended)
python run.py --run

# Or use module invocation
python -m src.main --run

# Run with custom score threshold (5-10)
python run.py --run --score 5

# Run with 24-hour filter for report generation (only includes articles from last 24 hours)
python run.py --run --filter-hours 24

# Combine score threshold and time filter
python run.py --run --score 8 --filter-hours 24

# Validate RSS sources
python run.py --validate-rss

# Analyze single article by ID
python run.py --analyze-one <article_id>

# Run tests
pytest tests/ -v

# Run specific test file
pytest tests/test_rss_fetcher.py -v

# Run single test
pytest tests/test_charts.py::TestKeywordExtraction::test_extract_top_keywords -v

# View database content (using Python)
python -c "
import sqlite3
conn = sqlite3.connect('data/geopolitical.db')
cursor = conn.cursor()
cursor.execute('SELECT id, title, source_name, score FROM articles a LEFT JOIN analyses an ON a.id = an.article_id LIMIT 10')
for row in cursor.fetchall(): print(row)
"
```

## Key Components

### src/config.py
Central configuration file containing:
- RSS sources (10 URLs)
- DeepSeek API credentials
- Feishu webhook URL
- Database path
- Analysis thresholds (HIGH_SCORE_THRESHOLD = 7, ARTICLE_TIME_FILTER_HOURS = 24)

### src/feeds/rss_fetcher.py
RSS fetching module with:
- `fetch_feeds()` - concurrent RSS fetching
- `filter_by_date()` - filters articles from last N hours
- `deduplicate_by_url()` - removes duplicates against database
- `validate_article_data()` - validates required fields (title, link, content)
- `validate_all_sources()` - tests each RSS source

### src/ai/analyzers.py
DeepSeek API integration with:
- `analyze_article()` - single article analysis
- `generate_daily_report()` - synthesizes high-value articles into report
- Uses system prompts from `src/ai/prompts/`

### src/db/models.py & repository.py
SQLite database layer:
- `Article` - stores RSS articles (url is unique index)
- `Analysis` - stores AI analysis results (one-to-one with Article)
- `Report` - caches generated daily reports
- Repository classes provide CRUD operations
- `AnalysisRepository.get_analyses_for_report()` accepts optional `filter_last_hours` parameter

### Data Model Key Fields

**Article**: id, title, url (unique), pub_date, content, source_domain, source_name
**Analysis**: article_id (FK), summary, category, tags (JSON), score (1-10), deep_insight, impact_level
**Report**: report_date (unique), markdown_content, chart_data (JSON)

### src/charts/generator.py
Plotly-based chart generation:
- Keyword bar charts
- Category distribution (donut)
- Impact radar (semicircle)
- Source distribution

### src/feishu/sender.py
Feishu webhook integration:
- `send_to_feishu()` - sync version using requests
- `send_report_to_feishu()` - report sending wrapper
- `adapt_markdown_for_feishu()` - converts Markdown to Feishu-compatible format
- Uses color tags: `<font color='red'>`, `<font color='grey'>`, etc.

### run.py
Simple entry point wrapper that calls `src.main`:
- Accepts same arguments as `python -m src.main`
- Use this for convenience: `python run.py --run`

### src/main.py
Main workflow orchestrator with 8 steps:
1. Fetch RSS feeds
2. Filter by date (last 24 hours)
3. Deduplicate against database
4. Store new articles
5. Analyze new articles with DeepSeek
6. Get high-value articles from database (always runs, uses --filter-hours if specified)
7. Generate daily report
8. Send to Feishu

Note: Step 6 always runs even if there are no new articles - it reads from the existing database.

## Testing

Test files are in `tests/` directory:
- `test_rss_fetcher.py` - RSS fetching and filtering
- `test_rss_validation.py` - RSS data validation
- `test_charts.py` - Chart generation
- `test_feishu.py` - Feishu formatting
- `test_analyzers.py` - AI analysis (mocked)

## Important Notes

- Database is at `data/geopolitical.db` (SQLite)
- Virtual environment is at `venv/`
- All tests pass (37/37)
- API keys and webhook URLs are stored in `.env` file (never commit this file)
- RSS sources require User-Agent header to avoid 403 errors (implemented in rss_fetcher.py)
- Eurasia Review and Chatham House are blocked by GFW in China - they fail gracefully without breaking workflow
- The system uses DeepSeek API (deepseek-reasoner model)
- Reports are sent via Feishu webhook
- Time filtering uses system local timezone (datetime.now())

### AI Analysis Categories
- Conflict & Security
- Diplomacy & Policy
- Global Economy & Trade
- Energy & Resources
- Tech War & Cyber
- Elections & Politics

### Impact Levels
- Global Shift, High Risk, Moderate, Low

### Score Thresholds
- 10: War outbreak, nuclear deterrence, major diplomatic breaks
- 8-9: Military standoff, resource embargoes, international resolutions
- 5-7: Diplomatic summits, trade deals, arms sales
- 1-4: Routine diplomatic messages

Only articles with score >= 7 enter the daily report.

### RSS Field Mapping
RSS feeds return `link` field, but database uses `url`. The rss_fetcher.py maps `url = link` for compatibility.
