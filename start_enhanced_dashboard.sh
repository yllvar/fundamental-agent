#!/bin/bash
# 강화된 Dashboard 시작 스크립트 (실제 FRED 데이터 포함)

echo "🚀 강화된 Economic 모니터링 Dashboard 시작"
echo "=" * 50

# Project Directory로 이동
cd /home/ec2-user/projects/ABP/fundamental_agent

# Virtual environment activated
source /home/ec2-user/dl_env/bin/activate

# 환경변수 setup
export ALPHA_VANTAGE_API_KEY=9TLAUWS4L3099YK3
export FRED_API_KEY=d4235fa1b67058fff90f8a9cc43793c8

echo "🔑 API 키 설정 complete"
echo "  Alpha Vantage: ${ALPHA_VANTAGE_API_KEY:0:8}..."
echo "  FRED: ${FRED_API_KEY:0:8}..."
echo ""

echo "📊 데이터 소스:"
echo "  ✅ Alpha Vantage Intelligence API"
echo "  ✅ FRED Economic 데이터 (실제 API)"
echo "  ✅ 강화된 News & SNS 모니터링"
echo ""

echo "🌐 Dashboard 시작 중..."
echo "접근 URL: http://localhost:8501"
echo ""
echo "⚠️ SSH 터널링이 설정되어 있는지 check하세요!"
echo "🛑 stopped"
echo ""

# 강화된 Dashboard run
streamlit run streamlit_enhanced_dashboard.py --server.address localhost --server.port 8501
