#!/usr/bin/env python3
"""
Twitter API 연동 모듈 (공식 API v2)
주의: API 키가 필요하며 유료 서비스입니다
"""

import tweepy
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os
import time
import json

class TwitterAPICollector:
    """Twitter API v2를 사용한 데이터 수집기"""
    
    def __init__(self):
        """초기화"""
        self.logger = logging.getLogger(__name__)
        
        # API 키 설정 (환경 변수에서 읽기)
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        # API 클라이언트 초기화
        self.client = None
        self._initialize_client()
        
        # 경제 관련 검색 키워드
        self.economic_keywords = [
            # 한국어 키워드
            "연준 OR 금리 OR 인플레이션 OR 주식시장",
            "비트코인 OR 암호화폐 OR 블록체인",
            "부동산 OR 주택가격 OR 모기지",
            "실업률 OR 고용 OR 일자리",
            "환율 OR 달러 OR 원화",
            
            # 영어 키워드
            "Fed OR interest rate OR inflation",
            "stock market OR S&P500 OR NASDAQ",
            "Bitcoin OR cryptocurrency OR crypto",
            "unemployment OR jobs OR employment",
            "USD OR dollar OR forex"
        ]
    
    def _initialize_client(self):
        """Twitter API 클라이언트 초기화"""
        try:
            if not self.bearer_token:
                self.logger.warning("⚠️ Twitter Bearer Token이 설정되지 않았습니다")
                return
            
            # API v2 클라이언트 생성
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                wait_on_rate_limit=True
            )
            
            # 연결 테스트
            try:
                me = self.client.get_me()
                self.logger.info(f"✅ Twitter API 연결 성공: @{me.data.username}")
            except Exception as e:
                self.logger.error(f"❌ Twitter API 인증 실패: {e}")
                self.client = None
                
        except Exception as e:
            self.logger.error(f"❌ Twitter API 초기화 실패: {e}")
            self.client = None
    
    def collect_economic_tweets(self, max_results: int = 100) -> Dict[str, Any]:
        """경제 관련 트윗 수집"""
        
        if not self.client:
            self.logger.warning("⚠️ Twitter API 클라이언트가 초기화되지 않았습니다")
            return self._get_fallback_data()
        
        self.logger.info(f"🐦 Twitter에서 경제 관련 트윗 수집 시작 (최대 {max_results}개)")
        
        all_tweets = []
        
        try:
            for keyword in self.economic_keywords:
                self.logger.info(f"🔍 키워드 검색: {keyword}")
                
                # 트윗 검색 (최근 7일)
                tweets = tweepy.Paginator(
                    self.client.search_recent_tweets,
                    query=keyword,
                    tweet_fields=['created_at', 'author_id', 'public_metrics', 'context_annotations', 'lang'],
                    max_results=min(max_results // len(self.economic_keywords), 100),
                    limit=1
                ).flatten(limit=max_results // len(self.economic_keywords))
                
                for tweet in tweets:
                    tweet_data = {
                        'id': tweet.id,
                        'text': tweet.text,
                        'created_at': tweet.created_at,
                        'author_id': tweet.author_id,
                        'retweet_count': tweet.public_metrics['retweet_count'],
                        'like_count': tweet.public_metrics['like_count'],
                        'reply_count': tweet.public_metrics['reply_count'],
                        'quote_count': tweet.public_metrics['quote_count'],
                        'language': tweet.lang,
                        'keyword': keyword
                    }
                    
                    # 감정 분석
                    tweet_data['sentiment'] = self._analyze_tweet_sentiment(tweet.text)
                    
                    all_tweets.append(tweet_data)
                
                # Rate limiting 방지
                time.sleep(1)
        
        except Exception as e:
            self.logger.error(f"❌ 트윗 수집 오류: {e}")
            return self._get_fallback_data()
        
        # 결과 정리
        result = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'total_tweets': len(all_tweets),
            'tweets': all_tweets,
            'summary': self._generate_twitter_summary(all_tweets)
        }
        
        self.logger.info(f"✅ Twitter 데이터 수집 완료: {len(all_tweets)}개 트윗")
        return result
    
    def _analyze_tweet_sentiment(self, text: str) -> Dict[str, Any]:
        """트윗 감정 분석"""
        try:
            from textblob import TextBlob
            
            blob = TextBlob(text)
            sentiment = blob.sentiment
            
            return {
                'polarity': sentiment.polarity,      # -1 (부정) ~ 1 (긍정)
                'subjectivity': sentiment.subjectivity,  # 0 (객관적) ~ 1 (주관적)
                'label': 'positive' if sentiment.polarity > 0.1 else 'negative' if sentiment.polarity < -0.1 else 'neutral'
            }
        except Exception as e:
            self.logger.warning(f"감정 분석 오류: {e}")
            return {'polarity': 0, 'subjectivity': 0, 'label': 'neutral'}
    
    def _generate_twitter_summary(self, tweets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Twitter 데이터 요약 생성"""
        if not tweets:
            return {}
        
        # 감정 분석 요약
        sentiments = [tweet['sentiment']['polarity'] for tweet in tweets]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        positive_tweets = len([s for s in sentiments if s > 0.1])
        negative_tweets = len([s for s in sentiments if s < -0.1])
        neutral_tweets = len(tweets) - positive_tweets - negative_tweets
        
        # 인기 트윗 (좋아요 + 리트윗 기준)
        popular_tweets = sorted(
            tweets, 
            key=lambda x: x['like_count'] + x['retweet_count'], 
            reverse=True
        )[:5]
        
        # 키워드별 분포
        keyword_distribution = {}
        for tweet in tweets:
            keyword = tweet['keyword']
            if keyword not in keyword_distribution:
                keyword_distribution[keyword] = 0
            keyword_distribution[keyword] += 1
        
        return {
            'total_tweets': len(tweets),
            'sentiment_summary': {
                'average_sentiment': avg_sentiment,
                'positive_tweets': positive_tweets,
                'negative_tweets': negative_tweets,
                'neutral_tweets': neutral_tweets,
                'sentiment_label': 'positive' if avg_sentiment > 0.1 else 'negative' if avg_sentiment < -0.1 else 'neutral'
            },
            'popular_tweets': popular_tweets,
            'keyword_distribution': keyword_distribution,
            'languages': list(set([tweet['language'] for tweet in tweets])),
            'time_range': {
                'earliest': min([tweet['created_at'] for tweet in tweets]).isoformat(),
                'latest': max([tweet['created_at'] for tweet in tweets]).isoformat()
            }
        }
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """API 사용 불가 시 대체 데이터"""
        self.logger.info("📝 Twitter API 대신 시뮬레이션 데이터 사용")
        
        # 현실적인 시뮬레이션 데이터
        sample_tweets = [
            {
                'id': f'sim_{i}',
                'text': tweet_text,
                'created_at': datetime.now() - timedelta(hours=i),
                'author_id': f'user_{i}',
                'retweet_count': max(0, 50 - i * 5),
                'like_count': max(0, 200 - i * 10),
                'reply_count': max(0, 20 - i * 2),
                'quote_count': max(0, 10 - i),
                'language': 'ko' if any(ord(c) > 127 for c in tweet_text) else 'en',
                'keyword': 'simulation',
                'sentiment': {
                    'polarity': (i % 3 - 1) * 0.3,  # -0.3, 0, 0.3 순환
                    'subjectivity': 0.5,
                    'label': ['negative', 'neutral', 'positive'][i % 3]
                }
            }
            for i, tweet_text in enumerate([
                "연준 금리 인상 발표로 주식시장이 하락세를 보이고 있다 #Fed #금리인상",
                "비트코인이 다시 5만달러를 돌파했다! 불마켓 시작인가? #Bitcoin #crypto",
                "부동산 가격 상승이 계속되고 있어 서민들의 부담이 가중되고 있다 #부동산",
                "실업률이 3.5%로 하락하며 고용시장이 개선되고 있다 #고용 #경제",
                "달러 강세로 원화 가치가 하락하고 있어 수입물가 상승이 우려된다 #환율",
                "Fed raises interest rates by 0.25% to combat inflation #Fed #InterestRates",
                "Stock market volatility increases amid geopolitical tensions #StockMarket",
                "Cryptocurrency market shows signs of recovery #Crypto #Bitcoin",
                "Unemployment rate drops to lowest level in decades #Jobs #Economy",
                "Dollar strengthens against major currencies #USD #Forex"
            ])
        ]
        
        return {
            'status': 'simulation',
            'timestamp': datetime.now().isoformat(),
            'total_tweets': len(sample_tweets),
            'tweets': sample_tweets,
            'summary': self._generate_twitter_summary(sample_tweets),
            'note': 'Twitter API 키가 없어 시뮬레이션 데이터를 사용했습니다'
        }

# 환경 변수 설정 가이드
def setup_twitter_api_guide():
    """Twitter API 설정 가이드"""
    guide = """
    🐦 Twitter API 설정 가이드
    
    1. Twitter Developer Account 생성:
       https://developer.twitter.com/
    
    2. 프로젝트 생성 및 API 키 발급
    
    3. 환경 변수 설정:
       export TWITTER_BEARER_TOKEN="your_bearer_token"
       export TWITTER_API_KEY="your_api_key"
       export TWITTER_API_SECRET="your_api_secret"
       export TWITTER_ACCESS_TOKEN="your_access_token"
       export TWITTER_ACCESS_TOKEN_SECRET="your_access_token_secret"
    
    4. 또는 .env 파일에 추가:
       TWITTER_BEARER_TOKEN=your_bearer_token
       TWITTER_API_KEY=your_api_key
       TWITTER_API_SECRET=your_api_secret
       TWITTER_ACCESS_TOKEN=your_access_token
       TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
    
    💰 비용:
    - Basic Plan: $100/월 (10,000 트윗/월)
    - Pro Plan: $5,000/월 (1,000,000 트윗/월)
    
    ⚠️ 주의사항:
    - 2023년부터 무료 API 제공 중단
    - Rate Limiting 존재 (15분당 300 요청)
    - 실시간 스트리밍은 별도 요금
    """
    print(guide)

if __name__ == "__main__":
    # 설정 가이드 출력
    setup_twitter_api_guide()
    
    # 테스트 실행
    collector = TwitterAPICollector()
    result = collector.collect_economic_tweets(max_results=50)
    
    print(f"\n📊 수집 결과:")
    print(f"상태: {result['status']}")
    print(f"트윗 수: {result['total_tweets']}")
    if 'note' in result:
        print(f"참고: {result['note']}")
