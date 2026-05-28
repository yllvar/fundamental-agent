#!/usr/bin/env python3
"""
통합 소셜 데이터 수집기
Twitter API, 무료 대안, 시뮬레이션 데이터를 통합 관리
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import os
import sys

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from twitter_api_collector import TwitterAPICollector
from free_twitter_alternatives import FreeTwitterAlternatives

class IntegratedSocialCollector:
    """통합 소셜 데이터 수집기"""
    
    def __init__(self):
        """초기화"""
        self.logger = logging.getLogger(__name__)
        
        # Twitter API 수집기 (유료)
        self.twitter_collector = TwitterAPICollector()
        
        # 무료 대안 수집기
        self.free_collector = FreeTwitterAlternatives()
        
        # API 키 존재 여부 확인
        self.has_twitter_api = bool(os.getenv('TWITTER_BEARER_TOKEN'))
        
        self.logger.info(f"✅ 통합 소셜 수집기 초기화 완료 (Twitter API: {'사용 가능' if self.has_twitter_api else '사용 불가'})")
    
    def collect_social_data_for_network_analysis(self, data_source: str = "auto", max_items: int = 100) -> List[str]:
        """네트워크 분석용 소셜 데이터 수집"""
        
        self.logger.info(f"🔍 네트워크 분석용 소셜 데이터 수집 시작 (소스: {data_source})")
        
        texts = []
        
        try:
            if data_source == "auto":
                # 자동 선택: API 키가 있으면 Twitter API, 없으면 무료 대안
                if self.has_twitter_api:
                    data_source = "twitter_api"
                else:
                    data_source = "free_alternatives"
            
            if data_source == "twitter_api" and self.has_twitter_api:
                # Twitter API 사용
                twitter_data = self.twitter_collector.collect_economic_tweets(max_items)
                texts = self._extract_texts_from_twitter_data(twitter_data)
                
            elif data_source == "free_alternatives":
                # 무료 대안 사용
                alternative_data = self.free_collector.collect_alternative_social_data()
                texts = self._extract_texts_from_alternative_data(alternative_data)
                
            elif data_source == "reddit_only":
                # Reddit만 사용
                reddit_data = self.free_collector._collect_reddit_data()
                if reddit_data:
                    texts = [f"{post['title']} {post['text']}" for post in reddit_data['posts']]
                
            elif data_source == "simulation":
                # 시뮬레이션 데이터 사용
                simulation_data = self.free_collector._generate_realistic_simulation()
                texts = [post['text'] for post in simulation_data['posts']]
                
            else:
                # 기본값: 시뮬레이션 데이터
                self.logger.warning(f"알 수 없는 데이터 소스: {data_source}, 시뮬레이션 사용")
                simulation_data = self.free_collector._generate_realistic_simulation()
                texts = [post['text'] for post in simulation_data['posts']]
            
            # 텍스트 정제
            texts = self._clean_texts(texts)
            
            self.logger.info(f"✅ 소셜 데이터 수집 완료: {len(texts)}개 텍스트")
            return texts
            
        except Exception as e:
            self.logger.error(f"❌ 소셜 데이터 수집 실패: {e}")
            # 백업: 시뮬레이션 데이터 사용
            simulation_data = self.free_collector._generate_realistic_simulation()
            return [post['text'] for post in simulation_data['posts']]
    
    def _extract_texts_from_twitter_data(self, twitter_data: Dict[str, Any]) -> List[str]:
        """Twitter API 데이터에서 텍스트 추출"""
        texts = []
        
        if twitter_data.get('status') == 'success':
            for tweet in twitter_data.get('tweets', []):
                text = tweet.get('text', '').strip()
                if text and len(text) > 10:  # 최소 길이 필터
                    texts.append(text)
        
        return texts
    
    def _extract_texts_from_alternative_data(self, alternative_data: Dict[str, Any]) -> List[str]:
        """무료 대안 데이터에서 텍스트 추출"""
        texts = []
        
        for source_name, source_data in alternative_data.get('sources', {}).items():
            if source_name == 'reddit':
                for post in source_data.get('posts', []):
                    title = post.get('title', '').strip()
                    content = post.get('text', '').strip()
                    combined_text = f"{title} {content}".strip()
                    if combined_text and len(combined_text) > 10:
                        texts.append(combined_text)
            
            elif source_name == 'nitter':
                for post in source_data.get('posts', []):
                    text = post.get('text', '').strip()
                    if text and len(text) > 10:
                        texts.append(text)
            
            elif source_name == 'news_comments':
                for comment in source_data.get('comments', []):
                    text = comment.get('text', '').strip()
                    if text and len(text) > 10:
                        texts.append(text)
            
            elif source_name == 'forums':
                for post in source_data.get('posts', []):
                    title = post.get('title', '').strip()
                    content = post.get('content', '').strip()
                    combined_text = f"{title} {content}".strip()
                    if combined_text and len(combined_text) > 10:
                        texts.append(combined_text)
            
            elif source_name == 'simulation':
                for post in source_data.get('posts', []):
                    text = post.get('text', '').strip()
                    if text and len(text) > 10:
                        texts.append(text)
        
        return texts
    
    def _clean_texts(self, texts: List[str]) -> List[str]:
        """텍스트 정제"""
        cleaned_texts = []
        
        for text in texts:
            # 기본 정제
            text = text.strip()
            
            # 너무 짧거나 긴 텍스트 필터
            if 10 <= len(text) <= 1000:
                # URL 제거
                import re
                text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
                
                # 해시태그 정리 (제거하지 않고 공백으로 분리)
                text = re.sub(r'#(\w+)', r'\1', text)
                
                # 멘션 제거
                text = re.sub(r'@\w+', '', text)
                
                # 여러 공백을 하나로
                text = re.sub(r'\s+', ' ', text).strip()
                
                if text:
                    cleaned_texts.append(text)
        
        return cleaned_texts
    
    def get_available_data_sources(self) -> Dict[str, Dict[str, Any]]:
        """사용 가능한 데이터 소스 정보 반환"""
        
        sources = {
            "auto": {
                "name": "자동 선택",
                "description": "API 키 유무에 따라 자동 선택",
                "cost": "무료 또는 유료",
                "reliability": "높음",
                "available": True
            },
            "twitter_api": {
                "name": "Twitter API",
                "description": "공식 Twitter API v2",
                "cost": "$100+/월",
                "reliability": "매우 높음",
                "available": self.has_twitter_api,
                "note": "API 키 필요" if not self.has_twitter_api else "사용 가능"
            },
            "free_alternatives": {
                "name": "무료 대안",
                "description": "Reddit + Nitter + 뉴스 댓글",
                "cost": "무료",
                "reliability": "보통",
                "available": True
            },
            "reddit_only": {
                "name": "Reddit 전용",
                "description": "Reddit 경제 서브레딧",
                "cost": "무료",
                "reliability": "높음",
                "available": True
            },
            "simulation": {
                "name": "시뮬레이션",
                "description": "현실적인 샘플 데이터",
                "cost": "무료",
                "reliability": "보통",
                "available": True,
                "note": "테스트 및 데모용"
            }
        }
        
        return sources
    
    def test_all_sources(self) -> Dict[str, Any]:
        """모든 데이터 소스 테스트"""
        
        self.logger.info("🧪 모든 데이터 소스 테스트 시작")
        
        test_results = {}
        sources = self.get_available_data_sources()
        
        for source_id, source_info in sources.items():
            if not source_info['available']:
                test_results[source_id] = {
                    'status': 'unavailable',
                    'reason': source_info.get('note', 'Not available')
                }
                continue
            
            try:
                self.logger.info(f"🔍 {source_info['name']} 테스트 중...")
                
                texts = self.collect_social_data_for_network_analysis(
                    data_source=source_id, 
                    max_items=10
                )
                
                test_results[source_id] = {
                    'status': 'success',
                    'text_count': len(texts),
                    'sample_text': texts[0] if texts else None,
                    'cost': source_info['cost'],
                    'reliability': source_info['reliability']
                }
                
                self.logger.info(f"✅ {source_info['name']}: {len(texts)}개 텍스트 수집")
                
            except Exception as e:
                test_results[source_id] = {
                    'status': 'error',
                    'error': str(e),
                    'cost': source_info['cost'],
                    'reliability': source_info['reliability']
                }
                
                self.logger.error(f"❌ {source_info['name']} 테스트 실패: {e}")
        
        return test_results

if __name__ == "__main__":
    # 테스트 실행
    collector = IntegratedSocialCollector()
    
    print("🔍 사용 가능한 데이터 소스:")
    sources = collector.get_available_data_sources()
    
    for source_id, info in sources.items():
        status = "✅" if info['available'] else "❌"
        print(f"{status} {info['name']}: {info['description']} ({info['cost']})")
        if 'note' in info:
            print(f"   📝 {info['note']}")
    
    print("\n🧪 전체 소스 테스트:")
    test_results = collector.test_all_sources()
    
    for source_id, result in test_results.items():
        if result['status'] == 'success':
            print(f"✅ {source_id}: {result['text_count']}개 텍스트 수집 성공")
        elif result['status'] == 'unavailable':
            print(f"⚠️ {source_id}: {result['reason']}")
        else:
            print(f"❌ {source_id}: {result['error']}")
    
    print("\n💡 권장사항:")
    if collector.has_twitter_api:
        print("- Twitter API 키가 있으므로 'twitter_api' 또는 'auto' 사용 권장")
    else:
        print("- Twitter API 키가 없으므로 'free_alternatives' 또는 'reddit_only' 사용 권장")
        print("- 테스트 목적이라면 'simulation' 사용 가능")
