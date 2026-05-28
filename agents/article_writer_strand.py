"""
Article Writing Strand Agent
Write economic articles based on events and data analysis
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from .strands_framework import BaseStrandAgent, StrandContext, StrandMessage, MessageType

class ArticleWriterStrand(BaseStrandAgent):
    """Article Writing Strand Agent"""
    
    def __init__(self):
        super().__init__(
            agent_id="article_writer",
            name="Article Writer Agent"
        )
        
        self.capabilities = [
            "economic_article_writing",
            "market_analysis_writing",
            "technical_analysis_writing",
            "news_summarization",
            "content_structuring"
        ]
        
        # Article templates
        self.article_templates = {
            'price_change': {
                'title_template': "{symbol} {direction} {change_percent:.1f}%, {impact_description}",
                'lead_template': "{symbol} recorded {change_percent:+.2f}% {direction} at {timestamp}, drawing market attention.",
                'focus_areas': ['Price change causes', 'Market reaction', 'Technical analysis', 'Future outlook']
            },
            'volume_spike': {
                'title_template': "{symbol} Trading Volume Surge, {volume_ratio:.1f}x Increase",
                'lead_template': "{symbol} trading volume surged {volume_ratio:.1f}x above average, showing abnormal trading patterns.",
                'focus_areas': ['Volume surge causes', 'Institutional investor trends', 'Market sentiment', 'Stock price impact']
            },
            'high_volatility': {
                'title_template': "{symbol} High Volatility, {volatility:.1f}% Recorded",
                'lead_template': "{symbol} shows high volatility of {volatility:.1f}%, drawing investor attention.",
                'focus_areas': ['Volatility causes', 'Market instability factors', 'Investment strategy', 'Risk management']
            }
        }
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return self.capabilities
    
    async def process(self, context: StrandContext, message: Optional[StrandMessage] = None) -> Dict[str, Any]:
        """Process article writing"""
        
        # Collect required data
        event_data = context.input_data.get('event')
        data_analysis = await self.get_shared_data(context, 'data_analysis')
        
        if not event_data:
            raise Exception("No event data")
        
        symbol = event_data.get('symbol')
        self.logger.info(f"✍️ {symbol} article writing started")
        
        try:
            # 1. Create article structure
            article_structure = await self._create_article_structure(event_data, data_analysis)
            
            # 2. Generate article content
            article_content = await self._generate_article_content(article_structure, event_data, data_analysis)
            
            # 3. Create article metadata
            article_metadata = await self._create_article_metadata(event_data, article_content)
            
            # 4. Create final article package
            article_package = {
                'title': article_content['title'],
                'lead': article_content['lead'],
                'body': article_content['body'],
                'conclusion': article_content['conclusion'],
                'metadata': article_metadata,
                'word_count': len(article_content['body'].split()),
                'created_at': datetime.now().isoformat(),
                'symbol': symbol,
                'event_type': event_data.get('event_type')
            }
            
            # Save to shared memory
            await self.set_shared_data(context, 'article', article_package)
            
            self.logger.info(f"✅ {symbol} article writing completed ({article_package['word_count']} words)")
            return article_package
            
        except Exception as e:
            self.logger.error(f"❌ Article writing failed: {e}")
            raise
    
    async def _create_article_structure(self, event_data: Dict[str, Any], data_analysis: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Create article structure"""
        
        event_type = event_data.get('event_type', 'unknown')
        symbol = event_data.get('symbol', 'Unknown')
        
        # Select template
        template = self.article_templates.get(event_type, self.article_templates['price_change'])
        
        # Base structure
        structure = {
            'event_type': event_type,
            'symbol': symbol,
            'template': template,
            'sections': [
                'title',
                'lead',
                'event_description',
                'data_analysis',
                'technical_analysis',
                'market_impact',
                'conclusion'
            ]
        }
        
        # Include additional sections if data analysis is available
        if data_analysis:
            structure['sections'].extend(['chart_analysis', 'statistical_insights'])
        
        return structure
    
    async def _generate_article_content(self, structure: Dict[str, Any], event_data: Dict[str, Any], data_analysis: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate article content"""
        
        symbol = event_data.get('symbol', 'Unknown')
        event_type = event_data.get('event_type', 'unknown')
        
        # System prompt
        system_prompt = self._create_system_prompt()
        
        # Create user prompt
        user_prompt = await self._create_user_prompt(structure, event_data, data_analysis)
        
        # Call LLM
        if self.llm:
            try:
                article_text = await self.call_llm(system_prompt, user_prompt)
                
                # Parse article
                parsed_article = await self._parse_article_response(article_text)
                return parsed_article
                
            except Exception as e:
                self.logger.error(f"LLM call failed: {e}")
                # Fallback: template-based article generation
                return await self._generate_template_article(structure, event_data, data_analysis)
        else:
            # Generate using template if no LLM available
            return await self._generate_template_article(structure, event_data, data_analysis)
    
    def _create_system_prompt(self) -> str:
        """Create system prompt"""
        return """You are a professional economic journalist. Please write accurate and objective economic articles based on the given economic events and data analysis.

Article writing guidelines:
1. Deliver objective and accurate information
2. Professional yet easy-to-understand writing style
3. Content based on data and analysis
4. Avoid investment advice and focus on providing information
5. Write in English
6. Write detailed articles of at least 2000 characters
7. Include background explanation, market analysis, expert opinions, and future outlook

Article structure:
- Title: Concise title capturing the core message
- Lead: First paragraph summarizing key content (100-150 characters)
- Body: Detailed analysis and explanation (1500+ characters)
  * Event background and cause analysis
  * Market data and technical analysis
  * Industry trends and impact analysis
  * Related companies and sector impact
  * Investor reaction and market sentiment
  * Expert analysis and opinions
- Conclusion: Summary and implications (200-300 characters)

Response format:
TITLE: [title]
LEAD: [lead paragraph]
BODY: [body - minimum 1500 characters]
CONCLUSION: [conclusion]
IMAGE_PROMPT: [image generation prompt based on article content - write in English]"""
    
    async def _create_user_prompt(self, structure: Dict[str, Any], event_data: Dict[str, Any], data_analysis: Optional[Dict[str, Any]]) -> str:
        """Create user prompt"""
        
        symbol = event_data.get('symbol', 'Unknown')
        event_type = event_data.get('event_type', 'unknown')
        description = event_data.get('description', '')
        severity = event_data.get('severity', 'low')
        
        prompt = f"""Please write an article about the following economic event:

=== Event Information ===
Symbol: {symbol}
Event Type: {event_type}
Description: {description}
Severity: {severity}
Timestamp: {event_data.get('timestamp', 'Unknown')}
"""
        
        # Additional event data
        if 'change_percent' in event_data:
            prompt += f"Change: {event_data['change_percent']:.2f}%\n"
        
        # Add data analysis information
        if data_analysis:
            prompt += "\n=== Data Analysis Results ===\n"
            
            # Raw data
            raw_data = data_analysis.get('raw_data', {})
            if raw_data:
                prompt += f"Current Price: {raw_data.get('current_price', 'N/A')}\n"
                prompt += f"Volume: {raw_data.get('volume', 'N/A')}\n"
            
            # Technical indicators
            technical = data_analysis.get('technical_indicators', {})
            if technical:
                prompt += "\nTechnical Indicators:\n"
                if technical.get('rsi'):
                    prompt += f"- RSI: {technical['rsi']:.1f}\n"
                if technical.get('sma_20'):
                    prompt += f"- 20-day SMA: {technical['sma_20']:.2f}\n"
                if technical.get('macd'):
                    prompt += f"- MACD: {technical['macd']:.2f}\n"
            
            # Statistics
            stats = data_analysis.get('statistics', {})
            if stats:
                prompt += "\nStatistics:\n"
                if stats.get('volatility_annualized'):
                    prompt += f"- Annualized Volatility: {stats['volatility_annualized']:.1f}%\n"
                if stats.get('volume_ratio'):
                    prompt += f"- Volume Ratio: {stats['volume_ratio']:.1f}x\n"
            
            # Market comparison
            market_comp = data_analysis.get('market_comparison', {})
            if market_comp:
                prompt += "\nMarket Comparison:\n"
                if market_comp.get('beta'):
                    prompt += f"- Beta: {market_comp['beta']:.2f}\n"
                if market_comp.get('correlation_with_spy'):
                    prompt += f"- SPY Correlation: {market_comp['correlation_with_spy']:.2f}\n"
        
        prompt += "\nPlease write a professional and objective economic article based on the above information."
        
        return prompt
    
    async def _parse_article_response(self, article_text: str) -> Dict[str, Any]:
        """Parse LLM response"""
        
        try:
            lines = article_text.strip().split('\n')
            
            title = ""
            lead = ""
            body = ""
            conclusion = ""
            image_prompt = ""
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith('TITLE:'):
                    title = line.replace('TITLE:', '').strip()
                    current_section = 'title'
                elif line.startswith('LEAD:'):
                    lead = line.replace('LEAD:', '').strip()
                    current_section = 'lead'
                elif line.startswith('BODY:'):
                    body = line.replace('BODY:', '').strip()
                    current_section = 'body'
                elif line.startswith('CONCLUSION:'):
                    conclusion = line.replace('CONCLUSION:', '').strip()
                    current_section = 'conclusion'
                elif line.startswith('IMAGE_PROMPT:'):
                    image_prompt = line.replace('IMAGE_PROMPT:', '').strip()
                    current_section = 'image_prompt'
                else:
                    # Add content to current section
                    if current_section == 'lead' and lead:
                        lead += " " + line
                    elif current_section == 'body' and body:
                        body += " " + line
                    elif current_section == 'conclusion' and conclusion:
                        conclusion += " " + line
                    elif current_section == 'image_prompt' and image_prompt:
                        image_prompt += " " + line
            
            return {
                'title': title or "Fundamental Agent",
                'lead': lead or "An economic event has occurred.",
                'body': body or "Detailed analysis is in progress.",
                'conclusion': conclusion or "Continuous monitoring is required.",
                'image_prompt': image_prompt or "economic news, financial market, stock chart"
            }
            
        except Exception as e:
            self.logger.error(f"Article parsing failed: {e}")
            return await self._generate_fallback_article()
    
    async def _generate_template_article(self, structure: Dict[str, Any], event_data: Dict[str, Any], data_analysis: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate template-based article"""
        
        symbol = event_data.get('symbol', 'Unknown')
        event_type = event_data.get('event_type', 'unknown')
        template = structure.get('template', self.article_templates['price_change'])
        
        # Base variables
        variables = {
            'symbol': symbol,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'direction': 'rise' if event_data.get('change_percent', 0) > 0 else 'fall',
            'change_percent': abs(event_data.get('change_percent', 0)),
            'impact_description': 'Market attention focus',
            'volume_ratio': 1.0,
            'volatility': 10.0
        }
        
        # Extract additional variables from data analysis
        if data_analysis:
            stats = data_analysis.get('statistics', {})
            if stats.get('volume_ratio'):
                variables['volume_ratio'] = stats['volume_ratio']
            if stats.get('volatility_annualized'):
                variables['volatility'] = stats['volatility_annualized'] * 100
        
        # Generate title
        try:
            title = template['title_template'].format(**variables)
        except:
            title = f"{symbol} Market Trend"
        
        # Generate lead
        try:
            lead = template['lead_template'].format(**variables)
        except:
            lead = f"Market interest in {symbol} is increasing."
        
        # Generate body
        body = await self._generate_template_body(event_data, data_analysis, template)
        
        # Generate conclusion
        conclusion = await self._generate_template_conclusion(event_data, data_analysis)
        
        return {
            'title': title,
            'lead': lead,
            'body': body,
            'conclusion': conclusion
        }
    
    async def _generate_template_body(self, event_data: Dict[str, Any], data_analysis: Optional[Dict[str, Any]], template: Dict[str, Any]) -> str:
        """Generate template-based body (2000+ characters)"""
        
        symbol = event_data.get('symbol', 'Unknown')
        body_parts = []
        
        # 1. Event overview and background
        body_parts.append("## 📊 Event Overview")
        if event_data.get('description'):
            body_parts.append(f"{event_data['description']} This movement is drawing attention from market participants and is analyzed as the result of multiple factors working in combination.")
        
        # 2. Current market situation analysis
        body_parts.append("\n\n## 💹 Current Market Situation")
        if data_analysis:
            raw_data = data_analysis.get('raw_data', {})
            if raw_data.get('current_price'):
                body_parts.append(f"{symbol} is currently trading at ${raw_data['current_price']:.2f}. This level has been receiving continuous attention since market open.")
            
            if raw_data.get('volume'):
                body_parts.append(f"Today's trading volume is {raw_data['volume']:,} shares, indicating more active trading than usual.")
        
        # 3. Technical analysis detail
        body_parts.append("\n\n## 📈 Technical Analysis")
        if data_analysis:
            technical = data_analysis.get('technical_indicators', {})
            if technical:
                body_parts.append("The comprehensive analysis of key technical indicators is as follows.")
                
                if technical.get('rsi'):
                    rsi = technical['rsi']
                    if rsi > 70:
                        body_parts.append(f"The RSI indicator has entered the overbought zone at {rsi:.1f}. This suggests short-term correction pressure may be imminent, indicating a need for cautious approach.")
                    elif rsi < 30:
                        body_parts.append(f"The RSI indicator is in the oversold zone at {rsi:.1f}. This presents a potential technical rebound opportunity, which could be interpreted as a buying opportunity.")
                    else:
                        body_parts.append(f"The RSI indicator is in the neutral zone at {rsi:.1f}, showing a technically balanced state.")
                
                if technical.get('sma_20'):
                    current_price = technical.get('current_price', 0)
                    sma_20 = technical['sma_20']
                    if current_price > sma_20:
                        body_parts.append(f"Trading above the 20-day moving average (${sma_20:.2f}) maintains the short-term uptrend. This is interpreted as a signal reflecting positive investor sentiment.")
                    else:
                        body_parts.append(f"Trading below the 20-day moving average (${sma_20:.2f}) shows short-term weakness. Caution against additional downward pressure is warranted.")
                
                if technical.get('macd') and technical.get('macd_signal'):
                    macd = technical['macd']
                    macd_signal = technical['macd_signal']
                    if macd > macd_signal:
                        body_parts.append(f"The MACD indicator shows the main line ({macd:.2f}) crossing above the signal line ({macd_signal:.2f}), generating a buy signal.")
                    else:
                        body_parts.append(f"The MACD indicator shows the main line ({macd:.2f}) positioned below the signal line ({macd_signal:.2f}), indicating a bearish signal.")
        
        # 4. Market comparison and relative performance
        body_parts.append("\n\n## 🔄 Market Comparison Analysis")
        if data_analysis:
            market_comp = data_analysis.get('market_comparison', {})
            if market_comp:
                body_parts.append("Let us examine relative performance through comparison with major market indices.")
                
                if market_comp.get('beta'):
                    beta = market_comp['beta']
                    if beta > 1:
                        body_parts.append(f"With a beta of {beta:.2f}, it shows higher volatility than the market. This means it may show larger gains during market upswings and larger losses during downturns.")
                    elif beta < 1:
                        body_parts.append(f"With a beta of {beta:.2f}, it shows stable movements relative to the market. This may be suitable for investors with relatively conservative investment preferences.")
                
                if market_comp.get('correlation_with_spy'):
                    correlation = market_comp['correlation_with_spy']
                    if abs(correlation) > 0.7:
                        body_parts.append(f"The correlation with the S&P 500 index is {correlation:.2f}, showing {'high positive correlation' if correlation > 0 else 'high negative correlation'}.")
                    else:
                        body_parts.append(f"The correlation with the S&P 500 index is {correlation:.2f}, showing relatively independent movements, which may provide portfolio diversification benefits.")
        
        # 5. Statistical analysis and volatility
        body_parts.append("\n\n## 📊 Statistical Analysis")
        if data_analysis:
            stats = data_analysis.get('statistics', {})
            if stats:
                if stats.get('volatility_annualized'):
                    vol = stats['volatility_annualized'] * 100
                    if vol > 30:
                        body_parts.append(f"Annualized volatility is {vol:.1f}%, recording a high level. This suggests the possibility of significant short-term price movements, requiring special attention to risk management.")
                    elif vol > 20:
                        body_parts.append(f"Annualized volatility is {vol:.1f}%, showing a moderate level. This is assessed as providing an appropriate level of risk and return opportunities.")
                    else:
                        body_parts.append(f"Annualized volatility is {vol:.1f}%, maintaining a low level, providing a relatively stable investment environment.")
                
                if stats.get('volume_ratio') and stats['volume_ratio'] > 1.5:
                    volume_ratio = stats['volume_ratio']
                    body_parts.append(f"The volume increase of {volume_ratio:.1f}x compared to the average is a signal showing both increased institutional investor interest and active retail investor participation. This volume increase provides important clues about future price direction.")
        
        # 6. Industry trends and impact factors
        body_parts.append("\n\n## 🏢 Industry Trends and Impact Factors")
        body_parts.append(f"The industry that {symbol} belongs to is currently being influenced by various internal and external factors. Changes in the macroeconomic environment, industry characteristics, and individual company fundamentals are all working in combination.")
        
        # 7. Investor sentiment and market reaction
        body_parts.append("\n\n## 💭 Investor Sentiment and Market Reaction")
        body_parts.append("Overall market participant reactions show a mix of short-term wait-and-see approaches and simultaneous moves to seek mid-to-long-term investment opportunities. Institutional investors are showing a cautious approach based on fundamental analysis, while retail investors are observed to be more sensitive to technical analysis and market momentum.")
        
        # 8. Risk factors and precautions
        body_parts.append("\n\n## ⚠️ Risk Factors and Precautions")
        body_parts.append("Key risk factors to consider when investing include macroeconomic uncertainty, intensifying industry competition, regulatory environment changes, and global economic trends. Position sizing and risk management are especially important in the current high-volatility market environment.")
        
        return "\n".join(body_parts)
    
    async def _generate_template_conclusion(self, event_data: Dict[str, Any], data_analysis: Optional[Dict[str, Any]]) -> str:
        """Generate template-based conclusion"""
        
        symbol = event_data.get('symbol', 'Unknown')
        event_type = event_data.get('event_type', 'unknown')
        
        conclusions = []
        
        # Event type specific conclusions
        if event_type == 'volume_spike':
            conclusions.append(f"The surge in {symbol} trading volume indicates increased market participant interest.")
        elif event_type == 'price_change':
            change = event_data.get('change_percent', 0)
            if abs(change) > 5:
                conclusions.append(f"{symbol}'s {'surge' if change > 0 else 'sharp decline'} is drawing investor attention.")
        elif event_type == 'high_volatility':
            conclusions.append(f"{symbol}'s high volatility reflects market uncertainty.")
        
        # General conclusion
        conclusions.append("Investors are advised to make careful investment decisions through thorough analysis and risk management.")
        
        return " ".join(conclusions)
    
    async def _generate_fallback_article(self) -> Dict[str, Any]:
        """Generate fallback article (2000+ characters)"""
        
        body = """## 📊 Market Overview

Notable movements are being observed in the economic market. Market participants are currently reacting sensitively to various economic indicators, corporate earnings, and macroeconomic environment changes.

## 💹 Current Market Situation

Global financial markets are showing volatility under the influence of multiple complex factors. Central bank monetary policy directions, inflation trends, and geopolitical risks are analyzed to be affecting market sentiment.

Investors are paying more attention to mid-to-long-term fundamental factors rather than short-term market noise, which is interpreted as a positive signal for creating a healthy investment environment.

## 📈 Technical Analysis

Comprehensive analysis of key technical indicators suggests that the market is currently in a phase of seeking direction. The arrangement of moving averages and momentum indicator movements can provide clues about future market direction.

In particular, changes in trading volume patterns serve as important indicators reflecting shifts in market participant sentiment, and are expected to help predict future market flows.

## 🔄 Market Comparison Analysis

Evaluating relative performance through comparison with major domestic and international market indices shows different characteristics and movements across markets. This is analyzed to stem from differences in regional economic conditions and policy environments.

## 🏢 Industry Trends

Different industries are showing varying performance, which appears to result from differences in industry characteristics and sensitivity to market environment changes. The performance gap between technology stocks and traditional value stocks is particularly notable.

## 💭 Investor Sentiment

Investors are currently taking a cautious approach, which is interpreted as a natural phenomenon in uncertain market environments. Institutional investors are seeking long-term investment opportunities, while retail investors are observed to be paying more attention to risk management.

## ⚠️ Risk Factors

Key risk factors to consider when investing include macroeconomic uncertainty, geopolitical risks, and potential monetary policy changes. These factors can increase market volatility, and investors should prepare adequate countermeasures.

## 📊 Expert Opinions

Market experts are expressing cautious optimism about the current situation. While volatility may persist in the short term, they forecast a stable growth trajectory in the mid-to-long term along with fundamental improvements.

## 🎯 Future Outlook

Future market outlook may vary depending on multiple variables, but overall is expected to show gradual recovery. However, temporary corrections and volatility are likely unavoidable in this process, and investors need to be adequately prepared."""
        
        return {
            'title': "Economic Market Comprehensive Analysis",
            'lead': "Notable movements are being observed in the economic market, with various factors appearing to complexly influence the current market situation.",
            'body': body,
            'conclusion': "In summary of the current market situation, while short-term uncertainty exists, mid-to-long-term stable growth potential is evident. Investors need to respond to market changes through careful investment approaches and systematic risk management, and consultation with experts is recommended for investment decisions.",
            'image_prompt': "professional financial market analysis, economic charts, business growth, modern financial illustration"
        }
    
    async def _create_article_metadata(self, event_data: Dict[str, Any], article_content: Dict[str, Any]) -> Dict[str, Any]:
        """Create article metadata"""
        
        return {
            'author': 'Fundamental Agent',
            'category': 'Economy',
            'tags': [
                event_data.get('symbol', 'market'),
                event_data.get('event_type', 'analysis'),
                'economic_news',
                'market_analysis'
            ],
            'language': 'en',
            'source': 'Fundamental Agent System',
            'confidence_score': 0.85,
            'reading_time_minutes': max(1, len(article_content.get('body', '').split()) // 200)
        }
