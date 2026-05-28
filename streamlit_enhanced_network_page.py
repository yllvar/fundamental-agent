#!/usr/bin/env python3
"""
개선된 경제 개념 네트워크 분석 Streamlit 페이지
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
import random

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_monitoring.enhanced_economic_network_analyzer import EnhancedEconomicNetworkAnalyzer

def create_enhanced_network_page():
    """개선된 네트워크 분석 페이지 생성"""
    
    st.title("🕸️ 개선된 경제 개념 네트워크 분석")
    st.markdown("---")
    
    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ 분석 설정")
        
        # 데이터 소스 선택
        data_source = st.selectbox(
            "데이터 소스",
            ["자동 선택", "Reddit 전용", "무료 대안 (Reddit+Nitter)", "시뮬레이션 데이터"]
        )
        
        # 데이터 소스 정보 표시
        if data_source == "자동 선택":
            st.info("💡 API 키 유무에 따라 최적의 소스를 자동 선택합니다")
        elif data_source == "Reddit 전용":
            st.info("📱 Reddit 경제 서브레딧에서 실제 데이터를 수집합니다")
        elif data_source == "무료 대안 (Reddit+Nitter)":
            st.info("🆓 여러 무료 소스를 조합하여 데이터를 수집합니다")
        else:
            st.info("🎭 현실적인 시뮬레이션 데이터를 사용합니다")
        
        # 네트워크 설정
        st.subheader("네트워크 설정")
        min_edge_weight = st.slider("최소 연결 강도", 0.1, 1.0, 0.3, 0.1)
        max_nodes = st.slider("최대 노드 수", 10, 50, 30, 5)
        layout_type = st.selectbox("레이아웃", ["spring", "circular", "kamada_kawai", "random"])
        
        # 분석 실행 버튼
        if st.button("🔍 네트워크 분석 실행", type="primary", key="enhanced_network_analysis"):
            st.session_state.run_analysis = True
    
    # 메인 컨텐츠
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 경제 개념 네트워크")
        
        # 분석 실행
        if st.session_state.get('run_analysis', False):
            with st.spinner("네트워크 분석 중..."):
                network_data = run_enhanced_network_analysis(
                    data_source, min_edge_weight, max_nodes
                )
                st.session_state.network_data = network_data
                st.session_state.run_analysis = False
        
        # 네트워크 시각화
        if 'network_data' in st.session_state:
            network_data = st.session_state.network_data
            
            if 'error' not in network_data:
                # 네트워크 그래프 생성
                fig = create_enhanced_network_visualization(
                    network_data, layout_type, min_edge_weight
                )
                st.plotly_chart(fig, use_container_width=True, height=600)
                
                # 네트워크 메트릭 표시
                display_network_metrics(network_data)
            else:
                st.error(f"분석 오류: {network_data['error']}")
        else:
            # 초기 상태 - 샘플 네트워크 표시
            st.info("👆 사이드바에서 '네트워크 분석 실행' 버튼을 클릭하여 분석을 시작하세요.")
            display_sample_network()
    
    with col2:
        st.subheader("📈 분석 결과")
        
        if 'network_data' in st.session_state and 'error' not in st.session_state.network_data:
            network_data = st.session_state.network_data
            
            # 주요 인사이트
            st.markdown("### 🎯 주요 인사이트")
            analyzer = EnhancedEconomicNetworkAnalyzer()
            insights = analyzer.generate_network_insights(network_data)
            
            for insight in insights:
                st.markdown(f"• {insight}")
            
            # 상위 개념들
            st.markdown("### 🏆 핵심 경제 개념")
            display_top_concepts(network_data)
            
            # 관계 유형 분포
            st.markdown("### 🔗 관계 유형 분포")
            display_relationship_distribution(network_data)
            
            # 감정 분석 결과
            st.markdown("### 😊 감정 분석")
            display_sentiment_analysis(network_data)
        
        else:
            st.markdown("### 📋 분석 대기 중")
            st.info("네트워크 분석을 실행하면 여기에 결과가 표시됩니다.")
            
            # 개선 사항 설명
            st.markdown("### ✨ 개선된 기능")
            st.markdown("""
            **🚀 주요 개선사항:**
            - **50+ 노드**: 16개 경제 카테고리 × 다양한 세부 개념
            - **의미 있는 관계**: 단순 동시출현 → 경제적 연관성
            - **가중치 시스템**: 개념 중요도 및 관계 강도 반영
            - **감정 분석**: 개념별 긍정/부정 감정 분석
            - **시간적 분석**: 트렌드 변화 추적
            - **인터랙티브**: 실시간 필터링 및 탐색
            """)

@st.cache_data(ttl=300)
def run_enhanced_network_analysis(data_source: str, min_edge_weight: float, max_nodes: int) -> dict:
    """개선된 네트워크 분석 실행"""
    
    analyzer = EnhancedEconomicNetworkAnalyzer()
    
    try:
        # 통합 소셜 데이터 수집기 사용
        from data_monitoring.integrated_social_collector import IntegratedSocialCollector
        
        collector = IntegratedSocialCollector()
        
        # 데이터 소스 매핑
        source_mapping = {
            "자동 선택": "auto",
            "Reddit 전용": "reddit_only", 
            "무료 대안 (Reddit+Nitter)": "free_alternatives",
            "시뮬레이션 데이터": "simulation"
        }
        
        mapped_source = source_mapping.get(data_source, "simulation")
        
        # 실제 소셜 데이터 수집
        sample_texts = collector.collect_social_data_for_network_analysis(
            data_source=mapped_source,
            max_items=50
        )
        
        # 백업: 샘플 데이터가 없으면 기본 샘플 사용
        if not sample_texts:
            sample_texts = generate_sample_economic_texts("시뮬레이션 데이터")
        
    except Exception as e:
        st.warning(f"⚠️ 실제 데이터 수집 실패: {e}")
        # 백업: 기본 샘플 데이터 사용
        sample_texts = generate_sample_economic_texts(data_source)
    
    try:
        # 네트워크 분석 실행
        network_result = analyzer.analyze_concept_relationships(sample_texts)
        
        # 노드 수 제한
        if network_result.get('graph') and len(network_result['graph'].nodes()) > max_nodes:
            # 중요도 기준으로 상위 노드만 선택
            G = network_result['graph']
            node_scores = [(node, data.get('score', 0)) for node, data in G.nodes(data=True)]
            top_nodes = sorted(node_scores, key=lambda x: x[1], reverse=True)[:max_nodes]
            top_node_names = [node for node, _ in top_nodes]
            
            # 서브그래프 생성
            subG = G.subgraph(top_node_names).copy()
            network_result['graph'] = subG
            network_result['node_count'] = len(subG.nodes())
            network_result['edge_count'] = len(subG.edges())
        
        # 데이터 소스 정보 추가
        network_result['data_source'] = data_source
        network_result['text_count'] = len(sample_texts)
        
        return network_result
        
    except Exception as e:
        return {'error': str(e), 'data_source': data_source}

def generate_sample_economic_texts(data_source: str) -> list:
    """데이터 소스별 샘플 텍스트 생성"""
    
    if data_source == "샘플 경제 뉴스":
        return [
            "연준이 기준금리를 0.25%p 인상하며 인플레이션 억제에 나섰다. 이번 금리 인상으로 주식시장은 하락세를 보이고 있으며, 특히 기술주가 큰 타격을 받고 있다.",
            "애플과 마이크로소프트가 AI 기술 개발을 위한 파트너십을 발표했다. 이는 기술 섹터의 경쟁력 강화와 함께 관련 주가 상승을 이끌고 있다.",
            "중국과 미국 간의 무역 분쟁이 재점화되면서 글로벌 공급망에 차질이 우려된다. 이로 인해 원자재 가격이 상승하고 인플레이션 압력이 증가하고 있다.",
            "비트코인이 다시 5만 달러를 돌파하며 암호화폐 시장이 활기를 띠고 있다. 기관 투자자들의 관심 증가와 함께 디지털 자산에 대한 투자 심리가 개선되고 있다.",
            "ESG 투자가 주류로 자리잡으면서 친환경 기업들의 주가가 상승하고 있다. 특히 재생에너지와 전기차 관련 기업들이 큰 관심을 받고 있다.",
            "고용시장이 개선되면서 실업률이 3.5%로 하락했다. 이는 소비자 신뢰도 상승과 함께 소비 증가로 이어질 것으로 예상된다.",
            "부동산 시장이 금리 인상에도 불구하고 견조한 모습을 보이고 있다. 주택 공급 부족과 함께 가격 상승 압력이 지속되고 있다.",
            "에너지 가격 상승으로 인플레이션 우려가 커지고 있다. 특히 원유와 천연가스 가격 급등이 전체 물가 상승을 주도하고 있다.",
            "정부의 대규모 인프라 투자 계획이 발표되면서 건설 및 소재 관련 주식들이 강세를 보이고 있다. 이는 경기 부양 효과와 함께 고용 창출에도 기여할 것으로 예상된다.",
            "지정학적 리스크가 증가하면서 안전자산 선호 현상이 나타나고 있다. 금과 국채 가격이 상승하는 반면, 위험자산인 주식은 변동성이 확대되고 있다."
        ]
    
    elif data_source == "Reddit 댓글":
        return [
            "Fed가 또 금리 올렸네... 내 주식 포트폴리오가 걱정된다. 특히 테크주들이 많이 떨어졌어.",
            "인플레이션이 이렇게 계속 오르면 생활비가 너무 부담스러워. 정부가 뭔가 대책을 내놔야 할 것 같은데.",
            "비트코인 다시 오르기 시작했네! 이번엔 진짜 10만 달러까지 갈 수 있을까?",
            "ESG 투자가 트렌드라고 하는데, 정말 수익성이 있을까? 아직 확신이 안 서네.",
            "애플 실적 발표 앞두고 있는데, 이번 분기는 어떨까? iPhone 판매량이 관건일 것 같아.",
            "중국 경제가 둔화되고 있다는 뉴스가 많이 나오는데, 우리나라 경제에도 영향이 클 것 같아.",
            "부동산 가격이 계속 오르고 있어서 집 사기가 너무 어려워졌어. 언제쯤 안정될까?",
            "에너지 주식들이 요즘 좋은 것 같은데, 장기적으로 투자해볼 만할까?",
            "실업률이 낮아졌다고 하는데, 체감상으로는 취업이 여전히 어려운 것 같아.",
            "전쟁 때문에 시장이 불안정해. 안전자산으로 갈아타야 할 시점인가?"
        ]
    
    elif data_source == "Twitter 데이터":
        return [
            "#Fed #금리인상 또 시작됐네. #인플레이션 잡으려다 #경기침체 올 수도 있겠어 #주식시장",
            "#Apple #AI 파트너십 소식에 주가 급등! #기술주 #투자 기회일까? #AAPL",
            "#Bitcoin 5만달러 돌파! #암호화폐 #불마켓 다시 시작되나? #BTC #투자",
            "#ESG투자 열풍 속에서 #친환경 기업들 주목받고 있어 #지속가능투자 #그린에너지",
            "#무역전쟁 재점화? #중미관계 악화로 #공급망 차질 우려 #글로벌경제",
            "#고용시장 개선으로 #소비심리 회복 기대 #실업률 하락 #경기회복",
            "#부동산 가격 여전히 상승세 #금리인상에도 불구하고 #주택시장 견조",
            "#에너지가격 급등으로 #인플레이션 압력 증가 #원유 #천연가스",
            "#정부 #인프라투자 계획 발표 #건설주 #소재주 관심 증가",
            "#지정학적리스크 증가로 #안전자산 선호 #금 #국채 가격 상승"
        ]
    
    else:  # 뉴스 댓글
        return [
            "금리 인상이 계속되면 서민들 대출 부담만 늘어날 텐데... 정책 당국이 좀 더 신중하게 접근했으면 좋겠어요.",
            "기술주 투자했다가 큰 손실 봤습니다. 앞으로는 좀 더 안정적인 투자처를 찾아야겠어요.",
            "인플레이션 때문에 장보기가 부담스러워졌어요. 특히 식료품 가격이 너무 많이 올랐네요.",
            "암호화폐 투자는 여전히 위험하다고 생각해요. 변동성이 너무 커서 일반인들이 접근하기 어려워요.",
            "ESG 투자가 좋다고는 하는데, 실제로 수익률이 어떤지 궁금하네요. 장기적으로는 좋을 것 같긴 해요.",
            "고용시장이 좋아졌다고 하지만, 청년 취업은 여전히 어려운 것 같아요. 양질의 일자리가 부족해요.",
            "부동산 투자는 이제 일반인들이 접근하기 어려운 수준이 된 것 같아요. 정부 대책이 필요해요.",
            "에너지 가격 상승이 모든 물가에 영향을 미치고 있어요. 대체 에너지 개발이 시급해 보여요.",
            "정부의 경기 부양책이 효과가 있을지 의문이에요. 근본적인 구조 개선이 필요한 것 같아요.",
            "국제 정세가 불안해서 투자하기가 조심스러워요. 당분간은 현금 보유 비중을 늘려야겠어요."
        ]

def create_enhanced_network_visualization(network_data: dict, layout_type: str, min_edge_weight: float):
    """개선된 네트워크 시각화 생성"""
    
    G = network_data['graph']
    
    if len(G.nodes()) == 0:
        # 빈 그래프 처리
        fig = go.Figure()
        fig.add_annotation(text="분석할 데이터가 없습니다", 
                          xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False)
        return fig
    
    # 레이아웃 계산
    if layout_type == "spring":
        pos = nx.spring_layout(G, k=3, iterations=50)
    elif layout_type == "circular":
        pos = nx.circular_layout(G)
    elif layout_type == "kamada_kawai":
        pos = nx.kamada_kawai_layout(G)
    else:  # random
        pos = nx.random_layout(G)
    
    # 엣지 트레이스 생성
    edge_x = []
    edge_y = []
    edge_info = []
    
    for edge in G.edges(data=True):
        if edge[2].get('weight', 0) >= min_edge_weight:
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
            weight = edge[2].get('weight', 0)
            rel_type = edge[2].get('relationship_type', 'related')
            edge_info.append(f"{edge[0]} ↔ {edge[1]}<br>강도: {weight:.2f}<br>유형: {rel_type}")
    
    edge_trace = go.Scatter(x=edge_x, y=edge_y,
                           line=dict(width=0.5, color='#888'),
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
        'monetary_policy': '#FF6B6B',      # 빨강
        'inflation': '#4ECDC4',           # 청록
        'stock_market': '#45B7D1',        # 파랑
        'corporate_performance': '#96CEB4', # 연두
        'technology': '#FFEAA7',          # 노랑
        'financial_sector': '#DDA0DD',     # 보라
        'energy': '#FFA07A',              # 주황
        'real_estate': '#98D8C8',         # 민트
        'international_trade': '#F7DC6F', # 연노랑
        'cryptocurrency': '#BB8FCE',       # 연보라
        'esg': '#85C1E9',                 # 연파랑
        'labor_market': '#F8C471',        # 연주황
        'consumer_spending': '#82E0AA',    # 연초록
        'government_policy': '#F1948A',    # 연빨강
        'geopolitical_risk': '#D7DBDD',    # 회색
        'market_sentiment': '#AED6F1'      # 하늘색
    }
    
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
        analyzer = EnhancedEconomicNetworkAnalyzer()
        display_name = analyzer._get_concept_display_name(node)
        node_text.append(display_name)
        
        # 호버 정보
        sentiment_emoji = "😊" if sentiment > 0.1 else "😟" if sentiment < -0.1 else "😐"
        info = f"<b>{display_name}</b><br>"
        info += f"점수: {score:.1f}<br>"
        info += f"언급 횟수: {mentions}<br>"
        info += f"감정: {sentiment_emoji} ({sentiment:.2f})<br>"
        info += f"관련 용어: {', '.join(terms[:3])}"
        node_info.append(info)
        
        # 노드 크기 (점수 기반)
        size = max(10, min(score * 5, 50))
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
                            text=f'경제 개념 네트워크 ({len(G.nodes())}개 노드, {len(G.edges())}개 연결)',
                            font=dict(size=16)
                        ),
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40),
                        annotations=[ dict(
                            text="노드 크기: 중요도 | 색상: 경제 카테고리",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002,
                            xanchor='left', yanchor='bottom',
                            font=dict(size=12)
                        )],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        height=600))
    
    return fig

def display_sample_network():
    """샘플 네트워크 표시"""
    st.info("🎯 **개선된 네트워크 분석의 특징:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📈 더 많은 노드:**
        - 16개 주요 경제 카테고리
        - 각 카테고리별 10-20개 세부 개념
        - 총 50-100개 노드 생성 가능
        
        **🔗 의미 있는 관계:**
        - 경제적 인과관계 분석
        - 상관관계 vs 역상관관계 구분
        - 시간적 선후관계 고려
        """)
    
    with col2:
        st.markdown("""
        **🎨 향상된 시각화:**
        - 카테고리별 색상 구분
        - 중요도 기반 노드 크기
        - 관계 강도별 연결선 굵기
        
        **📊 고급 분석:**
        - 감정 분석 통합
        - 네트워크 중심성 지표
        - 실시간 인사이트 생성
        """)

def display_network_metrics(network_data: dict):
    """네트워크 메트릭 표시"""
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
        clustering = metrics.get('average_clustering', 0)
        st.metric("평균 클러스터링", f"{clustering:.3f}")

def display_top_concepts(network_data: dict):
    """상위 개념들 표시"""
    metrics = network_data.get('metrics', {})
    
    if 'top_nodes' in metrics:
        top_by_degree = metrics['top_nodes'].get('by_degree', [])
        
        if top_by_degree:
            analyzer = EnhancedEconomicNetworkAnalyzer()
            
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
        # 파이 차트 생성
        fig = px.pie(
            values=list(relationship_counts.values()),
            names=list(relationship_counts.keys()),
            title="관계 유형 분포"
        )
        st.plotly_chart(fig, use_container_width=True)

def display_sentiment_analysis(network_data: dict):
    """감정 분석 결과 표시"""
    concept_sentiments = network_data.get('concept_sentiments', {})
    
    if not concept_sentiments:
        st.info("감정 분석 데이터가 없습니다.")
        return
    
    # 감정 점수 계산
    sentiment_data = []
    analyzer = EnhancedEconomicNetworkAnalyzer()
    
    for concept, sentiments in concept_sentiments.items():
        if sentiments:
            avg_sentiment = np.mean(sentiments)
            display_name = analyzer._get_concept_display_name(concept)
            sentiment_data.append({
                'concept': display_name,
                'sentiment': avg_sentiment,
                'emoji': "😊" if avg_sentiment > 0.1 else "😟" if avg_sentiment < -0.1 else "😐"
            })
    
    # 감정별로 정렬
    sentiment_data.sort(key=lambda x: x['sentiment'], reverse=True)
    
    # 상위 5개 표시
    for data in sentiment_data[:5]:
        sentiment_color = "green" if data['sentiment'] > 0 else "red" if data['sentiment'] < 0 else "gray"
        st.markdown(f"{data['emoji']} **{data['concept']}**: "
                   f"<span style='color: {sentiment_color}'>{data['sentiment']:.3f}</span>", 
                   unsafe_allow_html=True)

if __name__ == "__main__":
    create_enhanced_network_page()
