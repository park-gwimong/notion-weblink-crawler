# -*- coding: utf-8 -*-
"""
Coupang tech blog crawler (RSS-based)
https://medium.com/@coupang-engineering-kr
"""

import re
from datetime import datetime
from typing import List, Dict, Any
from html import unescape

import feedparser

from .base import BaseCrawler, Post


class CoupangCrawler(BaseCrawler):
    """Coupang tech blog crawler (RSS feed)."""

    name = "Coupang"
    source_id = "coupang"
    base_url = "https://medium.com/@coupang-engineering-kr"
    feed_url = "https://medium.com/feed/@coupang-engineering-kr"

    def fetch(self) -> List[Dict[str, Any]]:
        """Fetch latest posts from RSS feed."""
        try:
            print(f"  {self.name} RSS feed loading...")
            feed = feedparser.parse(self.feed_url)

            if feed.bozo and not feed.entries:
                print(f"ERROR {self.name} RSS parsing failed: {feed.bozo_exception}")
                return []

            posts = []
            for entry in feed.entries[:self.max_posts]:
                post = self._parse_entry(entry)
                if post:
                    posts.append(post.to_dict())

            print(f"  Parsed {len(posts)} posts")
            return posts

        except Exception as e:
            print(f"ERROR {self.name} crawler failed: {e}")
            return []

    def _parse_entry(self, entry) -> Post:
        """Build Post from a feed entry."""
        title = entry.get('title', '').strip()
        url = entry.get('link', '').strip()

        if not title or not url:
            return None

        summary = self._extract_summary(entry)
        date = self._parse_date(entry)

        return Post(
            title=title,
            url=url,
            summary=summary,
            date=date,
            source=self.source_id,
        )

    def _extract_summary(self, entry) -> str:
        """Extract clean summary text from the feed entry."""
        raw = entry.get('summary', '') or entry.get('description', '')

        text = re.sub(r'<[^>]+>', '', raw)
        text = unescape(text)
        text = re.sub(r'\s+', ' ', text).strip()

        if len(text) > 500:
            text = text[:497] + '...'

        return text

    def _parse_date(self, entry) -> str:
        """Parse date as YYYY.MM.DD."""
        time_struct = entry.get('published_parsed') or entry.get('updated_parsed')

        if time_struct:
            try:
                dt = datetime(*time_struct[:6])
                return dt.strftime('%Y.%m.%d')
            except Exception:
                pass

        date_str = entry.get('published', '') or entry.get('updated', '')
        if date_str:
            try:
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(date_str)
                return dt.strftime('%Y.%m.%d')
            except Exception:
                pass

        return datetime.now().strftime('%Y.%m.%d')

    def parse_posts(self, page) -> List[Post]:
        """Not used for RSS-based crawler."""
        return []


def fetch_coupang_posts():
    """Fetch latest posts from Coupang tech blog."""
    crawler = CoupangCrawler()
    return crawler.fetch()

