#!/bin/bash
# 네이버 D2 → Notion 크롤러 빠른 설치 스크립트

set -e

echo "=========================================="
echo "네이버 D2 → Notion 크롤러 설치"
echo "=========================================="
echo ""

# 1. Python 확인
echo "1️⃣  Python 버전 확인..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3가 설치되어 있지 않습니다."
    echo "   설치 방법: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ $PYTHON_VERSION"
echo ""

# 2. Notion API Token 입력
echo "2️⃣  Notion Integration Token 입력"
echo "   (https://www.notion.so/my-integrations 에서 생성)"
read -p "Token: " NOTION_TOKEN

if [ -z "$NOTION_TOKEN" ]; then
    echo "❌ Token이 입력되지 않았습니다."
    exit 1
fi

# 환경 변수로 저장
export NOTION_API_KEY="$NOTION_TOKEN"
echo "export NOTION_API_KEY='$NOTION_TOKEN'" >> ~/.bashrc
echo "✅ Token 저장됨"
echo ""

# 3. 테스트 실행
echo "3️⃣  테스트 실행..."
python3 d2_to_notion_complete.py

echo ""
echo "=========================================="
echo "✅ 설치 완료!"
echo "=========================================="
echo ""
echo "다음 단계:"
echo "  1. Weblinks DB에 Integration 연결 확인"
echo "  2. cron으로 자동 실행 설정:"
echo "     crontab -e"
echo "     0 9 * * * cd $(pwd) && python3 d2_to_notion_complete.py"
echo ""
