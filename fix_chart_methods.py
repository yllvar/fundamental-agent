#!/usr/bin/env python3
"""
차트 생성 메서드 수정 - 한글을 영어로 변경
"""

chart_methods_code = '''
    async def _create_price_volume_chart(self, symbol: str, data: pd.DataFrame, filename: str) -> str:
        """Price and Volume Chart Generation"""
        
        try:
            # Create subplots
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.1,
                subplot_titles=(f'{symbol} Price', 'Volume'),
                row_width=[0.7, 0.3]
            )
            
            # Candlestick chart
            fig.add_trace(
                go.Candlestick(
                    x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name='Price'
                ),
                row=1, col=1
            )
            
            # Volume chart
            colors = ['red' if close < open else 'green' 
                     for close, open in zip(data['Close'], data['Open'])]
            
            fig.add_trace(
                go.Bar(
                    x=data.index,
                    y=data['Volume'],
                    name='Volume',
                    marker_color=colors
                ),
                row=2, col=1
            )
            
            # Layout update
            fig.update_layout(
                title=f'{symbol} Price and Volume Analysis',
                xaxis_title='Date',
                yaxis_title='Price ($)',
                yaxis2_title='Volume',
                template='plotly_white',
                height=600,
                showlegend=False
            )
            
            # Save chart
            output_dir = "output/charts"
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, filename)
            fig.write_html(filepath)
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Price volume chart creation failed: {e}")
            return ""
    
    async def _create_technical_indicators_chart(self, symbol: str, data: pd.DataFrame, 
                                               indicators: Dict[str, Any], filename: str) -> str:
        """Technical Indicators Chart Generation"""
        
        try:
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.1,
                subplot_titles=(f'{symbol} Price + Moving Averages', 'MACD', 'RSI')
            )
            
            # Price + Moving Averages
            fig.add_trace(
                go.Scatter(x=data.index, y=data['Close'], name='Close Price', line=dict(color='blue')),
                row=1, col=1
            )
            
            # Calculate and add moving averages
            sma_20 = data['Close'].rolling(20).mean()
            sma_50 = data['Close'].rolling(50).mean()
            
            fig.add_trace(
                go.Scatter(x=data.index, y=sma_20, name='SMA 20', line=dict(color='orange')),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=data.index, y=sma_50, name='SMA 50', line=dict(color='red')),
                row=1, col=1
            )
            
            # MACD calculation and plot
            ema_12 = data['Close'].ewm(span=12).mean()
            ema_26 = data['Close'].ewm(span=26).mean()
            macd = ema_12 - ema_26
            macd_signal = macd.ewm(span=9).mean()
            
            fig.add_trace(
                go.Scatter(x=data.index, y=macd, name='MACD', line=dict(color='blue')),
                row=2, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=data.index, y=macd_signal, name='Signal', line=dict(color='red')),
                row=2, col=1
            )
            
            # RSI calculation and plot
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            fig.add_trace(
                go.Scatter(x=data.index, y=rsi, name='RSI', line=dict(color='purple')),
                row=3, col=1
            )
            
            # Add RSI reference lines
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
            
            # Layout update
            fig.update_layout(
                title=f'{symbol} Technical Analysis',
                template='plotly_white',
                height=800,
                showlegend=True
            )
            
            # Save chart
            output_dir = "output/charts"
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, filename)
            fig.write_html(filepath)
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Technical indicators chart creation failed: {e}")
            return ""
    
    async def _create_recent_detail_chart(self, symbol: str, data: pd.DataFrame, filename: str) -> str:
        """Recent 5-Day Detail Chart Generation"""
        
        try:
            fig = go.Figure()
            
            # Candlestick chart for recent data
            fig.add_trace(
                go.Candlestick(
                    x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name='Price'
                )
            )
            
            # Add volume as secondary y-axis
            fig.add_trace(
                go.Bar(
                    x=data.index,
                    y=data['Volume'],
                    name='Volume',
                    yaxis='y2',
                    opacity=0.3
                )
            )
            
            # Layout with secondary y-axis
            fig.update_layout(
                title=f'{symbol} Recent 5-Day Detailed Analysis',
                xaxis_title='Time',
                yaxis_title='Price ($)',
                yaxis2=dict(
                    title='Volume',
                    overlaying='y',
                    side='right'
                ),
                template='plotly_white',
                height=500
            )
            
            # Save chart
            output_dir = "output/charts"
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, filename)
            fig.write_html(filepath)
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Recent detail chart creation failed: {e}")
            return ""
    
    async def _create_market_comparison_chart(self, symbol: str, comparison_data: Dict[str, Any], filename: str) -> str:
        """Market Comparison Chart Generation"""
        
        try:
            fig = go.Figure()
            
            # Create comparison data visualization
            categories = ['Beta', 'Correlation with SPY', 'Relative Performance (%)']
            values = [
                comparison_data.get('beta', 1.0),
                comparison_data.get('correlation_with_spy', 0.0),
                comparison_data.get('relative_performance_1m', 0.0)
            ]
            
            fig.add_trace(
                go.Bar(
                    x=categories,
                    y=values,
                    name=f'{symbol} vs Market',
                    marker_color=['blue', 'green', 'red']
                )
            )
            
            # Add reference lines
            fig.add_hline(y=1.0, line_dash="dash", line_color="gray", 
                         annotation_text="Market Beta = 1.0")
            
            # Layout update
            fig.update_layout(
                title=f'{symbol} Market Comparison Analysis',
                xaxis_title='Metrics',
                yaxis_title='Values',
                template='plotly_white',
                height=400
            )
            
            # Save chart
            output_dir = "output/charts"
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, filename)
            fig.write_html(filepath)
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Market comparison chart creation failed: {e}")
            return ""
'''

print("차트 생성 메서드 코드가 준비되었습니다.")
print("이 코드를 data_analysis_agent.py에 적용해야 합니다.")
