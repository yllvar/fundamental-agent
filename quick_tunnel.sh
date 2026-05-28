#!/bin/bash
# 빠른 SSH 터널링 스크립트

echo "🚀 SSH 터널링 starting..."

# 키 권한 setup
chmod 400 ~/Desktop/keys/jihwanw_key.pem

echo "🔑 SSH 키 권한 설정 complete"
echo "🌐 터널 생성 중... (EC2에 접속됩니다)"
echo ""
echo "📊 EC2 접속 후 다음 명령어를 실행하세요:"
echo "cd /home/ec2-user/projects/ABP/fundamental_agent && source /home/ec2-user/dl_env/bin/activate && ALPHA_VANTAGE_API_KEY=9TLAUWS4L3099YK3 streamlit run streamlit_intelligence_dashboard.py"
echo ""
echo "🌍 그 후 브라우저에서: http://localhost:8501"
echo ""

# SSH 터널 생성 및 access
ssh -L 8501:localhost:8501 -i ~/Desktop/keys/jihwanw_key.pem ec2-user@98.80.100.116
