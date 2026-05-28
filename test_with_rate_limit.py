#!/usr/bin/env python3
"""
Rate Limit을 고려한 Intelligence API 테스트
"""

import os
import requests
import json
import time
from datetime import datetime, timedelta

# API 키 설정
API_KEY = "9TLAUWS4L3099YK3"
BASE_URL = "https://www.alphavantage.co/query"

def wait_for_rate_limit():
    """Rate limit 대기 (Free tier: 25 requests per day, 5 per minute)"""
    print("⏳ Rate limit 대기 중... (15초)")
    time.sleep(15)

def test_single_endpoint(function_name, params=None, description=""):
    """단일 엔드포인트 테스트 (Rate limit 포함)"""
    
    print(f"\n🔍 {function_name} - {description}")
    print("-" * 50)
    
    # Rate limit 대기
    wait_for_rate_limit()
    
    # 기본 파라미터
    default_params = {
        'function': function_name,
        'apikey': API_KEY
    }
    
    if params:
        default_params.update(params)
    
    try:
        response = requests.get(BASE_URL, params=default_params, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Rate limit 정보 메시지 체크
            if "Information" in data and "rate limit" in data["Information"]:
                print(f"ℹ️ Rate Limit Info: {data['Information'][:100]}...")
                # 실제 데이터가 있는지 확인
                data_keys = [k for k in data.keys() if k != "Information"]
                if data_keys:
                    print(f"📋 Data keys found: {data_keys}")
                    return True, data
                else:
                    print("⚠️ No actual data returned, only rate limit info")
                    return False, data
            
            # 에러 체크
            elif "Error Message" in data:
                print(f"❌ API Error: {data['Error Message']}")
                return False, data
            elif "error" in data:
                print(f"❌ Error: {data['error']}")
                return False, data
            else:
                # 성공
                print(f"✅ Success! Response keys: {list(data.keys())}")
                
                # 데이터 요약
                total_items = 0
                for key, value in data.items():
                    if isinstance(value, list):
                        print(f"  📋 {key}: {len(value)} items")
                        total_items += len(value)
                        if value and len(value) > 0:
                            print(f"    First item keys: {list(value[0].keys()) if isinstance(value[0], dict) else 'Not dict'}")
                    elif isinstance(value, dict):
                        print(f"  📁 {key}: {len(value)} keys")
                    else:
                        print(f"  📄 {key}: {str(value)[:100]}...")
                
                print(f"📊 Total data items: {total_items}")
                return True, data
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, None

def main():
    """순차적 엔드포인트 테스트"""
    
    print("🧠 Alpha Vantage Intelligence API 순차 테스트")
    print("=" * 60)
    print(f"🔑 API Key: {API_KEY}")
    print("⏰ Free tier: 25 requests/day, 5 requests/minute")
    
    results = {}
    
    # 1. Market Status (가장 기본적인 것부터)
    print("\n1️⃣ Market Status 테스트")
    success, data = test_single_endpoint('MARKET_STATUS', description="글로벌 시장 상태")
    results['MARKET_STATUS'] = {
        'success': success, 
        'data_count': len(data.get('markets', [])) if data else 0,
        'has_data': bool(data and 'markets' in data)
    }
    
    # 2. Top Gainers/Losers (두 번째로 중요한 것)
    print("\n2️⃣ Top Gainers/Losers 테스트")
    success, data = test_single_endpoint('TOP_GAINERS_LOSERS', description="상위 상승/하락 종목")
    top_movers_count = 0
    has_movers_data = False
    if data:
        for key in ['top_gainers', 'top_losers', 'most_actively_traded']:
            if key in data:
                top_movers_count += len(data[key])
                has_movers_data = True
    
    results['TOP_GAINERS_LOSERS'] = {
        'success': success, 
        'data_count': top_movers_count,
        'has_data': has_movers_data
    }
    
    # 3. News Sentiment (세 번째)
    print("\n3️⃣ News Sentiment 테스트")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%dT%H%M")
    success, data = test_single_endpoint('NEWS_SENTIMENT', {
        'tickers': 'AAPL',
        'limit': 5
    }, description="뉴스 감정 분석")
    
    results['NEWS_SENTIMENT'] = {
        'success': success, 
        'data_count': len(data.get('feed', [])) if data else 0,
        'has_data': bool(data and 'feed' in data)
    }
    
    # 결과 요약 (처음 3개만)
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약 (처음 3개 엔드포인트)")
    print("-" * 40)
    
    working_endpoints = []
    total_data = 0
    
    for endpoint, result in results.items():
        status = "✅ 작동" if result['has_data'] else "⚠️ 데이터 없음" if result['success'] else "❌ 실패"
        data_count = result['data_count']
        print(f"{endpoint:20} {status:12} ({data_count:3}개 데이터)")
        
        if result['has_data']:
            working_endpoints.append(endpoint)
            total_data += data_count
    
    print("-" * 40)
    print(f"실제 데이터가 있는 엔드포인트: {len(working_endpoints)}개")
    print(f"총 수집 데이터: {total_data}개")
    
    if working_endpoints:
        print(f"✅ 작동하는 엔드포인트: {', '.join(working_endpoints)}")
    
    # 결과 저장
    output_file = "output/rate_limited_test_results.json"
    os.makedirs("output", exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"📁 결과 저장: {output_file}")
    
    return results

if __name__ == "__main__":
    main()
