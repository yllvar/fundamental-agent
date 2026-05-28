#!/usr/bin/env python3
"""
Completely independent Fundamental Agent system
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
    """Completely independent Fundamental Agent system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Output directory setup
        self.output_dirs = {
            'articles': 'output/standalone_articles',
            'charts': 'output/standalone_charts',
            'images': 'output/standalone_images',
            'data': 'output/standalone_data'
        }
        
        for dir_path in self.output_dirs.values():
            os.makedirs(dir_path, exist_ok=True)
        
        # Initialize DeepSeek
        self.init_llm()
        
        self.logger.info("✅ Standalone news system initialized")
    
    def init_llm(self):
        """Initialize DeepSeek API"""
        self.llm = None
        api_key = os.environ.get('DEEPSEEK_API_KEY')
        if api_key:
            try:
                self.deepseek_client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)
                self.llm = self.deepseek_client
                self.logger.info("✅ DeepSeek initialized")
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
                        'historical_data': hist.tail(10).to_dict('records')
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
                avg_volume = np.mean([d.get('Volume', 0) for d in data.get('historical_data', [])])
                if avg_volume > 0 and data['volume'] > avg_volume * 2:
                    conditions.append("Volume surge")
            
            # 3. Technical signals
            if data['current_price'] > data['sma_5'] * 1.02:
                conditions.append("Short-term uptrend")
            elif data['current_price'] < data['sma_5'] * 0.98:
                conditions.append("Short-term downtrend")
            
            # Create event
            if conditions:
                severity = 'critical' if abs(change_percent) >= 7.0 else 'high' if abs(change_percent) >= 5.0 else 'medium' if abs(change_percent) >= 3.0 else 'low'
                
                event = {
                    'symbol': symbol,
                    'name': data['name'],
                    'event_type': 'market_movement',
                    'severity': severity,
                    'title': f"{symbol} {', '.join(conditions)}",
                    'description': f"{data['name']} ({symbol}) moved {change_percent:+.2f}% with {', '.join(conditions)}.",
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
                'title': f"{symbol} Daily Market Update",
                'description': f"{data['name']} ({symbol}) {direction}d {change_percent:+.2f}%.",
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
        
        self.logger.info(f"🚨 {len(events)} event(s) detected")
        return events
    
    def create_price_chart(self, symbol: str, data: Dict[str, Any]) -> str:
        """Create price chart"""
        
        try:
            historical_data = data.get('historical_data', [])
            if not historical_data:
                return ""
            
            # Prepare data
            dates = [datetime.fromisoformat(d['Date'].replace('Z', '+00:00')).date() if isinstance(d['Date'], str) else d['Date'] for d in historical_data]
            prices = [d['Close'] for d in historical_data]
            volumes = [d.get('Volume', 0) for d in historical_data]
            
            # Create chart
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[3, 1])
            
            # Price chart
            ax1.plot(dates, prices, linewidth=2, color='#1f77b4', label='Close Price')
            ax1.fill_between(dates, prices, alpha=0.3, color='#1f77b4')
            ax1.set_title(f'{symbol} - Price Trend (Last 10 Days)', fontsize=16, fontweight='bold')
            ax1.set_ylabel('Price ($)', fontsize=12)
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            
            # Show current price
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
            filename = f"{symbol}_price_chart_{timestamp}.png"
            filepath = os.path.join(self.output_dirs['charts'], filename)
            
            plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            self.logger.info(f"📈 Chart created: {filename}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"❌ {symbol} chart creation failed: {e}")
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
            
            system_prompt = """You are an experienced economic journalist. Write a professional and insightful economic article in English based on the given market data and events.

Article writing principles:
1. Deliver objective and accurate information
2. Data-driven analysis and interpretation
3. Provide useful insights for investors
4. Clear and easy-to-understand writing style
5. Interpret within the overall market context

Article structure:
- Headline (concise and impactful)
- Lead (summary of key points)
- Body (detailed analysis and background)
- Market outlook (future prospects and implications)"""

            user_prompt = f"""Please write a professional economic article in English based on the following information:

Main Event:
- Symbol: {event['symbol']} ({event['name']})
- Current Situation: {event['title']}
- Price Change: {event['change_percent']:+.2f}% (${event['current_price']:.2f})
- Volume: {event['volume']:,} shares
- Detected Conditions: {', '.join(event.get('conditions', []))}

Overall Market Status:
- Total Symbols: {market_summary.get('total_symbols', 0)}
- Average Change: {market_summary.get('avg_change', 0):+.2f}%
- Rising Symbols: {market_summary.get('positive_count', 0)}
- Declining Symbols: {market_summary.get('negative_count', 0)}

Major Symbol Movements:
{chr(10).join(other_symbols)}

Technical Information:
- 5-Day Moving Average: ${symbol_data.get('sma_5', 0):.2f}
- 10-Day Moving Average: ${symbol_data.get('sma_10', 0):.2f}
- 52-Week High: ${symbol_data.get('high_52w', 0):.2f}
- 52-Week Low: ${symbol_data.get('low_52w', 0):.2f}

Written at: {datetime.now().strftime('%B %d, %Y at %H:%M')}

Please write a professional and insightful article in English."""

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
        
        direction = 'surge' if change_percent > 0 else 'decline'
        market_summary = market_data.get('market_summary', {})
        
        article = f"""# {symbol} {abs(change_percent):.1f}% {direction}, {', '.join(conditions[:2])}

## Key Summary
{name} {direction}d {change_percent:+.2f}% to ${current_price:.2f} during {datetime.now().strftime('%B %d, %Y')} trading. {', '.join(conditions)} observed.

## Detailed Analysis
Today, {name} ({symbol}) is trading at ${current_price:.2f}, reflecting a {change_percent:+.2f}% {direction} from the previous close."""

        if abs(change_percent) >= 5:
            article += f" This represents significant volatility and is classified as a {event['severity']}-level market event."
        elif abs(change_percent) >= 3:
            article += f" This is a notable movement drawing investor attention."
        else:
            article += f" This is within the normal range of market fluctuation."

        article += f"""

Trading volume reached {event['volume']:,} shares, indicating investor interest levels.

## Overall Market Trend
Out of {market_summary.get('total_symbols', 0)} total symbols, {market_summary.get('positive_count', 0)} rose and {market_summary.get('negative_count', 0)} declined. The average market change was {market_summary.get('avg_change', 0):+.2f}%."""

        # Other major symbols movements
        article += "\n\n### Key Symbol Movements\n"
        for sym, data in list(market_data['symbols'].items())[:5]:
            if sym != symbol:
                article += f"- {sym}: {data['change_percent']:+.2f}% (${data['current_price']:.2f})\n"

        article += f"""

## Investment Implications
{name}'s {'upward' if change_percent > 0 else 'downward'} movement """

        if change_percent > 0:
            article += "is interpreted as reflecting positive market sentiment and investor confidence."
        else:
            article += "appears to reflect a market correction or temporary investor unease."

        article += " Investors should closely monitor future market trends and related news."

        article += f"\n\n---\n*Article generated: {datetime.now().strftime('%B %d, %Y at %H:%M')} | AI Auto-generated*"
        
        return article
