#!/usr/bin/env python3
"""
orchestrator_agent.py 문법 오류 수정
"""

import re

def fix_orchestrator_syntax():
    """orchestrator_agent.py의 문법 오류 수정"""
    
    try:
        # 파일 읽기
        with open('agents/orchestrator_agent.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # f-string 내부의 triple quote 문제 수정
        # _generate_streamlit_page_content 메서드를 찾아서 수정
        
        # 문제가 되는 부분을 찾아서 간단한 버전으로 교체
        pattern = r'def _generate_streamlit_page_content\(self, package: ArticlePackage\) -> str:.*?return content'
        
        replacement = '''def _generate_streamlit_page_content(self, package: ArticlePackage) -> str:
        """Streamlit 페이지 콘텐츠 생성"""
        
        article = package.article
        event = package.event
        
        # 간단한 Streamlit 페이지 생성
        content = f"""#!/usr/bin/env python3
import streamlit as st
import os
from datetime import datetime

st.set_page_config(page_title="{event.title}", page_icon="📈", layout="wide")

def main():
    st.title("📈 {event.title}")
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Symbol", "{event.symbol}")
    with col2:
        st.metric("Change", "{event.change_percent:+.2f}%")
    with col3:
        st.metric("Severity", "{event.severity.value.upper()}")
    with col4:
        st.metric("Time", "{event.timestamp.strftime('%H:%M')}")
    
    st.markdown("## 📰 Article Content")
    st.markdown('''{article.get('content', 'Content not available')}''')
    
    st.markdown("## 📊 Charts")
    st.info("Charts are available as HTML files in the output/charts directory")
    
    st.markdown("## 🔍 Review Results")
    review = {package.review_result}
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Quality Score", f"{{review.get('quality_score', 0):.1f}}/10")
    with col2:
        st.metric("Overall Score", f"{{review.get('overall_score', 0):.1f}}/10")

if __name__ == "__main__":
    main()
"""
        
        return content'''
        
        # 정규식으로 교체
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        # 파일 쓰기
        with open('agents/orchestrator_agent.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ orchestrator_agent.py 문법 오류 수정 완료")
        return True
        
    except Exception as e:
        print(f"❌ 수정 실패: {e}")
        return False

if __name__ == "__main__":
    fix_orchestrator_syntax()
