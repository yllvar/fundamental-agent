#!/usr/bin/env python3
"""
Demo API 키와 새 API 키 비교 테스트
"""

import requests
import json
import time

def test_api_key(api_key, key_name):
    """특정 API 키로 테스트"""
    
    print(f"\n🔑 {key_name} 테스트: {api_key}")
    print("-" * 50)
    
    base_url = "https://www.alphavantage.co/query"
    
    # 1. Market Status 테스트
    print("📊 Market Status 테스트:")
    params = {
        "function": "MARKET_STATUS",
        "apikey": api_key
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        data = response.json()
        
        print(f"  Status: {response.status_code}")
        print(f"  Keys: {list(data.keys())}")
        
        if "markets" in data:
            print(f"  ✅ Markets data: {len(data['markets'])} items")
            return True
        elif "Information" in data:
            print(f"  ℹ️ Info: {data['Information'][:100]}...")
            return False
        elif "Error Message" in data:
            print(f"  ❌ Error: {data['Error Message']}")
            return False
        else:
            print(f"  ⚠️ Unknown response: {data}")
            return False
            
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False

def test_top_gainers(api_key, key_name):
    """Top Gainers/Losers 테스트"""
    
    print(f"\n📈 {key_name} - Top Gainers/Losers 테스트:")
    
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "TOP_GAINERS_LOSERS",
        "apikey": api_key
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        data = response.json()
        
        print(f"  Status: {response.status_code}")
        print(f"  Keys: {list(data.keys())}")
        
        if "top_gainers" in data:
            gainers = len(data.get('top_gainers', []))
            losers = len(data.get('top_losers', []))
            active = len(data.get('most_actively_traded', []))
            print(f"  ✅ Top movers: {gainers} gainers, {losers} losers, {active} active")
            return True
        elif "Information" in data:
            print(f"  ℹ️ Info: {data['Information'][:100]}...")
            return False
        else:
            print(f"  ⚠️ Other response: {list(data.keys())}")
            return False
            
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False

def main():
    """API 키 비교 테스트"""
    
    print("🔍 Alpha Vantage API 키 비교 테스트")
    print("=" * 60)
    
    # Demo 키 테스트
    demo_key = "demo"
    new_key = "9TLAUWS4L3099YK3"
    
    print("\n1️⃣ Demo API 키 테스트")
    demo_market_works = test_api_key(demo_key, "Demo Key")
    time.sleep(2)  # 짧은 대기
    demo_movers_works = test_top_gainers(demo_key, "Demo Key")
    
    print("\n2️⃣ 새 API 키 테스트")
    time.sleep(5)  # 조금 더 대기
    new_market_works = test_api_key(new_key, "New Key")
    time.sleep(5)
    new_movers_works = test_top_gainers(new_key, "New Key")
    
    # 결과 비교
    print("\n" + "=" * 60)
    print("📊 비교 결과")
    print("-" * 30)
    
    print(f"Demo Key (demo):")
    print(f"  Market Status: {'✅ 작동' if demo_market_works else '❌ 실패'}")
    print(f"  Top Movers: {'✅ 작동' if demo_movers_works else '❌ 실패'}")
    
    print(f"\nNew Key ({new_key}):")
    print(f"  Market Status: {'✅ 작동' if new_market_works else '❌ 실패'}")
    print(f"  Top Movers: {'✅ 작동' if new_movers_works else '❌ 실패'}")
    
    # 권장사항
    print(f"\n💡 권장사항:")
    if demo_market_works or demo_movers_works:
        print("  • Demo 키가 여전히 작동하므로 당분간 demo 키 사용")
        print("  • 새 API 키는 24시간 후 다시 테스트")
        print("  • 새 API 키 활성화 후 News Sentiment, Insider Transactions 등 추가 기능 사용 가능")
    else:
        print("  • 두 키 모두 문제가 있음. Alpha Vantage 지원팀 문의 필요")
    
    return {
        'demo_key': {
            'market_status': demo_market_works,
            'top_movers': demo_movers_works
        },
        'new_key': {
            'market_status': new_market_works,
            'top_movers': new_movers_works
        }
    }

if __name__ == "__main__":
    main()
