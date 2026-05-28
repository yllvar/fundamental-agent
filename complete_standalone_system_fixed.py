#!/usr/bin/env python3
"""
Fully standalone Fundamental Agent system
A stable system operating without OrchestratorStrand dependency
"""

import os
import sys
import json
import requests
import logging
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI

from notifications.telegram_notifier import TelegramNotifier

DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# matplotlib settings
matplotlib.use('Agg')
plt.rcParams['font.family'] = 'DejaVu Sans'

# Load .env file
load_dotenv()

# Logging settings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StandaloneNewsSystem:
    """Fully standalone Fundamental Agent system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Output directory settings
        self.output_dirs = {
            'articles': 'output/standalone_articles',
            'charts': 'output/standalone_charts',
            'images': 'output/standalone_images',
            'data': 'output/standalone_data'
        }
        
        for dir_path in self.output_dirs.values():
            os.makedirs(dir_path, exist_ok=True)
        
        # DeepSeek initialization
        self.init_llm()
        
        # Telegram 설정
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.telegram_notifier = TelegramNotifier(self.telegram_bot_token, self.telegram_chat_id) if self.telegram_bot_token and self.telegram_chat_id else None
        
        self.logger.info("✅ Standalone news system initialized successfully")
    
    def init_llm(self):
        """Initialize DeepSeek API"""
        self.llm = None
        api_key = os.environ.get('DEEPSEEK_API_KEY')
        if api_key:
            try:
                self.deepseek_client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)
                self.llm = self.deepseek_client
                self.logger.info("✅ DeepSeek initialization complete")
            except Exception as e:
                self.logger.error(f"❌ DeepSeek initialization failed: {e}")
        else:
            self.logger.warning("⚠️ DEEPSEEK_API_KEY not set")
    
    def collect_market_data(self, symbols: List[str] = None) -> Dict[str, Any]:
        """Collect market data"""
        
        if symbols is None:
            symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA', 'META', 'AMZN', '^GSPC', '^IXIC', '^VIX']
        
        self.logger.info(f"📊 Collecting data for {len(symbols)} symbols...")
        
        market_data = {
            'timestamp': datetime.now().isoformat(),
            'symbols': {},
            'market_summary': {}
        }
        
        successful_symbols = 0
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="10d")
                
                if not hist.empty and len(hist) >= 2:
                    current_price = hist['Close'].iloc[-1]
                    previous_price = hist['Close'].iloc[-2]
                    change_percent = ((current_price - previous_price) / previous_price) * 100
                    
                    # Calculate technical indicators
                    sma_5 = hist['Close'].rolling(window=5).mean().iloc[-1]
                    sma_10 = hist['Close'].rolling(window=min(10, len(hist))).mean().iloc[-1]
                    
                    market_data['symbols'][symbol] = {
                        'name': info.get('longName', symbol),
                        'current_price': float(current_price),
                        'previous_price': float(previous_price),
                        'change_percent': float(change_percent),
                        'volume': int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0,
                        'high_52w': info.get('fiftyTwoWeekHigh', 0),
                        'low_52w': info.get('fiftyTwoWeekLow', 0),
                        'market_cap': info.get('marketCap', 0),
                        'sma_5': float(sma_5) if not pd.isna(sma_5) else float(current_price),
                        'sma_10': float(sma_10) if not pd.isna(sma_10) else float(current_price),
                        'chart_data': [
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
                        ]
                    }
                    
                    successful_symbols += 1
                    self.logger.info(f"✅ {symbol}: {change_percent:+.2f}%")
                
            except Exception as e:
                self.logger.error(f"❌ {symbol} data collection failed: {e}")
                continue
        
        # Generate market summary
        if market_data['symbols']:
            changes = [data['change_percent'] for data in market_data['symbols'].values()]
            market_data['market_summary'] = {
                'total_symbols': successful_symbols,
                'avg_change': np.mean(changes),
                'positive_count': sum(1 for c in changes if c > 0),
                'negative_count': sum(1 for c in changes if c < 0),
                'max_gainer': max(market_data['symbols'].items(), key=lambda x: x[1]['change_percent']),
                'max_loser': min(market_data['symbols'].items(), key=lambda x: x[1]['change_percent'])
            }
        
        # Save data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        data_file = os.path.join(self.output_dirs['data'], f'market_data_{timestamp}.json')
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(market_data, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"💾 Market data saved: {data_file}")
        return market_data
    
    def detect_significant_events(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect significant events"""
        
        events = []
        
        for symbol, data in market_data['symbols'].items():
            change_percent = data['change_percent']
            
            # Event detection conditions
            conditions = []
            
            # 1. Large price movement
            if abs(change_percent) >= 3.0:
                severity = 'critical' if abs(change_percent) >= 7.0 else 'high' if abs(change_percent) >= 5.0 else 'medium'
                direction = 'surge' if change_percent > 0 else 'plunge'
                conditions.append(f"{abs(change_percent):.1f}% {direction}")
            
            # 2. Volume surge (simple estimation)
            if data['volume'] > 0:
                avg_volume = np.mean([d.get('volume', 0) for d in data.get('chart_data', [])])
                if avg_volume > 0 and data['volume'] > avg_volume * 2:
                    conditions.append("volume surge")
            
            # 3. Technical signals
            if data['current_price'] > data['sma_5'] * 1.02:
                conditions.append("short-term uptrend")
            elif data['current_price'] < data['sma_5'] * 0.98:
                conditions.append("short-term downtrend")
            
            # Create event
            if conditions:
                severity = 'critical' if abs(change_percent) >= 7.0 else 'high' if abs(change_percent) >= 5.0 else 'medium' if abs(change_percent) >= 3.0 else 'low'
                
                event = {
                    'symbol': symbol,
                    'name': data['name'],
                    'event_type': 'market_movement',
                    'severity': severity,
                    'title': f"{symbol} {', '.join(conditions)}",
                    'description': f"{data['name']} fluctuated {change_percent:+.2f}% with {', '.join(conditions)} conditions.",
                    'current_price': data['current_price'],
                    'change_percent': change_percent,
                    'volume': data['volume'],
                    'conditions': conditions,
                    'timestamp': datetime.now().isoformat()
                }
                events.append(event)
        
        # If no events, create event for the most volatile symbol
        if not events and market_data['symbols']:
            max_change_symbol = max(
                market_data['symbols'].items(),
                key=lambda x: abs(x[1]['change_percent'])
            )
            
            symbol, data = max_change_symbol
            change_percent = data['change_percent']
            direction = 'rise' if change_percent > 0 else 'decline'
            
            event = {
                'symbol': symbol,
                'name': data['name'],
                'event_type': 'daily_update',
                'severity': 'low',
                'title': f"{symbol} Daily Market Trend",
                'description': f"{data['name']} {direction}ed by {change_percent:+.2f}%.",
                'current_price': data['current_price'],
                'change_percent': change_percent,
                'volume': data['volume'],
                'conditions': [f"{abs(change_percent):.1f}% {direction}"],
                'timestamp': datetime.now().isoformat()
            }
            events.append(event)
        
        # Sort by severity
        severity_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        events.sort(key=lambda x: severity_order.get(x['severity'], 0), reverse=True)
        
        self.logger.info(f"🚨 {len(events)} events detected")
        return events
    
    def create_enhanced_price_chart(self, symbol: str, data: Dict[str, Any]) -> str:
        """Enhanced price chart generation (error fixed)"""
        
        try:
            chart_data = data.get('chart_data', [])
            if not chart_data or len(chart_data) < 2:
                self.logger.warning(f"⚠️ {symbol} insufficient chart data")
                return ""
            
            # Prepare data (fixed part)
            dates = []
            prices = []
            volumes = []
            highs = []
            lows = []
            
            for item in chart_data:
                try:
                    # Date handling - correctly process pandas DataFrame index
                    if 'timestamp' in item and item['timestamp']:
                        date = item['timestamp']
                        if isinstance(date, str):
                            date = datetime.fromisoformat(date.replace('Z', '+00:00'))
                    elif 'date' in item:
                        date = datetime.strptime(item['date'], '%Y-%m-%d')
                    else:
                        continue  # Skip if no date info
                    
                    dates.append(date)
                    prices.append(float(item.get('close', item.get('Close', 0))))
                    volumes.append(int(item.get('volume', item.get('Volume', 0))))
                    highs.append(float(item.get('high', item.get('High', item.get('close', item.get('Close', 0))))))
                    lows.append(float(item.get('low', item.get('Low', item.get('close', item.get('Close', 0))))))
                    
                except (ValueError, KeyError, TypeError) as e:
                    self.logger.warning(f"⚠️ {symbol} data parsing error: {e}")
                    continue
            
            if len(dates) < 2:
                self.logger.warning(f"⚠️ {symbol} insufficient valid data")
                return ""
            
            # Create chart
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[3, 1])
            
            # Price chart
            ax1.plot(dates, prices, linewidth=2, color='#1f77b4', label='Close Price')
            ax1.fill_between(dates, prices, alpha=0.3, color='#1f77b4')
            ax1.set_title(f'{symbol} - Price Trend (Last {len(dates)} Days)', fontsize=16, fontweight='bold')
            ax1.set_ylabel('Price ($)', fontsize=12)
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            
            # Display current price
            current_price = data['current_price']
            change_percent = data['change_percent']
            color = 'green' if change_percent > 0 else 'red'
            ax1.axhline(y=current_price, color=color, linestyle='--', alpha=0.7)
            ax1.text(dates[-1], current_price, f'${current_price:.2f} ({change_percent:+.2f}%)', 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.7, edgecolor='none'),
                    color='white', fontweight='bold')
            
            # Volume chart
            ax2.bar(dates, volumes, alpha=0.7, color='orange')
            ax2.set_title('Volume', fontsize=12)
            ax2.set_ylabel('Volume', fontsize=10)
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Save file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{symbol}_fixed_chart_{timestamp}.png"
            filepath = os.path.join(self.output_dirs['charts'], filename)
            
            plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            self.logger.info(f"📈 Fixed chart generated successfully: {filename}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"❌ {symbol} chart generation failed: {e}")
            import traceback
            self.logger.error(f"Detailed error: {traceback.format_exc()}")
            return ""
    
    def generate_comprehensive_article(self, event: Dict[str, Any], market_data: Dict[str, Any]) -> str:
        """Generate comprehensive article"""
        
        if not self.llm:
            return self.generate_template_article(event, market_data)
        
        try:
            # Prepare market context
            market_summary = market_data.get('market_summary', {})
            symbol_data = market_data['symbols'].get(event['symbol'], {})
            
            # Other major symbols info
            other_symbols = []
            for sym, data in list(market_data['symbols'].items())[:5]:
                if sym != event['symbol']:
                    other_symbols.append(f"{sym}: {data['change_percent']:+.2f}%")
            
            system_prompt = """You are an experienced economic journalist. Based on the given market data and events, write a professional and insightful economic article in English.

Article writing principles:
1. Deliver objective and accurate information
2. Data-driven analysis and interpretation
3. Provide useful insights for investors
4. Clear and easy-to-understand writing style
5. Interpretation within the overall market context

Article structure:
- Headline (concise and impactful)
- Lead (summary of key points)
- Body (detailed analysis and background)
- Market outlook (future prospects and implications)"""

            user_prompt = f"""Based on the following information, please write a professional economic article in English:

Main Event:
- Symbol: {event['symbol']} ({event['name']})
- Current Situation: {event['title']}
- Price Change: {event['change_percent']:+.2f}% (${event['current_price']:.2f})
- Volume: {event['volume']:,} shares
- Detected Conditions: {', '.join(event.get('conditions', []))}

Overall Market Status:
- Total Symbols: {market_summary.get('total_symbols', 0)}
- Average Change: {market_summary.get('avg_change', 0):+.2f}%
- Advancing Symbols: {market_summary.get('positive_count', 0)}
- Declining Symbols: {market_summary.get('negative_count', 0)}

Major Symbol Trends:
{chr(10).join(other_symbols)}

Technical Information:
- 5-Day SMA: ${symbol_data.get('sma_5', 0):.2f}
- 10-Day SMA: ${symbol_data.get('sma_10', 0):.2f}
- 52-Week High: ${symbol_data.get('high_52w', 0):.2f}
- 52-Week Low: ${symbol_data.get('low_52w', 0):.2f}

Written at: {datetime.now().strftime('%B %d, %Y %H:%M')}

Please write a professional and insightful article."""

            response = self.deepseek_client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=3000,
                temperature=0.7
            )
            return response.choices[0].message.content or ""
            
        except Exception as e:
            self.logger.error(f"❌ AI article generation failed: {e}")
            return self.generate_template_article(event, market_data)
    
    def generate_template_article(self, event: Dict[str, Any], market_data: Dict[str, Any]) -> str:
        """Generate template-based article"""
        
        symbol = event['symbol']
        name = event['name']
        change_percent = event['change_percent']
        current_price = event['current_price']
        conditions = event.get('conditions', [])
        
        direction = 'rise' if change_percent > 0 else 'decline'
        market_summary = market_data.get('market_summary', {})
        
        article = f"""# {symbol} {abs(change_percent):.1f}% {direction}: {', '.join(conditions[:2])}

## Key Summary
{name} recorded a {change_percent:+.2f}% {direction} to ${current_price:.2f} during the {datetime.now().strftime('%B %d, %Y')} trading session. {', '.join(conditions)} observed.

## Detailed Analysis
Today, {name} ({symbol}) stock is trading at ${current_price:.2f}, a {change_percent:+.2f}% {direction} from the previous close."""

        if abs(change_percent) >= 5:
            article += f" This move shows significant volatility and is classified as a {event['severity']} level market event."
        elif abs(change_percent) >= 3:
            article += f" This is a notable fluctuation drawing investor attention."
        else:
            article += f" This movement is within the normal market volatility range."

        article += f"""

Trading volume reached {event['volume']:,} shares, reflecting investor interest.

## Overall Market Trend
Out of {market_summary.get('total_symbols', 0)} total symbols, {market_summary.get('positive_count', 0)} advanced and {market_summary.get('negative_count', 0)} declined. The overall average change was {market_summary.get('avg_change', 0):+.2f}%."""

        # Other major symbols trend
        article += "\n\n### Major Symbol Trends\n"
        for sym, data in list(market_data['symbols'].items())[:5]:
            if sym != symbol:
                article += f"- {sym}: {data['change_percent']:+.2f}% (${data['current_price']:.2f})\n"

        article += f"""

## Investment Implications
{name}'s {'uptrend' if change_percent > 0 else 'downtrend'} """

        if change_percent > 0:
            article += "is interpreted as reflecting positive market sentiment and investor confidence."
        else:
            article += "appears to reflect a market adjustment process or temporary unease."

        article += " Investors should carefully monitor future market trends and related news."

        article += f"\n\n---\n*Article generated: {datetime.now().strftime('%B %d, %Y at %H:%M')} | AI Auto-generated*"
        
        return article
    def create_html_article(self, article_content: str, event: Dict[str, Any], chart_path: str = "") -> str:
        """Create HTML article"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        symbol = event['symbol']
        
        # Chart image HTML
        chart_html = ""
        if chart_path and os.path.exists(chart_path):
            chart_filename = os.path.basename(chart_path)
            chart_html = f'''
            <div class="chart-container">
                <h3>📈 Price Chart</h3>
                <img src="../standalone_charts/{chart_filename}" alt="{symbol} Chart" style="width: 100%; max-width: 800px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            </div>
            '''
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{event['title']} - Fundamental Agent</title>
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
                <div class="meta-item">📊 Symbol: {symbol}</div>
                <div class="meta-item">⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
                <div class="meta-item">🤖 AI Auto-generated</div>
                <div class="meta-item">📈 Real-time Data</div>
            </div>
        </div>
        
        <div class="price-info">
            💰 Current Price: ${event['current_price']:.2f} 
            ({event['change_percent']:+.2f}% {'📈' if event['change_percent'] > 0 else '📉'})
            | Volume: {event['volume']:,}
            <span class="severity-badge severity-{event['severity']}">{event['severity']}</span>
        </div>
        
        <div class="conditions-list">
            <strong>🔍 Detected Conditions:</strong>
            <ul>
                {chr(10).join([f'<li>{condition}</li>' for condition in event.get('conditions', [])])}
            </ul>
        </div>
        
        {chart_html}
        
        <div class="content">
            {self.markdown_to_html(article_content)}
        </div>
        
        <div class="footer">
            <p><strong>🤖 This article was automatically generated by AI analyzing real-time market data.</strong></p>
            <p>📊 Data Source: Yahoo Finance | Generated: {datetime.now().strftime('%B %d, %Y %H:%M')}</p>
            <p>⚠️ This information is not investment advice. Please make investment decisions carefully.</p>
        </div>
    </div>
</body>
</html>'''
        
        # Save HTML file
        filename = f"{symbol}_standalone_{timestamp}.html"
        filepath = os.path.join(self.output_dirs['articles'], filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"📄 HTML article generated: {filepath}")
        return filepath
    
    def markdown_to_html(self, markdown_text: str) -> str:
        """Convert markdown to HTML"""
        
        html = markdown_text
        
        # Convert headers
        html = html.replace('### ', '<h3>').replace('\n### ', '</h3>\n<h3>')
        html = html.replace('## ', '<h2>').replace('\n## ', '</h2>\n<h2>')  
        html = html.replace('# ', '<h1>').replace('\n# ', '</h1>\n<h1>')
        
        # Close last header
        if '<h1>' in html and html.count('<h1>') > html.count('</h1>'):
            html += '</h1>'
        if '<h2>' in html and html.count('<h2>') > html.count('</h2>'):
            html += '</h2>'
        if '<h3>' in html and html.count('<h3>') > html.count('</h3>'):
            html += '</h3>'
        
        # Convert paragraphs
        paragraphs = html.split('\n\n')
        html_paragraphs = []
        
        for p in paragraphs:
            p = p.strip()
            if p and not p.startswith('<h') and not p.startswith('*') and not p.startswith('---'):
                if p.startswith('- '):
                    # Handle list
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
        """Send enhanced Telegram notification"""
        
        telegram_success = False
        if self.telegram_notifier:
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
                    f"{emoji} <b>Standalone Fundamental Agent</b>\n"
                    f"<b>{event['title']}</b>\n\n"
                    f"{event['description']}\n\n"
                    f"📊 Symbol: {event['symbol']} | Change: {event['change_percent']:+.2f}%\n"
                    f"💰 Price: ${event['current_price']:.2f} | Volume: {event['volume']:,}\n"
                    f"⚠️ Severity: {event['severity'].upper()} | Conditions: {len(event.get('conditions', []))}\n"
                    f"📄 HTML: {os.path.basename(article_filepath)}"
                )
                asyncio.run(self.telegram_notifier._send_telegram(tg_message))
                self.logger.info("✅ Telegram notification sent successfully")
                telegram_success = True
            except Exception as e:
                self.logger.error(f"❌ Telegram notification error: {e}")
        
        return telegram_success
    
    def run_complete_system(self) -> Dict[str, Any]:
        """Run complete system"""
        
        start_time = datetime.now()
        self.logger.info("🚀 Standalone news system started")
        
        try:
            # 1. Collect market data
            self.logger.info("📊 Step 1: Collecting market data")
            market_data = self.collect_market_data()
            
            if not market_data['symbols']:
                raise Exception("Market data collection failed")
            
            # 2. Detect events
            self.logger.info("🚨 Step 2: Detecting significant events")
            events = self.detect_significant_events(market_data)
            
            if not events:
                raise Exception("No events detected")
            
            # 3. Generate and process articles
            self.logger.info("✍️ Step 3: Generating comprehensive articles")
            results = []
            
            for event in events[:3]:  # Process up to 3 events
                self.logger.info(f"📝 Processing {event['symbol']}...")
                
                # Create chart
                chart_path = self.create_enhanced_price_chart(event['symbol'], market_data['symbols'][event['symbol']])
                
                # Generate AI article
                article_content = self.generate_comprehensive_article(event, market_data)
                
                # Create HTML file
                html_filepath = self.create_html_article(article_content, event, chart_path)
                
                # Send Telegram notification
                telegram_success = self.send_enhanced_telegram_notification(html_filepath, event, chart_path)
                
                results.append({
                    'event': event,
                    'article_content': article_content,
                    'html_file': html_filepath,
                    'chart_file': chart_path,
                    'telegram_sent': telegram_success
                })
                
                self.logger.info(f"✅ {event['symbol']} processing complete")
            
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
            
            # Save result
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            result_file = os.path.join(self.output_dirs['data'], f'execution_result_{timestamp}.json')
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2, default=str)
            
            self.logger.info(f"🎉 Standalone system execution complete ({execution_time:.1f}s)")
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
    
    print("🚀 Fully standalone Fundamental Agent system")
    print("=" * 70)
    print("✅ No OrchestratorStrand dependency")
    print("✅ Stable standalone execution")
    print("✅ AI article generation + Charts + Telegram alerts")
    print("=" * 70)
    
    # Initialize system
    system = StandaloneNewsSystem()
    
    # Run complete system
    result = system.run_complete_system()
    
    # Print results
    print("\n📊 Execution Results:")
    print(f"Status: {result.get('status', 'unknown')}")
    print(f"Execution Time: {result.get('execution_time', 0):.1f}s")
    print(f"Events Processed: {result.get('events_processed', 0)}")
    print(f"Articles Generated: {result.get('articles_generated', 0)}")
    print(f"Charts Generated: {result.get('charts_generated', 0)}")
    print(f"Telegram Notifications: {result.get('telegram_notifications', 0)}")
    
    if result.get('status') == 'success':
        print("\n🎉 Standalone system execution complete!")
        
        # Market summary
        market_summary = result.get('market_summary', {})
        if market_summary:
            print("\n📈 Market Summary:")
            print(f"  Total Symbols: {market_summary.get('total_symbols', 0)}")
            print(f"  Average Change: {market_summary.get('avg_change', 0):+.2f}%")
            print(f"  Advancing: {market_summary.get('positive_count', 0)}")
            print(f"  Declining: {market_summary.get('negative_count', 0)}")
        
        # Generated file list
        results = result.get('results', [])
        if results:
            print("\n💡 Generated Files:")
            for i, res in enumerate(results):
                event = res.get('event', {})
                html_file = res.get('html_file', '')
                chart_file = res.get('chart_file', '')
                
                print(f"  {i+1}. {event.get('symbol', 'Unknown')} ({event.get('severity', 'unknown')})")
                if html_file:
                    print(f"     📄 HTML: {html_file}")
                if chart_file:
                    print(f"     📈 Chart: {chart_file}")
                print(f"     📱 Telegram: {'✅' if res.get('telegram_sent') else '❌'}")
        
        print("\n🌐 View HTML Article:")
        if results and results[0].get('html_file'):
            latest_html = results[0]['html_file']
            print(f"  open {latest_html}")
        
        print("\n📱 Check Telegram for notifications!")
    else:
        print(f"\n❌ Execution Failed: {result.get('error', 'Unknown error')}")
        print("\n🔧 Troubleshooting:")
        print("  • AWS credentials: aws sts get-caller-identity")
        print("  • Check TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env")
        print("  • Check internet connection")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
