#!/usr/bin/env python3
"""
Streamlit 대시보드 데모 스크립트
"""

import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path

def check_dependencies():
    """필요한 의존성 확인"""
    try:
        import streamlit
        import plotly
        import matplotlib
        import pandas
        import numpy
        print("✅ 모든 의존성이 설치되어 있습니다.")
        return True
    except ImportError as e:
        print(f"❌ 의존성 누락: {e}")
        print("다음 명령으로 설치하세요: pip install -r requirements.txt")
        return False

def check_article_data():
    """기사 데이터 확인"""
    output_dir = Path(__file__).parent / "output"
    
    if not output_dir.exists():
        print("❌ output 디렉토리가 없습니다.")
        return False
    
    json_files = list(output_dir.glob("pipeline_result_*.json"))
    
    if not json_files:
        print("⚠️ 생성된 기사가 없습니다.")
        print("먼저 다음 명령으로 기사를 생성하세요:")
        print("python main.py --mode full --market-summary")
        return False
    
    print(f"✅ {len(json_files)}개의 기사를 찾았습니다.")
    return True

def start_streamlit():
    """Streamlit 애플리케이션 시작"""
    print("🚀 Streamlit 대시보드를 시작합니다...")
    
    # 현재 디렉토리를 프로젝트 루트로 설정
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Streamlit 실행 명령
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        "streamlit_app/app.py",
        "--server.headless", "false",
        "--server.address", "0.0.0.0",
        "--server.port", "8501"
    ]
    
    print("📍 대시보드 URL: http://localhost:8501")
    print("🌐 외부 접속 URL: http://[YOUR_IP]:8501")
    print("⏹️  종료하려면 Ctrl+C를 누르세요.")
    print("-" * 60)
    
    try:
        # 브라우저 자동 열기 (로컬 환경에서만)
        try:
            time.sleep(2)
            webbrowser.open("http://localhost:8501")
        except:
            pass
        
        # Streamlit 실행
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n👋 대시보드가 종료되었습니다.")
    except subprocess.CalledProcessError as e:
        print(f"❌ 실행 오류: {e}")
        return False
    
    return True

def show_usage_guide():
    """사용법 안내"""
    print("""
📖 Streamlit 대시보드 사용법:

1. 🎛️ 사이드바 제어판:
   - "새 기사 생성" 버튼으로 최신 경제 기사 생성
   - 기사 목록에서 원하는 기사 선택
   - 차트, 이미지, 광고 표시 옵션 설정

2. 📊 메인 대시보드:
   - 실시간 시장 현황 메트릭
   - 인터랙티브 차트 (주식 현황, 변화율, 섹터 성과, VIX 지수)
   - AI 생성 경제 기사 본문
   - 기사 관련 이미지 및 워드클라우드
   - 맞춤형 광고

3. 🔄 실시간 업데이트:
   - 새 기사 생성 시 자동으로 최신 데이터 수집
   - 차트와 메트릭 실시간 업데이트
   - 기사 내용 기반 맞춤 광고 표시

4. 📱 반응형 디자인:
   - 데스크톱, 태블릿, 모바일 지원
   - 다크/라이트 테마 자동 적용
   - 사용자 친화적 인터페이스
""")

def main():
    """메인 함수"""
    print("🎯 경제 뉴스 AI 대시보드 데모")
    print("=" * 50)
    
    # 의존성 확인
    if not check_dependencies():
        return
    
    # 기사 데이터 확인
    if not check_article_data():
        print("\n💡 기사를 먼저 생성하시겠습니까? (y/n): ", end="")
        response = input().lower().strip()
        
        if response == 'y':
            print("기사를 생성하고 있습니다...")
            try:
                subprocess.run([
                    sys.executable, "main.py", 
                    "--mode", "full", 
                    "--market-summary"
                ], check=True, timeout=300)
                print("✅ 기사 생성 완료!")
            except subprocess.TimeoutExpired:
                print("⏰ 기사 생성 시간 초과")
                return
            except subprocess.CalledProcessError:
                print("❌ 기사 생성 실패")
                return
        else:
            print("기사 생성 없이 데모를 계속합니다.")
    
    # 사용법 안내
    show_usage_guide()
    
    print("\n계속하려면 Enter를 누르세요...")
    input()
    
    # Streamlit 시작
    start_streamlit()

if __name__ == "__main__":
    main()
