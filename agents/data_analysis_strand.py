"""
Data Analysis Strand Agent
Analyzes event-related data and generates charts
"""

import os
import sys
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

# Improved Matplotlib settings
matplotlib.use('Agg')

# Korean font settings
import matplotlib.font_manager as fm
import platform

# System-specific font settings
def setup_matplotlib_fonts():
    """Set matplotlib fonts"""
    if platform.system() == 'Linux':
        # Try available fonts on Linux
        font_candidates = [
            'NanumGothic', 'NanumBarunGothic', 'DejaVu Sans', 
            'Liberation Sans', 'Arial', 'sans-serif'
        ]
        
        for font_name in font_candidates:
            try:
                # Check if font exists
                font_path = fm.findfont(fm.FontProperties(family=font_name))
                if font_path:
                    plt.rcParams['font.family'] = font_name
                    break
            except:
                continue
        else:
            # Fallback to default when all fonts fail
            plt.rcParams['font.family'] = 'sans-serif'
    
    # Common settings
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.titlesize'] = 16
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12
    plt.rcParams['legend.fontsize'] = 12

# Apply font settings
setup_matplotlib_fonts()

from .strands_framework import BaseStrandAgent, StrandContext, StrandMessage, MessageType

class DataAnalysisStrand(BaseStrandAgent):
    """Data Analysis Strand Agent"""
    
    def __init__(self):
        super().__init__(
            agent_id="data_analyst",
            name="Data Analysis Agent"
        )
        
        # Set output directory
        self.charts_dir = "output/charts"
        os.makedirs(self.charts_dir, exist_ok=True)
        
        self.capabilities = [
            "stock_data_analysis",
            "technical_indicators",
            "chart_generation",
            "market_comparison",
            "volatility_analysis"
        ]
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return self.capabilities
    
    async def process(self, context: StrandContext, message: Optional[StrandMessage] = None) -> Dict[str, Any]:
        """Process data analysis"""
        
        # Extract event information from input data
        event_data = context.input_data.get('event')
        if not event_data:
            raise Exception("No event data")
        
        symbol = event_data.get('symbol')
        if not symbol:
            raise Exception("No symbol information")
        
        self.logger.info(f"📊 {symbol} data analysis started")
        
        try:
            # 1. Basic data collection
            analysis_result = await self._collect_basic_data(symbol)
            
            # 2. Calculate technical indicators
            technical_indicators = await self._calculate_technical_indicators(symbol)
            analysis_result['technical_indicators'] = technical_indicators
            
            # 3. Statistical analysis
            statistics = await self._calculate_statistics(symbol)
            analysis_result['statistics'] = statistics
            
            # 4. Market comparison analysis
            market_comparison = await self._market_comparison_analysis(symbol)
            analysis_result['market_comparison'] = market_comparison
            
            # 5. Chart generation
            chart_paths = await self._generate_charts(symbol, analysis_result)
            analysis_result['chart_paths'] = chart_paths
            
            # 6. Event impact analysis
            event_impact = await self._analyze_event_impact(event_data, analysis_result)
            analysis_result['event_impact'] = event_impact
            
            # Save results to shared memory
            await self.set_shared_data(context, 'data_analysis', analysis_result)
            await self.set_shared_data(context, 'chart_paths', chart_paths)
            
            self.logger.info(f"✅ {symbol} data analysis completed")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"❌ Data analysis failed: {e}")
            raise
    
    async def _collect_basic_data(self, symbol: str) -> Dict[str, Any]:
        """Basic data collection"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1mo")
            
            if hist.empty:
                raise Exception(f"Cannot fetch data: {symbol}")
            
            current_price = hist['Close'].iloc[-1]
            previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            volume = hist['Volume'].iloc[-1]
            
            return {
                'symbol': symbol,
                'analysis_timestamp': datetime.now().isoformat(),
                'raw_data': {
                    'current_price': float(current_price),
                    'previous_close': float(previous_close),
                    'volume': int(volume),
                    'high_52w': info.get('fiftyTwoWeekHigh'),
                    'low_52w': info.get('fiftyTwoWeekLow')
                },
                'historical_data': hist
            }
        except Exception as e:
            self.logger.error(f"Basic data collection failed: {e}")
            raise
    
    async def _calculate_technical_indicators(self, symbol: str) -> Dict[str, Any]:
        """Calculate technical indicators"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="3mo")
            
            if len(hist) < 20:
                return {}
            
            # 이동평균
            sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            sma_50 = hist['Close'].rolling(window=50).mean().iloc[-1] if len(hist) >= 50 else None
            
            # MACD
            exp1 = hist['Close'].ewm(span=12).mean()
            exp2 = hist['Close'].ewm(span=26).mean()
            macd = exp1 - exp2
            macd_signal = macd.ewm(span=9).mean()
            
            # RSI
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # 볼린저 밴드
            bb_period = 20
            bb_std = 2
            sma = hist['Close'].rolling(window=bb_period).mean()
            std = hist['Close'].rolling(window=bb_period).std()
            bb_upper = sma + (std * bb_std)
            bb_lower = sma - (std * bb_std)
            
            return {
                'sma_20': float(sma_20) if not pd.isna(sma_20) else None,
                'sma_50': float(sma_50) if sma_50 and not pd.isna(sma_50) else None,
                'macd': float(macd.iloc[-1]) if not pd.isna(macd.iloc[-1]) else None,
                'macd_signal': float(macd_signal.iloc[-1]) if not pd.isna(macd_signal.iloc[-1]) else None,
                'rsi': float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None,
                'bb_upper': float(bb_upper.iloc[-1]) if not pd.isna(bb_upper.iloc[-1]) else None,
                'bb_lower': float(bb_lower.iloc[-1]) if not pd.isna(bb_lower.iloc[-1]) else None,
                'current_price': float(hist['Close'].iloc[-1])
            }
        except Exception as e:
            self.logger.error(f"Technical indicator calculation failed: {e}")
            return {}
    
    async def _calculate_statistics(self, symbol: str) -> Dict[str, Any]:
        """Statistical analysis"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo")
            
            if hist.empty:
                return {}
            
            # 변동성 계산
            returns = hist['Close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)  # 연율화
            
            # 거래량 비율
            avg_volume = hist['Volume'].mean()
            current_volume = hist['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            # 가격 통계
            price_stats = {
                'mean_1m': float(hist['Close'].mean()),
                'std_1m': float(hist['Close'].std()),
                'min_1m': float(hist['Close'].min()),
                'max_1m': float(hist['Close'].max()),
                'current_vs_mean': float((hist['Close'].iloc[-1] / hist['Close'].mean() - 1) * 100)
            }
            
            # 추세 강도
            trend_strength = abs(returns.mean()) / returns.std() if returns.std() > 0 else 0
            
            return {
                'volatility_annualized': float(volatility),
                'volume_ratio': float(volume_ratio),
                'price_statistics': price_stats,
                'trend_strength': float(trend_strength)
            }
        except Exception as e:
            self.logger.error(f"Statistical analysis failed: {e}")
            return {}
    
    async def _market_comparison_analysis(self, symbol: str) -> Dict[str, Any]:
        """Market comparison analysis"""
        try:
            # SPY와 비교
            ticker = yf.Ticker(symbol)
            spy_ticker = yf.Ticker("SPY")
            
            hist = ticker.history(period="1mo")
            spy_hist = spy_ticker.history(period="1mo")
            
            if hist.empty or spy_hist.empty:
                return {}
            
            # 공통 날짜 찾기
            common_dates = hist.index.intersection(spy_hist.index)
            if len(common_dates) < 5:
                self.logger.warning("Not enough common dates")
                return {}
            
            # 수익률 계산
            symbol_returns = hist.loc[common_dates]['Close'].pct_change().dropna()
            spy_returns = spy_hist.loc[common_dates]['Close'].pct_change().dropna()
            
            # 베타 계산
            covariance = np.cov(symbol_returns, spy_returns)[0][1]
            spy_variance = np.var(spy_returns)
            beta = covariance / spy_variance if spy_variance > 0 else 0
            
            # 상관관계
            correlation = np.corrcoef(symbol_returns, spy_returns)[0][1]
            
            # 상대 성과
            symbol_total_return = (hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100
            spy_total_return = (spy_hist['Close'].iloc[-1] / spy_hist['Close'].iloc[0] - 1) * 100
            relative_performance = symbol_total_return - spy_total_return
            
            return {
                'beta': float(beta),
                'correlation_with_spy': float(correlation),
                'relative_performance_1m': float(relative_performance),
                'market_benchmark': 'SPY',
                'data_points_used': len(common_dates)
            }
        except Exception as e:
            self.logger.error(f"Market comparison analysis failed: {e}")
            return {}
    
    async def _generate_charts(self, symbol: str, analysis_data: Dict[str, Any]) -> List[str]:
        """Chart generation"""
        chart_paths = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo")
            
            if hist.empty:
                return chart_paths
            
            # 1. 가격/거래량 차트
            chart_path = await self._create_price_volume_chart(symbol, hist, timestamp)
            if chart_path:
                chart_paths.append(chart_path)
            
            # 2. 기술적 분석 차트
            chart_path = await self._create_technical_chart(symbol, hist, analysis_data, timestamp)
            if chart_path:
                chart_paths.append(chart_path)
            
            # 3. Recent trend chart
            chart_path = await self._create_recent_trend_chart(symbol, hist, timestamp)
            if chart_path:
                chart_paths.append(chart_path)
            
            # 4. 시장 비교 차트
            chart_path = await self._create_market_comparison_chart(symbol, timestamp)
            if chart_path:
                chart_paths.append(chart_path)
            
            self.logger.info(f"✅ {symbol} chart generation completed: {len(chart_paths)}")
            return chart_paths
            
        except Exception as e:
            self.logger.error(f"Chart generation failed: {e}")
            return chart_paths
    
    async def _create_price_volume_chart(self, symbol: str, hist: pd.DataFrame, timestamp: str) -> Optional[str]:
        """Create price/volume chart"""
        try:
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.1,
                subplot_titles=(f'{symbol} 가격', '거래량'),
                row_width=[0.7, 0.3]
            )
            
            # 가격 차트
            fig.add_trace(
                go.Candlestick(
                    x=hist.index,
                    open=hist['Open'],
                    high=hist['High'],
                    low=hist['Low'],
                    close=hist['Close'],
                    name='가격'
                ),
                row=1, col=1
            )
            
            # 거래량 차트
            fig.add_trace(
                go.Bar(
                    x=hist.index,
                    y=hist['Volume'],
                    name='거래량',
                    marker_color='lightblue'
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                title=f'{symbol} 가격 및 거래량',
                xaxis_rangeslider_visible=False,
                height=600
            )
            
            chart_path = os.path.join(self.charts_dir, f"{symbol}_price_volume_{timestamp}.html")
            fig.write_html(chart_path)
            return chart_path
            
        except Exception as e:
            self.logger.error(f"Price/volume chart creation failed: {e}")
            return None
    
    async def _create_technical_chart(self, symbol: str, hist: pd.DataFrame, analysis_data: Dict[str, Any], timestamp: str) -> Optional[str]:
        """Create technical analysis chart"""
        try:
            fig = go.Figure()
            
            # 가격 라인
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=hist['Close'],
                mode='lines',
                name='종가',
                line=dict(color='blue')
            ))
            
            # 이동평균선
            technical = analysis_data.get('technical_indicators', {})
            if technical.get('sma_20'):
                sma_20_series = hist['Close'].rolling(window=20).mean()
                fig.add_trace(go.Scatter(
                    x=hist.index,
                    y=sma_20_series,
                    mode='lines',
                    name='SMA 20',
                    line=dict(color='orange', dash='dash')
                ))
            
            # 볼린저 밴드
            if technical.get('bb_upper') and technical.get('bb_lower'):
                bb_period = 20
                sma = hist['Close'].rolling(window=bb_period).mean()
                std = hist['Close'].rolling(window=bb_period).std()
                bb_upper = sma + (std * 2)
                bb_lower = sma - (std * 2)
                
                fig.add_trace(go.Scatter(
                    x=hist.index,
                    y=bb_upper,
                    mode='lines',
                    name='볼린저 상단',
                    line=dict(color='red', dash='dot')
                ))
                
                fig.add_trace(go.Scatter(
                    x=hist.index,
                    y=bb_lower,
                    mode='lines',
                    name='볼린저 하단',
                    line=dict(color='red', dash='dot'),
                    fill='tonexty',
                    fillcolor='rgba(255,0,0,0.1)'
                ))
            
            fig.update_layout(
                title=f'{symbol} 기술적 분석',
                xaxis_title='날짜',
                yaxis_title='가격',
                height=500
            )
            
            chart_path = os.path.join(self.charts_dir, f"{symbol}_technical_{timestamp}.html")
            fig.write_html(chart_path)
            return chart_path
            
        except Exception as e:
            self.logger.error(f"Technical analysis chart creation failed: {e}")
            return None
    
    async def _create_recent_trend_chart(self, symbol: str, hist: pd.DataFrame, timestamp: str) -> Optional[str]:
        """Create recent trend chart"""
        try:
            # 최근 7일 데이터
            recent_data = hist.tail(7)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=recent_data.index,
                y=recent_data['Close'],
                mode='lines+markers',
                name='종가',
                line=dict(color='green', width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title=f'{symbol} 최근 7일 동향',
                xaxis_title='날짜',
                yaxis_title='가격',
                height=400
            )
            
            chart_path = os.path.join(self.charts_dir, f"{symbol}_recent_{timestamp}.html")
            fig.write_html(chart_path)
            return chart_path
            
        except Exception as e:
            self.logger.error(f"Recent trend chart creation failed: {e}")
            return None
    
    async def _create_market_comparison_chart(self, symbol: str, timestamp: str) -> Optional[str]:
        """Create market comparison chart"""
        try:
            ticker = yf.Ticker(symbol)
            spy_ticker = yf.Ticker("SPY")
            
            hist = ticker.history(period="1mo")
            spy_hist = spy_ticker.history(period="1mo")
            
            if hist.empty or spy_hist.empty:
                return None
            
            # 정규화 (첫날을 100으로)
            symbol_normalized = (hist['Close'] / hist['Close'].iloc[0]) * 100
            spy_normalized = (spy_hist['Close'] / spy_hist['Close'].iloc[0]) * 100
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=symbol_normalized,
                mode='lines',
                name=symbol,
                line=dict(color='blue')
            ))
            
            fig.add_trace(go.Scatter(
                x=spy_hist.index,
                y=spy_normalized,
                mode='lines',
                name='SPY (시장)',
                line=dict(color='red')
            ))
            
            fig.update_layout(
                title=f'{symbol} vs 시장(SPY) 비교',
                xaxis_title='날짜',
                yaxis_title='정규화된 가격 (시작일=100)',
                height=400
            )
            
            chart_path = os.path.join(self.charts_dir, f"{symbol}_comparison_{timestamp}.html")
            fig.write_html(chart_path)
            return chart_path
            
        except Exception as e:
            self.logger.error(f"Market comparison chart creation failed: {e}")
            return None
    
    async def _analyze_event_impact(self, event_data: Dict[str, Any], analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Event impact analysis"""
        try:
            event_type = event_data.get('event_type', 'unknown')
            severity = event_data.get('severity', 'low')
            
            # 기본 영향 분석
            impact_analysis = {
                'event_type': event_type,
                'severity': severity,
                'market_impact': 'moderate',
                'technical_outlook': 'neutral',
                'risk_level': 'medium'
            }
            
            # 기술적 지표 기반 전망
            technical = analysis_data.get('technical_indicators', {})
            if technical:
                rsi = technical.get('rsi', 50)
                current_price = technical.get('current_price', 0)
                bb_upper = technical.get('bb_upper', 0)
                bb_lower = technical.get('bb_lower', 0)
                
                # RSI 기반 판단
                if rsi > 70:
                    impact_analysis['technical_outlook'] = 'overbought'
                elif rsi < 30:
                    impact_analysis['technical_outlook'] = 'oversold'
                
                # 볼린저 밴드 기반 판단
                if bb_upper and bb_lower and current_price:
                    if current_price > bb_upper:
                        impact_analysis['technical_outlook'] = 'breakout_upward'
                    elif current_price < bb_lower:
                        impact_analysis['technical_outlook'] = 'breakout_downward'
            
            # 통계 기반 리스크 평가
            stats = analysis_data.get('statistics', {})
            if stats:
                volatility = stats.get('volatility_annualized', 0)
                if volatility > 0.3:  # above 30%
                    impact_analysis['risk_level'] = 'high'
                elif volatility < 0.15:  # below 15%
                    impact_analysis['risk_level'] = 'low'
            
            return impact_analysis
            
        except Exception as e:
            self.logger.error(f"Event impact analysis failed: {e}")
            return {
                'event_type': 'unknown',
                'severity': 'low',
                'market_impact': 'unknown',
                'technical_outlook': 'neutral',
                'risk_level': 'medium'
            }
