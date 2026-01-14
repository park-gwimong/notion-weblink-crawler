# CLAUDE.md

## 프로젝트 개요

기술 블로그 새 글을 Notion "Weblinks" DB에 자동 추가하는 크롤러.
GitHub Actions로 매일 09:00 KST 실행.

## 지원 블로그

| 크롤러 | 블로그 | 방식 |
|--------|--------|------|
| D2Crawler | d2.naver.com | Playwright |
| KakaoCrawler | tech.kakao.com | Playwright |
| TossCrawler | toss.tech | Playwright |
| DaangnCrawler | medium.com/daangn | Playwright |
| GCCompanyCrawler | medium.com/gccompany | RSS |
| WantedCrawler | medium.com/wantedjobs | Playwright |
| CoupangCrawler | medium.com/coupang-engineering | Playwright |
| RidiCrawler | ridicorp.com | Playwright |

## 파일 구조

```
├── main.py              # 진입점
├── config.py            # 환경변수, 상수
├── cache.py             # URL 캐시 (중복 방지)
├── notion_client.py     # Notion API
├── crawlers/
│   ├── __init__.py      # CRAWLERS 리스트
│   ├── base.py          # BaseCrawler, Post
│   ├── d2.py
│   ├── kakao.py
│   ├── toss.py
│   ├── daangn.py
│   ├── gccompany.py     # RSS 기반
│   ├── wanted.py
│   ├── coupang.py
│   └── ridi.py
└── .github/workflows/
    └── crawler.yml
```

## 데이터 흐름

```
main.py
  → CRAWLERS 순회
  → 각 크롤러.fetch()
  → Playwright/RSS로 파싱
  → Post 객체 생성
  → cache 체크
  → NotionClient.create_page()
  → cache.add()
```

## 명령어

```bash
# 로컬 실행
pip install -r requirements.txt
playwright install chromium
export NOTION_API_KEY="your_token"
python main.py

# 캐시 초기화
rm notion_urls_cache.txt
```

## 새 크롤러 추가

1. `crawlers/newblog.py` 생성:

```python
from .base import BaseCrawler, Post

class NewBlogCrawler(BaseCrawler):
    name = "NewBlog"
    source_id = "newblog"
    base_url = "https://example.com/blog"

    def parse_posts(self, page):
        posts = []
        page.wait_for_selector('.post', timeout=self.timeout)
        for item in page.query_selector_all('.post'):
            title = item.query_selector('h2').inner_text()
            url = item.query_selector('a').get_attribute('href')
            posts.append(Post(title=title, url=url, source=self.source_id))
        return posts

def fetch_newblog_posts():
    return NewBlogCrawler().fetch()
```

2. `crawlers/__init__.py` 수정:

```python
from .newblog import NewBlogCrawler, fetch_newblog_posts

CRAWLERS = [
    # 기존 크롤러들...
    NewBlogCrawler,
]
```

## 설정값 (config.py)

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `NOTION_API_TOKEN` | API 토큰 | 환경변수 |
| `WEBLINKS_DATABASE_ID` | DB ID | 하드코딩 |
| `MAX_POSTS_PER_SOURCE` | 블로그당 최대 글 수 | 10 |
| `REQUEST_DELAY` | API 호출 딜레이 | 0.3초 |
| `PLAYWRIGHT_TIMEOUT` | 렌더링 타임아웃 | 15000ms |

## Notion DB 속성

| 속성 | 타입 |
|------|------|
| Name | title |
| URL | url |
| Tags | select |
| Summary | rich_text (최대 2000자) |
| Published Date | date |

## 트러블슈팅

### Notion API

- **Invalid token**: `NOTION_API_KEY` 환경변수 확인
- **404 object_not_found**: DB에 Integration 연결 확인
- **validation_error**: DB 속성 이름/타입 확인

### 파싱 실패

각 크롤러의 CSS 셀렉터가 블로그 구조 변경으로 깨질 수 있음.

디버깅: `base.py`의 `headless=True`를 `False`로 변경 후 브라우저 확인.

### GitHub Actions

- Private 저장소는 유료 플랜 필요
- 60일 이상 비활성 시 스케줄 중단
- Actions 탭에서 워크플로우 활성화 확인
