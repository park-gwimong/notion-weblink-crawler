# -*- coding: utf-8 -*-
"""
캐시 관리 모듈
URL 중복 방지를 위한 캐시 처리
"""

import os
from config import CACHE_FILE


class URLCache:
    """URL 캐시 관리 클래스"""

    def __init__(self, cache_file: str = CACHE_FILE):
        self.cache_file = cache_file
        self._urls: set = set()
        self._loaded = False

    def load(self) -> set:
        """캐시 파일에서 URL 목록 로드"""
        if self._loaded:
            return self._urls

        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                self._urls = set(line.strip() for line in f if line.strip())
        else:
            self._urls = set()

        self._loaded = True
        return self._urls

    def contains(self, url: str) -> bool:
        """URL이 캐시에 있는지 확인"""
        if not self._loaded:
            self.load()
        return url in self._urls

    def add(self, url: str) -> None:
        """URL을 캐시에 추가"""
        if not self._loaded:
            self.load()

        if url not in self._urls:
            self._urls.add(url)
            with open(self.cache_file, 'a', encoding='utf-8') as f:
                f.write(url + '\n')

    def __len__(self) -> int:
        """캐시된 URL 개수"""
        if not self._loaded:
            self.load()
        return len(self._urls)

    def __contains__(self, url: str) -> bool:
        """in 연산자 지원"""
        return self.contains(url)


# 기본 캐시 인스턴스
cache = URLCache()
