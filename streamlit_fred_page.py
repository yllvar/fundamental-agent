#!/usr/bin/env python3
"""
FRED 경제 지표 상세 페이지
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

def show_fred_page(fred_data):
    """FRED 경제 지표 상세 페이지"""
    st.header("📊 FRED 경제 지표 상세 분석")
    
    if fred_data.get('status') != 'success':
        st.error(f"❌ FRED 데이터 로드 실패: {fred_data.get('error', 'Unknown')}")
        return
    
    fred_info = fred_data.get('data', {})
    indicators = fred_info.get('indicators', {})
    summary = fred_data.get('summary', {})
    
    # 요약 정보
    st.subheader("📈 FRED 데이터 요약")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "수집된 지표",
            summary.get('collected_indicators', 0),
            f"총 {summary.get('total_indicators', 0)}개 중"
        )
    
    with col2:
        highlights = summary.get('key_highlights', {})
        if 'interest_rates' in highlights:
            fed_rate = highlights['interest_rates']
            st.metric(
                "연방기금금리",
                f"{fed_rate.get('federal_funds_rate', 0):.2f}%",
                f"{fed_rate.get('change', 0):+.2f}%"
            )
    
    with col3:
        if 'employment' in highlights:
            employment = highlights['employment']
            st.metric(
                "실업률",
                f"{employment.get('unemployment_rate', 0):.1f}%",
                employment.get('trend', '보합')
            )
    
    with col4:
        if 'inflation' in highlights:
            inflation = highlights['inflation']
            st.metric(
                "인플레이션",
                f"{inflation.get('cpi_change', 0):+.1f}%",
                inflation.get('trend', '보합')
            )
    
    st.markdown("---")
    
    # 탭으로 구분
    tab1, tab2, tab3, tab4 = st.tabs(["🏦 금리 정책", "💼 고용 시장", "💰 인플레이션", "📊 전체 지표"])
    
    with tab1:
        st.subheader("🏦 금리 및 통화 정책")
        
        # 금리 관련 지표들
        interest_indicators = [
            'federal_funds_rate', '10_year_treasury', '3_month_treasury', 'mortgage_rate'
        ]
        
        interest_data = []
        for indicator_key in interest_indicators:
            if indicator_key in indicators:
                indicator = indicators[indicator_key]
                interest_data.append({
                    '지표명': indicator.get('title', indicator_key),
                    '현재값': f"{indicator.get('latest_value', 0):.2f}%",
                    '이전값': f"{indicator.get('previous_value', 0):.2f}%",
                    '변화': f"{indicator.get('change', 0):+.4f}%",
                    '변화율': f"{indicator.get('change_percent', 0):+.2f}%",
                    '최신 날짜': indicator.get('latest_date', 'N/A'),
                    '단위': indicator.get('units', ''),
                    'FRED 링크': f"https://fred.stlouisfed.org/series/{indicator.get('series_id', '')}"
                })
        
        if interest_data:
            df = pd.DataFrame(interest_data)
            
            # 링크가 포함된 테이블 표시
            for idx, row in df.iterrows():
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                
                with col1:
                    st.write(f"**{row['지표명']}**")
                    st.caption(f"최신: {row['최신 날짜']}")
                
                with col2:
                    st.metric("현재값", row['현재값'])
                
                with col3:
                    st.metric("변화", row['변화'])
                
                with col4:
                    st.metric("변화율", row['변화율'])
                
                with col5:
                    st.link_button("📊 FRED", row['FRED 링크'])
                
                st.markdown("---")
            
            # 금리 트렌드 차트
            create_fred_trend_chart(indicators, interest_indicators, "금리 트렌드")
    
    with tab2:
        st.subheader("💼 고용 시장 지표")
        
        employment_indicators = [
            'unemployment_rate', 'nonfarm_payrolls', 'labor_force_participation', 'initial_claims'
        ]
        
        employment_data = []
        for indicator_key in employment_indicators:
            if indicator_key in indicators:
                indicator = indicators[indicator_key]
                employment_data.append({
                    '지표명': indicator.get('title', indicator_key),
                    '현재값': f"{indicator.get('latest_value', 0):,.1f}",
                    '이전값': f"{indicator.get('previous_value', 0):,.1f}",
                    '변화': f"{indicator.get('change', 0):+,.2f}",
                    '변화율': f"{indicator.get('change_percent', 0):+.2f}%",
                    '최신 날짜': indicator.get('latest_date', 'N/A'),
                    '단위': indicator.get('units', ''),
                    'FRED 링크': f"https://fred.stlouisfed.org/series/{indicator.get('series_id', '')}"
                })
        
        if employment_data:
            df = pd.DataFrame(employment_data)
            
            for idx, row in df.iterrows():
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                
                with col1:
                    st.write(f"**{row['지표명']}**")
                    st.caption(f"최신: {row['최신 날짜']}")
                
                with col2:
                    st.metric("현재값", row['현재값'])
                
                with col3:
                    st.metric("변화", row['변화'])
                
                with col4:
                    st.metric("변화율", row['변화율'])
                
                with col5:
                    st.link_button("📊 FRED", row['FRED 링크'])
                
                st.markdown("---")
            
            create_fred_trend_chart(indicators, employment_indicators, "고용 시장 트렌드")
    
    with tab3:
        st.subheader("💰 인플레이션 지표")
        
        inflation_indicators = [
            'cpi', 'core_cpi', 'pce', 'core_pce'
        ]
        
        inflation_data = []
        for indicator_key in inflation_indicators:
            if indicator_key in indicators:
                indicator = indicators[indicator_key]
                inflation_data.append({
                    '지표명': indicator.get('title', indicator_key),
                    '현재값': f"{indicator.get('latest_value', 0):,.1f}",
                    '이전값': f"{indicator.get('previous_value', 0):,.1f}",
                    '변화': f"{indicator.get('change', 0):+,.2f}",
                    '변화율': f"{indicator.get('change_percent', 0):+.2f}%",
                    '최신 날짜': indicator.get('latest_date', 'N/A'),
                    '단위': indicator.get('units', ''),
                    'FRED 링크': f"https://fred.stlouisfed.org/series/{indicator.get('series_id', '')}"
                })
        
        if inflation_data:
            df = pd.DataFrame(inflation_data)
            
            for idx, row in df.iterrows():
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                
                with col1:
                    st.write(f"**{row['지표명']}**")
                    st.caption(f"최신: {row['최신 날짜']}")
                
                with col2:
                    st.metric("현재값", row['현재값'])
                
                with col3:
                    st.metric("변화", row['변화'])
                
                with col4:
                    st.metric("변화율", row['변화율'])
                
                with col5:
                    st.link_button("📊 FRED", row['FRED 링크'])
                
                st.markdown("---")
            
            create_fred_trend_chart(indicators, inflation_indicators, "인플레이션 트렌드")
    
    with tab4:
        st.subheader("📊 전체 FRED 지표")
        
        # 모든 지표를 카테고리별로 표시
        all_indicators_data = []
        
        for indicator_key, indicator in indicators.items():
            all_indicators_data.append({
                '지표명': indicator.get('title', indicator_key),
                '시리즈 ID': indicator.get('series_id', ''),
                '현재값': f"{indicator.get('latest_value', 0):,.2f}",
                '단위': indicator.get('units', ''),
                '변화율': f"{indicator.get('change_percent', 0):+.2f}%",
                '최신 날짜': indicator.get('latest_date', 'N/A'),
                '주기': indicator.get('frequency', ''),
                'FRED 링크': f"https://fred.stlouisfed.org/series/{indicator.get('series_id', '')}"
            })
        
        if all_indicators_data:
            df = pd.DataFrame(all_indicators_data)
            
            # 검색 기능
            search_term = st.text_input("🔍 지표 검색", placeholder="지표명 또는 시리즈 ID 입력")
            
            if search_term:
                df = df[df['지표명'].str.contains(search_term, case=False, na=False) | 
                       df['시리즈 ID'].str.contains(search_term, case=False, na=False)]
            
            # 정렬 옵션
            sort_by = st.selectbox("정렬 기준", ['지표명', '변화율', '최신 날짜'])
            ascending = st.checkbox("오름차순", value=True)
            
            df_sorted = df.sort_values(by=sort_by, ascending=ascending)
            
            # 페이지네이션
            items_per_page = st.selectbox("페이지당 항목 수", [10, 20, 50], index=1)
            
            total_items = len(df_sorted)
            total_pages = (total_items - 1) // items_per_page + 1
            
            if total_pages > 1:
                page_num = st.number_input("페이지", min_value=1, max_value=total_pages, value=1)
                start_idx = (page_num - 1) * items_per_page
                end_idx = start_idx + items_per_page
                df_page = df_sorted.iloc[start_idx:end_idx]
            else:
                df_page = df_sorted
            
            # 테이블 표시 (링크 포함)
            for idx, row in df_page.iterrows():
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**{row['지표명']}**")
                        st.caption(f"ID: {row['시리즈 ID']} | {row['주기']}")
                    
                    with col2:
                        st.write(f"{row['현재값']} {row['단위']}")
                        st.caption(row['최신 날짜'])
                    
                    with col3:
                        change_color = "green" if "+" in row['변화율'] else "red" if "-" in row['변화율'] else "gray"
                        st.markdown(f"<span style='color: {change_color}'>{row['변화율']}</span>", unsafe_allow_html=True)
                    
                    with col4:
                        st.link_button("📊 FRED", row['FRED 링크'])
                    
                    with col5:
                        # 차트 보기 버튼 (향후 구현)
                        if st.button(f"📈", key=f"chart_{idx}"):
                            st.info(f"{row['지표명']} 차트 기능은 향후 구현 예정입니다.")
                    
                    st.markdown("---")
            
            # 페이지 정보
            if total_pages > 1:
                st.write(f"페이지 {page_num}/{total_pages} (총 {total_items}개 지표)")

def create_fred_trend_chart(indicators, indicator_keys, title):
    """FRED 지표 트렌드 차트 생성"""
    
    fig = make_subplots(
        rows=len(indicator_keys), cols=1,
        subplot_titles=[indicators.get(key, {}).get('title', key) for key in indicator_keys if key in indicators],
        vertical_spacing=0.1
    )
    
    for i, indicator_key in enumerate(indicator_keys, 1):
        if indicator_key in indicators:
            indicator = indicators[indicator_key]
            historical_data = indicator.get('historical_data', [])
            
            if historical_data:
                dates = [item['date'] for item in historical_data]
                values = [item['value'] for item in historical_data]
                
                fig.add_trace(
                    go.Scatter(
                        x=dates,
                        y=values,
                        mode='lines+markers',
                        name=indicator.get('title', indicator_key),
                        line=dict(width=2)
                    ),
                    row=i, col=1
                )
    
    fig.update_layout(
        title=title,
        height=200 * len(indicator_keys),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
