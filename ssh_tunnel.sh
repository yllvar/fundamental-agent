#!/bin/bash
echo "🔧 SSH 터널링 starting..."
echo
echo "⚠️ 다음 정보를 입력하세요:"
read -p "EC2 IP 주소: " EC2_IP
read -p "SSH 키 파일 경로: " KEY_PATH

echo
echo "🚀 터널 생성 중..."
ssh -L 8501:localhost:8501 -i "$KEY_PATH" ec2-user@$EC2_IP