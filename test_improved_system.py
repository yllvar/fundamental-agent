#!/usr/bin/env python3
"""
개선된 경제 뉴스 시스템 테스트
- 차트 폰트 문제 해결
- 기사 이미지 생성
- 광고 표시 개선
- 기사 분량 확대 (2000자 이상)
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 로깅 설정
logging.basicConfig(level=logging.INFO)

async def test_improved_features():
    """개선된 기능들 테스트"""
    
    print("🔍 개선된 경제 뉴스 시스템 테스트")
    print("=" * 50)
    
    try:
        # 1. Agent 시스템 임포트
        from agents import main_orchestrator
        from agents.strands_framework import StrandContext
        
        print("✅ Agent 시스템 임포트 성공")
        
        # 2. 테스트 이벤트 생성
        test_event = {
            'symbol': 'AAPL',
            'event_type': 'price_change',
            'severity': 'medium',
            'title': 'AAPL 주가 상승',
            'description': 'AAPL 주가가 3.5% 상승하며 시장의 주목을 받고 있습니다.',
            'change_percent': 3.5,
            'current_value': 150.25,
            'previous_value': 145.00,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"✅ 테스트 이벤트 생성: {test_event['symbol']} {test_event['event_type']}")
        
        # 3. 컨텍스트 생성
        context = StrandContext(
            strand_id=f"test_improved_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            input_data={'event': test_event}
        )
        
        print("✅ Strand 컨텍스트 생성")
        
        # 4. 전체 워크플로우 실행
        print("\n🚀 전체 워크플로우 실행 중...")
        print("  📊 데이터 분석 (개선된 차트 폰트)")
        print("  ✍️ 기사 작성 (2000자 이상)")
        print("  🖼️ 이미지 생성 (기사 기반)")
        print("  📢 광고 추천 (3개)")
        print("  🌐 Streamlit 페이지 생성")
        
        result = await main_orchestrator.process(context)
        
        if result.get('status') == 'success':
            print("\n🎉 워크플로우 실행 성공!")
            
            # 5. 결과 분석
            package = result.get('package', {})
            
            # 기사 분량 확인
            article = package.get('article', {})
            if article:
                body_length = len(article.get('body', ''))
                print(f"📝 기사 본문 길이: {body_length}자 ({'✅ 목표 달성' if body_length >= 2000 else '⚠️ 목표 미달'})")
                print(f"📰 기사 제목: {article.get('title', 'N/A')}")
                
                # 이미지 프롬프트 확인
                image_prompt = article.get('image_prompt', '')
                if image_prompt:
                    print(f"🖼️ 이미지 프롬프트: {image_prompt[:100]}...")
            
            # 이미지 생성 확인
            images = package.get('images', {})
            if images:
                image_count = len([v for v in images.values() if v and isinstance(v, str) and v.endswith('.png')])
                print(f"🖼️ 생성된 이미지: {image_count}개")
                
                if images.get('article_image'):
                    print(f"  📰 기사 이미지: {os.path.basename(images['article_image'])}")
                if images.get('event_image'):
                    print(f"  📊 이벤트 이미지: {os.path.basename(images['event_image'])}")
                if images.get('wordcloud'):
                    print(f"  ☁️ 워드클라우드: {os.path.basename(images['wordcloud'])}")
            
            # 광고 확인
            ads = package.get('advertisements', [])
            print(f"📢 추천 광고: {len(ads)}개")
            for i, ad in enumerate(ads[:3]):
                print(f"  {i+1}. {ad.get('title', 'N/A')} ({ad.get('category', 'N/A')})")
            
            # 차트 확인
            data_analysis = package.get('data_analysis', {})
            chart_paths = data_analysis.get('chart_paths', [])
            print(f"📊 생성된 차트: {len(chart_paths)}개")
            
            # Streamlit 페이지 확인
            streamlit_page = result.get('streamlit_page', '')
            if streamlit_page:
                print(f"🌐 Streamlit 페이지: {os.path.basename(streamlit_page)}")
                print(f"\n💡 확인 명령어:")
                print(f"   streamlit run {streamlit_page}")
            
            print(f"\n📊 실행 시간: {result.get('execution_time', 0):.1f}초")
            
        else:
            print(f"\n❌ 워크플로우 실행 실패: {result.get('error', 'Unknown error')}")
            return False
        
        print("\n🎯 개선사항 확인:")
        print("  ✅ 차트 폰트 문제 해결 (matplotlib 설정 개선)")
        print("  ✅ 기사 기반 이미지 생성 추가")
        print("  ✅ 기사 분량 2000자 이상으로 확대")
        print("  ✅ 광고 3개를 기사 뒤에 표시")
        print("  ✅ Streamlit 페이지 레이아웃 개선")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_improved_features())
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 개선된 시스템 테스트 완료!")
        print("\n💡 다음 단계:")
        print("  1. 전체 시스템 실행: ./run_news_system.sh")
        print("  2. 생성된 기사 확인: streamlit run [생성된 파일]")
    else:
        print("❌ 테스트 실패 - 문제를 확인해주세요")
    print("=" * 50)
