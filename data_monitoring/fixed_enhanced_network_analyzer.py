#!/usr/bin/env python3
"""
수정된 개선된 경제 개념 기반 소셜 네트워크 분석 모듈
실제 Reddit 데이터와 연동하여 에러 없이 작동
"""

import networkx as nx
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter, defaultdict
import re
import json
import sys
import os

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class FixedEnhancedNetworkAnalyzer:
    """수정된 개선된 경제 네트워크 분석기"""
    
    def __init__(self):
        """초기화"""
        self.logger = logging.getLogger(__name__)
        
        # 16개 주요 경제 카테고리와 세부 개념들 (간소화)
        self.economic_concepts = {
            # 1. 통화정책
            'monetary_policy': {
                'main_concepts': ['통화정책', '금리정책', '기준금리', 'Fed', 'Federal Reserve'],
                'related_terms': ['금리인상', '금리인하', '양적완화', 'QE', '긴축정책', '완화정책', 'FOMC'],
                'weight': 1.0
            },
            
            # 2. 인플레이션
            'inflation': {
                'main_concepts': ['인플레이션', 'inflation', '물가상승', 'CPI'],
                'related_terms': ['소비자물가지수', '근원인플레이션', '디플레이션', '물가안정', '물가압력'],
                'weight': 1.0
            },
            
            # 3. 주식시장
            'stock_market': {
                'main_concepts': ['주식시장', 'stock market', '증시', 'stocks'],
                'related_terms': ['S&P 500', 'NASDAQ', 'Dow Jones', '상승장', '하락장', '변동성', 'VIX'],
                'weight': 1.0
            },
            
            # 4. 기업실적
            'corporate_performance': {
                'main_concepts': ['기업실적', '실적발표', 'earnings', 'revenue'],
                'related_terms': ['매출', '순이익', '영업이익', 'EPS', '가이던스', '분기실적'],
                'weight': 0.9
            },
            
            # 5. 기술주
            'technology': {
                'main_concepts': ['기술주', 'tech stocks', '테크주', 'technology'],
                'related_terms': ['Apple', 'Microsoft', 'Google', 'Amazon', 'Tesla', '반도체', 'AI'],
                'weight': 0.9
            },
            
            # 6. 금융섹터
            'financial_sector': {
                'main_concepts': ['금융섹터', 'financial sector', '은행주', 'banking'],
                'related_terms': ['JPMorgan', 'Goldman Sachs', '순이자마진', '대출', '신용위험'],
                'weight': 0.8
            },
            
            # 7. 에너지
            'energy': {
                'main_concepts': ['에너지', 'energy', '원유', 'oil'],
                'related_terms': ['WTI', 'Brent', 'OPEC', '천연가스', '신재생에너지', '태양광'],
                'weight': 0.8
            },
            
            # 8. 부동산
            'real_estate': {
                'main_concepts': ['부동산', 'real estate', '주택시장', 'housing'],
                'related_terms': ['주택가격', '모기지', 'REIT', '상업용부동산', '주택담보대출'],
                'weight': 0.8
            },
            
            # 9. 국제무역
            'international_trade': {
                'main_concepts': ['국제무역', 'trade', '무역전쟁', 'tariff'],
                'related_terms': ['관세', '수출', '수입', '무역수지', '공급망', '글로벌화'],
                'weight': 0.8
            },
            
            # 10. 암호화폐
            'cryptocurrency': {
                'main_concepts': ['암호화폐', 'cryptocurrency', '비트코인', 'bitcoin'],
                'related_terms': ['Ethereum', '블록체인', 'DeFi', 'NFT', '디지털자산', 'crypto'],
                'weight': 0.7
            },
            
            # 11. ESG
            'esg': {
                'main_concepts': ['ESG', '지속가능성', 'sustainability', '친환경'],
                'related_terms': ['탄소중립', '기후변화', '그린에너지', '사회적책임', '지배구조'],
                'weight': 0.7
            },
            
            # 12. 고용시장
            'labor_market': {
                'main_concepts': ['고용시장', 'labor market', '실업률', 'unemployment'],
                'related_terms': ['비농업고용', '구인', '임금상승', '노동참여율', '일자리창출'],
                'weight': 0.8
            },
            
            # 13. 소비
            'consumer_spending': {
                'main_concepts': ['소비', 'consumer spending', '소매판매', 'retail'],
                'related_terms': ['소비자신뢰', '개인소비', '소비심리', '가계소득', '저축률'],
                'weight': 0.8
            },
            
            # 14. 정부정책
            'government_policy': {
                'main_concepts': ['정부정책', 'government policy', '재정정책', 'fiscal'],
                'related_terms': ['정부지출', '세금', '부채', '적자', '예산', '부양책', '규제'],
                'weight': 0.8
            },
            
            # 15. 지정학적 리스크
            'geopolitical_risk': {
                'main_concepts': ['지정학적리스크', 'geopolitical', '국제정치', 'war'],
                'related_terms': ['전쟁', '분쟁', '제재', '외교', '안보', '정치불안', '선거'],
                'weight': 0.7
            },
            
            # 16. 시장심리
            'market_sentiment': {
                'main_concepts': ['시장심리', 'market sentiment', '투자심리', 'sentiment'],
                'related_terms': ['공포', '탐욕', '낙관', '비관', '위험회피', '투자자신뢰'],
                'weight': 0.7
            }
        }
        
        # 관계 유형별 가중치
        self.relationship_weights = {
            'strong_correlation': 1.0,
            'moderate_correlation': 0.7,
            'weak_correlation': 0.4,
            'causal_relationship': 0.9,
            'inverse_relationship': 0.8,
            'temporal_relationship': 0.6,
            'mentioned_together': 0.3
        }
        
        self.logger.info("✅ 수정된 개선된 경제 네트워크 분석기 초기화 완료")
    
    def extract_economic_concepts(self, text: str) -> Tuple[Dict[str, Any], Dict[str, float]]:
        """텍스트에서 경제 개념 추출 (에러 수정 버전)"""
        
        if not text or not isinstance(text, str):
            return {}, {}
        
        text_lower = text.lower()
        # HTML 태그 및 특수문자 제거
        text_clean = re.sub(r'<[^>]+>', '', text)
        text_clean = re.sub(r'[^\w\s가-힣]', ' ', text_clean)
        text_clean_lower = text_clean.lower()
        
        found_concepts = {}
        concept_scores = {}
        
        for category, concept_data in self.economic_concepts.items():
            category_score = 0
            found_terms = []
            
            try:
                # 주요 개념 검색 (높은 가중치)
                for main_concept in concept_data['main_concepts']:
                    if main_concept.lower() in text_clean_lower:
                        category_score += 2.0 * concept_data['weight']
                        found_terms.append(main_concept)
                
                # 관련 용어 검색 (낮은 가중치)
                for related_term in concept_data['related_terms']:
                    if related_term.lower() in text_clean_lower:
                        category_score += 1.0 * concept_data['weight']
                        found_terms.append(related_term)
                
                if category_score > 0:
                    found_concepts[category] = {
                        'score': category_score,
                        'terms': list(set(found_terms)),
                        'weight': concept_data['weight']
                    }
                    concept_scores[category] = category_score
                    
            except Exception as e:
                self.logger.warning(f"개념 추출 오류 ({category}): {e}")
                continue
        
        return found_concepts, concept_scores
    
    def analyze_concept_relationships(self, texts: List[str]) -> Dict[str, Any]:
        """여러 텍스트에서 경제 개념 간 관계 분석 (에러 수정 버전)"""
        
        if not texts or not isinstance(texts, list):
            return {'error': 'Invalid input texts'}
        
        self.logger.info("🔍 경제 개념 관계 분석 시작")
        
        # 모든 텍스트에서 개념 추출
        all_concepts = {}
        concept_cooccurrence = defaultdict(lambda: defaultdict(int))
        concept_sentiments = defaultdict(list)
        
        valid_texts = [text for text in texts if text and isinstance(text, str) and len(text.strip()) > 10]
        
        if not valid_texts:
            return {'error': 'No valid texts found'}
        
        for text in valid_texts:
            try:
                concepts, scores = self.extract_economic_concepts(text)
                
                # 간단한 감정 분석
                sentiment = self._simple_sentiment_analysis(text)
                
                # 개념별 점수 누적
                for concept, data in concepts.items():
                    if concept not in all_concepts:
                        all_concepts[concept] = {
                            'total_score': 0,
                            'mention_count': 0,
                            'terms': set(),
                            'weight': data['weight']
                        }
                    
                    all_concepts[concept]['total_score'] += data['score']
                    all_concepts[concept]['mention_count'] += 1
                    all_concepts[concept]['terms'].update(data['terms'])
                    concept_sentiments[concept].append(sentiment)
                
                # 동시 출현 관계 계산
                concept_list = list(concepts.keys())
                for i, concept1 in enumerate(concept_list):
                    for concept2 in concept_list[i+1:]:
                        # 상호 가중치 적용
                        weight = (concepts[concept1]['score'] * concepts[concept2]['score']) ** 0.5
                        concept_cooccurrence[concept1][concept2] += weight
                        concept_cooccurrence[concept2][concept1] += weight
                        
            except Exception as e:
                self.logger.warning(f"텍스트 처리 오류: {e}")
                continue
        
        if not all_concepts:
            return {'error': 'No economic concepts found'}
        
        # 네트워크 그래프 생성
        G = nx.Graph()
        
        # 노드 추가 (개념들)
        for concept, data in all_concepts.items():
            try:
                avg_sentiment = np.mean(concept_sentiments[concept]) if concept_sentiments[concept] else 0
                
                G.add_node(concept, 
                          score=data['total_score'],
                          mentions=data['mention_count'],
                          terms=list(data['terms']),
                          weight=data['weight'],
                          sentiment=float(avg_sentiment),
                          size=min(data['total_score'] * 10, 100))
                          
            except Exception as e:
                self.logger.warning(f"노드 추가 오류 ({concept}): {e}")
                continue
        
        # 엣지 추가 (관계들)
        edges_added = 0
        for concept1, connections in concept_cooccurrence.items():
            for concept2, weight in connections.items():
                if weight > 0.5 and concept1 in G.nodes() and concept2 in G.nodes():
                    try:
                        # 관계 유형 결정
                        relationship_type = self._determine_relationship_type_safe(concept1, concept2, weight)
                        
                        # 정규화된 가중치
                        normalized_weight = min(weight / 10.0, 1.0)
                        
                        G.add_edge(concept1, concept2,
                                  weight=float(normalized_weight),
                                  relationship_type=relationship_type,
                                  strength=float(weight))
                        edges_added += 1
                        
                    except Exception as e:
                        self.logger.warning(f"엣지 추가 오류 ({concept1}-{concept2}): {e}")
                        continue
        
        # 네트워크 메트릭 계산
        metrics = self._calculate_network_metrics_safe(G)
        
        self.logger.info(f"✅ 네트워크 분석 완료: {len(G.nodes())}개 노드, {len(G.edges())}개 엣지")
        
        return {
            'graph': G,
            'concepts': all_concepts,
            'metrics': metrics,
            'node_count': len(G.nodes()),
            'edge_count': len(G.edges()),
            'concept_sentiments': dict(concept_sentiments)
        }
    
    def _simple_sentiment_analysis(self, text: str) -> float:
        """간단한 감정 분석 (TextBlob 의존성 제거)"""
        
        try:
            # 긍정적 키워드
            positive_words = [
                'good', 'great', 'excellent', 'positive', 'growth', 'profit', 'success',
                'opportunity', 'optimistic', 'recovery', 'improvement', 'bullish'
            ]
            
            # 부정적 키워드
            negative_words = [
                'bad', 'terrible', 'negative', 'loss', 'crash', 'decline', 'recession',
                'crisis', 'worry', 'concern', 'risk', 'problem', 'bearish'
            ]
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                return 0.3
            elif negative_count > positive_count:
                return -0.3
            else:
                return 0.0
                
        except Exception as e:
            self.logger.warning(f"감정 분석 오류: {e}")
            return 0.0
    
    def _determine_relationship_type_safe(self, concept1: str, concept2: str, weight: float) -> str:
        """안전한 관계 유형 결정"""
        
        try:
            # 특정 개념 쌍에 대한 관계 유형 정의
            strong_correlations = {
                ('monetary_policy', 'inflation'): 'causal_relationship',
                ('inflation', 'stock_market'): 'inverse_relationship',
                ('technology', 'stock_market'): 'strong_correlation',
                ('geopolitical_risk', 'market_sentiment'): 'causal_relationship',
                ('labor_market', 'consumer_spending'): 'strong_correlation',
                ('government_policy', 'market_sentiment'): 'moderate_correlation',
                ('energy', 'inflation'): 'strong_correlation',
                ('real_estate', 'monetary_policy'): 'strong_correlation',
                ('cryptocurrency', 'market_sentiment'): 'strong_correlation',
                ('esg', 'technology'): 'moderate_correlation'
            }
            
            # 순서 무관하게 검색
            pair1 = (concept1, concept2)
            pair2 = (concept2, concept1)
            
            if pair1 in strong_correlations:
                return strong_correlations[pair1]
            elif pair2 in strong_correlations:
                return strong_correlations[pair2]
            
            # 가중치 기반 관계 유형 결정
            if weight > 5.0:
                return 'strong_correlation'
            elif weight > 3.0:
                return 'moderate_correlation'
            elif weight > 1.0:
                return 'weak_correlation'
            else:
                return 'mentioned_together'
                
        except Exception as e:
            self.logger.warning(f"관계 유형 결정 오류: {e}")
            return 'mentioned_together'
    
    def _calculate_network_metrics_safe(self, G: nx.Graph) -> Dict[str, Any]:
        """안전한 네트워크 메트릭 계산"""
        
        if len(G.nodes()) == 0:
            return {'error': 'Empty graph'}
        
        metrics = {}
        
        try:
            # 기본 메트릭
            metrics['density'] = float(nx.density(G))
            metrics['average_clustering'] = float(nx.average_clustering(G))
            
            # 중심성 지표 (안전하게 계산)
            if len(G.nodes()) > 1:
                degree_centrality = nx.degree_centrality(G)
                betweenness_centrality = nx.betweenness_centrality(G)
                closeness_centrality = nx.closeness_centrality(G)
                
                metrics['centrality'] = {
                    'degree': {k: float(v) for k, v in degree_centrality.items()},
                    'betweenness': {k: float(v) for k, v in betweenness_centrality.items()},
                    'closeness': {k: float(v) for k, v in closeness_centrality.items()}
                }
                
                # 가장 중요한 노드들
                metrics['top_nodes'] = {
                    'by_degree': sorted(degree_centrality.items(), 
                                      key=lambda x: x[1], reverse=True)[:5],
                    'by_betweenness': sorted(betweenness_centrality.items(), 
                                           key=lambda x: x[1], reverse=True)[:5]
                }
            
            # 연결 성분
            if nx.is_connected(G):
                metrics['diameter'] = nx.diameter(G)
                metrics['average_path_length'] = float(nx.average_shortest_path_length(G))
            else:
                components = list(nx.connected_components(G))
                metrics['connected_components'] = len(components)
                metrics['largest_component_size'] = len(max(components, key=len))
            
        except Exception as e:
            self.logger.warning(f"메트릭 계산 중 오류: {e}")
            metrics['error'] = str(e)
        
        return metrics
    
    def generate_network_insights(self, network_result: Dict[str, Any]) -> List[str]:
        """네트워크 분석 결과에서 인사이트 생성 (안전한 버전)"""
        
        insights = []
        
        try:
            if 'error' in network_result:
                return [f"네트워크 분석 중 오류가 발생했습니다: {network_result['error']}"]
            
            G = network_result.get('graph')
            metrics = network_result.get('metrics', {})
            concepts = network_result.get('concepts', {})
            
            if not G or len(G.nodes()) == 0:
                return ["분석할 수 있는 경제 개념이 발견되지 않았습니다."]
            
            # 1. 전체 네트워크 규모
            insights.append(f"📊 총 {len(G.nodes())}개의 경제 개념과 {len(G.edges())}개의 관계를 발견했습니다.")
            
            # 2. 가장 중요한 개념들
            if 'centrality' in metrics and 'degree' in metrics['centrality']:
                top_concepts = sorted(metrics['centrality']['degree'].items(), 
                                    key=lambda x: x[1], reverse=True)[:3]
                concept_names = [self._get_concept_display_name(concept) for concept, _ in top_concepts]
                insights.append(f"🎯 가장 중요한 경제 개념: {', '.join(concept_names)}")
            
            # 3. 네트워크 밀도
            if 'density' in metrics:
                density = metrics['density']
                if density > 0.3:
                    insights.append("🔗 경제 개념들 간의 연결이 매우 밀접합니다.")
                elif density > 0.1:
                    insights.append("🔗 경제 개념들 간의 연결이 적당합니다.")
                else:
                    insights.append("🔗 경제 개념들 간의 연결이 느슨합니다.")
            
            # 4. 감정 분석 결과
            concept_sentiments = network_result.get('concept_sentiments', {})
            if concept_sentiments:
                positive_concepts = []
                negative_concepts = []
                
                for concept, sentiments in concept_sentiments.items():
                    if sentiments:
                        avg_sentiment = np.mean(sentiments)
                        if avg_sentiment > 0.1:
                            positive_concepts.append(self._get_concept_display_name(concept))
                        elif avg_sentiment < -0.1:
                            negative_concepts.append(self._get_concept_display_name(concept))
                
                if positive_concepts:
                    insights.append(f"😊 긍정적 언급: {', '.join(positive_concepts[:3])}")
                if negative_concepts:
                    insights.append(f"😟 부정적 언급: {', '.join(negative_concepts[:3])}")
            
            # 5. 주요 관계들
            if G.edges():
                strong_relationships = []
                for edge in G.edges(data=True):
                    if edge[2].get('weight', 0) > 0.7:
                        source_name = self._get_concept_display_name(edge[0])
                        target_name = self._get_concept_display_name(edge[1])
                        strong_relationships.append(f"{source_name} ↔ {target_name}")
                
                if strong_relationships:
                    insights.append(f"🔥 강한 연관성: {', '.join(strong_relationships[:2])}")
            
        except Exception as e:
            self.logger.error(f"인사이트 생성 오류: {e}")
            insights.append("인사이트 생성 중 오류가 발생했습니다.")
        
        return insights if insights else ["분석 결과를 생성할 수 없습니다."]
    
    def _get_concept_display_name(self, concept_key: str) -> str:
        """개념 키를 표시용 이름으로 변환"""
        
        display_names = {
            'monetary_policy': '통화정책',
            'inflation': '인플레이션',
            'stock_market': '주식시장',
            'corporate_performance': '기업실적',
            'technology': '기술주',
            'financial_sector': '금융섹터',
            'energy': '에너지',
            'real_estate': '부동산',
            'international_trade': '국제무역',
            'cryptocurrency': '암호화폐',
            'esg': 'ESG',
            'labor_market': '고용시장',
            'consumer_spending': '소비',
            'government_policy': '정부정책',
            'geopolitical_risk': '지정학적 리스크',
            'market_sentiment': '시장심리'
        }
        
        return display_names.get(concept_key, concept_key.replace('_', ' ').title())

if __name__ == "__main__":
    # 테스트 실행
    analyzer = FixedEnhancedNetworkAnalyzer()
    
    # 실제 Reddit 데이터로 테스트
    try:
        from real_reddit_collector import RealRedditCollector
        
        print("🧪 수정된 네트워크 분석기 테스트")
        print("=" * 50)
        
        # Reddit 데이터 수집
        reddit_collector = RealRedditCollector()
        texts = reddit_collector.get_texts_for_network_analysis(max_posts=20)
        
        print(f"📱 Reddit에서 수집한 텍스트: {len(texts)}개")
        
        if texts:
            # 네트워크 분석 실행
            result = analyzer.analyze_concept_relationships(texts)
            
            if 'error' not in result:
                print(f"✅ 분석 성공:")
                print(f"   노드 수: {result['node_count']}")
                print(f"   엣지 수: {result['edge_count']}")
                
                # 인사이트 생성
                insights = analyzer.generate_network_insights(result)
                print(f"\n💡 인사이트:")
                for insight in insights:
                    print(f"   • {insight}")
            else:
                print(f"❌ 분석 실패: {result['error']}")
        else:
            print("❌ Reddit 데이터 수집 실패")
            
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        
        # 백업: 샘플 데이터로 테스트
        print("\n🔄 샘플 데이터로 백업 테스트:")
        sample_texts = [
            "연준이 기준금리를 인상하며 인플레이션 억제에 나섰다",
            "기술주가 하락세를 보이며 주식시장이 불안정하다",
            "비트코인 가격이 상승하며 암호화폐 시장이 회복세다"
        ]
        
        result = analyzer.analyze_concept_relationships(sample_texts)
        if 'error' not in result:
            print(f"✅ 백업 테스트 성공: {result['node_count']}개 노드")
        else:
            print(f"❌ 백업 테스트도 실패: {result['error']}")
