    def create_html_article(self, article_content: str, event: Dict[str, Any], chart_path: str = "") -> str:
        """HTML 기사 생성"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        symbol = event['symbol']
        
        # 차트 이미지 HTML
        chart_html = ""
        if chart_path and os.path.exists(chart_path):
            chart_filename = os.path.basename(chart_path)
            chart_html = f'''
            <div class="chart-container">
                <h3>📈 가격 차트</h3>
                <img src="../standalone_charts/{chart_filename}" alt="{symbol} 차트" style="width: 100%; max-width: 800px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            </div>
            '''
        
        html_content = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{event['title']} - 경제 뉴스</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }}
        .article-container {{
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .header {{
            border-bottom: 4px solid #007bff;
            padding-bottom: 25px;
            margin-bottom: 35px;
            background: linear-gradient(90deg, #007bff, #0056b3);
            margin: -40px -40px 35px -40px;
            padding: 25px 40px;
            border-radius: 15px 15px 0 0;
            color: white;
        }}
        .title {{
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 15px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
        .meta-info {{
            font-size: 14px;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            opacity: 0.9;
        }}
        .meta-item {{
            background: rgba(255,255,255,0.2);
            padding: 8px 12px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }}
        .price-info {{
            background: {'linear-gradient(135deg, #d4edda, #c3e6cb)' if event['change_percent'] > 0 else 'linear-gradient(135deg, #f8d7da, #f1b0b7)'};
            color: {'#155724' if event['change_percent'] > 0 else '#721c24'};
            padding: 20px;
            border-radius: 12px;
            margin: 25px 0;
            font-weight: bold;
            font-size: 18px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .severity-badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
            margin-left: 10px;
        }}
        .severity-critical {{ background: #dc3545; color: white; }}
        .severity-high {{ background: #fd7e14; color: white; }}
        .severity-medium {{ background: #ffc107; color: #212529; }}
        .severity-low {{ background: #28a745; color: white; }}
        .content {{
            font-size: 17px;
            line-height: 1.8;
            color: #333;
        }}
        .content h1 {{
            color: #007bff;
            border-bottom: 3px solid #007bff;
            padding-bottom: 12px;
            margin-top: 35px;
        }}
        .content h2 {{
            color: #0056b3;
            margin-top: 30px;
            font-size: 24px;
        }}
        .content h3 {{
            color: #495057;
            margin-top: 25px;
        }}
        .chart-container {{
            margin: 30px 0;
            text-align: center;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
        }}
        .conditions-list {{
            background: #e3f2fd;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #2196f3;
        }}
        .footer {{
            margin-top: 50px;
            padding-top: 25px;
            border-top: 2px solid #eee;
            color: #666;
            font-size: 14px;
            text-align: center;
            background: #f8f9fa;
            margin-left: -40px;
            margin-right: -40px;
            margin-bottom: -40px;
            padding-left: 40px;
            padding-right: 40px;
            padding-bottom: 25px;
            border-radius: 0 0 15px 15px;
        }}
        .highlight {{
            background: linear-gradient(120deg, #a8edea 0%, #fed6e3 100%);
            padding: 3px 6px;
            border-radius: 4px;
            font-weight: 500;
        }}
        .data-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .data-item {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #dee2e6;
        }}
        .data-value {{
            font-size: 20px;
            font-weight: bold;
            color: #007bff;
        }}
        .data-label {{
            font-size: 12px;
            color: #6c757d;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="article-container">
        <div class="header">
            <div class="title">{event['title']}</div>
            <div class="meta-info">
                <div class="meta-item">📊 종목: {symbol}</div>
                <div class="meta-item">⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
                <div class="meta-item">🤖 AI 자동 생성</div>
                <div class="meta-item">📈 실시간 데이터</div>
            </div>
        </div>
        
        <div class="price-info">
            💰 현재가: ${event['current_price']:.2f} 
            ({event['change_percent']:+.2f}% {'📈' if event['change_percent'] > 0 else '📉'})
            | 거래량: {event['volume']:,}
            <span class="severity-badge severity-{event['severity']}">{event['severity']}</span>
        </div>
        
        <div class="conditions-list">
            <strong>🔍 감지된 조건:</strong>
            <ul>
                {chr(10).join([f'<li>{condition}</li>' for condition in event.get('conditions', [])])}
            </ul>
        </div>
        
        {chart_html}
        
        <div class="content">
            {self.markdown_to_html(article_content)}
        </div>
        
        <div class="footer">
            <p><strong>🤖 이 기사는 AI가 실시간 시장 데이터를 분석하여 자동 생성했습니다.</strong></p>
            <p>📊 데이터 출처: Yahoo Finance | 생성 시간: {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')}</p>
            <p>⚠️ 이 정보는 투자 조언이 아니며, 투자 결정은 신중히 하시기 바랍니다.</p>
        </div>
    </div>
</body>
</html>'''
        
        # HTML 파일 저장
        filename = f"{symbol}_standalone_{timestamp}.html"
        filepath = os.path.join(self.output_dirs['articles'], filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"📄 HTML 기사 생성: {filepath}")
        return filepath
    
    def markdown_to_html(self, markdown_text: str) -> str:
        """마크다운을 HTML로 변환"""
        
        html = markdown_text
        
        # 헤더 변환
        html = html.replace('### ', '<h3>').replace('\n### ', '</h3>\n<h3>')
        html = html.replace('## ', '<h2>').replace('\n## ', '</h2>\n<h2>')  
        html = html.replace('# ', '<h1>').replace('\n# ', '</h1>\n<h1>')
        
        # 마지막 헤더 닫기
        if '<h1>' in html and html.count('<h1>') > html.count('</h1>'):
            html += '</h1>'
        if '<h2>' in html and html.count('<h2>') > html.count('</h2>'):
            html += '</h2>'
        if '<h3>' in html and html.count('<h3>') > html.count('</h3>'):
            html += '</h3>'
        
        # 문단 변환
        paragraphs = html.split('\n\n')
        html_paragraphs = []
        
        for p in paragraphs:
            p = p.strip()
            if p and not p.startswith('<h') and not p.startswith('*') and not p.startswith('---'):
                if p.startswith('- '):
                    # 리스트 처리
                    items = p.split('\n- ')
                    list_html = '<ul class="content-list">'
                    for item in items:
                        item = item.replace('- ', '').strip()
                        if item:
                            list_html += f'<li>{item}</li>'
                    list_html += '</ul>'
                    html_paragraphs.append(list_html)
                else:
                    html_paragraphs.append(f'<p>{p}</p>')
            elif p.startswith('*') and p.endswith('*'):
                html_paragraphs.append(f'<p class="footer-note"><em>{p[1:-1]}</em></p>')
            elif p.startswith('---'):
                html_paragraphs.append('<hr>')
            else:
                html_paragraphs.append(p)
        
        return '\n'.join(html_paragraphs)
    
    def send_enhanced_telegram_notification(self, article_filepath: str, event: Dict[str, Any], chart_path: str = "") -> bool:
        """향상된 Telegram 알림 전송"""
        
        if not hasattr(self, 'telegram_notifier') or not self.telegram_notifier:
            self.logger.warning("⚠️ Telegram notifier not configured")
            return False
        
        try:
            import asyncio
            severity_emojis = {
                'critical': '🚨',
                'high': '⚠️',
                'medium': '📊',
                'low': '📈'
            }
            emoji = severity_emojis.get(event['severity'], '📊')
            tg_message = (
                f"{emoji} <b>독립 AI 뉴스 시스템</b>\n"
                f"<b>{event['title']}</b>\n\n"
                f"{event['description']}\n\n"
                f"📊 Symbol: {event['symbol']} | Change: {event['change_percent']:+.2f}%\n"
                f"💰 Price: ${event['current_price']:.2f} | Volume: {event['volume']:,}\n"
                f"⚠️ Severity: {event['severity'].upper()} | Conditions: {len(event.get('conditions', []))}\n"
                f"📄 HTML: {os.path.basename(article_filepath)}"
            )
            asyncio.run(self.telegram_notifier._send_telegram(tg_message))
            self.logger.info("✅ Telegram 알림 전송 성공")
            return True
                
        except Exception as e:
            self.logger.error(f"❌ Telegram 알림 전송 오류: {e}")
            return False
    
    def run_complete_system(self) -> Dict[str, Any]:
        """전체 시스템 실행"""
        
        start_time = datetime.now()
        self.logger.info("🚀 독립적인 뉴스 시스템 시작")
        
        try:
            # 1. 시장 데이터 수집
            self.logger.info("📊 1단계: 시장 데이터 수집")
            market_data = self.collect_market_data()
            
            if not market_data['symbols']:
                raise Exception("시장 데이터 수집 실패")
            
            # 2. 이벤트 감지
            self.logger.info("🚨 2단계: 중요 이벤트 감지")
            events = self.detect_significant_events(market_data)
            
            if not events:
                raise Exception("감지된 이벤트 없음")
            
            # 3. 기사 생성 및 처리
            self.logger.info("✍️ 3단계: 종합 기사 생성")
            results = []
            
            for event in events[:3]:  # 최대 3개 이벤트 처리
                self.logger.info(f"📝 {event['symbol']} 처리 중...")
                
                # 차트 생성
                chart_path = self.create_price_chart(event['symbol'], market_data['symbols'][event['symbol']])
                
                # AI 기사 생성
                article_content = self.generate_comprehensive_article(event, market_data)
                
                # HTML 파일 생성
                html_filepath = self.create_html_article(article_content, event, chart_path)
                
                # Telegram 알림 전송
                telegram_success = self.send_enhanced_telegram_notification(html_filepath, event, chart_path)
                
                results.append({
                    'event': event,
                    'article_content': article_content,
                    'html_file': html_filepath,
                    'chart_file': chart_path,
                    'telegram_sent': telegram_success
                })
                
                self.logger.info(f"✅ {event['symbol']} 처리 완료")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'status': 'success',
                'execution_time': execution_time,
                'events_processed': len(results),
                'articles_generated': len(results),
                'charts_generated': sum(1 for r in results if r['chart_file']),
                'telegram_notifications': sum(1 for r in results if r['telegram_sent']),
                'results': results,
                'market_summary': market_data.get('market_summary', {}),
                'timestamp': datetime.now().isoformat()
            }
            
            # 결과 저장
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            result_file = os.path.join(self.output_dirs['data'], f'execution_result_{timestamp}.json')
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2, default=str)
            
            self.logger.info(f"🎉 독립 시스템 실행 완료 ({execution_time:.1f}초)")
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"❌ 시스템 실행 실패: {e}")
            
            return {
                'status': 'error',
                'error': str(e),
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            }

def main():
    """메인 함수"""
    
    print("🚀 완전히 독립적인 경제 뉴스 생성 시스템")
    print("=" * 70)
    print("✅ OrchestratorStrand 의존성 없음")
    print("✅ 안정적인 독립 실행")
    print("✅ AI 기사 생성 + 차트 + Telegram 알림")
    print("=" * 70)
    
    # 시스템 초기화
    system = StandaloneNewsSystem()
    
    # 전체 시스템 실행
    result = system.run_complete_system()
    
    # 결과 출력
    print("\n📊 실행 결과:")
    print(f"상태: {result.get('status', 'unknown')}")
    print(f"실행 시간: {result.get('execution_time', 0):.1f}초")
    print(f"처리된 이벤트: {result.get('events_processed', 0)}개")
    print(f"생성된 기사: {result.get('articles_generated', 0)}개")
    print(f"생성된 차트: {result.get('charts_generated', 0)}개")
    print(f"Telegram 알림: {result.get('telegram_notifications', 0)}개")
    
    if result.get('status') == 'success':
        print("\n🎉 독립 시스템 실행 완료!")
        
        # 시장 요약
        market_summary = result.get('market_summary', {})
        if market_summary:
            print(f"\n📈 시장 요약:")
            print(f"  전체 종목: {market_summary.get('total_symbols', 0)}개")
            print(f"  평균 변동률: {market_summary.get('avg_change', 0):+.2f}%")
            print(f"  상승 종목: {market_summary.get('positive_count', 0)}개")
            print(f"  하락 종목: {market_summary.get('negative_count', 0)}개")
        
        # 생성된 파일 목록
        results = result.get('results', [])
        if results:
            print("\n💡 생성된 파일:")
            for i, res in enumerate(results):
                event = res.get('event', {})
                html_file = res.get('html_file', '')
                chart_file = res.get('chart_file', '')
                
                print(f"  {i+1}. {event.get('symbol', 'Unknown')} ({event.get('severity', 'unknown')})")
                if html_file:
                    print(f"     📄 HTML: {html_file}")
                if chart_file:
                    print(f"     📈 차트: {chart_file}")
                print(f"     📱 Telegram: {'✅' if res.get('telegram_sent') else '❌'}")
        
        print("\n🌐 HTML 기사 보기:")
        if results and results[0].get('html_file'):
            latest_html = results[0]['html_file']
            print(f"  open {latest_html}")
        
        print("\n📱 Telegram 알림을 확인하세요!")
    else:
        print(f"\n❌ 실행 실패: {result.get('error', 'Unknown error')}")
        print("\n🔧 문제 해결:")
        print("  • AWS 자격 증명: aws sts get-caller-identity")
        print("  • TELEGRAM_BOT_TOKEN 및 TELEGRAM_CHAT_ID 확인")
        print("  • 인터넷 연결 확인")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
