#!/usr/bin/env python3
"""
실제 Reddit 데이터를 사용하는 개선된 네트워크 분석 Streamlit 페이지
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
import numpy as np
from datetime import datetime
import sys
import os
import json

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_monitoring.fixed_enhanced_network_analyzer import FixedEnhancedNetworkAnalyzer
from data_monitoring.real_reddit_collector import RealRedditCollector

def create_real_network_page():
    """실제 Reddit 데이터를 사용하는 네트워크 분석 페이지"""
    
    st.title("🕸️ 실제 Reddit 데이터 기반 경제 네트워크 분석")
    st.markdown("---")
    
    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ 분석 설정")
        
        # 데이터 수집 설정
        st.subheader("📱 Reddit 데이터 수집")
        max_posts = st.slider("최대 포스트 수", 10, 100, 30, 10)
        
        # 네트워크 설정
        st.subheader("🕸️ 네트워크 설정")
        min_edge_weight = st.slider("최소 연결 강도", 0.1, 1.0, 0.3, 0.1)
        max_nodes = st.slider("최대 노드 수", 5, 30, 15, 5)
        layout_type = st.selectbox("레이아웃", ["spring", "circular", "kamada_kawai"])
        
        # 분석 실행 버튼
        if st.button("🔍 실제 데이터 분석 실행", type="primary", key="real_network_analysis"):
            st.session_state.run_real_analysis = True
        
        # Reddit 연결 상태 표시
        st.markdown("---")
        st.subheader("📊 Reddit 연결 상태")
        
        try:
            collector = RealRedditCollector()
            st.success("✅ Reddit API 연결 성공")
            st.info("📱 실제 경제 서브레딧에서 데이터를 수집합니다")
        except Exception as e:
            st.error(f"❌ Reddit 연결 실패: {str(e)}")
            st.warning("⚠️ .env 파일의 Reddit API 키를 확인하세요")
    
    # 메인 컨텐츠
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 실제 Reddit 데이터 기반 경제 개념 네트워크")
        
        # 분석 실행
        if st.session_state.get('run_real_analysis', False):
            with st.spinner("실제 Reddit 데이터 수집 및 분석 중..."):
                network_data = run_real_network_analysis(max_posts, min_edge_weight, max_nodes)
                st.session_state.real_network_data = network_data
                st.session_state.run_real_analysis = False
        
        # 네트워크 시각화
        if 'real_network_data' in st.session_state:
            network_data = st.session_state.real_network_data
            
            if 'error' not in network_data:
                # 데이터 소스 정보 표시
                st.info(f"📱 실제 Reddit 데이터 {network_data.get('text_count', 0)}개 텍스트 분석 결과")
                
                # 네트워크 그래프 생성
                fig = create_real_network_visualization(network_data, layout_type, min_edge_weight)
                st.plotly_chart(fig, use_container_width=True, height=600)
                
                # 네트워크 메트릭 표시
                display_real_network_metrics(network_data)
                
                # Reddit 데이터 상세 정보
                if 'reddit_stats' in network_data:
                    display_reddit_stats(network_data['reddit_stats'])
                    
            else:
                st.error(f"분석 오류: {network_data['error']}")
                st.info("💡 .env 파일의 Reddit API 키를 확인하고 다시 시도해보세요")
        else:
            # 초기 상태
            st.info("👆 사이드바에서 '실제 데이터 분석 실행' 버튼을 클릭하여 분석을 시작하세요.")
            
            # 시스템 정보 표시
            display_system_info()
    
    with col2:
        st.subheader("📈 분석 결과")
        
        if 'real_network_data' in st.session_state and 'error' not in st.session_state.real_network_data:
            network_data = st.session_state.real_network_data
            
            # 주요 인사이트
            st.markdown("### 🎯 실제 데이터 인사이트")
            analyzer = FixedEnhancedNetworkAnalyzer()
            insights = analyzer.generate_network_insights(network_data)
            
            for insight in insights:
                st.markdown(f"• {insight}")
            
            # 상위 개념들
            st.markdown("### 🏆 핵심 경제 개념")
            display_top_concepts(network_data)
            
            # 관계 유형 분포
            st.markdown("### 🔗 관계 유형 분포")
            display_relationship_distribution(network_data)
            
            # Reddit 서브레딧별 기여도
            if 'reddit_stats' in network_data:
                st.markdown("### 📱 서브레딧별 기여도")
                display_subreddit_contribution(network_data['reddit_stats'])
        
        else:
            st.markdown("### 📋 분석 대기 중")
            st.info("실제 Reddit 데이터 분석을 실행하면 여기에 결과가 표시됩니다.")
            
            # 개선 사항 설명
            st.markdown("### ✨ 실제 데이터 분석의 장점")
            st.markdown("""
            **🚀 실제 데이터 사용:**
            - ✅ **실제 Reddit 포스트**: 가상 데이터 없음
            - ✅ **실시간 경제 토론**: 현재 이슈 반영
            - ✅ **다양한 관점**: 8개 경제 서브레딧
            - ✅ **감정 분석**: 실제 투자자 심리 반영
            - ✅ **신뢰성**: API 키 기반 공식 데이터
            """)

@st.cache_data(ttl=300)
def run_real_network_analysis(max_posts: int, min_edge_weight: float, max_nodes: int) -> dict:
    """실제 Reddit 데이터를 사용한 네트워크 분석 실행"""
    
    try:
        # Reddit 데이터 수집
        collector = RealRedditCollector()
        texts = collector.get_texts_for_network_analysis(max_posts=max_posts)
        
        if not texts:
            return {'error': 'Reddit 데이터 수집 실패 - 텍스트가 없습니다'}
        
        # 추가 통계 정보 수집
        posts_data = collector.collect_economic_posts(max_posts_per_subreddit=max_posts//8)
        reddit_stats = posts_data.get('subreddit_stats', {})
        
        # 네트워크 분석 실행
        analyzer = FixedEnhancedNetworkAnalyzer()
        network_result = analyzer.analyze_concept_relationships(texts)
        
        if 'error' in network_result:
            return network_result
        
        # 노드 수 제한
        if network_result.get('graph') and len(network_result['graph'].nodes()) > max_nodes:
            G = network_result['graph']
            node_scores = [(node, data.get('score', 0)) for node, data in G.nodes(data=True)]
            top_nodes = sorted(node_scores, key=lambda x: x[1], reverse=True)[:max_nodes]
            top_node_names = [node for node, _ in top_nodes]
            
            # 서브그래프 생성
            subG = G.subgraph(top_node_names).copy()
            network_result['graph'] = subG
            network_result['node_count'] = len(subG.nodes())
            network_result['edge_count'] = len(subG.edges())
        
        # 추가 정보 포함
        network_result['text_count'] = len(texts)
        network_result['reddit_stats'] = reddit_stats
        network_result['data_source'] = 'Real Reddit Data'
        
        return network_result
        
    except Exception as e:
        return {'error': f'분석 실행 중 오류: {str(e)}'}

def create_real_network_visualization(network_data: dict, layout_type: str, min_edge_weight: float):
    """실제 데이터 기반 네트워크 시각화 생성"""
    
    G = network_data['graph']
    
    if len(G.nodes()) == 0:
        fig = go.Figure()
        fig.add_annotation(text="분석할 데이터가 없습니다", 
                          xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False)
        return fig
    
    # 레이아웃 계산
    if layout_type == "spring":
        pos = nx.spring_layout(G, k=2, iterations=50)
    elif layout_type == "circular":
        pos = nx.circular_layout(G)
    else:  # kamada_kawai
        pos = nx.kamada_kawai_layout(G)
    
    # 엣지 트레이스 생성
    edge_x = []
    edge_y = []
    edge_weights = []
    
    for edge in G.edges(data=True):
        if edge[2].get('weight', 0) >= min_edge_weight:
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_weights.append(edge[2].get('weight', 0))
    
    edge_trace = go.Scatter(x=edge_x, y=edge_y,
                           line=dict(width=1, color='#888'),
                           hoverinfo='none',
                           mode='lines')
    
    # 노드 트레이스 생성
    node_x = []
    node_y = []
    node_text = []
    node_info = []
    node_size = []
    node_color = []
    
    # 카테고리별 색상 매핑
    category_colors = {
        'monetary_policy': '#FF6B6B',
        'inflation': '#4ECDC4',
        'stock_market': '#45B7D1',
        'corporate_performance': '#96CEB4',
        'technology': '#FFEAA7',
        'financial_sector': '#DDA0DD',
        'energy': '#FFA07A',
        'real_estate': '#98D8C8',
        'international_trade': '#F7DC6F',
        'cryptocurrency': '#BB8FCE',
        'esg': '#85C1E9',
        'labor_market': '#F8C471',
        'consumer_spending': '#82E0AA',
        'government_policy': '#F1948A',
        'geopolitical_risk': '#D7DBDD',
        'market_sentiment': '#AED6F1'
    }
    
    analyzer = FixedEnhancedNetworkAnalyzer()
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        # 노드 정보
        node_data = G.nodes[node]
        score = node_data.get('score', 0)
        mentions = node_data.get('mentions', 0)
        sentiment = node_data.get('sentiment', 0)
        terms = node_data.get('terms', [])
        
        # 표시 이름
        display_name = analyzer._get_concept_display_name(node)
        node_text.append(display_name)
        
        # 호버 정보
        sentiment_emoji = "😊" if sentiment > 0.1 else "😟" if sentiment < -0.1 else "😐"
        info = f"<b>{display_name}</b><br>"
        info += f"점수: {score:.1f}<br>"
        info += f"Reddit 언급: {mentions}회<br>"
        info += f"감정: {sentiment_emoji} ({sentiment:.2f})<br>"
        info += f"관련 용어: {', '.join(terms[:3])}"
        node_info.append(info)
        
        # 노드 크기 (점수 기반)
        size = max(15, min(score * 8, 60))
        node_size.append(size)
        
        # 노드 색상 (카테고리 기반)
        color = category_colors.get(node, '#888888')
        node_color.append(color)
    
    node_trace = go.Scatter(x=node_x, y=node_y,
                           mode='markers+text',
                           hoverinfo='text',
                           text=node_text,
                           hovertext=node_info,
                           textposition="middle center",
                           marker=dict(size=node_size,
                                     color=node_color,
                                     line=dict(width=2, color='white')))
    
    # 그래프 생성
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                        title=dict(
                            text=f'실제 Reddit 데이터 기반 경제 개념 네트워크<br>({len(G.nodes())}개 노드, {len(G.edges())}개 연결)',
                            font=dict(size=16)
                        ),
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=60),
                        annotations=[ dict(
                            text="📱 실제 Reddit 데이터 | 노드 크기: 언급 빈도 | 색상: 경제 카테고리",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002,
                            xanchor='left', yanchor='bottom',
                            font=dict(size=10)
                        )],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        height=600))
    
    return fig

def display_system_info():
    """시스템 정보 표시"""
    st.info("🎯 **실제 Reddit 데이터 분석 시스템**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📱 데이터 소스:**
        - r/economics (경제학)
        - r/investing (투자)
        - r/stocks (주식)
        - r/personalfinance (개인금융)
        """)
    
    with col2:
        st.markdown("""
        **🔍 분석 기능:**
        - 실시간 Reddit 포스트 수집
        - 경제 개념 자동 추출
        - 감정 분석 통합
        - 네트워크 관계 분석
        """)

def display_real_network_metrics(network_data: dict):
    """실제 네트워크 메트릭 표시"""
    metrics = network_data.get('metrics', {})
    
    if not metrics:
        return
    
    st.markdown("### 📊 네트워크 메트릭")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("노드 수", network_data.get('node_count', 0))
    
    with col2:
        st.metric("연결 수", network_data.get('edge_count', 0))
    
    with col3:
        density = metrics.get('density', 0)
        st.metric("네트워크 밀도", f"{density:.3f}")
    
    with col4:
        text_count = network_data.get('text_count', 0)
        st.metric("분석 텍스트", f"{text_count}개")

def display_top_concepts(network_data: dict):
    """상위 개념들 표시"""
    metrics = network_data.get('metrics', {})
    
    if 'top_nodes' in metrics:
        top_by_degree = metrics['top_nodes'].get('by_degree', [])
        
        if top_by_degree:
            analyzer = FixedEnhancedNetworkAnalyzer()
            
            for i, (concept, centrality) in enumerate(top_by_degree[:5], 1):
                display_name = analyzer._get_concept_display_name(concept)
                st.markdown(f"{i}. **{display_name}** (중심성: {centrality:.3f})")

def display_relationship_distribution(network_data: dict):
    """관계 유형 분포 표시"""
    G = network_data.get('graph')
    
    if not G:
        return
    
    # 관계 유형 집계
    relationship_counts = {}
    for _, _, data in G.edges(data=True):
        rel_type = data.get('relationship_type', 'unknown')
        relationship_counts[rel_type] = relationship_counts.get(rel_type, 0) + 1
    
    if relationship_counts:
        # 바 차트 생성
        fig = px.bar(
            x=list(relationship_counts.keys()),
            y=list(relationship_counts.values()),
            title="관계 유형별 분포"
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

def display_reddit_stats(reddit_stats: dict):
    """Reddit 통계 표시"""
    st.markdown("### 📱 Reddit 데이터 수집 통계")
    
    successful_subreddits = []
    failed_subreddits = []
    
    for subreddit, stats in reddit_stats.items():
        if 'error' in stats:
            failed_subreddits.append(subreddit)
        else:
            successful_subreddits.append((subreddit, stats.get('posts_collected', 0)))
    
    # 성공한 서브레딧
    if successful_subreddits:
        st.markdown("**✅ 수집 성공:**")
        for subreddit, count in successful_subreddits:
            st.markdown(f"• r/{subreddit}: {count}개 포스트")
    
    # 실패한 서브레딧
    if failed_subreddits:
        st.markdown("**❌ 수집 실패:**")
        for subreddit in failed_subreddits:
            st.markdown(f"• r/{subreddit}")

def display_subreddit_contribution(reddit_stats: dict):
    """서브레딧별 기여도 표시"""
    
    subreddit_data = []
    for subreddit, stats in reddit_stats.items():
        if 'error' not in stats:
            subreddit_data.append({
                'subreddit': f"r/{subreddit}",
                'posts': stats.get('posts_collected', 0),
                'subscribers': stats.get('subscribers', 0)
            })
    
    if subreddit_data:
        df = pd.DataFrame(subreddit_data)
        
        # 포스트 수 기준 파이 차트
        fig = px.pie(df, values='posts', names='subreddit', 
                    title="서브레딧별 포스트 기여도")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    create_real_network_page()
