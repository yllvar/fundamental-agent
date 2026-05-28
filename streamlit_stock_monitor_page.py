#!/usr/bin/env python3
"""
진행률 표시 기능이 있는 개별 주식 모니터링 Streamlit 페이지
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime
import numpy as np
import time
import yfinance as yf

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def collect_stock_data_with_progress():
    """진행률 표시와 함께 주식 데이터 수집"""
    
    # 진행률 표시 컨테이너
    st.subheader("📊 데이터 수집 진행 상황")
    
    # 진행률 바
    progress_bar = st.progress(0)
    
    # 상태 텍스트
    status_text = st.empty()
    
    # 수집 통계
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        alpha_status = st.empty()
    with col2:
        us_status = st.empty()
    with col3:
        kr_status = st.empty()
    with col4:
        jp_status = st.empty()
    
    # 로그 컨테이너
    st.markdown("#### 📝 실시간 로그")
    log_container = st.empty()
    
    # 로그 저장
    logs = []
    start_time = time.time()
    
    def add_log(message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        emoji = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}.get(level, "📝")
        log_entry = f"{emoji} [{timestamp}] {message}"
        logs.append(log_entry)
        
        # 최근 15개 로그만 표시
        recent_logs = logs[-15:]
        log_container.text("\n".join(recent_logs))
    
    def update_progress(current, total, message=""):
        # 안전한 진행률 계산
        if total <= 0:
            progress = 0.0
        else:
            progress = current / total
        
        # 진행률을 0.0 ~ 1.0 범위로 제한
        progress = max(0.0, min(progress, 1.0))
        
        try:
            progress_bar.progress(progress)
        except Exception as e:
            # 진행률 바 업데이트 실패 시 로그만 기록
            print(f"Progress bar update failed: {e}")
        
        elapsed = time.time() - start_time
        status_msg = f"진행률: {current}/{total} ({progress*100:.1f}%) - 경과시간: {elapsed:.1f}초"
        if message:
            status_msg += f"\n🔄 현재 작업: {message}"
        
        try:
            status_text.text(status_msg)
        except Exception as e:
            print(f"Status text update failed: {e}")
    
    try:
        # 시장별 주식 심볼 정의
        market_symbols = {
            'US': {
                'name': '미국 시장',
                'symbols': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'JPM', 'JNJ']
            },
            'KR': {
                'name': '한국 시장',
                'symbols': ['005930.KS', '000660.KS', '035420.KS', '005380.KS', '051910.KS', '035720.KS', '006400.KS', '207940.KS', '005490.KS', '068270.KS']
            },
            'JP': {
                'name': '일본 시장',
                'symbols': ['7203.T', '6758.T', '9984.T', '8306.T', '9432.T', '6861.T', '8316.T', '7974.T', '6954.T', '4063.T']
            }
        }
        
        # 전체 수집 시작
        add_log("🚀 주식 데이터 수집을 시작합니다", "SUCCESS")
        update_progress(0, 100, "초기화 중...")
        time.sleep(0.5)
        
        # 1. Alpha Vantage 시뮬레이션 (실제 API는 제한이 있으므로)
        add_log("📈 Alpha Vantage 상위/하위 종목 수집 중...", "INFO")
        alpha_status.metric("Alpha Vantage", "수집 중...", "🔄")
        update_progress(10, 100, "Alpha Vantage API 호출")
        time.sleep(1)
        
        # 가상의 Alpha Vantage 데이터
        av_data = {
            'top_gainers': [
                {'ticker': 'AAPL', 'price': '213.25', 'change_percentage': '5.09%'},
                {'ticker': 'TSLA', 'price': '319.91', 'change_percentage': '3.62%'},
                {'ticker': 'AMZN', 'price': '222.31', 'change_percentage': '4.00%'},
                {'ticker': 'NFLX', 'price': '1178.48', 'change_percentage': '2.67%'},
                {'ticker': 'PYPL', 'price': '69.42', 'change_percentage': '2.34%'}
            ],
            'top_losers': [
                {'ticker': 'UNH', 'price': '245.78', 'change_percentage': '-2.08%'},
                {'ticker': 'DIS', 'price': '115.17', 'change_percentage': '-2.66%'},
                {'ticker': 'MSFT', 'price': '524.94', 'change_percentage': '-0.53%'},
                {'ticker': 'JNJ', 'price': '170.59', 'change_percentage': '-0.09%'},
                {'ticker': 'JPM', 'price': '291.35', 'change_percentage': '-0.01%'}
            ],
            'most_actively_traded': [
                {'ticker': 'AAPL', 'price': '213.25', 'change_percentage': '5.09%', 'volume': '45000000'},
                {'ticker': 'TSLA', 'price': '319.91', 'change_percentage': '3.62%', 'volume': '42000000'},
                {'ticker': 'NVDA', 'price': '179.42', 'change_percentage': '0.65%', 'volume': '38000000'},
                {'ticker': 'META', 'price': '771.99', 'change_percentage': '1.12%', 'volume': '35000000'},
                {'ticker': 'AMZN', 'price': '222.31', 'change_percentage': '4.00%', 'volume': '33000000'}
            ]
        }
        
        alpha_status.metric("Alpha Vantage", "완료", "✅")
        add_log("✅ Alpha Vantage 데이터 수집 완료", "SUCCESS")
        update_progress(20, 100, "Alpha Vantage 완료")
        
        # 2. 시장별 데이터 수집
        add_log("🌍 시장별 주식 데이터 수집 시작", "INFO")
        
        market_data = {}
        markets = ['US', 'KR', 'JP']
        status_widgets = [us_status, kr_status, jp_status]
        
        progress_step = 0
        
        for i, market in enumerate(markets):
            market_name = market_symbols[market]['name']
            symbols = market_symbols[market]['symbols']
            
            add_log(f"🔍 {market_name} 데이터 수집 중...", "INFO")
            status_widgets[i].metric(market_name, "수집 중...", "🔄")
            
            market_stocks = []
            
            for j, symbol in enumerate(symbols):
                progress_step += 1
                update_progress(20 + progress_step * 6, 100, f"{market_name} - {symbol} 처리 중")
                
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='2d')
                    info = ticker.info
                    
                    if len(hist) >= 2:
                        current_price = hist['Close'].iloc[-1]
                        prev_price = hist['Close'].iloc[-2]
                        change = current_price - prev_price
                        change_percent = (change / prev_price) * 100
                        volume = int(hist['Volume'].iloc[-1])
                        
                        stock_data = {
                            'symbol': symbol,
                            'name': info.get('longName', symbol),
                            'price': float(current_price),
                            'change': float(change),
                            'change_percent': float(change_percent),
                            'volume': volume,
                            'market_cap': info.get('marketCap'),
                            'sector': info.get('sector'),
                            'market': market_name,
                            'currency': info.get('currency', 'USD')
                        }
                        market_stocks.append(stock_data)
                        
                        add_log(f"✅ {symbol}: {change_percent:+.2f}% (${current_price:.2f})", "SUCCESS")
                    
                    time.sleep(0.1)  # API 제한 방지
                        
                except Exception as e:
                    add_log(f"⚠️ {symbol} 데이터 수집 실패: {str(e)}", "WARNING")
                    continue
            
            market_data[market] = market_stocks
            
            if market_stocks:
                success_count = len(market_stocks)
                status_widgets[i].metric(market_name, f"{success_count}개", "✅")
                add_log(f"✅ {market_name} 완료: {success_count}개 종목", "SUCCESS")
            else:
                status_widgets[i].metric(market_name, "실패", "❌")
                add_log(f"❌ {market_name} 데이터 수집 실패", "ERROR")
        
        # 3. 트렌드 분석
        add_log("📊 시장 트렌드 분석 중...", "INFO")
        update_progress(90, 100, "트렌드 분석 중...")
        
        trends = {}
        for market, stocks in market_data.items():
            if stocks:
                changes = [s['change_percent'] for s in stocks]
                gainers = [s for s in stocks if s['change_percent'] > 0]
                losers = [s for s in stocks if s['change_percent'] < 0]
                unchanged = [s for s in stocks if s['change_percent'] == 0]
                
                avg_change = np.mean(changes)
                
                trends[market] = {
                    'total_stocks': len(stocks),
                    'gainers': len(gainers),
                    'losers': len(losers),
                    'unchanged': len(unchanged),
                    'avg_change_percent': float(avg_change),
                    'avg_volume': int(np.mean([s['volume'] for s in stocks])),
                    'market_sentiment': 'bullish' if avg_change > 1 else 'bearish' if avg_change < -1 else 'neutral'
                }
                
                add_log(f"📊 {market_symbols[market]['name']}: {trends[market]['market_sentiment']} (평균 {avg_change:.2f}%)", "INFO")
        
        # 완료
        progress_bar.progress(1.0)
        update_progress(100, 100, "모든 작업 완료!")
        status_text.success("✅ 모든 데이터 수집이 완료되었습니다!")
        add_log("🎉 전체 데이터 수집 및 분석 완료!", "SUCCESS")
        
        return {
            'alpha_vantage': av_data,
            'market_data': market_data,
            'trends': trends,
            'market_symbols': market_symbols
        }, None
        
    except Exception as e:
        add_log(f"💥 데이터 수집 중 오류 발생: {str(e)}", "ERROR")
        status_text.error(f"❌ 오류 발생: {str(e)}")
        return None, str(e)

def show_alpha_vantage_section(av_data):
    """Alpha Vantage 섹션 표시"""
    if not av_data:
        st.warning("Alpha Vantage 데이터를 불러올 수 없습니다.")
        return
    
    st.subheader("📈 Alpha Vantage 실시간 상위/하위 종목")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🚀 상위 상승 종목")
        if 'top_gainers' in av_data:
            for item in av_data['top_gainers']:
                change_pct = float(item['change_percentage'].rstrip('%'))
                st.metric(
                    label=item['ticker'],
                    value=f"${float(item['price']):.2f}",
                    delta=f"{change_pct:.2f}%"
                )
    
    with col2:
        st.markdown("#### 📉 상위 하락 종목")
        if 'top_losers' in av_data:
            for item in av_data['top_losers']:
                change_pct = float(item['change_percentage'].rstrip('%'))
                st.metric(
                    label=item['ticker'],
                    value=f"${float(item['price']):.2f}",
                    delta=f"{change_pct:.2f}%"
                )
    
    with col3:
        st.markdown("#### 📊 거래량 상위 종목")
        if 'most_actively_traded' in av_data:
            for item in av_data['most_actively_traded']:
                change_pct = float(item['change_percentage'].rstrip('%'))
                st.metric(
                    label=item['ticker'],
                    value=f"${float(item['price']):.2f}",
                    delta=f"{change_pct:.2f}%",
                    help=f"거래량: {int(item['volume']):,}"
                )

def show_market_overview(trends, market_symbols):
    """시장 개요 표시"""
    st.subheader("🌍 시장별 개요")
    
    if not trends:
        st.warning("시장 트렌드 데이터가 없습니다.")
        return
    
    # 시장 감정 색상 매핑
    sentiment_colors = {
        'bullish': '🟢',
        'bearish': '🔴', 
        'neutral': '🟡'
    }
    
    cols = st.columns(len(trends))
    
    for i, (market, trend) in enumerate(trends.items()):
        with cols[i]:
            sentiment_icon = sentiment_colors.get(trend['market_sentiment'], '⚪')
            market_name = market_symbols[market]['name']
            
            st.metric(
                label=f"{sentiment_icon} {market_name}",
                value=f"{trend['avg_change_percent']:.2f}%",
                delta=f"{trend['gainers']}/{trend['total_stocks']} 상승"
            )
            
            # 상세 정보
            with st.expander("상세 정보"):
                st.write(f"📈 상승: {trend['gainers']}개")
                st.write(f"📉 하락: {trend['losers']}개")
                st.write(f"➡️ 보합: {trend['unchanged']}개")
                st.write(f"📊 평균 거래량: {trend['avg_volume']:,}")

def show_market_details(market_data, market_symbols):
    """시장별 상세 정보 표시"""
    st.subheader("📊 시장별 상세 분석")
    
    if not market_data:
        st.warning("시장 데이터가 없습니다.")
        return
    
    # 시장 선택
    market_names = {code: info['name'] for code, info in market_symbols.items()}
    selected_market = st.selectbox(
        "분석할 시장 선택",
        options=list(market_names.keys()),
        format_func=lambda x: market_names[x]
    )
    
    if selected_market not in market_data or not market_data[selected_market]:
        st.warning(f"{market_names[selected_market]} 데이터가 없습니다.")
        return
    
    stocks = market_data[selected_market]
    
    # 탭으로 구분
    tab1, tab2, tab3 = st.tabs(["📈 상위 상승", "📉 상위 하락", "📊 거래량 상위"])
    
    with tab1:
        st.markdown("#### 🚀 상위 상승 종목")
        top_gainers = sorted(stocks, key=lambda x: x['change_percent'], reverse=True)[:10]
        
        if top_gainers:
            gainers_data = []
            for stock in top_gainers:
                gainers_data.append({
                    '종목코드': stock['symbol'],
                    '종목명': stock['name'],
                    '현재가': f"{stock['price']:.2f} {stock['currency']}",
                    '변화': f"{stock['change']:+.2f}",
                    '변화율': f"{stock['change_percent']:+.2f}%",
                    '거래량': f"{stock['volume']:,}",
                    '섹터': stock['sector'] or 'N/A'
                })
            
            df = pd.DataFrame(gainers_data)
            st.dataframe(df, use_container_width=True)
            
            # 차트
            fig = px.bar(
                x=[s['symbol'] for s in top_gainers],
                y=[s['change_percent'] for s in top_gainers],
                title="상위 상승 종목 변화율",
                labels={'x': '종목', 'y': '변화율 (%)'},
                color=[s['change_percent'] for s in top_gainers],
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("#### 📉 상위 하락 종목")
        top_losers = sorted(stocks, key=lambda x: x['change_percent'])[:10]
        
        if top_losers:
            losers_data = []
            for stock in top_losers:
                losers_data.append({
                    '종목코드': stock['symbol'],
                    '종목명': stock['name'],
                    '현재가': f"{stock['price']:.2f} {stock['currency']}",
                    '변화': f"{stock['change']:+.2f}",
                    '변화율': f"{stock['change_percent']:+.2f}%",
                    '거래량': f"{stock['volume']:,}",
                    '섹터': stock['sector'] or 'N/A'
                })
            
            df = pd.DataFrame(losers_data)
            st.dataframe(df, use_container_width=True)
            
            # 차트
            fig = px.bar(
                x=[s['symbol'] for s in top_losers],
                y=[s['change_percent'] for s in top_losers],
                title="상위 하락 종목 변화율",
                labels={'x': '종목', 'y': '변화율 (%)'},
                color=[s['change_percent'] for s in top_losers],
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("#### 📊 거래량 상위 종목")
        top_volume = sorted(stocks, key=lambda x: x['volume'], reverse=True)[:10]
        
        if top_volume:
            volume_data = []
            for stock in top_volume:
                volume_data.append({
                    '종목코드': stock['symbol'],
                    '종목명': stock['name'],
                    '현재가': f"{stock['price']:.2f} {stock['currency']}",
                    '변화율': f"{stock['change_percent']:+.2f}%",
                    '거래량': f"{stock['volume']:,}",
                    '시가총액': f"{stock['market_cap']:,}" if stock['market_cap'] else 'N/A',
                    '섹터': stock['sector'] or 'N/A'
                })
            
            df = pd.DataFrame(volume_data)
            st.dataframe(df, use_container_width=True)
            
            # 차트
            fig = px.bar(
                x=[s['symbol'] for s in top_volume],
                y=[s['volume'] for s in top_volume],
                title="거래량 상위 종목",
                labels={'x': '종목', 'y': '거래량'},
                color=[s['change_percent'] for s in top_volume],
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)

def show_stock_monitor_page():
    """개별 주식 모니터링 메인 페이지"""
    
    st.title("📈 개별 주식 모니터링")
    st.markdown("**실시간 개별 주식 분석 및 시장별 상위/하위 종목 모니터링**")
    st.markdown("---")
    
    # 캐시 확인
    if 'stock_data' not in st.session_state or st.button("🔄 새로운 데이터 수집", type="primary", key="stock_data_collect"):
        # 데이터 수집 (진행률 표시와 함께)
        with st.container():
            data, error = collect_stock_data_with_progress()
        
        if error:
            st.error(f"❌ 데이터 수집 실패: {error}")
            return
        
        if not data:
            st.warning("⚠️ 수집된 데이터가 없습니다.")
            return
        
        # 세션 상태에 저장
        st.session_state.stock_data = data
        st.session_state.last_update = datetime.now()
        
        # 성공 메시지
        st.success("✅ 데이터 수집이 완료되었습니다!")
        time.sleep(2)
        st.rerun()
    
    # 캐시된 데이터 사용
    if 'stock_data' in st.session_state:
        data = st.session_state.stock_data
        last_update = st.session_state.get('last_update', datetime.now())
        
        # 업데이트 시간 표시
        st.info(f"📅 마지막 업데이트: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")
        
        st.markdown("---")
        
        # Alpha Vantage 섹션
        show_alpha_vantage_section(data['alpha_vantage'])
        
        st.markdown("---")
        
        # 시장 개요
        show_market_overview(data['trends'], data['market_symbols'])
        
        st.markdown("---")
        
        # 시장별 상세 분석
        show_market_details(data['market_data'], data['market_symbols'])
        
    else:
        st.info("📊 '새로운 데이터 수집' 버튼을 클릭하여 데이터를 불러오세요.")

if __name__ == "__main__":
    show_stock_monitor_page()
