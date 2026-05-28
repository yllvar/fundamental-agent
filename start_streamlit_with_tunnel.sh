#!/bin/bash

# Streamlit을 외부 접속 가능하도록 run
echo "🚀 Streamlit 서버를 시작합니다..."
echo "📡 외부 접속을 위해 0.0.0.0:8501에서 실행됩니다."

# 백그라운드에서 run
nohup streamlit run integrated_dashboard.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    > streamlit.log 2>&1 &

echo "✅ Streamlit 서버가 백그라운드에서 시작되었습니다."
echo "📋 로그 check: tail -f streamlit.log"
echo "🔗 SSH 터널링으로 접속하세요."
echo ""
echo "로컬 PC에서 다음 명령어 실행:"
echo "ssh -L 8501:localhost:8501 -i [키파일] ec2-user@[EC2-IP]"
echo ""
echo "그 후 브라우저에서 http://localhost:8501 접속"
