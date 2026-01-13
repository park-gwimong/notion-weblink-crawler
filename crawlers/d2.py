# -*- coding: utf-8 -*-
"""
네이버 D2 블로그 크롤러
https://d2.naver.com/helloworld
"""

from typing import List
from playwright.sync_api import Page

from .base import BaseCrawler, Post


class D2Crawler(BaseCrawler):
    """네이버 D2 블로그 크롤러"""

    name = "D2"
    source_id = "d2"
    base_url = "https://d2.naver.com/helloworld"

    def parse_posts(self, page: Page) -> List[Post]:
        """D2 블로그 포스트 파싱"""
        posts = []
        seen_urls = set()

        # JavaScript 렌더링 대기
        page.wait_for_selector('.cont_post', timeout=self.timeout)

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

                url = self._make_absolute_url(href)

                # URL 중복 체크
                if url in seen_urls:
                    continue

                # 요약(summary) 추출
                summary_elem = article.query_selector('.post_txt')
                summary = summary_elem.inner_text().strip() if summary_elem else ""

                # 날짜 추출 (dl > dd 중 첫 번째)
                date_elem = article.query_selector('dl dd')
                date = date_elem.inner_text().strip() if date_elem else ""

                posts.append(Post(
                    title=title,
                    url=url,
                    summary=summary,
                    date=date,
                    source=self.source_id,
                ))
                seen_urls.add(url)

            except Exception:
                continue

        return posts


# 편의를 위한 함수형 인터페이스
def fetch_d2_posts():
    """D2 블로그에서 최신 글 가져오기"""
    crawler = D2Crawler()
    return crawler.fetch()
