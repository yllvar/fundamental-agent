#!/bin/bash

echo "🔍 Streamlit 서버 상태 check"
echo "================================"

# 프로세스 check
echo "📋 실행 중인 Streamlit 프로세스:"
ps aux | grep streamlit | grep -v grep

echo ""
echo "🌐 포트 8501 사용 상태:"
netstat -tlnp | grep :8501 || echo "포트 8501이 사용되지 않고 있습니다."

echo ""
echo "📊 System 리소스:"
echo "CPU 사용률: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')"
echo "메모리 사용률: $(free | grep Mem | awk '{printf("%.1f%%", $3/$2 * 100.0)}')"

echo ""
echo "📝 최근 로그 (마지막 10줄):"
if [ -f "streamlit.log" ]; then
    tail -10 streamlit.log
else
    echo "streamlit.log 파일을 찾을 수 not found."
fi

echo ""
echo "🔗 연결 테스트:"
curl -s -o /dev/null -w "%{http_code}" http://localhost:8501 | \
    case $(cat) in
        200) echo "✅ Streamlit 서버가 정상적으로 실행 중입니다." ;;
        *) echo "❌ Streamlit 서버에 연결할 수 not found." ;;
    esac
