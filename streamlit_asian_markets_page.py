#!/usr/bin/env python3
"""
아시아 시장 분석 상세 페이지
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import sys
import os

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_monitoring.asian_markets_collector import AsianMarketsCollector

@st.cache_data(ttl=300)  # 5분 캐시
def collect_asian_markets_data():
    """아시아 시장 데이터 수집 (캐시됨)"""
    try:
        collector = AsianMarketsCollector()
        return collector.get_comprehensive_asian_data(), None
    except Exception as e:
        return None, str(e)

def show_asian_markets_page():
    """아시아 시장 분석 메인 페이지"""
    st.header("🌏 아시아 시장 분석")
    
    # 데이터 로딩
    with st.spinner("🔄 아시아 시장 데이터 수집 중..."):
        asian_data, error = collect_asian_markets_data()
    
    if error:
        st.error(f"❌ 아시아 시장 데이터 로드 실패: {error}")
        return
    
    if not asian_data:
        st.warning("⚠️ 아시아 시장 데이터가 없습니다.")
        return
    
    # 요약 정보
    show_asian_market_summary(asian_data)
    
    st.markdown("---")
    
    # 탭으로 구분
    tab1, tab2, tab3, tab4 = st.tabs(["📊 시장 지수", "🏆 주요 주식", "🌍 국가별 분석", "📈 섹터 분석"])
    
    with tab1:
        show_market_indices(asian_data)
    
    with tab2:
        show_major_stocks(asian_data)
    
    with tab3:
        show_country_analysis(asian_data)
    
    with tab4:
        show_sector_analysis(asian_data)

def show_asian_market_summary(asian_data):
    """아시아 시장 요약 정보"""
    st.subheader("📊 아시아 시장 요약")
    
    summary = asian_data.get('market_summary', {})
    indices = asian_data.get('market_indices', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "총 시장 수",
            summary.get('total_markets', 0),
            f"개장: {len(asian_data.get('open_markets', []))}개"
        )
    
    with col2:
        st.metric(
            "상승 시장",
            summary.get('positive_markets', 0),
            f"하락: {summary.get('negative_markets', 0)}개"
        )
    
    with col3:
        avg_change = summary.get('average_change', 0)
        st.metric(
            "평균 변화율",
            f"{avg_change:+.2f}%",
            "전체 시장"
        )
    
    with col4:
        best_performer = summary.get('best_performer')
        if best_performer:
            st.metric(
                "최고 성과",
                best_performer['market'],
                f"{best_performer['change_percent']:+.2f}%"
            )
    
    # 개장 중인 시장 표시
    open_markets = asian_data.get('open_markets', [])
    if open_markets:
        st.success(f"🟢 **현재 개장 중인 시장**: {', '.join(open_markets)}")
    else:
        st.info("🔴 **현재 모든 아시아 시장이 폐장 상태입니다**")

def show_market_indices(asian_data):
    """시장 지수 상세 표시"""
    st.subheader("📊 아시아 주요 시장 지수")
    
    indices = asian_data.get('market_indices', {})
    
    if not indices:
        st.warning("시장 지수 데이터가 없습니다.")
        return
    
    # 지수 데이터를 테이블로 표시
    indices_list = []
    
    for market_key, data in indices.items():
        if 'current_price' in data:
            indices_list.append({
                '국가': data['market_name'],
                '지수명': data['index_name'],
                '현재가': f"{data['current_price']:,.2f}",
                '전일대비': f"{data['change']:+,.2f}",
                '변화율': f"{data['change_percent']:+.2f}%",
                '거래량': f"{data['volume']:,}" if data['volume'] > 0 else 'N/A',
                '통화': data['currency'],
                '시장시간': data['market_hours'],
                '상태': '🟢 개장' if data.get('market_status') == 'open' else '🔴 폐장',
                '심볼': data['symbol']
            })
    
    if indices_list:
        df = pd.DataFrame(indices_list)
        
        # 인터랙티브 테이블
        st.dataframe(df, use_container_width=True)
        
        # 변화율 차트
        st.subheader("📈 시장 지수 변화율 비교")
        
        chart_data = []
        for item in indices_list:
            change_pct = float(item['변화율'].replace('%', '').replace('+', ''))
            chart_data.append({
                '국가': item['국가'],
                '변화율': change_pct
            })
        
        if chart_data:
            chart_df = pd.DataFrame(chart_data)
            
            fig = px.bar(
                chart_df,
                x='국가',
                y='변화율',
                title="아시아 시장 지수 변화율 (%)",
                color='변화율',
                color_continuous_scale=['red', 'yellow', 'green'],
                text='변화율'
            )
            
            fig.update_traces(texttemplate='%{text:+.2f}%', textposition='outside')
            fig.update_layout(height=400)
            
            st.plotly_chart(fig, use_container_width=True)
        
        # 개별 지수 상세 정보
        st.subheader("🔍 개별 지수 상세 정보")
        
        selected_country = st.selectbox(
            "국가 선택",
            [item['국가'] for item in indices_list]
        )
        
        selected_data = next((item for item in indices_list if item['국가'] == selected_country), None)
        
        if selected_data:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**{selected_data['지수명']}**")
                st.write(f"현재가: {selected_data['현재가']} {selected_data['통화']}")
                st.write(f"변화: {selected_data['전일대비']} ({selected_data['변화율']})")
            
            with col2:
                st.write(f"**거래 정보**")
                st.write(f"거래량: {selected_data['거래량']}")
                st.write(f"시장 상태: {selected_data['상태']}")
                st.write(f"거래 시간: {selected_data['시장시간']}")
            
            with col3:
                # Yahoo Finance 링크
                symbol = selected_data['심볼']
                yahoo_link = f"https://finance.yahoo.com/quote/{symbol}"
                st.link_button("📊 Yahoo Finance", yahoo_link)
                
                # Google Finance 링크
                google_link = f"https://www.google.com/finance/quote/{symbol}"
                st.link_button("📈 Google Finance", google_link)

def show_major_stocks(asian_data):
    """주요 주식 상세 표시"""
    st.subheader("🏆 아시아 주요 주식")
    
    stocks_data = asian_data.get('major_stocks', {})
    
    if not stocks_data:
        st.warning("주식 데이터가 없습니다.")
        return
    
    # 국가 선택
    country_options = list(stocks_data.keys())
    country_names = {
        'korea': '🇰🇷 한국',
        'japan': '🇯🇵 일본', 
        'china': '🇨🇳 중국',
        'hongkong': '🇭🇰 홍콩',
        'taiwan': '🇹🇼 대만',
        'singapore': '🇸🇬 싱가포르',
        'india': '🇮🇳 인도'
    }
    
    selected_countries = st.multiselect(
        "국가 선택 (복수 선택 가능)",
        country_options,
        default=country_options[:3],  # 기본으로 처음 3개 선택
        format_func=lambda x: country_names.get(x, x)
    )
    
    if not selected_countries:
        st.info("분석할 국가를 선택해주세요.")
        return
    
    # 선택된 국가들의 주식 데이터 통합
    all_stocks = []
    
    for country in selected_countries:
        country_stocks = stocks_data.get(country, [])
        for stock in country_stocks:
            stock['country'] = country_names.get(country, country)
            all_stocks.append(stock)
    
    if not all_stocks:
        st.warning("선택된 국가의 주식 데이터가 없습니다.")
        return
    
    # 정렬 옵션
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sort_by = st.selectbox(
            "정렬 기준",
            ["시가총액", "변화율", "거래량", "주가"]
        )
    
    with col2:
        sort_order = st.selectbox("정렬 순서", ["내림차순", "오름차순"])
    
    with col3:
        show_count = st.selectbox("표시 개수", [10, 20, 30, 50], index=1)
    
    # 정렬 적용
    sort_key_map = {
        "시가총액": "market_cap",
        "변화율": "change_percent", 
        "거래량": "volume",
        "주가": "current_price"
    }
    
    sort_key = sort_key_map[sort_by]
    reverse = (sort_order == "내림차순")
    
    # 시가총액이 숫자가 아닌 경우 처리
    for stock in all_stocks:
        if not isinstance(stock.get('market_cap'), (int, float)):
            stock['market_cap'] = 0
    
    sorted_stocks = sorted(all_stocks, key=lambda x: x.get(sort_key, 0), reverse=reverse)[:show_count]
    
    # 주식 테이블 표시
    stocks_table = []
    
    for stock in sorted_stocks:
        market_cap = stock.get('market_cap', 0)
        market_cap_str = f"{market_cap/1e9:.1f}B" if market_cap > 1e9 else f"{market_cap/1e6:.1f}M" if market_cap > 1e6 else str(market_cap)
        
        stocks_table.append({
            '국가': stock['country'],
            '종목명': stock['name'],
            '심볼': stock['symbol'],
            '섹터': stock['sector'],
            '현재가': f"{stock['current_price']:.2f}",
            '변화': f"{stock['change']:+.2f}",
            '변화율': f"{stock['change_percent']:+.2f}%",
            '거래량': f"{stock['volume']:,}",
            '시가총액': market_cap_str,
            'P/E': stock.get('pe_ratio', 'N/A'),
            '배당수익률': f"{stock.get('dividend_yield', 0)*100:.2f}%" if isinstance(stock.get('dividend_yield'), (int, float)) else 'N/A',
            '통화': stock['currency']
        })
    
    if stocks_table:
        df = pd.DataFrame(stocks_table)
        
        # 스타일링된 테이블
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "변화율": st.column_config.NumberColumn(
                    "변화율",
                    format="%.2f%%"
                )
            }
        )
        
        # 상위 종목 상세 정보
        st.subheader("🔍 상위 종목 상세 정보")
        
        for i, stock in enumerate(sorted_stocks[:5], 1):
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    change_color = "🟢" if stock['change_percent'] > 0 else "🔴" if stock['change_percent'] < 0 else "🟡"
                    st.markdown(f"### {i}. {change_color} {stock['name']}")
                    st.caption(f"{stock['country']} • {stock['sector']} • {stock['symbol']}")
                
                with col2:
                    st.metric("현재가", f"{stock['current_price']:.2f}")
                    st.caption(stock['currency'])
                
                with col3:
                    st.metric("변화율", f"{stock['change_percent']:+.2f}%")
                    st.caption(f"{stock['change']:+.2f}")
                
                with col4:
                    st.link_button("📊 상세", stock['yahoo_finance_url'])
                
                # 추가 정보
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    market_cap = stock.get('market_cap', 0)
                    if market_cap > 1e9:
                        st.write(f"**시가총액**: {market_cap/1e9:.1f}B {stock['currency']}")
                    elif market_cap > 1e6:
                        st.write(f"**시가총액**: {market_cap/1e6:.1f}M {stock['currency']}")
                    else:
                        st.write(f"**시가총액**: {market_cap:,} {stock['currency']}")
                
                with col2:
                    st.write(f"**거래량**: {stock['volume']:,}")
                    pe_ratio = stock.get('pe_ratio', 'N/A')
                    st.write(f"**P/E 비율**: {pe_ratio}")
                
                with col3:
                    dividend_yield = stock.get('dividend_yield', 0)
                    if isinstance(dividend_yield, (int, float)) and dividend_yield > 0:
                        st.write(f"**배당수익률**: {dividend_yield*100:.2f}%")
                    else:
                        st.write(f"**배당수익률**: N/A")
                
                st.markdown("---")

def show_country_analysis(asian_data):
    """국가별 분석"""
    st.subheader("🌍 국가별 시장 분석")
    
    indices = asian_data.get('market_indices', {})
    stocks_data = asian_data.get('major_stocks', {})
    
    country_names = {
        'korea': '🇰🇷 한국',
        'japan': '🇯🇵 일본', 
        'china': '🇨🇳 중국',
        'hongkong': '🇭🇰 홍콩',
        'taiwan': '🇹🇼 대만',
        'singapore': '🇸🇬 싱가포르',
        'india': '🇮🇳 인도'
    }
    
    # 국가별 요약 카드
    for country_key, country_name in country_names.items():
        if country_key in indices:
            index_data = indices[country_key]
            country_stocks = stocks_data.get(country_key, [])
            
            with st.container():
                st.markdown(f"### {country_name}")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if 'current_price' in index_data:
                        st.metric(
                            index_data['index_name'],
                            f"{index_data['current_price']:,.2f}",
                            f"{index_data['change_percent']:+.2f}%"
                        )
                
                with col2:
                    st.metric("주요 종목 수", len(country_stocks))
                    market_status = "🟢 개장" if index_data.get('market_status') == 'open' else "🔴 폐장"
                    st.write(f"**상태**: {market_status}")
                
                with col3:
                    if country_stocks:
                        avg_change = sum(stock.get('change_percent', 0) for stock in country_stocks) / len(country_stocks)
                        st.metric("평균 주식 변화율", f"{avg_change:+.2f}%")
                
                with col4:
                    # 관련 링크
                    if 'symbol' in index_data:
                        yahoo_link = f"https://finance.yahoo.com/quote/{index_data['symbol']}"
                        st.link_button("📊 지수 차트", yahoo_link)
                
                # 해당 국가 상위 3개 종목
                if country_stocks:
                    st.write("**주요 종목 TOP 3:**")
                    
                    top_3_stocks = sorted(country_stocks, key=lambda x: x.get('market_cap', 0), reverse=True)[:3]
                    
                    for i, stock in enumerate(top_3_stocks, 1):
                        change_emoji = "🟢" if stock['change_percent'] > 0 else "🔴" if stock['change_percent'] < 0 else "🟡"
                        st.write(f"{i}. {change_emoji} **{stock['name']}** ({stock['change_percent']:+.2f}%) - {stock['sector']}")
                
                st.markdown("---")

def show_sector_analysis(asian_data):
    """섹터별 분석"""
    st.subheader("📈 섹터별 분석")
    
    stocks_data = asian_data.get('major_stocks', {})
    
    # 모든 주식을 섹터별로 그룹화
    sector_data = {}
    
    for country, stocks in stocks_data.items():
        for stock in stocks:
            sector = stock.get('sector', 'Unknown')
            if sector not in sector_data:
                sector_data[sector] = []
            
            stock_copy = stock.copy()
            stock_copy['country'] = country
            sector_data[sector].append(stock_copy)
    
    if not sector_data:
        st.warning("섹터 데이터가 없습니다.")
        return
    
    # 섹터별 통계
    sector_stats = []
    
    for sector, stocks in sector_data.items():
        if stocks:
            avg_change = sum(stock.get('change_percent', 0) for stock in stocks) / len(stocks)
            total_market_cap = sum(stock.get('market_cap', 0) for stock in stocks if isinstance(stock.get('market_cap'), (int, float)))
            
            sector_stats.append({
                '섹터': sector,
                '종목 수': len(stocks),
                '평균 변화율': round(avg_change, 2),
                '총 시가총액': total_market_cap,
                '대표 종목': max(stocks, key=lambda x: x.get('market_cap', 0))['name']
            })
    
    # 섹터별 성과 차트
    if sector_stats:
        sector_df = pd.DataFrame(sector_stats)
        sector_df = sector_df.sort_values('평균 변화율', ascending=False)
        
        fig = px.bar(
            sector_df,
            x='섹터',
            y='평균 변화율',
            title="섹터별 평균 변화율 (%)",
            color='평균 변화율',
            color_continuous_scale=['red', 'yellow', 'green'],
            text='평균 변화율'
        )
        
        fig.update_traces(texttemplate='%{text:+.1f}%', textposition='outside')
        fig.update_layout(height=400, xaxis_tickangle=-45)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 섹터별 상세 테이블
        st.subheader("📊 섹터별 상세 통계")
        
        display_df = sector_df.copy()
        display_df['총 시가총액'] = display_df['총 시가총액'].apply(
            lambda x: f"{x/1e12:.1f}T" if x > 1e12 else f"{x/1e9:.1f}B" if x > 1e9 else f"{x/1e6:.1f}M"
        )
        display_df['평균 변화율'] = display_df['평균 변화율'].apply(lambda x: f"{x:+.2f}%")
        
        st.dataframe(display_df, use_container_width=True)
        
        # 섹터별 상위 종목
        st.subheader("🏆 섹터별 상위 종목")
        
        selected_sector = st.selectbox(
            "섹터 선택",
            list(sector_data.keys())
        )
        
        if selected_sector and selected_sector in sector_data:
            sector_stocks = sector_data[selected_sector]
            sector_stocks.sort(key=lambda x: x.get('market_cap', 0), reverse=True)
            
            for i, stock in enumerate(sector_stocks[:5], 1):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    change_emoji = "🟢" if stock['change_percent'] > 0 else "🔴" if stock['change_percent'] < 0 else "🟡"
                    st.write(f"**{i}. {change_emoji} {stock['name']}**")
                    
                    country_names = {
                        'korea': '🇰🇷 한국', 'japan': '🇯🇵 일본', 'china': '🇨🇳 중국',
                        'hongkong': '🇭🇰 홍콩', 'taiwan': '🇹🇼 대만', 'singapore': '🇸🇬 싱가포르', 'india': '🇮🇳 인도'
                    }
                    country_name = country_names.get(stock['country'], stock['country'])
                    st.caption(f"{country_name} • {stock['symbol']}")
                
                with col2:
                    st.metric("현재가", f"{stock['current_price']:.2f}")
                
                with col3:
                    st.metric("변화율", f"{stock['change_percent']:+.2f}%")
                
                with col4:
                    st.link_button("📊 상세", stock['yahoo_finance_url'])

if __name__ == "__main__":
    show_asian_markets_page()
