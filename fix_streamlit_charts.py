#!/usr/bin/env python3
"""
Streamlit 페이지의 차트 표시 오류 수정
"""

import os
import glob

def fix_streamlit_chart_display():
    """Streamlit 페이지의 차트 표시 방식 수정"""
    
    # streamlit_articles 디렉토리의 모든 파일 찾기
    article_files = glob.glob("streamlit_articles/article_*.py")
    
    for file_path in article_files:
        print(f"수정 중: {file_path}")
        
        try:
            # 파일 읽기
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 잘못된 차트 표시 코드 찾기 및 수정
            old_chart_code = """    # 차트 표시 (실제로는 저장된 차트 이미지 로드)
    for i, chart_path in enumerate(['output/charts/^VIX_price_volume_20250806_081838.html', 'output/charts/^VIX_technical_20250806_081838.html', 'output/charts/^VIX_recent_20250806_081838.html', 'output/charts/^VIX_comparison_20250806_081838.html']):
        if os.path.exists(chart_path):
            st.image(chart_path, caption=f"차트 {i+1}")"""
            
            # 새로운 차트 표시 코드
            new_chart_code = """    # 차트 표시 (HTML 파일을 올바르게 표시)
    chart_paths = [path for path in ['output/charts/^VIX_price_volume_20250806_081838.html', 'output/charts/^VIX_technical_20250806_081838.html', 'output/charts/^VIX_recent_20250806_081838.html', 'output/charts/^VIX_comparison_20250806_081838.html'] if os.path.exists(path)]
    
    if chart_paths:
        for i, chart_path in enumerate(chart_paths):
            st.markdown(f"### 📊 Chart {i+1}")
            try:
                # HTML 파일 읽기 및 표시
                with open(chart_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                st.components.v1.html(html_content, height=600)
            except Exception as e:
                st.error(f"Chart loading error: {e}")
                st.markdown(f"Chart file: `{chart_path}`")
    else:
        st.info("No charts available for this article.")"""
            
            # 일반적인 패턴으로 수정
            if "st.image(chart_path" in content:
                # 더 일반적인 패턴 매칭
                import re
                
                # 차트 표시 부분을 찾아서 수정
                pattern = r'# 차트 표시.*?st\.image\(chart_path.*?\)'
                
                replacement = """# 차트 표시 (HTML 파일을 올바르게 표시)
    if 'charts' in locals() and charts:
        for i, chart_path in enumerate(charts):
            if os.path.exists(chart_path):
                st.markdown(f"### 📊 Chart {i+1}")
                try:
                    if chart_path.endswith('.html'):
                        # HTML 파일 읽기 및 표시
                        with open(chart_path, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        st.components.v1.html(html_content, height=600)
                    else:
                        # 이미지 파일 표시
                        st.image(chart_path, caption=f"Chart {i+1}")
                except Exception as e:
                    st.error(f"Chart loading error: {e}")
                    st.markdown(f"Chart file: `{chart_path}`")
    else:
        st.info("No charts available for this article.")"""
                
                content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            
            # 파일 쓰기
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"✅ 수정 완료: {file_path}")
            
        except Exception as e:
            print(f"❌ 수정 실패: {file_path} - {e}")

if __name__ == "__main__":
    fix_streamlit_chart_display()
    print("🎉 모든 Streamlit 페이지 수정 완료!")
