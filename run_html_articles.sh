#!/bin/bash

# HTML 기사 생성 및 Slack 전송 간편 실행 스크립트

echo "📰 HTML 기사 자동 생성 System"
echo "=================================================="

# 현재 Directory로 이동
cd "$(dirname "$0")"

# .env 파일 check
if [ -f ".env" ]; then
    echo "✅ .env 파일 Load됨"
    source .env
else
    echo "❌ .env 파일을 찾을 수 not found."
    exit 1
fi

# 출력 Directory 생성
mkdir -p output/html_articles
mkdir -p output/market_data

echo ""
echo "🚀 HTML 기사 생성 System 실행 중..."
echo "  📊 1단계: 실시간 시장 데이터 수집"
echo "  🚨 2단계: 이벤트 감지 (3% 이상 변동)"
echo "  ✍️ 3단계: AI 기사 작성"
echo "  📄 4단계: HTML 파일 생성"
echo "  📱 5단계: Slack 알림 전송"
echo ""

# HTML 기사 생성 System run
python html_article_slack_system.py

# 실행 결과 check
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 HTML 기사 생성 complete!"
    echo ""
    
    # 생성된 HTML 파일 목록
    if [ -d "output/html_articles" ] && [ "$(ls -A output/html_articles)" ]; then
        echo "📄 생성된 HTML 기사:"
        ls -t output/html_articles/*.html 2>/dev/null | head -5 | while read file; do
            if [ -f "$file" ]; then
                filename=$(basename "$file")
                echo "  📰 $filename"
            fi
        done
        
        echo ""
        echo "💡 HTML 기사 보는 방법:"
        latest_html=$(ls -t output/html_articles/*.html 2>/dev/null | head -1)
        if [ -n "$latest_html" ]; then
            echo "  🌐 브라우저에서 열기: open $latest_html"
            echo "  📱 모바일에서 보기: 파일을 웹서버에 업Load"
        fi
    fi
    
    # 시장 데이터 파일
    if [ -d "output/market_data" ] && [ "$(ls -A output/market_data)" ]; then
        latest_data=$(ls -t output/market_data/*.json 2>/dev/null | head -1)
        if [ -n "$latest_data" ]; then
            echo "  📊 시장 데이터: $(basename "$latest_data")"
        fi
    fi
    
    echo ""
    echo "📱 Slack 채널을 check하여 알림을 check하세요!"
    echo ""
    echo "📋 추가 명령어:"
    echo "  • 다시 실행: ./run_html_articles.sh"
    echo "  • Slack 테스트: python test_slack_notification.py"
    echo "  • 최신 HTML 보기: open \$(ls -t output/html_articles/*.html | head -1)"
    
else
    echo ""
    echo "❌ HTML 기사 생성 실패"
    echo "📋 문제 해결:"
    echo "  • AWS 자격 증명 check: aws sts get-caller-identity"
    echo "  • Slack 웹훅 테스트: python test_slack_notification.py"
    echo "  • 인터넷 연결 check"
fi

echo "=================================================="
