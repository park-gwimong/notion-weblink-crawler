# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based web crawler that automatically fetches new articles from tech blogs and adds them to a Notion database called "Weblinks". It runs daily via GitHub Actions or can be executed locally/via cron.

**Supported blogs**:
- Naver D2 (https://d2.naver.com/helloworld)
- Kakao Tech (https://tech.kakao.com/blog)
- Toss Tech (https://toss.tech/category/engineering)

**Primary deployment method**: GitHub Actions (scheduled workflow)

## Project Structure

```
notion-weblink-crawler/
├── main.py                 # 진입점 - 메인 실행 로직
├── config.py               # 설정 - 환경변수, 상수
├── cache.py                # 캐시 관리 - URL 중복 방지
├── notion_client.py        # Notion API 클라이언트
├── crawlers/
│   ├── __init__.py         # 크롤러 모듈 export
│   ├── base.py             # BaseCrawler 추상 클래스
│   ├── d2.py               # D2 블로그 크롤러
│   ├── kakao.py            # 카카오 테크 크롤러
│   └── toss.py             # 토스 테크 크롤러
├── .github/workflows/
│   └── crawler.yml         # GitHub Actions 워크플로우
├── requirements.txt
└── notion_urls_cache.txt   # URL 캐시 파일
```

## Core Architecture

### 모듈 구조

1. **config.py** - 중앙 설정 관리
   - `NOTION_API_TOKEN`, `WEBLINKS_DATABASE_ID`
   - `MAX_POSTS_PER_SOURCE`, `REQUEST_DELAY`, `PLAYWRIGHT_TIMEOUT`
   - `BLOG_URLS` - 블로그 URL 매핑

2. **cache.py** - URLCache 클래스
   - `load()` - 캐시 파일 로드
   - `contains(url)` / `__contains__` - URL 존재 확인
   - `add(url)` - URL 추가 및 파일 저장

3. **notion_client.py** - NotionClient 클래스
   - `query_database()` - 데이터베이스 쿼리
   - `create_page()` - 페이지 생성

4. **crawlers/base.py** - BaseCrawler 추상 클래스
   - `name`, `source_id`, `base_url` - 크롤러 메타데이터
   - `fetch()` - 블로그 크롤링 실행
   - `parse_posts(page)` - 서브클래스에서 구현 (추상 메서드)

5. **crawlers/d2.py, kakao.py** - 구체 크롤러
   - `BaseCrawler` 상속
   - `parse_posts()` 구현

### Data Flow
```
main.py → CRAWLERS 순회 → 각 크롤러.fetch() → Playwright 렌더링
→ parse_posts() → Post 객체 → cache 체크 → NotionClient.create_page() → cache.add()
```

## Commands

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Set API key and run
export NOTION_API_KEY="your_integration_token"
python main.py
```

### GitHub Actions
```bash
# Manual workflow trigger (via GitHub UI)
Actions tab → "Tech Blog Crawler" → "Run workflow"

# The workflow runs automatically daily at 00:00 UTC (09:00 KST)
```

### Cache Management
```bash
# View cached URLs
cat notion_urls_cache.txt

# Reset cache (forces re-processing of all articles)
rm notion_urls_cache.txt
```

## Adding a New Crawler

1. Create `crawlers/newblog.py`:
```python
from .base import BaseCrawler, Post

class NewBlogCrawler(BaseCrawler):
    name = "NewBlog"
    source_id = "newblog"
    base_url = "https://newblog.example.com"

    def parse_posts(self, page):
        posts = []
        # DOM 파싱 로직 구현
        page.wait_for_selector('.post-item', timeout=self.timeout)
        items = page.query_selector_all('.post-item')
        for item in items:
            # ... 제목, URL, 요약, 날짜 추출
            posts.append(Post(title=..., url=..., source=self.source_id))
        return posts

def fetch_newblog_posts():
    return NewBlogCrawler().fetch()
```

2. Update `crawlers/__init__.py`:
```python
from .newblog import NewBlogCrawler, fetch_newblog_posts

CRAWLERS = [
    D2Crawler,
    KakaoCrawler,
    NewBlogCrawler,  # 추가
]
```

## Configuration

### config.py 주요 설정

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `NOTION_API_TOKEN` | Notion API 토큰 | 환경변수 `NOTION_API_KEY` |
| `WEBLINKS_DATABASE_ID` | 대상 데이터베이스 ID | (하드코딩) |
| `MAX_POSTS_PER_SOURCE` | 블로그당 최대 글 수 | 10 |
| `REQUEST_DELAY` | API 호출 간 딜레이 | 0.3초 |
| `PLAYWRIGHT_TIMEOUT` | 렌더링 타임아웃 | 15000ms |

### Notion Database 속성

| 속성 | 타입 | 설명 |
|------|------|------|
| Name | title | 글 제목 |
| URL | url | 글 링크 |
| Tags | select | 기본값 "Articles" |
| Summary | rich_text | 요약 (최대 2000자) |
| Published Date | date | 발행일 |

## Troubleshooting

### Notion API Errors
- **"Invalid token"**: `NOTION_API_KEY` 환경변수 확인
- **"object_not_found" (404)**: Integration이 데이터베이스에 연결되었는지 확인
- **"validation_error"**: 데이터베이스 속성 확인 (Name, URL, Tags, Summary, Published Date)

### Parsing Failures

#### D2 Blog (`crawlers/d2.py`)
```python
# 셀렉터 (D2Crawler.parse_posts)
page.wait_for_selector('.cont_post')
articles = page.query_selector_all('.cont_post')
h2_link = article.query_selector('h2 a')        # 제목 & URL
summary_elem = article.query_selector('.post_txt')  # 요약
date_elem = article.query_selector('dl dd')     # 날짜
```

#### Kakao Tech Blog (`crawlers/kakao.py`)
```python
# 셀렉터 (KakaoCrawler.parse_posts)
page.wait_for_selector('.link_post')
post_cards = page.query_selector_all('.link_post')
title_elem = card.query_selector('.tit_post')      # 제목
summary_elem = card.query_selector('.desc_post')   # 요약
date_elem = card.query_selector('.txt_date')       # 날짜
```

#### Toss Tech Blog (`crawlers/toss.py`)
```python
# 셀렉터 (TossCrawler.parse_posts)
page.wait_for_selector('a[href^="/article/"]')
post_links = page.query_selector_all('a[href^="/article/"]')
title_elem = link.query_selector('h3, h2, [class*="title"]')  # 제목
summary_elem = link.query_selector('p, [class*="desc"]')      # 요약
date_elem = link.query_selector('time, [class*="date"]')      # 날짜
```

디버깅: `BaseCrawler.fetch()`에서 `headless=False`로 변경하여 브라우저 확인

### GitHub Actions Not Running
- Repository가 public인지 확인 (private은 유료 플랜 필요)
- `NOTION_API_KEY` secret 설정 확인
- Actions 탭에서 워크플로우 활성화 확인

## Important Notes

- 워크플로우는 `[skip ci]` 커밋 메시지로 재귀 실행 방지
- 캐시 파일은 URL만 포함 (민감 정보 없음)
- 각 블로그당 최신 10개 글 크롤링
- 각 포스트에 `source` 필드로 출처 추적 ('d2', 'kakao', 'toss' 등)
