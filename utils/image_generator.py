"""
Article Image and Chart Generation Module
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from wordcloud import WordCloud
import io
import base64
from typing import Dict, List, Optional, Tuple
import logging
import os

class ArticleImageGenerator:
    """Article image generation class"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Korean font setup
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['axes.unicode_minus'] = False
        
        # Color palette
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e', 
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff7f0e',
            'info': '#17a2b8'
        }
        
        # Output directory
        self.output_dir = "output/images"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_stock_chart(self, symbol: str, period: str = "1mo") -> str:
        """Generate stock chart"""
        try:
            # Data collection
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                return None
            
            # Create chart
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), 
                                          gridspec_kw={'height_ratios': [3, 1]})
            
            # Price chart
            ax1.plot(data.index, data['Close'], color=self.colors['primary'], 
                    linewidth=2, label='Close Price')
            ax1.fill_between(data.index, data['Close'], alpha=0.3, 
                           color=self.colors['primary'])
            
            # Add moving averages
            data['MA20'] = data['Close'].rolling(window=20).mean()
            data['MA50'] = data['Close'].rolling(window=50).mean()
            
            ax1.plot(data.index, data['MA20'], color=self.colors['warning'], 
                    linewidth=1, label='MA20', alpha=0.8)
            ax1.plot(data.index, data['MA50'], color=self.colors['danger'], 
                    linewidth=1, label='MA50', alpha=0.8)
            
            ax1.set_title(f'{symbol} Stock Price Chart', fontsize=16, fontweight='bold')
            ax1.set_ylabel('Price ($)', fontsize=12)
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Volume chart
            colors = ['red' if close < open else 'green' 
                     for close, open in zip(data['Close'], data['Open'])]
            ax2.bar(data.index, data['Volume'], color=colors, alpha=0.6)
            ax2.set_title('Trading Volume', fontsize=12)
            ax2.set_ylabel('Volume', fontsize=10)
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Save file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_dir}/stock_chart_{symbol}_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            return filename
            
        except Exception as e:
            self.logger.error(f"Failed to generate stock chart for {symbol}: {str(e)}")
            return None
    
    def generate_market_overview_chart(self, symbols: List[str]) -> str:
        """Generate market overview chart"""
        try:
            # Data collection
            data = {}
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                info = ticker.history(period="1d")
                if not info.empty:
                    current = info['Close'].iloc[-1]
                    previous = info['Open'].iloc[-1]
                    change_pct = ((current - previous) / previous) * 100
                    data[symbol] = change_pct
            
            if not data:
                return None
            
            # Create chart
            fig, ax = plt.subplots(figsize=(12, 6))
            
            symbols = list(data.keys())
            changes = list(data.values())
            colors = ['green' if x > 0 else 'red' for x in changes]
            
            bars = ax.bar(symbols, changes, color=colors, alpha=0.7)
            
            # Display values
            for bar, change in zip(bars, changes):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{change:.2f}%', ha='center', 
                       va='bottom' if height > 0 else 'top')
            
            ax.set_title('Market Overview - Daily Change (%)', 
                        fontsize=16, fontweight='bold')
            ax.set_ylabel('Change (%)', fontsize=12)
            ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            ax.grid(True, alpha=0.3)
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Save file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_dir}/market_overview_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            return filename
            
        except Exception as e:
            self.logger.error(f"Failed to generate market overview chart: {str(e)}")
            return None
    
    def generate_sector_performance_chart(self, sector_data: Dict[str, float]) -> str:
        """Generate sector performance chart"""
        try:
            if not sector_data:
                return None
            
            # Sort data
            sorted_data = sorted(sector_data.items(), key=lambda x: x[1], reverse=True)
            sectors = [item[0] for item in sorted_data]
            performance = [item[1] for item in sorted_data]
            
            # Create chart
            fig, ax = plt.subplots(figsize=(10, 8))
            
            colors = ['green' if x > 0 else 'red' for x in performance]
            bars = ax.barh(sectors, performance, color=colors, alpha=0.7)
            
            # Display values
            for bar, perf in zip(bars, performance):
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2.,
                       f'{perf:.2f}%', ha='left' if width > 0 else 'right',
                       va='center')
            
            ax.set_title('Sector Performance (%)', fontsize=16, fontweight='bold')
            ax.set_xlabel('Performance (%)', fontsize=12)
            ax.axvline(x=0, color='black', linestyle='-', alpha=0.3)
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Save file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_dir}/sector_performance_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            return filename
            
        except Exception as e:
            self.logger.error(f"Failed to generate sector performance chart: {str(e)}")
            return None
    
    def generate_technical_indicators_chart(self, symbol: str) -> str:
        """Generate technical indicators chart"""
        try:
            # Data collection
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="3mo")
            
            if data.empty:
                return None
            
            # Calculate technical indicators
            data['RSI'] = self._calculate_rsi(data['Close'])
            data['MACD'], data['MACD_Signal'] = self._calculate_macd(data['Close'])
            data['BB_Upper'], data['BB_Lower'] = self._calculate_bollinger_bands(data['Close'])
            
            # Create chart
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            
            # 1. Price + Bollinger Bands
            ax1.plot(data.index, data['Close'], label='Close', color=self.colors['primary'])
            ax1.plot(data.index, data['BB_Upper'], label='BB Upper', color=self.colors['danger'], alpha=0.7)
            ax1.plot(data.index, data['BB_Lower'], label='BB Lower', color=self.colors['danger'], alpha=0.7)
            ax1.fill_between(data.index, data['BB_Upper'], data['BB_Lower'], alpha=0.1)
            ax1.set_title(f'{symbol} - Price & Bollinger Bands')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # 2. RSI
            ax2.plot(data.index, data['RSI'], color=self.colors['warning'])
            ax2.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Overbought')
            ax2.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='Oversold')
            ax2.set_title('RSI (Relative Strength Index)')
            ax2.set_ylim(0, 100)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # 3. MACD
            ax3.plot(data.index, data['MACD'], label='MACD', color=self.colors['primary'])
            ax3.plot(data.index, data['MACD_Signal'], label='Signal', color=self.colors['secondary'])
            ax3.bar(data.index, data['MACD'] - data['MACD_Signal'], 
                   label='Histogram', alpha=0.3)
            ax3.set_title('MACD')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
            # 4. Volume
            ax4.bar(data.index, data['Volume'], alpha=0.6, color=self.colors['info'])
            ax4.set_title('Trading Volume')
            ax4.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Save file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_dir}/technical_indicators_{symbol}_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            return filename
            
        except Exception as e:
            self.logger.error(f"Failed to generate technical indicators chart for {symbol}: {str(e)}")
            return None
    
    def generate_wordcloud(self, text: str, title: str = "Word Cloud") -> str:
        """Generate word cloud"""
        try:
            if not text:
                return None
            
            # Generate word cloud
            wordcloud = WordCloud(
                width=800, height=400,
                background_color='white',
                colormap='viridis',
                max_words=100,
                relative_scaling=0.5,
                random_state=42
            ).generate(text)
            
            # Create chart
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.set_title(title, fontsize=16, fontweight='bold')
            ax.axis('off')
            
            plt.tight_layout()
            
            # Save file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_dir}/wordcloud_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            return filename
            
        except Exception as e:
            self.logger.error(f"Failed to generate word cloud: {str(e)}")
            return None
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_macd(self, prices: pd.Series) -> Tuple[pd.Series, pd.Series]:
        """Calculate MACD"""
        ema12 = prices.ewm(span=12).mean()
        ema26 = prices.ewm(span=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9).mean()
        return macd, signal
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> Tuple[pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper, lower
    
    def generate_article_images(self, article_data: Dict, symbols: List[str] = None) -> List[str]:
        """Generate article image package"""
        generated_images = []
        
        try:
            # Default symbols
            if not symbols:
                symbols = ["AAPL", "GOOGL", "MSFT", "^GSPC"]
            
            # 1. Market overview chart
            market_chart = self.generate_market_overview_chart(symbols[:4])
            if market_chart:
                generated_images.append(market_chart)
            
            # 2. Key stock chart
            if symbols:
                stock_chart = self.generate_stock_chart(symbols[0])
                if stock_chart:
                    generated_images.append(stock_chart)
            
            # 3. Technical indicators chart
            if symbols:
                tech_chart = self.generate_technical_indicators_chart(symbols[0])
                if tech_chart:
                    generated_images.append(tech_chart)
            
            # 4. Word cloud (based on article content)
            if article_data.get('content'):
                wordcloud = self.generate_wordcloud(
                    article_data['content'], 
                    "Article Keywords"
                )
                if wordcloud:
                    generated_images.append(wordcloud)
            
            # 5. Sector performance chart (sample data)
            sector_data = {
                "Technology": 2.3,
                "Healthcare": 1.1,
                "Financial": -0.8,
                "Energy": -1.5,
                "Consumer": 0.9
            }
            sector_chart = self.generate_sector_performance_chart(sector_data)
            if sector_chart:
                generated_images.append(sector_chart)
            
            self.logger.info(f"Generated {len(generated_images)} article images")
            return generated_images
            
        except Exception as e:
            self.logger.error(f"Failed to generate article images: {str(e)}")
            return generated_images

# Test function
def test_image_generator():
    """Test image generator"""
    generator = ArticleImageGenerator()
    
    print("📊 Starting image generator test...")
    
    # Test data
    test_article = {
        "content": "stock market analysis technology growth investment financial economic news"
    }
    
    # Generate images
    images = generator.generate_article_images(test_article, ["AAPL", "GOOGL", "MSFT"])
    
    print(f"✅ Generated images: {len(images)}")
    for img in images:
        print(f"  📁 {img}")

if __name__ == "__main__":
    test_image_generator()
