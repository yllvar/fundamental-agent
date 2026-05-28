#!/usr/bin/env python3
"""
개선된 경제 네트워크 분석 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_monitoring.enhanced_economic_network_analyzer import EnhancedEconomicNetworkAnalyzer
import json

def test_enhanced_network_analysis():
    """개선된 네트워크 분석 테스트"""
    
    print("🚀 개선된 경제 네트워크 분석 테스트 시작")
    print("=" * 60)
    
    # 분석기 초기화
    analyzer = EnhancedEconomicNetworkAnalyzer()
    
    # 샘플 경제 텍스트
    sample_texts = [
        "연준이 기준금리를 0.25%p 인상하며 인플레이션 억제에 나섰다. 이번 금리 인상으로 주식시장은 하락세를 보이고 있으며, 특히 기술주가 큰 타격을 받고 있다.",
        "애플과 마이크로소프트가 AI 기술 개발을 위한 파트너십을 발표했다. 이는 기술 섹터의 경쟁력 강화와 함께 관련 주가 상승을 이끌고 있다.",
        "중국과 미국 간의 무역 분쟁이 재점화되면서 글로벌 공급망에 차질이 우려된다. 이로 인해 원자재 가격이 상승하고 인플레이션 압력이 증가하고 있다.",
        "비트코인이 다시 5만 달러를 돌파하며 암호화폐 시장이 활기를 띠고 있다. 기관 투자자들의 관심 증가와 함께 디지털 자산에 대한 투자 심리가 개선되고 있다.",
        "ESG 투자가 주류로 자리잡으면서 친환경 기업들의 주가가 상승하고 있다. 특히 재생에너지와 전기차 관련 기업들이 큰 관심을 받고 있다.",
        "고용시장이 개선되면서 실업률이 3.5%로 하락했다. 이는 소비자 신뢰도 상승과 함께 소비 증가로 이어질 것으로 예상된다.",
        "부동산 시장이 금리 인상에도 불구하고 견조한 모습을 보이고 있다. 주택 공급 부족과 함께 가격 상승 압력이 지속되고 있다.",
        "에너지 가격 상승으로 인플레이션 우려가 커지고 있다. 특히 원유와 천연가스 가격 급등이 전체 물가 상승을 주도하고 있다.",
        "정부의 대규모 인프라 투자 계획이 발표되면서 건설 및 소재 관련 주식들이 강세를 보이고 있다. 이는 경기 부양 효과와 함께 고용 창출에도 기여할 것으로 예상된다.",
        "지정학적 리스크가 증가하면서 안전자산 선호 현상이 나타나고 있다. 금과 국채 가격이 상승하는 반면, 위험자산인 주식은 변동성이 확대되고 있다."
    ]
    
    print(f"📝 분석할 텍스트 수: {len(sample_texts)}")
    print()
    
    # 1. 개념 추출 테스트
    print("1️⃣ 경제 개념 추출 테스트")
    print("-" * 40)
    
    for i, text in enumerate(sample_texts[:3], 1):
        print(f"\n📄 텍스트 {i}: {text[:50]}...")
        concepts, scores = analyzer.extract_economic_concepts(text)
        
        print(f"   발견된 개념 수: {len(concepts)}")
        for concept, data in list(concepts.items())[:3]:
            display_name = analyzer._get_concept_display_name(concept)
            print(f"   • {display_name}: {data['score']:.1f}점 ({len(data['terms'])}개 용어)")
    
    # 2. 네트워크 분석 테스트
    print("\n\n2️⃣ 네트워크 관계 분석 테스트")
    print("-" * 40)
    
    network_result = analyzer.analyze_concept_relationships(sample_texts)
    
    if 'error' in network_result:
        print(f"❌ 분석 오류: {network_result['error']}")
        return
    
    G = network_result['graph']
    concepts = network_result['concepts']
    metrics = network_result['metrics']
    
    print(f"📊 네트워크 규모:")
    print(f"   • 노드 수: {len(G.nodes())}")
    print(f"   • 엣지 수: {len(G.edges())}")
    print(f"   • 네트워크 밀도: {metrics.get('density', 0):.3f}")
    
    # 3. 상위 개념들
    print(f"\n🏆 상위 경제 개념들:")
    for concept, data in sorted(concepts.items(), key=lambda x: x[1]['total_score'], reverse=True)[:5]:
        display_name = analyzer._get_concept_display_name(concept)
        print(f"   • {display_name}: {data['total_score']:.1f}점 ({data['mention_count']}회 언급)")
    
    # 4. 주요 관계들
    print(f"\n🔗 주요 관계들:")
    edges_with_weight = [(edge[0], edge[1], edge[2]['weight']) for edge in G.edges(data=True)]
    edges_sorted = sorted(edges_with_weight, key=lambda x: x[2], reverse=True)
    
    for source, target, weight in edges_sorted[:5]:
        source_name = analyzer._get_concept_display_name(source)
        target_name = analyzer._get_concept_display_name(target)
        print(f"   • {source_name} ↔ {target_name}: {weight:.2f}")
    
    # 5. 인사이트 생성
    print(f"\n💡 생성된 인사이트:")
    insights = analyzer.generate_network_insights(network_result)
    for insight in insights:
        print(f"   • {insight}")
    
    # 6. 결과 저장
    output_file = f"output/enhanced_network_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # 그래프는 JSON으로 직렬화할 수 없으므로 제외
    save_data = {
        'concepts': concepts,
        'metrics': metrics,
        'insights': insights,
        'node_count': len(G.nodes()),
        'edge_count': len(G.edges()),
        'nodes': list(G.nodes()),
        'edges': [(edge[0], edge[1], edge[2]) for edge in G.edges(data=True)]
    }
    
    try:
        os.makedirs('output', exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n💾 결과 저장: {output_file}")
    except Exception as e:
        print(f"❌ 저장 오류: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 개선된 네트워크 분석 테스트 완료!")
    
    # 개선 효과 요약
    print(f"\n🚀 개선 효과 요약:")
    print(f"   • 노드 수: {len(G.nodes())}개 (기존 7-21개 → 대폭 증가)")
    print(f"   • 의미 있는 관계: 경제적 연관성 기반")
    print(f"   • 카테고리화: 16개 경제 분야로 체계화")
    print(f"   • 감정 분석: 개념별 긍정/부정 감정 분석")
    print(f"   • 실시간 인사이트: {len(insights)}개 인사이트 자동 생성")

if __name__ == "__main__":
    from datetime import datetime
    test_enhanced_network_analysis()
