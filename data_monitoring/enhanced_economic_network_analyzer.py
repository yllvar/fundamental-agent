#!/usr/bin/env python3
"""
개선된 경제 개념 기반 소셜 네트워크 분석 모듈
SNS 및 댓글 내용을 기반으로 경제 개념들 간의 관계를 분석
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
import json

class EnhancedEconomicNetworkAnalyzer:
    """개선된 경제 개념 네트워크 분석기"""
    
    def __init__(self):
        """초기화"""
        self.logger = logging.getLogger(__name__)
        
        # 16개 주요 경제 카테고리와 세부 개념들
        self.economic_concepts = {
            # 1. 통화정책 (Monetary Policy)
            'monetary_policy': {
                'main_concepts': ['통화정책', '금리정책', '기준금리', '연방기금금리', 'Fed Rate'],
                'related_terms': [
                    '금리인상', '금리인하', '금리동결', '양적완화', 'QE', 'Quantitative Easing',
                    '테이퍼링', 'Tapering', '긴축정책', '완화정책', '중앙은행', 'Federal Reserve',
                    'Fed', 'ECB', 'BOJ', 'PBOC', '통화공급', 'Money Supply', 'FOMC'
                ],
                'weight': 1.0
            },
            
            # 2. 인플레이션 (Inflation)
            'inflation': {
                'main_concepts': ['인플레이션', 'Inflation', '물가상승', 'CPI', 'PCE'],
                'related_terms': [
                    '소비자물가지수', 'Consumer Price Index', '근원인플레이션', 'Core Inflation',
                    '디플레이션', 'Deflation', '스태그플레이션', 'Stagflation', '물가안정',
                    '인플레이션 타겟', 'Inflation Target', '물가압력', 'Price Pressure'
                ],
                'weight': 1.0
            },
            
            # 3. 주식시장 (Stock Market)
            'stock_market': {
                'main_concepts': ['주식시장', 'Stock Market', '증시', 'Equity Market'],
                'related_terms': [
                    'S&P 500', 'NASDAQ', 'Dow Jones', 'KOSPI', 'KOSDAQ', '상승장', '하락장',
                    'Bull Market', 'Bear Market', '변동성', 'Volatility', 'VIX', '공포지수',
                    '시가총액', 'Market Cap', '거래량', 'Volume', 'P/E Ratio', 'PER'
                ],
                'weight': 1.0
            },
            
            # 4. 기업실적 (Corporate Performance)
            'corporate_performance': {
                'main_concepts': ['기업실적', '실적발표', 'Earnings', 'Corporate Results'],
                'related_terms': [
                    '매출', 'Revenue', '순이익', 'Net Income', '영업이익', 'Operating Income',
                    'EPS', 'Earnings Per Share', '가이던스', 'Guidance', '실적전망',
                    '분기실적', 'Quarterly Results', '연간실적', 'Annual Results'
                ],
                'weight': 0.9
            },
            
            # 5. 기술주 (Technology Stocks)
            'technology': {
                'main_concepts': ['기술주', 'Tech Stocks', '테크주', 'Technology Sector'],
                'related_terms': [
                    'Apple', 'Microsoft', 'Google', 'Amazon', 'Tesla', 'Meta', 'Netflix',
                    'NVIDIA', 'Intel', 'AMD', '반도체', 'Semiconductor', 'AI', '인공지능',
                    '클라우드', 'Cloud Computing', '전기차', 'EV', 'Electric Vehicle'
                ],
                'weight': 0.9
            },
            
            # 6. 금융섹터 (Financial Sector)
            'financial_sector': {
                'main_concepts': ['금융섹터', 'Financial Sector', '은행주', 'Banking'],
                'related_terms': [
                    'JPMorgan', 'Goldman Sachs', 'Bank of America', 'Wells Fargo',
                    '순이자마진', 'NIM', '대출', 'Lending', '신용위험', 'Credit Risk',
                    '자본비율', 'Capital Ratio', '스트레스 테스트', 'Stress Test'
                ],
                'weight': 0.8
            },
            
            # 7. 에너지 (Energy)
            'energy': {
                'main_concepts': ['에너지', 'Energy', '원유', 'Oil', '천연가스', 'Natural Gas'],
                'related_terms': [
                    'WTI', 'Brent', 'OPEC', '셰일오일', 'Shale Oil', '정유', 'Refining',
                    '신재생에너지', 'Renewable Energy', '태양광', 'Solar', '풍력', 'Wind',
                    'ExxonMobil', 'Chevron', 'Shell', 'BP'
                ],
                'weight': 0.8
            },
            
            # 8. 부동산 (Real Estate)
            'real_estate': {
                'main_concepts': ['부동산', 'Real Estate', '주택시장', 'Housing Market'],
                'related_terms': [
                    '주택가격', 'Home Prices', '모기지', 'Mortgage', '주택담보대출',
                    '부동산 투자', 'Real Estate Investment', 'REIT', '상업용 부동산',
                    'Commercial Real Estate', '주택 판매', 'Home Sales'
                ],
                'weight': 0.8
            },
            
            # 9. 국제무역 (International Trade)
            'international_trade': {
                'main_concepts': ['국제무역', 'International Trade', '무역전쟁', 'Trade War'],
                'related_terms': [
                    '관세', 'Tariff', '수출', 'Export', '수입', 'Import', '무역수지', 'Trade Balance',
                    '공급망', 'Supply Chain', '글로벌화', 'Globalization', 'WTO',
                    '미중무역', 'US-China Trade', '브렉시트', 'Brexit'
                ],
                'weight': 0.8
            },
            
            # 10. 암호화폐 (Cryptocurrency)
            'cryptocurrency': {
                'main_concepts': ['암호화폐', 'Cryptocurrency', '비트코인', 'Bitcoin'],
                'related_terms': [
                    'Ethereum', '이더리움', '블록체인', 'Blockchain', 'DeFi', 'NFT',
                    '디지털 자산', 'Digital Asset', '가상화폐', 'Virtual Currency',
                    'CBDC', '중앙은행 디지털화폐', 'Stablecoin', '스테이블코인'
                ],
                'weight': 0.7
            },
            
            # 11. ESG (Environmental, Social, Governance)
            'esg': {
                'main_concepts': ['ESG', '지속가능성', 'Sustainability', '친환경'],
                'related_terms': [
                    '탄소중립', 'Carbon Neutral', '기후변화', 'Climate Change',
                    '그린에너지', 'Green Energy', '사회적 책임', 'Social Responsibility',
                    '지배구조', 'Governance', '지속가능 투자', 'Sustainable Investment'
                ],
                'weight': 0.7
            },
            
            # 12. 고용시장 (Labor Market)
            'labor_market': {
                'main_concepts': ['고용시장', 'Labor Market', '실업률', 'Unemployment Rate'],
                'related_terms': [
                    '비농업 고용', 'Non-farm Payroll', '구인', 'Job Opening', '임금상승',
                    'Wage Growth', '노동참여율', 'Labor Participation Rate',
                    '구직급여', 'Unemployment Benefits', '일자리 창출', 'Job Creation'
                ],
                'weight': 0.8
            },
            
            # 13. 소비 (Consumer Spending)
            'consumer_spending': {
                'main_concepts': ['소비', 'Consumer Spending', '소매판매', 'Retail Sales'],
                'related_terms': [
                    '소비자 신뢰', 'Consumer Confidence', '개인소비', 'Personal Consumption',
                    '소비심리', 'Consumer Sentiment', '가계소득', 'Household Income',
                    '저축률', 'Savings Rate', '소비패턴', 'Consumption Pattern'
                ],
                'weight': 0.8
            },
            
            # 14. 정부정책 (Government Policy)
            'government_policy': {
                'main_concepts': ['정부정책', 'Government Policy', '재정정책', 'Fiscal Policy'],
                'related_terms': [
                    '정부지출', 'Government Spending', '세금', 'Tax', '세율', 'Tax Rate',
                    '부채', 'Debt', '적자', 'Deficit', '예산', 'Budget', '부양책', 'Stimulus',
                    '인프라', 'Infrastructure', '규제', 'Regulation'
                ],
                'weight': 0.8
            },
            
            # 15. 지정학적 리스크 (Geopolitical Risk)
            'geopolitical_risk': {
                'main_concepts': ['지정학적 리스크', 'Geopolitical Risk', '국제정치', 'International Politics'],
                'related_terms': [
                    '전쟁', 'War', '분쟁', 'Conflict', '제재', 'Sanctions', '외교', 'Diplomacy',
                    '안보', 'Security', '테러', 'Terrorism', '정치적 불안', 'Political Instability',
                    '선거', 'Election', '정권교체', 'Regime Change'
                ],
                'weight': 0.7
            },
            
            # 16. 시장심리 (Market Sentiment)
            'market_sentiment': {
                'main_concepts': ['시장심리', 'Market Sentiment', '투자심리', 'Investor Sentiment'],
                'related_terms': [
                    '공포', 'Fear', '탐욕', 'Greed', '낙관', 'Optimism', '비관', 'Pessimism',
                    '위험회피', 'Risk Aversion', '위험선호', 'Risk Appetite',
                    '시장 분위기', 'Market Mood', '투자자 신뢰', 'Investor Confidence'
                ],
                'weight': 0.7
            }
        }
        
        # 관계 유형별 가중치
        self.relationship_weights = {
            'strong_correlation': 1.0,      # 강한 상관관계
            'moderate_correlation': 0.7,    # 보통 상관관계
            'weak_correlation': 0.4,        # 약한 상관관계
            'causal_relationship': 0.9,     # 인과관계
            'inverse_relationship': 0.8,    # 역상관관계
            'temporal_relationship': 0.6,   # 시간적 관계
            'mentioned_together': 0.3       # 단순 동시 언급
        }
        
        self.logger.info("✅ 개선된 경제 네트워크 분석기 초기화 완료")
    
    def extract_economic_concepts(self, text: str) -> Dict[str, Any]:
        """텍스트에서 경제 개념 추출 (개선된 버전)"""
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
        
        return found_concepts, concept_scores
    
    def analyze_concept_relationships(self, texts: List[str]) -> Dict[str, Any]:
        """여러 텍스트에서 경제 개념 간 관계 분석"""
        self.logger.info("🔍 경제 개념 관계 분석 시작")
        
        # 모든 텍스트에서 개념 추출
        all_concepts = {}
        concept_cooccurrence = defaultdict(lambda: defaultdict(int))
        concept_sentiments = defaultdict(list)
        
        for text in texts:
            concepts, scores = self.extract_economic_concepts(text)
            
            # 감정 분석
            try:
                sentiment = TextBlob(text).sentiment.polarity
            except:
                sentiment = 0.0
            
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
        
        # 네트워크 그래프 생성
        G = nx.Graph()
        
        # 노드 추가 (개념들)
        for concept, data in all_concepts.items():
            avg_sentiment = np.mean(concept_sentiments[concept]) if concept_sentiments[concept] else 0
            
            G.add_node(concept, 
                      score=data['total_score'],
                      mentions=data['mention_count'],
                      terms=list(data['terms']),
                      weight=data['weight'],
                      sentiment=avg_sentiment,
                      size=min(data['total_score'] * 10, 100))  # 시각화용 크기
        
        # 엣지 추가 (관계들)
        edges_added = 0
        for concept1, connections in concept_cooccurrence.items():
            for concept2, weight in connections.items():
                if weight > 0.5:  # 임계값 이상의 관계만 포함
                    # 관계 유형 결정
                    relationship_type = self._determine_relationship_type_advanced(
                        concept1, concept2, weight
                    )
                    
                    # 정규화된 가중치
                    normalized_weight = min(weight / 10.0, 1.0)
                    
                    G.add_edge(concept1, concept2,
                              weight=normalized_weight,
                              relationship_type=relationship_type,
                              strength=weight)
                    edges_added += 1
        
        # 네트워크 메트릭 계산
        metrics = self._calculate_network_metrics(G)
        
        self.logger.info(f"✅ 네트워크 분석 완료: {len(G.nodes())}개 노드, {len(G.edges())}개 엣지")
        
        return {
            'graph': G,
            'concepts': all_concepts,
            'metrics': metrics,
            'node_count': len(G.nodes()),
            'edge_count': len(G.edges()),
            'concept_sentiments': dict(concept_sentiments)
        }
    
    def _determine_relationship_type_advanced(self, concept1: str, concept2: str, weight: float) -> str:
        """고급 관계 유형 결정"""
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
    
    def _calculate_network_metrics(self, G: nx.Graph) -> Dict[str, Any]:
        """네트워크 메트릭 계산"""
        if len(G.nodes()) == 0:
            return {}
        
        metrics = {}
        
        try:
            # 기본 메트릭
            metrics['density'] = nx.density(G)
            metrics['average_clustering'] = nx.average_clustering(G)
            
            # 중심성 지표
            degree_centrality = nx.degree_centrality(G)
            betweenness_centrality = nx.betweenness_centrality(G)
            closeness_centrality = nx.closeness_centrality(G)
            
            metrics['centrality'] = {
                'degree': degree_centrality,
                'betweenness': betweenness_centrality,
                'closeness': closeness_centrality
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
                metrics['average_path_length'] = nx.average_shortest_path_length(G)
            else:
                components = list(nx.connected_components(G))
                metrics['connected_components'] = len(components)
                metrics['largest_component_size'] = len(max(components, key=len))
            
        except Exception as e:
            self.logger.warning(f"메트릭 계산 중 오류: {e}")
            metrics['error'] = str(e)
        
        return metrics
    
    def analyze_sns_comments_network(self, comments_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """SNS 댓글 데이터에서 네트워크 분석"""
        self.logger.info("💬 SNS 댓글 네트워크 분석 시작")
        
        # 댓글 텍스트 추출
        texts = []
        for comment in comments_data:
            text = comment.get('text', '') or comment.get('content', '') or comment.get('body', '')
            if text and len(text.strip()) > 10:  # 최소 길이 필터
                texts.append(text.strip())
        
        if not texts:
            self.logger.warning("분석할 댓글 텍스트가 없습니다")
            return {'error': 'No valid comment texts found'}
        
        # 개념 관계 분석
        network_result = self.analyze_concept_relationships(texts)
        
        # 추가 분석: 시간별 트렌드 (댓글에 시간 정보가 있는 경우)
        if comments_data and 'timestamp' in comments_data[0]:
            network_result['temporal_analysis'] = self._analyze_temporal_trends(comments_data)
        
        return network_result
    
    def _analyze_temporal_trends(self, comments_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """시간별 개념 트렌드 분석"""
        # 시간별로 댓글 그룹화
        from collections import defaultdict
        import datetime
        
        time_groups = defaultdict(list)
        
        for comment in comments_data:
            timestamp = comment.get('timestamp')
            if timestamp:
                # 시간을 시간대별로 그룹화 (예: 1시간 단위)
                if isinstance(timestamp, str):
                    try:
                        dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    except:
                        continue
                else:
                    dt = timestamp
                
                hour_key = dt.replace(minute=0, second=0, microsecond=0)
                time_groups[hour_key].append(comment.get('text', ''))
        
        # 시간대별 개념 분석
        temporal_trends = {}
        for time_key, texts in time_groups.items():
            if texts:
                concepts, _ = self.extract_economic_concepts(' '.join(texts))
                temporal_trends[time_key.isoformat()] = {
                    concept: data['score'] for concept, data in concepts.items()
                }
        
        return temporal_trends
    
    def generate_network_insights(self, network_result: Dict[str, Any]) -> List[str]:
        """네트워크 분석 결과에서 인사이트 생성"""
        insights = []
        
        if 'error' in network_result:
            return ["네트워크 분석 중 오류가 발생했습니다."]
        
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
                avg_sentiment = np.mean(sentiments) if sentiments else 0
                if avg_sentiment > 0.1:
                    positive_concepts.append(self._get_concept_display_name(concept))
                elif avg_sentiment < -0.1:
                    negative_concepts.append(self._get_concept_display_name(concept))
            
            if positive_concepts:
                insights.append(f"😊 긍정적 언급: {', '.join(positive_concepts[:3])}")
            if negative_concepts:
                insights.append(f"😟 부정적 언급: {', '.join(negative_concepts[:3])}")
        
        # 5. 특별한 관계 패턴
        strong_relationships = []
        for edge in G.edges(data=True):
            if edge[2].get('weight', 0) > 0.7:
                concept1_name = self._get_concept_display_name(edge[0])
                concept2_name = self._get_concept_display_name(edge[1])
                relationship_type = edge[2].get('relationship_type', 'related')
                strong_relationships.append(f"{concept1_name} ↔ {concept2_name}")
        
        if strong_relationships:
            insights.append(f"🔥 강한 연관성: {', '.join(strong_relationships[:2])}")
        
        return insights
    
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
