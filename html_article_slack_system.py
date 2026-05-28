#!/usr/bin/env python3
"""
HTML Article Generation and Telegram Delivery System
Alternative system that operates when the AI agent fails
"""

import os
import json
import logging
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI
import requests

from notifications.telegram_notifier import TelegramNotifier

DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# .env 파일 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HTMLArticleTelegramSystem:
    """HTML Article Generation and Telegram Delivery System"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 출력 디렉토리 설정
        self.output_dirs = {
            'articles': 'output/html_articles',
            'data': 'output/market_data'
        }
        
        for dir_path in self.output_dirs.values():
            os.makedirs(dir_path, exist_ok=True)
        
        # DeepSeek API 클라이언트 초기화
        self.deepseek_client = None
        api_key = os.environ.get('DEEPSEEK_API_KEY')
        if api_key:
            try:
                self.deepseek_client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)
                self.logger.info("✅ DeepSeek initialized")
            except Exception as e:
                self.logger.error(f"❌ DeepSeek initialization failed: {e}")
        else:
            self.logger.warning("⚠️ DEEPSEEK_API_KEY not set")
        self.llm = self.deepseek_client  # 호환성을 위해 llm 속성 유지
        
        # Telegram 설정
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.telegram_notifier = TelegramNotifier(self.telegram_bot_token, self.telegram_chat_id) if self.telegram_bot_token and self.telegram_chat_id else None
        if self.telegram_notifier:
            self.logger.info("✅ Telegram notifier configured")
        else:
            self.logger.warning("⚠️ Telegram notifier not configured")
    
    def collect_market_data(self, symbols: List[str] = None) -> Dict[str, Any]:
        """Collect market data"""
        
        if symbols is None:
            symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', '^GSPC', '^IXIC', '^VIX']
        
        market_data = {
            'timestamp': datetime.now().isoformat(),
            'symbols': {}
        }
        
        self.logger.info(f"📊 Collecting data for {len(symbols)} symbols...")
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="5d")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    previous_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                    change_percent = ((current_price - previous_price) / previous_price) * 100
                    
                    market_data['symbols'][symbol] = {
                        'name': info.get('longName', symbol),
                        'current_price': float(current_price),
                        'previous_price': float(previous_price),
                        'change_percent': float(change_percent),
                        'volume': int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0,
                        'high_52w': info.get('fiftyTwoWeekHigh', 0),
                        'low_52w': info.get('fiftyTwoWeekLow', 0),
                        'market_cap': info.get('marketCap', 0)
                    }
                    
                    self.logger.info(f"✅ {symbol}: {change_percent:+.2f}%")
                
            except Exception as e:
                self.logger.error(f"❌ {symbol} data collection failed: {e}")
                continue
        
        # 데이터 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        data_file = os.path.join(self.output_dirs['data'], f'market_data_{timestamp}.json')
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(market_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"💾 Market data saved: {data_file}")
        return market_data
    
    def detect_events(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect events"""
        
        events = []
        
        for symbol, data in market_data['symbols'].items():
            change_percent = data['change_percent']
            
            # 이벤트 감지 조건
            if abs(change_percent) >= 3.0:  # 3% 이상 변동
                severity = 'high' if abs(change_percent) >= 5.0 else 'medium'
                direction = 'rise' if change_percent > 0 else 'fall'
                
                event = {
                    'symbol': symbol,
                    'name': data['name'],
                    'event_type': 'price_change',
                    'severity': severity,
                    'title': f"{symbol} stock price {abs(change_percent):.1f}% {direction}",
                    'description': f"{data['name']} {change_percent:+.2f}% {direction}.",
                    'current_price': data['current_price'],
                    'change_percent': change_percent,
                    'volume': data['volume'],
                    'timestamp': datetime.now().isoformat()
                }
                events.append(event)
        
        # 이벤트가 없으면 가장 큰 변동 종목으로 이벤트 생성
        if not events and market_data['symbols']:
            max_change_symbol = max(
                market_data['symbols'].items(),
                key=lambda x: abs(x[1]['change_percent'])
            )
            
            symbol, data = max_change_symbol
            change_percent = data['change_percent']
            direction = 'rise' if change_percent > 0 else 'fall'
            
            event = {
                'symbol': symbol,
                'name': data['name'],
                'event_type': 'market_update',
                'severity': 'low',
                'title': f"{symbol} Market Update",
                'description': f"{data['name']} {change_percent:+.2f}% {direction}.",
                'current_price': data['current_price'],
                'change_percent': change_percent,
                'volume': data['volume'],
                'timestamp': datetime.now().isoformat()
            }
            events.append(event)
        
        self.logger.info(f"🚨 {len(events)} event(s) detected")
        return events
    
    def generate_article_with_ai(self, event: Dict[str, Any], market_data: Dict[str, Any]) -> str:
        """Generate article using AI"""
        
        if not self.deepseek_client:
            return self.generate_article_template(event, market_data)

        try:
            system_prompt = """You are a professional economic journalist. Write a professional and objective economic article in English based on the given market data and events.

Article Writing Guidelines:
1. Headlines should be concise and impactful
2. Summarize key points in the lead paragraph
3. Data-driven objective analysis
4. Include market outlook and investment implications
5. Use professional yet easy-to-understand language

Article Structure:
- Headline
- Lead (key summary)
- Body (detailed analysis)
- Conclusion (market outlook)"""

            user_prompt = f"""Please write an economic article based on the following event and market data:

Event Information:
- Symbol: {event['symbol']} ({event['name']})
- Change: {event['change_percent']:+.2f}%
- Current Price: ${event['current_price']:.2f}
- Volume: {event['volume']:,}

Overall Market Situation:
"""

            # Add major symbols data
            for symbol, data in list(market_data['symbols'].items())[:5]:
                user_prompt += f"- {symbol}: {data['change_percent']:+.2f}%\n"

            user_prompt += f"\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

            response = self.deepseek_client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            return response.choices[0].message.content or ""

        except Exception as e:
            self.logger.error(f"❌ AI article generation failed: {e}")
            return self.generate_article_template(event, market_data)
    
    def generate_article_template(self, event: Dict[str, Any], market_data: Dict[str, Any]) -> str:
        """Generate article from template (fallback when AI fails)"""
        
        symbol = event['symbol']
        name = event['name']
        change_percent = event['change_percent']
        current_price = event['current_price']
        direction = 'rise' if change_percent > 0 else 'fall'
        
        article = f"""# {symbol} stock price {abs(change_percent):.1f}% {direction}, Market in Focus

## Key Summary
{name} recorded {change_percent:+.2f}% {direction} to ${current_price:.2f} in trading on {datetime.now().strftime('%Y-%m-%d')}.

## Detailed Analysis
Today, {name}({symbol}) closed at ${current_price:.2f}, {change_percent:+.2f}% {direction} from the previous day. This is interpreted as"""
        
        if abs(change_percent) >= 3:
            article += "a move showing significant volatility."
        else:
            article += "a move showing a stable trend."
        
        article += f"""

Trading volume was {event['volume']:,} shares, suggesting heightened investor interest.

## Market Outlook
"""
        
        if change_percent > 0:
            article += f"The upward trend in {name} appears to reflect positive market sentiment. "
        else:
            article += f"The downward trend in {name} is interpreted as part of a market correction. "
        
        article += "Investors should closely monitor future market trends."
        
        # Add other key symbols trends
        article += "\n\n## Key Market Trends\n"
        for sym, data in list(market_data['symbols'].items())[:5]:
            if sym != symbol:
                article += f"- {sym}: {data['change_percent']:+.2f}%\n"
        
        article += f"\n*Article generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*"
        
        return article
    
    def create_html_article(self, article_content: str, event: Dict[str, Any]) -> str:
        """Create HTML article"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        symbol = event['symbol']
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{event['title']} - Fundamental Agent</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .article-container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            border-bottom: 3px solid #007bff;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .title {{
            color: #333;
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .meta-info {{
            color: #666;
            font-size: 14px;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }}
        .meta-item {{
            background: #f8f9fa;
            padding: 5px 10px;
            border-radius: 5px;
        }}
        .price-info {{
            background: {'#d4edda' if event['change_percent'] > 0 else '#f8d7da'};
            color: {'#155724' if event['change_percent'] > 0 else '#721c24'};
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            font-weight: bold;
        }}
        .content {{
            font-size: 16px;
            line-height: 1.8;
            color: #333;
        }}
        .content h1 {{
            color: #007bff;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }}
        .content h2 {{
            color: #0056b3;
            margin-top: 30px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 14px;
            text-align: center;
        }}
        .highlight {{
            background: #fff3cd;
            padding: 2px 4px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div class="article-container">
        <div class="header">
            <div class="title">{event['title']}</div>
            <div class="meta-info">
                <div class="meta-item">📊 Symbol: {symbol}</div>
                <div class="meta-item">⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
                <div class="meta-item">🤖 AI Auto-generated</div>
            </div>
        </div>
        
        <div class="price-info">
            💰 Current Price: ${event['current_price']:.2f} 
            ({event['change_percent']:+.2f}% {'📈' if event['change_percent'] > 0 else '📉'})
            | Volume: {event['volume']:,}
        </div>
        
        <div class="content">
            {self.markdown_to_html(article_content)}
        </div>
        
        <div class="footer">
            <p>🤖 This article was automatically generated by AI analyzing real-time market data.</p>
            <p>📊 Data source: Yahoo Finance | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
    </div>
</body>
</html>"""
        
        # HTML 파일 저장
        filename = f"{symbol}_article_{timestamp}.html"
        filepath = os.path.join(self.output_dirs['articles'], filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"📄 HTML article created: {filepath}")
        return filepath
    
    def markdown_to_html(self, markdown_text: str) -> str:
        """Convert simple markdown to HTML"""
        
        html = markdown_text
        
        # 헤더 변환
        html = html.replace('# ', '<h1>').replace('\n# ', '</h1>\n<h1>')
        html = html.replace('## ', '<h2>').replace('\n## ', '</h2>\n<h2>')
        
        # 마지막 헤더 닫기
        if '<h1>' in html and '</h1>' not in html.split('<h1>')[-1]:
            html += '</h1>'
        if '<h2>' in html and '</h2>' not in html.split('<h2>')[-1]:
            html += '</h2>'
        
        # 문단 변환
        paragraphs = html.split('\n\n')
        html_paragraphs = []
        
        for p in paragraphs:
            p = p.strip()
            if p and not p.startswith('<h') and not p.startswith('*'):
                if p.startswith('- '):
                    # 리스트 처리
                    items = p.split('\n- ')
                    list_html = '<ul>'
                    for item in items:
                        item = item.replace('- ', '')
                        if item:
                            list_html += f'<li>{item}</li>'
                    list_html += '</ul>'
                    html_paragraphs.append(list_html)
                else:
                    html_paragraphs.append(f'<p>{p}</p>')
            elif p.startswith('*') and p.endswith('*'):
                html_paragraphs.append(f'<p><em>{p[1:-1]}</em></p>')
            else:
                html_paragraphs.append(p)
        
        return '\n'.join(html_paragraphs)
    
    def send_telegram_notification(self, article_filepath: str, event: Dict[str, Any]) -> bool:
        """Send article notification via Telegram"""
        
        try:
            # Read article file
            with open(article_filepath, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Extract summary (first paragraph)
            summary = event['description']
            if len(summary) > 200:
                summary = summary[:200] + "..."
            
            # Telegram 전송
            if self.telegram_notifier:
                try:
                    import asyncio
                    tg_message = f"📰 <b>AI Economic Article Generated</b>\n<b>{event['title']}</b>\n\n{summary}\n\n📊 Symbol: {event['symbol']} | Change: {event['change_percent']:+.2f}% | Price: ${event['current_price']:.2f}"
                    asyncio.run(self.telegram_notifier._send_telegram(tg_message))
                    self.logger.info("✅ Telegram notification sent successfully")
                    return True
                except Exception as e:
                    self.logger.error(f"❌ Telegram notification error: {e}")
            
            return False
                
        except Exception as e:
            self.logger.error(f"❌ Notification error: {e}")
            return False
    
    def run_complete_system(self) -> Dict[str, Any]:
        """Run complete system"""
        
        start_time = datetime.now()
        self.logger.info("🚀 HTML Article Generation System started")
        
        try:
            # 1. Collect market data
            self.logger.info("📊 Step 1: Collecting market data")
            market_data = self.collect_market_data()
            
            if not market_data['symbols']:
                raise Exception("Market data collection failed")
            
            # 2. Detect events
            self.logger.info("🚨 Step 2: Detecting events")
            events = self.detect_events(market_data)
            
            if not events:
                raise Exception("No events detected")
            
            # 3. Generate articles and convert to HTML
            self.logger.info("✍️ Step 3: Generating articles")
            results = []
            
            for event in events[:2]:  # 최대 2개 이벤트 처리
                self.logger.info(f"📝 Generating article for {event['symbol']}...")
                
                # AI 기사 생성
                article_content = self.generate_article_with_ai(event, market_data)
                
                # HTML 파일 생성
                html_filepath = self.create_html_article(article_content, event)
                
                # Telegram 알림 전송
                telegram_success = self.send_telegram_notification(html_filepath, event)
                
                results.append({
                    'event': event,
                    'article_content': article_content,
                    'html_file': html_filepath,
                    'telegram_sent': telegram_success
                })
                
                self.logger.info(f"✅ {event['symbol']} processed")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'status': 'success',
                'execution_time': execution_time,
                'events_processed': len(results),
                'articles_generated': len(results),
                'telegram_notifications': sum(1 for r in results if r['telegram_sent']),
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"🎉 System execution complete ({execution_time:.1f}s)")
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"❌ System execution failed: {e}")
            
            return {
                'status': 'error',
                'error': str(e),
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            }

def main():
    """Main function"""
    
    print("🚀 HTML Article Generation and Telegram Delivery System")
    print("=" * 60)
    
    # 시스템 초기화
    system = HTMLArticleTelegramSystem()
    
    # 전체 시스템 실행
    result = system.run_complete_system()
    
    # Print results
    print("\n📊 Execution Results:")
    print(f"Status: {result.get('status', 'unknown')}")
    print(f"Execution time: {result.get('execution_time', 0):.1f}s")
    print(f"Events processed: {result.get('events_processed', 0)}")
    print(f"Articles generated: {result.get('articles_generated', 0)}")
    print(f"Telegram notifications: {result.get('telegram_notifications', 0)}")
    
    if result.get('status') == 'success':
        print("\n🎉 HTML article generation and Telegram delivery complete!")
        
        # 생성된 파일 목록
        results = result.get('results', [])
        if results:
            print("\n💡 Generated HTML articles:")
            for i, res in enumerate(results):
                html_file = res.get('html_file', '')
                if html_file:
                    print(f"  {i+1}. {html_file}")
                    print(f"     Open in browser: open {html_file}")
        
        print("\n📱 Check notifications in your Telegram!")
    else:
        print(f"\n❌ Execution failed: {result.get('error', 'Unknown error')}")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
