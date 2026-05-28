#!/bin/bash
# 개인화된 SSH 터널링 명령어 모음

echo "🔧 개인화된 SSH 터널링 가이드"
echo "=" * 50
echo ""
echo "📋 check된 정보:"
echo "  로컬 IP: 10.40.3.202, 10.9.135.172, 11.160.153.48"
echo "  EC2 공개 IP: 98.80.100.116"
echo "  SSH 키: ~/Desktop/keys/jihwanw_key.pem"
echo ""

echo "🚀 실행 순서:"
echo "=" * 30
echo ""

echo "1️⃣ SSH 키 권한 설정 (로컬 컴퓨터에서):"
echo "chmod 400 ~/Desktop/keys/jihwanw_key.pem"
echo ""

echo "2️⃣ SSH 터널 생성 (로컬 컴퓨터에서):"
echo "ssh -L 8501:localhost:8501 -i ~/Desktop/keys/jihwanw_key.pem ec2-user@98.80.100.116"
echo ""

echo "3️⃣ EC2에서 Streamlit 실행 (SSH 연결된 터미널에서):"
echo "cd /home/ec2-user/projects/ABP/fundamental_agent"
echo "source /home/ec2-user/dl_env/bin/activate"
echo "ALPHA_VANTAGE_API_KEY=9TLAUWS4L3099YK3 streamlit run streamlit_intelligence_dashboard.py"
echo ""

echo "4️⃣ 로컬 브라우저에서 접근:"
echo "http://localhost:8501"
echo ""

echo "🔧 백그라운드 터널 (선택사항):"
echo "ssh -L 8501:localhost:8501 -i ~/Desktop/keys/jihwanw_key.pem -f -N ec2-user@98.80.100.116"
echo ""

echo "🛑 터널 stopped"
echo "ps aux | grep ssh"
echo "kill [SSH_PROCESS_ID]"
