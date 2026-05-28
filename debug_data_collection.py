#!/usr/bin/env python3
"""
Intelligence API 데이터 수집 디버깅
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from data_monitoring.alphavantage_intelligence import AlphaVantageIntelligence

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def debug_intelligence_collection():
    """Intelligence 데이터 수집 디버깅"""
    
    print("🔍 Intelligence API 데이터 수집 디버깅")
    print("=" * 50)
    
    intelligence = AlphaVantageIntelligence()
    
    # 1. Market Status 직접 테스트
    print("\n1️⃣ Market Status 직접 테스트:")
    try:
        market_statuses = intelligence.get_market_status()
        print(f"📊 반환된 데이터 수: {len(market_statuses)}")
        
        if market_statuses:
            print("✅ Market Status 데이터 수집 성공!")
            for i, status in enumerate(market_statuses[:3], 1):
                print(f"  {i}. {status.market} - {status.region} ({status.current_status})")
        else:
            print("❌ Market Status 데이터가 비어있음")
            
    except Exception as e:
        print(f"❌ Market Status 오류: {e}")
        import traceback
        traceback.print_exc()
    
    # 2. Top Gainers/Losers 직접 테스트
    print("\n2️⃣ Top Gainers/Losers 직접 테스트:")
    try:
        top_movers = intelligence.get_top_gainers_losers()
        print(f"📊 반환된 카테고리 수: {len(top_movers)}")
        
        for category, movers in top_movers.items():
            print(f"  {category}: {len(movers)}개")
            if movers:
                print(f"    샘플: {movers[0].ticker} ({movers[0].change_percentage})")
        
        if any(len(movers) > 0 for movers in top_movers.values()):
            print("✅ Top Movers 데이터 수집 성공!")
        else:
            print("❌ Top Movers 데이터가 비어있음")
            
    except Exception as e:
        print(f"❌ Top Movers 오류: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. 종합 수집 테스트
    print("\n3️⃣ 종합 데이터 수집 테스트:")
    try:
        comprehensive_data = intelligence.collect_comprehensive_intelligence()
        
        print(f"📊 종합 데이터 키: {list(comprehensive_data.keys())}")
        
        market_status = comprehensive_data.get('market_status', [])
        top_movers = comprehensive_data.get('top_gainers_losers', {})
        
        print(f"  Market Status: {len(market_status)}개")
        print(f"  Top Movers 카테고리: {len(top_movers)}개")
        
        for category, movers in top_movers.items():
            print(f"    {category}: {len(movers)}개")
        
        if len(market_status) > 0 or any(len(movers) > 0 for movers in top_movers.values()):
            print("✅ 종합 데이터 수집 성공!")
        else:
            print("❌ 종합 데이터가 비어있음")
            
        return comprehensive_data
        
    except Exception as e:
        print(f"❌ 종합 수집 오류: {e}")
        import traceback
        traceback.print_exc()
        return {}

if __name__ == "__main__":
    debug_intelligence_collection()
