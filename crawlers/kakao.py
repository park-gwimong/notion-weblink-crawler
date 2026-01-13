# -*- coding: utf-8 -*-
"""
카카오 테크 블로그 크롤러
https://tech.kakao.com/blog
"""

import re
from typing import List
from playwright.sync_api import Page

from .base import BaseCrawler, Post


class KakaoCrawler(BaseCrawler):
    """카카오 테크 블로그 크롤러"""

    name = "카카오"
    source_id = "kakao"
    base_url = "https://tech.kakao.com/blog"

    def parse_posts(self, page: Page) -> List[Post]:
        """카카오 테크 블로그 포스트 파싱"""
        posts = []
        seen_urls = set()

        # JavaScript 렌더링 대기 - 글 카드가 로드될 때까지
        page.wait_for_selector('.link_post', timeout=self.timeout)

        # 블로그 글 카드 선택
        post_cards = page.query_selector_all('.link_post')

        for card in post_cards:
            try:
                href = card.get_attribute('href')
                if not href:
                    continue

                url = self._make_absolute_url(href)

                # URL 중복 체크
                if url in seen_urls:
                    continue

                # 제목 추출 (.tit_post)
                title = self._extract_title(card)
                if not title or len(title) < 3:
                    continue

                # 요약 추출 (.desc_post)
                summary = self._extract_summary(card)

                # 날짜 추출 (.txt_date)
                date = self._extract_date(card)

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

    def _extract_title(self, card) -> str:
        """카드에서 제목 추출"""
        title_elem = card.query_selector('.tit_post')
        if title_elem:
            return title_elem.inner_text().strip()
        return ""

    def _extract_summary(self, card) -> str:
        """카드에서 요약 추출"""
        summary_elem = card.query_selector('.desc_post')
        if summary_elem:
            return summary_elem.inner_text().strip()
        return ""

    def _extract_date(self, card) -> str:
        """카드에서 날짜 추출"""
        date_elem = card.query_selector('.txt_date')
        if date_elem:
            date_text = date_elem.inner_text().strip()
            # YYYY.MM.DD 형식 찾기
            date_match = re.search(r'(\d{4}[.\-/]\d{2}[.\-/]\d{2})', date_text)
            if date_match:
                return date_match.group(1).replace('-', '.').replace('/', '.')
        return ""


# 편의를 위한 함수형 인터페이스
def fetch_kakao_tech_posts():
    """카카오 테크 블로그에서 최신 글 가져오기"""
    crawler = KakaoCrawler()
    return crawler.fetch()
