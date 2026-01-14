# -*- coding: utf-8 -*-

import re
from datetime import datetime
from typing import List, Dict, Any
from html import unescape

import feedparser

from .base import BaseCrawler, Post


class DaangnCrawler(BaseCrawler):
    """당근마켓 기술 블로그 크롤러 (RSS 피드)"""

    name = "당근"
    source_id = "daangn"
    base_url = "https://medium.com/daangn"
    feed_url = "https://medium.com/feed/daangn"

    def fetch(self) -> List[Dict[str, Any]]:
        """RSS 피드에서 최신 글 가져오기"""
        try:
            print(f"  🌐 {self.name} RSS 피드 로딩 중...")
            feed = feedparser.parse(self.feed_url)

            if feed.bozo and not feed.entries:
                print(f"❌ {self.name} RSS 파싱 실패: {feed.bozo_exception}")
                return []

            posts = []
            for entry in feed.entries[:self.max_posts]:
                post = self._parse_entry(entry)
                if post:
                    posts.append(post.to_dict())

            print(f"  ✅ {len(posts)}개 글 파싱 완료")
            return posts

        except Exception as e:
            print(f"❌ {self.name} 크롤링 실패: {e}")
            return []

    def _parse_entry(self, entry) -> Post:
        """RSS 엔트리에서 Post 객체 생성"""
        title = entry.get('title', '').strip()
        url = entry.get('link', '').strip()

        if not title or not url:
            return None

        # 요약 추출 (HTML 태그 제거)
        summary = self._extract_summary(entry)

        # 날짜 파싱
        date = self._parse_date(entry)

        return Post(
            title=title,
            url=url,
            summary=summary,
            date=date,
            source=self.source_id,
        )

    def _extract_summary(self, entry) -> str:
        """RSS 엔트리에서 요약 추출"""
        # summary 또는 description 필드 사용
        raw = entry.get('summary', '') or entry.get('description', '')

        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', raw)
        # HTML 엔티티 디코딩
        text = unescape(text)
        # 연속 공백 정리
        text = re.sub(r'\s+', ' ', text).strip()

        # 최대 500자로 제한
        if len(text) > 500:
            text = text[:497] + '...'

        return text

    def _parse_date(self, entry) -> str:
        """RSS 엔트리에서 날짜 파싱 (YYYY.MM.DD 형식)"""
        # published_parsed 또는 updated_parsed 사용
        time_struct = entry.get('published_parsed') or entry.get('updated_parsed')

        if time_struct:
            try:
                dt = datetime(*time_struct[:6])
                return dt.strftime('%Y.%m.%d')
            except Exception:
                pass

        # 문자열에서 파싱 시도
        date_str = entry.get('published', '') or entry.get('updated', '')
        if date_str:
            # RFC 2822 형식 파싱 시도
            try:
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(date_str)
                return dt.strftime('%Y.%m.%d')
            except Exception:
                pass

        return datetime.now().strftime('%Y.%m.%d')

    def parse_posts(self, page) -> List[Post]:
        """RSS 기반이므로 사용하지 않음 (추상 메서드 구현)"""
        return []


# 편의를 위한 함수형 인터페이스
def fetch_daangn_posts():
    """당근마켓 기술 블로그에서 최신 글 가져오기"""
    crawler = DaangnCrawler()
    return crawler.fetch()
