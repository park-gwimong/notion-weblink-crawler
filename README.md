# 네이버 D2 → Notion 자동 크롤러 설치 가이드

## 📋 개요

매일 오전 9시에 네이버 D2 블로그(https://d2.naver.com/helloworld)를 확인하여 새 글을 자동으로 Notion Weblinks 데이터베이스에 추가합니다.

---

## 🎯 배포 옵션

### ⭐ 옵션 1: GitHub Actions (추천)

**장점**: 무료, 설정 간단, 서버 불필요

#### 설정 방법

1. **GitHub 저장소 생성**
   ```bash
   mkdir d2-notion-crawler
   cd d2-notion-crawler
   git init
   ```

2. **파일 복사**
   - `d2_to_notion_complete.py` (메인 스크립트)
   - `.github/workflows/d2_crawler.yml` (GitHub Actions 설정)
   - `notion_urls_cache.txt` (빈 파일)

3. **Notion Integration 생성**
   - https://www.notion.so/my-integrations 접속
   - "New integration" 클릭
   - 이름: "D2 Blog Crawler"
   - Capabilities: "Read content", "Insert content" 선택
   - Integration Token 복사

4. **Notion 데이터베이스에 Integration 연결**
   - Weblinks 데이터베이스 페이지 열기
   - 우측 상단 "..." → "Connections" → "D2 Blog Crawler" 추가

5. **GitHub Secrets 설정**
   - GitHub 저장소 → Settings → Secrets and variables → Actions
   - "New repository secret" 클릭
   - Name: `NOTION_API_KEY`
   - Value: (복사한 Integration Token 붙여넣기)

6. **Push & 실행**
   ```bash
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/username/d2-notion-crawler.git
   git push -u origin main
   ```

7. **수동 테스트**
   - Actions 탭 → "D2 Blog to Notion" → "Run workflow"

#### GitHub Actions 설정 파일 (`workflows/d2_crawler.yml`)

```yaml
name: D2 Blog to Notion

on:
  schedule:
    # 매일 오전 9시 (한국 시간 = UTC 0시)
    - cron: '0 0 * * *'
  workflow_dispatch:  # 수동 실행

jobs:
  crawl:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Run crawler
      env:
        NOTION_API_KEY: ${{ secrets.NOTION_API_KEY }}
      run: python d2_to_notion_complete.py
    
    - name: Commit cache
      run: |
        git config user.name "GitHub Action"
        git config user.email "action@github.com"
        git add notion_urls_cache.txt
        git diff --quiet && git diff --staged --quiet || git commit -m "Update cache"
        git push
```

---

### 옵션 2: 로컬 서버 + Cron

**장점**: 완전한 제어, 추가 기능 쉽게 확장

#### 설정 방법

1. **환경 설정**
   ```bash
   # Python 3.7+ 필요
   python3 --version
   
   # 스크립트 실행 권한
   chmod +x d2_to_notion_complete.py
   ```

2. **환경 변수 설정**
   ```bash
   export NOTION_API_KEY="your_integration_token_here"
   
   # 영구 설정 (bashrc/zshrc)
   echo 'export NOTION_API_KEY="your_token"' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **Cron 설정**
   ```bash
   crontab -e
   
   # 추가할 내용 (매일 오전 9시)
   0 9 * * * cd /path/to/d2-notion-crawler && python3 d2_to_notion_complete.py >> crawler.log 2>&1
   ```

4. **테스트 실행**
   ```bash
   python3 d2_to_notion_complete.py
   ```

---

### 옵션 3: AWS Lambda (고급)

**장점**: 서버리스, 확장성

#### 설정 개요

1. Lambda 함수 생성 (Python 3.10 런타임)
2. 코드 업로드 (`d2_to_notion_complete.py`)
3. 환경 변수 `NOTION_API_KEY` 설정
4. EventBridge로 스케줄 설정 (cron(0 0 * * ? *))
5. S3에 캐시 파일 저장 (옵션)

---

## 🔧 문제 해결

### Notion API 오류

**증상**: "Invalid token" 오류
**해결**: 
- Integration Token이 올바른지 확인
- Weblinks DB에 Integration이 연결되었는지 확인

**증상**: "Parent not found" 오류
**해결**:
- 데이터베이스 ID 확인: `20c6b9de-20ed-4563-8c87-ed03e0539d19`
- Integration이 DB에 접근 권한이 있는지 확인

### 크롤링 오류

**증상**: 글을 가져오지 못함
**해결**:
- D2 블로그 HTML 구조 변경 가능성
- `fetch_d2_posts()` 함수의 정규식 패턴 업데이트

### GitHub Actions 실행 안 됨

**증상**: Scheduled workflow가 실행되지 않음
**해결**:
- Repository가 public인지 확인 (private는 유료)
- 최근 60일 내 commit이 있는지 확인
- Actions 탭에서 workflow가 활성화되어 있는지 확인

---

## 📊 모니터링

### 로그 확인

**GitHub Actions**:
- Actions 탭 → 실행 기록 클릭 → 로그 확인

**로컬 Cron**:
```bash
tail -f crawler.log
```

### 추가된 글 확인

Notion Weblinks 데이터베이스에서:
- Tags가 "Articles"인 항목 필터
- Created 날짜 기준 정렬

---

## 🚀 커스터마이징

### 다른 태그 사용

`d2_to_notion_complete.py` 파일에서:

```python
"Tags": {
    "select": {
        "name": "Articles"  # ← 원하는 태그로 변경
    }
}
```

### 크롤링 개수 변경

```python
return posts[:10]  # ← 숫자 변경 (예: [:20])
```

### 실행 시간 변경

GitHub Actions (`workflows/d2_crawler.yml`):

```yaml
cron: '0 0 * * *'  # UTC 0시 = 한국 9시
# 한국 시간 기준:
# 오전 6시 = '0 21 * * *'
# 정오 12시 = '0 3 * * *'
# 오후 6시 = '0 9 * * *'
```

---

## 📝 파일 구조

```
d2-notion-crawler/
├── d2_to_notion_complete.py    # 메인 스크립트
├── notion_urls_cache.txt         # URL 캐시 (자동 생성)
├── .github/
│   └── workflows/
│       └── d2_crawler.yml        # GitHub Actions 설정
├── README.md                     # 이 파일
└── requirements.txt              # Python 의존성 (옵션)
```

---

## 🔐 보안

- Notion API Token은 절대 코드에 직접 넣지 마세요
- 환경 변수나 GitHub Secrets 사용
- Integration은 필요한 권한만 부여
- 캐시 파일은 공개 저장소에 포함해도 안전 (URL만 저장)

---

## 📞 지원

문제가 발생하면:
1. 로그 확인
2. Notion API 상태 확인 (https://status.notion.so)
3. D2 블로그 접근 가능 여부 확인
4. Integration 권한 재확인
