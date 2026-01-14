# -*- coding: utf-8 -*-
"""
RIDI tech blog crawler
https://ridicorp.com/story-category/tech-blog/
"""

from typing import List
from playwright.sync_api import Page

from .base import BaseCrawler, Post


class RidiCrawler(BaseCrawler):
    """RIDI tech blog crawler."""

    name = "RIDI"
    source_id = "ridi"
    base_url = "https://ridicorp.com/story-category/tech-blog/"

    def parse_posts(self, page: Page) -> List[Post]:
        """Parse posts from RIDI story category page."""
        posts = []
        seen_urls = set()

        page.wait_for_selector('.entry-meta', timeout=self.timeout)

        articles = page.query_selector_all('article')
        if not articles:
            articles = page.query_selector_all('.entry-meta')

        for article in articles:
            try:
                container = article
                if hasattr(article, "query_selector"):
                    meta = article.query_selector('.entry-meta')
                    if meta:
                        container = meta

                link = None
                if hasattr(container, "query_selector"):
                    link = container.query_selector('.entry-title a')
                    if not link:
                        link = container.query_selector('a[href*="/story/"]')
                if not link:
                    continue

                href = link.get_attribute('href')
                if not href:
                    continue

                url = self._make_absolute_url(href)
                if url in seen_urls:
                    continue

                title = self._extract_title(container, link)
                if not title or len(title) < 3:
                    continue

                summary = self._extract_summary(container, link)
                date = self._extract_date(container, link)

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

    def _extract_title(self, article, link) -> str:
        """Extract title from the entry meta."""
        candidates = [
            '.entry-title', 'h2', 'h3', '.story-card__title', '.story-item__title',
            '.card__title', '.title', '[class*="title"]',
        ]
        for selector in candidates:
            elem = article.query_selector(selector) if hasattr(article, "query_selector") else None
            if elem:
                text = elem.inner_text().strip()
                if text:
                    return text

        if hasattr(link, "inner_text"):
            text = link.inner_text().strip()
            if text:
                return text.split('\n')[0].strip()

        return ""

    def _extract_summary(self, article, link) -> str:
        """Extract summary if available."""
        candidates = [
            '.entry-summary', 'p', '.story-card__desc', '.story-item__desc',
            '.card__desc', '.summary', '[class*="desc"]',
        ]
        for selector in candidates:
            elem = article.query_selector(selector) if hasattr(article, "query_selector") else None
            if elem:
                text = elem.inner_text().strip()
                if text and len(text) > 10:
                    return text
        return ""

    def _extract_date(self, article, link) -> str:
        """Extract date text if available."""
        candidates = [
            '.entry-date', 'time', '.date', '.post-date', '[class*="date"]',
        ]
        for selector in candidates:
            elem = article.query_selector(selector) if hasattr(article, "query_selector") else None
            if elem:
                text = elem.inner_text().strip()
                if text:
                    return text
        return ""


def fetch_ridi_posts():
    """Fetch latest posts from RIDI tech blog."""
    crawler = RidiCrawler()
    return crawler.fetch()
