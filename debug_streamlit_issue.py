#!/usr/bin/env python3
"""
Streamlit 데이터 수집 문제 진단 스크립트
"""

import sys
import os
import time
import traceback
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_data_collection_step_by_step():
    """단계별 데이터 수집 테스트"""
    
    print("🔍 Streamlit 데이터 수집 문제 진단")
    print("=" * 50)
    
    # 환경변수 확인
    print("\n1️⃣ 환경변수 확인:")
    alpha_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    fred_key = os.getenv('FRED_API_KEY')
    
    print(f"  ALPHA_VANTAGE_API_KEY: {'✅ 설정됨' if alpha_key else '❌ 없음'}")
    print(f"  FRED_API_KEY: {'✅ 설정됨' if fred_key else '❌ 없음'}")
    
    # Enhanced Data Collector 초기화 테스트
    print("\n2️⃣ Enhanced Data Collector 초기화 테스트:")
    try:
        from data_monitoring.enhanced_data_collector import EnhancedGlobalDataCollector
        collector = EnhancedGlobalDataCollector()
        print("  ✅ Enhanced Data Collector 초기화 성공")
    except Exception as e:
        print(f"  ❌ Enhanced Data Collector 초기화 실패: {e}")
        traceback.print_exc()
        return False
    
    # 각 데이터 소스별 개별 테스트
    results = {}
    
    # Intelligence 데이터 테스트
    print("\n3️⃣ Intelligence 데이터 수집 테스트:")
    start_time = time.time()
    try:
        intelligence_data = collector.collect_intelligence_data()
        elapsed = time.time() - start_time
        
        if intelligence_data.get('status') == 'success':
            print(f"  ✅ Intelligence 데이터 수집 성공 ({elapsed:.1f}초)")
            summary = intelligence_data.get('summary', {})
            print(f"     시장 상태: {summary.get('market_status_count', 0)}개")
            results['intelligence'] = True
        else:
            print(f"  ❌ Intelligence 데이터 수집 실패 ({elapsed:.1f}초)")
            print(f"     오류: {intelligence_data.get('error', 'Unknown')}")
            results['intelligence'] = False
            
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"  ❌ Intelligence 데이터 수집 예외 ({elapsed:.1f}초): {e}")
        results['intelligence'] = False
    
    # FRED 데이터 테스트
    print("\n4️⃣ FRED 데이터 수집 테스트:")
    start_time = time.time()
    try:
        fred_data = collector.collect_fred_data()
        elapsed = time.time() - start_time
        
        if fred_data.get('status') == 'success':
            print(f"  ✅ FRED 데이터 수집 성공 ({elapsed:.1f}초)")
            summary = fred_data.get('summary', {})
            print(f"     경제 지표: {summary.get('collected_indicators', 0)}개")
            results['fred'] = True
        else:
            print(f"  ❌ FRED 데이터 수집 실패 ({elapsed:.1f}초)")
            print(f"     오류: {fred_data.get('error', 'Unknown')}")
            results['fred'] = False
            
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"  ❌ FRED 데이터 수집 예외 ({elapsed:.1f}초): {e}")
        results['fred'] = False
    
    # 뉴스 데이터 테스트
    print("\n5️⃣ 뉴스 데이터 수집 테스트:")
    start_time = time.time()
    try:
        news_data = collector.collect_enhanced_news_data()
        elapsed = time.time() - start_time
        
        if news_data.get('status') == 'success':
            print(f"  ✅ 뉴스 데이터 수집 성공 ({elapsed:.1f}초)")
            summary = news_data.get('summary', {})
            print(f"     뉴스 기사: {summary.get('total_articles', 0)}개")
            results['news'] = True
        else:
            print(f"  ❌ 뉴스 데이터 수집 실패 ({elapsed:.1f}초)")
            print(f"     오류: {news_data.get('error', 'Unknown')}")
            results['news'] = False
            
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"  ❌ 뉴스 데이터 수집 예외 ({elapsed:.1f}초): {e}")
        results['news'] = False
    
    # 전체 데이터 수집 테스트 (Streamlit에서 사용하는 함수)
    print("\n6️⃣ 전체 데이터 수집 테스트 (Streamlit 함수):")
    start_time = time.time()
    try:
        # Streamlit에서 사용하는 collect_all_data 함수 시뮬레이션
        all_data = {
            'intelligence': collector.collect_intelligence_data(),
            'fred': collector.collect_fred_data(),
            'news': collector.collect_enhanced_news_data(),
            'timestamp': datetime.now().isoformat()
        }
        elapsed = time.time() - start_time
        
        print(f"  ✅ 전체 데이터 수집 완료 ({elapsed:.1f}초)")
        
        # 각 데이터 소스 상태 확인
        for source, data in all_data.items():
            if source != 'timestamp':
                status = data.get('status', 'unknown')
                print(f"     {source}: {status}")
        
        results['total'] = True
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"  ❌ 전체 데이터 수집 실패 ({elapsed:.1f}초): {e}")
        traceback.print_exc()
        results['total'] = False
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("📊 진단 결과 요약")
    print("-" * 25)
    
    for test_name, success in results.items():
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{test_name:12} {status}")
    
    # 문제 분석 및 해결책 제시
    print("\n🔧 문제 분석 및 해결책:")
    
    failed_tests = [name for name, success in results.items() if not success]
    
    if not failed_tests:
        print("  ✅ 모든 테스트 통과! Streamlit 문제는 다른 원인일 수 있습니다.")
        print("     - 캐시 문제: st.cache_data.clear() 시도")
        print("     - 브라우저 새로고침")
        print("     - Streamlit 재시작")
    else:
        print(f"  ❌ 실패한 테스트: {', '.join(failed_tests)}")
        
        if 'intelligence' in failed_tests:
            print("     - Alpha Vantage API 키 확인")
            print("     - 네트워크 연결 확인")
        
        if 'fred' in failed_tests:
            print("     - FRED API 키 확인")
            print("     - FRED API 서버 상태 확인")
        
        if 'news' in failed_tests:
            print("     - RSS 피드 접근 확인")
            print("     - textblob 패키지 설치 확인")
    
    return results

def test_streamlit_cache_function():
    """Streamlit 캐시 함수 테스트"""
    print("\n7️⃣ Streamlit 캐시 함수 테스트:")
    
    try:
        # Streamlit 없이 캐시 함수 시뮬레이션
        from data_monitoring.enhanced_data_collector import EnhancedGlobalDataCollector
        
        def collect_all_data_simulation():
            collector = EnhancedGlobalDataCollector()
            
            intelligence_data = collector.collect_intelligence_data()
            fred_data = collector.collect_fred_data()
            news_data = collector.collect_enhanced_news_data()
            
            return {
                'intelligence': intelligence_data,
                'fred': fred_data,
                'news': news_data,
                'timestamp': datetime.now().isoformat()
            }, None
        
        start_time = time.time()
        all_data, error = collect_all_data_simulation()
        elapsed = time.time() - start_time
        
        if error:
            print(f"  ❌ 캐시 함수 시뮬레이션 실패 ({elapsed:.1f}초): {error}")
            return False
        else:
            print(f"  ✅ 캐시 함수 시뮬레이션 성공 ({elapsed:.1f}초)")
            return True
            
    except Exception as e:
        print(f"  ❌ 캐시 함수 시뮬레이션 예외: {e}")
        return False

def main():
    """메인 진단 프로세스"""
    print(f"🕐 진단 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 단계별 테스트
    results = test_data_collection_step_by_step()
    
    # 캐시 함수 테스트
    cache_result = test_streamlit_cache_function()
    
    # 최종 권장사항
    print("\n" + "=" * 50)
    print("🎯 최종 권장사항")
    print("-" * 25)
    
    if all(results.values()) and cache_result:
        print("✅ 모든 데이터 수집 기능이 정상 작동합니다.")
        print("🔧 Streamlit 관련 해결책:")
        print("   1. 브라우저 강력 새로고침 (Ctrl+Shift+R)")
        print("   2. Streamlit 재시작")
        print("   3. 브라우저 캐시 삭제")
        print("   4. 다른 브라우저로 테스트")
    else:
        print("❌ 데이터 수집에 문제가 있습니다.")
        print("🔧 우선 해결해야 할 문제:")
        
        failed = [name for name, success in results.items() if not success]
        for fail in failed:
            print(f"   - {fail} 데이터 수집 문제")
    
    print(f"\n🕐 진단 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
