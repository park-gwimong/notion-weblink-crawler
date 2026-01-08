#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 D2 블로그 → Notion Weblinks 완전 자동화
Notion API를 직접 사용하는 버전
Playwright를 사용하여 렌더된 DOM에서 크롤링
"""

import os
import sys
import json
import time
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


# ============================================================================
# 설정
# ============================================================================

# Notion API 설정
NOTION_API_TOKEN = os.getenv('NOTION_API_KEY', '')  # 환경변수에서 가져오기
WEBLINKS_DATA_SOURCE_ID = "89728ea5-acb0-423c-b047-14ef6ce4ca83"  # Weblinks 데이터베이스 ID

# 네이버 D2 블로그
D2_BLOG_URL = "https://d2.naver.com/helloworld"

# 캐시 파일
CACHE_FILE = "notion_urls_cache.txt"


# ============================================================================
# D2 블로그 크롤링
# ============================================================================

def fetch_d2_posts():
    """D2 블로그에서 최신 글 가져오기 (Playwright로 렌더된 DOM 크롤링)"""
    try:
        with sync_playwright() as p:
            # 브라우저 실행 (headless 모드)
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # D2 블로그 페이지 로드
            print("  🌐 페이지 로딩 중...")
            page.goto(D2_BLOG_URL, wait_until="networkidle")

            # JavaScript 렌더링 대기
            page.wait_for_selector('.cont_post', timeout=10000)

            # 렌더된 DOM에서 글 목록 추출
            posts = []
            seen_urls = set()

            # 모든 article 선택
            articles = page.query_selector_all('.cont_post')

            for article in articles:
                try:
                    # h2 > a 태그에서 제목과 URL 추출
                    h2_link = article.query_selector('h2 a')
                    if not h2_link:
                        continue

                    title = h2_link.inner_text().strip()
                    href = h2_link.get_attribute('href')

                    if not href or not title:
                        continue

                    # 상대 경로를 절대 경로로 변환
                    if href.startswith('/'):
                        url = f"https://d2.naver.com{href}"
                    else:
                        url = href

                    # URL 중복 체크
                    if url in seen_urls:
                        continue

                    # 요약(summary) 추출
                    summary_elem = article.query_selector('.post_txt')
                    summary = summary_elem.inner_text().strip() if summary_elem else ""

                    # 날짜 추출 (dl > dd 중 첫 번째)
                    date_elem = article.query_selector('dl dd')
                    date = date_elem.inner_text().strip() if date_elem else datetime.now().strftime('%Y.%m.%d')

                    posts.append({
                        'title': title,
                        'url': url,
                        'summary': summary,
                        'date': date
                    })
                    seen_urls.add(url)

                except Exception:
                    continue

            browser.close()

            print(f"  ✅ {len(posts)}개 글 파싱 완료")
            return posts[:10]  # 최신 10개

    except Exception as e:
        print(f"❌ 크롤링 실패: {e}")
        return []


# ============================================================================
# Notion API 호출
# ============================================================================

def query_notion_database(data_source_id):
    """Notion 데이터베이스 쿼리 (기존 URL 확인용)"""
    if not NOTION_API_TOKEN:
        return []
    
    url = f"https://api.notion.com/v1/databases/{data_source_id}/query"
    
    headers = {
        "Authorization": f"Bearer {NOTION_API_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    try:
        req = Request(url, headers=headers, method='POST')
        req.data = json.dumps({}).encode('utf-8')
        
        with urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('results', [])
    
    except Exception as e:
        print(f"⚠️  Notion 쿼리 실패: {e}")
        return []


def create_notion_page(title, url, data_source_id, summary="", date=""):
    """Notion 페이지 생성"""
    if not NOTION_API_TOKEN:
        print(f"⚠️  Notion API 토큰 없음 (시뮬레이션): {title}")
        return False

    api_url = "https://api.notion.com/v1/pages"

    headers = {
        "Authorization": f"Bearer {NOTION_API_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    payload = {
        "parent": {
            "type": "database_id",
            "database_id": data_source_id
        },
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            },
            "URL": {
                "url": url
            },
            "Tags": {
                "select": {
                    "name": "Articles"
                }
            }
        }
    }

    # Summary 추가 (있는 경우)
    if summary:
        payload["properties"]["Summary"] = {
            "rich_text": [
                {
                    "text": {
                        "content": summary[:2000]  # Notion 제한: 2000자
                    }
                }
            ]
        }

    # Published Date 추가 (있는 경우)
    if date:
        # 날짜 형식 변환: 2025.12.18 -> 2025-12-18
        formatted_date = date.replace('.', '-')
        payload["properties"]["Published Date"] = {
            "date": {
                "start": formatted_date
            }
        }
    
    try:
        req = Request(api_url, headers=headers, method='POST')
        req.data = json.dumps(payload).encode('utf-8')

        with urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            return True

    except Exception as e:
        print(f"❌ 페이지 생성 실패: {e}")
        # 상세 에러 정보 출력
        if hasattr(e, 'read'):
            error_body = e.read().decode('utf-8')
            print(f"   상세: {error_body}")
        return False


# ============================================================================
# 캐시 관리
# ============================================================================

def load_cache():
    """캐시 파일에서 이미 추가된 URL 목록 로드"""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f if line.strip())
    return set()


def save_to_cache(url):
    """URL을 캐시에 저장"""
    with open(CACHE_FILE, 'a', encoding='utf-8') as f:
        f.write(url + '\n')


# ============================================================================
# 메인 로직
# ============================================================================

def main():
    """메인 실행"""
    print("=" * 70)
    print("📰 네이버 D2 → Notion Weblinks 자동 추가")
    print(f"🕐 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 1. 캐시 로드
    cached_urls = load_cache()
    print(f"\n📦 캐시: {len(cached_urls)}개 URL")
    
    # 2. D2 블로그에서 글 가져오기
    print("\n🔍 D2 블로그 크롤링 중...")
    posts = fetch_d2_posts()
    
    if not posts:
        print("❌ 글을 가져오지 못했습니다.")
        return
    
    print(f"✅ {len(posts)}개의 글 발견")
    
    # 3. 새 글 필터링
    new_posts = [p for p in posts if p['url'] not in cached_urls]
    
    if not new_posts:
        print("\n✨ 새로운 글이 없습니다!")
        return
    
    print(f"\n🆕 {len(new_posts)}개의 새 글:")
    for i, post in enumerate(new_posts, 1):
        print(f"  {i}. {post['title']}")
        print(f"     📅 {post['date']}")
        print(f"     🔗 {post['url']}")
        if post.get('summary'):
            summary_preview = post['summary'][:100] + '...' if len(post['summary']) > 100 else post['summary']
            print(f"     📝 {summary_preview}")
        print()
    
    # 4. Notion에 추가
    print("\n📝 Notion에 추가 중...")
    added = 0
    
    for post in new_posts:
        if create_notion_page(
            post['title'],
            post['url'],
            WEBLINKS_DATA_SOURCE_ID,
            summary=post.get('summary', ''),
            date=post.get('date', '')
        ):
            save_to_cache(post['url'])
            added += 1
            print(f"  ✅ {post['title']}")
        else:
            print(f"  ❌ {post['title']}")

        time.sleep(0.3)  # Rate limit 고려
    
    # 5. 결과
    print("\n" + "=" * 70)
    print(f"✨ 완료! {added}/{len(new_posts)}개 추가됨")
    print("=" * 70)


if __name__ == "__main__":
    main()
