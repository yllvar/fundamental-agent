#!/usr/bin/env python3
"""
Alpha Vantage API 간단 테스트
"""

import requests
import json

def test_alphavantage_api():
    print('🔍 Alpha Vantage API 테스트 결과:')
    print('=' * 50)
    
    # AAPL 5분 간격 데이터 요청
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=AAPL&interval=5min&apikey=9TLAUWS4L3099YK3'
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if 'Error Message' in data:
            print(f'❌ 오류: {data["Error Message"]}')
            return False
        elif 'Note' in data:
            print(f'⚠️  알림: {data["Note"]}')
            return False
        else:
            meta_data = data.get('Meta Data', {})
            time_series = data.get('Time Series (5min)', {})
            
            print(f'✅ 성공적으로 데이터 수집')
            print(f'   심볼: {meta_data.get("2. Symbol", "N/A")}')
            print(f'   마지막 업데이트: {meta_data.get("3. Last Refreshed", "N/A")}')
            print(f'   데이터 포인트: {len(time_series)}개')
            
            if time_series:
                latest_time = max(time_series.keys())
                latest_data = time_series[latest_time]
                print(f'   최신 가격: ${latest_data["4. close"]}')
                print(f'   최신 시간: {latest_time}')
                print(f'   거래량: {latest_data["5. volume"]}')
                
                # 최근 5개 데이터 포인트 표시
                print('\n📊 최근 5개 데이터 포인트:')
                sorted_times = sorted(time_series.keys(), reverse=True)
                for i, time_key in enumerate(sorted_times[:5]):
                    data_point = time_series[time_key]
                    print(f'   {i+1}. {time_key}: ${data_point["4. close"]} (Vol: {data_point["5. volume"]})')
            
            return True
            
    except Exception as e:
        print(f'❌ 요청 오류: {e}')
        return False

if __name__ == "__main__":
    test_alphavantage_api()
