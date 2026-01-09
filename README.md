# D2 Blog → Notion 크롤러

네이버 D2 블로그의 새 글을 Notion 데이터베이스에 자동으로 추가하는 크롤러.

매일 오전 9시(KST)에 GitHub Actions로 실행되며, 새 글이 있으면 Notion Weblinks DB에 추가한다.

## 동작 방식

1. Playwright로 D2 블로그 페이지 렌더링 (JavaScript 실행 필요)
2. `.cont_post` 셀렉터로 글 목록 파싱
3. 캐시 파일(`notion_urls_cache.txt`)과 비교하여 새 글 필터링
4. Notion API로 새 글 추가
5. 캐시 파일 업데이트 후 커밋

## 설정

### 1. Notion Integration 생성

https://www.notion.so/my-integrations 에서 새 Integration 생성 후 Token 복사.

### 2. Notion DB에 Integration 연결

Weblinks 데이터베이스 → 우측 상단 `...` → Connections → 생성한 Integration 추가.

DB에 아래 속성이 있어야 함:
- `Name` (title)
- `URL` (url)
- `Tags` (select)
- `Summary` (rich_text)
- `Published Date` (date)

### 3. GitHub Secrets 설정

Repository → Settings → Secrets and variables → Actions → `NOTION_API_KEY` 추가.

### 4. 실행

- 자동: 매일 UTC 00:00 (KST 09:00)
- 수동: Actions 탭 → "D2 Blog to Notion" → Run workflow

## 로컬 실행

```bash
pip install -r requirements.txt
playwright install chromium

export NOTION_API_KEY="your_token"
python d2_to_notion_complete.py
```

Windows:
```powershell
$env:NOTION_API_KEY="your_token"
python d2_to_notion_complete.py
```

## 파일 구조

```
├── d2_to_notion_complete.py    # 메인 스크립트
├── notion_urls_cache.txt       # 처리된 URL 캐시
├── requirements.txt            # 의존성 (playwright)
├── install.sh                  # 로컬 설치 스크립트
└── .github/workflows/
    └── d2_crawler.yml          # GitHub Actions 설정
```

## 설정 변경

### 태그 변경

`d2_to_notion_complete.py` 178-182행:
```python
"Tags": {
    "select": {
        "name": "Articles"  # 변경
    }
}
```

### 크롤링 개수

`d2_to_notion_complete.py` 109행:
```python
return posts[:10]  # 숫자 변경
```

### 실행 시간

`.github/workflows/d2_crawler.yml` 6행:
```yaml
- cron: '0 0 * * *'  # UTC 기준
```

## 문제 해결

### "Invalid token" 오류

- `NOTION_API_KEY` 환경변수 또는 GitHub Secret 확인
- Integration Token이 유효한지 확인

### "object_not_found" (404) 오류

- Notion DB에 Integration이 연결되어 있는지 확인 (Connections 메뉴)
- `d2_to_notion_complete.py` 29행의 DB ID가 맞는지 확인

### 글이 추가되지 않음

- `notion_urls_cache.txt` 삭제 후 재실행 (캐시에 이미 있으면 스킵)
- DB 속성(Name, URL, Tags, Summary, Published Date) 존재 여부 확인

### D2 블로그 구조 변경 시

`d2_to_notion_complete.py`의 셀렉터 수정:
```python
# 55행: 글 목록 컨테이너
page.wait_for_selector('.cont_post', timeout=10000)

# 67행: 제목/URL
h2_link = article.query_selector('h2 a')

# 88행: 요약
summary_elem = article.query_selector('.post_txt')

# 92행: 날짜
date_elem = article.query_selector('dl dd')
```

### GitHub Actions 실행 안 됨

- Private 저장소는 유료 플랜 필요
- 60일 이상 활동 없는 저장소는 스케줄 비활성화됨
- Actions 탭에서 workflow 활성화 상태 확인
