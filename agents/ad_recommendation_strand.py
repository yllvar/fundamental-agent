"""
Ad Recommendation Strand Agent
Analyzes article content and recommends 3 related ads
"""

import random
from typing import Dict, List, Any, Optional
from datetime import datetime

from .strands_framework import BaseStrandAgent, StrandContext, StrandMessage, MessageType

class AdRecommendationStrand(BaseStrandAgent):
    """Ad Recommendation Strand Agent"""
    
    def __init__(self):
        super().__init__(
            agent_id="ad_recommender",
            name="Ad Recommendation Agent"
        )
        
        self.capabilities = [
            "contextual_ad_matching",
            "financial_product_recommendation",
            "content_based_targeting",
            "audience_segmentation",
            "ad_performance_optimization"
        ]
        
        # Ad database
        self.ad_database = {
            'investment_platforms': [
                {
                    'id': 'inv_001',
                    'title': 'Smart Investment Platform',
                    'description': 'Start safe and profitable investing with AI-based portfolio management.',
                    'cta': 'Get Free Investment Consultation',
                    'keywords': ['investment', 'portfolio', 'profit', 'asset management'],
                    'target_events': ['price_change', 'volume_spike'],
                    'risk_level': 'medium'
                },
                {
                    'id': 'inv_002',
                    'title': 'Robo-Advisor Service',
                    'description': 'Save time and effort with expert-level automated investment management.',
                    'cta': '1 Month Free Trial',
                    'keywords': ['auto investing', 'robo-advisor', 'expert', 'management'],
                    'target_events': ['high_volatility'],
                    'risk_level': 'low'
                }
            ],
            'trading_tools': [
                {
                    'id': 'tool_001',
                    'title': 'Real-Time Trading Tools',
                    'description': 'Experience advanced charts and analysis tools used by professional traders.',
                    'cta': 'Try Premium Tools',
                    'keywords': ['trading', 'chart', 'analysis', 'real-time'],
                    'target_events': ['volume_spike', 'high_volatility'],
                    'risk_level': 'high'
                },
                {
                    'id': 'tool_002',
                    'title': 'Mobile Trading App',
                    'description': 'Enjoy fast and secure mobile trading anytime, anywhere.',
                    'cta': 'Download App',
                    'keywords': ['mobile', 'trading', 'app', 'convenience'],
                    'target_events': ['price_change'],
                    'risk_level': 'medium'
                }
            ],
            'education_services': [
                {
                    'id': 'edu_001',
                    'title': 'Investment Education Academy',
                    'description': 'Become an expert with systematic investment education from basics to advanced.',
                    'cta': 'Take Free Course',
                    'keywords': ['education', 'learning', 'basics', 'expert'],
                    'target_events': ['price_change', 'volume_spike', 'high_volatility'],
                    'risk_level': 'low'
                },
                {
                    'id': 'edu_002',
                    'title': 'Fundamental Agent Subscription',
                    'description': 'Stay ahead of the market with real-time analysis and expert opinions.',
                    'cta': 'Premium Subscription',
                    'keywords': ['news', 'analysis', 'expert', 'market info'],
                    'target_events': ['price_change', 'volume_spike'],
                    'risk_level': 'low'
                }
            ],
            'financial_products': [
                {
                    'id': 'prod_001',
                    'title': 'High-Yield Savings',
                    'description': 'A special savings product offering safety and high returns.',
                    'cta': 'View Product Details',
                    'keywords': ['savings', 'safe', 'returns', 'deposit'],
                    'target_events': ['high_volatility'],
                    'risk_level': 'low'
                },
                {
                    'id': 'prod_002',
                    'title': 'Investment Insurance',
                    'description': 'Coverage and investment at the same time! Enjoy stable returns and insurance benefits.',
                    'cta': 'Free Design Consultation',
                    'keywords': ['insurance', 'investment', 'coverage', 'stability'],
                    'target_events': ['price_change'],
                    'risk_level': 'medium'
                }
            ]
        }
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return self.capabilities
    
    async def process(self, context: StrandContext, message: Optional[StrandMessage] = None) -> Dict[str, Any]:
        """Process ad recommendation"""
        
        # Collect required data
        event_data = context.input_data.get('event')
        article = await self.get_shared_data(context, 'article')
        data_analysis = await self.get_shared_data(context, 'data_analysis')
        
        if not event_data or not article:
            raise Exception("No data for ad recommendation")
        
        self.logger.info("📢 Ad recommendation started")
        
        try:
            # 1. Context analysis
            context_analysis = await self._analyze_context(event_data, article, data_analysis)
            
            # 2. Audience analysis
            audience_profile = await self._analyze_audience(context_analysis)
            
            # 3. Ad matching
            matched_ads = await self._match_advertisements(context_analysis, audience_profile)
            
            # 4. Ad ranking and selection
            recommended_ads = await self._rank_and_select_ads(matched_ads, context_analysis)
            
            # 5. Ad personalization
            personalized_ads = await self._personalize_ads(recommended_ads, context_analysis)
            
            result = {
                'recommended_ads': personalized_ads,
                'context_analysis': context_analysis,
                'audience_profile': audience_profile,
                'recommendation_timestamp': datetime.now().isoformat(),
                'total_ads': len(personalized_ads)
            }
            
            # Save to shared memory
            await self.set_shared_data(context, 'advertisements', result)
            
            self.logger.info(f"✅ Ad recommendation completed: {len(personalized_ads)}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Ad recommendation failed: {e}")
            raise
    
    async def _analyze_context(self, event_data: Dict[str, Any], article: Dict[str, Any], data_analysis: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Context analysis"""
        
        symbol = event_data.get('symbol', 'Unknown')
        event_type = event_data.get('event_type', 'unknown')
        severity = event_data.get('severity', 'low')
        
        # Extract keywords from article
        article_text = f"{article.get('title', '')} {article.get('body', '')} {article.get('conclusion', '')}"
        keywords = await self._extract_keywords(article_text)
        
        # Market condition analysis
        market_condition = 'neutral'
        risk_sentiment = 'medium'
        
        if data_analysis:
            # Volatility-based market condition assessment
            stats = data_analysis.get('statistics', {})
            if stats.get('volatility_annualized'):
                volatility = stats['volatility_annualized']
                if volatility > 0.3:  # 30% 이상
                    market_condition = 'volatile'
                    risk_sentiment = 'high'
                elif volatility < 0.15:  # 15% 미만
                    market_condition = 'stable'
                    risk_sentiment = 'low'
            
            # Technical indicator-based analysis
            technical = data_analysis.get('technical_indicators', {})
            if technical.get('rsi'):
                rsi = technical['rsi']
                if rsi > 70:
                    market_condition = 'overbought'
                elif rsi < 30:
                    market_condition = 'oversold'
        
        return {
            'symbol': symbol,
            'event_type': event_type,
            'severity': severity,
            'keywords': keywords,
            'market_condition': market_condition,
            'risk_sentiment': risk_sentiment,
            'article_length': len(article.get('body', '').split()),
            'has_technical_analysis': bool(data_analysis and data_analysis.get('technical_indicators'))
        }
    
    async def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        
        # Financial keyword dictionary
        financial_keywords = {
            '투자', '거래', '수익', '손실', '리스크', '위험', '안전', '수익률',
            '포트폴리오', '자산', '주식', '채권', '펀드', '적금', '예금', '보험',
            '분석', '예측', '전망', '추천', '상승', '하락', '변동성', '안정성',
            '트레이딩', '매수', '매도', '차트', '지표', '시장', '경제', '금융'
        }
        
        # Convert text to lowercase and split words
        words = text.lower().split()
        
        # Extract financial keywords only
        extracted_keywords = []
        for word in words:
            for keyword in financial_keywords:
                if keyword in word:
                    extracted_keywords.append(keyword)
        
        # Deduplicate and sort by frequency
        keyword_counts = {}
        for keyword in extracted_keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        # Return top 10 keywords
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        return [keyword for keyword, count in sorted_keywords[:10]]
    
    async def _analyze_audience(self, context_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Target audience analysis"""
        
        event_type = context_analysis.get('event_type', 'unknown')
        risk_sentiment = context_analysis.get('risk_sentiment', 'medium')
        market_condition = context_analysis.get('market_condition', 'neutral')
        
        # Event type-based audience profiles
        audience_profiles = {
            'price_change': {
                'investor_type': 'active_trader',
                'risk_tolerance': 'medium_to_high',
                'interests': ['trading_tools', 'market_analysis', 'investment_platforms'],
                'experience_level': 'intermediate'
            },
            'volume_spike': {
                'investor_type': 'momentum_trader',
                'risk_tolerance': 'high',
                'interests': ['trading_tools', 'real_time_data', 'technical_analysis'],
                'experience_level': 'advanced'
            },
            'high_volatility': {
                'investor_type': 'risk_averse',
                'risk_tolerance': 'low_to_medium',
                'interests': ['stable_products', 'education', 'risk_management'],
                'experience_level': 'beginner_to_intermediate'
            }
        }
        
        base_profile = audience_profiles.get(event_type, audience_profiles['price_change'])
        
        # Adjustment based on market condition
        if market_condition == 'volatile':
            base_profile['risk_tolerance'] = 'low'
            base_profile['interests'].append('education')
        elif market_condition == 'stable':
            base_profile['risk_tolerance'] = 'medium_to_high'
            base_profile['interests'].append('investment_platforms')
        
        return {
            **base_profile,
            'market_awareness': 'high' if context_analysis.get('has_technical_analysis') else 'medium',
            'engagement_level': 'high' if context_analysis.get('article_length', 0) > 100 else 'medium'
        }
    
    async def _match_advertisements(self, context_analysis: Dict[str, Any], audience_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Ad matching"""
        
        event_type = context_analysis.get('event_type', 'unknown')
        keywords = context_analysis.get('keywords', [])
        risk_sentiment = context_analysis.get('risk_sentiment', 'medium')
        
        matched_ads = []
        
        # Review all ad categories
        for category, ads in self.ad_database.items():
            for ad in ads:
                score = 0
                
                # Event type matching
                if event_type in ad.get('target_events', []):
                    score += 3
                
                # Keyword matching
                ad_keywords = ad.get('keywords', [])
                keyword_matches = len(set(keywords) & set(ad_keywords))
                score += keyword_matches * 2
                
                # Risk level matching
                ad_risk = ad.get('risk_level', 'medium')
                audience_risk = audience_profile.get('risk_tolerance', 'medium')
                
                if self._risk_compatibility(ad_risk, audience_risk):
                    score += 2
                
                # Interest matching
                audience_interests = audience_profile.get('interests', [])
                if category.replace('_', ' ') in ' '.join(audience_interests):
                    score += 1
                
                if score > 0:
                    matched_ads.append({
                        **ad,
                        'category': category,
                        'match_score': score,
                        'match_reasons': self._get_match_reasons(ad, context_analysis, audience_profile)
                    })
        
        return matched_ads
    
    def _risk_compatibility(self, ad_risk: str, audience_risk: str) -> bool:
        """Risk compatibility check"""
        
        risk_levels = {'low': 1, 'medium': 2, 'high': 3}
        
        ad_level = risk_levels.get(ad_risk, 2)
        
        # Parse audience risk tolerance
        if 'low' in audience_risk:
            audience_max = 1 if 'to' not in audience_risk else 2
        elif 'high' in audience_risk:
            audience_max = 3
        else:
            audience_max = 2
        
        return ad_level <= audience_max
    
    def _get_match_reasons(self, ad: Dict[str, Any], context_analysis: Dict[str, Any], audience_profile: Dict[str, Any]) -> List[str]:
        """Generate matching reasons"""
        
        reasons = []
        
        # Event type matching
        if context_analysis.get('event_type') in ad.get('target_events', []):
            reasons.append(f"Suitable for {context_analysis.get('event_type')} event")
        
        # Keyword matching
        keywords = context_analysis.get('keywords', [])
        ad_keywords = ad.get('keywords', [])
        matches = set(keywords) & set(ad_keywords)
        if matches:
            reasons.append(f"Matching keywords: {', '.join(list(matches)[:3])}")
        
        # Risk level
        if self._risk_compatibility(ad.get('risk_level', 'medium'), audience_profile.get('risk_tolerance', 'medium')):
            reasons.append("Suitable risk level")
        
        return reasons
    
    async def _rank_and_select_ads(self, matched_ads: List[Dict[str, Any]], context_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Rank and select ads"""
        
        # Sort by match score
        sorted_ads = sorted(matched_ads, key=lambda x: x.get('match_score', 0), reverse=True)
        
        # 다양성을 위해 카테고리별로 최대 1개씩 선택
        selected_ads = []
        used_categories = set()
        
        for ad in sorted_ads:
            category = ad.get('category')
            if category not in used_categories and len(selected_ads) < 3:
                selected_ads.append(ad)
                used_categories.add(category)
        
        # Fill remaining by score if fewer than 3
        if len(selected_ads) < 3:
            for ad in sorted_ads:
                if ad not in selected_ads and len(selected_ads) < 3:
                    selected_ads.append(ad)
        
        # Random fill if still fewer than 3
        if len(selected_ads) < 3:
            all_ads = []
            for category_ads in self.ad_database.values():
                all_ads.extend(category_ads)
            
            remaining_ads = [ad for ad in all_ads if ad not in selected_ads]
            while len(selected_ads) < 3 and remaining_ads:
                selected_ads.append(remaining_ads.pop(random.randint(0, len(remaining_ads) - 1)))
        
        return selected_ads[:3]  # Max 3 ads
    
    async def _personalize_ads(self, ads: List[Dict[str, Any]], context_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Ad personalization"""
        
        personalized_ads = []
        symbol = context_analysis.get('symbol', 'Unknown')
        event_type = context_analysis.get('event_type', 'unknown')
        
        for i, ad in enumerate(ads):
            personalized_ad = {
                'id': ad.get('id', f'ad_{i+1}'),
                'title': ad.get('title', 'Investment Product'),
                'description': ad.get('description', 'An investment-related service.'),
                'cta': ad.get('cta', 'View Details'),
                'category': ad.get('category', 'general'),
                'match_score': ad.get('match_score', 0),
                'match_reasons': ad.get('match_reasons', []),
                'personalization': {
                    'symbol_context': symbol,
                    'event_context': event_type,
                    'relevance_score': ad.get('match_score', 0) / 10.0
                }
            }
            
            # Context-based description personalization
            if symbol != 'Unknown' and event_type == 'volume_spike':
                personalized_ad['description'] += f" Especially useful in active trading situations like {symbol}."
            elif event_type == 'high_volatility':
                personalized_ad['description'] += " Helps with stable investing in volatile markets."
            
            personalized_ads.append(personalized_ad)
        
        return personalized_ads
