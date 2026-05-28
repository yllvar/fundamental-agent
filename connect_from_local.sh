#!/bin/bash

echo "🚀 EC2 Streamlit Dashboard 연결 스크립트"
echo ""

# 설정 변수 (사용자가 Modify해야 함)
EC2_IP="YOUR_EC2_PUBLIC_IP"
KEY_FILE="~/.ssh/your-key.pem"
LOCAL_PORT=8501
REMOTE_PORT=8501

echo "📋 연결 정보:"
echo "   EC2 IP: $EC2_IP"
echo "   키 파일: $KEY_FILE"
echo "   로컬 포트: $LOCAL_PORT"
echo "   원격 포트: $REMOTE_PORT"
echo ""

echo "⚠️  주의: EC2_IP와 KEY_FILE 경로를 실제 값으로 Modify하세요!"
echo ""

# SSH 터널 생성
echo "🔗 SSH 터널을 생성합니다..."
echo "📱 터널이 연결되면 브라우저에서 http://localhost:$LOCAL_PORT 로 접속하세요"
echo ""

ssh -L $LOCAL_PORT:localhost:$REMOTE_PORT -i "$KEY_FILE" ec2-user@$EC2_IP
