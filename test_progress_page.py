#!/usr/bin/env python3
"""
진행률 표시 테스트 페이지
"""

import streamlit as st
import time
from datetime import datetime
import yfinance as yf

def test_progress_display():
    """진행률 표시 테스트"""
    
    st.title("📊 진행률 표시 테스트")
    st.markdown("---")
    
    if st.button("🚀 테스트 시작", type="primary"):
        
        # 진행률 표시 컨테이너
        st.subheader("📈 데이터 수집 진행 상황")
        
        # 진행률 바
        progress_bar = st.progress(0)
        
        # 상태 텍스트
        status_text = st.empty()
        
        # 로그 컨테이너
        st.markdown("#### 📝 실시간 로그")
        log_container = st.empty()
        
        # 수집 통계
        col1, col2, col3 = st.columns(3)
        with col1:
            metric1 = st.empty()
        with col2:
            metric2 = st.empty()
        with col3:
            metric3 = st.empty()
        
        # 로그 저장
        logs = []
        
        def add_log(message, level="INFO"):
            timestamp = datetime.now().strftime("%H:%M:%S")
            emoji = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}.get(level, "📝")
            log_entry = f"{emoji} [{timestamp}] {message}"
            logs.append(log_entry)
            
            # 최근 10개 로그만 표시
            recent_logs = logs[-10:]
            log_container.text("\n".join(recent_logs))
        
        def update_progress(current, total, message=""):
            progress = current / total if total > 0 else 0
            progress_bar.progress(progress)
            status_text.text(f"진행률: {current}/{total} ({progress*100:.1f}%) - {message}")
        
        try:
            # 테스트 시작
            add_log("🚀 데이터 수집 테스트를 시작합니다", "SUCCESS")
            time.sleep(1)
            
            # 1단계: Alpha Vantage 테스트
            add_log("📈 Alpha Vantage 데이터 수집 중...", "INFO")
            metric1.metric("Alpha Vantage", "수집 중...", "🔄")
            update_progress(1, 10, "Alpha Vantage API 호출")
            time.sleep(2)
            
            metric1.metric("Alpha Vantage", "완료", "✅")
            add_log("✅ Alpha Vantage 데이터 수집 완료", "SUCCESS")
            
            # 2단계: 주식 데이터 수집 시뮬레이션
            symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
            
            add_log("🌍 주식 데이터 수집 시작", "INFO")
            metric2.metric("주식 데이터", "수집 중...", "🔄")
            
            for i, symbol in enumerate(symbols):
                update_progress(i + 2, 10, f"{symbol} 처리 중...")
                add_log(f"🔍 {symbol} 데이터 수집 중...", "INFO")
                
                try:
                    # 실제 데이터 수집
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='1d')
                    
                    if not hist.empty:
                        price = hist['Close'].iloc[-1]
                        add_log(f"✅ {symbol}: ${price:.2f}", "SUCCESS")
                    else:
                        add_log(f"⚠️ {symbol}: 데이터 없음", "WARNING")
                        
                except Exception as e:
                    add_log(f"❌ {symbol}: 오류 - {str(e)}", "ERROR")
                
                time.sleep(1)  # 진행률 표시를 위한 지연
            
            metric2.metric("주식 데이터", f"{len(symbols)}개 완료", "✅")
            add_log(f"✅ 주식 데이터 수집 완료: {len(symbols)}개", "SUCCESS")
            
            # 3단계: 분석 단계
            add_log("📊 데이터 분석 중...", "INFO")
            metric3.metric("데이터 분석", "분석 중...", "🔄")
            update_progress(8, 10, "트렌드 분석 중...")
            time.sleep(2)
            
            metric3.metric("데이터 분석", "완료", "✅")
            add_log("✅ 데이터 분석 완료", "SUCCESS")
            
            # 완료
            update_progress(10, 10, "모든 작업 완료!")
            progress_bar.progress(1.0)
            status_text.success("✅ 모든 데이터 수집이 완료되었습니다!")
            add_log("🎉 전체 작업 완료!", "SUCCESS")
            
            st.balloons()  # 축하 효과
            
        except Exception as e:
            add_log(f"💥 오류 발생: {str(e)}", "ERROR")
            status_text.error(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    test_progress_display()
