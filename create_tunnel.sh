#!/bin/bash
# SSH 터널링 스크립트

echo "🔧 SSH 터널 설정 중..."

# 기존 터널 정리
pkill -f "ssh.*8501" 2>/dev/null

# 포트 사용 check
if lsof -i:8501 >/dev/null 2>&1; then
    echo "⚠️ 포트 8501이 사용 중입니다. 프로세스를 stopped"
    lsof -ti:8501 | xargs kill -9 2>/dev/null
    sleep 2
fi

echo "🚀 SSH 터널 생성 중..."
ssh -L 8501:localhost:8501 -i ~/Desktop/keys/EC2-DeepLearning.pem ec2-user@98.80.100.116
