#!/usr/bin/env python3
"""
아시아 시장 포함 통합 경제 뉴스 시스템 대시보드
모든 API (Yahoo Finance, Alpha Vantage, FRED, Reddit)와 아시아 시장을 활용한 종합 모니터링
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
import time
import threading
import queue
from typing import Dict, List, Any, Optional
import requests
from dotenv import load_dotenv
import logging

# 환경 변수 로드
load_dotenv()

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 아시아 시장 포함 종합 모니터링 시스템 import
from comprehensive_economic_monitor_with_asia_fixed import ComprehensiveEconomicMonitorWithAsia

# 페이지 설정
st.set_page_config(
    page_title="🌏 글로벌 경제 뉴스 시스템",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 전역 변수
if 'monitoring_active' not in st.session_state:
    st.session_state.monitoring_active = False
if 'comprehensive_data' not in st.session_state:
    st.session_state.comprehensive_data = {}
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'monitor_instance' not in st.session_state:
    st.session_state.monitor_instance = None

class GlobalDashboard:
    """글로벌 대시보드 클래스 (아시아 시장 포함)"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def initialize_monitor(self):
        """모니터링 시스템 초기화"""
        if st.session_state.monitor_instance is None:
            try:
                st.session_state.monitor_instance = ComprehensiveEconomicMonitorWithAsia()
                st.success("✅ 글로벌 종합 모니터링 시스템 초기화 완료")
                return True
            except Exception as e:
                st.error(f"❌ 모니터링 시스템 초기화 실패: {e}")
                return False
        return True
    
    async def run_comprehensive_monitoring(self):
        """종합 모니터링 실행"""
        if st.session_state.monitor_instance:
            try:
                data = await st.session_state.monitor_instance.run_comprehensive_monitoring()
                st.session_state.comprehensive_data = data
                st.session_state.last_update = datetime.now()
                return data
            except Exception as e:
                st.error(f"❌ 모니터링 실행 실패: {e}")
                return {}
        return {}
    
    def display_api_status(self):
        """API 상태 표시"""
        st.subheader("🔌 API 연결 상태")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Yahoo Finance (항상 사용 가능)
            st.metric("📊 Yahoo Finance", "🟢 연결됨", "글로벌 시장 데이터")
        
        with col2:
            # FRED API
            fred_key = os.getenv('FRED_API_KEY')
            if fred_key and fred_key != "demo":
                st.metric("📈 FRED API", "🟢 연결됨", "경제 지표")
            else:
                st.metric("📈 FRED API", "🟡 Demo 모드", "제한된 데이터")
        
        with col3:
            # Reddit API
            reddit_id = os.getenv('REDDIT_CLIENT_ID')
            reddit_secret = os.getenv('REDDIT_CLIENT_SECRET')
            if reddit_id and reddit_secret:
                st.metric("💬 Reddit API", "🟢 연결됨", "소셜 감정")
            else:
                st.metric("💬 Reddit API", "🔴 미연결", "API 키 필요")
        
        with col4:
            # Alpha Vantage API
            alpha_key = os.getenv('ALPHA_VANTAGE_API_KEY')
            if alpha_key:
                st.metric("🔍 Alpha Vantage", "🟢 연결됨", "고급 분석")
            else:
                st.metric("🔍 Alpha Vantage", "🔴 미연결", "API 키 필요")
    
    def display_global_market_overview(self, data: Dict[str, Any]):
        """글로벌 시장 개요 표시 (미국 + 아시아)"""
        st.subheader("🌍 글로벌 시장 현황")
        
        # 미국 시장 섹션
        st.markdown("### 🇺🇸 미국 시장")
        market_data = data.get('market_data', {})
        us_stocks = market_data.get('us_stocks', {})
        
        if us_stocks:
            # 주요 지수 표시
            major_indices = ['^GSPC', '^IXIC', '^DJI', '^VIX']
            cols = st.columns(len(major_indices))
            
            for i, symbol in enumerate(major_indices):
                if symbol in us_stocks:
                    stock_data = us_stocks[symbol]
                    with cols[i]:
                        name = stock_data.name if hasattr(stock_data, 'name') else symbol
                        price = stock_data.current_price if hasattr(stock_data, 'current_price') else 0
                        change = stock_data.change_percent if hasattr(stock_data, 'change_percent') else 0
                        
                        # 색상 결정
                        color = "normal"
                        if change > 0:
                            color = "inverse"
                        elif change < 0:
                            color = "off"
                        
                        st.metric(
                            label=name,
                            value=f"{price:.2f}",
                            delta=f"{change:+.2f}%",
                            delta_color=color
                        )
        
        # 아시아 시장 섹션
        st.markdown("### 🌏 아시아 시장")
        asian_data = data.get('asian_market_data', {})
        
        if asian_data and 'indices' in asian_data:
            self.display_asian_markets(asian_data)
        else:
            st.info("🌏 아시아 시장 데이터를 수집 중입니다...")
    
    def display_asian_markets(self, asian_data: Dict[str, Any]):
        """아시아 시장 데이터 표시"""
        indices = asian_data.get('indices', {})
        
        if indices:
            # 아시아 주요 지수 표시
            asian_indices = ['korea', 'japan', 'china', 'hongkong']
            cols = st.columns(len(asian_indices))
            
            market_names = {
                'korea': '🇰🇷 KOSPI',
                'japan': '🇯🇵 Nikkei',
                'china': '🇨🇳 Shanghai',
                'hongkong': '🇭🇰 Hang Seng'
            }
            
            for i, market in enumerate(asian_indices):
                if market in indices:
                    market_info = indices[market]
                    with cols[i]:
                        name = market_names.get(market, market)
                        price = market_info.get('current_price', 0)
                        change = market_info.get('change_percent', 0)
                        
                        # 색상 결정
                        color = "normal"
                        if change > 0:
                            color = "inverse"
                        elif change < 0:
                            color = "off"
                        
                        st.metric(
                            label=name,
                            value=f"{price:.2f}",
                            delta=f"{change:+.2f}%",
                            delta_color=color
                        )
            
            # 아시아 시장 히트맵
            self.create_asian_heatmap(indices)
    
    def create_asian_heatmap(self, indices: Dict[str, Any]):
        """아시아 시장 히트맵 생성"""
        try:
            # 데이터 준비
            markets = []
            changes = []
            names = []
            
            market_names = {
                'korea': '🇰🇷 한국',
                'japan': '🇯🇵 일본', 
                'china': '🇨🇳 중국',
                'hongkong': '🇭🇰 홍콩',
                'taiwan': '🇹🇼 대만',
                'singapore': '🇸🇬 싱가포르',
                'india': '🇮🇳 인도'
            }
            
            for market, data in indices.items():
                markets.append(market)
                change = data.get('change_percent', 0)
                changes.append(change)
                name = market_names.get(market, market)
                names.append(name)
            
            if len(markets) > 0:
                # 히트맵 생성
                fig = go.Figure(data=go.Scatter(
                    x=markets,
                    y=[1] * len(markets),
                    mode='markers',
                    marker=dict(
                        size=[abs(change) * 10 + 30 for change in changes],
                        color=changes,
                        colorscale='RdYlGn',
                        showscale=True,
                        colorbar=dict(title="변화율 (%)")
                    ),
                    text=[f"{name}<br>{change:+.2f}%" for name, change in zip(names, changes)],
                    hovertemplate='%{text}<extra></extra>'
                ))
                
                fig.update_layout(
                    title="🌏 아시아 시장 변화율 히트맵",
                    xaxis_title="시장",
                    yaxis=dict(visible=False),
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        except Exception as e:
            st.error(f"아시아 히트맵 생성 실패: {e}")
    
    def display_economic_indicators(self, data: Dict[str, Any]):
        """경제 지표 표시"""
        st.subheader("📈 경제 지표")
        
        economic_data = data.get('economic_indicators', {})
        
        if economic_data:
            cols = st.columns(min(len(economic_data), 4))
            
            indicator_names = {
                'FEDFUNDS': '연방기금금리',
                'GS10': '10년 국채',
                'CPIAUCSL': '소비자물가지수',
                'UNRATE': '실업률',
                'GDP': 'GDP'
            }
            
            for i, (indicator, values) in enumerate(economic_data.items()):
                if i < 4:  # 최대 4개만 표시
                    with cols[i]:
                        name = indicator_names.get(indicator, indicator)
                        if values and len(values) > 0:
                            latest_value = values[-1].get('value', 0)
                            st.metric(
                                label=name,
                                value=f"{latest_value:.2f}",
                                help=f"최신 {indicator} 데이터"
                            )
            
            # 경제 지표 차트
            self.create_economic_chart(economic_data)
        else:
            st.info("📊 경제 지표 데이터를 수집 중입니다...")
    
    def create_economic_chart(self, economic_data: Dict[str, Any]):
        """경제 지표 차트 생성"""
        try:
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=list(economic_data.keys())[:4],
                vertical_spacing=0.1
            )
            
            positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
            
            for i, (indicator, values) in enumerate(economic_data.items()):
                if i >= 4:
                    break
                
                if values:
                    dates = [item['date'] for item in values]
                    vals = [item['value'] for item in values]
                    
                    row, col = positions[i]
                    fig.add_trace(
                        go.Scatter(x=dates, y=vals, name=indicator, mode='lines+markers'),
                        row=row, col=col
                    )
            
            fig.update_layout(
                title="📊 경제 지표 추이",
                height=500,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        except Exception as e:
            st.error(f"경제 지표 차트 생성 실패: {e}")

def main():
    """메인 함수"""
    st.title("🌏 글로벌 경제 뉴스 시스템")
    st.markdown("**미국 + 아시아 시장을 포함한 종합 경제 데이터 모니터링**")
    st.markdown("---")
    
    dashboard = GlobalDashboard()
    
    # 사이드바
    with st.sidebar:
        st.header("🎛️ 글로벌 제어판")
        
        # API 상태 표시
        dashboard.display_api_status()
        
        st.markdown("---")
        
        # 모니터링 제어
        if st.button("🚀 글로벌 모니터링 시작", type="primary"):
            if dashboard.initialize_monitor():
                with st.spinner("🌍 글로벌 데이터 수집 중... (약 3분 소요)"):
                    # 비동기 함수를 동기적으로 실행
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        data = loop.run_until_complete(dashboard.run_comprehensive_monitoring())
                        st.success("✅ 글로벌 모니터링 완료!")
                        st.balloons()
                    finally:
                        loop.close()
        
        if st.button("🔄 데이터 새로고침"):
            st.rerun()
        
        # 마지막 업데이트 시간
        if st.session_state.last_update:
            st.info(f"🕐 마지막 업데이트: {st.session_state.last_update.strftime('%H:%M:%S')}")
        
        # 시스템 정보
        st.markdown("---")
        st.markdown("### 📋 시스템 정보")
        st.markdown("""
        **데이터 소스:**
        - 📊 Yahoo Finance (실시간)
        - 📈 FRED API (경제지표)
        - 💬 Reddit API (소셜감정)
        - 🔍 Alpha Vantage (고급분석)
        - 🌏 아시아 시장 (7개국)
        
        **주요 기능:**
        - 글로벌 시장 모니터링
        - 아시아 시장 추적
        - 경제 지표 분석
        - 소셜 감정 분석
        - 이벤트 자동 감지
        - Slack 알림 전송
        """)
    
    # 메인 콘텐츠
    if st.session_state.comprehensive_data:
        data = st.session_state.comprehensive_data
        
        # 탭 생성
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "🌍 글로벌 시장", "🌏 아시아 상세", "📈 경제 지표", "💬 소셜 감정", "🚨 이벤트", "📋 통계"
        ])
        
        with tab1:
            dashboard.display_global_market_overview(data)
        
        with tab2:
            # 아시아 시장 상세 정보는 다음 파트에서 구현
            st.info("🌏 아시아 시장 상세 정보 (구현 중)")
        
        with tab3:
            dashboard.display_economic_indicators(data)
        
        with tab4:
            st.info("💬 소셜 감정 분석 (구현 중)")
        
        with tab5:
            st.info("🚨 이벤트 감지 (구현 중)")
        
        with tab6:
            st.info("📋 통계 정보 (구현 중)")
    
    else:
        st.info("🚀 '글로벌 모니터링 시작' 버튼을 클릭하여 데이터 수집을 시작하세요.")
        
        # 시작 가이드
        st.markdown("""
        ## 🎯 글로벌 시스템 기능
        
        ### 🌍 **글로벌 시장 커버리지**
        - **🇺🇸 미국**: S&P 500, NASDAQ, Dow Jones, VIX
        - **🇰🇷 한국**: KOSPI, 삼성전자, SK하이닉스 등
        - **🇯🇵 일본**: Nikkei 225, 도요타, 소프트뱅크 등
        - **🇨🇳 중국**: Shanghai Composite, 알리바바, 텐센트 등
        - **🇭🇰 홍콩**: Hang Seng Index
        - **🇹🇼 대만**: Taiwan Weighted, TSMC 등
        - **🇸🇬 싱가포르**: Straits Times Index
        - **🇮🇳 인도**: BSE Sensex
        
        ### 📊 **종합 데이터 분석**
        - **29개 FRED 경제 지표**: 금리, 인플레이션, 고용 등
        - **8개 Reddit 서브레딧**: 실시간 투자 심리 분석
        - **Alpha Vantage**: 시장 상태, 상위/하위 종목
        - **64개 뉴스 기사**: 실시간 경제 뉴스 수집
        
        ### 🚨 **글로벌 이벤트 감지**
        - 미국/아시아 시장 급변동 감지
        - 지역 간 상관관계 분석
        - 통화 변동 모니터링
        - 글로벌 리스크 평가
        
        ### 📱 **실시간 알림**
        - 지역별 이벤트 구분 (🇺🇸/🌏)
        - 심각도별 알림 분류
        - 시차 고려 알림 시스템
        """)

if __name__ == "__main__":
    main()
