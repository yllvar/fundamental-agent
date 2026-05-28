#!/bin/bash
# AI 기사 생성 System 원클릭 설치 및 실행 스크립트

echo "🚀 AI 기사 생성 System 원클릭 설치 및 실행"
echo "=============================================="

# 현재 Directory check
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Task Directory: $SCRIPT_DIR"

# 1. Python 환경 check
echo ""
echo "🐍 Python 환경 check..."
if ! command -v python >/dev/null 2>&1; then
    echo "❌ Python이 설치되지 않았습니다"
    echo "Python 3.8+ 설치가 필요합니다"
    exit 1
fi

PYTHON_VERSION=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python $PYTHON_VERSION 감지"

# 2. pip 업그레이드
echo ""
echo "📦 pip 업그레이드..."
python -m pip install --upgrade pip

# 3. 필수 Package 설치
echo ""
echo "📦 필수 Package 설치 중..."

# requirements.txt가 있으면 사용, 없으면 직접 설치
if [ -f "requirements.txt" ]; then
    echo "📋 requirements.txt 사용"
    pip install -r requirements.txt
else
    echo "📋 개별 Package 설치"
    PACKAGES=(
        "streamlit>=1.28.0"
        "pandas>=1.5.0"
        "plotly>=5.15.0"
        "yfinance>=0.2.0"
        "boto3>=1.26.0"
        "numpy>=1.24.0"
        "requests>=2.28.0"
        "python-dateutil>=2.8.0"
    )
    
    for package in "${PACKAGES[@]}"; do
        echo "설치 중: $package"
        pip install "$package"
    done
fi

# 4. 필요한 Directory 생성
echo ""
echo "📁 Directory 구조 생성..."
DIRS=(
    "output"
    "logs" 
    "streamlit_articles"
    "output/charts"
    "output/images"
    "output/automated_articles"
)

for dir in "${DIRS[@]}"; do
    mkdir -p "$dir"
    echo "✅ $dir/ 생성"
done

# 5. 환경 변수 설정 check
echo ""
echo "🔑 환경 변수 설정 check..."

if [ -z "$AWS_ACCESS_KEY_ID" ]; then
    echo "⚠️ AWS_ACCESS_KEY_ID가 설정되지 않았습니다"
    read -p "AWS Access Key ID를 입력하세요 (Enter로 건너뛰기): " AWS_KEY
    if [ -n "$AWS_KEY" ]; then
        export AWS_ACCESS_KEY_ID="$AWS_KEY"
        echo "export AWS_ACCESS_KEY_ID=\"$AWS_KEY\"" >> ~/.bashrc
        echo "✅ AWS_ACCESS_KEY_ID 설정됨"
    fi
fi

if [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "⚠️ AWS_SECRET_ACCESS_KEY가 설정되지 않았습니다"
    read -s -p "AWS Secret Access Key를 입력하세요 (Enter로 건너뛰기): " AWS_SECRET
    echo
    if [ -n "$AWS_SECRET" ]; then
        export AWS_SECRET_ACCESS_KEY="$AWS_SECRET"
        echo "export AWS_SECRET_ACCESS_KEY=\"$AWS_SECRET\"" >> ~/.bashrc
        echo "✅ AWS_SECRET_ACCESS_KEY 설정됨"
    fi
fi

if [ -z "$AWS_DEFAULT_REGION" ]; then
    echo "ℹ️ AWS_DEFAULT_REGION 설정 (기본값: us-east-1)"
    read -p "AWS Region을 입력하세요 [us-east-1]: " AWS_REGION
    AWS_REGION=${AWS_REGION:-us-east-1}
    export AWS_DEFAULT_REGION="$AWS_REGION"
    echo "export AWS_DEFAULT_REGION=\"$AWS_REGION\"" >> ~/.bashrc
    echo "✅ AWS_DEFAULT_REGION=$AWS_REGION 설정됨"
fi

# 6. System 테스트
echo ""
echo "🧪 System 테스트 running..."
if [ -f "quick_test.sh" ]; then
    chmod +x quick_test.sh
    ./quick_test.sh
else
    echo "⚠️ quick_test.sh를 찾을 수 not found. 기본 테스트 running..."
    
    # 기본 테스트
    echo "이벤트 System 테스트:"
    python -c "
import sys
sys.path.append('.')
from data_monitoring.auto_article_event_system import AutoArticleEventSystem
system = AutoArticleEventSystem()
events = system.detect_events()
print(f'✅ {len(events)}개 이벤트 감지 성공')
" 2>/dev/null && echo "✅ 이벤트 System 정상" || echo "❌ 이벤트 System 오류"
fi

# 7. 실행 스크립트 권한 setup
echo ""
echo "🔧 실행 스크립트 권한 설정..."
SCRIPTS=(
    "run_ai_article_system.sh"
    "check_status.sh"
    "stop_system.sh"
    "quick_test.sh"
)

for script in "${SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        chmod +x "$script"
        echo "✅ $script 실행 권한 설정"
    else
        echo "⚠️ $script를 찾을 수 not found"
    fi
done

# 8. 기존 프로세스 정리
echo ""
echo "🔄 기존 프로세스 정리..."
pkill -f streamlit 2>/dev/null || true
sleep 2

# 9. System run
echo ""
echo "🚀 AI 기사 생성 System running..."

if [ -f "run_ai_article_system.sh" ]; then
    ./run_ai_article_system.sh
else
    echo "⚠️ run_ai_article_system.sh를 찾을 수 not found. 직접 running..."
    
    nohup streamlit run streamlit_comprehensive_dashboard.py \
        --server.port=8501 \
        --server.address=0.0.0.0 \
        --server.headless=true \
        --browser.gatherUsageStats=false \
        > streamlit_comprehensive.log 2>&1 &
    
    echo "✅ Streamlit 백그라운드 실행 시작"
    sleep 5
    
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8501 | grep -q "200"; then
        echo "🌐 웹 서버 응답 정상"
    else
        echo "⚠️ 웹 서버 응답 대기 중..."
    fi
fi

# 10. complete 메시지
echo ""
echo "=============================================="
echo "🎉 AI 기사 생성 System 설치 및 실행 complete!"
echo ""
echo "📊 Dashboard 접속: http://localhost:8501"
echo "🤖 AI 기사 생성 페이지로 이동하세요"
echo ""
echo "🔧 관리 명령어:"
echo "- 상태 check: ./check_status.sh"
echo "- System stop: ./stop_system.sh"
echo "- System 재시작: ./stop_system.sh && ./run_ai_article_system.sh"
echo "- 로그 check: tail -f streamlit_comprehensive.log"
echo ""
echo "📋 사용법:"
echo "1. 브라우저에서 http://localhost:8501 접속"
echo "2. 사이드바에서 '🤖 AI 기사 생성' 선택"
echo "3. '🔄 5분 자동 새로고침' 체크 (선택사항)"
echo "4. '🚀 AI 기사 생성 시작' 버튼 클릭"
echo ""
echo "🎯 자동 기사 생성이 5분마다 실행됩니다!"
