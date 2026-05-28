#!/usr/bin/env python3
"""
소셜 네트워크 분석 Streamlit 페이지
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

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_monitoring.social_network_analyzer import SocialNetworkAnalyzer

@st.cache_data(ttl=300)  # 5분 캐시
def analyze_network_data(news_data):
    """네트워크 분석 수행 (캐시됨)"""
    try:
        analyzer = SocialNetworkAnalyzer()
        
        # 뉴스 데이터 구조 확인 및 추출
        if news_data.get('status') == 'success':
            # 실제 뉴스 데이터 구조에 맞게 추출
            news_info = news_data.get('data', {}).get('news_data', {})
            
            # 뉴스 데이터에서 네트워크 분석
            news_network = analyzer.analyze_news_network(news_info)
        else:
            # 샘플 데이터로 대체
            sample_news_data = {
                'categories': {
                    'financial': [
                        {
                            'title': 'Federal Reserve raises interest rates amid inflation concerns',
                            'summary': 'Jerome Powell announced the Fed decision to combat rising inflation',
                            'sentiment': {'polarity': -0.2}
                        },
                        {
                            'title': 'Apple and Microsoft partnership on AI technology',
                            'summary': 'Tech giants collaborate on artificial intelligence development',
                            'sentiment': {'polarity': 0.3}
                        }
                    ]
                }
            }
            news_network = analyzer.analyze_news_network(sample_news_data)
        
        # Reddit 데이터 분석 (시뮬레이션)
        reddit_network = analyzer.analyze_reddit_network({})
        
        # 인사이트 생성
        insights = analyzer.generate_network_insights(news_network, reddit_network)
        
        return {
            'news_network': news_network,
            'reddit_network': reddit_network,
            'insights': insights
        }, None
        
    except Exception as e:
        import traceback
        error_details = f"{str(e)}\n{traceback.format_exc()}"
        return None, error_details

def show_network_analysis_page(news_data):
    """소셜 네트워크 분석 메인 페이지"""
    st.header("🕸️ 소셜 네트워크 분석")
    st.markdown("**뉴스 및 SNS 데이터를 활용한 엔티티 관계 분석**")
    
    # 네트워크 분석 수행
    with st.spinner("🔄 네트워크 분석 수행 중..."):
        network_data, error = analyze_network_data(news_data)
    
    if error:
        st.error(f"❌ 네트워크 분석 실패: {error}")
        return
    
    if not network_data:
        st.warning("⚠️ 네트워크 분석 데이터가 없습니다.")
        return
    
    # 분석 요약
    show_network_summary(network_data)
    
    st.markdown("---")
    
    # 탭으로 구분
    tab1, tab2, tab3, tab4 = st.tabs(["🌐 뉴스 네트워크", "📱 소셜 네트워크", "🔍 인사이트", "📊 메트릭"])
    
    with tab1:
        show_news_network_analysis(network_data['news_network'])
    
    with tab2:
        show_social_network_analysis(network_data['reddit_network'])
    
    with tab3:
        show_network_insights(network_data['insights'])
    
    with tab4:
        show_network_metrics(network_data)

def show_network_summary(network_data):
    """네트워크 분석 요약"""
    st.subheader("📊 네트워크 분석 요약")
    
    news_network = network_data['news_network']
    reddit_network = network_data['reddit_network']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "뉴스 엔티티",
            news_network.get('total_entities', 0),
            f"관계: {news_network.get('total_relationships', 0)}개"
        )
    
    with col2:
        communities_count = len(news_network.get('communities', []))
        st.metric(
            "엔티티 그룹",
            communities_count,
            "커뮤니티 수"
        )
    
    with col3:
        user_count = reddit_network['user_metrics'].get('nodes_count', 0)
        st.metric(
            "소셜 사용자",
            user_count,
            f"상호작용: {reddit_network['user_metrics'].get('edges_count', 0)}개"
        )
    
    with col4:
        topic_count = reddit_network['topic_metrics'].get('nodes_count', 0)
        st.metric(
            "주제 연관성",
            topic_count,
            f"연결: {reddit_network['topic_metrics'].get('edges_count', 0)}개"
        )

def show_news_network_analysis(news_network):
    """뉴스 네트워크 분석 표시"""
    st.subheader("🌐 뉴스 엔티티 네트워크 분석")
    
    G = news_network.get('graph')
    
    # 네트워크 데이터 상태 확인
    if not G:
        st.warning("⚠️ 네트워크 그래프 객체가 없습니다.")
        st.info("💡 뉴스 데이터에서 충분한 엔티티를 찾지 못했을 수 있습니다.")
        return
    
    if len(G.nodes()) == 0:
        st.warning("⚠️ 네트워크에 노드가 없습니다.")
        st.info("💡 뉴스 텍스트에서 경제 관련 엔티티를 찾지 못했습니다.")
        
        # 디버깅 정보 표시
        with st.expander("🔍 디버깅 정보"):
            st.write("**네트워크 분석 결과:**")
            st.write(f"- 총 엔티티: {news_network.get('total_entities', 0)}개")
            st.write(f"- 총 관계: {news_network.get('total_relationships', 0)}개")
            
            entity_mentions = news_network.get('entity_mentions', {})
            if entity_mentions:
                st.write("**발견된 엔티티:**")
                for entity, count in list(entity_mentions.items())[:10]:
                    st.write(f"  • {entity}: {count}회")
            else:
                st.write("**발견된 엔티티가 없습니다.**")
        
        return
    
    # 네트워크 기본 정보 표시
    st.info(f"📊 **네트워크 정보**: {len(G.nodes())}개 엔티티, {len(G.edges())}개 관계")
    
    # 네트워크 시각화
    st.markdown("#### 📈 네트워크 시각화")
    
    try:
        # NetworkX 그래프를 Plotly로 시각화
        fig = create_network_visualization(G, "뉴스 엔티티 네트워크")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"❌ 네트워크 시각화 오류: {e}")
        st.info("💡 네트워크가 너무 크거나 복잡할 수 있습니다.")
    
    # 중요한 엔티티 표시
    st.markdown("#### 🏆 중요한 엔티티")
    
    important_nodes = news_network.get('important_nodes', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎯 중심성 기준 상위 엔티티**")
        degree_nodes = important_nodes.get('by_degree', [])
        
        if degree_nodes:
            for i, (node, centrality) in enumerate(degree_nodes[:5], 1):
                mentions = G.nodes[node].get('mentions', 0)
                sentiment = G.nodes[node].get('avg_sentiment', 0)
                
                sentiment_emoji = "🟢" if sentiment > 0.1 else "🔴" if sentiment < -0.1 else "🟡"
                
                st.write(f"**{i}. {sentiment_emoji} {node}**")
                st.caption(f"중심성: {centrality:.3f} | 언급: {mentions}회 | 감정: {sentiment:+.2f}")
        else:
            st.info("중심성 데이터가 없습니다.")
    
    with col2:
        st.markdown("**📢 언급 빈도 기준 상위 엔티티**")
        mention_nodes = important_nodes.get('by_mentions', [])
        
        if mention_nodes:
            for i, (node, mentions) in enumerate(mention_nodes[:5], 1):
                sentiment = G.nodes[node].get('avg_sentiment', 0)
                sentiment_emoji = "🟢" if sentiment > 0.1 else "🔴" if sentiment < -0.1 else "🟡"
                
                st.write(f"**{i}. {sentiment_emoji} {node}**")
                st.caption(f"언급: {mentions}회 | 감정: {sentiment:+.2f}")
        else:
            st.info("언급 빈도 데이터가 없습니다.")
    
    # 주요 관계 표시
    st.markdown("#### 🔗 주요 엔티티 간 관계")
    
    if len(G.edges()) > 0:
        # 가중치가 높은 관계들
        edges_by_weight = sorted(G.edges(data=True), 
                               key=lambda x: x[2].get('weight', 0), reverse=True)
        
        relationships_data = []
        for source, target, data in edges_by_weight[:10]:
            relationships_data.append({
                '엔티티 1': source,
                '엔티티 2': target,
                '관계 강도': data.get('weight', 0),
                '관계 유형': data.get('relationship_type', 'unknown'),
                '맥락 예시': data.get('contexts', [''])[0][:80] + "..." if data.get('contexts') else 'N/A'
            })
        
        if relationships_data:
            df = pd.DataFrame(relationships_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("관계 데이터가 없습니다.")
    else:
        st.info("엔티티 간 관계가 발견되지 않았습니다.")
    
    # 커뮤니티 분석
    st.markdown("#### 👥 엔티티 커뮤니티")
    
    communities = news_network.get('communities', [])
    if communities:
        for i, community in enumerate(communities, 1):
            if len(community) > 1:  # 2개 이상의 노드가 있는 커뮤니티만 표시
                st.write(f"**커뮤니티 {i}**: {', '.join(community)}")
    else:
        st.info("커뮤니티가 발견되지 않았습니다.")

def show_social_network_analysis(reddit_network):
    """소셜 네트워크 분석 표시"""
    st.subheader("📱 소셜 네트워크 분석")
    
    user_network = reddit_network.get('user_network')
    topic_network = reddit_network.get('topic_network')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 👥 사용자 상호작용 네트워크")
        
        if user_network and len(user_network.nodes()) > 0:
            # 사용자 네트워크 시각화
            user_fig = create_network_visualization(user_network, "사용자 상호작용")
            st.plotly_chart(user_fig, use_container_width=True)
            
            # 사용자 네트워크 메트릭
            user_metrics = reddit_network.get('user_metrics', {})
            st.write(f"**사용자 수**: {user_metrics.get('nodes_count', 0)}")
            st.write(f"**상호작용 수**: {user_metrics.get('edges_count', 0)}")
            st.write(f"**네트워크 밀도**: {user_metrics.get('density', 0):.3f}")
        else:
            st.info("사용자 상호작용 데이터가 없습니다.")
    
    with col2:
        st.markdown("#### 🏷️ 주제 연관성 네트워크")
        
        if topic_network and len(topic_network.nodes()) > 0:
            # 주제 네트워크 시각화
            topic_fig = create_network_visualization(topic_network, "주제 연관성")
            st.plotly_chart(topic_fig, use_container_width=True)
            
            # 주제 네트워크 메트릭
            topic_metrics = reddit_network.get('topic_metrics', {})
            st.write(f"**주제 수**: {topic_metrics.get('nodes_count', 0)}")
            st.write(f"**연관성 수**: {topic_metrics.get('edges_count', 0)}")
            st.write(f"**네트워크 밀도**: {topic_metrics.get('density', 0):.3f}")
        else:
            st.info("주제 연관성 데이터가 없습니다.")

def show_network_insights(insights):
    """네트워크 인사이트 표시"""
    st.subheader("🔍 네트워크 분석 인사이트")
    
    news_insights = insights.get('news_insights', {})
    combined_insights = insights.get('combined_insights', {})
    
    # 주요 발견사항
    st.markdown("#### 🔍 주요 발견사항")
    
    key_findings = combined_insights.get('key_findings', [])
    if key_findings:
        for i, finding in enumerate(key_findings, 1):
            st.write(f"**{i}.** {finding}")
    else:
        st.info("주요 발견사항이 없습니다.")
    
    # 추천사항
    st.markdown("#### 💡 추천사항")
    
    recommendations = combined_insights.get('recommendations', [])
    if recommendations:
        for i, recommendation in enumerate(recommendations, 1):
            st.write(f"**{i}.** {recommendation}")
    else:
        st.info("추천사항이 없습니다.")
    
    # 네트워크 특성
    st.markdown("#### 📊 네트워크 특성")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🌐 뉴스 네트워크**")
        if news_insights:
            st.write(f"• 네트워크 크기: {news_insights.get('network_size', 'N/A')}")
            st.write(f"• 네트워크 밀도: {news_insights.get('network_density', 'N/A')}")
            st.write(f"• 클러스터링: {news_insights.get('clustering', 'N/A')}")
            st.write(f"• 커뮤니티 수: {news_insights.get('communities_count', 0)}개")
    
    with col2:
        st.markdown("**📱 소셜 네트워크**")
        reddit_insights = insights.get('reddit_insights', {})
        if reddit_insights:
            st.write(f"• 사용자 네트워크: {reddit_insights.get('user_network_size', 0)}개 노드")
            st.write(f"• 주제 네트워크: {reddit_insights.get('topic_network_size', 0)}개 노드")
            st.write(f"• 사용자 상호작용: {reddit_insights.get('user_interactions', 0)}개")
            st.write(f"• 주제 연관성: {reddit_insights.get('topic_correlations', 0)}개")
    
    # 중심적 엔티티
    st.markdown("#### 🎯 중심적 엔티티")
    
    most_central = news_insights.get('most_central_entities', [])
    most_mentioned = news_insights.get('most_mentioned_entities', [])
    sentiment_leaders = news_insights.get('sentiment_leaders', [])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**중심성 기준**")
        for entity in most_central[:3]:
            st.write(f"• {entity}")
    
    with col2:
        st.markdown("**언급 빈도 기준**")
        for entity in most_mentioned[:3]:
            st.write(f"• {entity}")
    
    with col3:
        st.markdown("**감정 영향력 기준**")
        for entity in sentiment_leaders[:3]:
            st.write(f"• {entity}")

def show_network_metrics(network_data):
    """네트워크 메트릭 상세 표시"""
    st.subheader("📊 네트워크 메트릭 상세")
    
    news_network = network_data['news_network']
    reddit_network = network_data['reddit_network']
    
    # 뉴스 네트워크 메트릭
    st.markdown("#### 🌐 뉴스 네트워크 메트릭")
    
    news_metrics = news_network.get('network_metrics', {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**기본 메트릭**")
        st.write(f"노드 수: {news_metrics.get('nodes_count', 0)}")
        st.write(f"엣지 수: {news_metrics.get('edges_count', 0)}")
        st.write(f"밀도: {news_metrics.get('density', 0):.4f}")
        st.write(f"평균 클러스터링: {news_metrics.get('average_clustering', 0):.4f}")
    
    with col2:
        st.markdown("**연결성 메트릭**")
        if 'diameter' in news_metrics:
            st.write(f"지름: {news_metrics['diameter']}")
            st.write(f"평균 경로 길이: {news_metrics['average_path_length']:.2f}")
        else:
            st.write(f"연결 컴포넌트: {news_metrics.get('connected_components', 'N/A')}")
            st.write(f"최대 컴포넌트: {news_metrics.get('largest_component_size', 'N/A')}")
    
    with col3:
        st.markdown("**중심성 분석**")
        top_degree = news_metrics.get('top_degree_centrality', [])
        if top_degree:
            st.write("**Degree Centrality Top 3:**")
            for node, centrality in top_degree[:3]:
                st.write(f"• {node}: {centrality:.3f}")
    
    # 중심성 비교 차트
    if news_metrics.get('top_degree_centrality'):
        st.markdown("#### 📈 중심성 비교")
        
        degree_data = news_metrics.get('top_degree_centrality', [])[:10]
        betweenness_data = news_metrics.get('top_betweenness_centrality', [])[:10]
        
        # 데이터프레임 생성
        centrality_df = pd.DataFrame({
            'Entity': [item[0] for item in degree_data],
            'Degree_Centrality': [item[1] for item in degree_data]
        })
        
        # 차트 생성
        fig = px.bar(
            centrality_df,
            x='Entity',
            y='Degree_Centrality',
            title="엔티티별 Degree Centrality",
            labels={'Degree_Centrality': 'Degree Centrality', 'Entity': '엔티티'}
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # 소셜 네트워크 메트릭
    st.markdown("#### 📱 소셜 네트워크 메트릭")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**사용자 네트워크**")
        user_metrics = reddit_network.get('user_metrics', {})
        st.write(f"사용자 수: {user_metrics.get('nodes_count', 0)}")
        st.write(f"상호작용 수: {user_metrics.get('edges_count', 0)}")
        st.write(f"밀도: {user_metrics.get('density', 0):.4f}")
        st.write(f"클러스터링: {user_metrics.get('average_clustering', 0):.4f}")
    
    with col2:
        st.markdown("**주제 네트워크**")
        topic_metrics = reddit_network.get('topic_metrics', {})
        st.write(f"주제 수: {topic_metrics.get('nodes_count', 0)}")
        st.write(f"연관성 수: {topic_metrics.get('edges_count', 0)}")
        st.write(f"밀도: {topic_metrics.get('density', 0):.4f}")
        st.write(f"클러스터링: {topic_metrics.get('average_clustering', 0):.4f}")

def create_network_visualization(G, title):
    """NetworkX 그래프를 Plotly로 시각화"""
    
    if len(G.nodes()) == 0:
        # 빈 그래프 처리
        fig = go.Figure()
        fig.add_annotation(text="네트워크 데이터가 없습니다", 
                          xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False)
        fig.update_layout(title=title)
        return fig
    
    # 레이아웃 계산
    pos = nx.spring_layout(G, k=1, iterations=50)
    
    # 엣지 그리기
    edge_x = []
    edge_y = []
    edge_info = []
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        
        # 엣지 정보
        weight = G[edge[0]][edge[1]].get('weight', 1)
        edge_info.append(f"{edge[0]} - {edge[1]}: {weight}")
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    # 노드 그리기
    node_x = []
    node_y = []
    node_text = []
    node_info = []
    node_size = []
    node_color = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
        
        # 노드 정보
        mentions = G.nodes[node].get('mentions', 0)
        sentiment = G.nodes[node].get('avg_sentiment', 0)
        degree = G.degree(node)
        
        node_info.append(f"{node}<br>언급: {mentions}회<br>감정: {sentiment:.2f}<br>연결: {degree}개")
        
        # 노드 크기 (degree 기반)
        node_size.append(max(10, degree * 3))
        
        # 노드 색상 (감정 기반)
        if sentiment > 0.1:
            node_color.append('green')
        elif sentiment < -0.1:
            node_color.append('red')
        else:
            node_color.append('blue')
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        hovertext=node_info,
        textposition="middle center",
        marker=dict(
            size=node_size,
            color=node_color,
            line=dict(width=2, color='white')
        )
    )
    
    # 그래프 생성
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       title=dict(text=title, font=dict(size=16)),
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=20,l=5,r=5,t=40),
                       annotations=[ dict(
                           text="노드 크기: 연결 수 | 색상: 감정 (녹색: 긍정, 빨강: 부정, 파랑: 중립)",
                           showarrow=False,
                           xref="paper", yref="paper",
                           x=0.005, y=-0.002,
                           xanchor="left", yanchor="bottom",
                           font=dict(size=10)
                       )],
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                   ))
    
    return fig

if __name__ == "__main__":
    # 테스트용 샘플 데이터
    sample_news_data = {
        'categories': {
            'financial': [
                {
                    'title': 'Federal Reserve raises interest rates',
                    'summary': 'Jerome Powell announced the decision',
                    'sentiment': {'polarity': -0.2}
                }
            ]
        }
    }
    
    show_network_analysis_page(sample_news_data)
