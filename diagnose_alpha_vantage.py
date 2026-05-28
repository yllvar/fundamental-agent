#!/usr/bin/env python3
"""
Alpha Vantage API 연결 진단 스크립트
"""

import os
import requests
import time
import json
from datetime import datetime

def test_api_key_status():
    """API 키 상태 확인"""
    print("🔑 API 키 상태 확인")
    print("-" * 30)
    
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY', '9TLAUWS4L3099YK3')
    print(f"사용 중인 API 키: {api_key[:8]}...")
    
    return api_key

def test_basic_connection(api_key):
    """기본 연결 테스트"""
    print("\n📡 기본 연결 테스트")
    print("-" * 30)
    
    # 가장 간단한 엔드포인트 테스트
    test_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey={api_key}"
    
    try:
        print("🔄 Alpha Vantage 서버 연결 중...")
        response = requests.get(test_url, timeout=30)
        
        print(f"📊 HTTP 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 서버 연결 성공")
            print(f"📋 응답 키: {list(data.keys())}")
            
            # Rate limit 체크
            if "Information" in data and "rate limit" in data["Information"]:
                print(f"⚠️ Rate Limit: {data['Information']}")
                return False, "rate_limit"
            elif "Error Message" in data:
                print(f"❌ API 오류: {data['Error Message']}")
                return False, "api_error"
            elif "Time Series (5min)" in data:
                print(f"✅ 정상 데이터 수신")
                return True, "success"
            else:
                print(f"⚠️ 예상치 못한 응답: {data}")
                return False, "unexpected"
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            return False, "http_error"
            
    except requests.exceptions.Timeout:
        print("❌ 연결 시간 초과")
        return False, "timeout"
    except requests.exceptions.ConnectionError:
        print("❌ 연결 오류")
        return False, "connection_error"
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
        return False, "exception"

def test_intelligence_endpoints(api_key):
    """Intelligence API 엔드포인트 테스트"""
    print("\n🧠 Intelligence API 엔드포인트 테스트")
    print("-" * 30)
    
    endpoints = [
        ("MARKET_STATUS", "https://www.alphavantage.co/query?function=MARKET_STATUS&apikey={}"),
        ("TOP_GAINERS_LOSERS", "https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={}"),
        ("NEWS_SENTIMENT", "https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL&apikey={}")
    ]
    
    results = {}
    
    for endpoint_name, url_template in endpoints:
        print(f"\n🔍 {endpoint_name} 테스트:")
        
        try:
            url = url_template.format(api_key)
            response = requests.get(url, timeout=30)
            
            print(f"  HTTP 상태: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Rate limit 체크
                if "Information" in data and "rate limit" in data["Information"]:
                    print(f"  ⚠️ Rate Limit: {data['Information'][:100]}...")
                    results[endpoint_name] = "rate_limit"
                elif "Error Message" in data:
                    print(f"  ❌ API 오류: {data['Error Message']}")
                    results[endpoint_name] = "api_error"
                else:
                    # 데이터 확인
                    expected_keys = {
                        "MARKET_STATUS": "markets",
                        "TOP_GAINERS_LOSERS": "top_gainers",
                        "NEWS_SENTIMENT": "feed"
                    }
                    
                    expected_key = expected_keys.get(endpoint_name)
                    if expected_key and expected_key in data:
                        data_count = len(data[expected_key])
                        print(f"  ✅ 성공: {data_count}개 데이터")
                        results[endpoint_name] = "success"
                    else:
                        print(f"  ⚠️ 예상 키 없음: {list(data.keys())}")
                        results[endpoint_name] = "no_data"
            else:
                print(f"  ❌ HTTP 오류: {response.status_code}")
                results[endpoint_name] = "http_error"
                
        except Exception as e:
            print(f"  ❌ 예외: {e}")
            results[endpoint_name] = "exception"
        
        # Rate limit 방지를 위한 대기
        time.sleep(2)
    
    return results

def test_rate_limit_status(api_key):
    """Rate limit 상태 확인"""
    print("\n⏱️ Rate Limit 상태 확인")
    print("-" * 30)
    
    # 연속으로 여러 요청을 보내서 rate limit 확인
    test_urls = [
        f"https://www.alphavantage.co/query?function=MARKET_STATUS&apikey={api_key}",
        f"https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={api_key}"
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"🔄 요청 {i} 전송 중...")
        
        try:
            start_time = time.time()
            response = requests.get(url, timeout=30)
            elapsed = time.time() - start_time
            
            print(f"  응답 시간: {elapsed:.2f}초")
            
            if response.status_code == 200:
                data = response.json()
                
                if "Information" in data and "rate limit" in data["Information"]:
                    print(f"  ⚠️ Rate Limit 도달!")
                    print(f"  메시지: {data['Information']}")
                    return "rate_limited"
                else:
                    print(f"  ✅ 정상 응답")
            else:
                print(f"  ❌ HTTP 오류: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ 예외: {e}")
        
        time.sleep(1)  # 1초 대기
    
    return "normal"

def check_network_connectivity():
    """네트워크 연결 상태 확인"""
    print("\n🌐 네트워크 연결 상태 확인")
    print("-" * 30)
    
    test_sites = [
        ("Google", "https://www.google.com"),
        ("Alpha Vantage", "https://www.alphavantage.co"),
        ("AWS", "https://aws.amazon.com")
    ]
    
    for site_name, url in test_sites:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"  ✅ {site_name}: 연결 성공")
            else:
                print(f"  ⚠️ {site_name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"  ❌ {site_name}: 연결 실패 ({e})")

def main():
    """메인 진단 프로세스"""
    print("🔍 Alpha Vantage API 연결 진단")
    print("=" * 50)
    print(f"진단 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. API 키 확인
    api_key = test_api_key_status()
    
    # 2. 네트워크 연결 확인
    check_network_connectivity()
    
    # 3. 기본 연결 테스트
    basic_success, basic_status = test_basic_connection(api_key)
    
    # 4. Intelligence API 테스트
    if basic_success:
        intelligence_results = test_intelligence_endpoints(api_key)
    else:
        print("\n⚠️ 기본 연결 실패로 Intelligence API 테스트 건너뜀")
        intelligence_results = {}
    
    # 5. Rate limit 상태 확인
    if basic_success:
        rate_limit_status = test_rate_limit_status(api_key)
    else:
        rate_limit_status = "unknown"
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("📊 진단 결과 요약")
    print("-" * 25)
    
    print(f"기본 연결: {'✅ 성공' if basic_success else '❌ 실패'} ({basic_status})")
    print(f"Rate Limit: {rate_limit_status}")
    
    if intelligence_results:
        print("\nIntelligence API 결과:")
        for endpoint, status in intelligence_results.items():
            status_emoji = "✅" if status == "success" else "⚠️" if status == "rate_limit" else "❌"
            print(f"  {endpoint}: {status_emoji} {status}")
    
    # 문제 해결 방안 제시
    print("\n🔧 문제 해결 방안:")
    
    if not basic_success:
        if basic_status == "rate_limit":
            print("  📊 Rate Limit 문제:")
            print("    - 1시간 후 다시 시도")
            print("    - API 호출 빈도 줄이기")
            print("    - 캐시 활용하기")
        elif basic_status == "timeout":
            print("  ⏱️ 연결 시간 초과:")
            print("    - 네트워크 상태 확인")
            print("    - 방화벽 설정 확인")
        elif basic_status == "api_error":
            print("  🔑 API 키 문제:")
            print("    - API 키 유효성 확인")
            print("    - 새 API 키 발급 고려")
    
    if rate_limit_status == "rate_limited":
        print("  ⚠️ Rate Limit 도달:")
        print("    - 요청 간격 늘리기")
        print("    - 캐시 시간 늘리기 (현재 5분 → 15분)")
        print("    - 불필요한 API 호출 제거")
    
    print(f"\n진단 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
