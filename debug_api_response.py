#!/usr/bin/env python3
"""
API 응답 파싱 디버깅
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json

def debug_api_response():
    """API 응답 상세 분석"""
    
    print("🔍 API 응답 상세 분석")
    print("=" * 40)
    
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
    base_url = "https://www.alphavantage.co/query"
    
    # 1. Market Status 응답 분석
    print("\n1️⃣ Market Status 응답 분석:")
    params = {
        "function": "MARKET_STATUS",
        "apikey": api_key
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        data = response.json()
        
        print(f"📊 응답 키: {list(data.keys())}")
        print(f"📄 전체 응답:")
        print(json.dumps(data, indent=2)[:1000] + "...")
        
        if "markets" in data:
            markets = data["markets"]
            print(f"\n📋 Markets 데이터:")
            print(f"  타입: {type(markets)}")
            print(f"  길이: {len(markets)}")
            
            if markets:
                print(f"  첫 번째 항목:")
                first_market = markets[0]
                for key, value in first_market.items():
                    print(f"    {key}: {value}")
        
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 2. Top Gainers/Losers 응답 분석
    print("\n2️⃣ Top Gainers/Losers 응답 분석:")
    params = {
        "function": "TOP_GAINERS_LOSERS",
        "apikey": api_key
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        data = response.json()
        
        print(f"📊 응답 키: {list(data.keys())}")
        
        for key in ["top_gainers", "top_losers", "most_actively_traded"]:
            if key in data:
                items = data[key]
                print(f"\n📋 {key}:")
                print(f"  타입: {type(items)}")
                print(f"  길이: {len(items)}")
                
                if items:
                    print(f"  첫 번째 항목:")
                    first_item = items[0]
                    for k, v in first_item.items():
                        print(f"    {k}: {v}")
        
    except Exception as e:
        print(f"❌ 오류: {e}")

if __name__ == "__main__":
    debug_api_response()
