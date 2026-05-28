#!/usr/bin/env python3
"""
자동 기사 생성을 위한 이벤트 시스템
5분마다 무조건 기사를 생성하기 위한 이벤트 생성
"""

import logging
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import yfinance as yf
import numpy as np
import random

# 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from data_monitoring.enhanced_data_collector import EnhancedGlobalDataCollector
except ImportError:
    # 대체 구현
    class EnhancedGlobalDataCollector:
        def __init__(self):
            pass

class AutoArticleEventSystem:
    """자동 기사 생성을 위한 이벤트 시스템"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_collector = EnhancedGlobalDataCollector()
        
        # 주요 모니터링 심볼
        self.symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA',
            '^GSPC', '^IXIC', '^DJI', '^VIX'
        ]
        
        # 기사 주제 템플릿
        self.article_topics = [
            "시장 동향 분석",
            "주요 종목 분석", 
            "경제 지표 해석",
            "섹터별 성과 분석",
            "투자 전략 제안",
            "글로벌 시장 영향",
            "기술적 분석",
            "펀더멘털 분석"
        ]
    
    def detect_events(self) -> List[Dict[str, Any]]:
        """이벤트 감지 - 항상 최소 1개 이벤트 반환"""
        try:
            self.logger.info("🔍 자동 기사 생성용 이벤트 감지 시작")
            
            events = []
            
            # 1. 실제 시장 데이터 기반 이벤트 생성
            market_events = self._generate_market_events()
            events.extend(market_events)
            
            # 2. 경제 지표 기반 이벤트 생성
            economic_events = self._generate_economic_events()
            events.extend(economic_events)
            
            # 3. 최소 1개 이벤트 보장
            if not events:
                events = self._generate_fallback_events()
            
            # 최대 3개 이벤트로 제한
            events = events[:3]
            
            self.logger.info(f"✅ {len(events)}개 이벤트 생성 완료")
            return events
            
        except Exception as e:
            self.logger.error(f"❌ 이벤트 감지 실패: {str(e)}")
            # 실패 시에도 기본 이벤트 반환
            return self._generate_fallback_events()
    
    def _generate_market_events(self) -> List[Dict[str, Any]]:
        """실제 시장 데이터 기반 이벤트 생성"""
        events = []
        
        try:
            # 랜덤하게 2-3개 심볼 선택
            selected_symbols = random.sample(self.symbols, min(3, len(self.symbols)))
            
            for symbol in selected_symbols:
                try:
                    # 최근 2일 데이터 가져오기
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='2d')
                    
                    if len(hist) >= 2:
                        current_price = hist['Close'].iloc[-1]
                        prev_price = hist['Close'].iloc[-2]
                        change_percent = ((current_price - prev_price) / prev_price) * 100
                        volume = hist['Volume'].iloc[-1]
                        
                        # 이벤트 생성 조건
                        if abs(change_percent) > 0.5:  # 0.5% 이상 변동
                            event_type = "price_movement"
                            if change_percent > 0:
                                description = f"{symbol} 주가 {change_percent:.2f}% 상승"
                                sentiment = "positive"
                            else:
                                description = f"{symbol} 주가 {abs(change_percent):.2f}% 하락"
                                sentiment = "negative"
                            
                            severity = min(abs(change_percent) / 10, 1.0)  # 최대 1.0
                            
                            events.append({
                                'type': event_type,
                                'symbol': symbol,
                                'description': description,
                                'severity': severity,
                                'sentiment': sentiment,
                                'price': float(current_price),
                                'change_percent': float(change_percent),
                                'volume': int(volume),
                                'timestamp': datetime.now().isoformat(),
                                'source': 'market_data'
                            })
                
                except Exception as e:
                    self.logger.warning(f"심볼 {symbol} 데이터 수집 실패: {str(e)}")
                    continue
        
        except Exception as e:
            self.logger.error(f"시장 이벤트 생성 실패: {str(e)}")
        
        return events
    
    def _generate_economic_events(self) -> List[Dict[str, Any]]:
        """경제 지표 기반 이벤트 생성"""
        events = []
        
        try:
            # VIX 기반 변동성 이벤트
            vix_ticker = yf.Ticker('^VIX')
            vix_hist = vix_ticker.history(period='2d')
            
            if len(vix_hist) >= 2:
                current_vix = vix_hist['Close'].iloc[-1]
                prev_vix = vix_hist['Close'].iloc[-2]
                vix_change = current_vix - prev_vix
                
                if abs(vix_change) > 1.0:  # VIX 1포인트 이상 변동
                    if vix_change > 0:
                        description = f"VIX 지수 {vix_change:.2f} 상승, 시장 불안감 증가"
                        sentiment = "negative"
                    else:
                        description = f"VIX 지수 {abs(vix_change):.2f} 하락, 시장 안정성 개선"
                        sentiment = "positive"
                    
                    events.append({
                        'type': 'volatility_change',
                        'symbol': '^VIX',
                        'description': description,
                        'severity': min(abs(vix_change) / 10, 1.0),
                        'sentiment': sentiment,
                        'vix_level': float(current_vix),
                        'vix_change': float(vix_change),
                        'timestamp': datetime.now().isoformat(),
                        'source': 'economic_indicator'
                    })
        
        except Exception as e:
            self.logger.warning(f"경제 이벤트 생성 실패: {str(e)}")
        
        return events
    
    def _generate_fallback_events(self) -> List[Dict[str, Any]]:
        """기본 이벤트 생성 (실패 시 또는 이벤트가 없을 때)"""
        
        # 현재 시간 기반으로 다양한 주제 선택
        current_hour = datetime.now().hour
        
        if 9 <= current_hour < 12:  # 오전
            topic = "시장 개장 분석"
            description = "오늘 시장 개장 후 주요 동향 분석"
        elif 12 <= current_hour < 15:  # 오후
            topic = "중간 시장 점검"
            description = "오늘 오후 시장 중간 점검 및 동향 분석"
        elif 15 <= current_hour < 18:  # 저녁
            topic = "시장 마감 분석"
            description = "오늘 시장 마감 후 종합 분석"
        else:  # 야간
            topic = "글로벌 시장 동향"
            description = "해외 시장 동향 및 내일 전망"
        
        # 랜덤 심볼 선택
        symbol = random.choice(['AAPL', 'MSFT', 'GOOGL', '^GSPC', '^IXIC'])
        
        return [{
            'type': 'scheduled_analysis',
            'symbol': symbol,
            'description': description,
            'topic': topic,
            'severity': 0.6,  # 중간 정도 중요도
            'sentiment': 'neutral',
            'timestamp': datetime.now().isoformat(),
            'source': 'scheduled_generation',
            'article_type': random.choice(self.article_topics)
        }]
    
    def get_market_context(self) -> Dict[str, Any]:
        """현재 시장 컨텍스트 정보 제공"""
        try:
            context = {
                'timestamp': datetime.now().isoformat(),
                'market_session': self._get_market_session(),
                'major_indices': {},
                'market_sentiment': 'neutral'
            }
            
            # 주요 지수 정보
            major_indices = ['^GSPC', '^IXIC', '^DJI']
            for index in major_indices:
                try:
                    ticker = yf.Ticker(index)
                    hist = ticker.history(period='1d')
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        context['major_indices'][index] = {
                            'price': float(current_price),
                            'name': self._get_index_name(index)
                        }
                except:
                    continue
            
            return context
            
        except Exception as e:
            self.logger.error(f"시장 컨텍스트 생성 실패: {str(e)}")
            return {
                'timestamp': datetime.now().isoformat(),
                'market_session': 'unknown',
                'major_indices': {},
                'market_sentiment': 'neutral'
            }
    
    def _get_market_session(self) -> str:
        """현재 시장 세션 판단"""
        current_hour = datetime.now().hour
        
        if 9 <= current_hour < 16:
            return 'regular_hours'
        elif 4 <= current_hour < 9:
            return 'pre_market'
        elif 16 <= current_hour < 20:
            return 'after_hours'
        else:
            return 'closed'
    
    def _get_index_name(self, symbol: str) -> str:
        """지수 심볼을 이름으로 변환"""
        names = {
            '^GSPC': 'S&P 500',
            '^IXIC': 'NASDAQ',
            '^DJI': 'Dow Jones',
            '^VIX': 'VIX'
        }
        return names.get(symbol, symbol)

def main():
    """테스트 실행"""
    logging.basicConfig(level=logging.INFO)
    
    system = AutoArticleEventSystem()
    
    print("=== 자동 기사 생성용 이벤트 시스템 테스트 ===")
    
    # 이벤트 감지 테스트
    events = system.detect_events()
    print(f"\n📊 감지된 이벤트: {len(events)}개")
    
    for i, event in enumerate(events, 1):
        print(f"\n이벤트 {i}:")
        print(f"  유형: {event['type']}")
        print(f"  심볼: {event['symbol']}")
        print(f"  설명: {event['description']}")
        print(f"  심각도: {event['severity']:.2f}")
        print(f"  감정: {event['sentiment']}")
    
    # 시장 컨텍스트 테스트
    context = system.get_market_context()
    print(f"\n🌍 시장 컨텍스트:")
    print(f"  세션: {context['market_session']}")
    print(f"  주요 지수: {len(context['major_indices'])}개")
    
    print("\n✅ 테스트 완료!")

if __name__ == "__main__":
    main()
