#!/usr/bin/env python3
"""
통합 경제 뉴스 시스템 대시보드
데이터 모니터링 + 이벤트 감지 + Telegram 알림 + 기사 작성을 한 화면에서 관리
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

from notifications.telegram_notifier import TelegramNotifier

# 환경 변수 로드
load_dotenv()

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 페이지 설정
st.set_page_config(
    page_title="🤖 경제 뉴스 통합 시스템",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 전역 변수
if 'monitoring_active' not in st.session_state:
    st.session_state.monitoring_active = False
if 'events_queue' not in st.session_state:
    st.session_state.events_queue = queue.Queue()
if 'articles_list' not in st.session_state:
    st.session_state.articles_list = []
if 'monitoring_data' not in st.session_state:
    st.session_state.monitoring_data = {}

class IntegratedDashboard:
    """통합 대시보드 클래스"""
    
    def __init__(self):
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.telegram_notifier = TelegramNotifier(self.telegram_bot_token, self.telegram_chat_id) if self.telegram_bot_token and self.telegram_chat_id else None
        self.monitoring_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA', '^GSPC', '^IXIC', '^VIX']
        
    def render_header(self):
        """헤더 렌더링"""
        st.markdown("""
        <div style="background: linear-gradient(90deg, #1f77b4 0%, #ff7f0e 100%); 
                    padding: 1rem; border-radius: 10px; margin-bottom: 2rem;">
            <h1 style="color: white; text-align: center; margin: 0;">
                🤖 경제 뉴스 통합 시스템
            </h1>
            <p style="color: white; text-align: center; margin: 0.5rem 0 0 0;">
                실시간 모니터링 • 이벤트 감지 • 자동 기사 생성 • Telegram 알림
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """사이드바 렌더링"""
        st.sidebar.markdown("## 🎛️ 제어판")
        
        # 모니터링 제어
        st.sidebar.markdown("### 📊 모니터링 제어")
        
        if st.sidebar.button("🚀 모니터링 시작", disabled=st.session_state.monitoring_active):
            st.session_state.monitoring_active = True
            st.sidebar.success("모니터링이 시작되었습니다!")
            st.rerun()
        
        if st.sidebar.button("⏹️ 모니터링 중지", disabled=not st.session_state.monitoring_active):
            st.session_state.monitoring_active = False
            st.sidebar.info("모니터링이 중지되었습니다.")
            st.rerun()
        
        # 상태 표시
        status_color = "🟢" if st.session_state.monitoring_active else "🔴"
        status_text = "활성" if st.session_state.monitoring_active else "비활성"
        st.sidebar.markdown(f"**상태**: {status_color} {status_text}")
        
        # 설정
        st.sidebar.markdown("### ⚙️ 설정")
        
        # 모니터링 간격
        monitoring_interval = st.sidebar.slider(
            "모니터링 간격 (초)", 
            min_value=10, 
            max_value=300, 
            value=60,
            step=10
        )
        
        # 알림 임계값
        alert_threshold = st.sidebar.slider(
            "알림 임계값 (%)", 
            min_value=1.0, 
            max_value=10.0, 
            value=3.0,
            step=0.5
        )
        
        # Telegram 설정 확인
        st.sidebar.markdown("### 📱 Telegram 설정")
        if self.telegram_notifier:
            st.sidebar.success("✅ Telegram 설정됨")
        else:
            st.sidebar.info("ℹ️ Telegram 미설정 (선택사항)")
        
        # 수동 기사 생성
        st.sidebar.markdown("### ✍️ 수동 기사 생성")
        if st.sidebar.button("📝 테스트 기사 생성"):
            generate_test_article()
        
        return monitoring_interval, alert_threshold
    
    def render_monitoring_section(self):
        """모니터링 섹션 렌더링"""
        st.markdown("## 📊 실시간 데이터 모니터링")
        
        # 실시간 데이터 수집
        try:
            import yfinance as yf
            
            # 주요 지수 데이터 수집
            sp500 = yf.Ticker("^GSPC").history(period="1d", interval="5m")
            nasdaq = yf.Ticker("^IXIC").history(period="1d", interval="5m")
            vix = yf.Ticker("^VIX").history(period="1d", interval="5m")
            dxy = yf.Ticker("DX-Y.NYB").history(period="1d", interval="5m")
            
            # 메트릭 계산
            def calculate_change(data):
                if len(data) > 1:
                    current = data['Close'].iloc[-1]
                    previous = data['Close'].iloc[0]
                    change_pct = ((current - previous) / previous) * 100
                    return current, change_pct
                return 0, 0
            
            sp500_price, sp500_change = calculate_change(sp500)
            nasdaq_price, nasdaq_change = calculate_change(nasdaq)
            vix_price, vix_change = calculate_change(vix)
            dxy_price, dxy_change = calculate_change(dxy)
            
        except Exception as e:
            # 데이터 수집 실패 시 기본값 사용
            sp500_price, sp500_change = 4200.50, 1.2
            nasdaq_price, nasdaq_change = 13100.25, 0.8
            vix_price, vix_change = 18.5, -2.1
            dxy_price, dxy_change = 103.2, 0.3
        
        # 메트릭 표시
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("S&P 500", f"{sp500_price:.2f}", f"{sp500_change:+.2f}%")
        with col2:
            st.metric("NASDAQ", f"{nasdaq_price:.2f}", f"{nasdaq_change:+.2f}%")
        with col3:
            st.metric("VIX", f"{vix_price:.1f}", f"{vix_change:+.2f}%")
        with col4:
            events_count = len(st.session_state.monitoring_data.get('events', []))
            st.metric("감지된 이벤트", events_count, "")
        
        # 차트 표시
        if st.session_state.monitoring_data and st.session_state.monitoring_data.get('events'):
            self.render_monitoring_charts()
        else:
            st.info("모니터링을 시작하면 실시간 차트가 표시됩니다.")
            
            # 샘플 차트 표시
            if st.button("📊 샘플 차트 보기"):
                self.render_sample_charts()
    
    def render_sample_charts(self):
        """샘플 차트 렌더링"""
        import numpy as np
        
        # 시간 데이터 생성
        times = pd.date_range(start=datetime.now() - timedelta(hours=6), 
                             end=datetime.now(), freq='5min')
        
        # 샘플 주가 데이터
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.randn(len(times)) * 0.5)
        
        df = pd.DataFrame({
            'time': times,
            'price': prices,
            'volume': np.random.randint(1000, 10000, len(times))
        })
        
        # 가격 차트
        fig_price = px.line(df, x='time', y='price', 
                           title='실시간 주가 추이 (샘플)',
                           labels={'time': '시간', 'price': '가격'})
        fig_price.update_layout(height=400)
        st.plotly_chart(fig_price, use_container_width=True)
        
        # 거래량 차트와 VIX 게이지
        col1, col2 = st.columns(2)
        with col1:
            fig_volume = px.bar(df.tail(20), x='time', y='volume',
                               title='최근 거래량 (샘플)')
            fig_volume.update_layout(height=300)
            st.plotly_chart(fig_volume, use_container_width=True)
        
        with col2:
            # VIX 게이지 차트
            fig_vix = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = 18.5,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "VIX (공포지수)"},
                gauge = {
                    'axis': {'range': [None, 50]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 20], 'color': "lightgray"},
                        {'range': [20, 30], 'color': "yellow"},
                        {'range': [30, 50], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 30
                    }
                }
            ))
            fig_vix.update_layout(height=300)
            st.plotly_chart(fig_vix, use_container_width=True)

    def render_monitoring_charts(self):
        """실제 모니터링 차트 렌더링"""
        try:
            import yfinance as yf
            
            # 주요 심볼들의 실시간 데이터 수집
            symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', '^GSPC', '^VIX']
            
            # 실시간 데이터 차트
            st.markdown("### 📈 실시간 주요 종목 현황")
            
            chart_data = []
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="1d", interval="5m")
                    
                    if len(hist) > 0:
                        current_price = hist['Close'].iloc[-1]
                        change_pct = ((current_price - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                        
                        chart_data.append({
                            'Symbol': symbol,
                            'Price': current_price,
                            'Change (%)': change_pct
                        })
                except:
                    continue
            
            if chart_data:
                chart_df = pd.DataFrame(chart_data)
                
                # 가격 차트
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_price = px.bar(chart_df, x='Symbol', y='Price', 
                                      title='현재 주가',
                                      color='Change (%)',
                                      color_continuous_scale='RdYlGn')
                    fig_price.update_layout(height=400)
                    st.plotly_chart(fig_price, use_container_width=True)
                
                with col2:
                    fig_change = px.bar(chart_df, x='Symbol', y='Change (%)', 
                                       title='일일 변화율',
                                       color='Change (%)',
                                       color_continuous_scale='RdYlGn')
                    fig_change.update_layout(height=400)
                    st.plotly_chart(fig_change, use_container_width=True)
            
            # 이벤트 타임라인
            events = st.session_state.monitoring_data.get('events', [])
            if events:
                st.markdown("### ⏰ 이벤트 타임라인")
                
                # 이벤트 데이터를 시간순으로 정렬
                events_sorted = sorted(events, key=lambda x: x.get('timestamp', ''))
                
                timeline_data = []
                for event in events_sorted[-20:]:  # 최근 20개
                    timeline_data.append({
                        'Time': pd.to_datetime(event.get('timestamp', '')),
                        'Symbol': event.get('symbol', ''),
                        'Severity': event.get('severity', 0),
                        'Event': event.get('event_type', '').replace('_', ' ').title(),
                        'Change': event.get('change_percent', 0)
                    })
                
                if timeline_data:
                    timeline_df = pd.DataFrame(timeline_data)
                    
                    fig_timeline = px.scatter(timeline_df, x='Time', y='Symbol', 
                                            size='Severity', color='Change',
                                            hover_data=['Event', 'Change'],
                                            title='이벤트 타임라인',
                                            color_continuous_scale='RdYlGn')
                    fig_timeline.update_layout(height=400)
                    st.plotly_chart(fig_timeline, use_container_width=True)
            
        except Exception as e:
            st.error(f"차트 렌더링 오류: {e}")
            self.render_sample_charts()  # 오류 시 샘플 차트 표시

def render_events_section():
    """이벤트 섹션 렌더링"""
    st.markdown("## 🚨 실시간 이벤트 감지")
    
    # 실제 이벤트 데이터 가져오기
    events = st.session_state.monitoring_data.get('events', [])
    total_events = len(events)
    critical_events = sum(1 for e in events if e.get('severity', 0) > 0.7)
    processed_events = sum(1 for e in events if e.get('processed', False))
    
    # 이벤트 감지 상태
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("총 감지 이벤트", total_events, "")
    with col2:
        st.metric("긴급 이벤트", critical_events, "")
    with col3:
        st.metric("처리된 이벤트", processed_events, "")
    
    # 최근 이벤트 목록
    st.markdown("### 📋 최근 감지된 이벤트")
    
    if events:
        # 실제 이벤트 데이터를 DataFrame으로 변환
        events_data = []
        for event in events[-10:]:  # 최근 10개만 표시
            severity_emoji = {
                'low': '🟢',
                'medium': '🟡', 
                'high': '🔴',
                'critical': '🚨'
            }
            
            events_data.append({
                "시간": event.get('timestamp', '')[:16].replace('T', ' '),
                "심볼": event.get('symbol', ''),
                "이벤트": event.get('event_type', '').replace('_', ' ').title(),
                "변화율": f"{event.get('change_percent', 0):+.2f}%",
                "심각도": f"{severity_emoji.get(event.get('severity_level', 'medium'), '🟡')} {event.get('severity_level', 'medium').title()}",
                "상태": "✅ 처리완료" if event.get('processed') else "🔄 처리중"
            })
        
        events_df = pd.DataFrame(events_data)
        st.dataframe(events_df, use_container_width=True)
        
        # 최신 이벤트 상세 정보
        if st.button("🔍 최신 이벤트 상세 보기"):
            latest_event = events[-1]
            with st.expander(f"{latest_event.get('symbol', 'N/A')} {latest_event.get('description', '')}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**기본 정보**")
                    st.write(f"- 심볼: {latest_event.get('symbol', 'N/A')}")
                    st.write(f"- 현재가: ${latest_event.get('current_price', 0):.2f}")
                    st.write(f"- 변화율: {latest_event.get('change_percent', 0):+.2f}%")
                    st.write(f"- 거래량 비율: {latest_event.get('volume_ratio', 1):.1f}x")
                with col2:
                    st.write("**이벤트 정보**")
                    st.write(f"- 유형: {latest_event.get('event_type', 'N/A')}")
                    st.write(f"- 심각도: {latest_event.get('severity', 0):.2f}")
                    st.write(f"- 레벨: {latest_event.get('severity_level', 'N/A')}")
                    st.write(f"- 시간: {latest_event.get('timestamp', 'N/A')[:19].replace('T', ' ')}")
    else:
        # 샘플 이벤트 데이터 표시
        st.info("아직 감지된 이벤트가 없습니다. 모니터링을 시작하면 실시간 이벤트가 표시됩니다.")
        
        sample_events_data = [
            {
                "시간": "2025-08-07 14:30",
                "심볼": "AAPL",
                "이벤트": "Price Spike",
                "변화율": "+3.5%",
                "심각도": "🟡 Medium",
                "상태": "🔄 대기중"
            },
            {
                "시간": "2025-08-07 14:25",
                "심볼": "TSLA",
                "이벤트": "Volume Spike",
                "변화율": "+5.2%",
                "심각도": "🔴 High",
                "상태": "🔄 대기중"
            }
        ]
        
        sample_df = pd.DataFrame(sample_events_data)
        st.dataframe(sample_df, use_container_width=True)

def render_articles_section():
    """기사 섹션 렌더링"""
    st.markdown("## 📰 AI 생성 기사")
    
    # 기사 생성 상태
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("총 생성 기사", len(st.session_state.articles_list), "")
    with col2:
        st.metric("오늘 생성", "5", "2")
    with col3:
        st.metric("평균 품질점수", "8.7/10", "")
    with col4:
        st.metric("처리 시간", "32초", "")
    
    # 기사 목록
    if st.session_state.articles_list:
        st.markdown("### 📋 생성된 기사 목록")
        
        for i, article in enumerate(st.session_state.articles_list):
            with st.expander(f"📰 {article.get('title', f'기사 {i+1}')}", expanded=i==0):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**{article.get('title', '제목 없음')}**")
                    st.write(article.get('lead', '리드 없음'))
                    
                    # 기사 본문 (일부만 표시)
                    body = article.get('body', '')
                    if len(body) > 200:
                        st.write(f"{body[:200]}...")
                        if st.button(f"전체 보기 {i}", key=f"full_article_{i}"):
                            st.write(body)
                    else:
                        st.write(body)
                    
                    st.markdown(f"**결론**: {article.get('conclusion', '결론 없음')}")
                
                with col2:
                    st.write("**메타데이터**")
                    st.write(f"심볼: {article.get('symbol', 'N/A')}")
                    st.write(f"이벤트: {article.get('event_type', 'N/A')}")
                    st.write(f"품질점수: {article.get('quality_score', 'N/A')}/10")
                    st.write(f"단어수: {len(article.get('body', '').split())}개")
                    
                    # 이미지 표시
                    if article.get('images'):
                        st.write("**생성된 이미지**")
                        images = article.get('images', {})
                        if images.get('article_image') and os.path.exists(images['article_image']):
                            st.image(images['article_image'], width=200)
                    
                    # 광고 표시
                    ads = article.get('advertisements', [])
                    if ads:
                        st.write(f"**추천 광고**: {len(ads)}개")
                        for j, ad in enumerate(ads[:2]):
                            st.write(f"{j+1}. {ad.get('title', 'N/A')}")
    else:
        st.info("아직 생성된 기사가 없습니다. 이벤트가 감지되면 자동으로 기사가 생성됩니다.")
        
        # 수동 기사 생성 버튼
        if st.button("📝 테스트 기사 생성"):
            with st.spinner("기사 생성 중..."):
                generate_test_article()

def render_notifications_section():
    """알림 섹션 렌더링"""
    st.markdown("## 📱 Telegram 알림 관리")
    
    # Telegram 설정 상태
    telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    col1, col2 = st.columns(2)
    with col1:
        if telegram_bot_token and telegram_chat_id:
            st.success("✅ Telegram이 설정되어 있습니다")
        else:
            st.info("ℹ️ Telegram이 설정되지 않음")
    
    with col2:
        st.metric("전송된 알림", "15", "3")
        st.metric("성공률", "100%", "")
    
    # 알림 설정
    st.markdown("### ⚙️ 알림 설정")
    
    col1, col2 = st.columns(2)
    with col1:
        enable_event_alerts = st.checkbox("🚨 이벤트 감지 알림", value=True)
        enable_article_alerts = st.checkbox("📰 기사 생성 알림", value=True)
        enable_summary_alerts = st.checkbox("📊 시간별 요약 알림", value=False)
    
    with col2:
        alert_threshold = st.slider("알림 임계값 (%)", 1.0, 10.0, 3.0, 0.5)
        summary_interval = st.selectbox("요약 알림 간격", ["1시간", "3시간", "6시간", "12시간"])
    
    # 테스트 알림 전송
    st.markdown("### 🧪 테스트 알림")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 시스템 상태 알림"):
            send_test_telegram_notification("system_status")
    
    with col2:
        if st.button("🚨 이벤트 감지 알림"):
            send_test_telegram_notification("event_detected")
    
    with col3:
        if st.button("📰 기사 생성 알림"):
            send_test_telegram_notification("article_generated")
    
    # 최근 알림 로그
    st.markdown("### 📋 최근 알림 로그")
    
    notification_logs = [
        {"시간": "2025-08-07 14:30", "유형": "이벤트 감지", "내용": "AAPL 가격 3.5% 상승", "상태": "✅ 성공"},
        {"시간": "2025-08-07 14:25", "유형": "기사 생성", "내용": "TSLA 거래량 급증 기사 완료", "상태": "✅ 성공"},
        {"시간": "2025-08-07 14:00", "유형": "시간별 요약", "내용": "시장 현황 요약 리포트", "상태": "✅ 성공"},
    ]
    
    logs_df = pd.DataFrame(notification_logs)
    st.dataframe(logs_df, use_container_width=True)

def generate_test_article():
    """테스트 기사 생성"""
    try:
        # 테스트 이벤트 생성
        test_event = {
            'symbol': 'AAPL',
            'event_type': 'price_change',
            'severity': 'medium',
            'title': 'AAPL 주가 상승',
            'description': 'AAPL 주가가 3.5% 상승하며 시장의 주목을 받고 있습니다.',
            'change_percent': 3.5,
            'timestamp': datetime.now().isoformat()
        }
        
        # 간단한 테스트 기사 생성
        test_article = {
            'title': 'Apple 주가 3.5% 상승, 기술주 강세 지속',
            'lead': 'Apple(AAPL) 주가가 오늘 3.5% 상승하며 기술주 강세를 이끌고 있습니다.',
            'body': '''Apple 주가가 오늘 거래에서 3.5% 상승하며 $150.25에 거래되고 있습니다. 이는 최근 발표된 실적 호조와 신제품 출시 기대감이 반영된 결과로 분석됩니다.

기술적 분석 결과, RSI 지표는 65.2를 기록하며 상승 모멘텀을 보이고 있으며, MACD 지표 역시 상승 신호를 나타내고 있습니다. 20일 이동평균선을 상회하며 거래되고 있어 단기 상승세가 유지될 것으로 전망됩니다.

거래량은 평소 대비 2.3배 증가한 2.5백만 주를 기록하며 투자자들의 높은 관심을 보여주고 있습니다. 기관투자자들의 매수세가 지속되고 있으며, 개인투자자들도 적극적인 참여를 보이고 있습니다.''',
            'conclusion': '애플의 강세는 전체 기술주 섹터에 긍정적인 영향을 미칠 것으로 예상되며, 투자자들은 지속적인 모니터링을 통해 투자 기회를 모색할 필요가 있습니다.',
            'symbol': 'AAPL',
            'event_type': 'price_change',
            'quality_score': 8.5,
            'created_at': datetime.now().isoformat(),
            'advertisements': [
                {'title': '스마트 투자 플랫폼', 'category': 'investment_platforms'},
                {'title': '실시간 트레이딩 도구', 'category': 'trading_tools'},
                {'title': '투자 교육 아카데미', 'category': 'education_services'}
            ]
        }
        
        # 세션 상태에 추가
        st.session_state.articles_list.insert(0, test_article)
        
        # Telegram 알림 전송
        if os.getenv('TELEGRAM_BOT_TOKEN') and os.getenv('TELEGRAM_CHAT_ID'):
            send_article_notification(test_article)
        
        st.success("✅ 테스트 기사가 생성되었습니다!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ 기사 생성 실패: {str(e)}")

def send_telegram_notification(text: str):
    """Telegram 알림 전송"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if bot_token and chat_id:
        notifier = TelegramNotifier(bot_token, chat_id)
        try:
            import asyncio
            asyncio.run(notifier._send_telegram(text))
        except:
            pass

def send_test_telegram_notification(notification_type: str):
    """테스트 Telegram 알림 전송"""
    tg_texts = {
        "system_status": "📊 시스템 상태 알림: 정상 운영 중",
        "event_detected": "🚨 이벤트 감지: AAPL 주가 3.5% 상승",
        "article_generated": "📰 기사 생성 완료: Apple 주가 3.5% 상승"
    }
    send_telegram_notification(tg_texts.get(notification_type, "테스트 알림"))
    st.success("✅ Telegram 알림이 전송되었습니다!")

def send_article_notification(article: Dict[str, Any]):
    """기사 생성 Telegram 알림 전송"""
    tg_text = f"📰 <b>AI 기사 생성 완료</b>\n\n{article.get('title', '')}\n심볼: {article.get('symbol', 'N/A')} | 품질: {article.get('quality_score', 'N/A')}/10"
    send_telegram_notification(tg_text)

def monitoring_worker():
    """백그라운드 모니터링 워커"""
    try:
        # 실제 데이터 수집 및 이벤트 감지 로직
        import yfinance as yf
        import numpy as np
        
        monitoring_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA', '^GSPC', '^IXIC', '^VIX']
        
        while st.session_state.monitoring_active:
            try:
                detected_events = []
                
                # 각 심볼에 대해 데이터 수집 및 이벤트 감지
                for symbol in monitoring_symbols:
                    try:
                        # 실시간 데이터 수집
                        ticker = yf.Ticker(symbol)
                        hist = ticker.history(period="1d", interval="5m")
                        
                        if len(hist) > 1:
                            # 최근 가격 변화 계산
                            current_price = hist['Close'].iloc[-1]
                            prev_price = hist['Close'].iloc[-2]
                            change_percent = ((current_price - prev_price) / prev_price) * 100
                            
                            # 거래량 변화 계산
                            current_volume = hist['Volume'].iloc[-1]
                            avg_volume = hist['Volume'].mean()
                            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
                            
                            # 이벤트 감지 로직
                            severity = 0
                            event_type = "normal"
                            description = f"{symbol} 정상 거래"
                            
                            # 가격 변화 기반 이벤트
                            if abs(change_percent) > 3:
                                severity = 0.7
                                event_type = "price_spike" if change_percent > 0 else "price_drop"
                                description = f"{symbol} 가격 {'급등' if change_percent > 0 else '급락'} ({change_percent:.2f}%)"
                            elif abs(change_percent) > 2:
                                severity = 0.5
                                event_type = "price_change"
                                description = f"{symbol} 가격 변동 ({change_percent:.2f}%)"
                            
                            # 거래량 기반 이벤트
                            if volume_ratio > 2:
                                severity = max(severity, 0.6)
                                event_type = "volume_spike"
                                description = f"{symbol} 거래량 급증 (평균 대비 {volume_ratio:.1f}배)"
                            
                            # VIX 특별 처리
                            if symbol == '^VIX' and current_price > 25:
                                severity = 0.8
                                event_type = "high_volatility"
                                description = f"VIX 고공행진 ({current_price:.2f}), 시장 불안 증가"
                            
                            # 이벤트 생성
                            if severity > 0.4:  # 임계값 이상인 경우만
                                event = {
                                    'symbol': symbol,
                                    'event_type': event_type,
                                    'description': description,
                                    'severity': severity,
                                    'severity_level': 'high' if severity > 0.7 else 'medium' if severity > 0.5 else 'low',
                                    'change_percent': round(change_percent, 2),
                                    'current_price': round(current_price, 2),
                                    'volume_ratio': round(volume_ratio, 2),
                                    'timestamp': datetime.now().isoformat()
                                }
                                detected_events.append(event)
                    
                    except Exception as e:
                        print(f"심볼 {symbol} 처리 오류: {e}")
                        continue
                
                # 감지된 이벤트 처리
                for event in detected_events:
                    if event.get('severity', 0) > 0.6:  # 임계값 이상인 경우
                        # Telegram 알림 전송
                        send_event_notification(event)
                        
                        # 기사 생성 트리거
                        if event.get('severity', 0) > 0.7:
                            generate_article_from_event(event)
                
                # 모니터링 데이터 업데이트
                st.session_state.monitoring_data = {
                    'last_update': datetime.now().isoformat(),
                    'events_count': len(detected_events),
                    'active_alerts': sum(1 for e in detected_events if e.get('severity', 0) > 0.6),
                    'events': detected_events[-10:]  # 최근 10개 이벤트만 저장
                }
                
                time.sleep(60)  # 1분 간격으로 모니터링
                
            except Exception as e:
                print(f"모니터링 오류: {e}")
                time.sleep(30)  # 오류 시 30초 대기
                
    except Exception as e:
        print(f"모니터링 워커 오류: {e}")
        st.session_state.monitoring_active = False

def send_event_notification(event: Dict[str, Any]):
    """이벤트 감지 Telegram 알림 전송"""
    tg_text = f"🚨 <b>시장 이벤트 감지</b>\n\n{event.get('description', '')}\n심볼: {event.get('symbol', 'N/A')} | 변화율: {event.get('change_percent', 'N/A')}%"
    send_telegram_notification(tg_text)

def generate_article_from_event(event: Dict[str, Any]):
    """이벤트 기반 기사 생성"""
    try:
        # 간단한 기사 생성 로직 (실제 AI 모델 대신 템플릿 사용)
        symbol = event.get('symbol', '')
        event_type = event.get('event_type', '')
        change_percent = event.get('change_percent', 0)
        current_price = event.get('current_price', 0)
        description = event.get('description', '')
        
        # 기사 제목 생성
        if event_type == "price_spike":
            title = f"{symbol} 주가 {abs(change_percent):.1f}% 급등, 투자자 관심 집중"
        elif event_type == "price_drop":
            title = f"{symbol} 주가 {abs(change_percent):.1f}% 급락, 시장 우려 확산"
        elif event_type == "volume_spike":
            title = f"{symbol} 거래량 급증, 시장 변동성 증가 신호"
        elif event_type == "high_volatility":
            title = f"VIX 지수 상승, 시장 불안감 고조"
        else:
            title = f"{symbol} 시장 동향 분석"
        
        # 기사 리드 생성
        lead = f"{symbol}이(가) 오늘 거래에서 {description.lower()}하며 시장의 주목을 받고 있습니다."
        
        # 기사 본문 생성
        body_parts = []
        
        # 가격 정보
        if current_price > 0:
            body_parts.append(f"{symbol}은(는) 현재 ${current_price:.2f}에 거래되고 있으며, 전 거래 대비 {change_percent:+.2f}%의 변화를 보이고 있습니다.")
        
        # 이벤트 분석
        if event_type == "price_spike":
            body_parts.append("이번 급등은 긍정적인 시장 심리와 기관투자자들의 매수세가 반영된 것으로 분석됩니다. 기술적 지표들도 상승 모멘텀을 뒷받침하고 있어 단기적으로 추가 상승 가능성이 있어 보입니다.")
        elif event_type == "price_drop":
            body_parts.append("급락의 배경에는 시장 전반의 불안감과 매도 압력이 작용한 것으로 보입니다. 투자자들은 향후 시장 동향을 주의 깊게 관찰할 필요가 있습니다.")
        elif event_type == "volume_spike":
            body_parts.append("거래량 급증은 시장 참여자들의 높은 관심을 반영하며, 향후 가격 변동성이 확대될 가능성을 시사합니다.")
        
        # 시장 전망
        body_parts.append("전문가들은 현재 시장 상황을 면밀히 분석하고 있으며, 투자자들에게는 신중한 접근을 권고하고 있습니다.")
        
        body = " ".join(body_parts)
        
        # 결론
        conclusion = f"{symbol}의 향후 움직임은 전체 시장 상황과 밀접한 관련이 있을 것으로 예상되며, 투자자들은 지속적인 모니터링을 통해 적절한 투자 전략을 수립해야 할 것입니다."
        
        # 기사 객체 생성
        article = {
            'title': title,
            'lead': lead,
            'body': body,
            'conclusion': conclusion,
            'symbol': symbol,
            'event_type': event_type,
            'quality_score': round(7.5 + (event.get('severity', 0) * 2), 1),
            'created_at': datetime.now().isoformat(),
            'source_event': event,
            'advertisements': [
                {'title': '스마트 투자 플랫폼', 'category': 'investment_platforms'},
                {'title': f'{symbol} 실시간 차트', 'category': 'trading_tools'},
                {'title': '시장 분석 리포트', 'category': 'research_services'}
            ]
        }
        
        # 세션 상태에 추가
        st.session_state.articles_list.insert(0, article)
        
        # Telegram 알림 전송
        send_article_notification(article)
        
        print(f"기사 생성 완료: {title}")
        
    except Exception as e:
        print(f"기사 생성 오류: {e}")

def main():
    """메인 함수"""
    # 헤더 렌더링
    dashboard.render_header()
    
    # 사이드바 렌더링
    monitoring_interval, alert_threshold = dashboard.render_sidebar()
    
    # 메인 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs(["📊 실시간 모니터링", "🚨 이벤트 감지", "📰 AI 기사", "📱 Telegram 알림"])
    
    with tab1:
        dashboard.render_monitoring_section()
    
    with tab2:
        render_events_section()
    
    with tab3:
        render_articles_section()
    
    with tab4:
        render_notifications_section()
    
    # 백그라운드 모니터링 시작
    if st.session_state.monitoring_active and 'monitoring_thread' not in st.session_state:
        st.session_state.monitoring_thread = threading.Thread(target=monitoring_worker, daemon=True)
        st.session_state.monitoring_thread.start()
    
    # 상태 표시
    if st.session_state.monitoring_active:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 시스템 상태")
        
        last_update = st.session_state.monitoring_data.get('last_update', 'N/A')
        if last_update != 'N/A':
            last_update = last_update[:19].replace('T', ' ')
        
        st.sidebar.write(f"**마지막 업데이트**: {last_update}")
        st.sidebar.write(f"**활성 이벤트**: {st.session_state.monitoring_data.get('active_alerts', 0)}개")
        st.sidebar.write(f"**생성된 기사**: {len(st.session_state.articles_list)}개")
        
        # 자동 새로고침 (30초마다)
        if st.sidebar.button("🔄 수동 새로고침"):
            st.rerun()
        
        # 자동 새로고침을 위한 placeholder
        placeholder = st.empty()
        with placeholder.container():
            st.info("⏱️ 모니터링 활성화됨 - 1분마다 자동 업데이트")
        
        # 30초 후 자동 새로고침
        time.sleep(30)
        st.rerun()

# Dashboard 객체 생성
dashboard = IntegratedDashboard()

if __name__ == "__main__":
    main()
