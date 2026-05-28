#!/bin/bash

# Slack Economic 알림 모니터링 상태 check 스크립트

echo "📊 Slack Economic 알림 모니터링 상태"
echo "================================"

cd /home/ec2-user/projects/ABP/fundamental_agent

# 프로세스 상태 check
if pgrep -f "start_slack_monitoring.py" > /dev/null; then
    PID=$(pgrep -f "start_slack_monitoring.py")
    echo "🟢 상태: 실행 중"
    echo "📋 프로세스 ID: $PID"
    
    # 실행 시간 check
    if [ -f "logs/monitoring.pid" ]; then
        STORED_PID=$(cat logs/monitoring.pid)
        if [ "$PID" = "$STORED_PID" ]; then
            echo "✅ PID 파일과 일치"
        else
            echo "⚠️  PID 파일 불일치 (저장된 PID: $STORED_PID)"
        fi
    fi
    
    # 프로세스 정보
    echo ""
    echo "📈 프로세스 정보:"
    ps -p $PID -o pid,ppid,etime,cmd --no-headers
    
else
    echo "🔴 상태: stop됨"
    
    if [ -f "logs/monitoring.pid" ]; then
        echo "⚠️  PID 파일이 남아있습니다. 정리가 필요할 수 있습니다."
    fi
fi

echo ""
echo "📄 로그 파일 상태:"

# 로그 파일들 check
if [ -f "logs/background_monitoring.log" ]; then
    LOG_SIZE=$(du -h logs/background_monitoring.log | cut -f1)
    LOG_LINES=$(wc -l < logs/background_monitoring.log)
    echo "  📋 백그라운드 로그: $LOG_SIZE ($LOG_LINES 줄)"
    
    # 최근 로그 check
    echo ""
    echo "📝 최근 로그 (마지막 5줄):"
    echo "------------------------"
    tail -5 logs/background_monitoring.log 2>/dev/null || echo "로그 파일을 읽을 수 not found."
else
    echo "  ❌ 백그라운드 로그 파일 없음"
fi

if [ -f "logs/slack_monitoring.log" ]; then
    LOG_SIZE=$(du -h logs/slack_monitoring.log | cut -f1)
    echo "  📋 Slack 모니터링 로그: $LOG_SIZE"
else
    echo "  ❌ Slack 모니터링 로그 파일 없음"
fi

echo ""
echo "🔧 관리 명령어:"
echo "  시작: ./start_background_monitoring.sh"
echo "  stop: ./stop_monitoring.sh"
echo "  로그 실시간 보기: tail -f logs/background_monitoring.log"
echo "  로그 오류 check: grep ERROR logs/background_monitoring.log"

# 디스크 사용량 check
echo ""
echo "💾 디스크 사용량:"
du -sh logs/ output/ 2>/dev/null || echo "  로그/출력 Directory check 불가"

# 최근 알림 통계 (간단히)
if [ -f "logs/slack_monitoring.log" ]; then
    TODAY=$(date +%Y-%m-%d)
    ALERT_COUNT=$(grep -c "Slack 알림 전송 성공" logs/slack_monitoring.log 2>/dev/null || echo "0")
    echo ""
    echo "📊 오늘 전송된 알림: $ALERT_COUNT 개"
fi
