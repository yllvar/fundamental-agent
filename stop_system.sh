#!/bin/bash
# AI Article Generation System stop script

echo "🛑 Stopping AI Article Generation System"
echo "=================================="

# Check Streamlit processes
STREAMLIT_PROCESSES=$(ps aux | grep streamlit | grep -v grep)
if [ -n "$STREAMLIT_PROCESSES" ]; then
    echo "📊 실행 중인 Streamlit 프로세스:"
    echo "$STREAMLIT_PROCESSES"
    echo ""
    
    # PID 추출
    STREAMLIT_PIDS=$(ps aux | grep streamlit | grep -v grep | awk '{print $2}')
    
    echo "🔄 Streamlit 프로세스 stopped"
    for PID in $STREAMLIT_PIDS; do
        echo "  stopped"
        kill $PID 2>/dev/null
    done
    
    # 강제 stop
    sleep 3
    
    # 여전히 실행 중인지 check
    REMAINING_PROCESSES=$(ps aux | grep streamlit | grep -v grep)
    if [ -n "$REMAINING_PROCESSES" ]; then
        echo "⚠️ 일부 프로세스가 여전히 실행 중입니다. 강제 stopped"
        pkill -9 -f streamlit 2>/dev/null
        sleep 2
    fi
    
    # 최종 check
    FINAL_CHECK=$(ps aux | grep streamlit | grep -v grep)
    if [ -z "$FINAL_CHECK" ]; then
        echo "✅ 모든 Streamlit 프로세스가 stopped"
    else
        echo "❌ 일부 프로세스 stopped"
        echo "$FINAL_CHECK"
    fi
else
    echo "ℹ️ 실행 중인 Streamlit 프로세스가 not found"
fi

echo ""

# 포트 check
echo "🌐 포트 8501 상태 check:"
if lsof -i :8501 >/dev/null 2>&1; then
    echo "⚠️ 포트 8501이 여전히 사용 중입니다"
    echo "사용 중인 프로세스:"
    lsof -i :8501
    
    # 포트 사용 프로세스 강제 stop
    echo "🔄 포트 사용 프로세스 강제 stopped"
    lsof -ti :8501 | xargs kill -9 2>/dev/null || true
    sleep 2
    
    if ! lsof -i :8501 >/dev/null 2>&1; then
        echo "✅ 포트 8501이 해제되었습니다"
    else
        echo "❌ 포트 8501 해제 실패"
    fi
else
    echo "✅ 포트 8501이 해제되어 있습니다"
fi

echo ""

# 임시 파일 정리 (선택사항)
echo "🧹 임시 파일 정리:"
if [ -f "streamlit_comprehensive.log" ]; then
    LOG_SIZE=$(du -h streamlit_comprehensive.log | cut -f1)
    echo "📝 로그 파일 크기: $LOG_SIZE"
    
    read -p "로그 파일을 Backup하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        BACKUP_NAME="streamlit_comprehensive_$(date +%Y%m%d_%H%M%S).log"
        cp streamlit_comprehensive.log "logs/$BACKUP_NAME" 2>/dev/null || cp streamlit_comprehensive.log "$BACKUP_NAME"
        echo "✅ 로그 Backup complete: $BACKUP_NAME"
    fi
    
    read -p "현재 로그 파일을 삭제하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm streamlit_comprehensive.log
        echo "✅ 로그 파일 삭제 complete"
    else
        echo "ℹ️ 로그 파일 유지"
    fi
else
    echo "ℹ️ 로그 파일이 not found"
fi

echo ""

# 세션 상태 정리 안내
echo "🔄 세션 상태 정리 안내:"
echo "Streamlit 세션 상태는 자동으로 정리됩니다."
echo "필요시 브라우저 캐시를 수동으로 정리하세요."

echo ""
echo "=================================="
echo "🎉 AI 기사 생성 System이 stop되었습니다"
echo ""
echo "🔧 다시 시작하려면:"
echo "./run_ai_article_system.sh"
echo ""
echo "📊 상태 check:"
echo "./check_status.sh"
