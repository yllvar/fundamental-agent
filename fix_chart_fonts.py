#!/usr/bin/env python3
"""
차트 폰트 문제 해결
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

def fix_matplotlib_fonts():
    """matplotlib 폰트 설정 수정"""
    
    print("🔧 matplotlib 폰트 설정 수정 중...")
    
    try:
        # 기본 폰트를 영어 폰트로 설정
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Liberation Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 한글 폰트 사용 안함
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['xtick.labelsize'] = 10
        plt.rcParams['ytick.labelsize'] = 10
        plt.rcParams['legend.fontsize'] = 10
        
        print("✅ matplotlib 폰트 설정 완료")
        
        # 테스트 차트 생성
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
        ax.set_title('Test Chart - English Font')
        ax.set_xlabel('Time Period')
        ax.set_ylabel('Price Value')
        
        # 테스트 이미지 저장
        test_path = 'output/test_font_chart.png'
        os.makedirs('output', exist_ok=True)
        plt.savefig(test_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ 테스트 차트 생성: {test_path}")
        return True
        
    except Exception as e:
        print(f"❌ 폰트 설정 실패: {e}")
        return False

def update_data_analysis_agent():
    """data_analysis_agent.py의 차트 생성 부분 수정"""
    
    print("🔧 data_analysis_agent.py 차트 생성 부분 수정...")
    
    try:
        # 파일 읽기
        with open('agents/data_analysis_agent.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # matplotlib 설정 추가
        matplotlib_setup = '''
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # GUI 백엔드 사용 안함
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Liberation Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12
'''
        
        # import 부분 뒤에 matplotlib 설정 추가
        if 'matplotlib.use(' not in content:
            import_end = content.find('class DataAnalysisAgent:')
            if import_end != -1:
                content = content[:import_end] + matplotlib_setup + '\n' + content[import_end:]
        
        # 파일 저장
        with open('agents/data_analysis_agent.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ data_analysis_agent.py 수정 완료")
        return True
        
    except Exception as e:
        print(f"❌ data_analysis_agent.py 수정 실패: {e}")
        return False

if __name__ == "__main__":
    print("🚀 차트 폰트 문제 해결 시작")
    print("=" * 50)
    
    success1 = fix_matplotlib_fonts()
    success2 = update_data_analysis_agent()
    
    if success1 and success2:
        print("\n🎉 차트 폰트 문제 해결 완료!")
        print("📊 이제 모든 차트가 영어로 표시됩니다.")
    else:
        print("\n❌ 일부 수정에 실패했습니다.")
