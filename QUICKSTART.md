# 빠른 시작

## GitHub Actions

1. Fork/Clone
2. https://www.notion.so/my-integrations → New integration → Token 복사
3. Notion DB → `...` → Connections → Integration 추가
4. GitHub Settings → Secrets → `NOTION_API_KEY` 추가
5. Actions → "Tech Blog Crawler" → Run workflow

매일 09:00 KST 자동 실행.

## 로컬 실행

```bash
pip install -r requirements.txt
playwright install chromium

export NOTION_API_KEY="your_token"
python main.py
```

## Notion DB 필수 속성

- Name (title)
- URL (url)
- Tags (select)
- Summary (rich_text)
- Published Date (date)
