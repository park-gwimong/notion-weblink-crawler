# -*- coding: utf-8 -*-
"""
Notion API 클라이언트 모듈
Notion 데이터베이스와의 통신 처리
"""

import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from typing import Optional, Dict, Any, List

from config import (
    NOTION_API_TOKEN,
    NOTION_API_VERSION,
    WEBLINKS_DATABASE_ID,
    DEFAULT_TAG,
)


class NotionClient:
    """Notion API 클라이언트"""

    BASE_URL = "https://api.notion.com/v1"

    def __init__(self, token: str = NOTION_API_TOKEN):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json",
        }

    def is_configured(self) -> bool:
        """API 토큰이 설정되어 있는지 확인"""
        return bool(self.token)

    def _request(self, endpoint: str, method: str = 'GET',
                 data: Optional[Dict] = None) -> Optional[Dict]:
        """API 요청 수행"""
        url = f"{self.BASE_URL}{endpoint}"

        try:
            req = Request(url, headers=self.headers, method=method)
            if data:
                req.data = json.dumps(data).encode('utf-8')

            with urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))

        except HTTPError as e:
            error_body = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
            print(f"❌ Notion API 오류: {e.code} - {error_body}")
            return None
        except Exception as e:
            print(f"❌ 요청 실패: {e}")
            return None

    def query_database(self, database_id: str = WEBLINKS_DATABASE_ID,
                       filter_: Optional[Dict] = None) -> List[Dict]:
        """데이터베이스 쿼리"""
        if not self.is_configured():
            return []

        data = {}
        if filter_:
            data['filter'] = filter_

        result = self._request(f"/databases/{database_id}/query", 'POST', data)
        return result.get('results', []) if result else []

    def create_page(self, title: str, url: str,
                    database_id: str = WEBLINKS_DATABASE_ID,
                    summary: str = "", date: str = "",
                    tag: str = DEFAULT_TAG) -> bool:
        """Notion 페이지 생성"""
        if not self.is_configured():
            print(f"⚠️  Notion API 토큰 없음 (시뮬레이션): {title}")
            return False

        payload = self._build_page_payload(
            database_id=database_id,
            title=title,
            url=url,
            summary=summary,
            date=date,
            tag=tag,
        )

        result = self._request("/pages", 'POST', payload)
        return result is not None

    def _build_page_payload(self, database_id: str, title: str, url: str,
                            summary: str, date: str, tag: str) -> Dict[str, Any]:
        """페이지 생성 페이로드 구성"""
        payload = {
            "parent": {
                "type": "database_id",
                "database_id": database_id,
            },
            "properties": {
                "Name": {
                    "title": [{"text": {"content": title}}]
                },
                "URL": {
                    "url": url
                },
                "Tags": {
                    "select": {"name": tag}
                },
            },
        }

        # Summary 추가
        if summary:
            payload["properties"]["Summary"] = {
                "rich_text": [{"text": {"content": summary[:2000]}}]
            }

        # Published Date 추가
        if date:
            formatted_date = date.replace('.', '-')
            payload["properties"]["Published Date"] = {
                "date": {"start": formatted_date}
            }

        return payload


# 기본 클라이언트 인스턴스
notion = NotionClient()
