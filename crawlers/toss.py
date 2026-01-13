# -*- coding: utf-8 -*-
"""
토스 테크 블로그 크롤러
https://toss.tech/category/engineering
"""

from typing import List
from playwright.sync_api import Page

from .base import BaseCrawler, Post


class TossCrawler(BaseCrawler):
    """토스 테크 블로그 크롤러"""

    name = "토스"
    source_id = "toss"
    base_url = "https://toss.tech/category/engineering"

    def parse_posts(self, page: Page) -> List[Post]:
        """토스 테크 블로그 포스트 파싱"""
        posts = []
        seen_urls = set()

        # JavaScript 렌더링 대기 - 글 카드가 로드될 때까지
        page.wait_for_selector('a[href^="/article/"]', timeout=self.timeout)

        # 블로그 글 링크 선택
        post_links = page.query_selector_all('a[href^="/article/"]')

        for link in post_links:
            try:
                href = link.get_attribute('href')
                if not href or '/article/' not in href:
                    continue

                url = self._make_absolute_url(href)

                # URL 중복 체크
                if url in seen_urls:
                    continue

                # 제목, 요약 한 번에 추출
                title, summary = self._parse_content(link)
                if not title or len(title) < 3:
                    continue

                posts.append(Post(
                    title=title,
                    url=url,
                    summary=summary,
                    date='',  # 토스 블로그는 날짜 정보 없음
                    source=self.source_id,
                ))
                seen_urls.add(url)

            except Exception:
                continue

        return posts

    def _parse_content(self, link) -> tuple:
        """링크에서 제목과 요약을 한 번에 추출"""
        text = link.inner_text().strip()
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # 토스 블로그 구조: [카테고리?, 기타?, 제목, 요약, ...]
        # 최소 4줄 이상일 때 인덱스 2, 3 사용
        if len(lines) >= 4:
            title = lines[2]
            summary = lines[3]
        elif len(lines) >= 2:
            title = lines[0]
            summary = lines[1]
        elif len(lines) == 1:
            title = lines[0]
            summary = ''
        else:
            title = ''
            summary = ''

        return title, summary


# 편의를 위한 함수형 인터페이스
def fetch_toss_posts():
    """토스 테크 블로그에서 최신 글 가져오기"""
    crawler = TossCrawler()
    return crawler.fetch()
