"""
고도화된 경제 이벤트 탐지 모듈
기술적 분석, 감정 분석, 상관관계 분석을 통합한 종합 이벤트 감지 시스템
"""

import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_monitoring.technical_analysis import TechnicalAnalyzer, TechnicalIndicators, TechnicalSignal
from data_monitoring.sentiment_analysis import SentimentAnalyzer, MarketSentiment, SentimentScore
from data_monitoring.correlation_analysis import CorrelationAnalyzer, MarketCorrelationBreak
from data_monitoring.data_collector import MarketData, EconomicDataCollector

class AdvancedEventType(Enum):
    # 기존 이벤트 타입
    SURGE = "surge"
    DROP = "drop"
    VOLATILITY = "volatility"
    VOLUME_SPIKE = "volume_spike"
    CORRELATION_BREAK = "correlation_break"
    
    # 새로운 고급 이벤트 타입
    TECHNICAL_BREAKOUT = "technical_breakout"      # 기술적 돌파
    SENTIMENT_SHIFT = "sentiment_shift"            # 감정 급변
    MOMENTUM_DIVERGENCE = "momentum_divergence"    # 모멘텀 다이버전스
    SECTOR_ROTATION = "sector_rotation"            # 섹터 로테이션
    MARKET_REGIME_CHANGE = "market_regime_change"  # 시장 체제 변화
    LIQUIDITY_CRISIS = "liquidity_crisis"          # 유동성 위기
    RISK_OFF = "risk_off"                          # 위험 회피
    RISK_ON = "risk_on"                            # 위험 선호

@dataclass
class AdvancedEconomicEvent:
    event_id: str
    symbol: str
    name: str
    event_type: AdvancedEventType
    severity: float  # 0-1 scale
    confidence: float  # 0-1 scale
    timestamp: datetime
    
    # 기본 시장 데이터
    current_price: float
    change_percent: float
    volume: int
    
    # 기술적 분석 데이터
    technical_indicators: Optional[TechnicalIndicators] = None
    technical_signal: Optional[TechnicalSignal] = None
    
    # 감정 분석 데이터
    market_sentiment: Optional[MarketSentiment] = None
    sentiment_score: float = 0.0
    
    # 상관관계 데이터
    correlation_breaks: List[MarketCorrelationBreak] = field(default_factory=list)
    
    # 이벤트 설명 및 컨텍스트
    description: str = ""
    detailed_analysis: str = ""
    trading_implications: str = ""
    risk_assessment: str = ""
    
    # 관련 심볼들
    related_symbols: List[str] = field(default_factory=list)
    
    # 예상 지속 시간
    expected_duration: str = "short"  # "short", "medium", "long"

class AdvancedEventDetector:
    """고도화된 경제 이벤트 탐지 클래스"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 분석 모듈들 초기화
        self.technical_analyzer = TechnicalAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.correlation_analyzer = CorrelationAnalyzer()
        self.data_collector = EconomicDataCollector()
        
        # 이벤트 히스토리 및 쿨다운 관리
        self.event_history = []
        self.alert_cooldown = {}
        
        # 임계값 설정
        self.thresholds = {
            'price_change_major': 5.0,      # 5% 이상 변동
            'price_change_extreme': 10.0,   # 10% 이상 변동
            'volume_spike': 3.0,            # 평균 대비 3배 이상
            'volatility_high': 15.0,        # 15% 이상 일중 변동성
            'sentiment_shift': 0.4,         # 감정 점수 0.4 이상 변화
            'correlation_break': 0.3,       # 상관관계 0.3 이상 이탈
            'rsi_overbought': 70,           # RSI 과매수
            'rsi_oversold': 30,             # RSI 과매도
        }
    
    async def detect_advanced_events(self, symbols: List[str]) -> List[AdvancedEconomicEvent]:
        """고도화된 이벤트 탐지 메인 함수"""
        all_events = []
        
        try:
            # 1. 기본 시장 데이터 수집
            market_data = await self._collect_market_data(symbols)
            
            # 2. 각 심볼별 개별 분석
            for symbol in symbols:
                if symbol not in market_data:
                    continue
                
                symbol_events = await self._analyze_symbol_events(symbol, market_data[symbol])
                all_events.extend(symbol_events)
            
            # 3. 시장 전체 분석 (상관관계, 섹터 로테이션 등)
            market_wide_events = await self._analyze_market_wide_events(symbols, market_data)
            all_events.extend(market_wide_events)
            
            # 4. 이벤트 필터링 및 우선순위 정렬
            filtered_events = self._filter_and_prioritize_events(all_events)
            
            # 5. 이벤트 히스토리 업데이트
            self._update_event_history(filtered_events)
            
            return filtered_events
            
        except Exception as e:
            self.logger.error(f"Error in advanced event detection: {str(e)}")
            return []
    
    async def _collect_market_data(self, symbols: List[str]) -> Dict[str, MarketData]:
        """시장 데이터 수집"""
        market_data = {}
        
        for symbol in symbols:
            try:
                data = self.data_collector.collect_yahoo_finance_data(symbol)
                if data:
                    market_data[symbol] = data
            except Exception as e:
                self.logger.error(f"Error collecting data for {symbol}: {str(e)}")
                continue
        
        return market_data
    
    async def _analyze_symbol_events(self, symbol: str, market_data: MarketData) -> List[AdvancedEconomicEvent]:
        """개별 심볼 이벤트 분석"""
        events = []
        
        try:
            # 기술적 분석 수행
            technical_indicators = self.technical_analyzer.analyze_symbol(symbol)
            
            # 감정 분석 수행
            market_sentiment = await self.sentiment_analyzer.analyze_market_sentiment(symbol)
            
            # 1. 기술적 돌파 이벤트 감지
            technical_events = self._detect_technical_events(
                symbol, market_data, technical_indicators
            )
            events.extend(technical_events)
            
            # 2. 감정 변화 이벤트 감지
            sentiment_events = self._detect_sentiment_events(
                symbol, market_data, market_sentiment
            )
            events.extend(sentiment_events)
            
            # 3. 모멘텀 다이버전스 감지
            momentum_events = self._detect_momentum_divergence(
                symbol, market_data, technical_indicators
            )
            events.extend(momentum_events)
            
            # 4. 극단적 가격/거래량 이벤트
            extreme_events = self._detect_extreme_events(
                symbol, market_data, technical_indicators, market_sentiment
            )
            events.extend(extreme_events)
            
        except Exception as e:
            self.logger.error(f"Error analyzing events for {symbol}: {str(e)}")
        
        return events
    
    def _detect_technical_events(self, symbol: str, market_data: MarketData, 
                                technical_indicators: Optional[TechnicalIndicators]) -> List[AdvancedEconomicEvent]:
        """기술적 분석 기반 이벤트 감지"""
        events = []
        
        if not technical_indicators:
            return events
        
        current_price = market_data.current_price
        
        # 1. 볼린저 밴드 돌파
        if current_price > technical_indicators.bollinger_upper:
            severity = min(1.0, (current_price - technical_indicators.bollinger_upper) / 
                          technical_indicators.bollinger_upper * 10)
            
            event = AdvancedEconomicEvent(
                event_id=f"{symbol}_BOLLINGER_BREAKOUT_{int(datetime.now().timestamp())}",
                symbol=symbol,
                name=market_data.name,
                event_type=AdvancedEventType.TECHNICAL_BREAKOUT,
                severity=severity,
                confidence=0.8,
                timestamp=datetime.now(),
                current_price=current_price,
                change_percent=market_data.change_percent,
                volume=market_data.volume,
                technical_indicators=technical_indicators,
                technical_signal=technical_indicators.overall_signal,
                description=f"{symbol} 볼린저 밴드 상단 돌파",
                detailed_analysis=f"현재가 {current_price:.2f}가 볼린저 밴드 상단 {technical_indicators.bollinger_upper:.2f}를 돌파했습니다.",
                trading_implications="단기 상승 모멘텀 강화, 과매수 구간 진입 주의",
                expected_duration="short"
            )
            events.append(event)
        
        elif current_price < technical_indicators.bollinger_lower:
            severity = min(1.0, (technical_indicators.bollinger_lower - current_price) / 
                          technical_indicators.bollinger_lower * 10)
            
            event = AdvancedEconomicEvent(
                event_id=f"{symbol}_BOLLINGER_SUPPORT_{int(datetime.now().timestamp())}",
                symbol=symbol,
                name=market_data.name,
                event_type=AdvancedEventType.TECHNICAL_BREAKOUT,
                severity=severity,
                confidence=0.8,
                timestamp=datetime.now(),
                current_price=current_price,
                change_percent=market_data.change_percent,
                volume=market_data.volume,
                technical_indicators=technical_indicators,
                technical_signal=technical_indicators.overall_signal,
                description=f"{symbol} 볼린저 밴드 하단 접촉",
                detailed_analysis=f"현재가 {current_price:.2f}가 볼린저 밴드 하단 {technical_indicators.bollinger_lower:.2f}에 접촉했습니다.",
                trading_implications="과매도 구간, 반등 가능성 주목",
                expected_duration="short"
            )
            events.append(event)
        
        # 2. RSI 극값 이벤트
        if technical_indicators.rsi > self.thresholds['rsi_overbought']:
            severity = min(1.0, (technical_indicators.rsi - 70) / 30)
            
            event = AdvancedEconomicEvent(
                event_id=f"{symbol}_RSI_OVERBOUGHT_{int(datetime.now().timestamp())}",
                symbol=symbol,
                name=market_data.name,
                event_type=AdvancedEventType.TECHNICAL_BREAKOUT,
                severity=severity,
                confidence=0.7,
                timestamp=datetime.now(),
                current_price=current_price,
                change_percent=market_data.change_percent,
                volume=market_data.volume,
                technical_indicators=technical_indicators,
                description=f"{symbol} RSI 과매수 구간 ({technical_indicators.rsi:.1f})",
                detailed_analysis=f"RSI가 {technical_indicators.rsi:.1f}로 과매수 구간에 진입했습니다.",
                trading_implications="조정 가능성 증가, 매도 압력 주의",
                expected_duration="medium"
            )
            events.append(event)
        
        elif technical_indicators.rsi < self.thresholds['rsi_oversold']:
            severity = min(1.0, (30 - technical_indicators.rsi) / 30)
            
            event = AdvancedEconomicEvent(
                event_id=f"{symbol}_RSI_OVERSOLD_{int(datetime.now().timestamp())}",
                symbol=symbol,
                name=market_data.name,
                event_type=AdvancedEventType.TECHNICAL_BREAKOUT,
                severity=severity,
                confidence=0.7,
                timestamp=datetime.now(),
                current_price=current_price,
                change_percent=market_data.change_percent,
                volume=market_data.volume,
                technical_indicators=technical_indicators,
                description=f"{symbol} RSI 과매도 구간 ({technical_indicators.rsi:.1f})",
                detailed_analysis=f"RSI가 {technical_indicators.rsi:.1f}로 과매도 구간에 진입했습니다.",
                trading_implications="반등 가능성 증가, 매수 기회 검토",
                expected_duration="medium"
            )
            events.append(event)
        
        # 3. MACD 신호 변화
        if (technical_indicators.macd > technical_indicators.macd_signal and 
            technical_indicators.macd_histogram > 0):
            
            severity = min(1.0, abs(technical_indicators.macd_histogram) * 100)
            
            event = AdvancedEconomicEvent(
                event_id=f"{symbol}_MACD_BULLISH_{int(datetime.now().timestamp())}",
                symbol=symbol,
                name=market_data.name,
                event_type=AdvancedEventType.MOMENTUM_DIVERGENCE,
                severity=severity,
                confidence=0.75,
                timestamp=datetime.now(),
                current_price=current_price,
                change_percent=market_data.change_percent,
                volume=market_data.volume,
                technical_indicators=technical_indicators,
                description=f"{symbol} MACD 강세 신호",
                detailed_analysis=f"MACD가 신호선을 상향 돌파하며 히스토그램이 양수로 전환했습니다.",
                trading_implications="상승 모멘텀 강화, 매수 신호",
                expected_duration="medium"
            )
            events.append(event)
        
        return events
