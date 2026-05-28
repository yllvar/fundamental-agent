#!/usr/bin/env python3
"""
실제 API 키로 모든 Intelligence API 엔드포인트 테스트
"""

import os
import requests
import json
from datetime import datetime, timedelta

# API 키 설정
API_KEY = "9TLAUWS4L3099YK3"
BASE_URL = "https://www.alphavantage.co/query"

def test_endpoint(function_name, params=None, description=""):
    """개별 엔드포인트 테스트"""
    
    print(f"\n🔍 {function_name} - {description}")
    print("-" * 50)
    
    # 기본 파라미터
    default_params = {
        'function': function_name,
        'apikey': API_KEY
    }
    
    if params:
        default_params.update(params)
    
    print(f"📋 Parameters: {default_params}")
    
    try:
        response = requests.get(BASE_URL, params=default_params, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # 에러 체크
            if "Error Message" in data:
                print(f"❌ API Error: {data['Error Message']}")
                return False, data
            elif "Information" in data and "demo" in data["Information"]:
                print(f"⚠️ Demo Limitation: {data['Information']}")
                return False, data
            elif "Note" in data:
                print(f"ℹ️ Note: {data['Note']}")
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
                            print(f"    Sample: {json.dumps(value[0], indent=2)[:150]}...")
                    elif isinstance(value, dict):
                        print(f"  📁 {key}: {len(value)} keys")
                        if value:
                            sample_key = list(value.keys())[0]
                            print(f"    Sample key: {sample_key}")
                    else:
                        print(f"  📄 {key}: {str(value)[:100]}...")
                
                print(f"📊 Total data items: {total_items}")
                return True, data
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False, None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, None

def main():
    """모든 엔드포인트 테스트"""
    
    print("🧠 Alpha Vantage Intelligence API 전체 테스트 (실제 API 키)")
    print("=" * 70)
    print(f"🔑 API Key: {API_KEY}")
    
    results = {}
    
    # 1. Market Status
    success, data = test_endpoint('MARKET_STATUS', description="글로벌 시장 상태")
    results['MARKET_STATUS'] = {'success': success, 'data_count': len(data.get('markets', [])) if data else 0}
    
    # 2. News Sentiment (실제 API 키로 테스트)
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%dT%H%M")
    success, data = test_endpoint('NEWS_SENTIMENT', {
        'tickers': 'AAPL,MSFT,GOOGL',
        'time_from': yesterday,
        'limit': 10
    }, description="뉴스 감정 분석")
    results['NEWS_SENTIMENT'] = {'success': success, 'data_count': len(data.get('feed', [])) if data else 0}
    
    # 3. Top Gainers/Losers
    success, data = test_endpoint('TOP_GAINERS_LOSERS', description="상위 상승/하락 종목")
    top_movers_count = 0
    if data:
        top_movers_count = (len(data.get('top_gainers', [])) + 
                           len(data.get('top_losers', [])) + 
                           len(data.get('most_actively_traded', [])))
    results['TOP_GAINERS_LOSERS'] = {'success': success, 'data_count': top_movers_count}
    
    # 4. Insider Transactions (실제 API 키로 테스트)
    success, data = test_endpoint('INSIDER_TRANSACTIONS', description="내부자 거래")
    results['INSIDER_TRANSACTIONS'] = {'success': success, 'data_count': len(data.get('data', [])) if data else 0}
    
    # 5. Earnings Call Transcript (실제 API 키로 테스트)
    success, data = test_endpoint('EARNINGS_CALL_TRANSCRIPT', {
        'symbol': 'AAPL'
    }, description="실적 발표 대화록")
    results['EARNINGS_CALL_TRANSCRIPT'] = {'success': success, 'data_count': len(data.get('transcript', [])) if data else 0}
    
    # 6. Analytics Sliding Window (실제 API 키로 테스트)
    success, data = test_endpoint('ANALYTICS_SLIDING_WINDOW', {
        'SYMBOLS': 'AAPL,MSFT',
        'RANGE': '1month',
        'INTERVAL': 'daily',
        'OHLC': 'close',
        'WINDOW_SIZE': 10,
        'CALCULATIONS': 'MEAN,STDDEV'
    }, description="고급 분석 (슬라이딩 윈도우)")
    analytics_count = 0
    if data:
        for symbol_data in data.values():
            if isinstance(symbol_data, list):
                analytics_count += len(symbol_data)
    results['ANALYTICS_SLIDING_WINDOW'] = {'success': success, 'data_count': analytics_count}
    
    # 결과 요약
    print("\n" + "=" * 70)
    print("📊 전체 테스트 결과 요약")
    print("-" * 40)
    
    total_success = 0
    total_data = 0
    
    for endpoint, result in results.items():
        status = "✅ 성공" if result['success'] else "❌ 실패"
        data_count = result['data_count']
        print(f"{endpoint:25} {status:8} ({data_count:3}개 데이터)")
        
        if result['success']:
            total_success += 1
            total_data += data_count
    
    print("-" * 40)
    print(f"성공한 엔드포인트: {total_success}/{len(results)}개")
    print(f"총 수집 데이터: {total_data}개")
    
    # 결과 저장
    output_file = "output/full_intelligence_api_test.json"
    os.makedirs("output", exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"📁 결과 저장: {output_file}")
    
    return results

if __name__ == "__main__":
    main()
