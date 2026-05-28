#!/bin/bash

# 원격 실행 스크립트
# 로컬 PC에서 EC2의 Streamlit을 원격으로 실행하고 터널링

echo "🚀 EC2에서 Economic News System 원격 실행"
echo "=================================="

# 설정 (사용자가 Modify해야 함)
EC2_IP="YOUR_EC2_PUBLIC_IP"
KEY_FILE="~/.ssh/your-key.pem"
PROJECT_PATH="/home/ec2-user/projects/ABP/fundamental_agent"

echo "📋 연결 정보:"
echo "   EC2 IP: $EC2_IP"
echo "   키 파일: $KEY_FILE"
echo "   Project 경로: $PROJECT_PATH"
echo ""

# 함수 정의
start_streamlit() {
    echo "🔧 EC2에서 Streamlit 서버 시작 중..."
    ssh -i "$KEY_FILE" ec2-user@$EC2_IP << EOF
        cd $PROJECT_PATH
        
        # 기존 Streamlit 프로세스 stop
        pkill -f streamlit
        
        # 백그라운드에서 Streamlit run
        nohup streamlit run integrated_dashboard.py \
            --server.port=8501 \
            --server.address=0.0.0.0 \
            --server.headless=true \
            > streamlit.log 2>&1 &
        
        echo "✅ Streamlit 서버가 시작되었습니다."
        sleep 3
        
        # 서버 상태 check
        if pgrep -f streamlit > /dev/null; then
            echo "✅ Streamlit 프로세스가 실행 중입니다."
        else
            echo "❌ Streamlit 시작에 실패했습니다."
            exit 1
        fi
EOF
}

create_tunnel() {
    echo "🔗 SSH 터널 생성 중..."
    echo "📱 브라우저에서 http://localhost:8501 로 접속하세요"
    echo "🛑 stopped"
    echo ""
    
    # SSH 터널 생성 (포그라운드에서 실행)
    ssh -L 8501:localhost:8501 -i "$KEY_FILE" ec2-user@$EC2_IP -N
}

stop_streamlit() {
    echo "🛑 EC2에서 Streamlit 서버 stop 중..."
    ssh -i "$KEY_FILE" ec2-user@$EC2_IP << EOF
        pkill -f streamlit
        echo "✅ Streamlit 서버가 stop되었습니다."
EOF
}

check_status() {
    echo "🔍 EC2 서버 상태 check 중..."
    ssh -i "$KEY_FILE" ec2-user@$EC2_IP << EOF
        cd $PROJECT_PATH
        echo "📋 Streamlit 프로세스:"
        ps aux | grep streamlit | grep -v grep || echo "실행 중인 Streamlit 프로세스가 not found."
        
        echo ""
        echo "🌐 포트 8501 상태:"
        netstat -tlnp | grep :8501 || echo "포트 8501이 사용되지 않고 있습니다."
        
        if [ -f "streamlit.log" ]; then
            echo ""
            echo "📝 최근 로그:"
            tail -5 streamlit.log
        fi
EOF
}

# 메뉴 표시
show_menu() {
    echo ""
    echo "📋 사용 가능한 명령어:"
    echo "1) start    - Streamlit 서버 시작 및 터널 연결"
    echo "2) stop     - Streamlit 서버 stop"
    echo "3) status   - 서버 상태 check"
    echo "4) tunnel   - 터널만 연결 (서버가 이미 실행 중인 경우)"
    echo "5) restart  - 서버 재시작"
    echo "6) exit     - stopped"
    echo ""
}

# 메인 로직
case "$1" in
    start)
        start_streamlit
        if [ $? -eq 0 ]; then
            create_tunnel
        fi
        ;;
    stop)
        stop_streamlit
        ;;
    status)
        check_status
        ;;
    tunnel)
        create_tunnel
        ;;
    restart)
        stop_streamlit
        sleep 2
        start_streamlit
        if [ $? -eq 0 ]; then
            create_tunnel
        fi
        ;;
    *)
        show_menu
        echo "사용법: $0 {start|stop|status|tunnel|restart}"
        echo ""
        echo "예시:"
        echo "  $0 start    # 서버 시작 및 터널 연결"
        echo "  $0 status   # 상태 check"
        echo "  $0 stop     # 서버 stop"
        ;;
esac
