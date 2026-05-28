#!/usr/bin/env python3
"""
FRED API 연결 테스트
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_monitoring.fred_data_collector import FREDDataCollector
import requests

def test_fred_api_direct():
    """FRED API 직접 테스트"""
    print("🔍 FRED API 직접 연결 테스트")
    print("=" * 40)
    
    api_key = os.getenv('FRED_API_KEY', 'd4235fa1b67058fff90f8a9cc43793c8')
    print(f"🔑 사용 중인 API 키: {api_key[:8]}...")
    
    # 간단한 시리즈 테스트 (연방기금금리)
    test_url = f"https://api.stlouisfed.org/fred/series/observations?series_id=FEDFUNDS&api_key={api_key}&file_type=json&limit=5"
    
    try:
        response = requests.get(test_url, timeout=30)
        print(f"📊 HTTP 상태: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 응답 키: {list(data.keys())}")
            
            if "observations" in data:
                observations = data["observations"]
                print(f"📈 데이터 포인트: {len(observations)}개")
                
                if observations:
                    latest = observations[-1]
                    print(f"📅 최신 데이터: {latest['date']} = {latest['value']}")
                    return True
            else:
                print(f"❌ 데이터 없음: {data}")
                return False
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            print(f"응답: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ 연결 오류: {e}")
        return False

def test_fred_collector():
    """FRED 수집기 테스트"""
    print("\n🔧 FRED 수집기 테스트")
    print("=" * 40)
    
    try:
        collector = FREDDataCollector()
        
        # 단일 시리즈 테스트
        print("\n1️⃣ 단일 시리즈 테스트 (연방기금금리):")
        fed_data = collector.get_series_data("FEDFUNDS", limit=5)
        
        if fed_data:
            print(f"✅ 데이터 수집 성공: {len(fed_data)}개 포인트")
            latest = fed_data[0]
            print(f"📊 최신값: {latest['date']} = {latest['value']}%")
        else:
            print("❌ 데이터 수집 실패")
            return False
        
        # 시리즈 정보 테스트
        print("\n2️⃣ 시리즈 정보 테스트:")
        series_info = collector.get_series_info("FEDFUNDS")
        
        if series_info:
            print(f"✅ 시리즈 정보:")
            print(f"  제목: {series_info.get('title', 'N/A')}")
            print(f"  단위: {series_info.get('units', 'N/A')}")
            print(f"  주기: {series_info.get('frequency', 'N/A')}")
        else:
            print("❌ 시리즈 정보 수집 실패")
        
        # 종합 지표 수집 테스트
        print("\n3️⃣ 종합 지표 수집 테스트:")
        comprehensive_data = collector.collect_key_indicators()
        
        summary = comprehensive_data.get('summary', {})
        collected = summary.get('collected_indicators', 0)
        total = summary.get('total_indicators', 0)
        
        print(f"📊 수집 결과: {collected}/{total}개 지표")
        
        if collected > 0:
            print("✅ 종합 수집 성공!")
            
            # 주요 지표 출력
            indicators = comprehensive_data.get('indicators', {})
            print(f"\n📈 수집된 주요 지표:")
            
            for name, data in list(indicators.items())[:5]:
                title = data.get('title', name)
                value = data.get('latest_value', 0)
                units = data.get('units', '')
                change = data.get('change', 0)
                
                print(f"  • {title}: {value} {units} ({change:+.2f})")
            
            return True
        else:
            print("❌ 종합 수집 실패")
            return False
            
    except Exception as e:
        print(f"❌ 수집기 테스트 오류: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 테스트"""
    print("🧪 FRED API 연결 및 수집기 테스트")
    print("=" * 50)
    
    # 환경변수 확인
    api_key = os.getenv('FRED_API_KEY')
    if api_key:
        print(f"✅ 환경변수 FRED_API_KEY 설정됨: {api_key[:8]}...")
    else:
        print("⚠️ 환경변수 FRED_API_KEY 없음. 하드코딩된 키 사용")
    
    # 직접 API 테스트
    direct_success = test_fred_api_direct()
    
    # 수집기 테스트
    collector_success = test_fred_collector()
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약")
    print("-" * 25)
    print(f"직접 API 연결: {'✅ 성공' if direct_success else '❌ 실패'}")
    print(f"FRED 수집기: {'✅ 성공' if collector_success else '❌ 실패'}")
    
    if direct_success and collector_success:
        print("\n🎉 FRED API 연결 및 수집기 모두 정상 작동!")
        print("이제 실제 경제 데이터를 사용할 수 있습니다.")
    else:
        print("\n⚠️ 일부 테스트 실패. 문제를 확인해주세요.")

if __name__ == "__main__":
    main()
