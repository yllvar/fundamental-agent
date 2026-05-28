#!/bin/bash
# AI 기사 생성 System 상태 check 스크립트

echo "🔍 AI 기사 생성 System 상태 check"
echo "=================================="

# Streamlit 프로세스 check
echo "📊 Streamlit 프로세스 상태:"
STREAMLIT_PROCESSES=$(ps aux | grep streamlit | grep -v grep)
if [ -n "$STREAMLIT_PROCESSES" ]; then
    echo "✅ Streamlit 실행 중"
    echo "$STREAMLIT_PROCESSES"
    
    # PID 추출
    STREAMLIT_PID=$(ps aux | grep streamlit | grep -v grep | awk '{print $2}' | head -1)
    echo "🎯 PID: $STREAMLIT_PID"
    
    # 메모리 사용량
    MEMORY_USAGE=$(ps -p $STREAMLIT_PID -o %mem --no-headers 2>/dev/null)
    if [ -n "$MEMORY_USAGE" ]; then
        echo "💾 메모리 사용량: ${MEMORY_USAGE}%"
    fi
    
    # CPU 사용량
    CPU_USAGE=$(ps -p $STREAMLIT_PID -o %cpu --no-headers 2>/dev/null)
    if [ -n "$CPU_USAGE" ]; then
        echo "⚡ CPU 사용량: ${CPU_USAGE}%"
    fi
else
    echo "❌ Streamlit이 실행되지 않고 있습니다"
fi

echo ""

# 포트 상태 check
echo "🌐 포트 8501 상태:"
if lsof -i :8501 >/dev/null 2>&1; then
    echo "✅ 포트 8501 사용 중"
    lsof -i :8501
else
    echo "❌ 포트 8501이 사용되지 않고 있습니다"
fi

echo ""

# 웹 서버 응답 check
echo "🔗 웹 서버 응답 check:"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501 2>/dev/null)
if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ 웹 서버 정상 응답 (HTTP $HTTP_STATUS)"
    echo "📊 Dashboard: http://localhost:8501"
else
    echo "❌ 웹 서버 응답 없음 (HTTP $HTTP_STATUS)"
fi

echo ""

# 로그 파일 check
echo "📝 로그 파일 상태:"
if [ -f "streamlit_comprehensive.log" ]; then
    LOG_SIZE=$(du -h streamlit_comprehensive.log | cut -f1)
    LOG_LINES=$(wc -l < streamlit_comprehensive.log)
    echo "✅ 로그 파일 존재: streamlit_comprehensive.log"
    echo "📏 파일 크기: $LOG_SIZE"
    echo "📄 라인 수: $LOG_LINES"
    
    echo ""
    echo "📋 최근 로그 (마지막 5줄):"
    echo "------------------------"
    tail -5 streamlit_comprehensive.log
else
    echo "❌ 로그 파일이 not found"
fi

echo ""

# 디스크 사용량 check
echo "💽 디스크 사용량:"
echo "출력 Directory:"
if [ -d "output" ]; then
    du -sh output/ 2>/dev/null || echo "output/ Directory check 불가"
else
    echo "❌ output/ Directory가 not found"
fi

echo "로그 Directory:"
if [ -d "logs" ]; then
    du -sh logs/ 2>/dev/null || echo "logs/ Directory check 불가"
else
    echo "❌ logs/ Directory가 not found"
fi

echo ""

# Python 환경 check
echo "🐍 Python 환경:"
python --version
echo "주요 Package 버전:"
pip list | grep -E "(streamlit|pandas|plotly|yfinance|boto3)" 2>/dev/null || echo "Package 정보 check 불가"

echo ""

# AWS 자격 증명 check
echo "🔑 AWS 자격 증명:"
if [ -n "$AWS_ACCESS_KEY_ID" ]; then
    echo "✅ AWS_ACCESS_KEY_ID 설정됨"
else
    echo "❌ AWS_ACCESS_KEY_ID 미설정"
fi

if [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "✅ AWS_SECRET_ACCESS_KEY 설정됨"
else
    echo "❌ AWS_SECRET_ACCESS_KEY 미설정"
fi

if [ -n "$AWS_DEFAULT_REGION" ]; then
    echo "✅ AWS_DEFAULT_REGION: $AWS_DEFAULT_REGION"
else
    echo "⚠️ AWS_DEFAULT_REGION 미설정 (기본값 사용)"
fi

echo ""
echo "=================================="

# 전체 상태 요약
if [ -n "$STREAMLIT_PROCESSES" ] && [ "$HTTP_STATUS" = "200" ]; then
    echo "🎉 System 상태: 정상 작동"
    echo "📊 Dashboard 접속: http://localhost:8501"
    echo "🤖 AI 기사 생성 페이지로 이동하여 사용하세요"
else
    echo "⚠️ System 상태: 문제 발생"
    echo "🔧 해결 방법:"
    echo "1. ./run_ai_article_system.sh 실행"
    echo "2. 로그 check: tail -f streamlit_comprehensive.log"
    echo "3. System 재시작: ./stop_system.sh && ./run_ai_article_system.sh"
fi
