#!/usr/bin/env python3
"""
Practical AI Article Generation System
Real working article generation using DeepSeek API
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from openai import OpenAI
import yfinance as yf


DEEPSEEK_BASE_URL = "https://api.deepseek.com"
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random

class SimpleAIArticleGenerator:
    """Simple and practical AI article generator"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Initialize DeepSeek API client
        self.deepseek_client = None
        api_key = os.environ.get('DEEPSEEK_API_KEY')
        if api_key:
            self.deepseek_client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)
            self.logger.info("✅ DeepSeek client initialized")
        else:
            self.logger.warning("⚠️ DEEPSEEK_API_KEY environment variable not set")

        self.model_id = "deepseek-v4-flash"

    def analyze_events(self, events: List[Dict]) -> Dict[str, Any]:
        """Analyze event data"""
        try:
            self.logger.info("📊 Event data analysis started")

            analysis = {
                'total_events': len(events),
                'event_summary': [],
                'market_sentiment': 'neutral',
                'key_symbols': [],
                'price_changes': [],
                'analysis_time': datetime.now().isoformat()
            }

            positive_events = 0
            negative_events = 0

            for event in events:
                symbol = event.get('symbol', 'Unknown')
                description = event.get('description', '')
                sentiment = event.get('sentiment', 'neutral')

                analysis['event_summary'].append({
                    'symbol': symbol,
                    'description': description,
                    'sentiment': sentiment
                })

                analysis['key_symbols'].append(symbol)

                # Use change_percent if available, otherwise try to extract from description
                change_percent = event.get('change_percent')
                if change_percent is not None:
                    analysis['price_changes'].append({
                        'symbol': symbol,
                        'change': change_percent
                    })
                else:
                    # Try to extract percentage from description
                    import re
                    percent_match = re.search(r'([-+]?\d+\.?\d*)%', description)
                    if percent_match:
                        try:
                            change_value = float(percent_match.group(1))
                            analysis['price_changes'].append({
                                'symbol': symbol,
                                'change': change_value
                            })
                        except ValueError:
                            pass

                if sentiment == 'positive':
                    positive_events += 1
                elif sentiment == 'negative':
                    negative_events += 1

            # Determine overall market sentiment
            if positive_events > negative_events:
                analysis['market_sentiment'] = 'bullish'
            elif negative_events > positive_events:
                analysis['market_sentiment'] = 'bearish'
            else:
                analysis['market_sentiment'] = 'neutral'

            # Remove duplicates
            analysis['key_symbols'] = list(set(analysis['key_symbols']))

            self.logger.info(f"✅ Analysis complete: {len(events)} events, sentiment: {analysis['market_sentiment']}")
            return analysis

        except Exception as e:
            self.logger.error(f"❌ Event analysis failed: {str(e)}")
            return {
                'total_events': len(events) if events else 0,
                'event_summary': [],
                'market_sentiment': 'neutral',
                'key_symbols': [],
                'price_changes': [],
                'analysis_time': datetime.now().isoformat(),
                'error': str(e)
            }

    def generate_article_with_deepseek(self, events: List[Dict], analysis: Dict) -> Dict[str, Any]:
        """Generate article using DeepSeek"""
        try:
            self.logger.info("✍️ DeepSeek article generation started")

            if not self.deepseek_client:
                return self._generate_fallback_article(events, analysis)

            # Generate prompt
            prompt = self._create_article_prompt(events, analysis)

            # Call DeepSeek API
            response = self.deepseek_client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7
            )

            article_content = response.choices[0].message.content or ""

            # Structure the article
            article = self._structure_article(article_content, events, analysis)

            self.logger.info("✅ DeepSeek article generation complete")
            return article

        except Exception as e:
            self.logger.error(f"❌ DeepSeek article generation failed: {str(e)}")
            return self._generate_fallback_article(events, analysis)

    def _create_article_prompt(self, events: List[Dict], analysis: Dict) -> str:
        """Generate article prompt (2000+ characters)"""

        # Event summary
        event_descriptions = []
        for event in events:
            event_descriptions.append(f"- {event.get('description', '')}")

        events_text = "\n".join(event_descriptions)

        prompt = f"""
You are a professional economic journalist. Write an in-depth economic news article in English based on the following market events.

**Detected Market Events:**
{events_text}

**Market Analysis Info:**
- Total events: {analysis.get('total_events', 0)}
- Market sentiment: {analysis.get('market_sentiment', 'neutral')}
- Key symbols: {', '.join(analysis.get('key_symbols', [])[:5])}
- Price changes: {analysis.get('price_changes', [])}

**Article Requirements (minimum 2000 characters):**

1. **Title (50 chars max)**: Engaging and accurate headline

2. **Lead paragraph (150-200 chars)**:
   - First paragraph summarizing key content
   - Include 5W1H

3. **Body paragraph 1 - Current Situation Analysis (400-500 chars)**:
   - Detailed analysis of current market conditions
   - Present specific figures and data
   - Explain movements of key symbols

4. **Body paragraph 2 - Cause Analysis (400-500 chars)**:
   - Analyze fundamental causes of market changes
   - Consider macroeconomic factors
   - Include industry expert perspectives

5. **Body paragraph 3 - Ripple Effects (400-500 chars)**:
   - Impact on other sectors/markets
   - Reactions of related symbols
   - Connection to global markets

6. **Body paragraph 4 - Outlook and Analysis (400-500 chars)**:
   - Short/medium-term outlook
   - Key variables and risk factors
   - Scenario-based analysis

7. **Conclusion (200-300 chars)**:
   - Key takeaways for investors
   - Cautions and investment strategy suggestions

**Writing Style:**
- Objective and professional tone
- Use specific figures and data
- Language accessible to investors
- Avoid excessive speculation or definitive statements
- Each paragraph must be logically connected
- Provide rich background information and context
- **Write at least 2000 characters** (very important!)

**Important: Adhere to the minimum character count for each section:**
- Lead paragraph: minimum 150 chars
- Body paragraph 1: minimum 400 chars
- Body paragraph 2: minimum 400 chars
- Body paragraph 3: minimum 400 chars
- Body paragraph 4: minimum 400 chars
- Conclusion: minimum 250 chars

**Write in the following format:**

Title: [Article Title]

Lead: [Lead paragraph of 150+ chars]

Body1: [Current situation analysis of 400+ chars]

Body2: [Cause analysis of 400+ chars]

Body3: [Ripple effect analysis of 400+ chars]

Body4: [Outlook and analysis of 400+ chars]

Conclusion: [Conclusion of 250+ chars]

**Caution: The entire article must be at least 2000 characters. Strictly adhere to the minimum character count for each section.**

Tags: [5 relevant keywords separated by commas]
"""

        return prompt

    def _structure_article(self, content: str, events: List[Dict], analysis: Dict) -> Dict[str, Any]:
        """Structure the article content"""

        try:
            # Default structure
            article = {
                'title': '',
                'lead': '',
                'content': '',
                'conclusion': '',
                'tags': [],
                'metadata': {
                    'events_count': len(events),
                    'market_sentiment': analysis.get('market_sentiment', 'neutral'),
                    'key_symbols': analysis.get('key_symbols', []),
                    'generated_at': datetime.now().isoformat(),
                    'word_count': len(content.split())
                }
            }

            # Parse content
            lines = content.strip().split('\n')
            current_section = None

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if line.startswith('Title:'):
                    article['title'] = line.replace('Title:', '').strip()
                elif line.startswith('Lead:'):
                    article['lead'] = line.replace('Lead:', '').strip()
                elif line.startswith('Body1:'):
                    current_section = 'content'
                    article['content'] = line.replace('Body1:', '').strip()
                elif line.startswith('Body2:'):
                    if article['content']:
                        article['content'] += '\n\n' + line.replace('Body2:', '').strip()
                    else:
                        article['content'] = line.replace('Body2:', '').strip()
                elif line.startswith('Body3:'):
                    if article['content']:
                        article['content'] += '\n\n' + line.replace('Body3:', '').strip()
                    else:
                        article['content'] = line.replace('Body3:', '').strip()
                elif line.startswith('Body4:'):
                    if article['content']:
                        article['content'] += '\n\n' + line.replace('Body4:', '').strip()
                    else:
                        article['content'] = line.replace('Body4:', '').strip()
                elif line.startswith('Conclusion:'):
                    article['conclusion'] = line.replace('Conclusion:', '').strip()
                elif line.startswith('Tags:'):
                    tags_text = line.replace('Tags:', '').strip()
                    article['tags'] = [tag.strip() for tag in tags_text.split(',')]

            # Set defaults
            if not article['title']:
                article['title'] = f"Market Trends: {', '.join(analysis.get('key_symbols', ['Key Stocks'])[:3])} Analysis"

            if not article['lead']:
                article['lead'] = f"Today, {analysis.get('total_events', 0)} major market events were detected."

            if not article['content']:
                article['content'] = content

            if not article['tags']:
                article['tags'] = ['Market Analysis', 'Stocks', 'Investment', 'Fundamental Agent', 'Market Trends']

            return article

        except Exception as e:
            self.logger.error(f"Article structuring failed: {str(e)}")
            return {
                'title': f"Market Analysis: {datetime.now().strftime('%Y-%m-%d')}",
                'lead': f"Analysis of {len(events)} market events",
                'content': content,
                'conclusion': "Careful review is required when making investment decisions.",
                'tags': ['Market Analysis', 'Stocks', 'Investment'],
                'metadata': {
                    'events_count': len(events),
                    'generated_at': datetime.now().isoformat(),
                    'word_count': len(content.split())
                }
            }

    def _generate_fallback_article(self, events: List[Dict], analysis: Dict) -> Dict[str, Any]:
        """Generate fallback article when DeepSeek is unavailable"""

        self.logger.info("📝 Fallback article generation started")

        # Generate article based on basic template
        symbols = analysis.get('key_symbols', ['Market'])[:3]
        sentiment = analysis.get('market_sentiment', 'neutral')

        sentiment_text = {
            'bullish': 'uptrend',
            'bearish': 'downtrend',
            'neutral': 'mixed'
        }.get(sentiment, 'mixed')

        title = f"{', '.join(symbols)} and Other Key Stocks Continue {sentiment_text}"

        lead = f"Today, {analysis.get('total_events', 0)} major market events were detected, showing a {sentiment_text}."

        # Generate event-based content
        content_parts = []

        for event in events[:3]:  # Top 3 events only
            symbol = event.get('symbol', 'Unknown')
            description = event.get('description', '')

            if 'change_percent' in event:
                change = event['change_percent']
                if change > 0:
                    content_parts.append(f"{symbol} rose {change:.2f}%, showing strength.")
                else:
                    content_parts.append(f"{symbol} fell {abs(change):.2f}%, showing weakness.")
            else:
                content_parts.append(f"{symbol}: {description} situation occurred.")

        content = "\n\n".join(content_parts)

        if not content:
            content = "Various events are occurring in today's market, drawing investors' attention. Each stock shows different movements, with the overall market displaying a mixed trend."

        conclusion = "Investors are advised to carefully consider each stock's fundamentals and overall market conditions before making investment decisions."

        return {
            'title': title,
            'lead': lead,
            'content': content,
            'conclusion': conclusion,
            'tags': ['Market Analysis', 'Stocks', 'Investment', 'Fundamental Agent'] + symbols,
            'metadata': {
                'events_count': len(events),
                'market_sentiment': sentiment,
                'key_symbols': symbols,
                'generated_at': datetime.now().isoformat(),
                'generation_method': 'template_based',
                'word_count': len(content.split())
            }
        }

    def create_simple_charts(self, events: List[Dict], analysis: Dict) -> List[Dict]:
        """Create simple charts"""
        try:
            self.logger.info("📊 Chart creation started")

            charts = []

            # 1. Price change chart
            price_changes = analysis.get('price_changes', [])
            if price_changes:
                symbols = [item['symbol'] for item in price_changes]
                changes = [item['change'] for item in price_changes]

                fig = px.bar(
                    x=symbols,
                    y=changes,
                    title="Key Stock Price Change Rate",
                    labels={'x': 'Symbol', 'y': 'Change Rate (%)'},
                    color=changes,
                    color_continuous_scale=['red', 'yellow', 'green']
                )

                charts.append({
                    'type': 'price_change',
                    'title': 'Key Stock Price Change Rate',
                    'figure': fig,
                    'description': f"Shows the price change rate of {len(symbols)} stocks."
                })

            # 2. Market sentiment pie chart
            sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
            for event in events:
                sentiment = event.get('sentiment', 'neutral')
                sentiment_counts[sentiment] += 1

            if sum(sentiment_counts.values()) > 0:
                fig = px.pie(
                    values=list(sentiment_counts.values()),
                    names=['Positive', 'Negative', 'Neutral'],
                    title="Market Sentiment Distribution"
                )

                charts.append({
                    'type': 'sentiment_distribution',
                    'title': 'Market Sentiment Distribution',
                    'figure': fig,
                    'description': "Shows the sentiment distribution of detected events."
                })

            self.logger.info(f"✅ {len(charts)} chart(s) created")
            return charts

        except Exception as e:
            self.logger.error(f"❌ Chart creation failed: {str(e)}")
            return []

    def generate_simple_review(self, article: Dict) -> Dict[str, Any]:
        """Simple article review"""
        try:
            self.logger.info("🔍 Article review started")

            review = {
                'quality_score': 0.0,
                'quality_assessment': {},
                'suggestions': [],
                'review_time': datetime.now().isoformat()
            }

            # Basic quality score calculation
            score = 5.0  # Base score

            # Title check
            title = article.get('title', '')
            if len(title) > 10:
                score += 1.0
                review['quality_assessment']['title'] = 'Appropriate length'
            else:
                review['suggestions'].append('Write a more specific title')
                review['quality_assessment']['title'] = 'Too short'

            # Content check
            content = article.get('content', '')
            word_count = len(content.split())

            if word_count > 100:
                score += 1.5
                review['quality_assessment']['content_length'] = 'Sufficient length'
            else:
                review['suggestions'].append('Write the article body in more detail')
                review['quality_assessment']['content_length'] = 'Insufficient length'

            # Tag check
            tags = article.get('tags', [])
            if len(tags) >= 3:
                score += 0.5
                review['quality_assessment']['tags'] = 'Appropriate tags'
            else:
                review['suggestions'].append('Add more relevant tags')
                review['quality_assessment']['tags'] = 'Insufficient tags'

            # Structure check
            if article.get('lead') and article.get('conclusion'):
                score += 1.0
                review['quality_assessment']['structure'] = 'Complete structure'
            else:
                review['suggestions'].append('Clearly separate the lead and conclusion')
                review['quality_assessment']['structure'] = 'Structure needs improvement'

            # Final score (out of 10)
            review['quality_score'] = min(score, 10.0)

            # Overall assessment
            if review['quality_score'] >= 8.0:
                review['overall_assessment'] = 'Excellent'
            elif review['quality_score'] >= 6.0:
                review['overall_assessment'] = 'Good'
            else:
                review['overall_assessment'] = 'Needs improvement'

            self.logger.info(f"✅ Review complete: {review['quality_score']:.1f}/10")
            return review

        except Exception as e:
            self.logger.error(f"❌ Article review failed: {str(e)}")
            return {
                'quality_score': 5.0,
                'quality_assessment': {'error': str(e)},
                'suggestions': ['An error occurred during the review process'],
                'review_time': datetime.now().isoformat()
            }

    def generate_simple_ads(self, article: Dict) -> Dict[str, Any]:
        """Simple ad recommendation"""
        try:
            self.logger.info("📢 Ad recommendation started")

            # Extract keywords from article content
            content = article.get('content', '') + ' ' + article.get('title', '')
            tags = article.get('tags', [])

            # Ad templates
            ad_templates = [
                {
                    'title': 'Smart Investment Platform',
                    'description': 'Start smarter investing with AI-based investment recommendations',
                    'keywords': ['investment', 'stock', 'portfolio'],
                    'category': 'investment_platform'
                },
                {
                    'title': 'Real-Time Market Analysis Tool',
                    'description': 'Get expert-level market analysis in real time',
                    'keywords': ['analysis', 'market', 'chart'],
                    'category': 'analysis_tool'
                },
                {
                    'title': 'Fundamental Agent Premium',
                    'description': 'Don\'t miss investment opportunities with fast and accurate economic news',
                    'keywords': ['news', 'economy', 'information'],
                    'category': 'news_service'
                },
                {
                    'title': 'Automated Trading System',
                    'description': 'Maximize profit opportunities with 24/7 automated trading',
                    'keywords': ['trading', 'automated', 'system'],
                    'category': 'trading_system'
                }
            ]

            # Calculate relevance and select ads
            recommendations = []

            for ad in ad_templates:
                relevance_score = 0.0

                # Keyword matching
                for keyword in ad['keywords']:
                    if keyword in content.lower() or keyword in ' '.join(tags).lower():
                        relevance_score += 2.0

                # Base relevance
                relevance_score += random.uniform(3.0, 7.0)

                recommendations.append({
                    'title': ad['title'],
                    'description': ad['description'],
                    'category': ad['category'],
                    'relevance_score': min(relevance_score, 10.0),
                    'click_url': f"https://example.com/{ad['category']}"
                })

            # Sort by relevance
            recommendations.sort(key=lambda x: x['relevance_score'], reverse=True)

            result = {
                'recommendations': recommendations[:3],  # Top 3 only
                'total_ads': len(recommendations),
                'generated_at': datetime.now().isoformat()
            }

            self.logger.info(f"✅ {len(result['recommendations'])} ad(s) recommended")
            return result

        except Exception as e:
            self.logger.error(f"❌ Ad recommendation failed: {str(e)}")
            return {
                'recommendations': [
                    {
                        'title': 'Investment Information Service',
                        'description': 'Providing professional investment information',
                        'category': 'general',
                        'relevance_score': 5.0,
                        'click_url': 'https://example.com'
                    }
                ],
                'total_ads': 1,
                'generated_at': datetime.now().isoformat()
            }

def main():
    """Test run"""
    logging.basicConfig(level=logging.INFO)

    generator = SimpleAIArticleGenerator()

    # Test events
    test_events = [
        {
            'type': 'price_movement',
            'symbol': 'AAPL',
            'description': 'AAPL stock price rose 2.5%',
            'severity': 0.7,
            'sentiment': 'positive',
            'change_percent': 2.5
        },
        {
            'type': 'price_movement',
            'symbol': 'TSLA',
            'description': 'TSLA stock price fell 1.8%',
            'severity': 0.6,
            'sentiment': 'negative',
            'change_percent': -1.8
        }
    ]

    print("=== Practical AI Article Generation System Test ===")

    # 1. Event analysis
    analysis = generator.analyze_events(test_events)
    print(f"\n📊 Analysis result: {analysis['market_sentiment']} sentiment")

    # 2. Article generation
    article = generator.generate_article_with_deepseek(test_events, analysis)
    print(f"\n📰 Article title: {article['title']}")
    print(f"📝 Content length: {len(article['content'])} chars")

    # 3. Chart generation
    charts = generator.create_simple_charts(test_events, analysis)
    print(f"\n📊 Charts generated: {len(charts)}")

    # 4. Review
    review = generator.generate_simple_review(article)
    print(f"\n🔍 Quality score: {review['quality_score']:.1f}/10")

    # 5. Ad recommendation
    ads = generator.generate_simple_ads(article)
    print(f"\n📢 Recommended ads: {len(ads['recommendations'])}")

    print("\n✅ Test complete!")

if __name__ == "__main__":
    main()
