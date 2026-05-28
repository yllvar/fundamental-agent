#!/usr/bin/env python3
"""
AI 기사 생성 시스템 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.orchestrator_strand import OrchestratorStrand
from agents.strands_framework import StrandContext

def test_ai_article_system():
    """AI 기사 생성 시스템 테스트"""
    
    print("=== AI 기사 생성 시스템 테스트 ===")
    
    try:
        # 오케스트레이터 초기화
        print("🤖 오케스트레이터 초기화 중...")
        orchestrator = OrchestratorStrand()
        print("✅ 오케스트레이터 초기화 완료")
        
        # 테스트 이벤트 데이터
        test_events = [{
            'type': 'market_movement',
            'symbol': 'AAPL',
            'description': '애플 주가 5% 상승',
            'severity': 0.8,
            'timestamp': '2025-08-07T06:30:00'
        }]
        
        # 컨텍스트 생성
        print("📋 컨텍스트 생성 중...")
        context = StrandContext(
            strand_id="test_article_generation",
            input_data={
                "events": test_events,
                "request_type": "comprehensive_article"
            }
        )
        print("✅ 컨텍스트 생성 완료")
        
        # 각 단계별 테스트
        print("\n📊 데이터 분석 테스트...")
        analysis_result = orchestrator.execute_data_analysis(context)
        if analysis_result:
            print("✅ 데이터 분석 성공")
        else:
            print("⚠️ 데이터 분석 부분 실패")
        
        print("\n✍️ 기사 작성 테스트...")
        article_result = orchestrator.execute_article_writing(context)
        if article_result:
            print("✅ 기사 작성 성공")
            print(f"   제목: {article_result.get('title', 'N/A')}")
        else:
            print("⚠️ 기사 작성 부분 실패")
        
        print("\n🎨 이미지 생성 테스트...")
        image_result = orchestrator.execute_image_generation(context)
        if image_result:
            print("✅ 이미지 생성 성공")
        else:
            print("⚠️ 이미지 생성 부분 실패")
        
        print("\n🔍 기사 검수 테스트...")
        review_result = orchestrator.execute_review(context)
        if review_result:
            print("✅ 기사 검수 성공")
        else:
            print("⚠️ 기사 검수 부분 실패")
        
        print("\n📢 광고 추천 테스트...")
        ad_result = orchestrator.execute_ad_recommendation(context)
        if ad_result:
            print("✅ 광고 추천 성공")
        else:
            print("⚠️ 광고 추천 부분 실패")
        
        print("\n🎉 전체 시스템 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_article_system()
