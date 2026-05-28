#!/usr/bin/env python3
"""
차트 생성 오류 수정 스크립트
'Date' 키 오류를 해결하고 향상된 차트 생성 함수로 교체
"""

import os
import re

def fix_chart_function():
    """차트 생성 함수 수정"""
    
    print("🔧 차트 생성 함수 수정 중...")
    
    # 기존 파일 읽기
    with open('complete_standalone_system.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 기존 create_price_chart 함수 찾기 및 교체
    old_function_pattern = r'def create_price_chart\(self, symbol: str, data: Dict\[str, Any\]\) -> str:.*?(?=def |\Z)'
    
    new_function = '''def create_enhanced_price_chart(self, symbol: str, data: Dict[str, Any]) -> str:
        """향상된 가격 차트 생성 (오류 수정)"""
        
        try:
            chart_data = data.get('chart_data', [])
            if not chart_data or len(chart_data) < 2:
                self.logger.warning(f"⚠️ {symbol} 차트 데이터 부족")
                return ""
            
            # 데이터 준비 (수정된 부분)
            dates = []
            prices = []
            volumes = []
            highs = []
            lows = []
            
            for item in chart_data:
                try:
                    # 날짜 처리 - pandas DataFrame의 인덱스를 올바르게 처리
                    if 'timestamp' in item and item['timestamp']:
                        date = item['timestamp']
                        if isinstance(date, str):
                            date = datetime.fromisoformat(date.replace('Z', '+00:00'))
                    elif 'date' in item:
                        date = datetime.strptime(item['date'], '%Y-%m-%d')
                    else:
                        continue  # 날짜 정보가 없으면 스킵
                    
                    dates.append(date)
                    prices.append(float(item.get('close', item.get('Close', 0))))
                    volumes.append(int(item.get('volume', item.get('Volume', 0))))
                    highs.append(float(item.get('high', item.get('High', item.get('close', item.get('Close', 0))))))
                    lows.append(float(item.get('low', item.get('Low', item.get('close', item.get('Close', 0))))))
                    
                except (ValueError, KeyError, TypeError) as e:
                    self.logger.warning(f"⚠️ {symbol} 데이터 파싱 오류: {e}")
                    continue
            
            if len(dates) < 2:
                self.logger.warning(f"⚠️ {symbol} 유효한 데이터 부족")
                return ""
            
            # 차트 생성
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[3, 1])
            
            # 가격 차트
            ax1.plot(dates, prices, linewidth=2, color='#1f77b4', label='Close Price')
            ax1.fill_between(dates, prices, alpha=0.3, color='#1f77b4')
            ax1.set_title(f'{symbol} - 가격 추이 (최근 {len(dates)}일)', fontsize=16, fontweight='bold')
            ax1.set_ylabel('가격 ($)', fontsize=12)
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            
            # 현재가 표시
            current_price = data['current_price']
            change_percent = data['change_percent']
            color = 'green' if change_percent > 0 else 'red'
            ax1.axhline(y=current_price, color=color, linestyle='--', alpha=0.7)
            ax1.text(dates[-1], current_price, f'${current_price:.2f} ({change_percent:+.2f}%)', 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.7, edgecolor='none'),
                    color='white', fontweight='bold')
            
            # 거래량 차트
            ax2.bar(dates, volumes, alpha=0.7, color='orange')
            ax2.set_title('거래량', fontsize=12)
            ax2.set_ylabel('거래량', fontsize=10)
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # 파일 저장
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{symbol}_fixed_chart_{timestamp}.png"
            filepath = os.path.join(self.output_dirs['charts'], filename)
            
            plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            self.logger.info(f"📈 수정된 차트 생성 성공: {filename}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"❌ {symbol} 차트 생성 실패: {e}")
            import traceback
            self.logger.error(f"상세 오류: {traceback.format_exc()}")
            return ""
    
    '''
    
    # 함수 교체
    content = re.sub(old_function_pattern, new_function, content, flags=re.DOTALL)
    
    # collect_market_data 함수에서 historical_data를 chart_data로 수정
    content = content.replace(
        "'historical_data': hist.tail(10).to_dict('records')",
        """'chart_data': [
                            {
                                'date': date.strftime('%Y-%m-%d'),
                                'timestamp': date,
                                'open': float(row['Open']),
                                'high': float(row['High']),
                                'low': float(row['Low']),
                                'close': float(row['Close']),
                                'volume': int(row['Volume']) if 'Volume' in row and not pd.isna(row['Volume']) else 0
                            }
                            for date, row in hist.tail(20).iterrows()
                        ]"""
    )
    
    # 차트 생성 호출 부분 수정
    content = content.replace(
        "chart_path = self.create_price_chart(event['symbol'], market_data['symbols'][event['symbol']])",
        "chart_path = self.create_enhanced_price_chart(event['symbol'], market_data['symbols'][event['symbol']])"
    )
    
    # 거래량 계산 부분 수정
    content = content.replace(
        "avg_volume = np.mean([d.get('Volume', 0) for d in data.get('historical_data', [])])",
        "avg_volume = np.mean([d.get('volume', 0) for d in data.get('chart_data', [])])"
    )
    
    # 수정된 내용 저장
    with open('complete_standalone_system_fixed.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 차트 생성 함수 수정 완료")
    print("📄 수정된 파일: complete_standalone_system_fixed.py")
    
    return True

def main():
    """메인 함수"""
    
    print("🔧 차트 생성 오류 수정 도구")
    print("=" * 50)
    
    if not os.path.exists('complete_standalone_system.py'):
        print("❌ complete_standalone_system.py 파일을 찾을 수 없습니다.")
        return
    
    if fix_chart_function():
        print("\n✅ 차트 생성 오류 수정 완료!")
        print("\n💡 수정된 시스템 실행:")
        print("  python complete_standalone_system_fixed.py")
        print("\n🔧 수정 사항:")
        print("  • 'Date' 키 오류 해결")
        print("  • pandas DataFrame 인덱스 올바른 처리")
        print("  • 차트 데이터 구조 개선")
        print("  • 오류 처리 강화")
        print("  • 상세한 로깅 추가")
    else:
        print("\n❌ 수정 실패")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
