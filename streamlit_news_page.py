#!/usr/bin/env python3
"""
뉴스 분석 상세 페이지 (클릭 가능한 링크 포함)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re

def show_news_page(news_data):
    """뉴스 분석 상세 페이지"""
    st.header("📰 뉴스 분석 상세")
    
    if news_data.get('status') != 'success':
        st.error(f"❌ 뉴스 데이터 로드 실패: {news_data.get('error', 'Unknown')}")
        return
    
    # 데이터 구조 확인 및 추출
    data = news_data.get('data', {})
    news_info = data.get('news_data', {})
    
    if not news_info:
        st.warning("⚠️ 뉴스 데이터가 비어있습니다.")
        st.info("💡 데이터 수집 중이거나 RSS 피드에 문제가 있을 수 있습니다.")
        
        # 디버깅 정보
        with st.expander("🔍 디버깅 정보"):
            st.write("**전체 데이터 구조:**")
            st.write(f"- 상태: {news_data.get('status')}")
            st.write(f"- 데이터 키: {list(data.keys()) if data else 'None'}")
            if news_info:
                st.write(f"- 뉴스 정보 키: {list(news_info.keys())}")
        return
    
    categories = news_info.get('categories', {})
    summary = news_info.get('summary', {})
    
    if not categories:
        st.warning("⚠️ 뉴스 카테고리 데이터가 없습니다.")
        return
    
    # 요약 정보
    st.subheader("📊 뉴스 수집 요약")
    
    # 전체 기사 수 계산
    total_articles = sum(len(articles) for articles in categories.values())
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 기사 수", total_articles)
    
    with col2:
        sentiment_analysis = summary.get('sentiment_analysis', {})
        positive_ratio = sentiment_analysis.get('positive_ratio', 0)
        positive_count = sentiment_analysis.get('positive', 0)
        st.metric(
            "긍정 비율", 
            f"{positive_ratio:.1f}%",
            f"총 {positive_count}개"
        )
    
    with col3:
        negative_ratio = sentiment_analysis.get('negative_ratio', 0)
        negative_count = sentiment_analysis.get('negative', 0)
        st.metric(
            "부정 비율", 
            f"{negative_ratio:.1f}%",
            f"총 {negative_count}개"
        )
    
    with col4:
        st.metric("카테고리 수", len(categories))
        
        # 카테고리별 기사 수 표시
        category_info = []
        for cat_name, articles in categories.items():
            category_info.append(f"{cat_name}: {len(articles)}개")
        st.caption(" | ".join(category_info))
    
    st.markdown("---")
    
    # 탭으로 구분
    tab1, tab2, tab3, tab4 = st.tabs(["📈 금융 뉴스", "🏛️ 경제 기관", "🌍 국제 기관", "🔥 트렌딩"])
    
    with tab1:
        show_news_category(categories.get('financial', []), "📈 금융 뉴스", "financial")
    
    with tab2:
        show_news_category(categories.get('economic', []), "🏛️ 경제 기관 뉴스", "economic")
    
    with tab3:
        show_news_category(categories.get('international', []), "🌍 국제 기관 뉴스", "international")
    
    with tab4:
        show_trending_analysis(summary)

def show_news_category(articles, title, category_key):
    """뉴스 카테고리별 상세 표시"""
    st.subheader(title)
    
    if not articles:
        st.info("해당 카테고리의 뉴스가 없습니다.")
        return
    
    # 필터링 옵션
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sentiment_filter = st.selectbox(
            "감정 필터",
            ["전체", "긍정", "부정", "중립"],
            key=f"sentiment_{category_key}"
        )
    
    with col2:
        source_options = ["전체"] + list(set(article.get('source_name', 'Unknown') for article in articles))
        source_filter = st.selectbox(
            "소스 필터",
            source_options,
            key=f"source_{category_key}"
        )
    
    with col3:
        sort_by = st.selectbox(
            "정렬 기준",
            ["최신순", "감정 점수", "소스명"],
            key=f"sort_{category_key}"
        )
    
    # 필터링 적용
    filtered_articles = articles.copy()
    
    if sentiment_filter != "전체":
        sentiment_map = {"긍정": "positive", "부정": "negative", "중립": "neutral"}
        filtered_articles = [
            article for article in filtered_articles 
            if article.get('sentiment', {}).get('label') == sentiment_map[sentiment_filter]
        ]
    
    if source_filter != "전체":
        filtered_articles = [
            article for article in filtered_articles 
            if article.get('source_name') == source_filter
        ]
    
    # 정렬 적용
    if sort_by == "최신순":
        filtered_articles.sort(key=lambda x: x.get('published_datetime', datetime.min), reverse=True)
    elif sort_by == "감정 점수":
        filtered_articles.sort(key=lambda x: abs(x.get('sentiment', {}).get('polarity', 0)), reverse=True)
    elif sort_by == "소스명":
        filtered_articles.sort(key=lambda x: x.get('source_name', ''))
    
    # 페이지네이션
    items_per_page = st.selectbox(f"페이지당 기사 수", [5, 10, 20], index=1, key=f"pagination_{category_key}")
    
    total_articles = len(filtered_articles)
    total_pages = (total_articles - 1) // items_per_page + 1 if total_articles > 0 else 1
    
    if total_pages > 1:
        page_num = st.number_input(
            "페이지", 
            min_value=1, 
            max_value=total_pages, 
            value=1,
            key=f"page_{category_key}"
        )
        start_idx = (page_num - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_articles = filtered_articles[start_idx:end_idx]
    else:
        page_articles = filtered_articles
    
    # 기사 표시
    for i, article in enumerate(page_articles):
        with st.container():
            # 감정에 따른 색상
            sentiment = article.get('sentiment', {})
            sentiment_label = sentiment.get('label', 'neutral')
            sentiment_color = {
                'positive': '🟢',
                'negative': '🔴', 
                'neutral': '🟡'
            }.get(sentiment_label, '🟡')
            
            polarity = sentiment.get('polarity', 0)
            
            # 헤더
            col1, col2, col3 = st.columns([6, 1, 1])
            
            with col1:
                title = article.get('title', 'No Title')
                st.markdown(f"### {sentiment_color} {title}")
                
                # 메타 정보
                source = article.get('source_name', 'Unknown')
                published = article.get('published', 'Unknown')
                author = article.get('author', 'Unknown')
                
                st.caption(f"📰 {source} | 📅 {published} | ✍️ {author}")
            
            with col2:
                # 감정 점수
                st.metric("감정 점수", f"{polarity:+.3f}")
                st.caption(sentiment_label.upper())
            
            with col3:
                # 원문 링크
                link = article.get('link', '')
                if link:
                    st.link_button("🔗 원문 보기", link)
                else:
                    st.write("링크 없음")
            
            # 요약
            summary_text = article.get('summary', '')
            if summary_text:
                # HTML 태그 제거
                clean_summary = re.sub('<.*?>', '', summary_text)
                if len(clean_summary) > 200:
                    clean_summary = clean_summary[:200] + "..."
                st.write(clean_summary)
            
            # 주제 태그
            topics = article.get('topics', [])
            if topics:
                topic_tags = " ".join([f"`{topic}`" for topic in topics])
                st.markdown(f"**주제**: {topic_tags}")
            
            st.markdown("---")
    
    # 페이지 정보
    if total_pages > 1:
        st.write(f"페이지 {page_num}/{total_pages} (총 {total_articles}개 기사)")
    
    # 카테고리 통계
    if filtered_articles:
        st.subheader(f"📊 {title} 통계")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 소스별 기사 수
            source_counts = {}
            for article in filtered_articles:
                source = article.get('source_name', 'Unknown')
                source_counts[source] = source_counts.get(source, 0) + 1
            
            if source_counts:
                fig = px.bar(
                    x=list(source_counts.values()),
                    y=list(source_counts.keys()),
                    orientation='h',
                    title="소스별 기사 수"
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 감정 분포
            sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
            for article in filtered_articles:
                sentiment_label = article.get('sentiment', {}).get('label', 'neutral')
                sentiment_counts[sentiment_label] += 1
            
            fig = px.pie(
                values=list(sentiment_counts.values()),
                names=['긍정', '부정', '중립'],
                title="감정 분포"
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

def show_trending_analysis(summary):
    """트렌딩 분석 표시"""
    st.subheader("🔥 트렌딩 분석")
    
    # 트렌딩 주제
    trending_topics = summary.get('trending_topics', {})
    if trending_topics:
        st.markdown("#### 📈 인기 주제")
        
        # 주제별 언급 횟수 차트
        topics = list(trending_topics.keys())[:10]
        counts = list(trending_topics.values())[:10]
        
        fig = px.bar(
            x=counts,
            y=topics,
            orientation='h',
            title="주제별 언급 횟수",
            labels={'x': '언급 횟수', 'y': '주제'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # 주제별 상세 정보
        for topic, count in list(trending_topics.items())[:5]:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{topic.replace('_', ' ').title()}**")
                st.caption(f"{count}회 언급")
            
            with col2:
                # 관련 검색 링크
                search_query = topic.replace('_', '+')
                google_search = f"https://www.google.com/search?q={search_query}+economy+news"
                st.link_button("🔍 Google", google_search)
    
    # 최근 하이라이트
    recent_highlights = summary.get('recent_highlights', [])
    if recent_highlights:
        st.markdown("#### ⭐ 주요 뉴스 하이라이트")
        
        for i, highlight in enumerate(recent_highlights[:5], 1):
            with st.container():
                sentiment = highlight.get('sentiment', 'neutral')
                sentiment_emoji = {
                    'positive': '🟢',
                    'negative': '🔴',
                    'neutral': '🟡'
                }.get(sentiment, '🟡')
                
                title = highlight.get('title', 'No Title')
                source = highlight.get('source', 'Unknown')
                topics = highlight.get('topics', [])
                
                st.markdown(f"**{i}. {sentiment_emoji} {title}**")
                st.caption(f"📰 {source}")
                
                if topics:
                    topic_tags = " ".join([f"`{topic}`" for topic in topics])
                    st.markdown(f"주제: {topic_tags}")
                
                st.markdown("---")
    
    # 감정 분석 트렌드
    sentiment_analysis = summary.get('sentiment_analysis', {})
    if sentiment_analysis:
        st.markdown("#### 💭 전체 감정 분석")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "긍정 기사",
                sentiment_analysis.get('positive', 0),
                f"{sentiment_analysis.get('positive_ratio', 0):.1f}%"
            )
        
        with col2:
            st.metric(
                "부정 기사",
                sentiment_analysis.get('negative', 0),
                f"{sentiment_analysis.get('negative_ratio', 0):.1f}%"
            )
        
        with col3:
            st.metric(
                "중립 기사",
                sentiment_analysis.get('neutral', 0),
                f"{100 - sentiment_analysis.get('positive_ratio', 0) - sentiment_analysis.get('negative_ratio', 0):.1f}%"
            )
