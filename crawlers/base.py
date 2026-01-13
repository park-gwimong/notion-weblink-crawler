# -*- coding: utf-8 -*-
"""
크롤러 베이스 클래스
모든 크롤러가 상속받는 추상 클래스
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any
from playwright.sync_api import sync_playwright, Page

import sys
sys.path.insert(0, '..')
from config import MAX_POSTS_PER_SOURCE, PLAYWRIGHT_TIMEOUT


class Post:
    """블로그 포스트 데이터 클래스"""

    def __init__(self, title: str, url: str, summary: str = "",
                 date: str = "", source: str = ""):
        self.title = title
        self.url = url
        self.summary = summary
        self.date = date or datetime.now().strftime('%Y.%m.%d')
        self.source = source

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'title': self.title,
            'url': self.url,
            'summary': self.summary,
            'date': self.date,
            'source': self.source,
        }


class BaseCrawler(ABC):
    """크롤러 베이스 클래스"""

    # 서브클래스에서 정의해야 할 속성
    name: str = ""           # 크롤러 이름 (예: "D2", "카카오")
    source_id: str = ""      # 소스 ID (예: "d2", "kakao")
    base_url: str = ""       # 블로그 기본 URL

    def __init__(self):
        self.max_posts = MAX_POSTS_PER_SOURCE
        self.timeout = PLAYWRIGHT_TIMEOUT

    @abstractmethod
    def parse_posts(self, page: Page) -> List[Post]:
        """
        페이지에서 포스트 목록 파싱 (서브클래스에서 구현)

        Args:
            page: Playwright 페이지 객체

        Returns:
            Post 객체 리스트
        """
        pass

    def fetch(self) -> List[Dict[str, Any]]:
        """블로그에서 최신 글 가져오기"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                print(f"  🌐 {self.name} 페이지 로딩 중...")
                page.goto(self.base_url, wait_until="networkidle")

                posts = self.parse_posts(page)
                browser.close()

                print(f"  ✅ {len(posts)}개 글 파싱 완료")
                return [post.to_dict() for post in posts[:self.max_posts]]

        except Exception as e:
            print(f"❌ {self.name} 크롤링 실패: {e}")
            return []

    def _make_absolute_url(self, href: str) -> str:
        """상대 경로를 절대 경로로 변환"""
        if href.startswith('http'):
            return href
        if href.startswith('/'):
            # base_url에서 도메인 추출
            from urllib.parse import urlparse
            parsed = urlparse(self.base_url)
            return f"{parsed.scheme}://{parsed.netloc}{href}"
        return href
