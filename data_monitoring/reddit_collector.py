#!/usr/bin/env python3
"""
Reddit 경제 데이터 수집기
"""

import os
import praw
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from textblob import TextBlob
import time
import re

class RedditEconomicCollector:
    """Reddit 경제 관련 데이터 수집기"""
    
    def __init__(self):
        """Reddit API 클라이언트 초기화"""
        self.logger = logging.getLogger(__name__)
        
        # 환경변수에서 Reddit 자격증명 로드
        self.client_id = os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.user_agent = os.getenv('REDDIT_USER_AGENT', 'EconomicNewsBot/1.0')
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Reddit API 자격증명이 환경변수에 설정되지 않았습니다.")
        
        # Reddit 클라이언트 초기화
        try:
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            )
            
            # 연결 테스트
            self.reddit.user.me()  # 인증 테스트
            self.logger.info(f"✅ Reddit API 연결 성공")
            
        except Exception as e:
            self.logger.error(f"❌ Reddit API 연결 실패: {e}")
            # 읽기 전용 모드로 시도
            try:
                self.reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent
                )
                self.logger.info("✅ Reddit API 읽기 전용 모드로 연결")
            except Exception as e2:
                self.logger.error(f"❌ Reddit API 읽기 전용 연결도 실패: {e2}")
                raise
        
        # 경제 관련 서브레딧 목록
        self.economic_subreddits = [
            'investing',
            'stocks',
            'economics',
            'SecurityAnalysis',
            'ValueInvesting',
            'financialindependence',
            'personalfinance',
            'StockMarket',
            'wallstreetbets',
            'economy',
            'finance',
            'business',
            'entrepreneur',
            'cryptocurrency',
            'Bitcoin'
        ]
        
        # 경제 관련 키워드
        self.economic_keywords = [
            'fed', 'federal reserve', 'interest rate', 'inflation', 'recession',
            'gdp', 'unemployment', 'stock market', 'nasdaq', 'sp500', 'dow jones',
            'earnings', 'revenue', 'profit', 'loss', 'merger', 'acquisition',
            'ipo', 'dividend', 'buyback', 'split', 'volatility', 'bull market',
            'bear market', 'correction', 'crash', 'rally', 'bubble'
        ]
        
        self.logger.info(f"🔧 Reddit 수집기 초기화 완료")
    
    def collect_subreddit_posts(self, subreddit_name: str, limit: int = 25, time_filter: str = 'day') -> List[Dict[str, Any]]:
        """특정 서브레딧에서 포스트 수집"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []
            
            # 인기 포스트 수집 (hot, new, top 중 선택)
            if time_filter == 'day':
                submissions = subreddit.hot(limit=limit)
            elif time_filter == 'week':
                submissions = subreddit.top(time_filter='week', limit=limit)
            else:
                submissions = subreddit.new(limit=limit)
            
            for submission in submissions:
                # 경제 관련 키워드 필터링
                if self._is_economic_content(submission.title + " " + submission.selftext):
                    post_data = {
                        'id': submission.id,
                        'title': submission.title,
                        'selftext': submission.selftext,
                        'score': submission.score,
                        'upvote_ratio': submission.upvote_ratio,
                        'num_comments': submission.num_comments,
                        'created_utc': submission.created_utc,
                        'created_datetime': datetime.fromtimestamp(submission.created_utc),
                        'author': str(submission.author) if submission.author else '[deleted]',
                        'subreddit': subreddit_name,
                        'url': submission.url,
                        'permalink': f"https://reddit.com{submission.permalink}",
                        'flair': submission.link_flair_text,
                        'is_self': submission.is_self,
                        'sentiment': self._analyze_sentiment(submission.title + " " + submission.selftext),
                        'economic_topics': self._extract_economic_topics(submission.title + " " + submission.selftext)
                    }
                    posts.append(post_data)
            
            self.logger.info(f"✅ r/{subreddit_name}: {len(posts)}개 경제 관련 포스트 수집")
            return posts
            
        except Exception as e:
            self.logger.error(f"❌ r/{subreddit_name} 수집 실패: {e}")
            return []
    
    def collect_subreddit_comments(self, subreddit_name: str, post_limit: int = 10, comment_limit: int = 50) -> List[Dict[str, Any]]:
        """특정 서브레딧의 댓글 수집"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            comments = []
            
            # 인기 포스트의 댓글 수집
            for submission in subreddit.hot(limit=post_limit):
                if self._is_economic_content(submission.title + " " + submission.selftext):
                    submission.comments.replace_more(limit=0)  # "더 보기" 댓글 제외
                    
                    comment_count = 0
                    for comment in submission.comments.list():
                        if comment_count >= comment_limit:
                            break
                        
                        if hasattr(comment, 'body') and len(comment.body) > 20:  # 의미있는 댓글만
                            comment_data = {
                                'id': comment.id,
                                'body': comment.body,
                                'score': comment.score,
                                'created_utc': comment.created_utc,
                                'created_datetime': datetime.fromtimestamp(comment.created_utc),
                                'author': str(comment.author) if comment.author else '[deleted]',
                                'subreddit': subreddit_name,
                                'post_id': submission.id,
                                'post_title': submission.title,
                                'permalink': f"https://reddit.com{comment.permalink}",
                                'sentiment': self._analyze_sentiment(comment.body),
                                'economic_topics': self._extract_economic_topics(comment.body)
                            }
                            comments.append(comment_data)
                            comment_count += 1
            
            self.logger.info(f"✅ r/{subreddit_name}: {len(comments)}개 댓글 수집")
            return comments
            
        except Exception as e:
            self.logger.error(f"❌ r/{subreddit_name} 댓글 수집 실패: {e}")
            return []
    
    def collect_comprehensive_data(self, max_subreddits: int = 8, posts_per_subreddit: int = 15) -> Dict[str, Any]:
        """종합적인 Reddit 경제 데이터 수집"""
        self.logger.info("🔄 Reddit 종합 경제 데이터 수집 시작")
        
        reddit_data = {
            'timestamp': datetime.now().isoformat(),
            'subreddits': {},
            'summary': {},
            'trending_topics': {},
            'sentiment_analysis': {}
        }
        
        all_posts = []
        all_comments = []
        
        # 주요 서브레딧에서 데이터 수집
        for i, subreddit_name in enumerate(self.economic_subreddits[:max_subreddits]):
            try:
                self.logger.info(f"📊 r/{subreddit_name} 수집 중... ({i+1}/{max_subreddits})")
                
                # 포스트 수집
                posts = self.collect_subreddit_posts(subreddit_name, limit=posts_per_subreddit)
                
                # 댓글 수집 (상위 포스트 5개에서만)
                comments = self.collect_subreddit_comments(subreddit_name, post_limit=5, comment_limit=20)
                
                reddit_data['subreddits'][subreddit_name] = {
                    'posts': posts,
                    'comments': comments,
                    'post_count': len(posts),
                    'comment_count': len(comments),
                    'avg_score': sum(p['score'] for p in posts) / len(posts) if posts else 0,
                    'avg_sentiment': sum(p['sentiment']['polarity'] for p in posts) / len(posts) if posts else 0
                }
                
                all_posts.extend(posts)
                all_comments.extend(comments)
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"❌ r/{subreddit_name} 처리 실패: {e}")
                continue
        
        # 전체 요약 생성
        reddit_data['summary'] = self._generate_summary(all_posts, all_comments)
        reddit_data['trending_topics'] = self._extract_trending_topics(all_posts + all_comments)
        reddit_data['sentiment_analysis'] = self._analyze_overall_sentiment(all_posts + all_comments)
        
        self.logger.info(f"✅ Reddit 데이터 수집 완료: {len(all_posts)}개 포스트, {len(all_comments)}개 댓글")
        return reddit_data
    
    def _is_economic_content(self, text: str) -> bool:
        """경제 관련 콘텐츠인지 판단"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.economic_keywords)
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """텍스트 감정 분석"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            if polarity > 0.1:
                label = "positive"
            elif polarity < -0.1:
                label = "negative"
            else:
                label = "neutral"
            
            return {
                'polarity': round(polarity, 3),
                'subjectivity': round(subjectivity, 3),
                'label': label
            }
        except:
            return {'polarity': 0, 'subjectivity': 0, 'label': 'neutral'}
    
    def _extract_economic_topics(self, text: str) -> List[str]:
        """경제 주제 추출"""
        text_lower = text.lower()
        topics = []
        
        topic_keywords = {
            'monetary_policy': ['fed', 'federal reserve', 'interest rate', 'monetary policy'],
            'stock_market': ['stock', 'nasdaq', 'sp500', 'dow jones', 'market'],
            'cryptocurrency': ['bitcoin', 'crypto', 'ethereum', 'blockchain'],
            'inflation': ['inflation', 'cpi', 'price increase', 'cost of living'],
            'employment': ['unemployment', 'jobs', 'employment', 'labor'],
            'earnings': ['earnings', 'revenue', 'profit', 'quarterly'],
            'recession': ['recession', 'economic downturn', 'bear market'],
            'investment': ['investing', 'portfolio', 'dividend', 'value investing']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def _generate_summary(self, posts: List[Dict], comments: List[Dict]) -> Dict[str, Any]:
        """전체 요약 생성"""
        if not posts and not comments:
            return {}
        
        total_posts = len(posts)
        total_comments = len(comments)
        
        # 감정 분석
        all_content = posts + comments
        sentiments = [item['sentiment']['label'] for item in all_content]
        
        # 인기 서브레딧
        subreddit_counts = {}
        for post in posts:
            subreddit = post['subreddit']
            subreddit_counts[subreddit] = subreddit_counts.get(subreddit, 0) + 1
        
        # 평균 점수
        avg_post_score = sum(p['score'] for p in posts) / len(posts) if posts else 0
        avg_comment_score = sum(c['score'] for c in comments) / len(comments) if comments else 0
        
        return {
            'total_posts': total_posts,
            'total_comments': total_comments,
            'total_content': total_posts + total_comments,
            'avg_post_score': round(avg_post_score, 2),
            'avg_comment_score': round(avg_comment_score, 2),
            'sentiment_distribution': {
                'positive': sentiments.count('positive'),
                'negative': sentiments.count('negative'),
                'neutral': sentiments.count('neutral')
            },
            'top_subreddits': dict(sorted(subreddit_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
            'collection_time': datetime.now().isoformat()
        }
    
    def _extract_trending_topics(self, content: List[Dict]) -> Dict[str, int]:
        """트렌딩 주제 추출"""
        topic_counts = {}
        
        for item in content:
            topics = item.get('economic_topics', [])
            for topic in topics:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # 상위 10개 주제 반환
        return dict(sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10])
    
    def _analyze_overall_sentiment(self, content: List[Dict]) -> Dict[str, Any]:
        """전체 감정 분석"""
        if not content:
            return {}
        
        sentiments = [item['sentiment'] for item in content]
        polarities = [s['polarity'] for s in sentiments]
        
        avg_polarity = sum(polarities) / len(polarities)
        
        # 감정 라벨 분포
        labels = [s['label'] for s in sentiments]
        total = len(labels)
        
        return {
            'average_polarity': round(avg_polarity, 3),
            'overall_sentiment': 'positive' if avg_polarity > 0.1 else 'negative' if avg_polarity < -0.1 else 'neutral',
            'distribution': {
                'positive': labels.count('positive'),
                'negative': labels.count('negative'),
                'neutral': labels.count('neutral')
            },
            'percentages': {
                'positive': round(labels.count('positive') / total * 100, 1),
                'negative': round(labels.count('negative') / total * 100, 1),
                'neutral': round(labels.count('neutral') / total * 100, 1)
            }
        }

def main():
    """테스트 실행"""
    print("📱 Reddit 경제 데이터 수집기 테스트")
    print("=" * 50)
    
    try:
        collector = RedditEconomicCollector()
        
        # 종합 데이터 수집 (소량 테스트)
        reddit_data = collector.collect_comprehensive_data(max_subreddits=3, posts_per_subreddit=5)
        
        # 결과 출력
        summary = reddit_data.get('summary', {})
        print(f"\n📊 수집 결과:")
        print(f"  총 포스트: {summary.get('total_posts', 0)}개")
        print(f"  총 댓글: {summary.get('total_comments', 0)}개")
        print(f"  평균 포스트 점수: {summary.get('avg_post_score', 0)}")
        
        # 감정 분석
        sentiment = reddit_data.get('sentiment_analysis', {})
        if sentiment:
            print(f"\n💭 전체 감정 분석:")
            print(f"  전체 감정: {sentiment.get('overall_sentiment', 'unknown')}")
            percentages = sentiment.get('percentages', {})
            print(f"  긍정: {percentages.get('positive', 0)}%")
            print(f"  부정: {percentages.get('negative', 0)}%")
            print(f"  중립: {percentages.get('neutral', 0)}%")
        
        # 트렌딩 주제
        trending = reddit_data.get('trending_topics', {})
        if trending:
            print(f"\n🔥 트렌딩 주제:")
            for topic, count in list(trending.items())[:5]:
                print(f"  {topic}: {count}회 언급")
        
        # 인기 서브레딧
        top_subreddits = summary.get('top_subreddits', {})
        if top_subreddits:
            print(f"\n📈 활발한 서브레딧:")
            for subreddit, count in top_subreddits.items():
                print(f"  r/{subreddit}: {count}개 포스트")
        
        print(f"\n✅ Reddit 데이터 수집 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
