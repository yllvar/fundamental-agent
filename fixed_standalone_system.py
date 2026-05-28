#!/usr/bin/env python3
"""
Chart generation error fixed fully standalone Fundamental Agent system
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
import matplotlib.dates as mdates
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

class FixedStandaloneNewsSystem:
    """Chart generation error fixed standalone Fundamental Agent system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Output directory settings
        self.output_dirs = {
            'articles': 'output/fixed_articles',
            'charts': 'output/fixed_charts',
            'images': 'output/fixed_images',
            'data': 'output/fixed_data'
        }
        
        for dir_path in self.output_dirs.values():
            os.makedirs(dir_path, exist_ok=True)
        
        # DeepSeek initialization
        self.init_llm()
        
        self.logger.info("✅ Fixed standalone news system initialized successfully")
    
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
        """Collect market data (improved data structure for chart generation)"""
        
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
                hist = ticker.history(period="30d")  # Extended to 30 days
                
                if not hist.empty and len(hist) >= 2:
                    current_price = hist['Close'].iloc[-1]
                    previous_price = hist['Close'].iloc[-2]
                    change_percent = ((current_price - previous_price) / previous_price) * 100
                    
                    # Calculate technical indicators
                    sma_5 = hist['Close'].rolling(window=5).mean().iloc[-1]
                    sma_10 = hist['Close'].rolling(window=min(10, len(hist))).mean().iloc[-1]
                    
                    # Chart data preparation (fixed part)
                    chart_data = []
                    for date, row in hist.tail(20).iterrows():  # Last 20 days
                        chart_data.append({
                            'date': date.strftime('%Y-%m-%d'),
                            'timestamp': date,
                            'open': float(row['Open']),
                            'high': float(row['High']),
                            'low': float(row['Low']),
                            'close': float(row['Close']),
                            'volume': int(row['Volume']) if 'Volume' in row and not pd.isna(row['Volume']) else 0
                        })
                    
                    market_data['symbols'][symbol] = {
                        'name': info.get('longName', symbol),
                        'current_price': float(current_price),
                        'previous_price': float(previous_price),
                        'change_percent': float(change_percent),
                        'volume': int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns and not pd.isna(hist['Volume'].iloc[-1]) else 0,
                        'high_52w': info.get('fiftyTwoWeekHigh', 0),
                        'low_52w': info.get('fiftyTwoWeekLow', 0),
                        'market_cap': info.get('marketCap', 0),
                        'sma_5': float(sma_5) if not pd.isna(sma_5) else float(current_price),
                        'sma_10': float(sma_10) if not pd.isna(sma_10) else float(current_price),
                        'chart_data': chart_data  # Fixed chart data
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
            
            # 2. Volume surge (improved calculation)
            if data['volume'] > 0 and data.get('chart_data'):
                volumes = [d['volume'] for d in data['chart_data'] if d['volume'] > 0]
                if len(volumes) > 5:
                    avg_volume = np.mean(volumes[:-1])  # Average excluding today
                    if avg_volume > 0 and data['volume'] > avg_volume * 2:
                        conditions.append("volume surge")
            
            # 3. Technical signals
            if data['current_price'] > data['sma_5'] * 1.02:
                conditions.append("short-term uptrend")
            elif data['current_price'] < data['sma_5'] * 0.98:
                conditions.append("short-term downtrend")
            
            # 4. Near 52-week high/low
            if data.get('high_52w', 0) > 0:
                if data['current_price'] > data['high_52w'] * 0.95:
                    conditions.append("near 52-week high")
            if data.get('low_52w', 0) > 0:
                if data['current_price'] < data['low_52w'] * 1.05:
                    conditions.append("near 52-week low")
            
            # Create event
            if conditions:
                severity = 'critical' if abs(change_percent) >= 7.0 else 'high' if abs(change_percent) >= 5.0 else 'medium' if abs(change_percent) >= 3.0 else 'low'
                
                event = {
                    'symbol': symbol,
                    'name': data['name'],
                    'event_type': 'market_movement',
                    'severity': severity,
                    'title': f"{symbol} {', '.join(conditions[:2])}",
                    'description': f"{data['name']} fluctuated {change_percent:+.2f}% with {', '.join(conditions[:3])} conditions.",
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
                    # Date handling
                    if 'timestamp' in item and item['timestamp']:
                        date = item['timestamp']
                        if isinstance(date, str):
                            date = datetime.fromisoformat(date.replace('Z', '+00:00'))
                    else:
                        date = datetime.strptime(item['date'], '%Y-%m-%d')
                    
                    dates.append(date)
                    prices.append(float(item['close']))
                    volumes.append(int(item.get('volume', 0)))
                    highs.append(float(item.get('high', item['close'])))
                    lows.append(float(item.get('low', item['close'])))
                    
                except (ValueError, KeyError, TypeError) as e:
                    self.logger.warning(f"⚠️ {symbol} data parsing error: {e}")
                    continue
            
            if len(dates) < 2:
                self.logger.warning(f"⚠️ {symbol} insufficient valid data")
                return ""
            
            # Create chart
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), height_ratios=[3, 1])
            fig.suptitle(f'{symbol} - Price and Volume Analysis', fontsize=16, fontweight='bold')
            
            # Price chart (candlestick style)
            ax1.plot(dates, prices, linewidth=2.5, color='#1f77b4', label='Close', marker='o', markersize=3)
            ax1.fill_between(dates, lows, highs, alpha=0.2, color='#1f77b4', label='High-Low Range')
            
            # Add moving average lines
            if len(prices) >= 5:
                sma_5 = pd.Series(prices).rolling(window=5).mean()
                ax1.plot(dates, sma_5, '--', color='orange', alpha=0.8, label='5-day SMA')
            
            if len(prices) >= 10:
                sma_10 = pd.Series(prices).rolling(window=10).mean()
                ax1.plot(dates, sma_10, '--', color='red', alpha=0.8, label='10-day SMA')
            
            # Highlight current price
            current_price = data['current_price']
            change_percent = data['change_percent']
            color = '#28a745' if change_percent > 0 else '#dc3545'
            
            ax1.axhline(y=current_price, color=color, linestyle='-', alpha=0.8, linewidth=2)
            ax1.text(dates[-1], current_price, f'${current_price:.2f}\n({change_percent:+.2f}%)', 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.8, edgecolor='none'),
                    color='white', fontweight='bold', ha='right', va='bottom')
            
            ax1.set_title(f'Price Trend (Last {len(dates)} Days)', fontsize=14)
            ax1.set_ylabel('Price ($)', fontsize=12)
            ax1.grid(True, alpha=0.3)
            ax1.legend(loc='upper left')
            
            # Date formatting
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax1.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//7)))
            
            # Volume chart
            colors = ['#28a745' if p >= prices[i-1] else '#dc3545' if i > 0 else '#6c757d' for i, p in enumerate(prices)]
            bars = ax2.bar(dates, volumes, alpha=0.7, color=colors)
            
            ax2.set_title('Volume', fontsize=12)
            ax2.set_ylabel('Volume', fontsize=10)
            ax2.grid(True, alpha=0.3)
            
            # Volume average line
            if len(volumes) > 1:
                avg_volume = np.mean(volumes)
                ax2.axhline(y=avg_volume, color='purple', linestyle='--', alpha=0.7, label=f'Avg: {avg_volume:,.0f}')
                ax2.legend()
            
            # Date formatting
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax2.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//7)))
            
            # Layout adjustment
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
            plt.tight_layout()
            
            # Save file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{symbol}_enhanced_chart_{timestamp}.png"
            filepath = os.path.join(self.output_dirs['charts'], filename)
            
            plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
            plt.close()
            
            self.logger.info(f"📈 Enhanced chart generated successfully: {filename}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"❌ {symbol} chart generation failed: {e}")
            import traceback
            self.logger.error(f"Detailed error: {traceback.format_exc()}")
            return ""
