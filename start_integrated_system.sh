#!/bin/bash

# 통합 Economic News System 시작 스크립트

echo "🤖 Economic News 통합 System 시작"
echo "=================================="

# Project Directory로 이동
cd "$(dirname "$0")"

# Virtual environment activated (있는 경우)
if [ -d "venv" ]; then
    echo "📦 Virtual environment activated 중..."
    source venv/bin/activate
fi

# 환경 변수 Load
if [ -f ".env" ]; then
    echo "⚙️  환경 변수 Load 중..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  .env 파일이 not found. 환경 변수를 check하세요."
fi

# Python 경로 setup
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 통합 Dashboard run
echo "🚀 통합 Dashboard 실행 중..."
echo "📱 브라우저에서 http://localhost:8501 로 접속하세요"
echo "⏹️  stopped"
echo "=================================="

python3 run_integrated_dashboard.py
