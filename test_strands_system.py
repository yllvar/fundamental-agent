#!/usr/bin/env python3
"""
Strands Agent 시스템 테스트
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_strands_system():
    """Strands Agent 시스템 테스트"""
    
    print("🔍 Strands Agent 시스템 테스트 시작...")
    
    try:
        # 1. 프레임워크 임포트 테스트
        print("\n📦 프레임워크 임포트 테스트:")
        from agents.strands_framework import BaseStrandAgent, StrandContext, orchestrator
        print("  ✅ Strands 프레임워크 임포트 성공")
        
        # 2. Agent 임포트 테스트
        print("\n🤖 Agent 임포트 테스트:")
        from agents import (
            DataAnalysisStrand,
            ArticleWriterStrand,
            ReviewStrand,
            ImageGeneratorStrand,
            AdRecommendationStrand,
            OrchestratorStrand,
            main_orchestrator
        )
        print("  ✅ 모든 Strand Agent 임포트 성공")
        
        # 3. 시스템 상태 확인
        print("\n📊 시스템 상태 확인:")
        status = main_orchestrator.get_system_status()
        print(f"  ✅ 등록된 에이전트: {len(status['registered_agents'])}개")
        for agent_id in status['registered_agents']:
            print(f"    - {agent_id}")
        
        # 4. 테스트 이벤트 생성
        print("\n🎯 테스트 이벤트 생성:")
        test_event = {
            'symbol': 'AAPL',
            'event_type': 'price_change',
            'severity': 'medium',
            'title': 'AAPL 가격 변동',
            'description': 'AAPL 주가가 3.5% 상승했습니다.',
            'change_percent': 3.5,
            'timestamp': datetime.now().isoformat()
        }
        print(f"  ✅ 테스트 이벤트: {test_event['symbol']} {test_event['event_type']}")
        
        # 5. 개별 Agent 테스트 (간단한 초기화 테스트)
        print("\n🔧 개별 Agent 초기화 테스트:")
        
        # 데이터 분석 Agent
        data_analyst = DataAnalysisStrand()
        print(f"  ✅ DataAnalysisStrand: {len(data_analyst.get_capabilities())}개 능력")
        
        # 기사 작성 Agent
        article_writer = ArticleWriterStrand()
        print(f"  ✅ ArticleWriterStrand: {len(article_writer.get_capabilities())}개 능력")
        
        # 검수 Agent
        reviewer = ReviewStrand()
        print(f"  ✅ ReviewStrand: {len(reviewer.get_capabilities())}개 능력")
        
        # 이미지 생성 Agent
        image_generator = ImageGeneratorStrand()
        print(f"  ✅ ImageGeneratorStrand: {len(image_generator.get_capabilities())}개 능력")
        
        # 광고 추천 Agent
        ad_recommender = AdRecommendationStrand()
        print(f"  ✅ AdRecommendationStrand: {len(ad_recommender.get_capabilities())}개 능력")
        
        # 6. 출력 디렉토리 확인
        print("\n📁 출력 디렉토리 확인:")
        output_dirs = [
            'output/automated_articles',
            'output/charts', 
            'output/images',
            'streamlit_articles'
        ]
        
        for dir_path in output_dirs:
            if os.path.exists(dir_path):
                file_count = len(os.listdir(dir_path))
                print(f"  ✅ {dir_path}: {file_count}개 파일")
            else:
                print(f"  ⚠️ {dir_path}: 디렉토리 없음 (자동 생성됨)")
                os.makedirs(dir_path, exist_ok=True)
        
        # 7. 환경 변수 확인
        print("\n🔑 환경 변수 확인:")
        env_vars = ['DEEPSEEK_API_KEY']
        for var in env_vars:
            value = os.getenv(var)
            if value:
                print(f"  ✅ {var}: 설정됨")
            else:
                print(f"  ⚠️ {var}: 설정되지 않음")
        
        print("\n🎉 Strands Agent 시스템 테스트 완료!")
        print("\n💡 다음 단계:")
        print("  1. 전체 워크플로우 테스트: python test_full_workflow.py")
        print("  2. 실제 이벤트 처리: python -c \"from agents import main_orchestrator; import asyncio; asyncio.run(main_orchestrator.process(...))\"")
        print("  3. Streamlit 대시보드 실행: streamlit run streamlit_articles/[최신파일].py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_simple_workflow():
    """간단한 워크플로우 테스트"""
    
    print("\n🚀 간단한 워크플로우 테스트...")
    
    try:
        from agents import main_orchestrator
        from agents.strands_framework import StrandContext
        
        # 테스트 이벤트
        test_event = {
            'symbol': 'TEST',
            'event_type': 'price_change',
            'severity': 'low',
            'title': 'TEST 심볼 테스트',
            'description': '시스템 테스트용 이벤트입니다.',
            'change_percent': 1.0,
            'timestamp': datetime.now().isoformat()
        }
        
        # 컨텍스트 생성
        context = StrandContext(
            strand_id=f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            input_data={'event': test_event}
        )
        
        print("  📊 데이터 분석 Agent만 테스트...")
        
        # 데이터 분석 Agent만 테스트 (실제 데이터 없이)
        from agents import DataAnalysisStrand
        data_analyst = DataAnalysisStrand()
        
        # 간단한 능력 확인
        capabilities = data_analyst.get_capabilities()
        print(f"  ✅ 데이터 분석 Agent 능력: {capabilities}")
        
        print("  ✅ 간단한 워크플로우 테스트 완료")
        return True
        
    except Exception as e:
        print(f"  ❌ 워크플로우 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    # 기본 테스트 실행
    success = asyncio.run(test_strands_system())
    
    if success:
        # 간단한 워크플로우 테스트
        asyncio.run(test_simple_workflow())
    
    print(f"\n{'='*50}")
    print("테스트 완료!")
    print(f"{'='*50}")
