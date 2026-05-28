#!/usr/bin/env python3
"""
강화된 소셜 네트워크 분석기
경제 개념 중심의 의미 있는 네트워크 구축
"""

import networkx as nx
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter, defaultdict
import re
from textblob import TextBlob

class EnhancedSocialNetworkAnalyzer:
    """강화된 소셜 네트워크 분석기 - 경제 개념 중심"""
    
    def __init__(self):
        """초기화"""
        self.logger = logging.getLogger(__name__)
        
        # 확장된 경제 개념 사전
        self.economic_concepts = {
            # 통화 정책
            'monetary_policy': [
                'federal reserve', 'fed', 'interest rates', 'interest rate', 'rates',
                'monetary policy', 'quantitative easing', 'qe', 'money supply',
                'central bank', 'jerome powell', 'fomc', 'fed funds rate'
            ],
            
            # 인플레이션
            'inflation': [
                'inflation', 'deflation', 'cpi', 'consumer price index',
                'price increases', 'cost of living', 'purchasing power',
                'pce', 'core inflation', 'wage inflation'
            ],
            
            # 고용 시장
            'employment': [
                'unemployment', 'jobs', 'employment', 'labor market',
                'job market', 'hiring', 'layoffs', 'wage growth',
                'labor force', 'jobless claims', 'nonfarm payrolls'
            ],
            
            # 주식 시장
            'stock_market': [
                'stock market', 'stocks', 'equity', 'shares', 'nasdaq',
                'sp500', 's&p 500', 'dow jones', 'market volatility',
                'bull market', 'bear market', 'correction', 'rally'
            ],
            
            # 기업 실적
            'earnings': [
                'earnings', 'revenue', 'profit', 'quarterly results',
                'eps', 'earnings per share', 'guidance', 'outlook',
                'financial results', 'income statement'
            ],
            
            # 경제 성장
            'economic_growth': [
                'gdp', 'economic growth', 'recession', 'expansion',
                'economic recovery', 'growth rate', 'productivity',
                'economic indicators', 'business cycle'
            ],
            
            # 금융 시장
            'financial_markets': [
                'bond market', 'treasury', 'yield curve', 'credit markets',
                'corporate bonds', 'municipal bonds', 'fixed income',
                'bond yields', 'treasury rates'
            ],
            
            # 섹터별
            'technology': [
                'tech stocks', 'technology', 'artificial intelligence', 'ai',
                'semiconductors', 'chips', 'software', 'cloud computing',
                'cybersecurity', 'fintech'
            ],
            
            'energy': [
                'oil prices', 'crude oil', 'energy sector', 'renewable energy',
                'natural gas', 'petroleum', 'opec', 'energy stocks',
                'clean energy', 'solar', 'wind power'
            ],
            
            'healthcare': [
                'healthcare', 'pharmaceuticals', 'biotech', 'medical devices',
                'drug development', 'clinical trials', 'fda approval',
                'health insurance', 'medicare', 'medicaid'
            ],
            
            'financial_services': [
                'banks', 'banking', 'financial services', 'credit',
                'lending', 'mortgages', 'insurance', 'fintech',
                'payment systems', 'digital payments'
            ],
            
            # 국제 경제
            'international_trade': [
                'trade war', 'tariffs', 'exports', 'imports',
                'trade deficit', 'trade surplus', 'wto', 'nafta',
                'supply chain', 'globalization'
            ],
            
            'currency': [
                'dollar', 'euro', 'yen', 'yuan', 'currency',
                'exchange rate', 'forex', 'dollar strength',
                'currency devaluation', 'currency appreciation'
            ],
            
            # 투자 관련
            'investment': [
                'investment', 'portfolio', 'asset allocation', 'diversification',
                'risk management', 'hedge funds', 'mutual funds', 'etf',
                'index funds', 'active investing', 'passive investing'
            ],
            
            'cryptocurrency': [
                'bitcoin', 'ethereum', 'cryptocurrency', 'crypto',
                'blockchain', 'digital currency', 'defi', 'nft',
                'crypto market', 'altcoins'
            ],
            
            # 정책 관련
            'fiscal_policy': [
                'fiscal policy', 'government spending', 'budget deficit',
                'national debt', 'stimulus', 'infrastructure spending',
                'tax policy', 'tax cuts', 'tax increases'
            ],
            
            'regulation': [
                'regulation', 'regulatory', 'sec', 'compliance',
                'antitrust', 'monopoly', 'market regulation',
                'financial regulation', 'banking regulation'
            ]
        }
        
        # 개념 간 관계 가중치
        self.concept_relationships = {
            ('monetary_policy', 'inflation'): 0.9,
            ('monetary_policy', 'stock_market'): 0.8,
            ('inflation', 'employment'): 0.7,
            ('earnings', 'stock_market'): 0.9,
            ('economic_growth', 'employment'): 0.8,
            ('technology', 'stock_market'): 0.7,
            ('energy', 'inflation'): 0.6,
            ('international_trade', 'currency'): 0.8,
            ('fiscal_policy', 'economic_growth'): 0.7,
            ('regulation', 'financial_services'): 0.8
        }
        
        self.logger.info("✅ 강화된 소셜 네트워크 분석기 초기화 완료")
    
    def extract_concepts_from_text(self, text: str) -> Dict[str, float]:
        """텍스트에서 경제 개념 추출 및 가중치 계산"""
        text_lower = text.lower()
        # HTML 태그 및 특수 문자 제거
        import re
        text_clean = re.sub(r'<[^>]+>', '', text)
        text_clean = re.sub(r'[^\w\s]', ' ', text_clean)
        text_clean_lower = text_clean.lower()
        
        concept_scores = {}
        
        for concept, keywords in self.economic_concepts.items():
            score = 0
            matches = []
            
            for keyword in keywords:
                # 정확한 매칭
                if keyword in text_clean_lower:
                    # 키워드 길이에 따른 가중치 (긴 키워드일수록 높은 점수)
                    weight = len(keyword.split()) * 1.5
                    score += weight
                    matches.append(keyword)
                
                # 부분 매칭 (단어 단위)
                keyword_words = keyword.split()
                if len(keyword_words) > 1:
                    if all(word in text_clean_lower for word in keyword_words):
                        score += len(keyword_words) * 1.2
                        matches.append(keyword)
            
            if score > 0:
                # 텍스트 길이 대비 정규화
                normalized_score = score / (len(text_clean.split()) + 1) * 100
                concept_scores[concept] = {
                    'score': normalized_score,
                    'matches': matches,
                    'raw_score': score
                }
        
        return concept_scores
    
    def build_concept_network_from_reddit(self, reddit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Reddit 데이터에서 경제 개념 네트워크 구축"""
        self.logger.info("🕸️ Reddit 경제 개념 네트워크 구축 시작")
        
        # 네트워크 그래프 생성
        G = nx.Graph()
        
        # 개념별 언급 횟수 및 감정
        concept_mentions = defaultdict(int)
        concept_sentiments = defaultdict(list)
        concept_contexts = defaultdict(list)
        
        # 개념 간 동시 출현 매트릭스
        concept_cooccurrence = defaultdict(int)
        
        # Reddit 데이터 처리
        subreddits = reddit_data.get('subreddits', {})
        
        for subreddit_name, subreddit_data in subreddits.items():
            # 포스트 분석
            posts = subreddit_data.get('posts', [])
            for post in posts:
                title = post.get('title', '')
                selftext = post.get('selftext', '')
                full_text = f"{title} {selftext}"
                
                if len(full_text.strip()) < 10:  # 너무 짧은 텍스트 제외
                    continue
                
                # 개념 추출
                concepts = self.extract_concepts_from_text(full_text)
                
                # 개념별 통계 업데이트
                for concept, data in concepts.items():
                    concept_mentions[concept] += 1
                    
                    # 감정 정보
                    sentiment = post.get('sentiment', {})
                    concept_sentiments[concept].append(sentiment.get('polarity', 0))
                    
                    # 컨텍스트 저장
                    concept_contexts[concept].append({
                        'text': full_text[:200] + "..." if len(full_text) > 200 else full_text,
                        'subreddit': subreddit_name,
                        'score': post.get('score', 0),
                        'url': post.get('permalink', '')
                    })
                
                # 개념 간 동시 출현 계산
                concept_list = list(concepts.keys())
                for i, concept1 in enumerate(concept_list):
                    for concept2 in concept_list[i+1:]:
                        # 두 개념의 점수 곱으로 관계 강도 계산
                        strength = concepts[concept1]['score'] * concepts[concept2]['score']
                        concept_cooccurrence[(concept1, concept2)] += strength
            
            # 댓글 분석
            comments = subreddit_data.get('comments', [])
            for comment in comments:
                body = comment.get('body', '')
                
                if len(body.strip()) < 20:  # 너무 짧은 댓글 제외
                    continue
                
                # 개념 추출
                concepts = self.extract_concepts_from_text(body)
                
                # 개념별 통계 업데이트 (댓글은 가중치 0.5)
                for concept, data in concepts.items():
                    concept_mentions[concept] += 0.5
                    
                    sentiment = comment.get('sentiment', {})
                    concept_sentiments[concept].append(sentiment.get('polarity', 0))
                    
                    concept_contexts[concept].append({
                        'text': body[:150] + "..." if len(body) > 150 else body,
                        'subreddit': subreddit_name,
                        'score': comment.get('score', 0),
                        'url': comment.get('permalink', ''),
                        'type': 'comment'
                    })
                
                # 댓글의 개념 간 동시 출현 (가중치 0.5)
                concept_list = list(concepts.keys())
                for i, concept1 in enumerate(concept_list):
                    for concept2 in concept_list[i+1:]:
                        strength = concepts[concept1]['score'] * concepts[concept2]['score'] * 0.5
                        concept_cooccurrence[(concept1, concept2)] += strength
        
        # 네트워크 그래프 구성
        # 노드 추가 (언급 횟수가 2 이상인 개념만)
        for concept, mentions in concept_mentions.items():
            if mentions >= 2:  # 최소 2회 이상 언급된 개념만
                avg_sentiment = np.mean(concept_sentiments[concept]) if concept_sentiments[concept] else 0
                
                G.add_node(concept, 
                          mentions=mentions,
                          avg_sentiment=avg_sentiment,
                          sentiment_std=np.std(concept_sentiments[concept]) if len(concept_sentiments[concept]) > 1 else 0,
                          contexts=concept_contexts[concept][:5])  # 상위 5개 컨텍스트만 저장
        
        # 엣지 추가
        for (concept1, concept2), strength in concept_cooccurrence.items():
            if concept1 in G.nodes() and concept2 in G.nodes() and strength > 1:
                # 기본 동시 출현 가중치
                weight = strength
                
                # 사전 정의된 관계 가중치 추가
                predefined_weight = self.concept_relationships.get((concept1, concept2)) or \
                                  self.concept_relationships.get((concept2, concept1))
                
                if predefined_weight:
                    weight *= (1 + predefined_weight)
                
                G.add_edge(concept1, concept2, 
                          weight=weight,
                          cooccurrence_count=strength,
                          relationship_type='conceptual')
        
        # 네트워크 분석 메트릭 계산
        network_metrics = self._calculate_enhanced_network_metrics(G)
        
        # 커뮤니티 탐지
        communities = self._detect_concept_communities(G)
        
        # 중요한 개념 식별
        important_concepts = self._identify_important_concepts(G, concept_mentions)
        
        return {
            'graph': G,
            'network_metrics': network_metrics,
            'communities': communities,
            'important_concepts': important_concepts,
            'concept_mentions': dict(concept_mentions),
            'concept_sentiments': {k: np.mean(v) for k, v in concept_sentiments.items()},
            'total_concepts': len(G.nodes()),
            'total_relationships': len(G.edges()),
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _calculate_enhanced_network_metrics(self, G: nx.Graph) -> Dict[str, Any]:
        """강화된 네트워크 메트릭 계산"""
        if len(G.nodes()) == 0:
            return {}
        
        metrics = {
            'nodes_count': len(G.nodes()),
            'edges_count': len(G.edges()),
            'density': nx.density(G),
            'average_clustering': nx.average_clustering(G),
        }
        
        if len(G.nodes()) > 0:
            # 중심성 측정
            degree_centrality = nx.degree_centrality(G)
            betweenness_centrality = nx.betweenness_centrality(G)
            closeness_centrality = nx.closeness_centrality(G)
            eigenvector_centrality = nx.eigenvector_centrality(G, max_iter=1000)
            
            metrics.update({
                'top_degree_centrality': sorted(degree_centrality.items(), 
                                               key=lambda x: x[1], reverse=True)[:10],
                'top_betweenness_centrality': sorted(betweenness_centrality.items(), 
                                                   key=lambda x: x[1], reverse=True)[:10],
                'top_closeness_centrality': sorted(closeness_centrality.items(), 
                                                 key=lambda x: x[1], reverse=True)[:10],
                'top_eigenvector_centrality': sorted(eigenvector_centrality.items(), 
                                                   key=lambda x: x[1], reverse=True)[:10]
            })
        
        # 연결성 분석
        if nx.is_connected(G):
            metrics['diameter'] = nx.diameter(G)
            metrics['average_path_length'] = nx.average_shortest_path_length(G)
        else:
            metrics['connected_components'] = nx.number_connected_components(G)
            largest_cc = max(nx.connected_components(G), key=len)
            metrics['largest_component_size'] = len(largest_cc)
        
        return metrics
    
    def _detect_concept_communities(self, G: nx.Graph) -> List[List[str]]:
        """개념 커뮤니티 탐지"""
        try:
            import community as community_louvain
            partition = community_louvain.best_partition(G)
            
            communities = defaultdict(list)
            for concept, community_id in partition.items():
                communities[community_id].append(concept)
            
            # 커뮤니티 크기 순으로 정렬
            sorted_communities = sorted(communities.values(), key=len, reverse=True)
            return sorted_communities
        
        except ImportError:
            # community 패키지가 없으면 연결 컴포넌트 사용
            return [list(component) for component in nx.connected_components(G)]
    
    def _identify_important_concepts(self, G: nx.Graph, concept_mentions: Dict) -> Dict[str, List[Tuple[str, float]]]:
        """중요한 개념 식별"""
        if len(G.nodes()) == 0:
            return {}
        
        # 다양한 중요도 측정
        degree_centrality = nx.degree_centrality(G)
        betweenness_centrality = nx.betweenness_centrality(G)
        
        # 언급 횟수 기반 중요도
        mention_importance = {node: concept_mentions.get(node, 0) for node in G.nodes()}
        
        # 감정 영향력 (절댓값이 클수록 중요)
        sentiment_importance = {}
        for node in G.nodes():
            sentiment = abs(G.nodes[node].get('avg_sentiment', 0))
            sentiment_importance[node] = sentiment
        
        # 종합 중요도 (여러 지표의 가중 평균)
        combined_importance = {}
        for node in G.nodes():
            score = (
                degree_centrality.get(node, 0) * 0.3 +
                betweenness_centrality.get(node, 0) * 0.2 +
                (mention_importance.get(node, 0) / max(mention_importance.values(), default=1)) * 0.3 +
                sentiment_importance.get(node, 0) * 0.2
            )
            combined_importance[node] = score
        
        return {
            'by_degree': sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:15],
            'by_betweenness': sorted(betweenness_centrality.items(), key=lambda x: x[1], reverse=True)[:15],
            'by_mentions': sorted(mention_importance.items(), key=lambda x: x[1], reverse=True)[:15],
            'by_sentiment_impact': sorted(sentiment_importance.items(), key=lambda x: x[1], reverse=True)[:15],
            'by_combined_score': sorted(combined_importance.items(), key=lambda x: x[1], reverse=True)[:15]
        }

def main():
    """테스트 실행"""
    print("🕸️ 강화된 소셜 네트워크 분석기 테스트")
    print("=" * 50)
    
    analyzer = EnhancedSocialNetworkAnalyzer()
    
    # 샘플 Reddit 데이터로 테스트
    sample_reddit_data = {
        'subreddits': {
            'investing': {
                'posts': [
                    {
                        'title': 'Fed rate hike impact on tech stocks and inflation concerns',
                        'selftext': 'The Federal Reserve decision to raise interest rates will significantly impact technology stocks. Inflation remains a key concern for investors.',
                        'sentiment': {'polarity': -0.2},
                        'score': 150,
                        'permalink': 'https://reddit.com/example1'
                    }
                ],
                'comments': [
                    {
                        'body': 'I think the stock market will see more volatility due to monetary policy changes. Earnings season will be crucial.',
                        'sentiment': {'polarity': -0.1},
                        'score': 25,
                        'permalink': 'https://reddit.com/example1/comment1'
                    }
                ]
            }
        }
    }
    
    # 개념 네트워크 구축
    concept_network = analyzer.build_concept_network_from_reddit(sample_reddit_data)
    
    print(f"📊 분석 결과:")
    print(f"  개념 수: {concept_network['total_concepts']}개")
    print(f"  관계 수: {concept_network['total_relationships']}개")
    
    # 중요한 개념
    important_concepts = concept_network['important_concepts']
    combined_scores = important_concepts.get('by_combined_score', [])
    
    if combined_scores:
        print(f"\n🎯 중요한 경제 개념 (종합 점수):")
        for i, (concept, score) in enumerate(combined_scores[:5], 1):
            print(f"   {i}. {concept.replace('_', ' ').title()}: {score:.3f}")
    
    print(f"\n✅ 강화된 네트워크 분석 테스트 완료!")

if __name__ == "__main__":
    main()
