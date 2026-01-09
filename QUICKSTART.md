# 빠른 시작

## GitHub Actions로 실행 (권장)

1. 이 저장소를 Fork 또는 Clone

2. Notion Integration 생성
   - https://www.notion.so/my-integrations → New integration
   - Token 복사

3. Notion DB에 Integration 연결
   - Weblinks DB → `...` → Connections → Integration 추가

4. GitHub Secret 추가
   - Settings → Secrets → Actions → `NOTION_API_KEY` 추가

5. 수동 실행으로 테스트
   - Actions → "D2 Blog to Notion" → Run workflow

이후 매일 오전 9시(KST)에 자동 실행됨.

---

## 로컬 실행

```bash
# 의존성 설치
pip install -r requirements.txt
playwright install chromium

# 실행
export NOTION_API_KEY="your_token"
python d2_to_notion_complete.py
```

또는 `./install.sh` 실행.

---

## 필수 조건

Notion DB에 아래 속성 필요:
- Name (title)
- URL (url)
- Tags (select)
- Summary (rich_text)
- Published Date (date)

---

상세 내용은 README.md 참고.
