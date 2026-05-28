#!/usr/bin/env python3
"""
진행률 표시 수정 테스트
"""

def test_progress_calculation():
    """진행률 계산 테스트"""
    
    def safe_progress(current, total):
        """안전한 진행률 계산"""
        if total <= 0:
            progress = 0.0
        else:
            progress = current / total
        
        # 진행률을 0.0 ~ 1.0 범위로 제한
        progress = max(0.0, min(progress, 1.0))
        return progress
    
    # 테스트 케이스들
    test_cases = [
        (0, 100, 0.0),      # 시작
        (50, 100, 0.5),     # 중간
        (100, 100, 1.0),    # 완료
        (104, 100, 1.0),    # 초과 (문제가 되었던 케이스)
        (0, 0, 0.0),        # 0으로 나누기
        (-5, 100, 0.0),     # 음수
        (150, 100, 1.0),    # 큰 초과값
    ]
    
    print("=== 진행률 계산 테스트 ===")
    
    for current, total, expected in test_cases:
        result = safe_progress(current, total)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{status} current={current}, total={total} -> {result:.2f} (expected: {expected:.2f})")
    
    print("\n=== 테스트 완료 ===")

if __name__ == "__main__":
    test_progress_calculation()
