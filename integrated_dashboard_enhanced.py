#!/usr/bin/env python3
"""
업그레이드된 통합 경제 뉴스 시스템 대시보드
모든 API (Yahoo Finance, Alpha Vantage, FRED, Reddit)를 활용한 종합 모니터링
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

# 새로운 종합 모니터링 시스템 import
from comprehensive_economic_monitor_final import ComprehensiveEconomicMonitor

# 페이지 설정
st.set_page_config(
    page_title="🤖 종합 경제 뉴스 시스템",
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

class EnhancedDashboard:
    """업그레이드된 대시보드 클래스"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def initialize_monitor(self):
        """모니터링 시스템 초기화"""
        if st.session_state.monitor_instance is None:
            try:
                st.session_state.monitor_instance = ComprehensiveEconomicMonitor()
                st.success("✅ 종합 모니터링 시스템 초기화 완료")
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
            st.metric("📊 Yahoo Finance", "🟢 연결됨", "실시간 시장 데이터")
        
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
    
    def display_market_overview(self, data: Dict[str, Any]):
        """시장 개요 표시"""
        st.subheader("📊 시장 현황")
        
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
        
        # 시장 히트맵
        if us_stocks:
            self.create_market_heatmap(us_stocks)
    
    def create_market_heatmap(self, stocks_data: Dict[str, Any]):
        """시장 히트맵 생성"""
        try:
            # 데이터 준비
            symbols = []
            changes = []
            names = []
            
            for symbol, data in stocks_data.items():
                if symbol.startswith('^'):  # 지수 제외
                    continue
                symbols.append(symbol)
                change = data.change_percent if hasattr(data, 'change_percent') else 0
                changes.append(change)
                name = data.name if hasattr(data, 'name') else symbol
                names.append(name)
            
            if len(symbols) > 0:
                # 히트맵 생성
                fig = go.Figure(data=go.Scatter(
                    x=symbols,
                    y=[1] * len(symbols),
                    mode='markers',
                    marker=dict(
                        size=[abs(change) * 10 + 20 for change in changes],
                        color=changes,
                        colorscale='RdYlGn',
                        showscale=True,
                        colorbar=dict(title="변화율 (%)")
                    ),
                    text=[f"{name}<br>{change:+.2f}%" for name, change in zip(names, changes)],
                    hovertemplate='%{text}<extra></extra>'
                ))
                
                fig.update_layout(
                    title="📈 주식 변화율 히트맵",
                    xaxis_title="종목",
                    yaxis=dict(visible=False),
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        except Exception as e:
            st.error(f"히트맵 생성 실패: {e}")
    
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
    
    def display_social_sentiment(self, data: Dict[str, Any]):
        """소셜 감정 분석 표시"""
        st.subheader("💬 소셜 미디어 감정 분석")
        
        social_data = data.get('social_sentiment', {})
        
        if social_data:
            # 감정 점수 표시
            cols = st.columns(len(social_data))
            
            for i, (platform, sentiment_info) in enumerate(social_data.items()):
                with cols[i]:
                    score = sentiment_info.get('sentiment_score', 0)
                    post_count = sentiment_info.get('post_count', 0)
                    
                    # 감정 상태 결정
                    if score > 0.5:
                        emoji = "😊"
                        status = "긍정적"
                        color = "normal"
                    elif score < -0.5:
                        emoji = "😟"
                        status = "부정적"
                        color = "inverse"
                    else:
                        emoji = "😐"
                        status = "중립적"
                        color = "off"
                    
                    st.metric(
                        label=f"{emoji} r/{platform}",
                        value=status,
                        delta=f"{score:.2f} ({post_count}개 게시물)",
                        delta_color=color
                    )
            
            # 감정 추이 차트
            self.create_sentiment_chart(social_data)
        else:
            st.info("💬 소셜 미디어 데이터를 수집 중입니다...")
    
    def create_sentiment_chart(self, social_data: Dict[str, Any]):
        """감정 분석 차트 생성"""
        try:
            platforms = list(social_data.keys())
            scores = [data.get('sentiment_score', 0) for data in social_data.values()]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=platforms,
                    y=scores,
                    marker_color=['green' if s > 0 else 'red' if s < 0 else 'gray' for s in scores],
                    text=[f"{s:.2f}" for s in scores],
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                title="📊 플랫폼별 감정 점수",
                xaxis_title="플랫폼",
                yaxis_title="감정 점수",
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        except Exception as e:
            st.error(f"감정 차트 생성 실패: {e}")
    
    def display_detected_events(self, data: Dict[str, Any]):
        """감지된 이벤트 표시"""
        st.subheader("🚨 감지된 이벤트")
        
        events = data.get('detected_events', [])
        
        if events:
            for event in events[-10:]:  # 최근 10개만 표시
                severity = event.get('severity', 0)
                symbol = event.get('symbol', 'Unknown')
                event_type = event.get('event_type', 'Unknown')
                description = event.get('description', 'No description')
                
                # 심각도에 따른 색상
                if severity > 0.8:
                    alert_type = "error"
                elif severity > 0.6:
                    alert_type = "warning"
                else:
                    alert_type = "info"
                
                with st.container():
                    if alert_type == "error":
                        st.error(f"🚨 **{symbol}** - {event_type}: {description}")
                    elif alert_type == "warning":
                        st.warning(f"⚠️ **{symbol}** - {event_type}: {description}")
                    else:
                        st.info(f"ℹ️ **{symbol}** - {event_type}: {description}")
        else:
            st.info("🔍 현재 감지된 이벤트가 없습니다.")
    
    def display_summary_stats(self, data: Dict[str, Any]):
        """요약 통계 표시"""
        st.subheader("📊 수집 통계")
        
        summary = data.get('summary', {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📈 시장 종목", summary.get('market_symbols', 0))
        
        with col2:
            st.metric("📊 경제 지표", summary.get('economic_indicators', 0))
        
        with col3:
            st.metric("💬 소셜 플랫폼", summary.get('social_platforms', 0))
        
        with col4:
            st.metric("🚨 새 이벤트", summary.get('new_events', 0))
        
        # 처리 시간
        processing_time = summary.get('processing_time', 0)
        st.metric("⏱️ 처리 시간", f"{processing_time:.2f}초")
        
        # 추가 통계 정보
        market_data = data.get('market_data', {})
        if market_data:
            st.subheader("📈 데이터 소스별 통계")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                fred_data = market_data.get('fred_data', {})
                if fred_data:
                    st.metric("🏛️ FRED 지표", len(fred_data.get('indicators', {})))
            
            with col2:
                news_data = market_data.get('news_data', {})
                if news_data:
                    st.metric("📰 뉴스 기사", news_data.get('total_articles', 0))
            
            with col3:
                alpha_data = market_data.get('alpha_vantage', {})
                if alpha_data:
                    st.metric("🔍 Alpha Vantage", len(alpha_data))

def main():
    """메인 함수"""
    st.title("🤖 종합 경제 뉴스 시스템")
    st.markdown("**모든 API를 활용한 통합 경제 데이터 모니터링**")
    st.markdown("---")
    
    dashboard = EnhancedDashboard()
    
    # 사이드바
    with st.sidebar:
        st.header("🎛️ 제어판")
        
        # API 상태 표시
        dashboard.display_api_status()
        
        st.markdown("---")
        
        # 모니터링 제어
        if st.button("🚀 종합 모니터링 시작", type="primary"):
            if dashboard.initialize_monitor():
                with st.spinner("📊 종합 데이터 수집 중... (약 2분 소요)"):
                    # 비동기 함수를 동기적으로 실행
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        data = loop.run_until_complete(dashboard.run_comprehensive_monitoring())
                        st.success("✅ 종합 모니터링 완료!")
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
        
        **주요 기능:**
        - 실시간 시장 모니터링
        - 경제 지표 추적
        - 소셜 감정 분석
        - 이벤트 자동 감지
        - Slack 알림 전송
        """)
    
    # 메인 콘텐츠
    if st.session_state.comprehensive_data:
        data = st.session_state.comprehensive_data
        
        # 탭 생성
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 시장 현황", "📈 경제 지표", "💬 소셜 감정", "🚨 이벤트", "📋 통계"
        ])
        
        with tab1:
            dashboard.display_market_overview(data)
        
        with tab2:
            dashboard.display_economic_indicators(data)
        
        with tab3:
            dashboard.display_social_sentiment(data)
        
        with tab4:
            dashboard.display_detected_events(data)
        
        with tab5:
            dashboard.display_summary_stats(data)
    
    else:
        st.info("🚀 '종합 모니터링 시작' 버튼을 클릭하여 데이터 수집을 시작하세요.")
        
        # 시작 가이드
        st.markdown("""
        ## 🎯 업그레이드된 시스템 기능
        
        ### 📊 **다중 데이터 소스 통합**
        - **Yahoo Finance**: 실시간 주식, 지수, 원자재, 통화 데이터
        - **FRED API**: 29개 연방준비제도 경제 지표 (금리, 인플레이션, 고용 등)
        - **Reddit API**: 8개 경제 서브레딧 실시간 감정 분석
        - **Alpha Vantage**: 시장 상태, 상위/하위 종목, 뉴스 감정 분석
        
        ### 🚨 **고도화된 이벤트 감지**
        - 가격 급변동 감지 (3% 이상)
        - 거래량 이상 패턴 (평균 대비 2배 이상)
        - 시장 변동성 모니터링 (VIX 25 이상)
        - 소셜 감정 급변 추적
        - 기술적 지표 돌파 감지
        
        ### 📱 **실시간 Slack 알림**
        - 심각도별 알림 분류 (0.6 이상 자동 전송)
        - 이벤트 상세 정보 제공
        - 시장 요약 리포트
        - 시스템 상태 모니터링
        
        ### 🤖 **AI 기사 생성 시스템**
        - 감지된 이벤트 기반 자동 기사 작성
        - 5개 전문 에이전트 협업
        - 품질 검수 및 최적화
        - 관련 이미지 및 광고 추천
        
        ### 📈 **실시간 데이터 현황**
        - **시장 데이터**: 15+ 주요 지수 및 종목
        - **경제 지표**: 29개 FRED 지표
        - **소셜 데이터**: 8개 Reddit 서브레딧
        - **뉴스 데이터**: 실시간 경제 뉴스 수집
        """)

if __name__ == "__main__":
    main()
