# -*- coding: utf-8 -*-

from .base import BaseCrawler, Post
from .d2 import D2Crawler, fetch_d2_posts
from .kakao import KakaoCrawler, fetch_kakao_tech_posts
from .toss import TossCrawler, fetch_toss_posts
from .daangn import DaangnCrawler, fetch_daangn_posts
from .gccompany import GCCompanyCrawler, fetch_gccompany_posts
from .wanted import WantedCrawler, fetch_wanted_posts
from .coupang import CoupangCrawler, fetch_coupang_posts
from .ridi import RidiCrawler, fetch_ridi_posts

# 등록된 모든 크롤러 클래스
CRAWLERS = [
    D2Crawler,
    KakaoCrawler,
    TossCrawler,
    DaangnCrawler,
    GCCompanyCrawler,
    WantedCrawler,
    CoupangCrawler,
    RidiCrawler,
]

__all__ = [
    'BaseCrawler',
    'Post',
    'D2Crawler',
    'KakaoCrawler',
    'TossCrawler',
    'DaangnCrawler',
    'GCCompanyCrawler',
    'WantedCrawler',
    'CoupangCrawler',
    'RidiCrawler',
    'fetch_d2_posts',
    'fetch_kakao_tech_posts',
    'fetch_toss_posts',
    'fetch_daangn_posts',
    'fetch_gccompany_posts',
    'fetch_wanted_posts',
    'fetch_coupang_posts',
    'fetch_ridi_posts',
    'CRAWLERS',
]
