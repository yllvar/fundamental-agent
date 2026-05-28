#!/usr/bin/env python3
"""
사용 가능한 Alpha Vantage Intelligence API 엔드포인트 테스트
"""

import requests
import json
import os
from datetime import datetime, timedelta

def test_endpoint(function_name, params=None):
    """개별 엔드포인트 테스트"""
    
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
    base_url = "https://www.alphavantage.co/query"
    
    # 기본 파라미터
    default_params = {
        'function': function_name,
        'apikey': api_key
    }
    
    if params:
        default_params.update(params)
    
    print(f"\n🔍 Testing {function_name}")
    print(f"📋 Params: {default_params}")
    print("-" * 50)
    
    try:
        response = requests.get(base_url, params=default_params, timeout=30)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # 에러 메시지 확인
            if "Error Message" in data:
                print(f"❌ Error: {data['Error Message']}")
                return False
            elif "Information" in data:
                if "demo" in data["Information"]:
                    print(f"⚠️ Demo limitation: {data['Information']}")
                    return False
                else:
                    print(f"ℹ️ Info: {data['Information']}")
            elif "error" in data:
                print(f"❌ API Error: {data['error']}")
                return False
            else:
                # 성공적인 응답
                print(f"✅ Success! Keys: {list(data.keys())}")
                
                # 데이터 요약
                for key, value in data.items():
                    if isinstance(value, list):
                        print(f"  📋 {key}: {len(value)} items")
                        if value and len(value) > 0:
                            print(f"    Sample: {json.dumps(value[0], indent=2)[:200]}...")
                    elif isinstance(value, dict):
                        print(f"  📁 {key}: {len(value)} keys")
                    else:
                        print(f"  📄 {key}: {value}")
                
                return True
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    """모든 엔드포인트 테스트"""
    
    print("🧠 Alpha Vantage Intelligence API 엔드포인트 테스트")
    print("=" * 60)
    
    results = {}
    
    # 1. Market Status
    print("\n1️⃣ MARKET_STATUS")
    results['MARKET_STATUS'] = test_endpoint('MARKET_STATUS')
    
    # 2. News Sentiment (확인된 사용 가능)
    print("\n2️⃣ NEWS_SENTIMENT")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%dT%H%M")
    results['NEWS_SENTIMENT'] = test_endpoint('NEWS_SENTIMENT', {
        'tickers': 'AAPL',
        'time_from': yesterday,
        'limit': 5
    })
    
    # 3. Top Gainers/Losers
    print("\n3️⃣ TOP_GAINERS_LOSERS")
    results['TOP_GAINERS_LOSERS'] = test_endpoint('TOP_GAINERS_LOSERS')
    
    # 4. Insider Transactions (확인된 사용 가능)
    print("\n4️⃣ INSIDER_TRANSACTIONS")
    results['INSIDER_TRANSACTIONS'] = test_endpoint('INSIDER_TRANSACTIONS')
    
    # 5. Earnings Call Transcript (확인된 사용 가능)
    print("\n5️⃣ EARNINGS_CALL_TRANSCRIPT")
    results['EARNINGS_CALL_TRANSCRIPT'] = test_endpoint('EARNINGS_CALL_TRANSCRIPT', {
        'symbol': 'AAPL'
    })
    
    # 6. Analytics Sliding Window
    print("\n6️⃣ ANALYTICS_SLIDING_WINDOW")
    results['ANALYTICS_SLIDING_WINDOW'] = test_endpoint('ANALYTICS_SLIDING_WINDOW', {
        'SYMBOLS': 'AAPL',
        'RANGE': '1month',
        'INTERVAL': 'daily',
        'OHLC': 'close',
        'WINDOW_SIZE': 10,
        'CALCULATIONS': 'MEAN'
    })
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약:")
    print("-" * 30)
    
    for endpoint, success in results.items():
        status = "✅ 사용 가능" if success else "❌ 사용 불가"
        print(f"{endpoint}: {status}")
    
    available_count = sum(results.values())
    total_count = len(results)
    
    print(f"\n🎯 총 {total_count}개 중 {available_count}개 엔드포인트 사용 가능")

if __name__ == "__main__":
    main()
