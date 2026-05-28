#!/usr/bin/env python3
"""
실제 Reddit 데이터 수집기 (가상 데이터 없음)
.env 파일의 API 키를 사용하여 실제 Reddit 데이터만 수집
"""

import os
import sys
import praw
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import time
import re

# .env 파일 로드
load_dotenv()

class RealRedditCollector:
    """실제 Reddit 데이터만 수집하는 클래스"""
    
    def __init__(self):
        """Reddit API 클라이언트 초기화"""
        self.logger = logging.getLogger(__name__)
        
        # 환경변수에서 Reddit 자격증명 로드
        self.client_id = os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.user_agent = os.getenv('REDDIT_USER_AGENT', 'EconomicNewsBot/1.0')
        
        if not self.client_id or not self.client_secret:
            raise ValueError("❌ Reddit API 자격증명이 .env 파일에 설정되지 않았습니다.")
        
        # Reddit 클라이언트 초기화
        try:
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            )
            
            # 연결 테스트
            test_subreddit = self.reddit.subreddit('economics')
            _ = test_subreddit.display_name  # 실제 API 호출로 연결 확인
            
            self.logger.info(f"✅ Reddit API 연결 성공")
            
        except Exception as e:
            self.logger.error(f"❌ Reddit API 연결 실패: {e}")
            raise
        
        # 경제 관련 서브레딧 목록
        self.economic_subreddits = [
            'economics',
            'investing', 
            'stocks',
            'personalfinance',
            'SecurityAnalysis',
            'ValueInvesting',
            'financialindependence',
            'StockMarket'
        ]
        
        self.logger.info(f"✅ 실제 Reddit 수집기 초기화 완료")
    
    def collect_economic_posts(self, max_posts_per_subreddit: int = 10) -> Dict[str, Any]:
        """경제 관련 Reddit 포스트 수집"""
        
        self.logger.info(f"📱 실제 Reddit 데이터 수집 시작 (서브레딧당 최대 {max_posts_per_subreddit}개)")
        
        all_posts = []
        subreddit_stats = {}
        
        for subreddit_name in self.economic_subreddits:
            try:
                self.logger.info(f"🔍 r/{subreddit_name} 수집 중...")
                
                subreddit = self.reddit.subreddit(subreddit_name)
                posts = []
                
                # 인기 포스트 수집
                for post in subreddit.hot(limit=max_posts_per_subreddit):
                    try:
                        # 포스트 데이터 추출
                        post_data = {
                            'id': post.id,
                            'title': post.title,
                            'selftext': post.selftext,
                            'score': post.score,
                            'upvote_ratio': post.upvote_ratio,
                            'num_comments': post.num_comments,
                            'created_utc': datetime.fromtimestamp(post.created_utc),
                            'author': str(post.author) if post.author else '[deleted]',
                            'subreddit': subreddit_name,
                            'url': post.url,
                            'permalink': f"https://reddit.com{post.permalink}",
                            'is_self': post.is_self,
                            'over_18': post.over_18,
                            'spoiler': post.spoiler,
                            'stickied': post.stickied
                        }
                        
                        # 감정 분석 (간단한 키워드 기반)
                        post_data['sentiment'] = self._analyze_post_sentiment(post.title, post.selftext)
                        
                        # 경제 관련성 점수
                        post_data['economic_relevance'] = self._calculate_economic_relevance(post.title, post.selftext)
                        
                        posts.append(post_data)
                        all_posts.append(post_data)
                        
                    except Exception as e:
                        self.logger.warning(f"포스트 처리 오류 (r/{subreddit_name}): {e}")
                        continue
                
                subreddit_stats[subreddit_name] = {
                    'posts_collected': len(posts),
                    'subscribers': subreddit.subscribers,
                    'active_users': getattr(subreddit, 'active_user_count', None)
                }
                
                self.logger.info(f"✅ r/{subreddit_name}: {len(posts)}개 포스트 수집")
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"❌ r/{subreddit_name} 수집 실패: {e}")
                subreddit_stats[subreddit_name] = {
                    'posts_collected': 0,
                    'error': str(e)
                }
                continue
        
        # 결과 정리
        result = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'total_posts': len(all_posts),
            'posts': all_posts,
            'subreddit_stats': subreddit_stats,
            'collection_summary': self._generate_collection_summary(all_posts, subreddit_stats)
        }
        
        self.logger.info(f"✅ Reddit 데이터 수집 완료: {len(all_posts)}개 포스트")
        return result
    
    def collect_economic_comments(self, max_comments_per_subreddit: int = 20) -> Dict[str, Any]:
        """경제 관련 Reddit 댓글 수집"""
        
        self.logger.info(f"💬 실제 Reddit 댓글 수집 시작")
        
        all_comments = []
        
        for subreddit_name in self.economic_subreddits[:3]:  # 처음 3개 서브레딧만
            try:
                self.logger.info(f"🔍 r/{subreddit_name} 댓글 수집 중...")
                
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # 인기 포스트의 댓글 수집
                for post in subreddit.hot(limit=3):  # 포스트당 3개만
                    try:
                        post.comments.replace_more(limit=0)  # "더 보기" 댓글 제거
                        
                        comment_count = 0
                        for comment in post.comments.list():
                            if comment_count >= max_comments_per_subreddit // 3:
                                break
                            
                            if hasattr(comment, 'body') and len(comment.body) > 20:
                                comment_data = {
                                    'id': comment.id,
                                    'body': comment.body,
                                    'score': comment.score,
                                    'created_utc': datetime.fromtimestamp(comment.created_utc),
                                    'author': str(comment.author) if comment.author else '[deleted]',
                                    'subreddit': subreddit_name,
                                    'post_id': post.id,
                                    'post_title': post.title,
                                    'permalink': f"https://reddit.com{comment.permalink}"
                                }
                                
                                # 감정 분석
                                comment_data['sentiment'] = self._analyze_comment_sentiment(comment.body)
                                
                                all_comments.append(comment_data)
                                comment_count += 1
                        
                    except Exception as e:
                        self.logger.warning(f"댓글 처리 오류: {e}")
                        continue
                
                self.logger.info(f"✅ r/{subreddit_name}: 댓글 수집 완료")
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                self.logger.error(f"❌ r/{subreddit_name} 댓글 수집 실패: {e}")
                continue
        
        result = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'total_comments': len(all_comments),
            'comments': all_comments
        }
        
        self.logger.info(f"✅ Reddit 댓글 수집 완료: {len(all_comments)}개 댓글")
        return result
    
    def _analyze_post_sentiment(self, title: str, selftext: str) -> Dict[str, Any]:
        """포스트 감정 분석 (키워드 기반)"""
        
        text = f"{title} {selftext}".lower()
        
        # 긍정적 키워드
        positive_keywords = [
            'good', 'great', 'excellent', 'positive', 'bullish', 'growth', 'profit',
            'success', 'opportunity', 'optimistic', 'recovery', 'improvement'
        ]
        
        # 부정적 키워드  
        negative_keywords = [
            'bad', 'terrible', 'negative', 'bearish', 'loss', 'crash', 'decline',
            'recession', 'crisis', 'worry', 'concern', 'risk', 'problem'
        ]
        
        positive_count = sum(1 for keyword in positive_keywords if keyword in text)
        negative_count = sum(1 for keyword in negative_keywords if keyword in text)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            polarity = 0.3
        elif negative_count > positive_count:
            sentiment = 'negative'
            polarity = -0.3
        else:
            sentiment = 'neutral'
            polarity = 0.0
        
        return {
            'label': sentiment,
            'polarity': polarity,
            'positive_keywords': positive_count,
            'negative_keywords': negative_count
        }
    
    def _analyze_comment_sentiment(self, text: str) -> Dict[str, Any]:
        """댓글 감정 분석"""
        return self._analyze_post_sentiment(text, "")
    
    def _calculate_economic_relevance(self, title: str, selftext: str) -> float:
        """경제 관련성 점수 계산"""
        
        text = f"{title} {selftext}".lower()
        
        economic_keywords = [
            'economy', 'economic', 'finance', 'financial', 'market', 'stock', 'investment',
            'inflation', 'recession', 'gdp', 'fed', 'interest rate', 'monetary policy',
            'fiscal policy', 'unemployment', 'employment', 'trade', 'currency', 'dollar',
            'bitcoin', 'cryptocurrency', 'real estate', 'housing', 'mortgage'
        ]
        
        relevance_score = 0
        for keyword in economic_keywords:
            if keyword in text:
                relevance_score += 1
        
        # 0-1 사이로 정규화
        return min(relevance_score / 5.0, 1.0)
    
    def _generate_collection_summary(self, posts: List[Dict], subreddit_stats: Dict) -> Dict[str, Any]:
        """수집 요약 생성"""
        
        if not posts:
            return {'error': 'No posts collected'}
        
        # 감정 분석 요약
        sentiments = [post['sentiment']['label'] for post in posts]
        sentiment_counts = {
            'positive': sentiments.count('positive'),
            'negative': sentiments.count('negative'),
            'neutral': sentiments.count('neutral')
        }
        
        # 상위 서브레딧
        subreddit_counts = {}
        for post in posts:
            subreddit = post['subreddit']
            subreddit_counts[subreddit] = subreddit_counts.get(subreddit, 0) + 1
        
        top_subreddits = sorted(subreddit_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # 평균 점수
        avg_score = sum(post['score'] for post in posts) / len(posts)
        avg_comments = sum(post['num_comments'] for post in posts) / len(posts)
        
        return {
            'total_posts': len(posts),
            'sentiment_distribution': sentiment_counts,
            'top_subreddits': top_subreddits,
            'average_score': round(avg_score, 1),
            'average_comments': round(avg_comments, 1),
            'successful_subreddits': len([s for s in subreddit_stats.values() if 'error' not in s]),
            'failed_subreddits': len([s for s in subreddit_stats.values() if 'error' in s])
        }
    
    def get_texts_for_network_analysis(self, max_posts: int = 50) -> List[str]:
        """네트워크 분석용 텍스트 추출"""
        
        self.logger.info(f"🕸️ 네트워크 분석용 텍스트 수집 (최대 {max_posts}개)")
        
        try:
            # 포스트 수집
            posts_data = self.collect_economic_posts(max_posts_per_subreddit=max_posts//len(self.economic_subreddits))
            
            texts = []
            for post in posts_data['posts']:
                # 제목과 본문 결합
                title = post['title'].strip()
                selftext = post['selftext'].strip()
                
                if selftext:
                    combined_text = f"{title}. {selftext}"
                else:
                    combined_text = title
                
                # 최소 길이 필터
                if len(combined_text) > 20:
                    texts.append(combined_text)
            
            self.logger.info(f"✅ 네트워크 분석용 텍스트 {len(texts)}개 추출")
            return texts
            
        except Exception as e:
            self.logger.error(f"❌ 네트워크 분석용 텍스트 수집 실패: {e}")
            return []

if __name__ == "__main__":
    # 테스트 실행
    try:
        collector = RealRedditCollector()
        
        print("📱 실제 Reddit 데이터 수집 테스트")
        print("=" * 50)
        
        # 포스트 수집 테스트
        posts_result = collector.collect_economic_posts(max_posts_per_subreddit=3)
        
        print(f"✅ 포스트 수집 결과:")
        print(f"   총 포스트: {posts_result['total_posts']}개")
        print(f"   성공한 서브레딧: {posts_result['collection_summary']['successful_subreddits']}개")
        print(f"   실패한 서브레딧: {posts_result['collection_summary']['failed_subreddits']}개")
        
        if posts_result['posts']:
            sample_post = posts_result['posts'][0]
            print(f"\n📝 샘플 포스트:")
            print(f"   제목: {sample_post['title'][:60]}...")
            print(f"   서브레딧: r/{sample_post['subreddit']}")
            print(f"   점수: {sample_post['score']}")
            print(f"   댓글 수: {sample_post['num_comments']}")
        
        # 네트워크 분석용 텍스트 수집 테스트
        texts = collector.get_texts_for_network_analysis(max_posts=20)
        print(f"\n🕸️ 네트워크 분석용 텍스트: {len(texts)}개")
        
        if texts:
            print(f"   샘플 텍스트: {texts[0][:80]}...")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        print("\n🔧 해결 방법:")
        print("1. .env 파일에 Reddit API 키가 올바르게 설정되어 있는지 확인")
        print("2. 인터넷 연결 상태 확인")
        print("3. Reddit API 사용량 제한 확인")
