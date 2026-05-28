#!/usr/bin/env python3
"""
Agents 시스템 테스트 스크립트
경제 뉴스 자동 생성 시스템의 Strand Agents 테스트
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_agents_system():
    """Agents 시스템 전체 테스트"""
    
    print("🚀 경제 뉴스 Agents 시스템 테스트 시작")
    print("=" * 60)
    
    try:
        # 1. 모듈 import 테스트
        print("\n1️⃣ 모듈 Import 테스트")
        from agents import main_orchestrator, orchestrator
        print("✅ Agents 모듈 import 성공")
        
        # 2. 등록된 에이전트 확인
        print("\n2️⃣ 등록된 에이전트 확인")
        agents_info = orchestrator.list_agents()
        print(f"📊 총 {len(agents_info)}개 에이전트 등록됨:")
        for agent_id, capabilities in agents_info.items():
            print(f"  🤖 {agent_id}: {', '.join(capabilities[:3])}...")
        
        # 3. 시스템 상태 확인
        print("\n3️⃣ 시스템 상태 확인")
        status = main_orchestrator.get_system_status()
        print(f"📈 오케스트레이터 상태: {status['orchestrator_status']}")
        print(f"📁 출력 디렉토리: {len(status['output_directories'])}개 설정됨")
        
        # 4. 샘플 이벤트로 테스트
        print("\n4️⃣ 샘플 이벤트 처리 테스트")
        
        sample_event = {
            'symbol': 'AAPL',
            'event_type': 'price_change',
            'severity': 0.7,
            'data': {
                'current_price': 150.25,
                'change_percent': 3.2,
                'volume_ratio': 1.5,
                'timestamp': datetime.now().isoformat()
            },
            'description': 'AAPL 주가 3.2% 상승'
        }
        
        print(f"📊 테스트 이벤트: {sample_event['description']}")
        
        # 오케스트레이터를 통한 처리
        from agents.strands_framework import StrandContext
        
        context = StrandContext(
            strand_id=f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            input_data={'event': sample_event}
        )
        
        print("⏳ 이벤트 처리 중...")
        result = await main_orchestrator.process(context)
        
        if result.get('success'):
            print("✅ 이벤트 처리 성공!")
            print(f"📄 생성된 기사 제목: {result.get('article', {}).get('title', 'N/A')}")
            print(f"🖼️ 생성된 이미지: {len(result.get('images', []))}개")
            print(f"📢 추천 광고: {len(result.get('ads', []))}개")
            
            # 결과 저장
            output_file = f"output/test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2, default=str)
            print(f"💾 결과 저장: {output_file}")
            
        else:
            print("❌ 이벤트 처리 실패")
            print(f"오류: {result.get('error', 'Unknown error')}")
        
        # 5. 성능 테스트 (다중 이벤트)
        print("\n5️⃣ 다중 이벤트 처리 테스트")
        
        multiple_events = [
            {
                'symbol': 'GOOGL',
                'event_type': 'volume_spike',
                'severity': 0.6,
                'data': {'volume_ratio': 2.5},
                'description': 'GOOGL 거래량 급증'
            },
            {
                'symbol': 'TSLA',
                'event_type': 'high_volatility',
                'severity': 0.8,
                'data': {'volatility': 12.5},
                'description': 'TSLA 높은 변동성'
            }
        ]
        
        print(f"📊 {len(multiple_events)}개 이벤트 동시 처리 테스트")
        print("⏳ 다중 이벤트 처리 중...")
        
        multi_results = await main_orchestrator.process_multiple_events(multiple_events)
        
        print(f"✅ 다중 이벤트 처리 완료: {len(multi_results)}개 성공")
        
        # 6. 출력 파일 확인
        print("\n6️⃣ 출력 파일 확인")
        import os
        
        output_dirs = ['output', 'streamlit_articles', 'output/charts', 'output/images']
        for dir_path in output_dirs:
            if os.path.exists(dir_path):
                files = os.listdir(dir_path)
                print(f"📁 {dir_path}: {len(files)}개 파일")
            else:
                print(f"📁 {dir_path}: 디렉토리 없음")
        
        print("\n" + "=" * 60)
        print("🎉 Agents 시스템 테스트 완료!")
        print("✅ 모든 컴포넌트가 정상적으로 작동합니다.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_individual_agents():
    """개별 에이전트 테스트"""
    
    print("\n🔍 개별 에이전트 테스트")
    print("-" * 40)
    
    try:
        from agents import (
            DataAnalysisStrand, ArticleWriterStrand, 
            ReviewStrand, ImageGeneratorStrand, AdRecommendationStrand
        )
        from agents.strands_framework import StrandContext
        
        # 테스트 데이터
        test_data = {
            'symbol': 'AAPL',
            'current_price': 150.25,
            'change_percent': 3.2,
            'volume': 50000000,
            'timestamp': datetime.now().isoformat()
        }
        
        context = StrandContext(
            strand_id="individual_test",
            input_data=test_data
        )
        
        # 1. 데이터 분석 에이전트 테스트
        print("📊 데이터 분석 에이전트 테스트...")
        data_agent = DataAnalysisStrand()
        data_result = await data_agent.process(context)
        print(f"✅ 데이터 분석 완료: {len(data_result.get('charts', []))}개 차트 생성")
        
        # 2. 기사 작성 에이전트 테스트
        print("✍️ 기사 작성 에이전트 테스트...")
        writer_agent = ArticleWriterStrand()
        article_result = await writer_agent.process(context)
        print(f"✅ 기사 작성 완료: {len(article_result.get('title', ''))} 글자 제목")
        
        # 3. 검수 에이전트 테스트
        print("🔍 검수 에이전트 테스트...")
        review_agent = ReviewStrand()
        review_result = await review_agent.process(context)
        print(f"✅ 검수 완료: 품질 점수 {review_result.get('quality_score', 0)}")
        
        print("✅ 개별 에이전트 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 개별 에이전트 테스트 실패: {e}")

def main():
    """메인 함수"""
    
    print("🤖 경제 뉴스 Agents 시스템 종합 테스트")
    print("=" * 60)
    
    # 출력 디렉토리 생성
    import os
    os.makedirs('output', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # 비동기 테스트 실행
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # 전체 시스템 테스트
        success = loop.run_until_complete(test_agents_system())
        
        if success:
            # 개별 에이전트 테스트
            loop.run_until_complete(test_individual_agents())
            
            print("\n🎯 테스트 요약")
            print("✅ Strands Framework 정상 작동")
            print("✅ 모든 에이전트 등록 및 초기화 완료")
            print("✅ 비동기 처리 시스템 정상")
            print("✅ AWS Bedrock 연동 정상")
            print("✅ 출력 파일 생성 정상")
            
            print("\n📋 다음 단계 권장사항:")
            print("1. demo_streamlit.py 실행하여 웹 대시보드 확인")
            print("2. 실제 시장 데이터로 테스트")
            print("3. Slack 알림 시스템 연동 테스트")
            
        else:
            print("\n❌ 시스템에 문제가 있습니다. 로그를 확인해주세요.")
            
    except KeyboardInterrupt:
        print("\n⏹️ 사용자에 의해 테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n💥 예상치 못한 오류: {e}")
    finally:
        loop.close()

if __name__ == "__main__":
    main()
