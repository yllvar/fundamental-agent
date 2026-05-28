#!/usr/bin/env python3
"""
시장 비교 분석 수정 사항 테스트
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.data_analysis_agent import DataAnalysisAgent
from data_monitoring.event_types import MarketEvent, EventType

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_market_comparison():
    """시장 비교 분석 테스트"""
    
    print("🔧 시장 비교 분석 수정 사항 테스트 시작...")
    
    try:
        # DataAnalysisAgent 초기화
        agent = DataAnalysisAgent()
        
        # 테스트용 이벤트 생성
        test_event = MarketEvent(
            symbol="AAPL",
            event_type=EventType.PRICE_SPIKE,
            severity=0.7,
            description="테스트 이벤트",
            timestamp=datetime.now(),
            data={"price_change": 5.2}
        )
        
        print(f"📊 {test_event.symbol} 종목에 대한 시장 비교 분석 실행...")
        
        # 분석 실행
        result = await agent.analyze_event(test_event)
        
        if result and 'market_comparison' in result:
            market_comp = result['market_comparison']
            print("\n✅ 시장 비교 분석 성공!")
            print(f"   - 베타: {market_comp.get('beta', 'N/A')}")
            print(f"   - SPY와의 상관관계: {market_comp.get('correlation_with_spy', 'N/A')}")
            print(f"   - 상대 성과 (1개월): {market_comp.get('relative_performance_1m', 'N/A')}%")
            print(f"   - 사용된 데이터 포인트: {market_comp.get('data_points_used', 'N/A')}")
            
            if 'error' in market_comp:
                print(f"   ⚠️ 경고: {market_comp['error']}")
        else:
            print("❌ 시장 비교 분석 결과를 찾을 수 없습니다")
            
        # 다른 종목들도 테스트
        test_symbols = ["GOOGL", "MSFT", "TSLA"]
        
        for symbol in test_symbols:
            print(f"\n📊 {symbol} 종목 테스트...")
            
            test_event.symbol = symbol
            result = await agent.analyze_event(test_event)
            
            if result and 'market_comparison' in result:
                market_comp = result['market_comparison']
                print(f"   ✅ {symbol} 분석 성공 - 베타: {market_comp.get('beta', 'N/A')}")
            else:
                print(f"   ❌ {symbol} 분석 실패")
        
        print("\n🎉 모든 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_market_comparison())
