#!/usr/bin/env python3
"""
Streamlit 대시보드 기능 데모 및 결과 출력
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_monitoring.alphavantage_intelligence_complete import AlphaVantageIntelligenceComplete
import pandas as pd
import json
from datetime import datetime

def demo_dashboard_data():
    """대시보드 데이터 데모"""
    
    print("🧠 Alpha Vantage Intelligence 대시보드 데모")
    print("=" * 60)
    
    # Intelligence 데이터 수집
    print("\n🔄 데이터 수집 중...")
    intelligence = AlphaVantageIntelligenceComplete()
    data = intelligence.collect_comprehensive_intelligence()
    
    if not data:
        print("❌ 데이터 수집 실패")
        return
    
    # 데이터 추출
    summary = data.get('summary', {})
    market_status = data.get('market_status', [])
    top_movers = data.get('top_gainers_losers', {})
    data_counts = summary.get('data_counts', {})
    market_analysis = summary.get('market_analysis', {})
    highlights = summary.get('highlights', {})
    
    # 1. 대시보드 헤더 정보
    print(f"\n📊 대시보드 개요")
    print("-" * 40)
    print(f"🔑 API 키: {data.get('api_key_used', 'unknown')}")
    print(f"⏰ 수집 시간: {data.get('timestamp', 'unknown')}")
    print(f"🌍 총 시장: {market_analysis.get('total_markets', 0)}개")
    print(f"🟢 개장 시장: {market_analysis.get('open_markets', 0)}개")
    print(f"🔴 폐장 시장: {market_analysis.get('closed_markets', 0)}개")
    
    # 2. 메트릭 카드 정보
    print(f"\n📈 주요 메트릭")
    print("-" * 40)
    print(f"📈 상승 종목: {data_counts.get('top_gainers', 0)}개")
    print(f"📉 하락 종목: {data_counts.get('top_losers', 0)}개")
    print(f"🔥 활발한 거래: {data_counts.get('most_active', 0)}개")
    
    # 3. 하이라이트
    print(f"\n🔥 주요 하이라이트")
    print("-" * 40)
    if 'top_gainer' in highlights:
        gainer = highlights['top_gainer']
        print(f"📈 최고 상승: {gainer['ticker']} ({gainer['change_percentage']})")
    
    if 'top_loser' in highlights:
        loser = highlights['top_loser']
        print(f"📉 최고 하락: {loser['ticker']} ({loser['change_percentage']})")
    
    if 'most_active' in highlights:
        active = highlights['most_active']
        volume_display = f"{active['volume']/1000000:.1f}M"
        print(f"🔥 최고 거래량: {active['ticker']} ({volume_display})")
    
    # 4. 개장 시장 목록
    if market_status:
        open_markets = [m for m in market_status if m['current_status'] == 'open']
        if open_markets:
            print(f"\n🟢 현재 개장 중인 시장 ({len(open_markets)}개)")
            print("-" * 40)
            for market in open_markets:
                print(f"• {market['region']}: {market['primary_exchanges']}")
                print(f"  운영시간: {market['local_open']} - {market['local_close']}")
    
    # 5. 상위 변동 종목 (각 카테고리별 상위 5개)
    print(f"\n📊 상위 변동 종목")
    print("-" * 40)
    
    # 상승 종목
    if 'top_gainers' in top_movers and top_movers['top_gainers']:
        print(f"\n📈 상위 상승 종목 (Top 5):")
        for i, gainer in enumerate(top_movers['top_gainers'][:5], 1):
            print(f"  {i}. {gainer['ticker']}: +{gainer['change_percentage']} "
                  f"(${gainer['price']:.2f}, 거래량: {gainer['volume']:,})")
    
    # 하락 종목
    if 'top_losers' in top_movers and top_movers['top_losers']:
        print(f"\n📉 상위 하락 종목 (Top 5):")
        for i, loser in enumerate(top_movers['top_losers'][:5], 1):
            print(f"  {i}. {loser['ticker']}: {loser['change_percentage']} "
                  f"(${loser['price']:.2f}, 거래량: {loser['volume']:,})")
    
    # 활발한 거래
    if 'most_actively_traded' in top_movers and top_movers['most_actively_traded']:
        print(f"\n🔥 최고 거래량 종목 (Top 5):")
        for i, active in enumerate(top_movers['most_actively_traded'][:5], 1):
            volume_m = active['volume'] / 1000000
            print(f"  {i}. {active['ticker']}: {active['change_percentage']} "
                  f"(거래량: {volume_m:.1f}M)")
    
    # 6. 지역별 시장 분석
    print(f"\n🌏 지역별 시장 분석")
    print("-" * 40)
    
    region_analysis = {}
    for market in market_status:
        region = market['region']
        status = market['current_status']
        
        if region not in region_analysis:
            region_analysis[region] = {'open': 0, 'closed': 0, 'exchanges': []}
        
        region_analysis[region][status] += 1
        if market['primary_exchanges']:
            region_analysis[region]['exchanges'].append(market['primary_exchanges'])
    
    for region, info in region_analysis.items():
        total = info['open'] + info['closed']
        status_emoji = "🟢" if info['open'] > 0 else "🔴"
        print(f"{status_emoji} {region}: {info['open']}개 개장, {info['closed']}개 폐장")
    
    # 7. 대시보드 차트 데이터 요약
    print(f"\n📊 대시보드 차트 데이터")
    print("-" * 40)
    print(f"• 시장 상태 차트: {len(market_status)}개 시장")
    print(f"• 상위 변동 차트: {len(top_movers)}개 카테고리")
    print(f"• 지역별 분석: {len(region_analysis)}개 지역")
    
    # 8. Streamlit 접근 정보
    print(f"\n🌐 Streamlit 대시보드 접근 정보")
    print("-" * 40)
    print(f"• 로컬 URL: http://localhost:8501")
    print(f"• 실행 명령어:")
    print(f"  cd /home/ec2-user/projects/ABP/fundamental_agent")
    print(f"  source /home/ec2-user/dl_env/bin/activate")
    print(f"  ALPHA_VANTAGE_API_KEY=9TLAUWS4L3099YK3 streamlit run streamlit_intelligence_dashboard.py")
    
    # 9. 대시보드 기능 목록
    print(f"\n🎛️ 대시보드 주요 기능")
    print("-" * 40)
    print(f"✅ 실시간 시장 상태 모니터링")
    print(f"✅ 상위 변동 종목 차트 및 테이블")
    print(f"✅ 지역별 시장 분석")
    print(f"✅ 인터랙티브 메트릭 카드")
    print(f"✅ 자동 새로고침 (5분 캐시)")
    print(f"✅ 상세 데이터 테이블 (탭 형태)")
    print(f"✅ 주요 하이라이트 표시")
    print(f"✅ 원시 데이터 확장 뷰")
    
    # 10. 데이터 저장
    output_file = f"output/dashboard_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs('output', exist_ok=True)
    
    demo_result = {
        'dashboard_info': {
            'api_key_used': data.get('api_key_used'),
            'collection_time': data.get('timestamp'),
            'total_data_items': (
                len(market_status) + 
                sum(len(movers) for movers in top_movers.values())
            )
        },
        'metrics': data_counts,
        'market_analysis': market_analysis,
        'highlights': highlights,
        'open_markets': [m for m in market_status if m['current_status'] == 'open'],
        'top_movers_summary': {
            'top_gainers_count': len(top_movers.get('top_gainers', [])),
            'top_losers_count': len(top_movers.get('top_losers', [])),
            'most_active_count': len(top_movers.get('most_actively_traded', []))
        },
        'regional_analysis': region_analysis
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(demo_result, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 데모 결과 저장: {output_file}")
    print(f"\n🎯 대시보드 데모 완료!")

if __name__ == "__main__":
    demo_dashboard_data()
