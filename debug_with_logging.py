#!/usr/bin/env python3
"""
로깅을 포함한 Market Status API 디버그
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
import requests

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_raw_api():
    """원시 API 호출 테스트"""
    
    print("🔍 원시 API 호출 테스트")
    print("=" * 40)
    
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
    base_url = "https://www.alphavantage.co/query"
    
    # Market Status 테스트
    print("\n1. Market Status API:")
    params = {
        "function": "MARKET_STATUS",
        "apikey": api_key
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            
            if "markets" in data:
                markets = data["markets"]
                print(f"Markets count: {len(markets)}")
                
                if markets:
                    print("First market sample:")
                    first_market = markets[0]
                    for key, value in first_market.items():
                        print(f"  {key}: {value}")
            else:
                print("No 'markets' key in response")
                print(f"Full response: {data}")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")
    
    # Top Gainers/Losers 테스트
    print("\n2. Top Gainers/Losers API:")
    params = {
        "function": "TOP_GAINERS_LOSERS",
        "apikey": api_key
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            
            for key in ["top_gainers", "top_losers", "most_actively_traded"]:
                if key in data:
                    items = data[key]
                    print(f"{key}: {len(items)} items")
                    if items:
                        print(f"  Sample: {items[0]}")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_raw_api()
