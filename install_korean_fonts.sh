#!/bin/bash
# 한글 폰트 설치 스크립트

echo "🔤 한글 폰트 설치 starting..."

# System 업데이트
sudo yum update -y

# 한글 폰트 Package 설치
echo "📦 한글 폰트 Package 설치 중..."
sudo yum install -y \
    google-noto-cjk-fonts \
    google-noto-fonts-common \
    dejavu-fonts-common \
    dejavu-sans-fonts

# 폰트 캐시 업데이트
echo "🔄 폰트 캐시 업데이트 중..."
fc-cache -fv

# 설치된 한글 폰트 check
echo "✅ 설치된 한글 폰트 목록:"
fc-list | grep -i "noto\|nanum\|dejavu" | head -10

# matplotlib 폰트 캐시 삭제 (재생성을 위해)
echo "🗑️ matplotlib 폰트 캐시 삭제..."
rm -rf ~/.cache/matplotlib

echo "🎉 한글 폰트 설치 complete!"
echo "📋 다음 단계:"
echo "1. Python 스크립트 재실행"
echo "2. matplotlib이 새 폰트를 인식하도록 재시작"
