#!/bin/bash

echo "🔄 Streamlit 안전 재시작"
echo "========================"

# 1. 기존 프로세스 정리
echo "1. 기존 Streamlit 프로세스 정리 중..."
pkill -f streamlit
sleep 3

# 2. 포트 check
echo "2. 포트 8501 상태 check 중..."
if netstat -tlnp | grep -q 8501; then
    echo "⚠️  포트 8501이 여전히 사용 중입니다."
    echo "   다른 포트(8502)를 사용합니다."
    PORT=8502
else
    echo "✅ 포트 8501 사용 가능"
    PORT=8501
fi

# 3. 환경 setup
echo "3. 환경 설정 중..."
source ~/dl_env/bin/activate
cd /home/ec2-user/projects/ABP/fundamental_agent

# 4. 환경 변수 Load
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# 5. Python 경로 setup
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 6. Streamlit run
echo "4. Streamlit 실행 중... (포트: $PORT)"
echo "📱 브라우저에서 http://localhost:$PORT 로 접속하세요"
echo "⏹️  stopped"
echo "========================"

streamlit run integrated_dashboard.py --server.address=0.0.0.0 --server.port=$PORT
