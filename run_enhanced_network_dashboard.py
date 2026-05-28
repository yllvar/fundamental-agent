#!/usr/bin/env python3
"""
개선된 네트워크 분석 대시보드 실행
"""

import streamlit as st
import sys
import os

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from streamlit_enhanced_network_page import create_enhanced_network_page

# 페이지 설정
st.set_page_config(
    page_title="🚀 개선된 경제 네트워크 분석",
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
</style>
""", unsafe_allow_html=True)

def main():
    """메인 함수"""
    
    # 헤더
    st.markdown("""
    # 🚀 개선된 경제 개념 네트워크 분석
    
    **기존 문제점 해결:**
    - ❌ 노드 수 부족 (7-21개) → ✅ 50+ 노드 생성 가능
    - ❌ 사용자 네트워크 무의미 → ✅ 경제 개념 기반 네트워크
    - ❌ 단순 동시 출현 → ✅ 경제적 인과관계 분석
    - ❌ 가독성 부족 → ✅ 카테고리별 색상 구분 및 인터랙티브 시각화
    """)
    
    st.markdown("---")
    
    # 개선된 네트워크 분석 페이지 실행
    create_enhanced_network_page()
    
    # 푸터
    st.markdown("---")
    st.markdown("""
    ### 📋 개선 사항 요약
    
    | 항목 | 기존 | 개선 후 |
    |------|------|---------|
    | **노드 수** | 7-21개 | 50-100개 |
    | **네트워크 유형** | 사용자 관계 | 경제 개념 관계 |
    | **관계 분석** | 단순 동시 출현 | 경제적 연관성 |
    | **시각화** | 기본 그래프 | 카테고리별 색상 + 크기 |
    | **인사이트** | 없음 | 자동 생성 |
    | **감정 분석** | 없음 | 개념별 감정 분석 |
    
    **🎯 핵심 개선 효과:**
    - **의미 있는 네트워크**: 경제 분석에 실용적인 인사이트 제공
    - **확장성**: 16개 경제 카테고리로 체계적 분류
    - **실시간 분석**: 다양한 데이터 소스 지원
    - **사용자 친화적**: 인터랙티브 필터링 및 탐색 기능
    """)

if __name__ == "__main__":
    main()
