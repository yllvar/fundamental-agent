#!/usr/bin/env python3
"""
Alpha Vantage Intelligence API 원시 응답 디버그
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
from datetime import datetime, timedelta

# Alpha Vantage API 키 (환경변수에서 가져오기)
API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')

def debug_api_call(function, **params):
    """API 호출 디버그"""
    base_url = "https://www.alphavantage.co/query"
    
    # 기본 파라미터
    params.update({
        'function': function,
        'apikey': API_KEY
    })
    
    print(f"\n🔍 Testing {function}")
    print(f"📡 URL: {base_url}")
    print(f"📋 Params: {params}")
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📄 Response Keys: {list(data.keys())}")
            
            # 응답 내용 요약
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, list):
                        print(f"  {key}: {len(value)} items")
                        if value:  # 첫 번째 항목 샘플
                            print(f"    Sample: {json.dumps(value[0], indent=2)[:200]}...")
                    elif isinstance(value, dict):
                        print(f"  {key}: {len(value)} keys")
                        if value:
                            sample_key = list(value.keys())[0]
                            print(f"    Sample key: {sample_key}")
                    else:
                        print(f"  {key}: {value}")
            
            return data
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    print("🧠 Alpha Vantage Intelligence API 원시 응답 디버그")
    print("=" * 60)
    
    # 1. Market Status
    debug_api_call('MARKET_STATUS')
    
    # 2. News Sentiment
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%dT%H%M")
    debug_api_call(
        'NEWS_SENTIMENT',
        tickers='AAPL,MSFT',
        time_from=yesterday,
        limit=5
    )
    
    # 3. Top Gainers Losers
    debug_api_call('TOP_GAINERS_LOSERS')
    
    # 4. Insider Transactions
    debug_api_call('INSIDER_TRANSACTIONS')
    
    # 5. Analytics Sliding Window
    debug_api_call(
        'ANALYTICS_SLIDING_WINDOW',
        SYMBOLS='AAPL,MSFT',
        RANGE='1month',
        INTERVAL='daily',
        OHLC='close',
        WINDOW_SIZE=10,
        CALCULATIONS='MEAN,STDDEV'
    )

if __name__ == "__main__":
    main()
