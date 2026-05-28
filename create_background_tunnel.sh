#!/bin/bash
# 백그라운드 SSH 터널링 스크립트

echo "🔧 백그라운드 SSH 터널 설정 중..."

# 기존 터널 정리
pkill -f "ssh.*8501" 2>/dev/null

# 백그라운드 터널 생성
ssh -L 8501:localhost:8501 -i ~/Desktop/keys/EC2-DeepLearning.pem -f -N ec2-user@98.80.100.116

if [ $? -eq 0 ]; then
    echo "✅ 백그라운드 터널 생성 성공"
    echo "🌐 브라우저에서 http://localhost:8501 접근 가능"
    echo "🛑 터널 stopped"
else
    echo "❌ 터널 생성 실패"
fi
