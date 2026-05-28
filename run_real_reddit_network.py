#!/usr/bin/env python3
"""
실제 Reddit 데이터 기반 네트워크 분석 대시보드 실행
"""

import streamlit as st
import sys
import os

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from streamlit_real_network_page import create_real_network_page

# 페이지 설정
st.set_page_config(
    page_title="📱 실제 Reddit 네트워크 분석",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stSelectbox > div > div {
        background-color: #f0f2f6;
    }
    .metric-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #007bff;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 0.75rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        padding: 0.75rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """메인 함수"""
    
    # 헤더
    st.markdown("""
    # 📱 실제 Reddit 데이터 기반 경제 네트워크 분석
    
    **🎯 실제 데이터만 사용하는 신뢰성 있는 분석:**
    - ✅ **실제 Reddit API**: .env 파일의 API 키 사용
    - ✅ **8개 경제 서브레딧**: r/economics, r/investing, r/stocks 등
    - ✅ **실시간 데이터**: 현재 경제 이슈 반영
    - ✅ **가상 데이터 없음**: 100% 실제 사용자 포스트
    """)
    
    # Reddit 연결 상태 확인
    try:
        from data_monitoring.real_reddit_collector import RealRedditCollector
        collector = RealRedditCollector()
        
        st.markdown("""
        <div class="success-box">
        ✅ <strong>Reddit API 연결 성공</strong><br>
        실제 경제 서브레딧에서 데이터를 수집할 준비가 완료되었습니다.
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.markdown(f"""
        <div class="error-box">
        ❌ <strong>Reddit API 연결 실패</strong><br>
        오류: {str(e)}<br><br>
        <strong>해결 방법:</strong><br>
        1. .env 파일에 Reddit API 키가 올바르게 설정되어 있는지 확인<br>
        2. 인터넷 연결 상태 확인<br>
        3. Reddit API 사용량 제한 확인
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 실제 네트워크 분석 페이지 실행
    create_real_network_page()
    
    # 푸터
    st.markdown("---")
    st.markdown("""
    ### 📊 실제 데이터 vs 가상 데이터 비교
    
    | 항목 | 가상/시뮬레이션 데이터 | **실제 Reddit 데이터** |
    |------|----------------------|----------------------|
    | **데이터 소스** | 미리 작성된 샘플 | ✅ 실제 Reddit API |
    | **신뢰성** | 낮음 | ✅ 높음 |
    | **실시간성** | 없음 | ✅ 실시간 업데이트 |
    | **다양성** | 제한적 | ✅ 수천 명의 실제 의견 |
    | **감정 분석** | 가상 | ✅ 실제 투자자 심리 |
    | **경제 이슈 반영** | 일반적 | ✅ 현재 핫이슈 |
    
    **🎯 실제 데이터 사용의 장점:**
    - **투자 의사결정**: 실제 투자자들의 생각과 감정 파악
    - **시장 트렌드**: 현재 가장 관심받는 경제 이슈 식별
    - **리스크 관리**: 실제 우려사항과 위험 요소 발견
    - **기회 포착**: 새로운 투자 기회와 트렌드 조기 발견
    """)
    
    # 사용 가이드
    with st.expander("📖 사용 가이드"):
        st.markdown("""
        ### 🚀 분석 실행 방법
        
        1. **사이드바 설정**:
           - 최대 포스트 수: 수집할 Reddit 포스트 개수
           - 최소 연결 강도: 네트워크에서 표시할 관계의 최소 강도
           - 최대 노드 수: 시각화할 최대 경제 개념 수
           - 레이아웃: 네트워크 그래프 배치 방식
        
        2. **분석 실행**:
           - "🔍 실제 데이터 분석 실행" 버튼 클릭
           - Reddit에서 실시간 데이터 수집 (30초-1분 소요)
           - 경제 개념 추출 및 네트워크 분석
        
        3. **결과 해석**:
           - **네트워크 그래프**: 경제 개념 간 관계 시각화
           - **인사이트**: AI가 생성한 주요 발견사항
           - **메트릭**: 네트워크 구조 분석 지표
           - **서브레딧 통계**: 데이터 수집 상세 정보
        
        ### ⚠️ 주의사항
        
        - **API 제한**: Reddit API는 분당 60회 요청 제한
        - **데이터 품질**: 실제 사용자 데이터이므로 품질이 다양함
        - **실시간성**: 분석 시점의 데이터 반영
        - **언어**: 주로 영어 포스트, 일부 한국어 포함
        """)

if __name__ == "__main__":
    main()
