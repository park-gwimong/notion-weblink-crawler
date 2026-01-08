# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based web crawler that automatically fetches new articles from Naver D2 blog (https://d2.naver.com/helloworld) and adds them to a Notion database called "Weblinks". It runs daily via GitHub Actions or can be executed locally/via cron.

**Primary deployment method**: GitHub Actions (scheduled workflow)

## Core Architecture

### Single-File Design
The entire crawler logic is contained in `d2_to_notion_complete.py` (~260 lines). It uses Playwright for browser automation and Python standard library (urllib, json) for API calls.

**Key components**:
1. **Web Scraping** (`fetch_d2_posts()`) - Uses Playwright to render JavaScript and extract content from DOM
   - Launches headless Chromium browser
   - Waits for page to fully render (`networkidle` state)
   - Queries `.cont_post` article containers
   - Extracts from each article:
     - **Title**: `h2 > a` tag text
     - **URL**: `h2 > a` href attribute
     - **Summary**: `.post_txt` div content
     - **Date**: First `dl > dd` element (format: YYYY.MM.DD)
2. **Notion API Integration** - Direct HTTP calls using urllib (no official SDK)
   - `query_notion_database()` - Queries existing entries
   - `create_notion_page()` - Creates new pages with specific properties
3. **URL Caching** (`notion_urls_cache.txt`) - Prevents duplicate entries by tracking processed URLs
4. **GitHub Actions Integration** - Workflow commits cache updates back to repository

### Data Flow
```
D2 Blog → Playwright (Headless Browser) → Rendered DOM → Selector Extraction → URL Cache Check → Notion API → Cache Update → Git Commit
```

### Notion Integration Details
- **Target Database ID**: Configured in `WEBLINKS_DATA_SOURCE_ID` variable (line 29)
- **Required Properties**:
  - `Name` (title) - Article title
  - `URL` (url) - Article link
  - `Tags` (select) - Always set to "Articles"
  - `Summary` (rich_text) - Article summary/description (first 2000 chars)
  - `Published Date` (date) - Publication date from D2 blog
- **API Version**: 2022-06-28
- **Authentication**: Bearer token from `NOTION_API_KEY` environment variable

## Commands

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Set API key and run crawler
export NOTION_API_KEY="your_integration_token"
python3 d2_to_notion_complete.py

# Quick install (interactive)
./install.sh
```

### GitHub Actions
```bash
# Manual workflow trigger (via GitHub UI)
Actions tab → "D2 Blog to Notion" → "Run workflow"

# The workflow runs automatically daily at 00:00 UTC (09:00 KST)
```

### Cache Management
```bash
# View cached URLs
cat notion_urls_cache.txt

# Reset cache (forces re-processing of all articles)
rm notion_urls_cache.txt
```

## Configuration

### Modifying the Tag
Edit `d2_to_notion_complete.py` around line 178-182:
```python
"Tags": {
    "select": {
        "name": "Articles"  # Change tag here
    }
}
```

### Changing Database ID
If you need to use a different Notion database, update line 29:
```python
WEBLINKS_DATA_SOURCE_ID = "your-database-id-here"
```

To find your database ID, use the Notion search API or check the database URL.

### Changing Article Limit
Edit line 66:
```python
return posts[:10]  # Modify number here
```

### Schedule Modification
Edit `.github/workflows/d2_crawler.yml` line 6:
```yaml
- cron: '0 0 * * *'  # UTC time (00:00 = 09:00 KST)
```

## Critical Constraints

1. **Playwright dependency** - Requires browser binaries (~140MB Chromium download). GitHub Actions workflow handles this automatically.
2. **Headless browser overhead** - Slower than raw HTTP requests but more reliable for JavaScript-rendered content
3. **Database schema dependency** - Requires specific Notion database properties: Name, URL, Tags, Summary, Published Date
4. **DOM selector dependency** - Uses `.cont_post` selector (line 55). May break if D2 blog changes HTML structure.
5. **Cache file dependency** - The workflow commits cache back to repo; requires write permissions
6. **Rate limiting** - 0.3s delay between Notion API calls (line 303)
7. **Windows encoding** - Script includes UTF-8 reconfiguration for Windows console (lines 18-20)
8. **Summary length limit** - Notion rich_text fields limited to 2000 characters (truncated if longer)

## Troubleshooting

### Notion API Errors
- **"Invalid token"**: Check `NOTION_API_KEY` environment variable and Integration permissions
- **"object_not_found" (404)**:
  - Verify Integration is connected to the Weblinks database (... → Connections in Notion)
  - Confirm database ID is correct (line 29)
  - Use Notion search API to find accessible databases
- **"validation_error"**: Database may be missing required properties (Name, URL, Tags, Summary, Published Date)

### Parsing Failures
If D2 blog changes HTML structure, update the DOM selectors:
```python
# Main article container (line 55)
page.wait_for_selector('.cont_post', timeout=10000)
articles = page.query_selector_all('.cont_post')

# Within each article:
h2_link = article.query_selector('h2 a')        # Title & URL
summary_elem = article.query_selector('.post_txt')  # Summary
date_elem = article.query_selector('dl dd')     # Date
```

You can inspect the rendered page structure by removing `headless=True` at line 47 to run Playwright in visible mode.

Current article structure (as of 2025-12):
```html
<div class="cont_post">
    <h2><a href="/helloworld/0004394">Title here</a></h2>
    <div class="post_txt">Summary text...</div>
    <dl>
        <dt><i class="xi-time-o"></i></dt>
        <dd>2025.12.18</dd>
    </dl>
</div>
```

### GitHub Actions Not Running
- Ensure repository is public (private repos require paid plan for scheduled workflows)
- Check that `NOTION_API_KEY` is set in repository secrets
- Verify workflow is enabled in Actions tab
- Repository must have activity within last 60 days

## Important Notes

- The workflow uses `[skip ci]` in commit messages to prevent recursive runs
- Cache file is safe to commit (contains only URLs, no sensitive data)
- The script fetches only the 10 most recent articles on each run
- Duplicate detection relies entirely on the cache file, not Notion API queries