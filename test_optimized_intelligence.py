#!/usr/bin/env python3
"""
최적화된 Alpha Vantage Intelligence API 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_monitoring.alphavantage_intelligence import AlphaVantageIntelligence
import json

def test_optimized_intelligence():
    """최적화된 Intelligence API 테스트"""
    
    print("🚀 최적화된 Alpha Vantage Intelligence API 테스트")
    print("=" * 60)
    
    intelligence = AlphaVantageIntelligence()
    
    # 종합 데이터 수집 테스트
    print("\n📊 종합 Intelligence 데이터 수집:")
    print("-" * 40)
    
    try:
        data = intelligence.collect_comprehensive_intelligence()
        
        # 시장 상태 분석
        market_status = data.get("market_status", [])
        print(f"🌍 시장 상태: {len(market_status)}개 시장")
        
        if market_status:
            open_markets = [m for m in market_status if m["current_status"] == "open"]
            closed_markets = [m for m in market_status if m["current_status"] == "closed"]
            
            print(f"  📈 개장 시장: {len(open_markets)}개")
            print(f"  📉 폐장 시장: {len(closed_markets)}개")
            
            if open_markets:
                print("  🌍 개장 중인 지역:")
                for market in open_markets[:3]:
                    print(f"    - {market['region']}: {market['primary_exchanges']}")
        
        # 상위 종목 분석
        top_movers = data.get("top_gainers_losers", {})
        print(f"\n📈 상위 종목 데이터:")
        
        for category, movers in top_movers.items():
            print(f"  {category.replace('_', ' ').title()}: {len(movers)}개")
            
            if movers:
                top_3 = movers[:3]
                for mover in top_3:
                    print(f"    {mover['ticker']}: {mover['change_percentage']}% (거래량: {mover['volume']:,})")
        
        # 요약 분석
        summary = data.get("summary", {})
        if summary:
            print(f"\n📋 분석 요약:")
            
            # 시장 분석
            market_analysis = summary.get("market_analysis", {})
            if market_analysis:
                print(f"  🌍 총 시장: {market_analysis.get('total_markets', 0)}개")
                print(f"  📈 개장 시장: {market_analysis.get('open_markets', 0)}개")
                
                open_regions = market_analysis.get('open_market_regions', [])
                if open_regions:
                    print(f"  🌏 개장 지역: {', '.join(open_regions)}")
            
            # 상위 종목 분석
            movers_analysis = summary.get("top_movers_analysis", {})
            if movers_analysis:
                if "gainers" in movers_analysis:
                    gainers = movers_analysis["gainers"]
                    top_performer = gainers.get("top_performer", {})
                    print(f"  🚀 최고 상승: {top_performer.get('ticker')} ({top_performer.get('change_percentage')}%)")
                    print(f"  📊 평균 상승률: {gainers.get('average_gain')}%")
                
                if "losers" in movers_analysis:
                    losers = movers_analysis["losers"]
                    worst_performer = losers.get("worst_performer", {})
                    print(f"  📉 최고 하락: {worst_performer.get('ticker')} ({worst_performer.get('change_percentage')}%)")
                    print(f"  📊 평균 하락률: {losers.get('average_loss')}%")
                
                if "most_active" in movers_analysis:
                    most_active = movers_analysis["most_active"]
                    highest_volume = most_active.get("highest_volume", {})
                    print(f"  🔥 최고 거래량: {highest_volume.get('ticker')} ({highest_volume.get('volume'):,})")
            
            # 리스크 지표
            risk_indicators = summary.get("risk_indicators", {})
            if risk_indicators:
                print(f"  ⚠️ 시장 변동성: {risk_indicators.get('volatility_level', 'unknown')}")
                print(f"  📈 최대 상승: {risk_indicators.get('max_gain_percentage')}%")
                print(f"  📉 최대 하락: {risk_indicators.get('max_loss_percentage')}%")
        
        print(f"\n✅ 테스트 완료!")
        
        # 데이터 저장
        intelligence.save_intelligence_data(data, "optimized_test_result.json")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")

if __name__ == "__main__":
    test_optimized_intelligence()
