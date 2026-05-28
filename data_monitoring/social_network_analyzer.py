#!/usr/bin/env python3
"""
소셜 네트워크 분석 모듈
뉴스 및 SNS 데이터를 활용한 네트워크 분석
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

class SocialNetworkAnalyzer:
    """소셜 네트워크 분석기"""
    
    def __init__(self):
        """초기화"""
        self.logger = logging.getLogger(__name__)
        
        # 경제 관련 엔티티 (기업, 인물, 기관 등) - 더 포괄적으로 확장
        self.economic_entities = {
            # 주요 기업 (더 많은 기업 추가)
            'companies': [
                'Apple', 'Microsoft', 'Google', 'Alphabet', 'Amazon', 'Tesla', 'Meta', 'Netflix',
                'Samsung', 'TSMC', 'ASML', 'Nvidia', 'Intel', 'AMD', 'Qualcomm',
                'JPMorgan', 'Goldman Sachs', 'Morgan Stanley', 'Bank of America', 'Wells Fargo',
                'Berkshire Hathaway', 'Visa', 'Mastercard', 'PayPal', 'Square',
                'Coca-Cola', 'PepsiCo', 'Johnson & Johnson', 'Pfizer', 'Moderna',
                'Walmart', 'Target', 'Home Depot', 'McDonald\'s', 'Starbucks',
                'Boeing', 'Airbus', 'General Electric', 'Ford', 'GM', 'Toyota',
                'ExxonMobil', 'Chevron', 'Shell', 'BP'
            ],
            
            # 주요 인물 (더 많은 인물 추가)
            'people': [
                'Jerome Powell', 'Janet Yellen', 'Christine Lagarde', 'Jay Powell',
                'Elon Musk', 'Warren Buffett', 'Jeff Bezos', 'Bill Gates', 'Tim Cook', 
                'Satya Nadella', 'Mark Zuckerberg', 'Larry Page', 'Sergey Brin',
                'Jamie Dimon', 'Larry Fink', 'Ray Dalio', 'Cathie Wood',
                'Charlie Munger', 'Michael Burry', 'Carl Icahn'
            ],
            
            # 기관 및 정부 (더 포괄적)
            'institutions': [
                'Federal Reserve', 'Fed', 'Treasury', 'SEC', 'FDIC', 'CFTC',
                'ECB', 'European Central Bank', 'Bank of Japan', 'BOJ',
                'People\'s Bank of China', 'PBOC', 'Bank of England', 'BOE',
                'IMF', 'World Bank', 'OECD', 'G7', 'G20', 'WTO',
                'Congress', 'Senate', 'House', 'White House', 'Biden Administration',
                'Supreme Court', 'Justice Department'
            ],
            
            # 경제 개념 (더 상세하게)
            'concepts': [
                'inflation', 'deflation', 'recession', 'depression', 'recovery',
                'GDP', 'unemployment', 'interest rates', 'interest rate', 'rates',
                'quantitative easing', 'QE', 'monetary policy', 'fiscal policy',
                'cryptocurrency', 'crypto', 'Bitcoin', 'Ethereum', 'blockchain',
                'ESG', 'climate change', 'supply chain', 'trade war', 'tariffs',
                'stock market', 'bond market', 'commodities', 'oil prices',
                'dollar', 'euro', 'yen', 'yuan', 'currency', 'forex',
                'earnings', 'revenue', 'profit', 'loss', 'merger', 'acquisition',
                'IPO', 'dividend', 'buyback', 'split', 'volatility'
            ]
        }
        
        # 관계 키워드
        self.relationship_keywords = {
            'partnership': ['partnership', 'collaboration', 'joint venture', 'alliance'],
            'competition': ['compete', 'rival', 'challenge', 'threat'],
            'investment': ['invest', 'funding', 'acquisition', 'merger', 'buyout'],
            'regulation': ['regulate', 'policy', 'rule', 'compliance', 'oversight'],
            'influence': ['impact', 'affect', 'influence', 'drive', 'cause'],
            'criticism': ['criticize', 'oppose', 'against', 'dispute', 'conflict']
        }
        
        self.logger.info("✅ 소셜 네트워크 분석기 초기화 완료")
    
    def extract_entities_from_text(self, text: str) -> Dict[str, List[str]]:
        """텍스트에서 경제 관련 엔티티 추출 (개선된 버전)"""
        # 텍스트 전처리
        text_lower = text.lower()
        # HTML 태그 제거
        import re
        text_clean = re.sub(r'<[^>]+>', '', text)
        text_clean_lower = text_clean.lower()
        
        found_entities = {
            'companies': [],
            'people': [],
            'institutions': [],
            'concepts': []
        }
        
        for category, entities in self.economic_entities.items():
            for entity in entities:
                entity_lower = entity.lower()
                
                # 정확한 매칭과 부분 매칭 모두 고려
                if (entity_lower in text_clean_lower or 
                    any(word in text_clean_lower for word in entity_lower.split() if len(word) > 2)):
                    
                    # 중복 제거
                    if entity not in found_entities[category]:
                        found_entities[category].append(entity)
        
        # 추가적인 패턴 매칭 (약어, 변형 등)
        additional_patterns = {
            'institutions': {
                'federal reserve': ['fed', 'federal reserve', 'central bank'],
                'sec': ['securities and exchange commission', 'sec'],
                'treasury': ['treasury department', 'treasury', 'us treasury'],
                'ecb': ['european central bank', 'ecb']
            },
            'concepts': {
                'interest rates': ['interest rate', 'rates', 'fed rate', 'federal funds rate'],
                'inflation': ['inflation', 'cpi', 'consumer price index', 'price increases'],
                'recession': ['recession', 'economic downturn', 'contraction'],
                'stock market': ['stock market', 'equity market', 'stocks', 'shares']
            }
        }
        
        for category, pattern_dict in additional_patterns.items():
            for main_entity, patterns in pattern_dict.items():
                for pattern in patterns:
                    if pattern in text_clean_lower:
                        # 메인 엔티티 이름으로 정규화
                        if main_entity not in [e.lower() for e in found_entities[category]]:
                            found_entities[category].append(main_entity.title())
        
        return found_entities
    
    def extract_relationships_from_text(self, text: str, entities: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """텍스트에서 엔티티 간 관계 추출"""
        relationships = []
        text_lower = text.lower()
        
        # 모든 엔티티를 하나의 리스트로 통합
        all_entities = []
        for category, entity_list in entities.items():
            for entity in entity_list:
                all_entities.append({'name': entity, 'category': category})
        
        # 엔티티 쌍에 대해 관계 검색
        for i, entity1 in enumerate(all_entities):
            for j, entity2 in enumerate(all_entities[i+1:], i+1):
                # 두 엔티티가 같은 문장에 나타나는지 확인
                sentences = text.split('.')
                
                for sentence in sentences:
                    sentence_lower = sentence.lower()
                    
                    if (entity1['name'].lower() in sentence_lower and 
                        entity2['name'].lower() in sentence_lower):
                        
                        # 관계 유형 결정
                        relationship_type = self._determine_relationship_type(sentence_lower)
                        
                        relationships.append({
                            'source': entity1['name'],
                            'target': entity2['name'],
                            'source_category': entity1['category'],
                            'target_category': entity2['category'],
                            'relationship_type': relationship_type,
                            'context': sentence.strip(),
                            'weight': 1
                        })
        
        return relationships
    
    def _determine_relationship_type(self, text: str) -> str:
        """텍스트에서 관계 유형 결정"""
        for rel_type, keywords in self.relationship_keywords.items():
            if any(keyword in text for keyword in keywords):
                return rel_type
        return 'mentioned_together'
    
    def analyze_news_network(self, news_data: Dict[str, Any]) -> Dict[str, Any]:
        """뉴스 데이터에서 네트워크 분석"""
        self.logger.info("📰 뉴스 네트워크 분석 시작")
        
        # 네트워크 그래프 생성
        G = nx.Graph()
        
        # 뉴스 카테고리별 데이터 처리
        categories = news_data.get('categories', {})
        all_relationships = []
        entity_mentions = defaultdict(int)
        entity_sentiments = defaultdict(list)
        
        for category, articles in categories.items():
            for article in articles:
                title = article.get('title', '')
                summary = article.get('summary', '')
                sentiment = article.get('sentiment', {})
                
                # 전체 텍스트
                full_text = f"{title} {summary}"
                
                # 엔티티 추출
                entities = self.extract_entities_from_text(full_text)
                
                # 엔티티 언급 횟수 및 감정 기록
                for category_entities in entities.values():
                    for entity in category_entities:
                        entity_mentions[entity] += 1
                        entity_sentiments[entity].append(sentiment.get('polarity', 0))
                
                # 관계 추출
                relationships = self.extract_relationships_from_text(full_text, entities)
                all_relationships.extend(relationships)
        
        # 네트워크 그래프 구성
        for rel in all_relationships:
            source = rel['source']
            target = rel['target']
            
            if G.has_edge(source, target):
                G[source][target]['weight'] += rel['weight']
                G[source][target]['contexts'].append(rel['context'])
            else:
                G.add_edge(source, target, 
                          weight=rel['weight'],
                          relationship_type=rel['relationship_type'],
                          contexts=[rel['context']])
        
        # 노드 속성 추가
        for node in G.nodes():
            G.nodes[node]['mentions'] = entity_mentions.get(node, 0)
            sentiments = entity_sentiments.get(node, [0])
            G.nodes[node]['avg_sentiment'] = np.mean(sentiments)
            G.nodes[node]['sentiment_std'] = np.std(sentiments)
        
        # 네트워크 분석 메트릭 계산
        network_metrics = self._calculate_network_metrics(G)
        
        # 커뮤니티 탐지
        communities = self._detect_communities(G)
        
        # 중요한 노드 식별
        important_nodes = self._identify_important_nodes(G)
        
        return {
            'graph': G,
            'network_metrics': network_metrics,
            'communities': communities,
            'important_nodes': important_nodes,
            'total_entities': len(G.nodes()),
            'total_relationships': len(G.edges()),
            'entity_mentions': dict(entity_mentions),
            'entity_sentiments': {k: np.mean(v) for k, v in entity_sentiments.items()},
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def analyze_reddit_network(self, reddit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Reddit 데이터에서 네트워크 분석"""
        self.logger.info("📱 Reddit 네트워크 분석 시작")
        
        # 사용자 간 상호작용 네트워크
        user_network = nx.Graph()
        
        # 주제 간 연관성 네트워크
        topic_network = nx.Graph()
        
        # Reddit 데이터 구조에 따라 분석
        # (실제 Reddit 데이터가 있다면 해당 구조에 맞게 수정)
        
        # 시뮬레이션 데이터로 예시 네트워크 생성
        sample_users = ['user1', 'user2', 'user3', 'user4', 'user5']
        sample_topics = ['inflation', 'fed_policy', 'stock_market', 'crypto', 'recession']
        
        # 사용자 간 상호작용 (댓글, 답글 등)
        for i, user1 in enumerate(sample_users):
            for user2 in sample_users[i+1:]:
                if np.random.random() > 0.6:  # 40% 확률로 상호작용
                    interaction_strength = np.random.randint(1, 10)
                    user_network.add_edge(user1, user2, weight=interaction_strength)
        
        # 주제 간 연관성
        for i, topic1 in enumerate(sample_topics):
            for topic2 in sample_topics[i+1:]:
                if np.random.random() > 0.5:  # 50% 확률로 연관성
                    correlation = np.random.random()
                    topic_network.add_edge(topic1, topic2, weight=correlation)
        
        # 네트워크 메트릭 계산
        user_metrics = self._calculate_network_metrics(user_network)
        topic_metrics = self._calculate_network_metrics(topic_network)
        
        return {
            'user_network': user_network,
            'topic_network': topic_network,
            'user_metrics': user_metrics,
            'topic_metrics': topic_metrics,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _calculate_network_metrics(self, G: nx.Graph) -> Dict[str, Any]:
        """네트워크 메트릭 계산"""
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
            
            metrics.update({
                'top_degree_centrality': sorted(degree_centrality.items(), 
                                               key=lambda x: x[1], reverse=True)[:5],
                'top_betweenness_centrality': sorted(betweenness_centrality.items(), 
                                                   key=lambda x: x[1], reverse=True)[:5],
                'top_closeness_centrality': sorted(closeness_centrality.items(), 
                                                 key=lambda x: x[1], reverse=True)[:5]
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
    
    def _detect_communities(self, G: nx.Graph) -> List[List[str]]:
        """커뮤니티 탐지"""
        try:
            # Louvain 알고리즘 사용 (community 패키지 필요)
            import community as community_louvain
            partition = community_louvain.best_partition(G)
            
            # 커뮤니티별로 노드 그룹화
            communities = defaultdict(list)
            for node, community_id in partition.items():
                communities[community_id].append(node)
            
            return list(communities.values())
        
        except ImportError:
            # community 패키지가 없으면 간단한 연결 컴포넌트 사용
            return [list(component) for component in nx.connected_components(G)]
    
    def _identify_important_nodes(self, G: nx.Graph) -> Dict[str, List[Tuple[str, float]]]:
        """중요한 노드 식별"""
        if len(G.nodes()) == 0:
            return {}
        
        # 다양한 중심성 측정
        degree_centrality = nx.degree_centrality(G)
        betweenness_centrality = nx.betweenness_centrality(G)
        
        # 언급 횟수 기반 중요도
        mention_importance = {}
        for node in G.nodes():
            mentions = G.nodes[node].get('mentions', 0)
            mention_importance[node] = mentions
        
        # 감정 기반 중요도 (절댓값이 클수록 중요)
        sentiment_importance = {}
        for node in G.nodes():
            sentiment = abs(G.nodes[node].get('avg_sentiment', 0))
            sentiment_importance[node] = sentiment
        
        return {
            'by_degree': sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:10],
            'by_betweenness': sorted(betweenness_centrality.items(), key=lambda x: x[1], reverse=True)[:10],
            'by_mentions': sorted(mention_importance.items(), key=lambda x: x[1], reverse=True)[:10],
            'by_sentiment_impact': sorted(sentiment_importance.items(), key=lambda x: x[1], reverse=True)[:10]
        }
    
    def generate_network_insights(self, news_network: Dict[str, Any], 
                                reddit_network: Dict[str, Any] = None) -> Dict[str, Any]:
        """네트워크 분석 인사이트 생성"""
        insights = {
            'timestamp': datetime.now().isoformat(),
            'news_insights': {},
            'reddit_insights': {},
            'combined_insights': {}
        }
        
        # 뉴스 네트워크 인사이트
        if news_network:
            G = news_network['graph']
            metrics = news_network['network_metrics']
            important_nodes = news_network['important_nodes']
            
            insights['news_insights'] = {
                'network_size': f"{metrics.get('nodes_count', 0)}개 엔티티, {metrics.get('edges_count', 0)}개 관계",
                'network_density': f"{metrics.get('density', 0):.3f} (0-1 범위)",
                'clustering': f"{metrics.get('average_clustering', 0):.3f}",
                'most_central_entities': [node for node, _ in important_nodes.get('by_degree', [])[:3]],
                'most_mentioned_entities': [node for node, _ in important_nodes.get('by_mentions', [])[:3]],
                'sentiment_leaders': [node for node, _ in important_nodes.get('by_sentiment_impact', [])[:3]],
                'communities_count': len(news_network.get('communities', [])),
                'key_relationships': self._extract_key_relationships(G)
            }
        
        # Reddit 네트워크 인사이트 (구현된 경우)
        if reddit_network:
            insights['reddit_insights'] = {
                'user_network_size': reddit_network['user_metrics'].get('nodes_count', 0),
                'topic_network_size': reddit_network['topic_metrics'].get('nodes_count', 0),
                'user_interactions': reddit_network['user_metrics'].get('edges_count', 0),
                'topic_correlations': reddit_network['topic_metrics'].get('edges_count', 0)
            }
        
        # 통합 인사이트
        insights['combined_insights'] = {
            'analysis_summary': f"뉴스 네트워크에서 {news_network.get('total_entities', 0)}개 엔티티 분석",
            'key_findings': self._generate_key_findings(news_network),
            'recommendations': self._generate_recommendations(news_network)
        }
        
        return insights
    
    def _extract_key_relationships(self, G: nx.Graph) -> List[Dict[str, Any]]:
        """주요 관계 추출"""
        key_relationships = []
        
        # 가중치가 높은 관계들
        edges_by_weight = sorted(G.edges(data=True), 
                               key=lambda x: x[2].get('weight', 0), reverse=True)
        
        for source, target, data in edges_by_weight[:5]:
            key_relationships.append({
                'source': source,
                'target': target,
                'strength': data.get('weight', 0),
                'type': data.get('relationship_type', 'unknown'),
                'context_sample': data.get('contexts', [''])[0][:100] + "..."
            })
        
        return key_relationships
    
    def _generate_key_findings(self, news_network: Dict[str, Any]) -> List[str]:
        """주요 발견사항 생성"""
        findings = []
        
        important_nodes = news_network.get('important_nodes', {})
        metrics = news_network.get('network_metrics', {})
        
        # 가장 중심적인 엔티티
        if important_nodes.get('by_degree'):
            top_entity = important_nodes['by_degree'][0][0]
            findings.append(f"'{top_entity}'가 뉴스 네트워크에서 가장 중심적인 역할을 함")
        
        # 네트워크 밀도
        density = metrics.get('density', 0)
        if density > 0.3:
            findings.append("높은 네트워크 밀도로 엔티티 간 강한 연결성을 보임")
        elif density < 0.1:
            findings.append("낮은 네트워크 밀도로 엔티티 간 연결이 제한적임")
        
        # 커뮤니티 수
        communities_count = len(news_network.get('communities', []))
        if communities_count > 1:
            findings.append(f"{communities_count}개의 주요 엔티티 그룹이 식별됨")
        
        return findings
    
    def _generate_recommendations(self, news_network: Dict[str, Any]) -> List[str]:
        """추천사항 생성"""
        recommendations = []
        
        important_nodes = news_network.get('important_nodes', {})
        
        # 모니터링 추천
        if important_nodes.get('by_mentions'):
            top_mentioned = important_nodes['by_mentions'][:3]
            entities = [node for node, _ in top_mentioned]
            recommendations.append(f"다음 엔티티들을 중점 모니터링: {', '.join(entities)}")
        
        # 감정 분석 추천
        if important_nodes.get('by_sentiment_impact'):
            sentiment_leaders = important_nodes['by_sentiment_impact'][:2]
            entities = [node for node, _ in sentiment_leaders]
            recommendations.append(f"감정 변화 주의 깊게 관찰: {', '.join(entities)}")
        
        # 네트워크 확장 추천
        recommendations.append("관계 네트워크 확장을 위해 더 많은 뉴스 소스 추가 고려")
        
        return recommendations

def main():
    """테스트 실행"""
    print("🕸️ 소셜 네트워크 분석기 테스트")
    print("=" * 50)
    
    analyzer = SocialNetworkAnalyzer()
    
    # 샘플 뉴스 데이터로 테스트
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
    
    # 뉴스 네트워크 분석
    news_network = analyzer.analyze_news_network(sample_news_data)
    
    print(f"📊 분석 결과:")
    print(f"  엔티티 수: {news_network['total_entities']}개")
    print(f"  관계 수: {news_network['total_relationships']}개")
    
    # 인사이트 생성
    insights = analyzer.generate_network_insights(news_network)
    
    print(f"\n🔍 주요 인사이트:")
    for finding in insights['combined_insights']['key_findings']:
        print(f"  • {finding}")
    
    print(f"\n💡 추천사항:")
    for recommendation in insights['combined_insights']['recommendations']:
        print(f"  • {recommendation}")

if __name__ == "__main__":
    main()
