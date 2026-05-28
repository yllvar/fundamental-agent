#!/bin/bash
# AI 기사 생성 System 실행 스크립트

echo "🤖 AI 기사 생성 System 시작"
echo "=================================="

# 현재 Directory check
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Task Directory: $SCRIPT_DIR"

# 기존 Streamlit 프로세스 stop
echo "🔄 기존 프로세스 정리 중..."
pkill -f streamlit 2>/dev/null || true
sleep 2

# Python 환경 check
echo "🐍 Python 환경 check..."
python --version
pip list | grep streamlit || echo "⚠️ Streamlit이 설치되지 않았을 수 있습니다"

# 필요한 Directory 생성
echo "📁 필요한 Directory 생성..."
mkdir -p output
mkdir -p logs
mkdir -p streamlit_articles
mkdir -p output/charts
mkdir -p output/images

# 환경 변수 check
echo "🔑 환경 변수 check..."
if [ -z "$AWS_ACCESS_KEY_ID" ]; then
    echo "⚠️ AWS_ACCESS_KEY_ID가 설정되지 않았습니다"
fi

if [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "⚠️ AWS_SECRET_ACCESS_KEY가 설정되지 않았습니다"
fi

# Streamlit run
echo "🚀 Streamlit Dashboard starting..."
echo "브라우저에서 http://localhost:8501 접속"
echo "페이지 선택: 🤖 AI 기사 생성"
echo ""
echo "stopped"
echo "=================================="

# 백그라운드 run
nohup streamlit run streamlit_comprehensive_dashboard.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false \
    > streamlit_comprehensive.log 2>&1 &

STREAMLIT_PID=$!
echo "🎯 Streamlit PID: $STREAMLIT_PID"

# 실행 상태 check
sleep 5
if ps -p $STREAMLIT_PID > /dev/null; then
    echo "✅ Streamlit이 성공적으로 시작되었습니다"
    echo "📊 Dashboard: http://localhost:8501"
    echo "📝 로그 파일: streamlit_comprehensive.log"
    
    # 포트 check
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8501 | grep -q "200"; then
        echo "🌐 웹 서버 응답 정상"
    else
        echo "⚠️ 웹 서버 응답 대기 중..."
    fi
else
    echo "❌ Streamlit 시작 실패"
    echo "📝 로그 check:"
    tail -10 streamlit_comprehensive.log
    exit 1
fi

echo ""
echo "🎉 AI 기사 생성 System이 실행되었습니다!"
echo ""
echo "📋 사용법:"
echo "1. 브라우저에서 http://localhost:8501 접속"
echo "2. 사이드바에서 '🤖 AI 기사 생성' 선택"
echo "3. '🔄 5분 자동 새로고침' 체크 (선택사항)"
echo "4. '🚀 AI 기사 생성 시작' 버튼 클릭"
echo ""
echo "🔧 관리 명령어:"
echo "- 상태 check: ./check_status.sh"
echo "- System stop: ./stop_system.sh"
echo "- 로그 check: tail -f streamlit_comprehensive.log"
