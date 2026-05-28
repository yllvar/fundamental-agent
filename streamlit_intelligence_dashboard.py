#!/usr/bin/env python3
"""
Alpha Vantage Intelligence API 통합 Streamlit 모니터링 대시보드
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import asyncio
import sys
import os
from datetime import datetime, timedelta
import json

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_monitoring.enhanced_data_collector import EnhancedGlobalDataCollector
from data_monitoring.alphavantage_intelligence_complete import AlphaVantageIntelligenceComplete

# 페이지 설정
st.set_page_config(
    page_title="🧠 Intelligence 모니터링 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 캐시된 데이터 수집 함수
@st.cache_data(ttl=300)  # 5분 캐시
def collect_intelligence_data():
    """Intelligence 데이터 수집 (캐시됨)"""
    try:
        intelligence = AlphaVantageIntelligenceComplete()
        data = intelligence.collect_comprehensive_intelligence()
        return data, None
    except Exception as e:
        return None, str(e)

@st.cache_data(ttl=600)  # 10분 캐시
def collect_enhanced_data():
    """Enhanced 데이터 수집 (캐시됨)"""
    try:
        collector = EnhancedGlobalDataCollector()
        intelligence_data = collector.collect_intelligence_data()
        return intelligence_data, None
    except Exception as e:
        return None, str(e)

def create_market_status_chart(market_data):
    """시장 상태 차트 생성"""
    if not market_data:
        return None
    
    # 데이터 준비
    regions = [m['region'] for m in market_data]
    statuses = [m['current_status'] for m in market_data]
    exchanges = [m['primary_exchanges'] for m in market_data]
    
    # 상태별 색상
    colors = ['#00ff00' if status == 'open' else '#ff0000' for status in statuses]
    
    # 차트 생성
    fig = go.Figure(data=[
        go.Bar(
            x=regions,
            y=[1] * len(regions),
            text=[f"{region}<br>{status.upper()}" for region, status in zip(regions, statuses)],
            textposition='inside',
            marker_color=colors,
            hovertemplate='<b>%{x}</b><br>Status: %{customdata[0]}<br>Exchanges: %{customdata[1]}<extra></extra>',
            customdata=list(zip(statuses, exchanges))
        )
    ])
    
    fig.update_layout(
        title="🌍 글로벌 시장 상태",
        xaxis_title="지역",
        yaxis_title="",
        showlegend=False,
        height=400,
        yaxis=dict(showticklabels=False)
    )
    
    return fig

def create_top_movers_chart(top_movers_data):
    """상위 변동 종목 차트 생성"""
    if not top_movers_data:
        return None
    
    # 서브플롯 생성
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=('📈 상위 상승', '📉 상위 하락', '🔥 최고 거래량'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # 상위 상승 종목
    if 'top_gainers' in top_movers_data and top_movers_data['top_gainers']:
        gainers = top_movers_data['top_gainers'][:10]  # 상위 10개
        tickers = [g['ticker'] for g in gainers]
        changes = [float(g['change_percentage'].replace('%', '')) for g in gainers]
        
        fig.add_trace(
            go.Bar(x=tickers, y=changes, name="상승률", marker_color='green'),
            row=1, col=1
        )
    
    # 상위 하락 종목
    if 'top_losers' in top_movers_data and top_movers_data['top_losers']:
        losers = top_movers_data['top_losers'][:10]  # 상위 10개
        tickers = [l['ticker'] for l in losers]
        changes = [float(l['change_percentage'].replace('%', '')) for l in losers]
        
        fig.add_trace(
            go.Bar(x=tickers, y=changes, name="하락률", marker_color='red'),
            row=1, col=2
        )
    
    # 최고 거래량 종목
    if 'most_actively_traded' in top_movers_data and top_movers_data['most_actively_traded']:
        actives = top_movers_data['most_actively_traded'][:10]  # 상위 10개
        tickers = [a['ticker'] for a in actives]
        volumes = [a['volume'] / 1000000 for a in actives]  # 백만 단위
        
        fig.add_trace(
            go.Bar(x=tickers, y=volumes, name="거래량(M)", marker_color='blue'),
            row=1, col=3
        )
    
    fig.update_layout(
        title="📊 상위 변동 종목 분석",
        height=500,
        showlegend=False
    )
    
    return fig

def create_market_overview_metrics(summary_data):
    """시장 개요 메트릭 생성"""
    if not summary_data:
        return None
    
    data_counts = summary_data.get('data_counts', {})
    market_analysis = summary_data.get('market_analysis', {})
    highlights = summary_data.get('highlights', {})
    
    # 메트릭 컬럼 생성
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🌍 총 시장",
            value=market_analysis.get('total_markets', 0),
            delta=f"개장: {market_analysis.get('open_markets', 0)}개"
        )
    
    with col2:
        st.metric(
            label="📈 상승 종목",
            value=data_counts.get('top_gainers', 0),
            delta=highlights.get('top_gainer', {}).get('change_percentage', 'N/A')
        )
    
    with col3:
        st.metric(
            label="📉 하락 종목", 
            value=data_counts.get('top_losers', 0),
            delta=highlights.get('top_loser', {}).get('change_percentage', 'N/A')
        )
    
    with col4:
        most_active_volume = highlights.get('most_active', {}).get('volume', 0)
        volume_display = f"{most_active_volume/1000000:.1f}M" if most_active_volume > 0 else "N/A"
        st.metric(
            label="🔥 최고 거래량",
            value=data_counts.get('most_active', 0),
            delta=volume_display
        )

def create_regional_analysis(market_data):
    """지역별 분석 차트"""
    if not market_data:
        return None
    
    # 지역별 상태 집계
    region_status = {}
    for market in market_data:
        region = market['region']
        status = market['current_status']
        
        if region not in region_status:
            region_status[region] = {'open': 0, 'closed': 0}
        
        region_status[region][status] += 1
    
    # 데이터프레임 생성
    regions = list(region_status.keys())
    open_counts = [region_status[r]['open'] for r in regions]
    closed_counts = [region_status[r]['closed'] for r in regions]
    
    # 스택 바 차트
    fig = go.Figure(data=[
        go.Bar(name='개장', x=regions, y=open_counts, marker_color='green'),
        go.Bar(name='폐장', x=regions, y=closed_counts, marker_color='red')
    ])
    
    fig.update_layout(
        title="🌏 지역별 시장 상태",
        barmode='stack',
        height=400
    )
    
    return fig

def display_top_movers_table(top_movers_data):
    """상위 변동 종목 테이블 표시"""
    if not top_movers_data:
        return
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["📈 상승 종목", "📉 하락 종목", "🔥 활발한 거래"])
    
    with tab1:
        if 'top_gainers' in top_movers_data and top_movers_data['top_gainers']:
            gainers_df = pd.DataFrame(top_movers_data['top_gainers'])
            gainers_df['change_percentage'] = gainers_df['change_percentage'].str.replace('%', '').astype(float)
            gainers_df = gainers_df.sort_values('change_percentage', ascending=False)
            
            st.dataframe(
                gainers_df[['ticker', 'price', 'change_percentage', 'volume']].head(20),
                column_config={
                    "ticker": "종목",
                    "price": st.column_config.NumberColumn("가격", format="$%.2f"),
                    "change_percentage": st.column_config.NumberColumn("변화율", format="%.2f%%"),
                    "volume": st.column_config.NumberColumn("거래량", format="%d")
                },
                use_container_width=True
            )
    
    with tab2:
        if 'top_losers' in top_movers_data and top_movers_data['top_losers']:
            losers_df = pd.DataFrame(top_movers_data['top_losers'])
            losers_df['change_percentage'] = losers_df['change_percentage'].str.replace('%', '').astype(float)
            losers_df = losers_df.sort_values('change_percentage', ascending=True)
            
            st.dataframe(
                losers_df[['ticker', 'price', 'change_percentage', 'volume']].head(20),
                column_config={
                    "ticker": "종목",
                    "price": st.column_config.NumberColumn("가격", format="$%.2f"),
                    "change_percentage": st.column_config.NumberColumn("변화율", format="%.2f%%"),
                    "volume": st.column_config.NumberColumn("거래량", format="%d")
                },
                use_container_width=True
            )
    
    with tab3:
        if 'most_actively_traded' in top_movers_data and top_movers_data['most_actively_traded']:
            active_df = pd.DataFrame(top_movers_data['most_actively_traded'])
            active_df['change_percentage'] = active_df['change_percentage'].str.replace('%', '').astype(float)
            active_df = active_df.sort_values('volume', ascending=False)
            
            st.dataframe(
                active_df[['ticker', 'price', 'change_percentage', 'volume']].head(20),
                column_config={
                    "ticker": "종목",
                    "price": st.column_config.NumberColumn("가격", format="$%.2f"),
                    "change_percentage": st.column_config.NumberColumn("변화율", format="%.2f%%"),
                    "volume": st.column_config.NumberColumn("거래량", format="%d")
                },
                use_container_width=True
            )

def main():
    """메인 대시보드"""
    
    # 헤더
    st.title("🧠 Alpha Vantage Intelligence 모니터링 대시보드")
    st.markdown("---")
    
    # 사이드바
    with st.sidebar:
        st.header("⚙️ 제어판")
        
        # 새로고침 버튼
        if st.button("🔄 데이터 새로고침", type="primary", key="intelligence_refresh"):
            st.cache_data.clear()
            st.rerun()
        
        # 자동 새로고침 설정
        auto_refresh = st.checkbox("🔄 자동 새로고침 (30초)", value=False)
        if auto_refresh:
            st.rerun()
        
        st.markdown("---")
        
        # API 키 상태
        st.subheader("🔑 API 상태")
        api_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
        if api_key == 'demo':
            st.info("Demo API 키 사용 중")
        else:
            st.success(f"API 키: {api_key[:8]}...")
        
        st.markdown("---")
        
        # 업데이트 시간
        st.subheader("⏰ 업데이트 정보")
        st.write(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 메인 콘텐츠
    try:
        # 데이터 로딩
        with st.spinner("🔄 Intelligence 데이터 수집 중..."):
            intelligence_data, error = collect_intelligence_data()
        
        if error:
            st.error(f"❌ 데이터 수집 오류: {error}")
            return
        
        if not intelligence_data:
            st.warning("⚠️ 수집된 데이터가 없습니다.")
            return
        
        # 데이터 추출
        summary = intelligence_data.get('summary', {})
        market_status = intelligence_data.get('market_status', [])
        top_movers = intelligence_data.get('top_gainers_losers', {})
        
        # 1. 개요 메트릭
        st.subheader("📊 시장 개요")
        create_market_overview_metrics(summary)
        
        st.markdown("---")
        
        # 2. 시장 상태 차트
        col1, col2 = st.columns(2)
        
        with col1:
            market_chart = create_market_status_chart(market_status)
            if market_chart:
                st.plotly_chart(market_chart, use_container_width=True)
        
        with col2:
            regional_chart = create_regional_analysis(market_status)
            if regional_chart:
                st.plotly_chart(regional_chart, use_container_width=True)
        
        # 3. 상위 변동 종목 차트
        st.subheader("📈 상위 변동 종목")
        movers_chart = create_top_movers_chart(top_movers)
        if movers_chart:
            st.plotly_chart(movers_chart, use_container_width=True)
        
        st.markdown("---")
        
        # 4. 상세 테이블
        st.subheader("📋 상세 데이터")
        display_top_movers_table(top_movers)
        
        # 5. 하이라이트 정보
        st.markdown("---")
        st.subheader("🔥 주요 하이라이트")
        
        highlights = summary.get('highlights', {})
        if highlights:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if 'top_gainer' in highlights:
                    gainer = highlights['top_gainer']
                    st.success(f"📈 최고 상승: **{gainer['ticker']}** ({gainer['change_percentage']})")
            
            with col2:
                if 'top_loser' in highlights:
                    loser = highlights['top_loser']
                    st.error(f"📉 최고 하락: **{loser['ticker']}** ({loser['change_percentage']})")
            
            with col3:
                if 'most_active' in highlights:
                    active = highlights['most_active']
                    volume_display = f"{active['volume']/1000000:.1f}M"
                    st.info(f"🔥 최고 거래량: **{active['ticker']}** ({volume_display})")
        
        # 6. 개장 시장 정보
        if market_status:
            open_markets = [m for m in market_status if m['current_status'] == 'open']
            if open_markets:
                st.markdown("---")
                st.subheader("🟢 현재 개장 중인 시장")
                
                for market in open_markets:
                    st.write(f"• **{market['region']}**: {market['primary_exchanges']} ({market['local_open']} - {market['local_close']})")
        
        # 7. 원시 데이터 (확장 가능)
        with st.expander("🔍 원시 데이터 보기"):
            st.json(intelligence_data)
    
    except Exception as e:
        st.error(f"❌ 대시보드 오류: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    # 자동 새로고침 (30초)
    import time
    time.sleep(1)
    main()
