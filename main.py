#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
from datetime import datetime

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from config import REQUEST_DELAY, EXCLUDE_TITLE_KEYWORDS
from cache import cache
from notion_client import notion
from crawlers import CRAWLERS


def crawl_all_blogs():
    """모든 블로그에서 글 크롤링. (글 목록, 실패한 블로그 이름 목록) 반환"""
    all_posts = []
    failed = []

    for CrawlerClass in CRAWLERS:
        crawler = CrawlerClass()
        print(f"\n🔍 {crawler.name} 블로그 크롤링 중...")

        posts = crawler.fetch()
        if posts:
            all_posts.extend(posts)
            print(f"✅ {crawler.name}: {len(posts)}개의 글 발견")
        else:
            failed.append(crawler.name)
            print(f"⚠️  {crawler.name} 블로그에서 글을 가져오지 못했습니다.")

    return all_posts, failed


def is_excluded(post):
    """제목에 제외 키워드가 있으면 True"""
    title = post.get('title', '').lower()
    return any(kw.lower() in title for kw in EXCLUDE_TITLE_KEYWORDS)


def filter_new_posts(posts):
    """캐시에 없는 새 글만 필터링"""
    return [p for p in posts if p['url'] not in cache]


def display_posts(posts):
    """포스트 목록 출력"""
    for i, post in enumerate(posts, 1):
        source_label = f"[{post.get('source', '?').upper()}]"
        print(f"  {i}. {source_label} {post['title']}")
        print(f"     📅 {post['date']}")
        print(f"     🔗 {post['url']}")
        if post.get('summary'):
            summary_preview = post['summary'][:100]
            if len(post['summary']) > 100:
                summary_preview += '...'
            print(f"     📝 {summary_preview}")
        print()


def add_to_notion(posts):
    """Notion에 포스트 추가"""
    added = 0

    for post in posts:
        source_label = f"[{post.get('source', '?').upper()}]"

        if notion.create_page(
            title=post['title'],
            url=post['url'],
            summary=post.get('summary', ''),
            date=post.get('date', ''),
        ):
            cache.add(post['url'])
            added += 1
            print(f"  ✅ {source_label} {post['title']}")
        else:
            print(f"  ❌ {source_label} {post['title']}")

        time.sleep(REQUEST_DELAY)

    return added


def main():
    """메인 실행"""
    print("=" * 70)
    print("📰 Tech Blog → Notion Weblinks 자동 추가")
    print(f"🕐 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # 1. 캐시 로드
    cache.load()
    print(f"\n📦 캐시: {len(cache)}개 URL")

    # 2. 모든 블로그에서 글 가져오기
    all_posts, failed = crawl_all_blogs()

    if not all_posts:
        print("\n❌ 어떤 블로그에서도 글을 가져오지 못했습니다.")
        return 1

    print(f"\n📊 총 {len(all_posts)}개의 글 발견")

    # 3. 새 글 필터링
    new_posts = filter_new_posts(all_posts)

    # 제외 키워드에 걸린 글은 캐시에만 넣어 다음 실행에서도 다시 보지 않게 한다
    excluded = [p for p in new_posts if is_excluded(p)]
    for post in excluded:
        cache.add(post['url'])
        print(f"  🚫 제외: {post['title']}")
    new_posts = [p for p in new_posts if not is_excluded(p)]

    if not new_posts:
        print("\n✨ 새로운 글이 없습니다!")
        return report_failures(failed)

    print(f"\n🆕 {len(new_posts)}개의 새 글:")
    display_posts(new_posts)

    # 4. Notion에 추가
    print("📝 Notion에 추가 중...")
    added = add_to_notion(new_posts)

    # 5. 결과
    print("\n" + "=" * 70)
    print(f"✨ 완료! {added}/{len(new_posts)}개 추가됨")
    print("=" * 70)

    if added < len(new_posts):
        print(f"\n❌ Notion 추가 실패 {len(new_posts) - added}건 (토큰·DB 연결 확인 필요)")
        return 1

    return report_failures(failed)


def report_failures(failed):
    """블로그 절반 이상이 실패하면 셀렉터 변경 등을 의심하고 실패 코드 반환"""
    if failed:
        print(f"\n⚠️  수집 실패 블로그: {', '.join(failed)}")
    if len(failed) * 2 >= len(CRAWLERS):
        print("❌ 절반 이상의 블로그 수집 실패")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
