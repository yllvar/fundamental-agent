#!/usr/bin/env python3
"""
아시아 시장 포함 종합 경제 데이터 모니터링 시스템
모든 API (Yahoo Finance, Alpha Vantage, FRED, Reddit)와 아시아 시장을 활용한 통합 모니터링
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 프로젝트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 기존 모듈들 import
from data_monitoring.enhanced_data_collector import EnhancedGlobalDataCollector
from data_monitoring.fred_data_collector import FREDDataCollector
from data_monitoring.real_reddit_collector import RealRedditCollector
from data_monitoring.alphavantage_intelligence_complete import AlphaVantageIntelligenceComplete
from data_monitoring.integrated_event_system import IntegratedEventSystem
from data_monitoring.asian_markets_collector import AsianMarketsCollector
from notifications.telegram_notifier import TelegramNotifier

class ComprehensiveEconomicMonitorWithAsia:
    """아시아 시장 포함 종합 경제 데이터 모니터링 시스템"""
    
    def __init__(self):
        """모니터링 시스템 초기화"""
        self.logger = logging.getLogger(__name__)
        
        # 데이터 수집기들 초기화
        self.init_data_collectors()
        
        # 모니터링 설정 (아시아 시장 포함)
        self.monitoring_config = {
            'update_interval': 60,  # 60초마다 업데이트
            'symbols': [
                # 미국 주요 지수
                '^GSPC', '^IXIC', '^DJI', '^VIX', '^RUT',
                
                # 아시아 주요 지수
                '^KS11',      # KOSPI (한국)
                '^N225',      # Nikkei 225 (일본)
                '000001.SS',  # Shanghai Composite (중국)
                '^HSI',       # Hang Seng (홍콩)
                '^TWII',      # Taiwan Weighted (대만)
                '^STI',       # Straits Times (싱가포르)
                '^BSESN',     # BSE Sensex (인도)
                
                # 미국 주요 주식
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META',
                
                # 아시아 주요 주식 (ADR)
                'TSM',        # Taiwan Semiconductor
                'BABA',       # Alibaba
                'TCEHY',      # Tencent
                '005930.KS',  # Samsung Electronics
                'NIO',        # NIO (중국 전기차)
                
                # 통화 (아시아 통화 포함)
                'EURUSD=X', 'USDJPY=X', 'GBPUSD=X', 'USDKRW=X',
                'USDCNY=X', 'USDHKD=X', 'USDSGD=X', 'USDINR=X',
                
                # 원자재
                'GC=F', 'CL=F', 'BTC-USD', 'ETH-USD',
                
                # 채권
                '^TNX', '^TYX', '^FVX'
            ],
            'fred_indicators': [
                'FEDFUNDS', 'GS10', 'CPIAUCSL', 'UNRATE', 'GDP'
            ],
            'reddit_subreddits': [
                'economics', 'investing', 'stocks', 'SecurityAnalysis'
            ],
            'asian_markets': [
                'korea', 'japan', 'china', 'hongkong', 'taiwan', 'singapore', 'india'
            ]
        }
        
        # 데이터 저장소
        self.market_data = {}
        self.economic_indicators = {}
        self.social_sentiment = {}
        self.news_data = {}
        self.asian_market_data = {}
        self.events_history = []
        
        # Telegram 알림 설정
        telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.telegram_notifier = TelegramNotifier(telegram_bot_token, telegram_chat_id) if telegram_bot_token and telegram_chat_id else None
        if self.telegram_notifier:
            self.logger.info("✅ Telegram 알림 설정 완료")
        else:
            self.logger.warning("⚠️ Telegram 알림이 설정되지 않음")
    
    def init_data_collectors(self):
        """데이터 수집기들 초기화"""
        try:
            # Yahoo Finance 기반 글로벌 데이터 수집기
            self.global_collector = EnhancedGlobalDataCollector()
            self.logger.info("✅ Yahoo Finance 수집기 초기화 완료")
            
            # 아시아 시장 전용 수집기
            self.asian_collector = AsianMarketsCollector()
            self.logger.info("✅ 아시아 시장 수집기 초기화 완료")
            
            # FRED 경제 지표 수집기
            fred_api_key = os.getenv('FRED_API_KEY')
            if fred_api_key:
                self.fred_collector = FREDDataCollector(fred_api_key)
                self.logger.info("✅ FRED 수집기 초기화 완료")
            else:
                self.fred_collector = None
                self.logger.warning("⚠️ FRED API 키 없음")
            
            # Reddit 소셜 데이터 수집기
            try:
                self.reddit_collector = RealRedditCollector()
                self.logger.info("✅ Reddit 수집기 초기화 완료")
            except Exception as e:
                self.reddit_collector = None
                self.logger.warning(f"⚠️ Reddit 수집기 초기화 실패: {e}")
            
            # Alpha Vantage 인텔리전스 수집기
            alpha_api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
            if alpha_api_key:
                try:
                    self.alpha_collector = AlphaVantageIntelligenceComplete()
                    self.logger.info("✅ Alpha Vantage 수집기 초기화 완료")
                except Exception as e:
                    self.alpha_collector = None
                    self.logger.warning(f"⚠️ Alpha Vantage 수집기 초기화 실패: {e}")
            else:
                self.alpha_collector = None
                self.logger.warning("⚠️ Alpha Vantage API 키 없음")
            
            # 이벤트 감지 시스템
            self.event_system = IntegratedEventSystem()
            self.logger.info("✅ 이벤트 감지 시스템 초기화 완료")
            
        except Exception as e:
            self.logger.error(f"❌ 데이터 수집기 초기화 실패: {e}")
            raise
    
    async def collect_market_data(self) -> Dict[str, Any]:
        """시장 데이터 수집 (아시아 시장 포함)"""
        try:
            self.logger.info("📊 글로벌 시장 데이터 수집 시작...")
            
            # Yahoo Finance 데이터 수집 (올바른 메서드 이름 사용)
            market_data = await self.global_collector.collect_all_market_data()
            
            # 아시아 시장 데이터 추가 수집
            try:
                self.logger.info("🌏 아시아 시장 데이터 수집 중...")
                asian_data = await asyncio.to_thread(
                    self.asian_collector.collect_all_asian_markets
                )
                market_data['asian_markets'] = asian_data
                self.asian_market_data = asian_data
                self.logger.info(f"✅ 아시아 시장 데이터 수집 완료: {len(asian_data)} 시장")
            except Exception as e:
                self.logger.warning(f"⚠️ 아시아 시장 데이터 수집 실패: {e}")
            
            # Alpha Vantage 데이터 추가 (있는 경우)
            if self.alpha_collector:
                try:
                    alpha_data = await asyncio.to_thread(
                        self.alpha_collector.collect_comprehensive_intelligence_data
                    )
                    market_data['alpha_vantage'] = alpha_data
                    self.logger.info("✅ Alpha Vantage 데이터 추가 완료")
                except Exception as e:
                    self.logger.warning(f"⚠️ Alpha Vantage 데이터 수집 실패: {e}")
            
            # FRED 데이터 추가 (있는 경우)
            if hasattr(self.global_collector, 'collect_fred_data'):
                try:
                    fred_data = await asyncio.to_thread(
                        self.global_collector.collect_fred_data
                    )
                    market_data['fred_data'] = fred_data
                    self.logger.info("✅ FRED 데이터 추가 완료")
                except Exception as e:
                    self.logger.warning(f"⚠️ FRED 데이터 수집 실패: {e}")
            
            # 뉴스 데이터 추가
            if hasattr(self.global_collector, 'collect_enhanced_news_data'):
                try:
                    news_data = await asyncio.to_thread(
                        self.global_collector.collect_enhanced_news_data
                    )
                    market_data['news_data'] = news_data
                    self.logger.info("✅ 뉴스 데이터 추가 완료")
                except Exception as e:
                    self.logger.warning(f"⚠️ 뉴스 데이터 수집 실패: {e}")
            
            self.market_data = market_data
            self.logger.info(f"✅ 글로벌 시장 데이터 수집 완료: {len(market_data)} 항목")
            
            return market_data
            
        except Exception as e:
            self.logger.error(f"❌ 시장 데이터 수집 실패: {e}")
            return {}
    
    async def collect_economic_indicators(self) -> Dict[str, Any]:
        """경제 지표 수집"""
        if not self.fred_collector:
            self.logger.info("📈 FRED 수집기가 없어 경제 지표 수집 건너뜀")
            return {}
        
        try:
            self.logger.info("📈 경제 지표 수집 시작...")
            
            indicators = {}
            for indicator in self.monitoring_config['fred_indicators']:
                try:
                    data = await asyncio.to_thread(
                        self.fred_collector.get_series_data, 
                        indicator, 
                        limit=10
                    )
                    if data:
                        indicators[indicator] = data
                        self.logger.info(f"✅ {indicator} 데이터 수집 완료")
                    else:
                        self.logger.warning(f"⚠️ {indicator} 데이터 없음")
                except Exception as e:
                    self.logger.warning(f"⚠️ {indicator} 수집 실패: {e}")
            
            self.economic_indicators = indicators
            self.logger.info(f"✅ 경제 지표 수집 완료: {len(indicators)} 지표")
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"❌ 경제 지표 수집 실패: {e}")
            return {}
    
    async def collect_social_sentiment(self) -> Dict[str, Any]:
        """소셜 미디어 감정 분석"""
        if not self.reddit_collector:
            self.logger.info("💬 Reddit 수집기가 없어 소셜 감정 분석 건너뜀")
            return {}
        
        try:
            self.logger.info("💬 소셜 감정 분석 시작...")
            
            sentiment_data = {}
            
            # Reddit 경제 포스트 수집 (올바른 메서드 사용)
            try:
                reddit_posts = await asyncio.to_thread(
                    self.reddit_collector.collect_economic_posts,
                    max_posts_per_subreddit=20
                )
                
                if reddit_posts and 'subreddit_data' in reddit_posts:
                    for subreddit, data in reddit_posts['subreddit_data'].items():
                        posts = data.get('posts', [])
                        if posts:
                            # 감정 점수 계산
                            sentiment_score = self.calculate_sentiment_score(posts)
                            sentiment_data[subreddit] = {
                                'posts': posts,
                                'sentiment_score': sentiment_score,
                                'post_count': len(posts),
                                'avg_score': data.get('avg_score', 0),
                                'total_comments': data.get('total_comments', 0)
                            }
                            self.logger.info(f"✅ r/{subreddit} 감정 분석 완료: {sentiment_score:.2f}")
                
            except Exception as e:
                self.logger.warning(f"⚠️ Reddit 데이터 수집 실패: {e}")
            
            self.social_sentiment = sentiment_data
            self.logger.info(f"✅ 소셜 감정 분석 완료: {len(sentiment_data)} 서브레딧")
            
            return sentiment_data
            
        except Exception as e:
            self.logger.error(f"❌ 소셜 감정 분석 실패: {e}")
            return {}
    
    def calculate_sentiment_score(self, posts: List[Dict]) -> float:
        """게시물들의 감정 점수 계산"""
        if not posts:
            return 0.0
        
        # 간단한 감정 분석 (키워드 기반)
        positive_keywords = ['bull', 'buy', 'up', 'gain', 'profit', 'good', 'great', 'excellent', 'rise', 'surge']
        negative_keywords = ['bear', 'sell', 'down', 'loss', 'crash', 'bad', 'terrible', 'awful', 'fall', 'drop']
        
        total_score = 0
        for post in posts:
            title = post.get('title', '').lower()
            score = post.get('score', 0)
            
            # 키워드 기반 감정 점수
            sentiment = 0
            for keyword in positive_keywords:
                if keyword in title:
                    sentiment += 1
            for keyword in negative_keywords:
                if keyword in title:
                    sentiment -= 1
            
            # 업보트 점수 반영 (가중치 적용)
            weighted_sentiment = sentiment * (1 + min(score, 100) / 100)
            total_score += weighted_sentiment
        
        return total_score / len(posts)
    
    async def detect_events(self) -> List[Dict[str, Any]]:
        """이벤트 감지"""
        try:
            self.logger.info("🚨 이벤트 감지 시작...")
            
            # 통합 이벤트 시스템 실행 (비동기 처리)
            events = await self.event_system.run_comprehensive_analysis()
            
            # 새로운 이벤트만 필터링
            new_events = []
            for event in events:
                # 이벤트 고유 식별자 생성
                event_id = f"{event.get('symbol', '')}_{event.get('event_type', '')}_{event.get('timestamp', '')}"
                
                # 중복 확인
                existing_ids = [f"{e.get('symbol', '')}_{e.get('event_type', '')}_{e.get('timestamp', '')}" 
                               for e in self.events_history]
                
                if event_id not in existing_ids:
                    new_events.append(event)
                    self.events_history.append(event)
            
            # 이벤트 히스토리 크기 제한 (최대 100개)
            if len(self.events_history) > 100:
                self.events_history = self.events_history[-100:]
            
            self.logger.info(f"✅ 이벤트 감지 완료: {len(new_events)} 새 이벤트")
            
            # 중요한 이벤트는 Telegram 알림
            for event in new_events:
                if event.get('severity', 0) > 0.6:
                    await self.send_event_alert(event)
            
            return new_events
            
        except Exception as e:
            self.logger.error(f"❌ 이벤트 감지 실패: {e}")
            return []
    
    async def send_event_alert(self, event: Dict[str, Any]):
        """이벤트 Telegram 알림 전송"""
        telegram_sent = False
        
        # Telegram 알림 전송
        if self.telegram_notifier:
            try:
                symbol = event.get('symbol', 'Unknown')
                event_type = event.get('event_type', 'Unknown')
                severity = event.get('severity', 0)
                description = event.get('description', 'No description')
                
                is_asian = symbol in ['^KS11', '^N225', '000001.SS', '^HSI', '^TWII', '^STI', '^BSESN']
                region_emoji = "🌏" if is_asian else "🇺🇸"
                
                tg_message = f"{region_emoji} <b>시장 이벤트 감지</b>\n\n<b>종목</b>: {symbol}\n<b>유형</b>: {event_type}\n<b>심각도</b>: {severity:.2f}\n<b>설명</b>: {description}\n<b>시간</b>: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                await self.telegram_notifier._send_telegram(tg_message)
                self.logger.info(f"📱 Telegram 알림 전송: {symbol} {event_type}")
                telegram_sent = True
                
            except Exception as e:
                self.logger.error(f"❌ Telegram 알림 전송 실패: {e}")
    
    async def run_comprehensive_monitoring(self) -> Dict[str, Any]:
        """종합 모니터링 실행 (아시아 시장 포함)"""
        start_time = datetime.now()
        self.logger.info("🚀 글로벌 종합 경제 모니터링 시작...")
        
        try:
            # 병렬로 모든 데이터 수집
            tasks = [
                self.collect_market_data(),
                self.collect_economic_indicators(),
                self.collect_social_sentiment(),
                self.detect_events()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            market_data, economic_data, social_data, events = results
            
            # 예외 처리
            if isinstance(market_data, Exception):
                self.logger.error(f"시장 데이터 수집 오류: {market_data}")
                market_data = {}
            
            if isinstance(economic_data, Exception):
                self.logger.error(f"경제 지표 수집 오류: {economic_data}")
                economic_data = {}
            
            if isinstance(social_data, Exception):
                self.logger.error(f"소셜 데이터 수집 오류: {social_data}")
                social_data = {}
            
            if isinstance(events, Exception):
                self.logger.error(f"이벤트 감지 오류: {events}")
                events = []
            
            # 결과 통합
            comprehensive_data = {
                'timestamp': start_time.isoformat(),
                'market_data': market_data,
                'economic_indicators': economic_data,
                'social_sentiment': social_data,
                'detected_events': events,
                'asian_market_data': self.asian_market_data,
                'summary': {
                    'market_symbols': len(market_data.get('us_stocks', {})),
                    'asian_markets': len(self.asian_market_data),
                    'economic_indicators': len(economic_data),
                    'social_platforms': len(social_data),
                    'new_events': len(events),
                    'processing_time': (datetime.now() - start_time).total_seconds()
                }
            }
            
            # 결과 저장
            await self.save_monitoring_result(comprehensive_data)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            self.logger.info(f"✅ 글로벌 종합 모니터링 완료 ({processing_time:.2f}초)")
            self.logger.info(f"📊 수집 결과: 시장 {len(market_data.get('us_stocks', {}))}개, "
                           f"아시아 {len(self.asian_market_data)}개, "
                           f"경제지표 {len(economic_data)}개, "
                           f"소셜 {len(social_data)}개, "
                           f"이벤트 {len(events)}개")
            
            return comprehensive_data
            
        except Exception as e:
            self.logger.error(f"❌ 종합 모니터링 실패: {e}")
            return {
                'timestamp': start_time.isoformat(),
                'error': str(e),
                'market_data': {},
                'economic_indicators': {},
                'social_sentiment': {},
                'detected_events': [],
                'asian_market_data': {}
            }
    
    async def save_monitoring_result(self, data: Dict[str, Any]):
        """모니터링 결과 저장"""
        try:
            # 출력 디렉토리 생성
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            
            # 타임스탬프 기반 파일명
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/comprehensive_monitoring_with_asia_{timestamp}.json"
            
            # JSON 파일로 저장
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            self.logger.info(f"💾 모니터링 결과 저장: {filename}")
            
        except Exception as e:
            self.logger.error(f"❌ 결과 저장 실패: {e}")
    
    def get_latest_data(self) -> Dict[str, Any]:
        """최신 수집 데이터 반환"""
        return {
            'market_data': self.market_data,
            'economic_indicators': self.economic_indicators,
            'social_sentiment': self.social_sentiment,
            'asian_market_data': self.asian_market_data,
            'events_count': len(self.events_history)
        }

# 실행 함수
async def main():
    """메인 실행 함수"""
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 모니터링 시스템 초기화 및 실행
    monitor = ComprehensiveEconomicMonitorWithAsia()
    result = await monitor.run_comprehensive_monitoring()
    
    print("\n" + "="*60)
    print("🎯 글로벌 종합 경제 모니터링 결과")
    print("="*60)
    print(f"📊 미국 시장: {len(result.get('market_data', {}).get('us_stocks', {}))}개 종목")
    print(f"🌏 아시아 시장: {len(result.get('asian_market_data', {}))}개 시장")
    print(f"📈 경제 지표: {len(result.get('economic_indicators', {}))}개 지표")
    print(f"💬 소셜 데이터: {len(result.get('social_sentiment', {}))}개 플랫폼")
    print(f"🚨 감지 이벤트: {len(result.get('detected_events', []))}개")
    print(f"⏱️ 처리 시간: {result.get('summary', {}).get('processing_time', 0):.2f}초")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
