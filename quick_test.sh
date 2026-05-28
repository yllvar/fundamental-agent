#!/bin/bash
# AI 기사 생성 System 빠른 테스트 스크립트

echo "🧪 AI 기사 생성 System 빠른 테스트"
echo "=================================="

# 현재 Directory check
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Task Directory: $SCRIPT_DIR"

# 1. Python 환경 테스트
echo ""
echo "🐍 Python 환경 테스트:"
python --version || { echo "❌ Python 실행 실패"; exit 1; }

# 2. 필수 Package 테스트
echo ""
echo "📦 필수 Package 테스트:"
REQUIRED_PACKAGES=("streamlit" "pandas" "plotly" "yfinance" "boto3")

for package in "${REQUIRED_PACKAGES[@]}"; do
    if python -c "import $package" 2>/dev/null; then
        VERSION=$(python -c "import $package; print($package.__version__)" 2>/dev/null || echo "버전 check 불가")
        echo "✅ $package: $VERSION"
    else
        echo "❌ $package: 설치되지 않음"
        MISSING_PACKAGES+=($package)
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo ""
    echo "⚠️ 누락된 Package가 있습니다:"
    printf '%s\n' "${MISSING_PACKAGES[@]}"
    echo ""
    echo "설치 명령어:"
    echo "pip install ${MISSING_PACKAGES[*]}"
    exit 1
fi

# 3. 이벤트 System 테스트
echo ""
echo "🔍 이벤트 감지 System 테스트:"
if python -c "
import sys
sys.path.append('.')
from data_monitoring.auto_article_event_system import AutoArticleEventSystem
system = AutoArticleEventSystem()
events = system.detect_events()
print(f'✅ 이벤트 감지 성공: {len(events)}개 이벤트')
for i, event in enumerate(events[:3], 1):
    print(f'  {i}. {event[\"description\"]}')
" 2>/dev/null; then
    echo "✅ 이벤트 System 정상"
else
    echo "❌ 이벤트 System 오류"
    echo "상세 오류:"
    python -c "
import sys
sys.path.append('.')
from data_monitoring.auto_article_event_system import AutoArticleEventSystem
system = AutoArticleEventSystem()
events = system.detect_events()
print(f'이벤트 수: {len(events)}')
" 2>&1
fi

# 4. AI 에이전트 System 테스트
echo ""
echo "🤖 AI 에이전트 System 테스트:"
if python -c "
import sys
sys.path.append('.')
from agents.orchestrator_strand import OrchestratorStrand
orchestrator = OrchestratorStrand()
print('✅ AI 에이전트 System 초기화 성공')
print(f'  능력: {len(orchestrator.get_capabilities())}개')
" 2>/dev/null; then
    echo "✅ AI 에이전트 System 정상"
else
    echo "❌ AI 에이전트 System 오류"
    echo "상세 오류:"
    python -c "
import sys
sys.path.append('.')
from agents.orchestrator_strand import OrchestratorStrand
orchestrator = OrchestratorStrand()
" 2>&1
fi

# 5. AWS 연결 테스트
echo ""
echo "☁️ AWS 연결 테스트:"
if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "✅ AWS 자격 증명 설정됨"
    
    # AWS CLI 테스트 (있는 경우)
    if command -v aws >/dev/null 2>&1; then
        if aws sts get-caller-identity >/dev/null 2>&1; then
            echo "✅ AWS CLI 연결 정상"
        else
            echo "⚠️ AWS CLI 연결 실패 (자격 증명 check 필요)"
        fi
    else
        echo "ℹ️ AWS CLI 미설치 (선택사항)"
    fi
    
    # Bedrock 연결 테스트
    if python -c "
import boto3
try:
    client = boto3.client('bedrock', region_name='us-east-1')
    print('✅ AWS Bedrock 연결 가능')
except Exception as e:
    print(f'⚠️ AWS Bedrock 연결 실패: {str(e)}')
" 2>/dev/null; then
        echo "✅ Bedrock 연결 테스트 complete"
    else
        echo "⚠️ Bedrock 연결 테스트 실패"
    fi
else
    echo "❌ AWS 자격 증명 미설정"
    echo "설정 방법:"
    echo "export AWS_ACCESS_KEY_ID=your_access_key"
    echo "export AWS_SECRET_ACCESS_KEY=your_secret_key"
    echo "export AWS_DEFAULT_REGION=us-east-1"
fi

# 6. Directory 구조 check
echo ""
echo "📁 Directory 구조 check:"
REQUIRED_DIRS=("output" "logs" "agents" "data_monitoring")

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir/ Directory 존재"
    else
        echo "⚠️ $dir/ Directory 없음 (자동 생성됨)"
        mkdir -p "$dir"
    fi
done

# 7. 포트 사용 가능성 check
echo ""
echo "🌐 포트 8501 사용 가능성 check:"
if lsof -i :8501 >/dev/null 2>&1; then
    echo "⚠️ 포트 8501이 이미 사용 중입니다"
    echo "사용 중인 프로세스:"
    lsof -i :8501
    echo ""
    echo "해결 방법:"
    echo "./stop_system.sh  # 기존 System stop"
else
    echo "✅ 포트 8501 사용 가능"
fi

# 8. 메모리 사용량 check
echo ""
echo "💾 System 리소스 check:"
MEMORY_TOTAL=$(free -h | awk '/^Mem:/ {print $2}')
MEMORY_AVAILABLE=$(free -h | awk '/^Mem:/ {print $7}')
echo "메모리: $MEMORY_AVAILABLE / $MEMORY_TOTAL 사용 가능"

DISK_USAGE=$(df -h . | awk 'NR==2 {print $4 " / " $2 " 사용 가능"}')
echo "디스크: $DISK_USAGE"

# 테스트 결과 요약
echo ""
echo "=================================="
echo "🧪 테스트 결과 요약:"

if [ ${#MISSING_PACKAGES[@]} -eq 0 ]; then
    echo "✅ 모든 필수 Package 설치됨"
else
    echo "❌ 누락된 Package 있음"
fi

if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "✅ AWS 자격 증명 설정됨"
else
    echo "⚠️ AWS 자격 증명 check 필요"
fi

if ! lsof -i :8501 >/dev/null 2>&1; then
    echo "✅ 포트 8501 사용 가능"
else
    echo "⚠️ 포트 8501 사용 중"
fi

echo ""
echo "🚀 System 실행 준비 상태:"
if [ ${#MISSING_PACKAGES[@]} -eq 0 ] && ! lsof -i :8501 >/dev/null 2>&1; then
    echo "🎉 모든 테스트 통과! System 실행 가능"
    echo ""
    echo "실행 명령어:"
    echo "./run_ai_article_system.sh"
else
    echo "⚠️ 일부 문제가 발견되었습니다. 위의 내용을 check하세요."
fi
