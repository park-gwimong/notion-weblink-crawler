# -*- coding: utf-8 -*-
"""
크롤러 모듈
각 블로그 사이트별 크롤러를 포함합니다.
"""

from .base import BaseCrawler, Post
from .d2 import D2Crawler, fetch_d2_posts
from .kakao import KakaoCrawler, fetch_kakao_tech_posts
from .toss import TossCrawler, fetch_toss_posts

# 등록된 모든 크롤러 클래스
CRAWLERS = [
    D2Crawler,
    KakaoCrawler,
    TossCrawler,
]

__all__ = [
    'BaseCrawler',
    'Post',
    'D2Crawler',
    'KakaoCrawler',
    'TossCrawler',
    'fetch_d2_posts',
    'fetch_kakao_tech_posts',
    'fetch_toss_posts',
    'CRAWLERS',
]
