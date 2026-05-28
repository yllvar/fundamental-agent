#!/usr/bin/env python3
"""
orchestrator_agent.py 문법 오류 완전 수정
"""

def fix_orchestrator_agent():
    """orchestrator_agent.py의 문법 오류 수정"""
    
    try:
        # 파일 읽기
        with open('agents/orchestrator_agent.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 문제가 되는 _generate_streamlit_page_content 메서드를 간단한 버전으로 교체
        new_method = '''    def _generate_streamlit_page_content(self, package: ArticlePackage) -> str:
        """Streamlit 페이지 콘텐츠 생성 (수정된 버전)"""
        
        article = package.article
        event = package.event
        
        # 간단하고 안전한 Streamlit 페이지 생성
        content_template = """#!/usr/bin/env python3
import streamlit as st
import streamlit.components.v1 as components
import os
from datetime import datetime

st.set_page_config(page_title="{title}", page_icon="📈", layout="wide")

def main():
    st.title("📈 {title}")
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Symbol", "{symbol}")
    with col2:
        st.metric("Change", "{change_percent:+.2f}%")
    with col3:
        st.metric("Severity", "{severity}")
    with col4:
        st.metric("Time", "{time}")
    
    st.markdown("## 📰 Article Content")
    st.markdown('''{content}''')
    
    st.markdown("## 📊 Related Charts")
    st.info("Charts are available as HTML files. Please check the output/charts directory.")
    
    st.markdown("## 🔍 Review Results")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Quality Score", "{quality_score:.1f}/10")
    with col2:
        st.metric("Overall Score", "{overall_score:.1f}/10")
    
    st.markdown("## 📢 Related Services")
    st.info("Personalized service recommendations will be displayed here.")
    
    st.markdown("---")
    st.markdown("**Generated Time:** " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    st.markdown("**System:** Fundamental Agent System")

if __name__ == "__main__":
    main()
"""
        
        # 안전한 문자열 포맷팅
        formatted_content = content_template.format(
            title=event.title.replace('"', '\\"'),
            symbol=event.symbol,
            change_percent=event.change_percent,
            severity=event.severity.value.upper(),
            time=event.timestamp.strftime('%H:%M'),
            content=article.get('content', 'Content not available').replace('"', '\\"')[:500] + "...",
            quality_score=package.review_result.get('quality_score', 0),
            overall_score=package.review_result.get('overall_score', 0)
        )
        
        return formatted_content'''
        
        # 기존 메서드를 찾아서 교체
        import re
        
        # _generate_streamlit_page_content 메서드 전체를 교체
        pattern = r'def _generate_streamlit_page_content\(self, package: ArticlePackage\) -> str:.*?return content'
        
        content = re.sub(pattern, new_method, content, flags=re.DOTALL)
        
        # 파일 저장
        with open('agents/orchestrator_agent.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ orchestrator_agent.py 문법 오류 수정 완료")
        return True
        
    except Exception as e:
        print(f"❌ 수정 실패: {e}")
        return False

def test_syntax():
    """Python 문법 검사"""
    
    try:
        import subprocess
        import sys
        
        result = subprocess.run([sys.executable, '-m', 'py_compile', 'agents/orchestrator_agent.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 문법 검사 통과")
            return True
        else:
            print(f"❌ 문법 오류: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 문법 검사 실패: {e}")
        return False

if __name__ == "__main__":
    print("🔧 orchestrator_agent.py 문법 오류 완전 수정")
    print("=" * 50)
    
    success = fix_orchestrator_agent()
    
    if success:
        syntax_ok = test_syntax()
        if syntax_ok:
            print("🎉 모든 문법 오류 수정 완료!")
        else:
            print("⚠️ 추가 문법 오류가 있을 수 있습니다.")
    else:
        print("❌ 수정에 실패했습니다.")
