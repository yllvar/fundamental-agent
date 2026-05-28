#!/usr/bin/env python3
"""
Market Status API 디버그 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_monitoring.alphavantage_intelligence import AlphaVantageIntelligence

def debug_market_status():
    """Market Status API 직접 테스트"""
    
    print("🔍 Market Status API 디버그")
    print("=" * 40)
    
    intelligence = AlphaVantageIntelligence()
    
    try:
        # 직접 API 호출
        market_statuses = intelligence.get_market_status()
        
        print(f"📊 수집된 시장 상태: {len(market_statuses)}개")
        
        if market_statuses:
            print("\n🌍 시장 상태 상세:")
            for i, status in enumerate(market_statuses[:5], 1):
                print(f"{i}. {status.market} ({status.region})")
                print(f"   거래소: {status.primary_exchanges}")
                print(f"   상태: {status.current_status}")
                print(f"   시간: {status.local_open} - {status.local_close}")
                if status.notes:
                    print(f"   메모: {status.notes}")
                print()
        else:
            print("❌ 시장 상태 데이터가 없습니다.")
            
        # Top Gainers/Losers도 테스트
        print("\n📈 Top Gainers/Losers 테스트:")
        top_movers = intelligence.get_top_gainers_losers()
        
        for category, movers in top_movers.items():
            print(f"{category}: {len(movers)}개")
            if movers:
                for mover in movers[:2]:
                    print(f"  {mover.ticker}: {mover.change_percentage}")
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_market_status()
