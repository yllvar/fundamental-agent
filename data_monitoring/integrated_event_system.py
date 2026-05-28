"""
통합 고도화 이벤트 감지 시스템
모든 분석 모듈을 통합하여 종합적인 이벤트 감지 수행
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
import logging

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_monitoring.advanced_event_detector import AdvancedEventDetector, AdvancedEconomicEvent, AdvancedEventType
from data_monitoring.advanced_event_detector_part2 import AdvancedEventDetectorExtended
from data_monitoring.enhanced_data_collector import EnhancedGlobalDataCollector

class IntegratedEventSystem:
    """통합 이벤트 감지 시스템"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.detector = AdvancedEventDetectorExtended()
        self.data_collector = EnhancedGlobalDataCollector()
        
        # 모니터링 대상 심볼들 (향상된 글로벌 커버리지)
        self.monitoring_symbols = [
            # 미국 주요 지수
            "^GSPC", "^IXIC", "^DJI", "^VIX", "^RUT",
            
            # 미국 주요 주식
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META",
            
            # 아시아 주요 지수
            "^KS11", "^N225", "000001.SS", "^HSI", "^TWII", "^STI",
            
            # 통화 (DXY 문제 해결)
            "DX-Y.NYB", "USDKRW=X", "USDJPY=X", "USDCNY=X", "EURUSD=X",
            
            # 원자재
            "GC=F", "CL=F", "BTC-USD",
            
            # 채권
            "^TNX", "^TYX", "^FVX"
            
            # 주요 개별 종목
            "AAPL", "GOOGL", "MSFT", "TSLA", "NVDA", "AMZN", "META",
            
            # 섹터 ETF
            "XLK", "XLF", "XLE", "XLV", "XLI", "XLY",
            
            # 기타 중요 지표
            "GLD", "TLT", "DXY"  # 금, 국채, 달러지수
        ]
    
    async def run_comprehensive_analysis(self) -> Dict:
        """종합적인 시장 분석 실행 (향상된 데이터 수집 포함)"""
        try:
            self.logger.info("통합 이벤트 감지 시스템 시작")
            
            # 1. 향상된 글로벌 데이터 수집
            self.logger.info("글로벌 시장 데이터 수집 중...")
            comprehensive_report = self.data_collector.generate_comprehensive_report()
            
            # 2. 고도화된 이벤트 감지 실행
            self.logger.info("고도화된 이벤트 감지 실행 중...")
            events = await self.detector.detect_advanced_events(self.monitoring_symbols)
            
            # 3. 뉴스 및 감정 분석 통합
            news_sentiment = comprehensive_report.get('sentiment_analysis', {})
            
            # 4. 결과 분석 및 요약
            analysis_summary = self._create_enhanced_analysis_summary(
                events, comprehensive_report, news_sentiment
            )
            
            # 5. 종합 결과 생성
            result = {
                "timestamp": datetime.now().isoformat(),
                "total_events": len(events),
                "analysis_summary": analysis_summary,
                "events": [self._event_to_dict(event) for event in events],
                "market_data_summary": comprehensive_report.get('market_summary', {}),
                "news_summary": comprehensive_report.get('news_summary', {}),
                "sentiment_analysis": news_sentiment,
                "economic_indicators": comprehensive_report.get('economic_indicators', []),
                "monitoring_symbols": self.monitoring_symbols,
                "data_sources": {
                    "us_markets": len(self.data_collector.market_symbols.get("US_INDICES", {})) + 
                                 len(self.data_collector.market_symbols.get("US_STOCKS", {})),
                    "asia_markets": len(self.data_collector.market_symbols.get("ASIA_INDICES", {})),
                    "currencies": len(self.data_collector.market_symbols.get("CURRENCIES", {})),
                    "commodities": len(self.data_collector.market_symbols.get("COMMODITIES", {})),
                    "news_articles": comprehensive_report.get('news_summary', {}).get('total_articles', 0)
                }
            }
            
            # 6. 결과 저장
            self._save_results(result)
            
            self.logger.info(f"분석 완료: {len(events)}개 이벤트 감지")
            return result
            
        except Exception as e:
            self.logger.error(f"종합 분석 실행 중 오류: {str(e)}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "total_events": 0,
                "events": []
            }
    
    def _create_enhanced_analysis_summary(self, events: List, comprehensive_report: Dict, news_sentiment: Dict) -> Dict:
        """향상된 분석 요약 생성"""
        try:
            # 기존 요약
            basic_summary = self._create_analysis_summary(events)
            
            # 추가 분석
            market_summary = comprehensive_report.get('market_summary', {})
            
            enhanced_summary = {
                **basic_summary,
                "global_market_status": {
                    "us_market": market_summary.get('us_market_status', 'neutral'),
                    "asia_market": market_summary.get('asia_market_status', 'neutral'),
                    "overall_sentiment": news_sentiment.get('overall_sentiment', 0.0)
                },
                "major_market_movers": market_summary.get('major_movers', [])[:3],
                "risk_assessment": {
                    "vix_level": market_summary.get('risk_indicators', {}).get('vix', {}).get('level', 'unknown'),
                    "news_sentiment": self._categorize_sentiment(news_sentiment.get('overall_sentiment', 0.0)),
                    "event_severity": self._assess_event_severity(events)
                },
                "news_insights": {
                    "total_articles": news_sentiment.get('total_articles', 0),
                    "sentiment_distribution": news_sentiment.get('sentiment_distribution', {}),
                    "top_keywords": news_sentiment.get('top_keywords', [])[:5]
                }
            }
            
            return enhanced_summary
            
        except Exception as e:
            self.logger.error(f"향상된 분석 요약 생성 오류: {e}")
            return self._create_analysis_summary(events)
    
    def _categorize_sentiment(self, sentiment_score: float) -> str:
        """감정 점수를 카테고리로 변환"""
        if sentiment_score > 0.3:
            return "매우 긍정적"
        elif sentiment_score > 0.1:
            return "긍정적"
        elif sentiment_score > -0.1:
            return "중립적"
        elif sentiment_score > -0.3:
            return "부정적"
        else:
            return "매우 부정적"
    
    def _assess_event_severity(self, events: List) -> str:
        """이벤트 심각도 평가"""
        if not events:
            return "낮음"
        
        high_severity_count = sum(1 for event in events if getattr(event, 'severity', 0.5) > 0.7)
        
        if high_severity_count >= 3:
            return "높음"
        elif high_severity_count >= 1:
            return "중간"
        else:
            return "낮음"
    
    def _create_analysis_summary(self, events: List[AdvancedEconomicEvent]) -> Dict:
        """분석 결과 요약 생성"""
        summary = {
            "high_severity_events": 0,
            "event_types": {},
            "affected_symbols": set(),
            "market_sentiment": "neutral",
            "risk_level": "medium",
            "key_insights": []
        }
        
        for event in events:
            # 고심각도 이벤트 카운트
            if event.severity > 0.7:
                summary["high_severity_events"] += 1
            
            # 이벤트 타입별 카운트
            event_type = event.event_type.value
            summary["event_types"][event_type] = summary["event_types"].get(event_type, 0) + 1
            
            # 영향받는 심볼 추가
            summary["affected_symbols"].add(event.symbol)
        
        # 영향받는 심볼을 리스트로 변환
        summary["affected_symbols"] = list(summary["affected_symbols"])
        
        # 시장 감정 및 위험 수준 평가
        summary["market_sentiment"] = self._assess_market_sentiment(events)
        summary["risk_level"] = self._assess_risk_level(events)
        
        # 주요 인사이트 생성
        summary["key_insights"] = self._generate_key_insights(events)
        
        return summary
    
    def _assess_market_sentiment(self, events: List[AdvancedEconomicEvent]) -> str:
        """시장 감정 평가"""
        sentiment_scores = []
        
        for event in events:
            if event.market_sentiment:
                sentiment_scores.append(event.market_sentiment.sentiment_score)
            elif event.event_type in [AdvancedEventType.SURGE, AdvancedEventType.RISK_ON]:
                sentiment_scores.append(0.5)
            elif event.event_type in [AdvancedEventType.DROP, AdvancedEventType.RISK_OFF]:
                sentiment_scores.append(-0.5)
        
        if not sentiment_scores:
            return "neutral"
        
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        
        if avg_sentiment > 0.3:
            return "positive"
        elif avg_sentiment < -0.3:
            return "negative"
        else:
            return "neutral"
    
    def _assess_risk_level(self, events: List[AdvancedEconomicEvent]) -> str:
        """위험 수준 평가"""
        high_risk_events = [
            AdvancedEventType.LIQUIDITY_CRISIS,
            AdvancedEventType.MARKET_REGIME_CHANGE,
            AdvancedEventType.CORRELATION_BREAK
        ]
        
        high_risk_count = sum(1 for event in events if event.event_type in high_risk_events)
        high_severity_count = sum(1 for event in events if event.severity > 0.8)
        
        total_risk_score = high_risk_count * 2 + high_severity_count
        
        if total_risk_score >= 5:
            return "very_high"
        elif total_risk_score >= 3:
            return "high"
        elif total_risk_score >= 1:
            return "medium"
        else:
            return "low"
    
    def _generate_key_insights(self, events: List[AdvancedEconomicEvent]) -> List[str]:
        """주요 인사이트 생성"""
        insights = []
        
        # 이벤트 타입별 분석
        event_counts = {}
        for event in events:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        # 가장 빈번한 이벤트 타입
        if event_counts:
            most_common = max(event_counts.items(), key=lambda x: x[1])
            insights.append(f"가장 빈번한 이벤트: {most_common[0]} ({most_common[1]}회)")
        
        # 고심각도 이벤트
        high_severity = [e for e in events if e.severity > 0.8]
        if high_severity:
            insights.append(f"고심각도 이벤트 {len(high_severity)}개 발생")
        
        # 섹터 로테이션
        sector_events = [e for e in events if e.event_type == AdvancedEventType.SECTOR_ROTATION]
        if sector_events:
            insights.append(f"섹터 로테이션 활발: {len(sector_events)}개 섹터 영향")
        
        # 상관관계 이탈
        correlation_events = [e for e in events if e.event_type == AdvancedEventType.CORRELATION_BREAK]
        if correlation_events:
            insights.append("시장 상관관계 구조 변화 감지")
        
        # 기술적 돌파
        technical_events = [e for e in events if e.event_type == AdvancedEventType.TECHNICAL_BREAKOUT]
        if len(technical_events) > 3:
            insights.append(f"기술적 돌파 다발 발생: {len(technical_events)}개")
        
        return insights[:5]  # 최대 5개 인사이트
    
    def _event_to_dict(self, event: AdvancedEconomicEvent) -> Dict:
        """이벤트를 딕셔너리로 변환"""
        return {
            "event_id": event.event_id,
            "symbol": event.symbol,
            "name": event.name,
            "event_type": event.event_type.value,
            "severity": event.severity,
            "confidence": event.confidence,
            "timestamp": event.timestamp.isoformat(),
            "current_price": event.current_price,
            "change_percent": event.change_percent,
            "volume": event.volume,
            "description": event.description,
            "detailed_analysis": event.detailed_analysis,
            "trading_implications": event.trading_implications,
            "risk_assessment": event.risk_assessment,
            "expected_duration": event.expected_duration,
            "related_symbols": event.related_symbols,
            "sentiment_score": event.sentiment_score,
            "technical_signal": event.technical_signal.value if event.technical_signal else None,
            "has_technical_data": event.technical_indicators is not None,
            "has_sentiment_data": event.market_sentiment is not None,
            "correlation_breaks_count": len(event.correlation_breaks)
        }
    
    def _save_results(self, result: Dict):
        """결과를 파일로 저장"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"logs/advanced_events_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"결과 저장 완료: {filename}")
            
        except Exception as e:
            self.logger.error(f"결과 저장 실패: {str(e)}")
    
    def get_event_summary_text(self, events: List[AdvancedEconomicEvent]) -> str:
        """이벤트 요약 텍스트 생성 (뉴스 생성용)"""
        if not events:
            return "현재 특별한 시장 이벤트가 감지되지 않았습니다."
        
        summary_parts = []
        
        # 고심각도 이벤트 우선 처리
        high_severity = [e for e in events if e.severity > 0.7][:3]
        
        for event in high_severity:
            summary_parts.append(f"• {event.description}: {event.detailed_analysis}")
        
        # 시장 전체 이벤트
        market_events = [e for e in events if e.symbol in ["MARKET", "^VIX", "^GSPC"]][:2]
        
        for event in market_events:
            if event not in high_severity:
                summary_parts.append(f"• {event.description}: {event.trading_implications}")
        
        return "\n".join(summary_parts[:5])  # 최대 5개 요약

# 테스트 및 실행 함수
async def test_integrated_system():
    """통합 시스템 테스트"""
    system = IntegratedEventSystem()
    
    print("=== 통합 고도화 이벤트 감지 시스템 테스트 ===")
    
    result = await system.run_comprehensive_analysis()
    
    if "error" in result:
        print(f"오류 발생: {result['error']}")
        return
    
    print(f"\n총 {result['total_events']}개 이벤트 감지")
    print(f"고심각도 이벤트: {result['analysis_summary']['high_severity_events']}개")
    print(f"시장 감정: {result['analysis_summary']['market_sentiment']}")
    print(f"위험 수준: {result['analysis_summary']['risk_level']}")
    
    print("\n=== 이벤트 타입별 분포 ===")
    for event_type, count in result['analysis_summary']['event_types'].items():
        print(f"{event_type}: {count}개")
    
    print("\n=== 주요 인사이트 ===")
    for insight in result['analysis_summary']['key_insights']:
        print(f"• {insight}")
    
    print("\n=== 상위 5개 이벤트 ===")
    for i, event in enumerate(result['events'][:5], 1):
        print(f"{i}. [{event['event_type']}] {event['symbol']}: {event['description']}")
        print(f"   심각도: {event['severity']:.2f}, 신뢰도: {event['confidence']:.2f}")
        print(f"   분석: {event['detailed_analysis'][:100]}...")
        print()

if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 테스트 실행
    asyncio.run(test_integrated_system())
