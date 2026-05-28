"""
Market Sentiment Analysis Module
"""

import re
import requests
import feedparser
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import logging
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json

class SentimentScore(Enum):
    VERY_POSITIVE = "very_positive"  # 0.6 ~ 1.0
    POSITIVE = "positive"            # 0.2 ~ 0.6
    NEUTRAL = "neutral"              # -0.2 ~ 0.2
    NEGATIVE = "negative"            # -0.6 ~ -0.2
    VERY_NEGATIVE = "very_negative"  # -1.0 ~ -0.6

@dataclass
class NewsItem:
    title: str
    content: str
    source: str
    published_date: datetime
    url: str
    sentiment_score: float  # -1.0 to 1.0
    keywords: List[str]

@dataclass
class MarketSentiment:
    symbol: str
    timestamp: datetime
    overall_sentiment: SentimentScore
    sentiment_score: float  # -1.0 to 1.0
    confidence: float  # 0.0 to 1.0
    
    # News-based sentiment
    news_sentiment: float
    news_count: int
    
    # Sentiment trend
    sentiment_trend: str  # "improving", "declining", "stable"
    
    # Social media sentiment (for future expansion)
    social_sentiment: Optional[float] = None
    
    # VIX-based Fear/Greed index
    fear_greed_index: float = 50.0  # 0-100 scale
    
    # Key news items
    key_news: Optional[List[NewsItem]] = None

class SentimentAnalyzer:
    """Market sentiment analysis class"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Sentiment analysis keyword dictionary
        self.positive_keywords = {
            'surge', 'rally', 'gain', 'rise', 'up', 'bull', 'bullish', 'growth', 
            'profit', 'earnings', 'beat', 'strong', 'robust', 'solid', 'positive',
            'optimistic', 'confident', 'breakthrough', 'success', 'record', 'high',
        }
        
        self.negative_keywords = {
            'fall', 'drop', 'decline', 'crash', 'bear', 'bearish', 'loss', 'losses',
            'weak', 'poor', 'disappointing', 'concern', 'worry', 'fear', 'risk',
            'uncertainty', 'volatile', 'pressure', 'struggle', 'challenge', 'low',
        }
        
        # News feed URLs
        self.news_feeds = [
            "https://feeds.bloomberg.com/markets/news.rss",
            "https://feeds.reuters.com/reuters/businessNews",
            "https://rss.cnn.com/rss/money_latest.rss",
            "https://feeds.marketwatch.com/marketwatch/topstories/"
        ]
    
    async def analyze_market_sentiment(self, symbol: str) -> Optional[MarketSentiment]:
        """Analyze market sentiment for a specific symbol"""
        try:
            # Collect news data
            news_items = await self._collect_news_data(symbol)
            
            if not news_items:
                self.logger.warning(f"No news data found for {symbol}")
                return None
            
            # Analyze news sentiment
            news_sentiment = self._analyze_news_sentiment(news_items)
            
            # Calculate VIX-based Fear/Greed index
            fear_greed_index = await self._calculate_fear_greed_index()
            
            # Analyze sentiment trend
            sentiment_trend = self._analyze_sentiment_trend(symbol, news_sentiment)
            
            # Calculate overall sentiment score
            overall_score = self._calculate_overall_sentiment(
                news_sentiment, fear_greed_index
            )
            
            # Classify sentiment
            sentiment_category = self._classify_sentiment(overall_score)
            
            # Calculate confidence
            confidence = self._calculate_confidence(news_items, overall_score)
            
            return MarketSentiment(
                symbol=symbol,
                timestamp=datetime.now(),
                overall_sentiment=sentiment_category,
                sentiment_score=overall_score,
                confidence=confidence,
                news_sentiment=news_sentiment,
                news_count=len(news_items),
                fear_greed_index=fear_greed_index,
                sentiment_trend=sentiment_trend,
                key_news=news_items[:5]  # Store top 5 news items
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment for {symbol}: {str(e)}")
            return None
    
    async def _collect_news_data(self, symbol: str) -> List[NewsItem]:
        """Collect news data"""
        news_items = []
        
        # Collect news from RSS feeds
        for feed_url in self.news_feeds:
            try:
                feed_items = await self._parse_rss_feed(feed_url, symbol)
                news_items.extend(feed_items)
            except Exception as e:
                self.logger.error(f"Error parsing feed {feed_url}: {str(e)}")
                continue
        
        # Remove duplicates and sort by date
        unique_news = {}
        for item in news_items:
            if item.title not in unique_news:
                unique_news[item.title] = item
        
        sorted_news = sorted(
            unique_news.values(), 
            key=lambda x: x.published_date, 
            reverse=True
        )
        
        return sorted_news[:20]  # Return latest 20 items
    
    async def _parse_rss_feed(self, feed_url: str, symbol: str) -> List[NewsItem]:
        """Parse RSS feed"""
        news_items = []
        
        try:
            # Parse RSS feed
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:10]:  # Process latest 10 items
                # Check symbol relevance
                if not self._is_relevant_to_symbol(entry.title + " " + entry.get('summary', ''), symbol):
                    continue
                
                # Calculate sentiment score
                content = entry.title + " " + entry.get('summary', '')
                sentiment_score = self._calculate_text_sentiment(content)
                
                # Extract keywords
                keywords = self._extract_keywords(content)
                
                # Parse published date
                published_date = datetime.now()
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_date = datetime(*entry.published_parsed[:6])
                
                news_item = NewsItem(
                    title=entry.title,
                    content=entry.get('summary', ''),
                    source=feed.feed.get('title', 'Unknown'),
                    published_date=published_date,
                    url=entry.get('link', ''),
                    sentiment_score=sentiment_score,
                    keywords=keywords
                )
                
                news_items.append(news_item)
                
        except Exception as e:
            self.logger.error(f"Error parsing RSS feed {feed_url}: {str(e)}")
        
        return news_items
    
    def _is_relevant_to_symbol(self, text: str, symbol: str) -> bool:
        """Check if text is relevant to symbol"""
        text_lower = text.lower()
        symbol_lower = symbol.lower()
        
        # Direct symbol matching
        if symbol_lower in text_lower:
            return True
        
        # Company name matching (simple mapping)
        symbol_mappings = {
            'aapl': ['apple', 'iphone', 'mac', 'ipad'],
            'googl': ['google', 'alphabet', 'android', 'youtube'],
            'msft': ['microsoft', 'windows', 'azure', 'office'],
            'tsla': ['tesla', 'elon musk', 'electric vehicle', 'ev'],
            'nvda': ['nvidia', 'gpu', 'ai chip', 'graphics'],
            '^gspc': ['s&p 500', 'sp500', 'market index'],
            '^ixic': ['nasdaq', 'tech stock', 'technology'],
            '^vix': ['vix', 'volatility', 'fear index']
        }
        
        if symbol_lower in symbol_mappings:
            for keyword in symbol_mappings[symbol_lower]:
                if keyword in text_lower:
                    return True
        
        # General market-related keywords
        market_keywords = ['stock', 'market', 'trading', 'investor', 'economy', 'financial']
        return any(keyword in text_lower for keyword in market_keywords)
    
    def _calculate_text_sentiment(self, text: str) -> float:
        """Calculate text sentiment score (simple keyword-based)"""
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.positive_keywords if word in text_lower)
        negative_count = sum(1 for word in self.negative_keywords if word in text_lower)
        
        total_words = len(text.split())
        
        if total_words == 0:
            return 0.0
        
        # Calculate normalized sentiment score
        positive_ratio = positive_count / total_words
        negative_ratio = negative_count / total_words
        
        sentiment_score = (positive_ratio - negative_ratio) * 10  # Scale adjustment
        
        # Clip to -1.0 ~ 1.0 range
        return max(-1.0, min(1.0, sentiment_score))
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction (remove stop words and extract important words)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Remove stop words
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
        
        keywords = [word for word in words if word not in stop_words]
        
        # Return top keywords based on frequency
        from collections import Counter
        word_counts = Counter(keywords)
        
        return [word for word, count in word_counts.most_common(10)]
    
    def _analyze_news_sentiment(self, news_items: List[NewsItem]) -> float:
        """Analyze overall sentiment of news items"""
        if not news_items:
            return 0.0
        
        # Apply time weighting (newer news gets higher weight)
        total_weighted_sentiment = 0.0
        total_weight = 0.0
        
        now = datetime.now()
        
        for item in news_items:
            # Calculate weight based on time difference (1.0 within 24h, decreasing after)
            time_diff = (now - item.published_date).total_seconds() / 3600  # Hours
            weight = max(0.1, 1.0 - (time_diff / 48))  # Weight decays over 48 hours
            
            total_weighted_sentiment += item.sentiment_score * weight
            total_weight += weight
        
        return total_weighted_sentiment / total_weight if total_weight > 0 else 0.0
    
    async def _calculate_fear_greed_index(self) -> float:
        """Calculate VIX-based Fear/Greed index"""
        try:
            import yfinance as yf
            
            # Collect VIX data
            vix = yf.Ticker("^VIX")
            vix_data = vix.history(period="5d")
            
            if vix_data.empty:
                return 50.0  # Neutral value
            
            current_vix = vix_data['Close'].iloc[-1]
            
            # Convert VIX to 0-100 Fear/Greed index
            # VIX below 10: Extreme Greed (90-100)
            # VIX below 20: Greed (60-90)
            # VIX below 30: Neutral (40-60)
            # VIX below 40: Fear (20-40)
            # VIX above 40: Extreme Fear (0-20)
            
            if current_vix <= 10:
                fear_greed_index = 90 + (10 - current_vix)  # 90-100
            elif current_vix <= 20:
                fear_greed_index = 60 + (20 - current_vix) * 3  # 60-90
            elif current_vix <= 30:
                fear_greed_index = 40 + (30 - current_vix) * 2  # 40-60
            elif current_vix <= 40:
                fear_greed_index = 20 + (40 - current_vix) * 2  # 20-40
            else:
                fear_greed_index = max(0, 20 - (current_vix - 40))  # 0-20
            
            return min(100, max(0, fear_greed_index))
            
        except Exception as e:
            self.logger.error(f"Error calculating fear/greed index: {str(e)}")
            return 50.0  # Return neutral value
    
    def _analyze_sentiment_trend(self, symbol: str, current_sentiment: float) -> str:
        """Analyze sentiment trend (simple implementation)"""
        # In practice, compare with historical data, but simplified here
        if current_sentiment > 0.3:
            return "improving"
        elif current_sentiment < -0.3:
            return "declining"
        else:
            return "stable"
    
    def _calculate_overall_sentiment(self, news_sentiment: float, fear_greed_index: float) -> float:
        """Calculate overall sentiment score"""
        # News sentiment (70%) and Fear/Greed index (30%) weighted average
        fear_greed_normalized = (fear_greed_index - 50) / 50  # Normalize to -1 ~ 1
        
        overall_sentiment = (news_sentiment * 0.7) + (fear_greed_normalized * 0.3)
        
        return max(-1.0, min(1.0, overall_sentiment))
    
    def _classify_sentiment(self, sentiment_score: float) -> SentimentScore:
        """Classify sentiment score into category"""
        if sentiment_score >= 0.6:
            return SentimentScore.VERY_POSITIVE
        elif sentiment_score >= 0.2:
            return SentimentScore.POSITIVE
        elif sentiment_score <= -0.6:
            return SentimentScore.VERY_NEGATIVE
        elif sentiment_score <= -0.2:
            return SentimentScore.NEGATIVE
        else:
            return SentimentScore.NEUTRAL
    
    def _calculate_confidence(self, news_items: List[NewsItem], overall_score: float) -> float:
        """Calculate confidence"""
        if not news_items:
            return 0.0
        
        # More news items increase confidence
        count_factor = min(1.0, len(news_items) / 10)
        
        # Check consistency of sentiment scores
        sentiment_scores = [item.sentiment_score for item in news_items]
        sentiment_std = np.std(sentiment_scores) if len(sentiment_scores) > 1 else 0
        consistency_factor = max(0.3, 1.0 - sentiment_std)
        
        # Check recency (ratio of news within 24 hours)
        now = datetime.now()
        recent_news = sum(1 for item in news_items 
                         if (now - item.published_date).total_seconds() < 86400)
        recency_factor = recent_news / len(news_items)
        
        confidence = (count_factor * 0.4 + consistency_factor * 0.4 + recency_factor * 0.2)
        
        return min(1.0, max(0.0, confidence))
    
    def get_sentiment_description(self, sentiment: MarketSentiment) -> str:
        """Generate sentiment analysis description"""
        desc_parts = []
        
        # Overall sentiment
        sentiment_desc = {
            SentimentScore.VERY_POSITIVE: "Very Positive",
            SentimentScore.POSITIVE: "Positive",
            SentimentScore.NEUTRAL: "Neutral",
            SentimentScore.NEGATIVE: "Negative",
            SentimentScore.VERY_NEGATIVE: "Very Negative"
        }
        
        desc_parts.append(f"Market Sentiment: {sentiment_desc[sentiment.overall_sentiment]}")
        desc_parts.append(f"Confidence: {sentiment.confidence:.1%}")
        
        # Fear/Greed index
        if sentiment.fear_greed_index > 70:
            desc_parts.append("Extreme Greed")
        elif sentiment.fear_greed_index > 55:
            desc_parts.append("Greed")
        elif sentiment.fear_greed_index < 30:
            desc_parts.append("Extreme Fear")
        elif sentiment.fear_greed_index < 45:
            desc_parts.append("Fear")
        
        # News count
        desc_parts.append(f"Analyzed News: {sentiment.news_count} articles")
        
        return ", ".join(desc_parts)

# Test function
async def test_sentiment_analyzer():
    analyzer = SentimentAnalyzer()
    
    symbols = ["AAPL", "^GSPC"]
    
    for symbol in symbols:
        print(f"\n=== {symbol} Sentiment Analysis ===")
        sentiment = await analyzer.analyze_market_sentiment(symbol)
        
        if sentiment:
            print(f"Overall Sentiment: {sentiment.overall_sentiment.value}")
            print(f"Sentiment Score: {sentiment.sentiment_score:.3f}")
            print(f"Fear/Greed Index: {sentiment.fear_greed_index:.1f}")
            print(f"Sentiment Trend: {sentiment.sentiment_trend}")
            print(f"Description: {analyzer.get_sentiment_description(sentiment)}")
            
            if sentiment.key_news:
                print("\nKey News:")
                for i, news in enumerate(sentiment.key_news[:3], 1):
                    print(f"{i}. {news.title} (Sentiment: {news.sentiment_score:.2f})")
        else:
            print("Analysis failed")

if __name__ == "__main__":
    asyncio.run(test_sentiment_analyzer())
