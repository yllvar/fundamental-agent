#!/usr/bin/env python3
"""
Reddit 연결 디버깅 스크립트
"""

import os
import sys
from dotenv import load_dotenv
import praw
import logging

# .env 파일 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_reddit_connection():
    """Reddit 연결 테스트"""
    
    print("🔍 Reddit API 연결 디버깅 시작")
    print("=" * 50)
    
    # 1. 환경변수 확인
    print("1️⃣ 환경변수 확인:")
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT', 'EconomicNewsBot/1.0')
    
    print(f"   REDDIT_CLIENT_ID: {'✅ 설정됨' if client_id else '❌ 없음'}")
    print(f"   REDDIT_CLIENT_SECRET: {'✅ 설정됨' if client_secret else '❌ 없음'}")
    print(f"   REDDIT_USER_AGENT: {user_agent}")
    
    if not client_id or not client_secret:
        print("❌ Reddit API 자격증명이 없습니다.")
        return False
    
    # 2. PRAW 설치 확인
    print("\n2️⃣ PRAW 패키지 확인:")
    try:
        import praw
        print(f"   ✅ PRAW 버전: {praw.__version__}")
    except ImportError:
        print("   ❌ PRAW 패키지가 설치되지 않았습니다.")
        print("   설치 명령: pip install praw")
        return False
    
    # 3. Reddit 연결 테스트
    print("\n3️⃣ Reddit API 연결 테스트:")
    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        # 읽기 전용 테스트
        print("   📡 Reddit 서버 연결 중...")
        
        # 간단한 서브레딧 접근 테스트
        subreddit = reddit.subreddit('economics')
        print(f"   ✅ 서브레딧 접근 성공: r/{subreddit.display_name}")
        print(f"   📊 구독자 수: {subreddit.subscribers:,}명")
        
        return reddit
        
    except Exception as e:
        print(f"   ❌ Reddit 연결 실패: {e}")
        print(f"   오류 타입: {type(e).__name__}")
        return False
    
    # 4. 실제 데이터 수집 테스트
    print("\n4️⃣ 실제 데이터 수집 테스트:")
    try:
        # 최신 포스트 1개만 가져오기
        posts = list(reddit.subreddit('economics').hot(limit=1))
        
        if posts:
            post = posts[0]
            print(f"   ✅ 포스트 수집 성공:")
            print(f"   📝 제목: {post.title[:50]}...")
            print(f"   👍 점수: {post.score}")
            print(f"   💬 댓글 수: {post.num_comments}")
            print(f"   🕒 작성 시간: {post.created_utc}")
            return True
        else:
            print("   ⚠️ 포스트를 찾을 수 없습니다.")
            return False
            
    except Exception as e:
        print(f"   ❌ 데이터 수집 실패: {e}")
        return False

def test_multiple_subreddits():
    """여러 서브레딧 테스트"""
    
    print("\n5️⃣ 경제 관련 서브레딧 접근 테스트:")
    
    # .env 파일에서 자격증명 로드
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT', 'EconomicNewsBot/1.0')
    
    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        # 경제 관련 서브레딧들
        subreddits = ['economics', 'investing', 'stocks', 'personalfinance']
        
        for sub_name in subreddits:
            try:
                subreddit = reddit.subreddit(sub_name)
                posts = list(subreddit.hot(limit=1))
                
                if posts:
                    print(f"   ✅ r/{sub_name}: {len(posts)}개 포스트 수집 성공")
                else:
                    print(f"   ⚠️ r/{sub_name}: 포스트 없음")
                    
            except Exception as e:
                print(f"   ❌ r/{sub_name}: 접근 실패 - {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Reddit 클라이언트 생성 실패: {e}")
        return False

if __name__ == "__main__":
    success = test_reddit_connection()
    
    if success:
        test_multiple_subreddits()
        print("\n" + "=" * 50)
        print("✅ Reddit 연결 디버깅 완료 - 정상 작동")
    else:
        print("\n" + "=" * 50)
        print("❌ Reddit 연결 문제 발견 - 수정 필요")
        
        print("\n🔧 해결 방법:")
        print("1. pip install praw 실행")
        print("2. .env 파일의 Reddit API 키 확인")
        print("3. 인터넷 연결 상태 확인")
        print("4. Reddit API 사용량 제한 확인")
