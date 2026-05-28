#!/usr/bin/env python3
"""
뉴스 및 소셜미디어 모니터링 강화 수집기 (실제 Reddit API 통합)
"""

import requests
import feedparser
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from textblob import TextBlob
import re
import time
import os

# Reddit 수집기 import
from data_monitoring.reddit_collector import RedditEconomicCollector

class EnhancedNewsCollector:
    """강화된 뉴스 및 소셜미디어 수집기 (실제 Reddit 데이터 포함)"""
    
    def __init__(self):
        """초기화"""
        self.logger = logging.getLogger(__name__)
        
        # Reddit 수집기 초기화
        try:
            self.reddit_collector = RedditEconomicCollector()
            self.use_reddit = True
            self.logger.info("✅ Reddit 수집기 활성화")
        except Exception as e:
            self.logger.warning(f"⚠️ Reddit 수집기 비활성화: {e}")
            self.use_reddit = False
        
        # 확장된 뉴스 소스
        self.news_sources = {
            "financial": [
                {"name": "Bloomberg Markets", "url": "https://feeds.bloomberg.com/markets/news.rss"},
                {"name": "Reuters Business", "url": "https://feeds.reuters.com/reuters/businessNews"},
                {"name": "MarketWatch", "url": "https://feeds.marketwatch.com/marketwatch/topstories/"},
                {"name": "CNN Money", "url": "https://rss.cnn.com/rss/money_latest.rss"},
                {"name": "Yahoo Finance", "url": "https://feeds.finance.yahoo.com/rss/2.0/headline"},
                {"name": "Financial Times", "url": "https://www.ft.com/rss/home"},
                {"name": "Wall Street Journal", "url": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml"}
            ],
            "economic": [
                {"name": "Federal Reserve", "url": "https://www.federalreserve.gov/feeds/press_all.xml"},
                {"name": "Treasury", "url": "https://home.treasury.gov/rss/press-releases"},
                {"name": "BLS News", "url": "https://www.bls.gov/feed/news_release/rss.xml"},
                {"name": "Commerce Dept", "url": "https://www.commerce.gov/rss.xml"}
            ],
            "international": [
                {"name": "ECB Press", "url": "https://www.ecb.europa.eu/rss/press.xml"},
                {"name": "Bank of Japan", "url": "https://www.boj.or.jp/en/rss/whatsnew.xml"},
                {"name": "IMF News", "url": "https://www.imf.org/en/News/RSS?language=eng"}
            ]
        }
        
        # 키워드 기반 분류
        self.keywords = {
            "monetary_policy": ["fed", "federal reserve", "interest rate", "monetary policy", "inflation", "deflation"],
            "market_sentiment": ["bull", "bear", "rally", "crash", "volatility", "correction"],
            "economic_indicators": ["gdp", "unemployment", "cpi", "ppi", "retail sales", "housing"],
            "geopolitical": ["trade war", "sanctions", "brexit", "election", "policy", "regulation"],
            "corporate": ["earnings", "merger", "acquisition", "ipo", "bankruptcy", "dividend"],
            "technology": ["ai", "blockchain", "crypto", "fintech", "digital", "innovation"]
        }
        
        self.logger.info("✅ 강화된 뉴스 수집기 초기화 완료")
    
    def collect_news_by_category(self, max_items_per_source: int = 10) -> Dict[str, Any]:
        """카테고리별 뉴스 수집"""
        self.logger.info("📰 카테고리별 뉴스 수집 시작")
        
        news_data = {
            "timestamp": datetime.now().isoformat(),
            "categories": {},
            "summary": {}
        }
        
        total_articles = 0
        
        for category, sources in self.news_sources.items():
            category_articles = []
            
            for source in sources:
                try:
                    articles = self._fetch_rss_feed(source["url"], max_items_per_source)
                    
                    for article in articles:
                        article["source_name"] = source["name"]
                        article["category"] = category
                        
                        # 감정 분석 추가
                        article["sentiment"] = self._analyze_sentiment(article["title"] + " " + article.get("summary", ""))
                        
                        # 키워드 분류
                        article["topics"] = self._classify_topics(article["title"] + " " + article.get("summary", ""))
                        
                        category_articles.append(article)
                    
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    self.logger.error(f"❌ {source['name']} 수집 오류: {e}")
                    continue
            
            news_data["categories"][category] = category_articles
            total_articles += len(category_articles)
            
            self.logger.info(f"✅ {category}: {len(category_articles)}개 기사")
        
        # 요약 정보 생성
        news_data["summary"] = self._generate_news_summary(news_data["categories"])
        news_data["summary"]["total_articles"] = total_articles
        
        self.logger.info(f"✅ 뉴스 수집 완료: {total_articles}개 기사")
        return news_data
    
    def _fetch_rss_feed(self, url: str, max_items: int) -> List[Dict[str, Any]]:
        """RSS 피드에서 뉴스 수집"""
        try:
            feed = feedparser.parse(url)
            articles = []
            
            for entry in feed.entries[:max_items]:
                article = {
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "summary": entry.get("summary", ""),
                    "author": entry.get("author", ""),
                    "published_parsed": entry.get("published_parsed", None)
                }
                
                # 발행 시간 정규화
                if article["published_parsed"]:
                    article["published_datetime"] = datetime(*article["published_parsed"][:6])
                else:
                    article["published_datetime"] = datetime.now()
                
                articles.append(article)
            
            return articles
            
        except Exception as e:
            self.logger.error(f"RSS 피드 파싱 오류 ({url}): {e}")
            return []
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """텍스트 감정 분석"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # 감정 라벨링
            if polarity > 0.1:
                label = "positive"
            elif polarity < -0.1:
                label = "negative"
            else:
                label = "neutral"
            
            return {
                "polarity": round(polarity, 3),
                "subjectivity": round(subjectivity, 3),
                "label": label
            }
            
        except Exception as e:
            self.logger.debug(f"감정 분석 오류: {e}")
            return {"polarity": 0, "subjectivity": 0, "label": "neutral"}
    
    def _classify_topics(self, text: str) -> List[str]:
        """키워드 기반 주제 분류"""
        text_lower = text.lower()
        topics = []
        
        for topic, keywords in self.keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def _generate_news_summary(self, categories: Dict[str, List]) -> Dict[str, Any]:
        """뉴스 요약 생성"""
        summary = {
            "by_category": {},
            "sentiment_analysis": {},
            "trending_topics": {},
            "recent_highlights": []
        }
        
        all_articles = []
        
        # 카테고리별 요약
        for category, articles in categories.items():
            if articles:
                sentiments = [article["sentiment"]["label"] for article in articles]
                summary["by_category"][category] = {
                    "count": len(articles),
                    "positive": sentiments.count("positive"),
                    "negative": sentiments.count("negative"),
                    "neutral": sentiments.count("neutral")
                }
                all_articles.extend(articles)
        
        # 전체 감정 분석
        if all_articles:
            all_sentiments = [article["sentiment"]["label"] for article in all_articles]
            total_count = len(all_sentiments)
            
            summary["sentiment_analysis"] = {
                "total_articles": total_count,
                "positive": all_sentiments.count("positive"),
                "negative": all_sentiments.count("negative"),
                "neutral": all_sentiments.count("neutral"),
                "positive_ratio": round(all_sentiments.count("positive") / total_count * 100, 1),
                "negative_ratio": round(all_sentiments.count("negative") / total_count * 100, 1)
            }
            
            # 주제별 트렌드
            topic_counts = {}
            for article in all_articles:
                for topic in article.get("topics", []):
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            summary["trending_topics"] = dict(sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10])
            
            # 최근 주요 뉴스 (감정 점수 기준)
            recent_articles = sorted(all_articles, key=lambda x: x["published_datetime"], reverse=True)[:20]
            important_articles = sorted(recent_articles, key=lambda x: abs(x["sentiment"]["polarity"]), reverse=True)[:5]
            
            summary["recent_highlights"] = [
                {
                    "title": article["title"],
                    "source": article["source_name"],
                    "sentiment": article["sentiment"]["label"],
                    "topics": article["topics"]
                }
                for article in important_articles
            ]
        
        return summary
    
    def get_social_media_mentions(self) -> Dict[str, Any]:
        """소셜미디어 언급 분석 (실제 Reddit 데이터 + Twitter 시뮬레이션)"""
        
        social_data = {
            "timestamp": datetime.now().isoformat(),
            "platforms": {},
            "overall_sentiment": {}
        }
        
        # Reddit 실제 데이터 수집
        if self.use_reddit:
            try:
                self.logger.info("📱 Reddit 실제 데이터 수집 중...")
                reddit_data = self.reddit_collector.collect_comprehensive_data(
                    max_subreddits=5, 
                    posts_per_subreddit=10
                )
                
                reddit_summary = reddit_data.get('summary', {})
                reddit_sentiment = reddit_data.get('sentiment_analysis', {})
                
                social_data["platforms"]["reddit"] = {
                    "posts": reddit_summary.get('total_posts', 0),
                    "comments": reddit_summary.get('total_comments', 0),
                    "total_content": reddit_summary.get('total_content', 0),
                    "avg_post_score": reddit_summary.get('avg_post_score', 0),
                    "sentiment": {
                        "positive": reddit_sentiment.get('percentages', {}).get('positive', 0),
                        "negative": reddit_sentiment.get('percentages', {}).get('negative', 0),
                        "neutral": reddit_sentiment.get('percentages', {}).get('neutral', 0)
                    },
                    "overall_sentiment": reddit_sentiment.get('overall_sentiment', 'neutral'),
                    "average_polarity": reddit_sentiment.get('average_polarity', 0),
                    "top_subreddits": list(reddit_summary.get('top_subreddits', {}).keys())[:5],
                    "trending_topics": list(reddit_data.get('trending_topics', {}).keys())[:5],
                    "data_source": "real_api"
                }
                
                self.logger.info(f"✅ Reddit 실제 데이터: {reddit_summary.get('total_content', 0)}개 콘텐츠")
                
            except Exception as e:
                self.logger.error(f"❌ Reddit 데이터 수집 실패: {e}")
                # 실패 시 기본값
                social_data["platforms"]["reddit"] = {
                    "posts": 0,
                    "comments": 0,
                    "error": str(e),
                    "data_source": "failed"
                }
        else:
            # Reddit 비활성화 시 시뮬레이션 데이터
            social_data["platforms"]["reddit"] = {
                "posts": 45,
                "comments": 892,
                "sentiment": {"positive": 35, "negative": 25, "neutral": 40},
                "top_subreddits": ["r/investing", "r/stocks", "r/economics"],
                "data_source": "simulation"
            }
        
        # Twitter 시뮬레이션 데이터 (실제 API 연동 시 교체)
        social_data["platforms"]["twitter"] = {
            "mentions": 1250,
            "sentiment": {"positive": 45, "negative": 30, "neutral": 25},
            "trending_hashtags": ["#Fed", "#Inflation", "#StockMarket", "#Economy", "#Bitcoin"],
            "data_source": "simulation"
        }
        
        # 기타 플랫폼 시뮬레이션
        social_data["platforms"]["news_comments"] = {
            "total_comments": 2340,
            "sentiment": {"positive": 35, "negative": 40, "neutral": 25},
            "data_source": "simulation"
        }
        
        # 전체 감정 계산
        social_data["overall_sentiment"] = self._calculate_overall_social_sentiment(social_data["platforms"])
        
        return social_data
    
    def _calculate_overall_social_sentiment(self, platforms: Dict[str, Any]) -> Dict[str, Any]:
        """소셜미디어 전체 감정 계산"""
        try:
            total_positive = 0
            total_negative = 0
            total_neutral = 0
            total_weight = 0
            
            # Reddit 실제 데이터 가중치 높게
            if "reddit" in platforms and platforms["reddit"].get("data_source") == "real_api":
                reddit_sentiment = platforms["reddit"].get("sentiment", {})
                reddit_weight = 0.6  # 실제 데이터이므로 높은 가중치
                
                total_positive += reddit_sentiment.get("positive", 0) * reddit_weight
                total_negative += reddit_sentiment.get("negative", 0) * reddit_weight
                total_neutral += reddit_sentiment.get("neutral", 0) * reddit_weight
                total_weight += reddit_weight
            
            # Twitter 시뮬레이션 데이터
            if "twitter" in platforms:
                twitter_sentiment = platforms["twitter"].get("sentiment", {})
                twitter_weight = 0.3
                
                total_positive += twitter_sentiment.get("positive", 0) * twitter_weight
                total_negative += twitter_sentiment.get("negative", 0) * twitter_weight
                total_neutral += twitter_sentiment.get("neutral", 0) * twitter_weight
                total_weight += twitter_weight
            
            # 기타 플랫폼
            if "news_comments" in platforms:
                news_sentiment = platforms["news_comments"].get("sentiment", {})
                news_weight = 0.1
                
                total_positive += news_sentiment.get("positive", 0) * news_weight
                total_negative += news_sentiment.get("negative", 0) * news_weight
                total_neutral += news_sentiment.get("neutral", 0) * news_weight
                total_weight += news_weight
            
            if total_weight > 0:
                avg_positive = total_positive / total_weight
                avg_negative = total_negative / total_weight
                avg_neutral = total_neutral / total_weight
                
                # 감정 점수 계산 (-1 to 1)
                sentiment_score = (avg_positive - avg_negative) / 100
                
                # 라벨링
                if sentiment_score > 0.1:
                    label = "positive"
                elif sentiment_score < -0.1:
                    label = "negative"
                else:
                    label = "neutral"
                
                return {
                    "score": round(sentiment_score, 3),
                    "label": label,
                    "confidence": 0.75,
                    "distribution": {
                        "positive": round(avg_positive, 1),
                        "negative": round(avg_negative, 1),
                        "neutral": round(avg_neutral, 1)
                    }
                }
            
        except Exception as e:
            self.logger.error(f"전체 소셜미디어 감정 계산 오류: {e}")
        
        # 기본값
        return {
            "score": 0.0,
            "label": "neutral",
            "confidence": 0.5,
            "distribution": {"positive": 33.3, "negative": 33.3, "neutral": 33.3}
        }

def main():
    """테스트 실행"""
    print("📰 강화된 뉴스 및 소셜미디어 수집기 테스트")
    print("=" * 50)
    
    collector = EnhancedNewsCollector()
    
    # 뉴스 수집
    news_data = collector.collect_news_by_category(max_items_per_source=5)
    
    # 결과 출력
    summary = news_data.get("summary", {})
    print(f"\n📊 뉴스 수집 결과:")
    print(f"  총 기사: {summary.get('total_articles', 0)}개")
    
    # 카테고리별 요약
    by_category = summary.get("by_category", {})
    for category, stats in by_category.items():
        print(f"  {category}: {stats['count']}개 (긍정: {stats['positive']}, 부정: {stats['negative']})")
    
    # 감정 분석
    sentiment = summary.get("sentiment_analysis", {})
    if sentiment:
        print(f"\n💭 전체 감정 분석:")
        print(f"  긍정: {sentiment.get('positive_ratio', 0)}%")
        print(f"  부정: {sentiment.get('negative_ratio', 0)}%")
    
    # 트렌딩 주제
    trending = summary.get("trending_topics", {})
    if trending:
        print(f"\n🔥 트렌딩 주제:")
        for topic, count in list(trending.items())[:5]:
            print(f"  {topic}: {count}회 언급")
    
    # 소셜미디어 데이터
    social_data = collector.get_social_media_mentions()
    print(f"\n📱 소셜미디어 분석:")
    print(f"  전체 감정: {social_data['overall_sentiment']['label']}")
    print(f"  Twitter 언급: {social_data['platforms']['twitter']['mentions']}회")

if __name__ == "__main__":
    main()
