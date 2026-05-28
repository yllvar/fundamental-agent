#!/usr/bin/env python3
"""
Reddit 소셜미디어 상세 페이지 (클릭 가능한 링크 포함)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def show_social_media_page(news_data):
    """Reddit 소셜미디어 상세 페이지"""
    st.header("📱 Reddit 소셜미디어 분석")
    
    if news_data.get('status') != 'success':
        st.error(f"❌ 소셜미디어 데이터 로드 실패: {news_data.get('error', 'Unknown')}")
        return
    
    # 데이터 구조 확인
    data = news_data.get('data', {})
    social_data = data.get('social_data', {})
    
    if not social_data:
        st.warning("⚠️ 소셜미디어 데이터가 비어있습니다.")
        return
    
    reddit_data = social_data.get('platforms', {}).get('reddit', {})
    
    if not reddit_data:
        st.warning("⚠️ Reddit 데이터가 없습니다.")
        return
    
    # Reddit 데이터 상태 확인
    data_source = reddit_data.get('data_source', 'unknown')
    
    if data_source != 'real_api':
        st.warning("⚠️ Reddit 실제 데이터를 사용할 수 없습니다. 시뮬레이션 데이터를 표시합니다.")
        show_reddit_simulation(reddit_data)
        return
    
    # Reddit 실제 데이터 표시
    st.subheader("📊 Reddit 데이터 요약")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 포스트", reddit_data.get('posts', 0))
    
    with col2:
        st.metric("총 댓글", reddit_data.get('comments', 0))
    
    with col3:
        st.metric("평균 점수", f"{reddit_data.get('avg_post_score', 0):.1f}")
    
    with col4:
        overall_sentiment = reddit_data.get('overall_sentiment', 'neutral')
        st.metric("전체 감정", overall_sentiment.title())
    
    st.markdown("---")
    
    # 탭으로 구분
    tab1, tab2, tab3, tab4 = st.tabs(["🏆 인기 포스트", "💬 활발한 댓글", "📊 서브레딧 분석", "🔥 트렌딩"])
    
    with tab1:
        show_reddit_posts_real(news_data)
    
    with tab2:
        show_reddit_comments_real(news_data)
    
    with tab3:
        show_subreddit_analysis(reddit_data)
    
    with tab4:
        show_reddit_trending(reddit_data)

def show_reddit_posts_real(news_data):
    """실제 Reddit 포스트 데이터 표시"""
    st.subheader("🏆 실제 Reddit 포스트")
    
    # enhanced_data_collector에서 수집한 실제 Reddit 데이터 접근
    try:
        # Reddit 수집기를 직접 호출하여 실제 데이터 가져오기
        from data_monitoring.reddit_collector import RedditEconomicCollector
        
        with st.spinner("📱 실제 Reddit 포스트 수집 중..."):
            reddit_collector = RedditEconomicCollector()
            reddit_data = reddit_collector.collect_comprehensive_data(max_subreddits=3, posts_per_subreddit=5)
        
        subreddits = reddit_data.get('subreddits', {})
        
        if not subreddits:
            st.warning("⚠️ Reddit 포스트 데이터가 없습니다.")
            return
        
        # 모든 포스트를 하나의 리스트로 수집
        all_posts = []
        for subreddit_name, subreddit_data in subreddits.items():
            posts = subreddit_data.get('posts', [])
            for post in posts:
                post['subreddit_name'] = subreddit_name
                all_posts.append(post)
        
        # 점수 기준으로 정렬
        all_posts.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # 필터링 옵션
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sentiment_filter = st.selectbox("감정 필터", ["전체", "긍정", "부정", "중립"], key="reddit_post_sentiment")
        
        with col2:
            subreddit_options = ["전체"] + list(subreddits.keys())
            subreddit_filter = st.selectbox("서브레딧 필터", subreddit_options, key="reddit_post_subreddit")
        
        with col3:
            show_count = st.selectbox("표시 개수", [5, 10, 15, 20], index=1, key="reddit_post_count")
        
        # 필터링 적용
        filtered_posts = all_posts.copy()
        
        if sentiment_filter != "전체":
            sentiment_map = {"긍정": "positive", "부정": "negative", "중립": "neutral"}
            filtered_posts = [
                post for post in filtered_posts 
                if post.get('sentiment', {}).get('label') == sentiment_map[sentiment_filter]
            ]
        
        if subreddit_filter != "전체":
            filtered_posts = [
                post for post in filtered_posts 
                if post.get('subreddit_name') == subreddit_filter
            ]
        
        # 포스트 표시
        for i, post in enumerate(filtered_posts[:show_count], 1):
            with st.container():
                # 감정에 따른 색상
                sentiment = post.get('sentiment', {})
                sentiment_label = sentiment.get('label', 'neutral')
                sentiment_emoji = {
                    'positive': '🟢',
                    'negative': '🔴',
                    'neutral': '🟡'
                }.get(sentiment_label, '🟡')
                
                # 헤더
                col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
                
                with col1:
                    title = post.get('title', 'No Title')
                    st.markdown(f"### {i}. {sentiment_emoji} {title}")
                    
                    author = post.get('author', 'Unknown')
                    subreddit = post.get('subreddit_name', 'Unknown')
                    created_time = post.get('created_datetime', 'Unknown')
                    
                    st.caption(f"r/{subreddit} • u/{author} • {created_time}")
                
                with col2:
                    st.metric("점수", post.get('score', 0))
                
                with col3:
                    st.metric("댓글", post.get('num_comments', 0))
                
                with col4:
                    permalink = post.get('permalink', '')
                    if permalink:
                        st.link_button("🔗 Reddit", permalink)
                    else:
                        st.write("링크 없음")
                
                # 포스트 내용 (요약)
                selftext = post.get('selftext', '')
                if selftext and len(selftext.strip()) > 0:
                    # 내용이 너무 길면 자르기
                    if len(selftext) > 200:
                        selftext = selftext[:200] + "..."
                    st.write(f"**내용**: {selftext}")
                
                # 감정 및 주제
                col1, col2 = st.columns(2)
                
                with col1:
                    polarity = sentiment.get('polarity', 0)
                    st.write(f"**감정**: {sentiment_label.title()} ({polarity:+.2f})")
                
                with col2:
                    topics = post.get('economic_topics', [])
                    if topics:
                        topic_tags = " ".join([f"`{topic}`" for topic in topics])
                        st.markdown(f"**주제**: {topic_tags}")
                
                # 추가 링크
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    subreddit_link = f"https://reddit.com/r/{subreddit}"
                    st.link_button(f"📂 r/{subreddit}", subreddit_link)
                
                with col2:
                    if author != 'Unknown' and author != '[deleted]':
                        user_link = f"https://reddit.com/u/{author}"
                        st.link_button(f"👤 u/{author}", user_link)
                
                with col3:
                    # 원본 URL (외부 링크인 경우)
                    url = post.get('url', '')
                    if url and url != permalink and not url.startswith('https://reddit.com'):
                        st.link_button("🌐 원본", url)
                
                st.markdown("---")
        
        # 통계 정보
        st.subheader("📊 포스트 통계")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 서브레딧별 포스트 수
            subreddit_counts = {}
            for post in all_posts:
                subreddit = post.get('subreddit_name', 'Unknown')
                subreddit_counts[subreddit] = subreddit_counts.get(subreddit, 0) + 1
            
            st.write("**서브레딧별 포스트 수:**")
            for subreddit, count in subreddit_counts.items():
                st.write(f"• r/{subreddit}: {count}개")
        
        with col2:
            # 감정 분포
            sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
            for post in all_posts:
                sentiment_label = post.get('sentiment', {}).get('label', 'neutral')
                sentiment_counts[sentiment_label] += 1
            
            st.write("**감정 분포:**")
            total = len(all_posts)
            for sentiment, count in sentiment_counts.items():
                percentage = (count / total * 100) if total > 0 else 0
                st.write(f"• {sentiment.title()}: {count}개 ({percentage:.1f}%)")
        
    except Exception as e:
        st.error(f"❌ Reddit 포스트 데이터 로드 오류: {e}")
        st.info("💡 Reddit API 연결에 문제가 있을 수 있습니다.")

def show_reddit_comments_real(news_data):
    """실제 Reddit 댓글 데이터 표시"""
    st.subheader("💬 실제 Reddit 댓글")
    
    try:
        from data_monitoring.reddit_collector import RedditEconomicCollector
        
        with st.spinner("💬 실제 Reddit 댓글 수집 중..."):
            reddit_collector = RedditEconomicCollector()
            reddit_data = reddit_collector.collect_comprehensive_data(max_subreddits=3, posts_per_subreddit=3)
        
        subreddits = reddit_data.get('subreddits', {})
        
        if not subreddits:
            st.warning("⚠️ Reddit 댓글 데이터가 없습니다.")
            return
        
        # 모든 댓글을 하나의 리스트로 수집
        all_comments = []
        for subreddit_name, subreddit_data in subreddits.items():
            comments = subreddit_data.get('comments', [])
            for comment in comments:
                comment['subreddit_name'] = subreddit_name
                all_comments.append(comment)
        
        # 점수 기준으로 정렬
        all_comments.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # 필터링 옵션
        col1, col2 = st.columns(2)
        
        with col1:
            show_count = st.selectbox("표시 개수", [10, 20, 30, 50], index=1, key="reddit_comment_count")
        
        with col2:
            subreddit_options = ["전체"] + list(subreddits.keys())
            subreddit_filter = st.selectbox("서브레딧 필터", subreddit_options, key="reddit_comment_subreddit")
        
        # 필터링 적용
        filtered_comments = all_comments.copy()
        
        if subreddit_filter != "전체":
            filtered_comments = [
                comment for comment in filtered_comments 
                if comment.get('subreddit_name') == subreddit_filter
            ]
        
        # 댓글 표시
        for i, comment in enumerate(filtered_comments[:show_count], 1):
            with st.container():
                # 감정에 따른 색상
                sentiment = comment.get('sentiment', {})
                sentiment_label = sentiment.get('label', 'neutral')
                sentiment_emoji = {
                    'positive': '🟢',
                    'negative': '🔴',
                    'neutral': '🟡'
                }.get(sentiment_label, '🟡')
                
                # 헤더
                col1, col2, col3 = st.columns([5, 1, 1])
                
                with col1:
                    author = comment.get('author', 'Unknown')
                    subreddit = comment.get('subreddit_name', 'Unknown')
                    post_title = comment.get('post_title', 'Unknown Post')
                    
                    st.markdown(f"**{i}. u/{author}** in r/{subreddit}")
                    st.caption(f"Re: {post_title[:60]}...")
                
                with col2:
                    st.metric("점수", comment.get('score', 0))
                
                with col3:
                    permalink = comment.get('permalink', '')
                    if permalink:
                        st.link_button("🔗 댓글", permalink)
                
                # 댓글 내용
                body = comment.get('body', '')
                if body:
                    # 내용이 너무 길면 자르기
                    if len(body) > 300:
                        body = body[:300] + "..."
                    st.write(f"{sentiment_emoji} {body}")
                
                # 감정 및 주제
                col1, col2 = st.columns(2)
                
                with col1:
                    polarity = sentiment.get('polarity', 0)
                    st.caption(f"감정: {sentiment_label.title()} ({polarity:+.2f})")
                
                with col2:
                    topics = comment.get('economic_topics', [])
                    if topics:
                        topic_tags = " ".join([f"`{topic}`" for topic in topics])
                        st.caption(f"주제: {topic_tags}")
                
                st.markdown("---")
        
        # 댓글 통계
        st.subheader("📊 댓글 통계")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**총 댓글 수**: {len(all_comments)}개")
            
            # 서브레딧별 댓글 수
            subreddit_counts = {}
            for comment in all_comments:
                subreddit = comment.get('subreddit_name', 'Unknown')
                subreddit_counts[subreddit] = subreddit_counts.get(subreddit, 0) + 1
            
            st.write("**서브레딧별 댓글 수:**")
            for subreddit, count in subreddit_counts.items():
                st.write(f"• r/{subreddit}: {count}개")
        
        with col2:
            # 평균 점수
            if all_comments:
                avg_score = sum(comment.get('score', 0) for comment in all_comments) / len(all_comments)
                st.write(f"**평균 점수**: {avg_score:.1f}")
            
            # 감정 분포
            sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
            for comment in all_comments:
                sentiment_label = comment.get('sentiment', {}).get('label', 'neutral')
                sentiment_counts[sentiment_label] += 1
            
            st.write("**감정 분포:**")
            total = len(all_comments)
            for sentiment, count in sentiment_counts.items():
                percentage = (count / total * 100) if total > 0 else 0
                st.write(f"• {sentiment.title()}: {count}개 ({percentage:.1f}%)")
        
    except Exception as e:
        st.error(f"❌ Reddit 댓글 데이터 로드 오류: {e}")
        st.info("💡 Reddit API 연결에 문제가 있을 수 있습니다.")

def show_reddit_posts(news_data):
    """Reddit 포스트 상세 표시"""
    st.subheader("🏆 인기 Reddit 포스트")
    
    # 실제 Reddit 데이터에서 포스트 추출
    # 이 부분은 실제 수집된 데이터 구조에 맞게 조정 필요
    
    # 시뮬레이션 데이터로 예시 표시
    sample_posts = [
        {
            'title': 'Fed Rate Decision Impact on Tech Stocks',
            'subreddit': 'investing',
            'score': 245,
            'comments': 67,
            'author': 'market_analyst_2024',
            'sentiment': {'label': 'positive', 'polarity': 0.3},
            'topics': ['monetary_policy', 'stock_market'],
            'permalink': 'https://reddit.com/r/investing/comments/example1',
            'created_datetime': datetime.now()
        },
        {
            'title': 'Q4 Earnings Season: What to Expect',
            'subreddit': 'stocks',
            'score': 189,
            'comments': 43,
            'author': 'earnings_watcher',
            'sentiment': {'label': 'neutral', 'polarity': 0.1},
            'topics': ['earnings', 'stock_market'],
            'permalink': 'https://reddit.com/r/stocks/comments/example2',
            'created_datetime': datetime.now()
        },
        {
            'title': 'Inflation Data Shows Cooling Trend',
            'subreddit': 'economics',
            'score': 156,
            'comments': 89,
            'author': 'econ_student',
            'sentiment': {'label': 'positive', 'polarity': 0.2},
            'topics': ['inflation', 'economic_indicators'],
            'permalink': 'https://reddit.com/r/economics/comments/example3',
            'created_datetime': datetime.now()
        }
    ]
    
    # 필터링 옵션
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sentiment_filter = st.selectbox("감정 필터", ["전체", "긍정", "부정", "중립"], key="post_sentiment")
    
    with col2:
        subreddit_options = ["전체"] + list(set(post['subreddit'] for post in sample_posts))
        subreddit_filter = st.selectbox("서브레딧 필터", subreddit_options, key="post_subreddit")
    
    with col3:
        sort_by = st.selectbox("정렬 기준", ["점수순", "댓글순", "최신순"], key="post_sort")
    
    # 포스트 표시
    for i, post in enumerate(sample_posts):
        with st.container():
            # 감정에 따른 색상
            sentiment_label = post['sentiment']['label']
            sentiment_emoji = {
                'positive': '🟢',
                'negative': '🔴',
                'neutral': '🟡'
            }.get(sentiment_label, '🟡')
            
            # 헤더
            col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
            
            with col1:
                st.markdown(f"### {sentiment_emoji} {post['title']}")
                st.caption(f"r/{post['subreddit']} • u/{post['author']}")
            
            with col2:
                st.metric("점수", post['score'])
            
            with col3:
                st.metric("댓글", post['comments'])
            
            with col4:
                st.link_button("🔗 Reddit", post['permalink'])
            
            # 감정 및 주제
            col1, col2 = st.columns(2)
            
            with col1:
                polarity = post['sentiment']['polarity']
                st.write(f"**감정**: {sentiment_label.title()} ({polarity:+.2f})")
            
            with col2:
                topics = post['topics']
                if topics:
                    topic_tags = " ".join([f"`{topic}`" for topic in topics])
                    st.markdown(f"**주제**: {topic_tags}")
            
            # 관련 링크
            col1, col2, col3 = st.columns(3)
            
            with col1:
                subreddit_link = f"https://reddit.com/r/{post['subreddit']}"
                st.link_button(f"📂 r/{post['subreddit']}", subreddit_link)
            
            with col2:
                user_link = f"https://reddit.com/u/{post['author']}"
                st.link_button(f"👤 u/{post['author']}", user_link)
            
            with col3:
                # Google 검색 링크
                search_query = post['title'].replace(' ', '+')
                google_link = f"https://www.google.com/search?q={search_query}"
                st.link_button("🔍 Google", google_link)
            
            st.markdown("---")

def show_reddit_comments(news_data):
    """Reddit 댓글 상세 표시"""
    st.subheader("💬 활발한 Reddit 댓글")
    
    # 시뮬레이션 댓글 데이터
    sample_comments = [
        {
            'body': 'Great analysis! The Fed decision will definitely impact growth stocks more than value stocks.',
            'score': 45,
            'author': 'value_investor_pro',
            'subreddit': 'investing',
            'post_title': 'Fed Rate Decision Impact on Tech Stocks',
            'sentiment': {'label': 'positive', 'polarity': 0.4},
            'topics': ['monetary_policy', 'stock_market'],
            'permalink': 'https://reddit.com/r/investing/comments/example1/comment1'
        },
        {
            'body': 'I disagree. The market has already priced in the rate changes. Look at the bond yields.',
            'score': 23,
            'author': 'bond_trader_2024',
            'subreddit': 'investing',
            'post_title': 'Fed Rate Decision Impact on Tech Stocks',
            'sentiment': {'label': 'negative', 'polarity': -0.2},
            'topics': ['monetary_policy', 'investment'],
            'permalink': 'https://reddit.com/r/investing/comments/example1/comment2'
        },
        {
            'body': 'Earnings season is always volatile. Best to stick with fundamentally strong companies.',
            'score': 67,
            'author': 'fundamental_analyst',
            'subreddit': 'stocks',
            'post_title': 'Q4 Earnings Season: What to Expect',
            'sentiment': {'label': 'neutral', 'polarity': 0.1},
            'topics': ['earnings', 'investment'],
            'permalink': 'https://reddit.com/r/stocks/comments/example2/comment1'
        }
    ]
    
    # 댓글 표시
    for i, comment in enumerate(sample_comments):
        with st.container():
            # 감정에 따른 색상
            sentiment_label = comment['sentiment']['label']
            sentiment_emoji = {
                'positive': '🟢',
                'negative': '🔴',
                'neutral': '🟡'
            }.get(sentiment_label, '🟡')
            
            # 헤더
            col1, col2, col3 = st.columns([5, 1, 1])
            
            with col1:
                st.markdown(f"**u/{comment['author']}** in r/{comment['subreddit']}")
                st.caption(f"Re: {comment['post_title']}")
            
            with col2:
                st.metric("점수", comment['score'])
            
            with col3:
                st.link_button("🔗 댓글", comment['permalink'])
            
            # 댓글 내용
            st.write(f"{sentiment_emoji} {comment['body']}")
            
            # 감정 및 주제
            col1, col2 = st.columns(2)
            
            with col1:
                polarity = comment['sentiment']['polarity']
                st.caption(f"감정: {sentiment_label.title()} ({polarity:+.2f})")
            
            with col2:
                topics = comment['topics']
                if topics:
                    topic_tags = " ".join([f"`{topic}`" for topic in topics])
                    st.caption(f"주제: {topic_tags}")
            
            st.markdown("---")

def show_subreddit_analysis(reddit_data):
    """서브레딧 분석"""
    st.subheader("📊 서브레딧 분석")
    
    # 활성 서브레딧
    top_subreddits = reddit_data.get('top_subreddits', [])
    if top_subreddits:
        st.markdown("#### 🏆 가장 활발한 서브레딧")
        
        for i, subreddit in enumerate(top_subreddits[:5], 1):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{i}. r/{subreddit}**")
                st.caption(get_subreddit_description(subreddit))
            
            with col2:
                # 서브레딧 방문 링크
                subreddit_link = f"https://reddit.com/r/{subreddit}"
                st.link_button("📂 방문", subreddit_link)
            
            with col3:
                # 서브레딧 정보 링크
                about_link = f"https://reddit.com/r/{subreddit}/about"
                st.link_button("ℹ️ 정보", about_link)
    
    # 감정 분포
    sentiment = reddit_data.get('sentiment', {})
    if sentiment:
        st.markdown("#### 💭 서브레딧별 감정 분포")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 감정 분포 파이 차트
            labels = ['긍정', '부정', '중립']
            values = [
                sentiment.get('positive', 0),
                sentiment.get('negative', 0),
                sentiment.get('neutral', 0)
            ]
            
            fig = px.pie(values=values, names=labels, title="Reddit 감정 분포")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 감정 메트릭
            st.metric("긍정 비율", f"{sentiment.get('positive', 0):.1f}%")
            st.metric("부정 비율", f"{sentiment.get('negative', 0):.1f}%")
            st.metric("중립 비율", f"{sentiment.get('neutral', 0):.1f}%")

def show_reddit_trending(reddit_data):
    """Reddit 트렌딩 분석"""
    st.subheader("🔥 Reddit 트렌딩 분석")
    
    # 트렌딩 주제
    trending_topics = reddit_data.get('trending_topics', [])
    if trending_topics:
        st.markdown("#### 📈 인기 주제")
        
        for i, topic in enumerate(trending_topics[:5], 1):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{i}. {topic.replace('_', ' ').title()}**")
                st.caption(get_topic_description(topic))
            
            with col2:
                # Reddit 검색 링크
                search_query = topic.replace('_', '+')
                reddit_search = f"https://www.reddit.com/search/?q={search_query}"
                st.link_button("🔍 Reddit", reddit_search)
            
            with col3:
                # Google 뉴스 검색
                google_news = f"https://news.google.com/search?q={search_query}"
                st.link_button("📰 뉴스", google_news)
    
    # 추천 서브레딧
    st.markdown("#### 💡 추천 경제 서브레딧")
    
    recommended_subreddits = [
        ('investing', '투자 전략 및 포트폴리오 논의'),
        ('stocks', '개별 주식 분석 및 토론'),
        ('economics', '경제학 이론 및 정책 분석'),
        ('SecurityAnalysis', '기업 분석 및 가치 투자'),
        ('ValueInvesting', '가치 투자 전략'),
        ('financialindependence', '경제적 자유 달성 방법'),
        ('personalfinance', '개인 재정 관리'),
        ('wallstreetbets', '고위험 투자 및 옵션 거래')
    ]
    
    for subreddit, description in recommended_subreddits:
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.write(f"**r/{subreddit}**")
            st.caption(description)
        
        with col2:
            subreddit_link = f"https://reddit.com/r/{subreddit}"
            st.link_button("📂 방문", subreddit_link)
        
        with col3:
            # 실시간 포스트 링크
            hot_link = f"https://reddit.com/r/{subreddit}/hot"
            st.link_button("🔥 인기", hot_link)

def show_reddit_simulation(reddit_data):
    """Reddit 시뮬레이션 데이터 표시"""
    st.info("📊 Reddit 시뮬레이션 데이터를 표시합니다.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("포스트", reddit_data.get('posts', 0))
    
    with col2:
        st.metric("댓글", reddit_data.get('comments', 0))
    
    with col3:
        st.write("**주요 서브레딧**")
        subreddits = reddit_data.get('top_subreddits', [])
        for subreddit in subreddits[:3]:
            subreddit_link = f"https://reddit.com/{subreddit}"
            st.link_button(subreddit, subreddit_link)

def get_subreddit_description(subreddit):
    """서브레딧 설명 반환"""
    descriptions = {
        'investing': '투자 전략 및 포트폴리오 관리',
        'stocks': '개별 주식 분석 및 토론',
        'economics': '경제학 이론 및 정책 분석',
        'SecurityAnalysis': '기업 분석 및 가치 투자',
        'ValueInvesting': '가치 투자 전략 및 철학',
        'financialindependence': '경제적 자유 달성 방법',
        'personalfinance': '개인 재정 관리 및 조언'
    }
    return descriptions.get(subreddit, '경제 관련 토론')

def get_topic_description(topic):
    """주제 설명 반환"""
    descriptions = {
        'stock_market': '주식 시장 동향 및 분석',
        'earnings': '기업 실적 발표 및 분석',
        'investment': '투자 전략 및 기회',
        'monetary_policy': '통화 정책 및 금리',
        'inflation': '인플레이션 및 물가 상승',
        'cryptocurrency': '암호화폐 및 디지털 자산',
        'recession': '경기 침체 및 경제 위기',
        'employment': '고용 시장 및 일자리'
    }
    return descriptions.get(topic, '경제 관련 주제')
