#!/usr/bin/env python3
"""
종합 경제 모니터링 대시보드 - 멀티페이지 버전
모든 데이터 소스를 링크와 함께 상세 표시
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
import time

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_monitoring.enhanced_data_collector import EnhancedGlobalDataCollector

# 페이지 모듈들 import
from streamlit_fred_page import show_fred_page
from streamlit_news_page import show_news_page
from streamlit_reddit_page import show_social_media_page
from streamlit_asian_markets_page import show_asian_markets_page
from streamlit_network_analysis_page import show_network_analysis_page
from streamlit_enhanced_network_page import create_enhanced_network_page
from streamlit_real_network_page import create_real_network_page
from streamlit_stock_monitor_page import show_stock_monitor_page
from streamlit_ai_article_generator import show_ai_article_generator, generate_article_fallback
from data_monitoring.integrated_event_system import IntegratedEventSystem

# 페이지 설정
st.set_page_config(
    page_title="🧠 종합 경제 모니터링 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 캐시된 데이터 수집 함수
def collect_all_comprehensive_data_with_progress():
    """진행률 표시와 함께 모든 데이터 종합 수집"""
    
    # 진행률 표시 컨테이너
    st.subheader("📊 종합 데이터 수집 진행 상황")
    
    # 진행률 바
    progress_bar = st.progress(0)
    
    # 상태 텍스트
    status_text = st.empty()
    
    # 수집 통계
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        intelligence_status = st.empty()
    with col2:
        fred_status = st.empty()
    with col3:
        news_status = st.empty()
    with col4:
        reddit_status = st.empty()
    
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
        collector = EnhancedGlobalDataCollector()
        
        # 전체 수집 시작
        add_log("🚀 종합 데이터 수집을 시작합니다", "SUCCESS")
        update_progress(0, 100, "초기화 중...")
        time.sleep(0.5)
        
        # 1. Intelligence 데이터 수집
        add_log("🧠 Alpha Vantage Intelligence 데이터 수집 중...", "INFO")
        intelligence_status.metric("Intelligence", "수집 중...", "🔄")
        update_progress(10, 100, "Alpha Vantage Intelligence API 호출")
        
        intelligence_data = collector.collect_intelligence_data()
        
        if intelligence_data:
            intelligence_status.metric("Intelligence", "완료", "✅")
            add_log("✅ Alpha Vantage Intelligence 데이터 수집 완료", "SUCCESS")
        else:
            intelligence_status.metric("Intelligence", "실패", "❌")
            add_log("❌ Alpha Vantage Intelligence 데이터 수집 실패", "ERROR")
        
        update_progress(30, 100, "Intelligence 데이터 완료")
        time.sleep(0.5)
        
        # 2. FRED 데이터 수집
        add_log("📊 FRED 경제 지표 데이터 수집 중...", "INFO")
        fred_status.metric("FRED", "수집 중...", "🔄")
        update_progress(40, 100, "FRED API 호출")
        
        fred_data = collector.collect_fred_data()
        
        if fred_data:
            fred_status.metric("FRED", "완료", "✅")
            add_log("✅ FRED 경제 지표 데이터 수집 완료", "SUCCESS")
        else:
            fred_status.metric("FRED", "실패", "❌")
            add_log("❌ FRED 데이터 수집 실패", "ERROR")
        
        update_progress(60, 100, "FRED 데이터 완료")
        time.sleep(0.5)
        
        # 3. 뉴스 데이터 수집
        add_log("📰 강화된 뉴스 데이터 수집 중...", "INFO")
        news_status.metric("뉴스", "수집 중...", "🔄")
        update_progress(70, 100, "뉴스 API 호출")
        
        news_data = collector.collect_enhanced_news_data()
        
        if news_data:
            news_status.metric("뉴스", "완료", "✅")
            add_log("✅ 강화된 뉴스 데이터 수집 완료", "SUCCESS")
        else:
            news_status.metric("뉴스", "실패", "❌")
            add_log("❌ 뉴스 데이터 수집 실패", "ERROR")
        
        update_progress(90, 100, "뉴스 데이터 완료")
        time.sleep(0.5)
        
        # 4. Reddit 데이터 (추가)
        add_log("📱 Reddit 소셜 데이터 수집 중...", "INFO")
        reddit_status.metric("Reddit", "수집 중...", "🔄")
        update_progress(95, 100, "Reddit API 호출")
        
        # Reddit 데이터는 뉴스 데이터에 포함되어 있음
        reddit_status.metric("Reddit", "완료", "✅")
        add_log("✅ Reddit 소셜 데이터 수집 완료", "SUCCESS")
        
        # 완료
        progress_bar.progress(1.0)
        update_progress(100, 100, "모든 작업 완료!")
        status_text.success("✅ 모든 데이터 수집이 완료되었습니다!")
        add_log("🎉 종합 데이터 수집 및 분석 완료!", "SUCCESS")
        
        return {
            'intelligence': intelligence_data,
            'fred': fred_data,
            'news': news_data,
            'timestamp': datetime.now().isoformat()
        }, None
        
    except Exception as e:
        add_log(f"💥 데이터 수집 중 오류 발생: {str(e)}", "ERROR")
        status_text.error(f"❌ 오류 발생: {str(e)}")
        return None, str(e)

@st.cache_data(ttl=300)  # 5분 캐시
def collect_all_comprehensive_data():
    """캐시된 데이터 수집 (백그라운드용)"""
    try:
        collector = EnhancedGlobalDataCollector()
        
        # 모든 데이터 소스 수집
        intelligence_data = collector.collect_intelligence_data()
        fred_data = collector.collect_fred_data()
        news_data = collector.collect_enhanced_news_data()
        
        return {
            'intelligence': intelligence_data,
            'fred': fred_data,
            'news': news_data,
            'timestamp': datetime.now().isoformat()
        }, None
        
    except Exception as e:
        return None, str(e)

def main():
    """메인 대시보드"""
    
    # 헤더
    st.title("🧠 종합 경제 모니터링 대시보드")
    st.markdown("**실시간 경제 데이터 통합 분석 시스템**")
    st.markdown("---")
    
    # 사이드바 네비게이션
    with st.sidebar:
        st.header("📊 페이지 네비게이션")
        
        page = st.selectbox(
            "페이지 선택",
            [
                "🏠 대시보드 홈",
                "🤖 AI 기사 생성",
                "📊 실시간 이벤트 기반 AI 기사",
                "📈 개별 주식 모니터링",
                "🧠 Alpha Vantage Intelligence",
                "📊 FRED 경제 지표",
                "🌏 아시아 시장 분석",
                "📰 뉴스 분석",
                "📱 소셜미디어 (Reddit)",
                "🕸️ 소셜 네트워크 분석",
                "🚀 개선된 네트워크 분석",
                "📱 실제 Reddit 네트워크 분석",
                "📈 통합 분석",
                "🔍 상세 데이터"
            ]
        )
        
        st.markdown("---")
        
        # 새로고침 버튼
        if st.button("🔄 전체 데이터 새로고침", type="primary", key="sidebar_refresh"):
            st.cache_data.clear()
            st.rerun()
        
        # 업데이트 정보
        st.subheader("⏰ 시스템 정보")
        st.write(f"마지막 업데이트: {datetime.now().strftime('%H:%M:%S')}")
        st.write("캐시 시간: 5분")
        st.write("데이터 소스: 4개")
    
    # 데이터 로딩 - 세션 상태 확인
    if 'comprehensive_data' not in st.session_state or st.button("🔄 새로운 데이터 수집", type="primary", key="comprehensive_data_collect"):
        # 진행률 표시와 함께 데이터 수집
        with st.container():
            all_data, error = collect_all_comprehensive_data_with_progress()
        
        if error:
            st.error(f"❌ 데이터 수집 오류: {error}")
            return
        
        if not all_data:
            st.warning("⚠️ 수집된 데이터가 없습니다.")
            return
        
        # 세션 상태에 저장
        st.session_state.comprehensive_data = all_data
        st.session_state.last_comprehensive_update = datetime.now()
        
        # 성공 메시지
        st.success("✅ 종합 데이터 수집이 완료되었습니다!")
        time.sleep(2)
        st.rerun()
    
    # 캐시된 데이터 사용
    if 'comprehensive_data' in st.session_state:
        all_data = st.session_state.comprehensive_data
        last_update = st.session_state.get('last_comprehensive_update', datetime.now())
        
        # 업데이트 시간 표시
        st.info(f"📅 마지막 업데이트: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.info("📊 '새로운 데이터 수집' 버튼을 클릭하여 데이터를 불러오세요.")
        return
    
    # 페이지별 라우팅
    if page == "🏠 대시보드 홈":
        show_dashboard_home(all_data)
    elif page == "🤖 AI 기사 생성":
        show_ai_article_generator()
    elif page == "📊 실시간 이벤트 기반 AI 기사":
        show_realtime_event_ai_articles(all_data)
    elif page == "📈 개별 주식 모니터링":
        show_stock_monitor_page()
    elif page == "🧠 Alpha Vantage Intelligence":
        show_alpha_vantage_page(all_data['intelligence'])
    elif page == "📊 FRED 경제 지표":
        show_fred_page(all_data['fred'])
    elif page == "🌏 아시아 시장 분석":
        show_asian_markets_page()
    elif page == "📰 뉴스 분석":
        show_news_page(all_data['news'])
    elif page == "📱 소셜미디어 (Reddit)":
        show_social_media_page(all_data['news'])
    elif page == "🕸️ 소셜 네트워크 분석":
        show_network_analysis_page(all_data['news'])
    elif page == "🚀 개선된 네트워크 분석":
        create_enhanced_network_page()
    elif page == "📱 실제 Reddit 네트워크 분석":
        create_real_network_page()
    elif page == "📈 통합 분석":
        show_integrated_analysis(all_data)
    elif page == "🔍 상세 데이터":
        show_detailed_data(all_data)

def show_realtime_event_ai_articles(all_data):
    """실시간 이벤트 기반 AI 기사 생성 페이지"""
    st.header("📊 실시간 이벤트 기반 AI 기사 생성")
    st.markdown("**데이터 모니터링 시스템에서 감지된 실시간 이벤트를 기반으로 AI 기사를 자동 생성합니다.**")
    st.markdown("---")
    
    # 실시간 이벤트 감지 시스템 초기화
    try:
        event_system = IntegratedEventSystem()
        
        # 이벤트 감지 실행
        with st.spinner("🔍 실시간 시장 이벤트 감지 중..."):
            import asyncio
            
            # 비동기 함수를 동기적으로 실행
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            analysis_result = loop.run_until_complete(event_system.run_comprehensive_analysis())
        
        if not analysis_result or 'events' not in analysis_result:
            st.warning("⚠️ 현재 감지된 중요한 시장 이벤트가 없습니다.")
            st.info("💡 시장이 안정적이거나 거래 시간 외일 수 있습니다.")
            return
        
        events = analysis_result['events']
        summary = analysis_result.get('summary', {})
        
        if not events:
            st.warning("⚠️ 현재 감지된 중요한 시장 이벤트가 없습니다.")
            st.info("💡 시장이 안정적이거나 거래 시간 외일 수 있습니다.")
            return
        
        # 감지된 이벤트 표시
        st.subheader(f"🚨 감지된 이벤트 ({len(events)}개)")
        
        # 분석 요약 표시
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 이벤트", f"{summary.get('total_events', 0)}개")
        
        with col2:
            st.metric("시장 감정", summary.get('market_sentiment', 'neutral').upper())
        
        with col3:
            st.metric("위험 수준", summary.get('risk_level', 'low').upper())
        
        with col4:
            st.metric("심각도", summary.get('severity_assessment', 'low').upper())
        
        # 이벤트 요약 테이블
        event_data = []
        for event in events:
            event_data.append({
                '심볼': event.get('symbol', 'N/A'),
                '이벤트 유형': event.get('event_type', 'N/A'),
                '설명': event.get('description', 'N/A')[:50] + '...',
                '심각도': f"{event.get('severity', 0):.2f}",
                '감정': event.get('sentiment', 'neutral')
            })
        
        if event_data:
            df_events = pd.DataFrame(event_data)
            st.dataframe(df_events, use_container_width=True)
        
        # 주요 인사이트 표시
        insights = summary.get('key_insights', [])
        if insights:
            st.subheader("💡 주요 인사이트")
            for i, insight in enumerate(insights, 1):
                st.write(f"{i}. {insight}")
        
        # AI 기사 생성 버튼
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🤖 실시간 이벤트 기반 AI 기사 생성", type="primary", key="realtime_ai_article"):
                # 이벤트를 AI 기사 생성에 적합한 형태로 변환
                formatted_events = []
                for event in events:
                    formatted_events.append({
                        'symbol': event.get('symbol', 'MARKET'),
                        'description': event.get('description', '시장 이벤트'),
                        'sentiment': event.get('sentiment', 'neutral'),
                        'severity': event.get('severity', 0.5),
                        'event_type': event.get('event_type', 'market_event')
                    })
                
                generate_realtime_ai_article(formatted_events)
    
    except Exception as e:
        st.error(f"❌ 이벤트 감지 시스템 오류: {str(e)}")
        st.info("💡 대신 수동으로 AI 기사를 생성하시려면 '🤖 AI 기사 생성' 페이지를 이용하세요.")
        
        # 디버깅 정보 표시
        with st.expander("🔍 디버깅 정보"):
            st.write(f"오류 상세: {str(e)}")
            st.write("시스템이 정상적으로 초기화되지 않았을 수 있습니다.")

def generate_realtime_ai_article(events):
    """실시간 이벤트를 기반으로 AI 기사 생성"""
    
    # 진행률 표시
    progress_container = st.container()
    
    with progress_container:
        st.subheader("🤖 AI 기사 생성 진행 상황")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 가짜 트래커 클래스 (진행률 표시용)
        class StreamlitProgressTracker:
            def __init__(self, progress_bar, status_text):
                self.progress_bar = progress_bar
                self.status_text = status_text
                self.current_step = 0
                self.total_steps = 6
            
            def update_step(self, step, description):
                self.current_step = step
                progress = step / self.total_steps
                self.progress_bar.progress(progress)
                self.status_text.text(f"단계 {step}/{self.total_steps}: {description}")
            
            def add_log(self, message, level="INFO"):
                if level == "SUCCESS":
                    st.success(f"✅ {message}")
                elif level == "ERROR":
                    st.error(f"❌ {message}")
                else:
                    st.info(f"ℹ️ {message}")
        
        # 트래커 초기화
        tracker = StreamlitProgressTracker(progress_bar, status_text)
        
        # AI 기사 생성 실행
        try:
            result = generate_article_fallback(events, tracker)
            
            if result:
                # 진행률 완료
                progress_bar.progress(1.0)
                status_text.text("✅ AI 기사 생성 완료!")
                
                # 결과 표시
                st.success("🎉 실시간 이벤트 기반 AI 기사가 성공적으로 생성되었습니다!")
                
                # 기사 내용 표시
                display_generated_article(result)
                
            else:
                st.error("❌ AI 기사 생성에 실패했습니다.")
                
        except Exception as e:
            st.error(f"💥 AI 기사 생성 중 오류 발생: {str(e)}")

def display_generated_article(result):
    """생성된 기사 표시"""
    
    # 기사 정보
    article = result.get('article', {})
    analysis = result.get('analysis', {})
    review = result.get('review', {})
    images = result.get('images', {})
    
    # 기사 제목 및 메타 정보
    st.markdown("---")
    st.header("📰 생성된 AI 기사")
    
    # 메타 정보
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("감지된 이벤트", f"{analysis.get('total_events', 0)}개")
    
    with col2:
        st.metric("시장 감정", analysis.get('market_sentiment', 'neutral').upper())
    
    with col3:
        st.metric("품질 점수", f"{review.get('quality_score', 0)}/10")
    
    with col4:
        st.metric("기사 길이", f"{len(article.get('content', ''))}자")
    
    # 기사 제목
    st.subheader(f"📰 {article.get('title', '제목 없음')}")
    
    # 기사 내용
    st.markdown("### 📝 기사 내용")
    content = article.get('content', '내용 없음')
    st.markdown(content)
    
    # AI 일러스트레이션 표시
    ai_illustration = images.get('ai_illustration')
    if ai_illustration:
        st.markdown("### 🎨 AI 생성 일러스트레이션")
        
        # 이미지 파일 표시
        image_file = ai_illustration.get('image_file')
        if image_file and image_file.get('image_path'):
            image_path = image_file['image_path']
            if os.path.exists(image_path):
                from PIL import Image
                try:
                    img = Image.open(image_path)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(img, caption="AI 생성 일러스트레이션")
                    with col2:
                        st.image(img, caption="AI 생성 일러스트레이션 (전체 너비)", use_container_width=True)
                    
                    # 이미지 정보
                    st.info(f"""
                    **이미지 정보:**
                    - 모델: {image_file.get('model_used', 'Unknown')}
                    - 파일 크기: {os.path.getsize(image_path)} bytes
                    - 생성 시간: {image_file.get('generated_at', 'Unknown')}
                    """)
                    
                except Exception as e:
                    st.error(f"이미지 로드 오류: {e}")
        
        # 텍스트 설명
        description = ai_illustration.get('description', '')
        if description:
            st.markdown("**📝 일러스트레이션 설명:**")
            st.text_area("AI 생성 설명", value=description, height=150, disabled=True)
    
    # 워드클라우드 표시
    wordcloud = images.get('wordcloud')
    if wordcloud and wordcloud.get('generated') and wordcloud.get('image'):
        st.markdown("### 🔤 키워드 워드클라우드")
        try:
            st.image(wordcloud['image'], caption="기사 핵심 키워드", use_container_width=True)
        except Exception as e:
            st.write(f"워드클라우드 표시 오류: {e}")
            keywords = wordcloud.get('keywords', [])
            if keywords:
                st.write("**주요 키워드:**", ", ".join(list(set(keywords))[:15]))
    
    # 검수 결과
    if review:
        st.markdown("### 🔍 AI 검수 결과")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("품질 점수", f"{review.get('quality_score', 0)}/10")
        
        with col2:
            suggestions = review.get('suggestions', [])
            if suggestions:
                st.write("**개선 제안:**")
                for i, suggestion in enumerate(suggestions[:3], 1):
                    st.write(f"{i}. {suggestion}")
    
    # 다운로드 옵션
    st.markdown("---")
    st.subheader("💾 다운로드 옵션")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 기사 텍스트 다운로드
        content_text = f"# {article.get('title', '제목 없음')}\n\n{article.get('content', '내용 없음')}"
        st.download_button(
            label="📄 기사 텍스트 다운로드",
            data=content_text,
            file_name=f"realtime_ai_article_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )
    
    with col2:
        # 분석 데이터 다운로드
        analysis_data = json.dumps(analysis, indent=2, ensure_ascii=False)
        st.download_button(
            label="📊 분석 데이터 다운로드",
            data=analysis_data,
            file_name=f"realtime_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col3:
        # 전체 결과 다운로드
        full_data = json.dumps(result, indent=2, ensure_ascii=False, default=str)
        st.download_button(
            label="📋 전체 결과 다운로드",
            data=full_data,
            file_name=f"realtime_full_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    """통합 분석 페이지"""
    st.header("📈 통합 분석")
    
    intelligence_data = all_data.get('intelligence', {})
    fred_data = all_data.get('fred', {})
    news_data = all_data.get('news', {})
    
    # 전체 시장 감정 종합
    st.subheader("🎭 종합 시장 감정")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Alpha Vantage 시장 상태
        intel_summary = intelligence_data.get('summary', {})
        open_markets = intel_summary.get('open_markets_count', 0)
        total_markets = intel_summary.get('market_status_count', 0)
        
        if total_markets > 0:
            market_ratio = open_markets / total_markets
            st.metric(
                "글로벌 시장 활성도",
                f"{market_ratio:.1%}",
                f"{open_markets}/{total_markets} 개장"
            )
    
    with col2:
        # FRED 경제 지표 트렌드
        fred_summary = fred_data.get('summary', {})
        highlights = fred_summary.get('key_highlights', {})
        
        if 'growth' in highlights:
            growth_trend = highlights['growth'].get('trend', '보합')
            gdp_rate = highlights['growth'].get('gdp_growth_rate', 0)
            st.metric(
                "경제 성장 동향",
                growth_trend,
                f"GDP: {gdp_rate}%"
            )
    
    with col3:
        # 뉴스 감정 분석
        news_summary = news_data.get('summary', {})
        overall_sentiment = news_summary.get('overall_market_sentiment', {})
        
        if overall_sentiment:
            sentiment_label = overall_sentiment.get('label', '중립')
            sentiment_score = overall_sentiment.get('score', 0)
            st.metric(
                "뉴스 시장 감정",
                sentiment_label,
                f"점수: {sentiment_score:+.3f}"
            )
    
    st.markdown("---")
    
    # 데이터 소스별 상태
    st.subheader("📊 데이터 소스 상태")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        intel_status = intelligence_data.get('status', 'failed')
        status_color = "🟢" if intel_status == 'success' else "🔴"
        st.write(f"{status_color} **Alpha Vantage**")
        st.caption(f"상태: {intel_status}")
        if intel_status == 'success':
            st.caption(f"시장: {intel_summary.get('market_status_count', 0)}개")
    
    with col2:
        fred_status = fred_data.get('status', 'failed')
        status_color = "🟢" if fred_status == 'success' else "🔴"
        st.write(f"{status_color} **FRED**")
        st.caption(f"상태: {fred_status}")
        if fred_status == 'success':
            st.caption(f"지표: {fred_summary.get('collected_indicators', 0)}개")
    
    with col3:
        news_status = news_data.get('status', 'failed')
        status_color = "🟢" if news_status == 'success' else "🔴"
        st.write(f"{status_color} **뉴스**")
        st.caption(f"상태: {news_status}")
        if news_status == 'success':
            st.caption(f"기사: {news_summary.get('total_articles', 0)}개")
    
    with col4:
        social_mentions = news_summary.get('social_mentions', {})
        reddit_posts = social_mentions.get('reddit_posts', 0)
        status_color = "🟢" if reddit_posts > 0 else "🔴"
        st.write(f"{status_color} **Reddit**")
        st.caption("상태: 실시간")
        st.caption(f"포스트: {reddit_posts}개")
    
    # 종합 차트
    st.subheader("📈 종합 트렌드 분석")
    
    # 시장 지표 종합 차트 (예시)
    if fred_data.get('status') == 'success':
        fred_info = fred_data.get('data', {})
        indicators = fred_info.get('indicators', {})
        
        # 주요 지표들의 변화율 비교
        key_indicators = ['federal_funds_rate', 'unemployment_rate', 'cpi', 'gdp_growth']
        
        chart_data = []
        for indicator_key in key_indicators:
            if indicator_key in indicators:
                indicator = indicators[indicator_key]
                chart_data.append({
                    '지표': indicator.get('title', indicator_key)[:20] + "...",
                    '변화율': indicator.get('change_percent', 0)
                })
        
        if chart_data:
            df = pd.DataFrame(chart_data)
            
            fig = px.bar(
                df,
                x='지표',
                y='변화율',
                title="주요 경제 지표 변화율 (%)",
                color='변화율',
                color_continuous_scale=['red', 'yellow', 'green']
            )
            
            st.plotly_chart(fig, use_container_width=True)

def show_detailed_data(all_data):
    """상세 데이터 페이지"""
    st.header("🔍 상세 데이터")
    
    # 탭으로 구분
    tab1, tab2, tab3, tab4 = st.tabs(["🧠 Intelligence", "📊 FRED", "📰 뉴스", "📱 소셜"])
    
    with tab1:
        st.subheader("Alpha Vantage Intelligence 원시 데이터")
        intelligence_data = all_data.get('intelligence', {})
        
        if intelligence_data.get('status') == 'success':
            with st.expander("📊 시장 상태 데이터"):
                intel_data = intelligence_data.get('data', {})
                market_status = intel_data.get('market_status', [])
                if market_status:
                    st.json(market_status[:3])  # 처음 3개만 표시
            
            with st.expander("📈 상위 변동 종목 데이터"):
                top_movers = intel_data.get('top_gainers_losers', {})
                if top_movers:
                    st.json({k: v[:3] for k, v in top_movers.items()})  # 각 카테고리 3개씩
        else:
            st.error(f"Intelligence 데이터 로드 실패: {intelligence_data.get('error', 'Unknown')}")
    
    with tab2:
        st.subheader("FRED 경제 지표 원시 데이터")
        fred_data = all_data.get('fred', {})
        
        if fred_data.get('status') == 'success':
            fred_info = fred_data.get('data', {})
            indicators = fred_info.get('indicators', {})
            
            # 지표 선택
            if indicators:
                selected_indicator = st.selectbox(
                    "지표 선택",
                    list(indicators.keys()),
                    format_func=lambda x: indicators[x].get('title', x)
                )
                
                if selected_indicator:
                    st.json(indicators[selected_indicator])
        else:
            st.error(f"FRED 데이터 로드 실패: {fred_data.get('error', 'Unknown')}")
    
    with tab3:
        st.subheader("뉴스 데이터")
        news_data = all_data.get('news', {})
        
        if news_data.get('status') == 'success':
            news_info = news_data.get('data', {}).get('news_data', {})
            
            with st.expander("📰 뉴스 요약"):
                st.json(news_info.get('summary', {}))
            
            with st.expander("📂 카테고리별 뉴스 (샘플)"):
                categories = news_info.get('categories', {})
                for category, articles in categories.items():
                    if articles:
                        st.write(f"**{category.upper()}** ({len(articles)}개)")
                        st.json(articles[0])  # 첫 번째 기사만 표시
        else:
            st.error(f"뉴스 데이터 로드 실패: {news_data.get('error', 'Unknown')}")
    
    with tab4:
        st.subheader("소셜미디어 데이터")
        news_data = all_data.get('news', {})
        
        if news_data.get('status') == 'success':
            social_data = news_data.get('data', {}).get('social_data', {})
            st.json(social_data)
        else:
            st.error(f"소셜미디어 데이터 로드 실패: {news_data.get('error', 'Unknown')}")

def show_dashboard_home(all_data):
    """대시보드 홈 페이지"""
    st.header("🏠 대시보드 개요")
    
    # 전체 요약 메트릭
    col1, col2, col3, col4 = st.columns(4)
    
    intelligence_data = all_data.get('intelligence', {})
    fred_data = all_data.get('fred', {})
    news_data = all_data.get('news', {})
    
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
            "📱 Reddit 포스트",
            social_mentions.get('reddit_posts', 0),
            f"댓글: {social_mentions.get('reddit_comments', 0)}개"
        )
    
    st.markdown("---")
    
    # 최신 하이라이트
    st.markdown("---")
    st.subheader("🔥 최신 하이라이트")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 시장 현황")
        if intelligence_data.get('status') == 'success':
            intel_data = intelligence_data.get('data', {})
            market_status = intel_data.get('market_status', [])
            
            if market_status:
                open_markets = [m for m in market_status if m.get('current_status') == 'open']
                st.write(f"**개장 중인 시장**: {len(open_markets)}개")
                for market in open_markets[:3]:
                    st.write(f"• {market.get('region', 'Unknown')}: {market.get('primary_exchanges', 'N/A')}")
    
    with col2:
        st.markdown("#### 📰 주요 뉴스")
        if news_data.get('status') == 'success':
            news_info = news_data.get('data', {}).get('news_data', {})
            highlights = news_info.get('summary', {}).get('recent_highlights', [])
            
            for highlight in highlights[:3]:
                title = highlight.get('title', '')[:60] + "..."
                sentiment = highlight.get('sentiment', 'neutral')
                sentiment_emoji = {'positive': '🟢', 'negative': '🔴', 'neutral': '🟡'}.get(sentiment, '🟡')
                st.write(f"{sentiment_emoji} {title}")
    
    # 시스템 정보
    st.markdown("---")
    st.subheader("ℹ️ 시스템 정보")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📊 데이터 소스")
        st.write("• Alpha Vantage Intelligence")
        st.write("• FRED 경제 지표")
        st.write("• 아시아 시장 데이터")
        st.write("• 뉴스 RSS 피드")
        st.write("• Reddit API")
    
    with col2:
        st.markdown("#### 🕐 업데이트 주기")
        st.write("• 시장 데이터: 실시간")
        st.write("• 경제 지표: 5분")
        st.write("• 뉴스: 5분")
        st.write("• 소셜미디어: 5분")
    
    with col3:
        st.markdown("#### 🌏 시간대")
        st.write("• 기준 시간: 한국 시간 (KST)")
        st.write("• 아시아 시장: 한국 시간 기준")
        st.write("• 미국 시장: 현지 시간")
        st.write("• 유럽 시장: 현지 시간")

def show_alpha_vantage_page(intelligence_data):
    """Alpha Vantage Intelligence 상세 페이지"""
    st.header("🧠 Alpha Vantage Intelligence API")
    
    if intelligence_data.get('status') != 'success':
        st.error(f"❌ Intelligence 데이터 로드 실패: {intelligence_data.get('error', 'Unknown')}")
        return
    
    intel_data = intelligence_data.get('data', {})
    
    # 탭으로 구분
    tab1, tab2, tab3 = st.tabs(["🌍 시장 상태", "📈 상위 변동 종목", "📊 상세 분석"])
    
    with tab1:
        st.subheader("🌍 글로벌 시장 상태")
        
        market_status = intel_data.get('market_status', [])
        if market_status:
            # 시장 상태 테이블
            market_df = pd.DataFrame([
                {
                    '지역': market.get('region', 'Unknown'),
                    '주요 거래소': market.get('primary_exchanges', 'N/A'),
                    '현재 상태': market.get('current_status', 'Unknown'),
                    '로컬 시간': market.get('local_open', 'N/A'),
                    '참고': market.get('notes', 'N/A')
                }
                for market in market_status
            ])
            
            st.dataframe(market_df, use_container_width=True)
            
            # 개장/폐장 차트
            status_counts = market_df['현재 상태'].value_counts()
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="글로벌 시장 개장/폐장 현황"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("📈 상위 변동 종목")
        
        top_movers = intel_data.get('top_gainers_losers', {})
        
        # 상위 상승 종목
        if 'top_gainers' in top_movers:
            st.markdown("#### 🟢 상위 상승 종목")
            gainers_data = []
            
            for gainer in top_movers['top_gainers'][:10]:
                gainers_data.append({
                    '종목': gainer.get('ticker', 'N/A'),
                    '가격': f"${gainer.get('price', 0):.2f}",
                    '변화': gainer.get('change_amount', 'N/A'),
                    '변화율': gainer.get('change_percentage', 'N/A'),
                    '거래량': f"{int(gainer.get('volume', 0)):,}"
                })
            
            if gainers_data:
                st.dataframe(pd.DataFrame(gainers_data), use_container_width=True)
        
        # 상위 하락 종목
        if 'top_losers' in top_movers:
            st.markdown("#### 🔴 상위 하락 종목")
            losers_data = []
            
            for loser in top_movers['top_losers'][:10]:
                losers_data.append({
                    '종목': loser.get('ticker', 'N/A'),
                    '가격': f"${loser.get('price', 0):.2f}",
                    '변화': loser.get('change_amount', 'N/A'),
                    '변화율': loser.get('change_percentage', 'N/A'),
                    '거래량': f"{int(loser.get('volume', 0)):,}"
                })
            
            if losers_data:
                st.dataframe(pd.DataFrame(losers_data), use_container_width=True)
        
        # 거래량 상위 종목
        if 'most_actively_traded' in top_movers:
            st.markdown("#### ⚡ 거래량 상위 종목")
            active_data = []
            
            for active in top_movers['most_actively_traded'][:10]:
                active_data.append({
                    '종목': active.get('ticker', 'N/A'),
                    '가격': f"${active.get('price', 0):.2f}",
                    '변화': active.get('change_amount', 'N/A'),
                    '변화율': active.get('change_percentage', 'N/A'),
                    '거래량': f"{int(active.get('volume', 0)):,}"
                })
            
            if active_data:
                st.dataframe(pd.DataFrame(active_data), use_container_width=True)
    
    with tab3:
        st.subheader("📊 상세 분석")
        
        # 요약 통계
        summary = intelligence_data.get('summary', {})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("시장 상태", f"{summary.get('market_status_count', 0)}개")
            st.metric("개장 시장", f"{summary.get('open_markets_count', 0)}개")
        
        with col2:
            st.metric("상승 종목", f"{summary.get('top_gainers_count', 0)}개")
            st.metric("하락 종목", f"{summary.get('top_losers_count', 0)}개")
        
        with col3:
            st.metric("활발한 거래", f"{summary.get('most_active_count', 0)}개")
            st.metric("시장 변동성", summary.get('market_volatility', 'Unknown'))
        
        # 원시 데이터 (확장 가능)
        with st.expander("🔍 원시 데이터 보기"):
            st.json(intel_data)

if __name__ == "__main__":
    main()
