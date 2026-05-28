#!/bin/bash
# 로컬 컴퓨터용 연결 테스트 스크립트

echo "🔍 로컬 컴퓨터 연결 상태 진단"
echo "=" * 40

echo "1️⃣ 포트 8501 사용 상태:"
if command -v lsof >/dev/null 2>&1; then
    lsof -i :8501 || echo "✅ 포트 8501 사용 가능"
else
    netstat -an | grep :8501 || echo "✅ 포트 8501 사용 가능"
fi

echo ""
echo "2️⃣ SSH 터널 프로세스:"
ps aux | grep "ssh.*8501" | grep -v grep || echo "✅ SSH 터널 프로세스 없음"

echo ""
echo "3️⃣ EC2 연결 테스트:"
echo "ssh -i ~/Desktop/keys/EC2-DeepLearning.pem ec2-user@98.80.100.116 'echo 연결 성공'"

echo ""
echo "4️⃣ 권장 해결 순서:"
echo "   a) pkill -f 'ssh.*8501'"
echo "   b) sleep 3"
echo "   c) ssh -L 8501:localhost:8501 -i ~/Desktop/keys/EC2-DeepLearning.pem ec2-user@98.80.100.116"

echo ""
echo "5️⃣ 대안 포트 사용:"
echo "   ssh -L 8502:localhost:8501 -i ~/Desktop/keys/EC2-DeepLearning.pem ec2-user@98.80.100.116"
echo "   브라우저: http://localhost:8502"
