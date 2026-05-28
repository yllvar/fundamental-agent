"""
고도화된 경제 이벤트 탐지 모듈 - 2부
감정 분석, 시장 전체 분석, 이벤트 필터링 기능
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_monitoring.advanced_event_detector import AdvancedEventDetector, AdvancedEconomicEvent, AdvancedEventType
from data_monitoring.sentiment_analysis import MarketSentiment, SentimentScore
from data_monitoring.data_collector import MarketData
from data_monitoring.technical_analysis import TechnicalIndicators
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional

class AdvancedEventDetectorExtended(AdvancedEventDetector):
    """고도화된 이벤트 감지 클래스 확장"""
    
    def _detect_sentiment_events(self, symbol: str, market_data: MarketData, 
                                market_sentiment: Optional[MarketSentiment]) -> List[AdvancedEconomicEvent]:
        """감정 분석 기반 이벤트 감지"""
        events = []
        
        if not market_sentiment:
            return events
        
        # 1. 극단적 감정 상태 감지
        if market_sentiment.overall_sentiment == SentimentScore.VERY_NEGATIVE:
            severity = min(1.0, abs(market_sentiment.sentiment_score))
            
            event = AdvancedEconomicEvent(
                event_id=f"{symbol}_SENTIMENT_PANIC_{int(datetime.now().timestamp())}",
                symbol=symbol,
                name=market_data.name,
                event_type=AdvancedEventType.SENTIMENT_SHIFT,
                severity=severity,
                confidence=market_sentiment.confidence,
                timestamp=datetime.now(),
                current_price=market_data.current_price,
                change_percent=market_data.change_percent,
                volume=market_data.volume,
                market_sentiment=market_sentiment,
                sentiment_score=market_sentiment.sentiment_score,
                description=f"{symbol} 극도의 부정적 감정 상태",
                detailed_analysis=f"시장 감정이 매우 부정적({market_sentiment.sentiment_score:.2f})이며, 공포/탐욕 지수는 {market_sentiment.fear_greed_index:.1f}입니다.",
                trading_implications="패닉 매도 가능성, 역발상 투자 기회 검토",
                risk_assessment="높은 변동성 지속 예상",
                expected_duration="medium"
            )
            events.append(event)
        
        elif market_sentiment.overall_sentiment == SentimentScore.VERY_POSITIVE:
            severity = market_sentiment.sentiment_score
            
            event = AdvancedEconomicEvent(
                event_id=f"{symbol}_SENTIMENT_EUPHORIA_{int(datetime.now().timestamp())}",
                symbol=symbol,
                name=market_data.name,
                event_type=AdvancedEventType.SENTIMENT_SHIFT,
                severity=severity,
                confidence=market_sentiment.confidence,
                timestamp=datetime.now(),
                current_price=market_data.current_price,
                change_percent=market_data.change_percent,
                volume=market_data.volume,
                market_sentiment=market_sentiment,
                sentiment_score=market_sentiment.sentiment_score,
                description=f"{symbol} 극도의 긍정적 감정 상태",
                detailed_analysis=f"시장 감정이 매우 긍정적({market_sentiment.sentiment_score:.2f})이며, 과도한 낙관론 징후가 보입니다.",
                trading_implications="과열 조짐, 조정 가능성 주의",
                risk_assessment="버블 위험 증가",
                expected_duration="short"
            )
            events.append(event)
        
        # 2. 공포/탐욕 지수 극값
        if market_sentiment.fear_greed_index < 20:  # 극도의 공포
            severity = (20 - market_sentiment.fear_greed_index) / 20
            
            event = AdvancedEconomicEvent(
                event_id=f"{symbol}_EXTREME_FEAR_{int(datetime.now().timestamp())}",
                symbol=symbol,
                name=market_data.name,
                event_type=AdvancedEventType.RISK_OFF,
                severity=severity,
                confidence=0.8,
                timestamp=datetime.now(),
                current_price=market_data.current_price,
                change_percent=market_data.change_percent,
                volume=market_data.volume,
                market_sentiment=market_sentiment,
                description=f"{symbol} 극도의 공포 상태 (공포지수: {market_sentiment.fear_greed_index:.1f})",
                detailed_analysis="시장이 극도의 공포 상태에 있으며, 패닉 매도가 발생할 수 있습니다.",
                trading_implications="역발상 투자 기회, 단 추가 하락 위험 존재",
                expected_duration="medium"
            )
            events.append(event)
        
        elif market_sentiment.fear_greed_index > 80:  # 극도의 탐욕
            severity = (market_sentiment.fear_greed_index - 80) / 20
            
            event = AdvancedEconomicEvent(
                event_id=f"{symbol}_EXTREME_GREED_{int(datetime.now().timestamp())}",
                symbol=symbol,
                name=market_data.name,
                event_type=AdvancedEventType.RISK_ON,
                severity=severity,
                confidence=0.8,
                timestamp=datetime.now(),
                current_price=market_data.current_price,
                change_percent=market_data.change_percent,
                volume=market_data.volume,
                market_sentiment=market_sentiment,
                description=f"{symbol} 극도의 탐욕 상태 (탐욕지수: {market_sentiment.fear_greed_index:.1f})",
                detailed_analysis="시장이 극도의 탐욕 상태에 있으며, 과열 조짐이 보입니다.",
                trading_implications="조정 위험 증가, 이익 실현 검토",
                expected_duration="short"
            )
            events.append(event)
        
        return events
    
    def _detect_momentum_divergence(self, symbol: str, market_data: MarketData, 
                                   technical_indicators: Optional[TechnicalIndicators]) -> List[AdvancedEconomicEvent]:
        """모멘텀 다이버전스 감지"""
        events = []
        
        if not technical_indicators:
            return events
        
        # MACD와 가격의 다이버전스 감지 (간단한 구현)
        # 실제로는 더 복잡한 히스토리컬 데이터 분석이 필요
        
        if (market_data.change_percent > 2.0 and 
            technical_indicators.macd < technical_indicators.macd_signal):
            
            severity = abs(market_data.change_percent) / 10.0
            
            event = AdvancedEconomicEvent(
                event_id=f"{symbol}_BEARISH_DIVERGENCE_{int(datetime.now().timestamp())}",
                symbol=symbol,
                name=market_data.name,
                event_type=AdvancedEventType.MOMENTUM_DIVERGENCE,
                severity=severity,
                confidence=0.6,
                timestamp=datetime.now(),
                current_price=market_data.current_price,
                change_percent=market_data.change_percent,
                volume=market_data.volume,
                technical_indicators=technical_indicators,
                description=f"{symbol} 약세 다이버전스 감지",
                detailed_analysis="가격은 상승하고 있으나 MACD 모멘텀이 약화되고 있어 다이버전스가 발생했습니다.",
                trading_implications="상승 모멘텀 약화, 조정 가능성 증가",
                expected_duration="medium"
            )
            events.append(event)
        
        elif (market_data.change_percent < -2.0 and 
              technical_indicators.macd > technical_indicators.macd_signal):
            
            severity = abs(market_data.change_percent) / 10.0
            
            event = AdvancedEconomicEvent(
                event_id=f"{symbol}_BULLISH_DIVERGENCE_{int(datetime.now().timestamp())}",
                symbol=symbol,
                name=market_data.name,
                event_type=AdvancedEventType.MOMENTUM_DIVERGENCE,
                severity=severity,
                confidence=0.6,
                timestamp=datetime.now(),
                current_price=market_data.current_price,
                change_percent=market_data.change_percent,
                volume=market_data.volume,
                technical_indicators=technical_indicators,
                description=f"{symbol} 강세 다이버전스 감지",
                detailed_analysis="가격은 하락하고 있으나 MACD 모멘텀이 개선되고 있어 다이버전스가 발생했습니다.",
                trading_implications="하락 모멘텀 약화, 반등 가능성 증가",
                expected_duration="medium"
            )
            events.append(event)
        
        return events
    
    def _detect_extreme_events(self, symbol: str, market_data: MarketData, 
                              technical_indicators: Optional[TechnicalIndicators],
                              market_sentiment: Optional[MarketSentiment]) -> List[AdvancedEconomicEvent]:
        """극단적 시장 이벤트 감지"""
        events = []
        
        # 1. 극단적 가격 변동
        if abs(market_data.change_percent) >= self.thresholds['price_change_extreme']:
            severity = min(1.0, abs(market_data.change_percent) / 20.0)
            
            event_type = AdvancedEventType.SURGE if market_data.change_percent > 0 else AdvancedEventType.DROP
            
            # 거래량과 감정 분석을 통한 신뢰도 계산
            confidence = 0.7
            if technical_indicators and technical_indicators.volume_ratio > 2.0:
                confidence += 0.1
            if market_sentiment and market_sentiment.confidence > 0.7:
                confidence += 0.1
            
            event = AdvancedEconomicEvent(
                event_id=f"{symbol}_EXTREME_MOVE_{int(datetime.now().timestamp())}",
                symbol=symbol,
                name=market_data.name,
                event_type=event_type,
                severity=severity,
                confidence=min(1.0, confidence),
                timestamp=datetime.now(),
                current_price=market_data.current_price,
                change_percent=market_data.change_percent,
                volume=market_data.volume,
                technical_indicators=technical_indicators,
                market_sentiment=market_sentiment,
                description=f"{symbol} 극단적 {'상승' if market_data.change_percent > 0 else '하락'} ({market_data.change_percent:+.1f}%)",
                detailed_analysis=f"일일 변동률이 {market_data.change_percent:+.1f}%로 극단적 수준에 도달했습니다.",
                trading_implications="높은 변동성 지속 예상, 리스크 관리 필수",
                risk_assessment="극도로 높은 위험 수준",
                expected_duration="short"
            )
            events.append(event)
        
        # 2. 유동성 위기 징후 (거래량 급감 + 변동성 증가)
        if (technical_indicators and 
            technical_indicators.volume_ratio < 0.3 and 
            abs(market_data.change_percent) > 3.0):
            
            severity = (3.0 - technical_indicators.volume_ratio) / 3.0
            
            event = AdvancedEconomicEvent(
                event_id=f"{symbol}_LIQUIDITY_CRISIS_{int(datetime.now().timestamp())}",
                symbol=symbol,
                name=market_data.name,
                event_type=AdvancedEventType.LIQUIDITY_CRISIS,
                severity=severity,
                confidence=0.8,
                timestamp=datetime.now(),
                current_price=market_data.current_price,
                change_percent=market_data.change_percent,
                volume=market_data.volume,
                technical_indicators=technical_indicators,
                description=f"{symbol} 유동성 위기 징후",
                detailed_analysis=f"거래량이 평균 대비 {technical_indicators.volume_ratio:.1f}배로 급감하면서 변동성이 증가했습니다.",
                trading_implications="매매 어려움 예상, 스프레드 확대 주의",
                risk_assessment="유동성 리스크 높음",
                expected_duration="medium"
            )
            events.append(event)
        
        return events
    
    async def _analyze_market_wide_events(self, symbols: List[str], 
                                         market_data: Dict[str, MarketData]) -> List[AdvancedEconomicEvent]:
        """시장 전체 분석 이벤트"""
        events = []
        
        try:
            # 1. 상관관계 이탈 감지
            correlation_breaks = self.correlation_analyzer.detect_correlation_breaks(symbols)
            
            for break_event in correlation_breaks:
                if break_event.significance > 0.5:  # 중요한 이탈만 처리
                    event = AdvancedEconomicEvent(
                        event_id=f"CORRELATION_BREAK_{int(datetime.now().timestamp())}",
                        symbol="MARKET",
                        name="시장 상관관계",
                        event_type=AdvancedEventType.CORRELATION_BREAK,
                        severity=break_event.significance,
                        confidence=0.8,
                        timestamp=break_event.timestamp,
                        current_price=0,
                        change_percent=0,
                        volume=0,
                        correlation_breaks=[break_event],
                        description=f"상관관계 이탈: {break_event.symbol1}-{break_event.symbol2}",
                        detailed_analysis=break_event.description,
                        trading_implications="시장 구조 변화 가능성, 분산투자 효과 변화",
                        expected_duration="long"
                    )
                    events.append(event)
            
            # 2. 섹터 로테이션 감지
            sector_analyses = self.correlation_analyzer.analyze_sector_correlations()
            
            for sector_name, analysis in sector_analyses.items():
                if analysis.rotation_signal != "neutral" and analysis.rotation_strength > 0.7:
                    
                    event_type = AdvancedEventType.SECTOR_ROTATION
                    
                    event = AdvancedEconomicEvent(
                        event_id=f"SECTOR_ROTATION_{sector_name}_{int(datetime.now().timestamp())}",
                        symbol=sector_name,
                        name=f"{sector_name} 섹터",
                        event_type=event_type,
                        severity=analysis.rotation_strength,
                        confidence=0.7,
                        timestamp=datetime.now(),
                        current_price=0,
                        change_percent=0,
                        volume=0,
                        description=f"{sector_name} 섹터 {'자금 유입' if analysis.rotation_signal == 'inflow' else '자금 유출'}",
                        detailed_analysis=f"{sector_name} 섹터에서 {analysis.rotation_signal} 신호가 감지되었습니다. 강도: {analysis.rotation_strength:.2f}",
                        trading_implications=f"{'섹터 비중 확대' if analysis.rotation_signal == 'inflow' else '섹터 비중 축소'} 검토",
                        related_symbols=analysis.symbols,
                        expected_duration="long"
                    )
                    events.append(event)
            
            # 3. 시장 체제 변화 감지 (VIX 기반)
            vix_data = None
            for symbol, data in market_data.items():
                if symbol == "^VIX":
                    vix_data = data
                    break
            
            if vix_data and abs(vix_data.change_percent) > 20:  # VIX 20% 이상 변동
                severity = min(1.0, abs(vix_data.change_percent) / 50.0)
                
                event_type = AdvancedEventType.RISK_OFF if vix_data.change_percent > 0 else AdvancedEventType.RISK_ON
                
                event = AdvancedEconomicEvent(
                    event_id=f"MARKET_REGIME_CHANGE_{int(datetime.now().timestamp())}",
                    symbol="^VIX",
                    name="VIX",
                    event_type=AdvancedEventType.MARKET_REGIME_CHANGE,
                    severity=severity,
                    confidence=0.9,
                    timestamp=datetime.now(),
                    current_price=vix_data.current_price,
                    change_percent=vix_data.change_percent,
                    volume=vix_data.volume,
                    description=f"시장 체제 변화: VIX {vix_data.change_percent:+.1f}%",
                    detailed_analysis=f"VIX가 {vix_data.change_percent:+.1f}% 변동하여 시장 체제 변화가 감지되었습니다.",
                    trading_implications="포트폴리오 리밸런싱 필요, 헤지 전략 검토",
                    risk_assessment="시장 변동성 급변",
                    expected_duration="medium"
                )
                events.append(event)
        
        except Exception as e:
            self.logger.error(f"Error in market-wide analysis: {str(e)}")
        
        return events
    
    def _filter_and_prioritize_events(self, events: List[AdvancedEconomicEvent]) -> List[AdvancedEconomicEvent]:
        """이벤트 필터링 및 우선순위 정렬"""
        filtered_events = []
        current_time = datetime.now()
        
        for event in events:
            # 쿨다운 체크
            cooldown_key = f"{event.symbol}_{event.event_type.value}"
            
            if cooldown_key in self.alert_cooldown:
                last_alert = self.alert_cooldown[cooldown_key]
                cooldown_minutes = 15  # 기본 15분 쿨다운
                
                # 이벤트 타입별 쿨다운 조정
                if event.event_type in [AdvancedEventType.SECTOR_ROTATION, AdvancedEventType.MARKET_REGIME_CHANGE]:
                    cooldown_minutes = 60  # 1시간
                elif event.event_type in [AdvancedEventType.CORRELATION_BREAK]:
                    cooldown_minutes = 30  # 30분
                
                if (current_time - last_alert).seconds < cooldown_minutes * 60:
                    continue
            
            # 최소 심각도 필터
            if event.severity < 0.3:
                continue
            
            # 신뢰도 필터
            if event.confidence < 0.5:
                continue
            
            self.alert_cooldown[cooldown_key] = current_time
            filtered_events.append(event)
        
        # 우선순위 정렬 (심각도 * 신뢰도)
        filtered_events.sort(key=lambda x: x.severity * x.confidence, reverse=True)
        
        # 최대 20개 이벤트만 반환
        return filtered_events[:20]
    
    def _update_event_history(self, events: List[AdvancedEconomicEvent]):
        """이벤트 히스토리 업데이트"""
        self.event_history.extend(events)
        
        # 24시간 이전 이벤트 제거
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.event_history = [
            event for event in self.event_history 
            if event.timestamp > cutoff_time
        ]
        
        # 최대 1000개 이벤트만 유지
        if len(self.event_history) > 1000:
            self.event_history = self.event_history[-1000:]
