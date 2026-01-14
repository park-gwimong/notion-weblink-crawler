# Tech Blog Crawler

기술 블로그 새 글을 Notion에 자동 추가.

## 지원 블로그

| 블로그 | URL |
|--------|-----|
| Naver D2 | https://d2.naver.com/helloworld |
| Kakao Tech | https://tech.kakao.com/blog |
| Toss Tech | https://toss.tech |
| 당근 | https://medium.com/daangn |
| 여기어때 | https://medium.com/gccompany |
| Wanted | https://medium.com/wantedjobs |
| Coupang | https://medium.com/coupang-engineering |
| Ridi | https://ridicorp.com/story-category/tech-blog |

## 빠른 시작

### GitHub Actions (권장)

1. Fork/Clone
2. [Notion Integration](https://www.notion.so/my-integrations) 생성 → Token 복사
3. Notion DB에 Integration 연결 (우측 상단 `...` → Connections)
4. GitHub Settings → Secrets → `NOTION_API_KEY` 추가
5. Actions 탭에서 "Tech Blog Crawler" 수동 실행

이후 매일 09:00 KST에 자동 실행.

### 로컬 실행

```bash
pip install -r requirements.txt
playwright install chromium

export NOTION_API_KEY="your_token"
python main.py
```

## Notion DB 필수 속성

- `Name` (title)
- `URL` (url)
- `Tags` (select)
- `Summary` (rich_text)
- `Published Date` (date)

## 파일 구조

```
├── main.py              # 진입점
├── config.py            # 설정
├── cache.py             # URL 캐시
├── notion_client.py     # Notion API
├── crawlers/
│   ├── base.py          # 크롤러 베이스
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

## 새 크롤러 추가

1. `crawlers/` 디렉토리에 새 파일 생성
2. `BaseCrawler` 상속, `parse_posts()` 구현
3. `crawlers/__init__.py`의 `CRAWLERS` 리스트에 추가

```python
from .base import BaseCrawler, Post

class NewCrawler(BaseCrawler):
    name = "NewBlog"
    source_id = "newblog"
    base_url = "https://example.com/blog"

    def parse_posts(self, page):
        posts = []
        page.wait_for_selector('.post', timeout=self.timeout)
        for item in page.query_selector_all('.post'):
            # 제목, URL, 요약, 날짜 파싱
            posts.append(Post(title=..., url=..., source=self.source_id))
        return posts
```

## 문제 해결

- **Invalid token**: `NOTION_API_KEY` 환경변수 확인
- **404 오류**: Notion DB에 Integration 연결 확인
- **글이 안 올라감**: `notion_urls_cache.txt` 삭제 후 재실행
- **셀렉터 오류**: 블로그 구조 변경됨. 해당 크롤러 파일 수정 필요
