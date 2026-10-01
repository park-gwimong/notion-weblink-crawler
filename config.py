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

# 제목에 이 단어가 들어간 글은 수집하지 않음 (대소문자 무시)
# 사내 문화·채용·행사 안내처럼 기술 학습과 거리가 먼 글을 거른다
EXCLUDE_TITLE_KEYWORDS = [
    "컬처", "culture",
    "네트워킹",
    "채용", "입사", "인턴",
    "밋업 후기", "행사 후기",
]
