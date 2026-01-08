# 🚀 빠른 시작 가이드

## 3분 안에 시작하기

### 방법 1: GitHub Actions (가장 쉬움) ⭐

```bash
# 1. GitHub에서 새 저장소 생성
# 2. 이 폴더를 업로드
# 3. Settings → Secrets → NOTION_API_KEY 추가
# 4. 끝! 매일 자동 실행됩니다.
```

**상세 가이드**: `README.md` 파일 참조

---

### 방법 2: 로컬 실행 (테스트용)

```bash
# 1. Notion Integration Token 발급
#    https://www.notion.so/my-integrations
#    - "New integration" 클릭
#    - 이름: "D2 Blog Crawler"
#    - Capabilities: "Read content", "Insert content"
#    - Token 복사

# 2. 실행
export NOTION_API_KEY="your_token_here"
python3 d2_to_notion_complete.py

# 3. 결과 확인
# Notion Weblinks DB에 새 글이 추가됩니다!
```

---

## 📂 파일 설명

- **d2_to_notion_complete.py** - 메인 스크립트
- **README.md** - 상세 가이드 (꼭 읽어보세요!)
- **.github/workflows/d2_crawler.yml** - GitHub Actions 설정
- **install.sh** - 로컬 설치 스크립트
- **notion_urls_cache.txt** - URL 캐시 (자동 생성)

---

## ⚙️ 필수 설정

### 1. Notion Integration 생성

https://www.notion.so/my-integrations

### 2. Weblinks DB에 Integration 연결

Weblinks 데이터베이스 → 우측 상단 "..." → Connections → Integration 추가

### 3. 실행 방법 선택

- **GitHub Actions**: 무료, 자동, 추천
- **로컬 Cron**: 서버가 있다면
- **수동 실행**: 테스트용

---

## 🐛 문제 해결

**오류**: "Invalid token"
→ Integration Token 재확인, DB 연결 확인

**오류**: "Parent not found"
→ Weblinks DB ID 확인: `20c6b9de-20ed-4563-8c87-ed03e0539d19`

**새 글이 추가되지 않음**
→ 캐시 파일 삭제: `rm notion_urls_cache.txt`

---

## 📞 더 알아보기

- 상세 가이드: `README.md`
- Notion API 문서: https://developers.notion.com
- D2 블로그: https://d2.naver.com/helloworld
