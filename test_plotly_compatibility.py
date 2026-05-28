#!/usr/bin/env python3
"""
Plotly 호환성 테스트 스크립트
"""

import plotly.graph_objects as go
import plotly
import sys

def test_plotly_compatibility():
    """Plotly 호환성 테스트"""
    
    print("🧪 Plotly 호환성 테스트")
    print("=" * 40)
    
    # Plotly 버전 확인
    print(f"📦 Plotly 버전: {plotly.__version__}")
    
    # 기본 그래프 생성 테스트
    try:
        # 샘플 데이터
        x_data = [1, 2, 3, 4]
        y_data = [10, 11, 12, 13]
        
        # 구버전 방식 (titlefont_size) - 실패해야 함
        print("\n1️⃣ 구버전 방식 테스트 (titlefont_size):")
        try:
            fig_old = go.Figure(
                data=go.Scatter(x=x_data, y=y_data),
                layout=go.Layout(
                    title="테스트 그래프",
                    titlefont_size=16  # 이것이 문제
                )
            )
            print("   ❌ 구버전 방식이 작동함 (예상과 다름)")
        except Exception as e:
            print(f"   ✅ 구버전 방식 실패 (예상됨): {type(e).__name__}")
        
        # 신버전 방식 (title dict) - 성공해야 함
        print("\n2️⃣ 신버전 방식 테스트 (title dict):")
        try:
            fig_new = go.Figure(
                data=go.Scatter(x=x_data, y=y_data),
                layout=go.Layout(
                    title=dict(
                        text="테스트 그래프",
                        font=dict(size=16)
                    )
                )
            )
            print("   ✅ 신버전 방식 성공")
            
            # HTML 생성 테스트
            html_str = fig_new.to_html()
            print(f"   ✅ HTML 생성 성공 (길이: {len(html_str)})")
            
        except Exception as e:
            print(f"   ❌ 신버전 방식 실패: {e}")
            return False
        
        # 네트워크 그래프 스타일 테스트
        print("\n3️⃣ 네트워크 그래프 스타일 테스트:")
        try:
            # 노드 데이터
            node_trace = go.Scatter(
                x=[1, 2, 3], 
                y=[1, 2, 1],
                mode='markers+text',
                text=['노드1', '노드2', '노드3'],
                textposition="middle center",
                marker=dict(size=[20, 30, 25], color=['red', 'blue', 'green'])
            )
            
            # 엣지 데이터
            edge_trace = go.Scatter(
                x=[1, 2, None, 2, 3, None], 
                y=[1, 2, None, 2, 1, None],
                mode='lines',
                line=dict(width=2, color='gray')
            )
            
            # 네트워크 그래프 생성
            network_fig = go.Figure(
                data=[edge_trace, node_trace],
                layout=go.Layout(
                    title=dict(
                        text="네트워크 테스트",
                        font=dict(size=16)
                    ),
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    height=400
                )
            )
            
            print("   ✅ 네트워크 그래프 생성 성공")
            
        except Exception as e:
            print(f"   ❌ 네트워크 그래프 실패: {e}")
            return False
        
        print("\n" + "=" * 40)
        print("✅ 모든 Plotly 호환성 테스트 통과!")
        return True
        
    except Exception as e:
        print(f"❌ 전체 테스트 실패: {e}")
        return False

def get_plotly_recommendations():
    """Plotly 사용 권장사항"""
    
    recommendations = """
    📋 Plotly 사용 권장사항:
    
    ✅ 권장 방식:
    layout=go.Layout(
        title=dict(
            text="제목",
            font=dict(size=16)
        )
    )
    
    ❌ 피해야 할 방식:
    layout=go.Layout(
        title="제목",
        titlefont_size=16  # 구버전 방식
    )
    
    🔧 기타 호환성 팁:
    - font 속성은 dict 형태로 사용
    - margin은 dict(b=20, l=5, r=5, t=40) 형태
    - annotations는 list of dict 형태
    - 모든 숫자 값은 명시적으로 지정
    """
    
    print(recommendations)

if __name__ == "__main__":
    success = test_plotly_compatibility()
    
    if success:
        print("\n🎉 Plotly 설정이 올바릅니다!")
        print("실제 Reddit 네트워크 분석을 실행할 수 있습니다.")
    else:
        print("\n❌ Plotly 설정에 문제가 있습니다.")
        print("🔧 해결 방법:")
        print("1. pip install --upgrade plotly")
        print("2. 코드에서 titlefont_size 제거")
        print("3. title을 dict 형태로 변경")
    
    get_plotly_recommendations()
