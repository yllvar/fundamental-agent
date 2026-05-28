#!/usr/bin/env python3
"""
최종 최적화된 Alpha Vantage Intelligence API 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_monitoring.enhanced_data_collector import EnhancedGlobalDataCollector
import json

def test_final_optimized():
    """최종 최적화된 시스템 테스트"""
    
    print("🚀 최종 최적화된 경제 뉴스 시스템 테스트")
    print("=" * 60)
    
    collector = EnhancedGlobalDataCollector()
    
    # Intelligence 데이터 수집 테스트
    print("\n🧠 Intelligence 데이터 수집:")
    print("-" * 40)
    
    intelligence_data = collector.collect_intelligence_data()
    
    if intelligence_data.get('status') == 'success':
        summary = intelligence_data.get('summary', {})
        data = intelligence_data.get('data', {})
        
        print("✅ Intelligence 데이터 수집 성공!")
        print(f"📊 시장 상태: {summary.get('market_status_count', 0)}개")
        print(f"📈 상승 종목: {summary.get('top_gainers_count', 0)}개")
        print(f"📉 하락 종목: {summary.get('top_losers_count', 0)}개")
        print(f"🔥 활발한 거래: {summary.get('most_active_count', 0)}개")
        print(f"🌍 개장 시장: {summary.get('open_markets_count', 0)}개")
        print(f"⚠️ 시장 변동성: {summary.get('market_volatility', 'unknown')}")
        
        # 상세 데이터 표시
        if 'data' in intelligence_data:
            intel_data = intelligence_data['data']
            
            # 시장 상태
            market_status = intel_data.get('market_status', [])
            if market_status:
                print(f"\n🌍 시장 상태 상세 (상위 5개):")
                for market in market_status[:5]:
                    status_emoji = "🟢" if market['current_status'] == 'open' else "🔴"
                    print(f"  {status_emoji} {market['region']}: {market['current_status']}")
            
            # 상위 종목
            top_movers = intel_data.get('top_gainers_losers', {})
            
            if 'top_gainers' in top_movers and top_movers['top_gainers']:
                print(f"\n📈 상위 상승 종목 (상위 5개):")
                for gainer in top_movers['top_gainers'][:5]:
                    print(f"  🚀 {gainer['ticker']}: +{gainer['change_percentage']}% (거래량: {gainer['volume']:,})")
            
            if 'top_losers' in top_movers and top_movers['top_losers']:
                print(f"\n📉 상위 하락 종목 (상위 5개):")
                for loser in top_movers['top_losers'][:5]:
                    print(f"  📉 {loser['ticker']}: {loser['change_percentage']}% (거래량: {loser['volume']:,})")
            
            if 'most_actively_traded' in top_movers and top_movers['most_actively_traded']:
                print(f"\n🔥 최고 거래량 종목 (상위 5개):")
                for active in top_movers['most_actively_traded'][:5]:
                    print(f"  🔥 {active['ticker']}: {active['change_percentage']}% (거래량: {active['volume']:,})")
            
            # 요약 분석
            if 'summary' in intel_data:
                summary_data = intel_data['summary']
                
                if 'risk_indicators' in summary_data:
                    risk = summary_data['risk_indicators']
                    print(f"\n⚠️ 리스크 분석:")
                    print(f"  📈 최대 상승률: {risk.get('max_gain_percentage', 'N/A')}%")
                    print(f"  📉 최대 하락률: {risk.get('max_loss_percentage', 'N/A')}%")
                    print(f"  🌊 시장 변동성: {risk.get('volatility_level', 'unknown')}")
    
    else:
        print(f"❌ Intelligence 데이터 수집 실패: {intelligence_data.get('error', 'Unknown error')}")
    
    print(f"\n" + "=" * 60)
    print("🎯 최적화 테스트 완료!")
    
    # 결과를 파일로 저장
    output_file = f"output/final_optimized_test_{intelligence_data.get('timestamp', '').replace(':', '')}.json"
    os.makedirs('output', exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(intelligence_data, f, indent=2, ensure_ascii=False)
    
    print(f"📁 결과 저장: {output_file}")

if __name__ == "__main__":
    test_final_optimized()
