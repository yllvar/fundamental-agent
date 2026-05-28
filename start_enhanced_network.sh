#!/bin/bash

echo "🚀 개선된 Economic 네트워크 분석 Dashboard 시작"
echo "============================================"

# 현재 Directory로 이동
cd "$(dirname "$0")"

# Virtual environment activated (있는 경우)
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated됨"
fi

# 필요한 Package check 및 설치
echo "📦 필요한 Package check 중..."
pip install -q streamlit plotly networkx textblob pandas numpy

# Streamlit run
echo "🌐 Streamlit Dashboard 실행 중..."
echo "📍 URL: http://localhost:8501"
echo "🔧 stopped"
echo ""

streamlit run run_enhanced_network_dashboard.py --server.port 8501 --server.address 0.0.0.0
