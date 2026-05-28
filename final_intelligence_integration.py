#!/usr/bin/env python3
"""
최종 최적화된 Intelligence API 통합 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_monitoring.enhanced_data_collector import EnhancedGlobalDataCollector
import asyncio
import json

async def test_final_integration():
    """최종 통합 테스트"""
    
    print("🚀 최종 최적화된 Intelligence API 통합 테스트")
    print("=" * 60)
    
    collector = EnhancedGlobalDataCollector()
    
    # 1. Intelligence 데이터 수집
    print("\n🧠 Intelligence 데이터 수집:")
    print("-" * 40)
    
    intelligence_data = collector.collect_intelligence_data()
    
    if intelligence_data.get('status') == 'success':
        print("✅ Intelligence 데이터 수집 성공!")
        
        summary = intelligence_data.get('summary', {})
        data = intelligence_data.get('data', {})
        
        print(f"📊 수집 요약:")
        print(f"  🌍 시장 상태: {summary.get('market_status_count', 0)}개")
        print(f"  📈 상승 종목: {summary.get('top_gainers_count', 0)}개")
        print(f"  📉 하락 종목: {summary.get('top_losers_count', 0)}개")
        print(f"  🔥 활발한 거래: {summary.get('most_active_count', 0)}개")
        print(f"  🟢 개장 시장: {summary.get('open_markets_count', 0)}개")
        print(f"  ⚠️ 시장 변동성: {summary.get('market_volatility', 'unknown')}")
        
        # 하이라이트 표시
        if 'data' in intelligence_data:
            intel_data = intelligence_data['data']
            
            # 개장 시장
            market_status = intel_data.get('market_status', [])
            if market_status:
                open_markets = [m for m in market_status if m['current_status'] == 'open']
                if open_markets:
                    print(f"\n🟢 현재 개장 중인 시장:")
                    for market in open_markets[:5]:
                        print(f"  • {market['region']}: {market['primary_exchanges']}")
            
            # 상위 종목
            top_movers = intel_data.get('top_gainers_losers', {})
            
            if 'top_gainers' in top_movers and top_movers['top_gainers']:
                print(f"\n📈 상위 상승 종목:")
                for gainer in top_movers['top_gainers'][:3]:
                    print(f"  🚀 {gainer['ticker']}: +{gainer['change_percentage']} (거래량: {gainer['volume']:,})")
            
            if 'top_losers' in top_movers and top_movers['top_losers']:
                print(f"\n📉 상위 하락 종목:")
                for loser in top_movers['top_losers'][:3]:
                    print(f"  📉 {loser['ticker']}: {loser['change_percentage']} (거래량: {loser['volume']:,})")
            
            if 'most_actively_traded' in top_movers and top_movers['most_actively_traded']:
                print(f"\n🔥 최고 거래량 종목:")
                for active in top_movers['most_actively_traded'][:3]:
                    print(f"  🔥 {active['ticker']}: {active['change_percentage']} (거래량: {active['volume']:,})")
    
    else:
        print(f"❌ Intelligence 데이터 수집 실패: {intelligence_data.get('error', 'Unknown error')}")
    
    # 2. 종합 리포트 생성
    print(f"\n📋 종합 리포트 생성:")
    print("-" * 40)
    
    try:
        comprehensive_report = await collector.generate_comprehensive_report_async()
        
        print("✅ 종합 리포트 생성 성공!")
        print(f"📊 데이터 소스:")
        
        data_sources = comprehensive_report.get('data_sources', {})
        print(f"  • Alpha Vantage 활성화: {data_sources.get('alphavantage_enabled', False)}")
        print(f"  • Intelligence 활성화: {data_sources.get('intelligence_enabled', False)}")
        print(f"  • 뉴스 소스: {data_sources.get('news_sources_count', 0)}개")
        
        # 감정 분석
        sentiment = comprehensive_report.get('sentiment_analysis', {})
        if sentiment:
            print(f"  • 전체 감정 점수: {sentiment.get('overall_sentiment', 0):.3f}")
            
            distribution = sentiment.get('sentiment_distribution', {})
            if distribution:
                print(f"  • 감정 분포: 긍정 {distribution.get('positive', 0)}개, "
                      f"중립 {distribution.get('neutral', 0)}개, "
                      f"부정 {distribution.get('negative', 0)}개")
        
        # Intelligence 인사이트
        insights = comprehensive_report.get('intelligence_insights', {})
        if insights:
            print(f"  • Intelligence 인사이트:")
            if 'open_markets_count' in insights:
                print(f"    - 개장 시장: {insights['open_markets_count']}개")
            if 'top_gainer' in insights:
                gainer = insights['top_gainer']
                print(f"    - 최고 상승: {gainer['ticker']} ({gainer['change_percentage']}%)")
            if 'top_loser' in insights:
                loser = insights['top_loser']
                print(f"    - 최고 하락: {loser['ticker']} ({loser['change_percentage']}%)")
        
    except Exception as e:
        print(f"❌ 종합 리포트 생성 실패: {e}")
    
    # 3. 결과 저장
    timestamp = intelligence_data.get('timestamp', '').replace(':', '').replace('-', '').replace('.', '')[:15]
    output_file = f"output/final_intelligence_integration_{timestamp}.json"
    
    final_result = {
        'intelligence_data': intelligence_data,
        'comprehensive_report': comprehensive_report if 'comprehensive_report' in locals() else {},
        'test_summary': {
            'intelligence_success': intelligence_data.get('status') == 'success',
            'comprehensive_report_success': 'comprehensive_report' in locals(),
            'total_market_status': summary.get('market_status_count', 0),
            'total_top_movers': (
                summary.get('top_gainers_count', 0) + 
                summary.get('top_losers_count', 0) + 
                summary.get('most_active_count', 0)
            )
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_result, f, indent=2, ensure_ascii=False)
    
    print(f"\n" + "=" * 60)
    print("🎯 최종 통합 테스트 완료!")
    print(f"📁 결과 저장: {output_file}")
    
    # 성공 여부 요약
    test_summary = final_result['test_summary']
    print(f"\n📊 테스트 결과:")
    print(f"  ✅ Intelligence API: {'성공' if test_summary['intelligence_success'] else '실패'}")
    print(f"  ✅ 종합 리포트: {'성공' if test_summary['comprehensive_report_success'] else '실패'}")
    print(f"  📊 총 수집 데이터: {test_summary['total_market_status'] + test_summary['total_top_movers']}개")

if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    asyncio.run(test_final_integration())
