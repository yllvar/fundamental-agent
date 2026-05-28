#!/bin/bash

# Economic News 자동 생성 파이프라인 실행 스크립트

echo "🚀 Economic News 자동 생성 파이프라인 시작"
echo "=================================================="

# 현재 Directory check
if [ ! -f "run_full_pipeline.py" ]; then
    echo "❌ run_full_pipeline.py 파일을 찾을 수 not found."
    echo "올바른 Directory에서 실행해주세요."
    exit 1
fi

# Python Virtual environment check (선택사항)
if [ -n "$VIRTUAL_ENV" ]; then
    echo "✅ Virtual environment activated됨: $VIRTUAL_ENV"
else
    echo "⚠️ Virtual environment이 activated되지 않았습니다."
fi

# AWS 자격증명 check
if aws sts get-caller-identity >/dev/null 2>&1; then
    echo "✅ AWS 자격증명 check됨"
else
    echo "❌ AWS 자격증명을 check할 수 not found."
    echo "aws configure를 실행하여 자격증명을 설정해주세요."
    exit 1
fi

echo ""
echo "📊 파이프라인 실행 중..."
echo "=================================================="

# 파이프라인 run
python run_full_pipeline.py "$@"

# 실행 결과 check
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 파이프라인 실행 complete!"
    echo "📁 결과 파일은 output/ Directory에서 check하세요."
    
    # 최신 결과 파일 표시
    if [ -d "output" ]; then
        echo ""
        echo "📄 생성된 파일:"
        ls -la output/ | grep "$(date +%Y%m%d)" | tail -5
    fi
else
    echo ""
    echo "❌ 파이프라인 실행 실패"
    echo "로그를 check하여 문제를 해결해주세요."
    exit 1
fi
