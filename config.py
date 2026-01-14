# -*- coding: utf-8 -*-

import os

# Notion API 설정
NOTION_API_TOKEN = os.getenv('NOTION_API_KEY', '')
NOTION_API_VERSION = "2022-06-28"
WEBLINKS_DATABASE_ID = "89728ea5-acb0-423c-b047-14ef6ce4ca83"

# 캐시 설정
CACHE_FILE = "notion_urls_cache.txt"

# 크롤링 설정
MAX_POSTS_PER_SOURCE = 10  # 각 블로그당 최대 가져올 글 수
REQUEST_DELAY = 0.3  # Notion API 호출 간 딜레이 (초)
PLAYWRIGHT_TIMEOUT = 15000  # Playwright 타임아웃 (ms)

# Notion 기본 태그
DEFAULT_TAG = "Articles"
