"""
기존 모니터링 시스템과 고도화된 이벤트 감지 시스템을 통합하는 래퍼
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
import json

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_monitoring.monitor import EconomicMonitor
from data_monitoring.integrated_event_system import IntegratedEventSystem
from data_monitoring.advanced_event_detector import AdvancedEconomicEvent

class EnhancedEconomicMonitor(EconomicMonitor):
    """고도화된 경제 모니터링 시스템"""
    
    def __init__(self):
        super().__init__()
        self.integrated_system = IntegratedEventSystem()
        self.logger = logging.getLogger(__name__)
        
        # 고도화된 분석 결과 저장
        self.latest_advanced_analysis = None
        self.advanced_events_history = []
    
    async def run_enhanced_monitoring_cycle(self) -> Dict:
        """고도화된 모니터링 사이클 실행"""
        try:
            self.logger.info("고도화된 모니터링 사이클 시작")
            
            # 1. 기존 기본 모니터링 실행
            basic_events = await self._run_basic_monitoring()
            
            # 2. 고도화된 분석 실행
            advanced_analysis = await self.integrated_system.run_comprehensive_analysis()
            
            # 3. 결과 통합
            integrated_result = self._integrate_results(basic_events, advanced_analysis)
            
            # 4. 결과 저장 및 업데이트
            self.latest_advanced_analysis = advanced_analysis
            self._update_history(integrated_result)
            
            self.logger.info(f"고도화된 모니터링 완료: {integrated_result['total_events']}개 이벤트")
            
            return integrated_result
            
        except Exception as e:
            self.logger.error(f"고도화된 모니터링 중 오류: {str(e)}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    async def _run_basic_monitoring(self) -> List:
        """기존 기본 모니터링 실행"""
        try:
            # 기존 모니터링 로직 실행 (간단화)
            market_data = {}
            
            # 기본 데이터 수집
            for symbol in self.monitoring_symbols:
                try:
                    data = self.data_collector.collect_yahoo_finance_data(symbol)
                    if data:
                        market_data[symbol] = data
                except Exception as e:
                    self.logger.error(f"기본 데이터 수집 실패 {symbol}: {str(e)}")
                    continue
            
            # 기존 이벤트 감지
            basic_events = self.event_detector.detect_events(market_data)
            
            return basic_events
            
        except Exception as e:
            self.logger.error(f"기본 모니터링 실패: {str(e)}")
            return []
    
    def _integrate_results(self, basic_events: List, advanced_analysis: Dict) -> Dict:
        """기본 이벤트와 고도화된 분석 결과 통합"""
        
        integrated_result = {
            "timestamp": datetime.now().isoformat(),
            "monitoring_type": "enhanced",
            
            # 기본 이벤트 정보
            "basic_events_count": len(basic_events),
            "basic_events": [self._basic_event_to_dict(event) for event in basic_events],
            
            # 고도화된 분석 정보
            "advanced_events_count": advanced_analysis.get("total_events", 0),
            "advanced_analysis": advanced_analysis,
            
            # 통합 요약
            "total_events": len(basic_events) + advanced_analysis.get("total_events", 0),
            "risk_assessment": self._assess_integrated_risk(basic_events, advanced_analysis),
            "priority_alerts": self._generate_priority_alerts(basic_events, advanced_analysis),
            
            # 뉴스 생성용 요약
            "news_summary": self._generate_news_summary(basic_events, advanced_analysis)
        }
        
        return integrated_result
    
    def _basic_event_to_dict(self, event) -> Dict:
        """기본 이벤트를 딕셔너리로 변환"""
        return {
            "event_id": event.event_id,
            "symbol": event.symbol,
            "name": event.name,
            "event_type": event.event_type.value,
            "severity": event.severity,
            "timestamp": event.timestamp.isoformat(),
            "description": event.description,
            "current_price": event.current_price,
            "change_percent": event.change_percent,
            "volume": event.volume,
            "source": "basic_monitoring"
        }
    
    def _assess_integrated_risk(self, basic_events: List, advanced_analysis: Dict) -> Dict:
        """통합 위험 평가"""
        risk_assessment = {
            "overall_risk_level": "medium",
            "risk_factors": [],
            "risk_score": 0.5,  # 0-1 scale
            "recommendations": []
        }
        
        # 기본 이벤트 위험도
        high_severity_basic = sum(1 for event in basic_events if event.severity > 0.7)
        
        # 고도화된 분석 위험도
        advanced_risk = advanced_analysis.get("analysis_summary", {}).get("risk_level", "medium")
        high_severity_advanced = advanced_analysis.get("analysis_summary", {}).get("high_severity_events", 0)
        
        # 위험 점수 계산
        risk_score = 0.3  # 기본값
        
        if high_severity_basic > 0:
            risk_score += 0.2
        if high_severity_advanced > 0:
            risk_score += 0.3
        if advanced_risk in ["high", "very_high"]:
            risk_score += 0.2
        
        risk_assessment["risk_score"] = min(1.0, risk_score)
        
        # 위험 수준 분류
        if risk_score >= 0.8:
            risk_assessment["overall_risk_level"] = "very_high"
        elif risk_score >= 0.6:
            risk_assessment["overall_risk_level"] = "high"
        elif risk_score >= 0.4:
            risk_assessment["overall_risk_level"] = "medium"
        else:
            risk_assessment["overall_risk_level"] = "low"
        
        # 위험 요소 식별
        if high_severity_basic > 0:
            risk_assessment["risk_factors"].append(f"고심각도 기본 이벤트 {high_severity_basic}개")
        if high_severity_advanced > 0:
            risk_assessment["risk_factors"].append(f"고심각도 고급 이벤트 {high_severity_advanced}개")
        
        # 권장사항 생성
        if risk_assessment["overall_risk_level"] in ["high", "very_high"]:
            risk_assessment["recommendations"].extend([
                "포트폴리오 리스크 재평가 필요",
                "헤지 전략 검토",
                "현금 비중 확대 고려"
            ])
        
        return risk_assessment
    
    def _generate_priority_alerts(self, basic_events: List, advanced_analysis: Dict) -> List[Dict]:
        """우선순위 알림 생성"""
        priority_alerts = []
        
        # 기본 이벤트에서 고심각도 알림
        for event in basic_events:
            if event.severity > 0.8:
                priority_alerts.append({
                    "type": "high_severity_basic",
                    "symbol": event.symbol,
                    "message": f"{event.name}: {event.description}",
                    "severity": event.severity,
                    "timestamp": event.timestamp.isoformat()
                })
        
        # 고도화된 분석에서 중요 알림
        advanced_events = advanced_analysis.get("events", [])
        for event in advanced_events[:3]:  # 상위 3개만
            if event["severity"] > 0.7:
                priority_alerts.append({
                    "type": "high_severity_advanced",
                    "symbol": event["symbol"],
                    "message": f"{event['name']}: {event['description']}",
                    "severity": event["severity"],
                    "timestamp": event["timestamp"],
                    "analysis": event.get("detailed_analysis", "")
                })
        
        # 심각도 순으로 정렬
        priority_alerts.sort(key=lambda x: x["severity"], reverse=True)
        
        return priority_alerts[:5]  # 최대 5개
    
    def _generate_news_summary(self, basic_events: List, advanced_analysis: Dict) -> str:
        """뉴스 생성용 요약 텍스트"""
        summary_parts = []
        
        # 고도화된 분석 인사이트
        insights = advanced_analysis.get("analysis_summary", {}).get("key_insights", [])
        if insights:
            summary_parts.append("주요 시장 동향:")
            for insight in insights[:3]:
                summary_parts.append(f"• {insight}")
        
        # 우선순위 이벤트
        priority_events = self._generate_priority_alerts(basic_events, advanced_analysis)
        if priority_events:
            summary_parts.append("\n주요 이벤트:")
            for alert in priority_events[:3]:
                summary_parts.append(f"• {alert['message']}")
        
        # 위험 평가
        risk_assessment = self._assess_integrated_risk(basic_events, advanced_analysis)
        summary_parts.append(f"\n시장 위험도: {risk_assessment['overall_risk_level']}")
        
        if risk_assessment["risk_factors"]:
            summary_parts.append("위험 요소: " + ", ".join(risk_assessment["risk_factors"]))
        
        return "\n".join(summary_parts)
    
    def _update_history(self, integrated_result: Dict):
        """결과 히스토리 업데이트"""
        self.advanced_events_history.append({
            "timestamp": integrated_result["timestamp"],
            "total_events": integrated_result["total_events"],
            "risk_level": integrated_result["risk_assessment"]["overall_risk_level"],
            "priority_alerts_count": len(integrated_result["priority_alerts"])
        })
        
        # 24시간 이전 히스토리 제거
        cutoff_time = datetime.now().timestamp() - 86400  # 24시간
        self.advanced_events_history = [
            record for record in self.advanced_events_history
            if datetime.fromisoformat(record["timestamp"]).timestamp() > cutoff_time
        ]
    
    def get_monitoring_status(self) -> Dict:
        """모니터링 상태 조회"""
        return {
            "is_running": self.is_running,
            "last_analysis": self.latest_advanced_analysis.get("timestamp") if self.latest_advanced_analysis else None,
            "monitoring_symbols_count": len(self.monitoring_symbols),
            "history_records": len(self.advanced_events_history),
            "latest_risk_level": self.advanced_events_history[-1]["risk_level"] if self.advanced_events_history else "unknown"
        }
    
    async def start_continuous_monitoring(self, interval_minutes: int = 30):
        """연속 모니터링 시작"""
        self.is_running = True
        self.logger.info(f"연속 고도화 모니터링 시작 (간격: {interval_minutes}분)")
        
        while self.is_running:
            try:
                # 고도화된 모니터링 실행
                result = await self.run_enhanced_monitoring_cycle()
                
                # 결과 로깅
                if "error" not in result:
                    self.logger.info(f"모니터링 완료: {result['total_events']}개 이벤트, 위험도: {result['risk_assessment']['overall_risk_level']}")
                
                # 대기
                await asyncio.sleep(interval_minutes * 60)
                
            except Exception as e:
                self.logger.error(f"연속 모니터링 중 오류: {str(e)}")
                await asyncio.sleep(60)  # 1분 후 재시도
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.is_running = False
        self.logger.info("고도화된 모니터링 중지")

# 테스트 함수
async def test_enhanced_monitor():
    """고도화된 모니터 테스트"""
    monitor = EnhancedEconomicMonitor()
    
    print("=== 고도화된 경제 모니터링 시스템 테스트 ===")
    
    # 단일 사이클 테스트
    result = await monitor.run_enhanced_monitoring_cycle()
    
    if "error" in result:
        print(f"오류 발생: {result['error']}")
        return
    
    print(f"\n총 이벤트: {result['total_events']}개")
    print(f"기본 이벤트: {result['basic_events_count']}개")
    print(f"고급 이벤트: {result['advanced_events_count']}개")
    print(f"전체 위험도: {result['risk_assessment']['overall_risk_level']}")
    
    print("\n=== 우선순위 알림 ===")
    for i, alert in enumerate(result['priority_alerts'], 1):
        print(f"{i}. [{alert['type']}] {alert['symbol']}: {alert['message']}")
        print(f"   심각도: {alert['severity']:.2f}")
    
    print("\n=== 뉴스 요약 ===")
    print(result['news_summary'])
    
    print("\n=== 모니터링 상태 ===")
    status = monitor.get_monitoring_status()
    for key, value in status.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 테스트 실행
    asyncio.run(test_enhanced_monitor())
