"""
Review Strand Agent
Reviews article quality and suggests improvements
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime

from .strands_framework import BaseStrandAgent, StrandContext, StrandMessage, MessageType

class ReviewStrand(BaseStrandAgent):
    """Review Strand Agent"""
    
    def __init__(self):
        super().__init__(
            agent_id="reviewer",
            name="Article Review Agent"
        )
        
        self.capabilities = [
            "content_quality_review",
            "fact_checking",
            "readability_analysis",
            "compliance_check",
            "improvement_suggestions"
        ]
        
        # Review criteria
        self.review_criteria = {
            'content_accuracy': {
                'weight': 0.3,
                'checks': ['data_consistency', 'factual_accuracy', 'source_reliability']
            },
            'readability': {
                'weight': 0.25,
                'checks': ['sentence_length', 'vocabulary_level', 'structure_clarity']
            },
            'completeness': {
                'weight': 0.2,
                'checks': ['essential_information', 'context_provision', 'conclusion_presence']
            },
            'compliance': {
                'weight': 0.15,
                'checks': ['investment_advice_avoidance', 'disclaimer_presence', 'objective_tone']
            },
            'engagement': {
                'weight': 0.1,
                'checks': ['title_effectiveness', 'lead_strength', 'flow_quality']
            }
        }
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return self.capabilities
    
    async def process(self, context: StrandContext, message: Optional[StrandMessage] = None) -> Dict[str, Any]:
        """Process article review"""
        
        # Get article data
        article = await self.get_shared_data(context, 'article')
        if not article:
            raise Exception("No article to review")
        
        self.logger.info("🔍 Article review started")
        
        try:
            # 1. Content accuracy review
            accuracy_score = await self._review_content_accuracy(article, context)
            
            # 2. Readability analysis
            readability_score = await self._analyze_readability(article)
            
            # 3. Completeness review
            completeness_score = await self._review_completeness(article)
            
            # 4. Compliance review
            compliance_score = await self._review_compliance(article)
            
            # 5. Engagement analysis
            engagement_score = await self._analyze_engagement(article)
            
            # 6. Overall score calculation
            overall_score = await self._calculate_overall_score({
                'accuracy': accuracy_score,
                'readability': readability_score,
                'completeness': completeness_score,
                'compliance': compliance_score,
                'engagement': engagement_score
            })
            
            # 7. Improvement suggestions
            improvements = await self._suggest_improvements(article, {
                'accuracy': accuracy_score,
                'readability': readability_score,
                'completeness': completeness_score,
                'compliance': compliance_score,
                'engagement': engagement_score
            })
            
            # Review result package
            review_result = {
                'overall_score': overall_score,
                'detailed_scores': {
                    'content_accuracy': accuracy_score,
                    'readability': readability_score,
                    'completeness': completeness_score,
                    'compliance': compliance_score,
                    'engagement': engagement_score
                },
                'improvements': improvements,
                'review_timestamp': datetime.now().isoformat(),
                'reviewer': self.name,
                'status': 'approved' if overall_score >= 7.0 else 'needs_revision'
            }
            
            # Save to shared memory
            await self.set_shared_data(context, 'review_result', review_result)
            
            self.logger.info(f"✅ Article review completed (score: {overall_score:.1f}/10)")
            return review_result
            
        except Exception as e:
            self.logger.error(f"❌ Article review failed: {e}")
            raise
    
    async def _review_content_accuracy(self, article: Dict[str, Any], context: StrandContext) -> float:
        """Content accuracy review"""
        
        score = 8.0  # Base score
        
        try:
            # Data consistency check
            data_analysis = await self.get_shared_data(context, 'data_analysis')
            if data_analysis:
                # Compare article figures with data analysis results
                body = article.get('body', '')
                
                # Price consistency
                raw_data = data_analysis.get('raw_data', {})
                current_price = raw_data.get('current_price')
                if current_price and str(current_price) not in body:
                    score -= 0.5
                
                # Technical indicator consistency
                technical = data_analysis.get('technical_indicators', {})
                if technical.get('rsi'):
                    rsi = technical['rsi']
                    if 'RSI' in body:
                        # Check if RSI value is accurately reflected
                        if abs(rsi - 50) > 20:  # Extreme values
                            if ('overbought' in body and rsi < 70) or ('oversold' in body and rsi > 30):
                                score -= 1.0
            
            # Basic fact-checking
            body = article.get('body', '').lower()
            
            # Detect inaccurate phrases
            inaccurate_phrases = [
                'definitely', 'certainly', '100%', 'absolutely',
                'invest now', 'buy now', 'sell now'
            ]
            
            for phrase in inaccurate_phrases:
                if phrase in body:
                    score -= 0.3
            
            return max(0.0, min(10.0, score))
            
        except Exception as e:
            self.logger.error(f"Content accuracy review failed: {e}")
            return 7.0
    
    async def _analyze_readability(self, article: Dict[str, Any]) -> float:
        """Readability analysis"""
        
        score = 8.0
        
        try:
            body = article.get('body', '')
            if not body:
                return 5.0
            
            # Sentence length analysis
            sentences = re.split(r'[.!?]', body)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if sentences:
                avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
                
                # Optimal sentence length: 15-25 words
                if avg_sentence_length > 30:
                    score -= 1.0
                elif avg_sentence_length > 25:
                    score -= 0.5
                elif avg_sentence_length < 10:
                    score -= 0.5
            
            # Paragraph structure analysis
            paragraphs = body.split('\n\n')
            if len(paragraphs) < 2:
                score -= 0.5
            
            # Technical term density check
            technical_terms = [
                'RSI', 'MACD', 'Bollinger', 'moving average', 'volatility',
                'beta', 'correlation', 'overbought', 'oversold'
            ]
            
            term_count = sum(1 for term in technical_terms if term in body)
            word_count = len(body.split())
            
            if word_count > 0:
                term_density = term_count / word_count
                if term_density > 0.1:  # Over 10% means too technical
                    score -= 0.5
            
            return max(0.0, min(10.0, score))
            
        except Exception as e:
            self.logger.error(f"Readability analysis failed: {e}")
            return 7.0
    
    async def _review_completeness(self, article: Dict[str, Any]) -> float:
        """Completeness review"""
        
        score = 8.0
        
        try:
            # Check required elements
            title = article.get('title', '')
            lead = article.get('lead', '')
            body = article.get('body', '')
            conclusion = article.get('conclusion', '')
            
            # Title check
            if not title or len(title) < 10:
                score -= 1.0
            
            # Lead check
            if not lead or len(lead) < 20:
                score -= 1.0
            
            # Body check
            if not body or len(body.split()) < 50:
                score -= 2.0
            
            # Conclusion check
            if not conclusion or len(conclusion) < 20:
                score -= 0.5
            
            # Essential information coverage
            essential_elements = [
                'price', 'volume', 'volatility', 'analysis', 'market'
            ]
            
            missing_elements = 0
            for element in essential_elements:
                if element not in body:
                    missing_elements += 1
            
            score -= missing_elements * 0.2
            
            return max(0.0, min(10.0, score))
            
        except Exception as e:
            self.logger.error(f"Completeness review failed: {e}")
            return 7.0
    
    async def _review_compliance(self, article: Dict[str, Any]) -> float:
        """Compliance review"""
        
        score = 9.0
        
        try:
            body = article.get('body', '').lower()
            title = article.get('title', '').lower()
            conclusion = article.get('conclusion', '').lower()
            
            full_text = f"{title} {body} {conclusion}"
            
            # Detect investment advice phrases
            investment_advice_phrases = [
                'invest now', 'buy now', 'sell now', 'recommend',
                'purchase', 'sell', 'investment opportunity', 'guaranteed returns'
            ]
            
            for phrase in investment_advice_phrases:
                if phrase in full_text:
                    score -= 2.0
            
            # Objective tone check
            subjective_phrases = [
                'certainly', 'definitely', 'undoubtedly', 'absolutely',
                'best', 'worst', 'perfect'
            ]
            
            for phrase in subjective_phrases:
                if phrase in full_text:
                    score -= 0.5
            
            # Disclaimer check
            disclaimer_keywords = [
                'investment decision', 'professional consultation', 'risk', 'careful'
            ]
            
            disclaimer_present = any(keyword in full_text for keyword in disclaimer_keywords)
            if not disclaimer_present:
                score -= 1.0
            
            return max(0.0, min(10.0, score))
            
        except Exception as e:
            self.logger.error(f"Compliance review failed: {e}")
            return 8.0
    
    async def _analyze_engagement(self, article: Dict[str, Any]) -> float:
        """Engagement analysis"""
        
        score = 7.0
        
        try:
            title = article.get('title', '')
            lead = article.get('lead', '')
            body = article.get('body', '')
            
            # Title effectiveness
            if title:
                # Contains numbers or specific info
                if any(char.isdigit() for char in title):
                    score += 0.5
                
                # Appropriate length (20-60 chars)
                if 20 <= len(title) <= 60:
                    score += 0.5
                
                # Emotional words
                emotional_words = ['surge', 'plunge', 'attention', 'interest', 'shock', 'remarkable']
                if any(word in title for word in emotional_words):
                    score += 0.3
            
            # Lead strength
            if lead:
                # Key information inclusion
                key_info = ['%', 'x', '$', 'points']
                if any(info in lead for info in key_info):
                    score += 0.5
                
                # Appropriate length
                if 50 <= len(lead) <= 150:
                    score += 0.3
            
            # Body flow
            if body:
                # Paragraph separation
                paragraphs = body.split('\n')
                if len(paragraphs) >= 3:
                    score += 0.5
                
                # Connector usage
                connectors = ['however', 'also', 'therefore', 'meanwhile', 'consequently']
                connector_count = sum(1 for conn in connectors if conn in body)
                score += min(1.0, connector_count * 0.2)
            
            return max(0.0, min(10.0, score))
            
        except Exception as e:
            self.logger.error(f"Engagement analysis failed: {e}")
            return 7.0
    
    async def _calculate_overall_score(self, scores: Dict[str, float]) -> float:
        """Calculate overall score"""
        
        try:
            weighted_score = 0.0
            
            for criterion, weight_info in self.review_criteria.items():
                weight = weight_info['weight']
                score_key = {
                    'content_accuracy': 'accuracy',
                    'readability': 'readability',
                    'completeness': 'completeness',
                    'compliance': 'compliance',
                    'engagement': 'engagement'
                }.get(criterion, criterion)
                
                score = scores.get(score_key, 7.0)
                weighted_score += score * weight
            
            return round(weighted_score, 1)
            
        except Exception as e:
            self.logger.error(f"Overall score calculation failed: {e}")
            return 7.0
    
    async def _suggest_improvements(self, article: Dict[str, Any], scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """Suggest improvements"""
        
        improvements = []
        
        try:
            # Suggest improvements per area
            if scores.get('accuracy', 8.0) < 7.0:
                improvements.append({
                    'category': 'content_accuracy',
                    'priority': 'high',
                    'suggestion': 'Check data consistency and fix inaccurate expressions.',
                    'details': 'Please review consistency between numerical information and analysis results.'
                })
            
            if scores.get('readability', 8.0) < 7.0:
                improvements.append({
                    'category': 'readability',
                    'priority': 'medium',
                    'suggestion': 'Adjust sentence length and reduce technical jargon.',
                    'details': 'Keep average sentence length to 15-25 words and use accessible language.'
                })
            
            if scores.get('completeness', 8.0) < 7.0:
                improvements.append({
                    'category': 'completeness',
                    'priority': 'high',
                    'suggestion': 'Add required information and complete the structure.',
                    'details': 'Improve completeness of title, lead, body, and conclusion. Include key information.'
                })
            
            if scores.get('compliance', 8.0) < 8.0:
                improvements.append({
                    'category': 'compliance',
                    'priority': 'critical',
                    'suggestion': 'Remove investment advice expressions and maintain an objective tone.',
                    'details': 'Avoid investment recommendation phrasing and include a disclaimer.'
                })
            
            if scores.get('engagement', 8.0) < 6.0:
                improvements.append({
                    'category': 'engagement',
                    'priority': 'low',
                    'suggestion': 'Increase the appeal of the title and lead.',
                    'details': 'Include specific figures and use engaging expressions.'
                })
            
            return improvements
            
        except Exception as e:
            self.logger.error(f"Improvement suggestion failed: {e}")
            return [{
                'category': 'general',
                'priority': 'medium',
                'suggestion': 'Review overall article quality.',
                'details': 'Please verify the accuracy and completeness of the content.'
            }]
