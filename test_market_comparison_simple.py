#!/usr/bin/env python3
"""
시장 비교 분석 수정 사항 간단 테스트
"""

import sys
import os
import asyncio
import logging
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class SimpleMarketEvent:
    """간단한 이벤트 클래스"""
    def __init__(self, symbol):
        self.symbol = symbol
        self.timestamp = datetime.now()

async def test_market_comparison_direct():
    """시장 비교 분석 직접 테스트"""
    
    print("🔧 시장 비교 분석 수정 사항 직접 테스트 시작...")
    
    try:
        # DataAnalysisAgent 임포트
        from agents.data_analysis_agent import DataAnalysisAgent
        
        # Agent 초기화
        agent = DataAnalysisAgent()
        
        # 테스트 심볼들
        test_symbols = ["AAPL", "GOOGL", "MSFT"]
        
        for symbol in test_symbols:
            print(f"\n📊 {symbol} 종목 테스트...")
            
            try:
                # 데이터 수집
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="1mo", interval="1d")
                
                if len(data) == 0:
                    print(f"   ❌ {symbol} 데이터 수집 실패")
                    continue
                
                # 시장 비교 분석 직접 호출
                result = await agent._compare_with_market(symbol, data)
                
                if result:
                    print(f"   ✅ {symbol} 분석 성공!")
                    print(f"      - 베타: {result.get('beta', 'N/A')}")
                    print(f"      - SPY 상관관계: {result.get('correlation_with_spy', 'N/A')}")
                    print(f"      - 상대 성과: {result.get('relative_performance_1m', 'N/A')}%")
                    print(f"      - 데이터 포인트: {result.get('data_points_used', 'N/A')}")
                    
                    if 'error' in result:
                        print(f"      ⚠️ 경고: {result['error']}")
                else:
                    print(f"   ❌ {symbol} 분석 결과 없음")
                    
            except Exception as e:
                print(f"   ❌ {symbol} 분석 중 오류: {e}")
        
        print("\n🎉 직접 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

def test_numpy_operations():
    """numpy 연산 테스트"""
    
    print("\n🔧 numpy 연산 테스트...")
    
    try:
        # 다른 크기의 배열 생성 (문제 상황 재현)
        arr1 = np.random.randn(22)
        arr2 = np.random.randn(21)
        
        print(f"배열1 크기: {len(arr1)}, 배열2 크기: {len(arr2)}")
        
        # 길이 맞추기
        min_len = min(len(arr1), len(arr2))
        arr1_aligned = arr1[:min_len]
        arr2_aligned = arr2[:min_len]
        
        print(f"정렬 후 - 배열1: {len(arr1_aligned)}, 배열2: {len(arr2_aligned)}")
        
        # 공분산 계산
        cov_matrix = np.cov(arr1_aligned, arr2_aligned)
        print(f"공분산 행렬 형태: {cov_matrix.shape}")
        print(f"공분산: {cov_matrix[0, 1]}")
        
        # 상관관계 계산
        corr_matrix = np.corrcoef(arr1_aligned, arr2_aligned)
        print(f"상관관계 행렬 형태: {corr_matrix.shape}")
        print(f"상관관계: {corr_matrix[0, 1]}")
        
        print("✅ numpy 연산 테스트 성공!")
        
    except Exception as e:
        print(f"❌ numpy 연산 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # numpy 연산 테스트 먼저 실행
    test_numpy_operations()
    
    # 시장 비교 분석 테스트
    asyncio.run(test_market_comparison_direct())
