#!/usr/bin/env python3
"""
강화된 Streamlit 대시보드 - FRED 데이터 및 뉴스/SNS 모니터링 포함
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime, timedelta
import json

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_monitoring.enhanced_data_collector import EnhancedGlobalDataCollector

# 페이지 설정
st.set_page_config(
    page_title="🧠 통합 경제 모니터링 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 캐시된 데이터 수집 함수들
@st.cache_data(ttl=300)  # 5분 캐시
def collect_all_data():
    """모든 데이터 수집"""
    try:
        collector = EnhancedGlobalDataCollector()
        
        # Intelligence 데이터
        intelligence_data = collector.collect_intelligence_data()
        
        # FRED 데이터
        fred_data = collector.collect_fred_data()
        
        # 강화된 뉴스 데이터
        news_data = collector.collect_enhanced_news_data()
        
        return {
            'intelligence': intelligence_data,
            'fred': fred_data,
            'news': news_data,
            'timestamp': datetime.now().isoformat()
        }, None
        
    except Exception as e:
        return None, str(e)

def create_fred_indicators_chart(fred_data):
    """FRED 주요 지표 차트"""
    if not fred_data or fred_data.get('status') != 'success':
        return None
    
    indicators = fred_data.get('data', {}).get('indicators', {})
    if not indicators:
        return None
    
    # 주요 지표 선택
    key_indicators = ['federal_funds_rate', 'unemployment_rate', 'cpi', 'gdp_growth']
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('연방기금금리', '실업률', '소비자물가지수', 'GDP 성장률'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    positions = [(1,1), (1,2), (2,1), (2,2)]
    
    for i, indicator_key in enumerate(key_indicators):
        if indicator_key in indicators:
            indicator = indicators[indicator_key]
            historical_data = indicator.get('historical_data', [])
            
            if historical_data:
                dates = [item['date'] for item in historical_data]
                values = [item['value'] for item in historical_data]
                
                row, col = positions[i]
                fig.add_trace(
                    go.Scatter(
                        x=dates, 
                        y=values, 
                        mode='lines+markers',
                        name=indicator.get('title', indicator_key),
                        line=dict(width=2)
                    ),
                    row=row, col=col
                )
    
    fig.update_layout(
        title="📊 FRED 주요 경제 지표",
        height=600,
        showlegend=False
    )
    
    return fig

def create_news_sentiment_chart(news_data):
    """뉴스 감정 분석 차트"""
    if not news_data or news_data.get('status') != 'success':
        return None
    
    news_info = news_data.get('data', {}).get('news_data', {})
    categories = news_info.get('categories', {})
    
    if not categories:
        return None
    
    # 카테고리별 감정 분석
    category_names = []
    positive_counts = []
    negative_counts = []
    neutral_counts = []
    
    for category, articles in categories.items():
        if articles:
            sentiments = [article.get('sentiment', {}).get('label', 'neutral') for article in articles]
            category_names.append(category.replace('_', ' ').title())
            positive_counts.append(sentiments.count('positive'))
            negative_counts.append(sentiments.count('negative'))
            neutral_counts.append(sentiments.count('neutral'))
    
    fig = go.Figure(data=[
        go.Bar(name='긍정', x=category_names, y=positive_counts, marker_color='green'),
        go.Bar(name='부정', x=category_names, y=negative_counts, marker_color='red'),
        go.Bar(name='중립', x=category_names, y=neutral_counts, marker_color='gray')
    ])
    
    fig.update_layout(
        title="📰 카테고리별 뉴스 감정 분석",
        barmode='stack',
        height=400
    )
    
    return fig

def create_social_sentiment_gauge(news_data):
    """소셜미디어 감정 게이지"""
    if not news_data or news_data.get('status') != 'success':
        return None
    
    social_data = news_data.get('data', {}).get('social_data', {})
    overall_sentiment = social_data.get('overall_sentiment', {})
    
    score = overall_sentiment.get('score', 0)
    label = overall_sentiment.get('label', 'neutral')
    
    # -1 to 1 범위를 0 to 100으로 변환
    gauge_value = (score + 1) * 50
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = gauge_value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "📱 소셜미디어 감정 지수"},
        delta = {'reference': 50},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 25], 'color': "red"},
                {'range': [25, 40], 'color': "orange"},
                {'range': [40, 60], 'color': "yellow"},
                {'range': [60, 75], 'color': "lightgreen"},
                {'range': [75, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig

def display_fred_summary(fred_data):
    """FRED 데이터 요약 표시"""
    if not fred_data or fred_data.get('status') != 'success':
        st.warning("⚠️ FRED 데이터를 불러올 수 없습니다.")
        return
    
    summary = fred_data.get('summary', {})
    highlights = summary.get('key_highlights', {})
    
    st.subheader("📊 FRED 경제 지표 요약")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'interest_rates' in highlights:
            fed_rate = highlights['interest_rates']
            st.metric(
                "연방기금금리",
                f"{fed_rate.get('federal_funds_rate', 0):.2f}%",
                f"{fed_rate.get('change', 0):+.2f}%"
            )
    
    with col2:
        if 'employment' in highlights:
            employment = highlights['employment']
            st.metric(
                "실업률",
                f"{employment.get('unemployment_rate', 0):.1f}%",
                f"{employment.get('change', 0):+.1f}%"
            )
    
    with col3:
        if 'inflation' in highlights:
            inflation = highlights['inflation']
            st.metric(
                "CPI 변화율",
                f"{inflation.get('cpi_change', 0):+.1f}%",
                inflation.get('trend', '보합')
            )
    
    with col4:
        if 'growth' in highlights:
            growth = highlights['growth']
            st.metric(
                "GDP 성장률",
                f"{growth.get('gdp_growth_rate', 0):.1f}%",
                growth.get('trend', '보합')
            )

def display_news_highlights(news_data):
    """뉴스 하이라이트 표시"""
    if not news_data or news_data.get('status') != 'success':
        st.warning("⚠️ 뉴스 데이터를 불러올 수 없습니다.")
        return
    
    news_info = news_data.get('data', {}).get('news_data', {})
    summary = news_info.get('summary', {})
    highlights = summary.get('recent_highlights', [])
    
    st.subheader("📰 주요 뉴스 하이라이트")
    
    if highlights:
        for i, article in enumerate(highlights[:5], 1):
            sentiment_color = {
                'positive': '🟢',
                'negative': '🔴',
                'neutral': '🟡'
            }.get(article.get('sentiment', 'neutral'), '🟡')
            
            st.write(f"{sentiment_color} **{article.get('title', '')}**")
            st.write(f"   📰 {article.get('source', '')} | 주제: {', '.join(article.get('topics', []))}")
            st.write("---")
    else:
        st.info("최근 주요 뉴스가 없습니다.")

def display_trending_topics(news_data):
    """트렌딩 주제 표시"""
    if not news_data or news_data.get('status') != 'success':
        return
    
    news_info = news_data.get('data', {}).get('news_data', {})
    summary = news_info.get('summary', {})
    trending = summary.get('trending_topics', {})
    
    if trending:
        st.subheader("🔥 트렌딩 주제")
        
        # 상위 10개 주제를 바 차트로 표시
        topics = list(trending.keys())[:10]
        counts = list(trending.values())[:10]
        
        fig = px.bar(
            x=counts,
            y=topics,
            orientation='h',
            title="주제별 언급 횟수",
            labels={'x': '언급 횟수', 'y': '주제'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def main():
    """메인 대시보드"""
    
    # 헤더
    st.title("🧠 통합 경제 모니터링 대시보드")
    st.markdown("**Alpha Vantage Intelligence + FRED 경제 데이터 + 뉴스/SNS 모니터링**")
    st.markdown("---")
    
    # 사이드바
    with st.sidebar:
        st.header("⚙️ 제어판")
        
        # 새로고침 버튼
        if st.button("🔄 전체 데이터 새로고침", type="primary"):
            st.cache_data.clear()
            st.rerun()
        
        # 데이터 소스 선택
        st.subheader("📊 데이터 소스")
        show_intelligence = st.checkbox("Intelligence API", value=True)
        show_fred = st.checkbox("FRED 경제 데이터", value=True)
        show_news = st.checkbox("뉴스 & SNS", value=True)
        
        st.markdown("---")
        
        # 업데이트 정보
        st.subheader("⏰ 업데이트 정보")
        st.write(f"마지막 업데이트: {datetime.now().strftime('%H:%M:%S')}")
    
    # 데이터 로딩
    with st.spinner("🔄 통합 데이터 수집 중..."):
        all_data, error = collect_all_data()
    
    if error:
        st.error(f"❌ 데이터 수집 오류: {error}")
        return
    
    if not all_data:
        st.warning("⚠️ 수집된 데이터가 없습니다.")
        return
    
    # 데이터 추출
    intelligence_data = all_data.get('intelligence', {})
    fred_data = all_data.get('fred', {})
    news_data = all_data.get('news', {})
    
    # 1. 전체 요약 메트릭
    st.subheader("📊 통합 대시보드 개요")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        intel_summary = intelligence_data.get('summary', {})
        st.metric(
            "🌍 글로벌 시장",
            intel_summary.get('market_status_count', 0),
            f"개장: {intel_summary.get('open_markets_count', 0)}개"
        )
    
    with col2:
        fred_summary = fred_data.get('summary', {})
        st.metric(
            "📊 FRED 지표",
            fred_summary.get('collected_indicators', 0),
            f"총 {fred_summary.get('total_indicators', 0)}개 중"
        )
    
    with col3:
        news_summary = news_data.get('summary', {})
        st.metric(
            "📰 뉴스 기사",
            news_summary.get('total_articles', 0),
            f"긍정: {news_summary.get('news_sentiment', {}).get('positive_ratio', 0):.1f}%"
        )
    
    with col4:
        social_mentions = news_summary.get('social_mentions', {})
        st.metric(
            "📱 소셜 언급",
            social_mentions.get('twitter', 0),
            f"Reddit: {social_mentions.get('reddit_posts', 0)}개"
        )
    
    st.markdown("---")
    
    # 2. FRED 경제 데이터 섹션
    if show_fred and fred_data.get('status') == 'success':
        display_fred_summary(fred_data)
        
        fred_chart = create_fred_indicators_chart(fred_data)
        if fred_chart:
            st.plotly_chart(fred_chart, use_container_width=True)
        
        st.markdown("---")
    
    # 3. Intelligence API 데이터 (기존)
    if show_intelligence and intelligence_data.get('status') == 'success':
        from streamlit_intelligence_dashboard import (
            create_market_status_chart, 
            create_top_movers_chart,
            display_top_movers_table
        )
        
        intel_data = intelligence_data.get('data', {})
        market_status = intel_data.get('market_status', [])
        top_movers = intel_data.get('top_gainers_losers', {})
        
        st.subheader("📈 시장 현황 (Alpha Vantage Intelligence)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            market_chart = create_market_status_chart(market_status)
            if market_chart:
                st.plotly_chart(market_chart, use_container_width=True)
        
        with col2:
            movers_chart = create_top_movers_chart(top_movers)
            if movers_chart:
                st.plotly_chart(movers_chart, use_container_width=True)
        
        st.markdown("---")
    
    # 4. 뉴스 및 소셜미디어 섹션
    if show_news and news_data.get('status') == 'success':
        st.subheader("📰 뉴스 & 소셜미디어 분석")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            news_chart = create_news_sentiment_chart(news_data)
            if news_chart:
                st.plotly_chart(news_chart, use_container_width=True)
        
        with col2:
            social_gauge = create_social_sentiment_gauge(news_data)
            if social_gauge:
                st.plotly_chart(social_gauge, use_container_width=True)
        
        # 뉴스 하이라이트
        col1, col2 = st.columns(2)
        
        with col1:
            display_news_highlights(news_data)
        
        with col2:
            display_trending_topics(news_data)
        
        st.markdown("---")
    
    # 5. 통합 분석 요약
    st.subheader("🎯 통합 분석 요약")
    
    # 전체 시장 감정
    overall_sentiment = news_data.get('summary', {}).get('overall_market_sentiment', {})
    if overall_sentiment:
        sentiment_score = overall_sentiment.get('score', 0)
        sentiment_label = overall_sentiment.get('label', '중립')
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "🎭 전체 시장 감정",
                sentiment_label,
                f"점수: {sentiment_score:+.3f}"
            )
        
        with col2:
            # FRED 기반 경제 상황
            fred_highlights = fred_data.get('summary', {}).get('key_highlights', {})
            if 'growth' in fred_highlights:
                growth_trend = fred_highlights['growth'].get('trend', '보합')
                st.metric("📈 경제 성장", growth_trend, "FRED 기준")
        
        with col3:
            # 시장 변동성
            intel_summary = intelligence_data.get('summary', {})
            volatility = intel_summary.get('market_volatility', 'unknown')
            st.metric("⚡ 시장 변동성", volatility, "Intelligence 기준")
    
    # 원시 데이터 (확장 가능)
    with st.expander("🔍 원시 데이터 보기"):
        tab1, tab2, tab3 = st.tabs(["Intelligence", "FRED", "News & Social"])
        
        with tab1:
            st.json(intelligence_data)
        
        with tab2:
            st.json(fred_data)
        
        with tab3:
            st.json(news_data)

if __name__ == "__main__":
    main()
