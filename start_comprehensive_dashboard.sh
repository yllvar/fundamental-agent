#!/bin/bash
# 종합 Economic 모니터링 Dashboard 시작 스크립트

echo "🚀 종합 Economic 모니터링 Dashboard 시작"
echo "=" * 60

# Project Directory로 이동
cd /home/ec2-user/projects/ABP/fundamental_agent

# Virtual environment activated
source /home/ec2-user/dl_env/bin/activate

# 모든 환경변수 setup
export ALPHA_VANTAGE_API_KEY=9TLAUWS4L3099YK3
export FRED_API_KEY=d4235fa1b67058fff90f8a9cc43793c8
export REDDIT_CLIENT_ID=aW9qAFC_YjMGyplGut0b4Q
export REDDIT_CLIENT_SECRET=SNGZlfVrbfp1ucCkFltxiNBMCUtS3w
export REDDIT_USER_AGENT=EconomicNewsBot/1.0

echo "🔑 모든 API 키 설정 complete"
echo "  Alpha Vantage: ${ALPHA_VANTAGE_API_KEY:0:8}..."
echo "  FRED: ${FRED_API_KEY:0:8}..."
echo "  Reddit: ${REDDIT_CLIENT_ID:0:8}..."
echo ""

echo "📊 통합 데이터 소스:"
echo "  ✅ Alpha Vantage Intelligence API (시장 상태, 상위 변동 종목)"
echo "  ✅ FRED Economic 데이터 (29개 실제 Economic 지표)"
echo "  ✅ News RSS 피드 (14개 주요 매체)"
echo "  ✅ Reddit API (5개 Economic 서브레딧)"
echo ""

echo "🎯 Dashboard 기능:"
echo "  📊 멀티페이지 네비게이션"
echo "  🔗 모든 데이터에 클릭 가능한 링크"
echo "  📈 인터랙티브 차트 및 분석"
echo "  🔍 상세 데이터 탐색"
echo "  📱 실시간 소셜미디어 분석"
echo ""

echo "🌐 종합 Dashboard 시작 중..."
echo "접근 URL: http://localhost:8501"
echo ""
echo "⚠️ SSH 터널링이 설정되어 있는지 check하세요!"
echo "   로컬 명령어: ssh -L 8501:localhost:8501 -i ~/Desktop/keys/EC2-DeepLearning.pem ec2-user@98.80.100.116"
echo ""
echo "🛑 stopped"
echo ""

# 종합 Dashboard run
streamlit run streamlit_comprehensive_dashboard.py --server.address localhost --server.port 8501
