"""
Visualization utilities module
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from typing import Dict, List, Any, Optional
import streamlit as st


class ChartGenerator:
    """Chart generation class"""
    
    def __init__(self):
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e', 
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff7f0e',
            'info': '#17a2b8'
        }
    
    def create_stock_price_chart(self, stock_data: Dict[str, Any], symbols: List[str] = None) -> go.Figure:
        """Create stock price chart"""
        if not symbols:
            symbols = list(stock_data.keys())[:5]
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Stock Price Changes', 'Volume'),
            vertical_spacing=0.1,
            row_heights=[0.7, 0.3]
        )
        
        # Price chart
        for i, symbol in enumerate(symbols):
            if symbol in stock_data:
                data = stock_data[symbol]
                color = list(self.colors.values())[i % len(self.colors)]
                
                fig.add_trace(
                    go.Scatter(
                        x=[symbol],
                        y=[data.get('current_price', 0)],
                        mode='markers+text',
                        name=f"{data.get('name', symbol)}",
                        text=[f"${data.get('current_price', 0):.2f}"],
                        textposition="top center",
                        marker=dict(
                            size=15,
                            color=color,
                            line=dict(width=2, color='white')
                        )
                    ),
                    row=1, col=1
                )
                
                # Volume chart
                fig.add_trace(
                    go.Bar(
                        x=[symbol],
                        y=[data.get('volume', 0)],
                        name=f"{symbol} Volume",
                        marker_color=color,
                        showlegend=False
                    ),
                    row=2, col=1
                )
        
        fig.update_layout(
            title="Major Stocks Overview",
            height=600,
            showlegend=True,
            template="plotly_white"
        )
        
        fig.update_xaxes(title_text="Symbol", row=2, col=1)
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        
        return fig
    
    def create_market_overview_chart(self, stock_data: Dict[str, Any]) -> go.Figure:
        """Create market overview chart"""
        # Extract major index data
        indices = {'^GSPC': 'S&P 500', '^DJI': 'Dow Jones', '^IXIC': 'Nasdaq', '^VIX': 'VIX'}
        
        index_data = []
        for symbol, name in indices.items():
            if symbol in stock_data:
                data = stock_data[symbol]
                index_data.append({
                    'Index': name,
                    'Value': data.get('current_price', 0),
                    'Change': data.get('change_percent', 0),
                    'Color': 'green' if data.get('change_percent', 0) >= 0 else 'red'
                })
        
        if not index_data:
            return go.Figure()
        
        df = pd.DataFrame(index_data)
        
        fig = go.Figure()
        
        # Index value chart
        fig.add_trace(
            go.Bar(
                x=df['Index'],
                y=df['Value'],
                name='Index Value',
                marker_color=df['Color'],
                text=[f"{val:.2f}" for val in df['Value']],
                textposition='outside'
            )
        )
        
        fig.update_layout(
            title="Major Indices Overview",
            xaxis_title="Index",
            yaxis_title="Value",
            height=400,
            template="plotly_white"
        )
        
        return fig
    
    def create_change_percentage_chart(self, stock_data: Dict[str, Any]) -> go.Figure:
        """Create change percentage chart"""
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
        
        change_data = []
        for symbol in symbols:
            if symbol in stock_data:
                data = stock_data[symbol]
                change_data.append({
                    'Symbol': data.get('name', symbol),
                    'Change%': data.get('change_percent', 0),
                    'Color': 'green' if data.get('change_percent', 0) >= 0 else 'red'
                })
        
        if not change_data:
            return go.Figure()
        
        df = pd.DataFrame(change_data)
        
        fig = go.Figure()
        
        fig.add_trace(
            go.Bar(
                x=df['Symbol'],
                y=df['Change%'],
                name='Change Rate (%)',
                marker_color=df['Color'],
                text=[f"{val:.2f}%" for val in df['Change%']],
                textposition='outside'
            )
        )
        
        fig.update_layout(
            title="Major Stock Change Rate",
            xaxis_title="Symbol",
            yaxis_title="Change Rate (%)",
            height=400,
            template="plotly_white"
        )
        
        # Add zero line
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        
        return fig
    
    def create_sector_performance_chart(self, stock_data: Dict[str, Any]) -> go.Figure:
        """Create sector performance chart"""
        sector_data = {}
        
        for symbol, data in stock_data.items():
            sector = data.get('sector', 'Unknown')
            if sector != 'Unknown' and sector:
                if sector not in sector_data:
                    sector_data[sector] = []
                sector_data[sector].append(data.get('change_percent', 0))
        
        # Calculate sector averages
        sector_avg = {sector: np.mean(changes) for sector, changes in sector_data.items()}
        
        if not sector_avg:
            return go.Figure()
        
        sectors = list(sector_avg.keys())
        changes = list(sector_avg.values())
        colors = ['green' if change >= 0 else 'red' for change in changes]
        
        fig = go.Figure()
        
        fig.add_trace(
            go.Bar(
                x=sectors,
                y=changes,
                name='Sector Avg Change Rate',
                marker_color=colors,
                text=[f"{val:.2f}%" for val in changes],
                textposition='outside'
            )
        )
        
        fig.update_layout(
            title="Sector Performance",
            xaxis_title="Sector",
            yaxis_title="Average Change Rate (%)",
            height=400,
            template="plotly_white"
        )
        
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        
        return fig
    
    def create_vix_fear_greed_gauge(self, economic_data: Dict[str, Any]) -> go.Figure:
        """Create VIX fear/greed gauge chart"""
        vix_value = economic_data.get('VIX', {}).get('value', 20)
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = vix_value,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "VIX Fear Index"},
            delta = {'reference': 20},
            gauge = {
                'axis': {'range': [None, 50]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 20], 'color': "lightgreen"},
                    {'range': [20, 30], 'color': "yellow"},
                    {'range': [30, 50], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 30
                }
            }
        ))
        
        fig.update_layout(height=300)
        
        return fig
    
    def create_market_cap_pie_chart(self, stock_data: Dict[str, Any]) -> go.Figure:
        """Create market cap pie chart"""
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
        
        cap_data = []
        for symbol in symbols:
            if symbol in stock_data:
                data = stock_data[symbol]
                market_cap = data.get('market_cap', 0)
                if market_cap > 0:
                    cap_data.append({
                        'Symbol': data.get('name', symbol),
                        'MarketCap': market_cap / 1e12
                    })
        
        if not cap_data:
            return go.Figure()
        
        df = pd.DataFrame(cap_data)
        
        fig = go.Figure(data=[go.Pie(
            labels=df['Symbol'],
            values=df['MarketCap'],
            hole=.3,
            textinfo='label+percent',
            textposition='outside'
        )])
        
        fig.update_layout(
            title="Major Stock Market Cap Share",
            height=400,
            showlegend=True
        )
        
        return fig


class NewsImageGenerator:
    """News image generation class"""
    
    def __init__(self):
        self.deepseek_client = None
    
    def generate_article_illustration(self, article_content: str, article_type: str = "market_summary") -> Optional[str]:
        """Generate illustration based on article content"""
        # In production, uses AWS Bedrock's image generation model
        # Here we return placeholder image URL
        
        image_prompts = {
            "market_summary": "https://via.placeholder.com/600x300/1f77b4/ffffff?text=Market+Analysis",
            "stock_focus": "https://via.placeholder.com/600x300/ff7f0e/ffffff?text=Stock+Focus",
            "economic_outlook": "https://via.placeholder.com/600x300/2ca02c/ffffff?text=Economic+Outlook",
            "sector_analysis": "https://via.placeholder.com/600x300/d62728/ffffff?text=Sector+Analysis"
        }
        
        return image_prompts.get(article_type, image_prompts["market_summary"])
    
    def create_wordcloud_from_article(self, article_content: str) -> Optional[str]:
        """Generate word cloud from article content"""
        try:
            from wordcloud import WordCloud
            import matplotlib.pyplot as plt
            import io
            import base64
            
            # Korean font config (system dependent)
            wordcloud = WordCloud(
                width=800, 
                height=400, 
                background_color='white',
                max_words=100,
                colormap='viridis'
            ).generate(article_content)
            
            # Encode image to base64
            img_buffer = io.BytesIO()
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.tight_layout(pad=0)
            plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
            plt.close()
            
            img_buffer.seek(0)
            img_str = base64.b64encode(img_buffer.read()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            st.error(f"Word cloud generation error: {str(e)}")
            return None


class AdGenerator:
    """Ad generation class"""
    
    def __init__(self):
        self.ad_templates = {
            "investment": [
                {
                    "title": "Smart Investment Platform",
                    "description": "Experience better returns with AI-based portfolio management",
                    "cta": "Try Free",
                    "image": "https://via.placeholder.com/300x200/007cba/ffffff?text=Smart+Investment",
                    "link": "#"
                },
                {
                    "title": "Robo Advisor",
                    "description": "Professional-grade asset management, automated",
                    "cta": "Start Now",
                    "image": "https://via.placeholder.com/300x200/28a745/ffffff?text=Robo+Advisor",
                    "link": "#"
                }
            ],
            "trading": [
                {
                    "title": "Real-Time Trading",
                    "description": "Start stock investing with zero commission",
                    "cta": "Open Account",
                    "image": "https://via.placeholder.com/300x200/dc3545/ffffff?text=Real+Time+Trading",
                    "link": "#"
                },
                {
                    "title": "Premium Charts",
                    "description": "Advanced analysis tools for professional traders",
                    "cta": "Free Trial",
                    "image": "https://via.placeholder.com/300x200/6f42c1/ffffff?text=Premium+Charts",
                    "link": "#"
                }
            ],
            "education": [
                {
                    "title": "Investment Courses",
                    "description": "Systematic investment learning from basics to advanced",
                    "cta": "Enroll Now",
                    "image": "https://via.placeholder.com/300x200/fd7e14/ffffff?text=Investment+Education",
                    "link": "#"
                },
                {
                    "title": "Fundamental Agent Subscription",
                    "description": "Key economic news delivered every morning",
                    "cta": "Subscribe",
                    "image": "https://via.placeholder.com/300x200/20c997/ffffff?text=Fundamental+Agent",
                    "link": "#"
                }
            ]
        }
    
    def generate_contextual_ads(self, article_content: str, article_tags: List[str]) -> List[Dict[str, str]]:
        """Generate contextual ads based on article content"""
        ads = []
        
        # Analyze article content and tags
        content_lower = article_content.lower()
        tags_lower = [tag.lower() for tag in article_tags]
        
        # Check for investment-related keywords
        investment_keywords = ['investment', 'portfolio', 'asset', 'return', 'invest', 'fund']
        trading_keywords = ['trade', 'trading', 'chart', 'stock', 'broker', 'commission']
        education_keywords = ['analysis', 'outlook', 'analysis', 'forecast', 'trend']
        
        # Determine ad category by keyword matching
        if any(keyword in content_lower or keyword in ' '.join(tags_lower) for keyword in investment_keywords):
            ads.extend(self.ad_templates["investment"])
        
        if any(keyword in content_lower or keyword in ' '.join(tags_lower) for keyword in trading_keywords):
            ads.extend(self.ad_templates["trading"])
        
        if any(keyword in content_lower or keyword in ' '.join(tags_lower) for keyword in education_keywords):
            ads.extend(self.ad_templates["education"])
        
        # Default ads (if no match)
        if not ads:
            ads = self.ad_templates["investment"] + self.ad_templates["education"]
        
        # Return max 3 ads
        return ads[:3]
    
    def create_ad_html(self, ad: Dict[str, str]) -> str:
        """Create ad HTML"""
        return f"""
        <div style="
            border: 1px solid #ddd; 
            border-radius: 8px; 
            padding: 15px; 
            margin: 10px 0; 
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="display: flex; align-items: center;">
                <img src="{ad['image']}" style="
                    width: 80px; 
                    height: 60px; 
                    border-radius: 4px; 
                    margin-right: 15px;
                    object-fit: cover;
                " />
                <div style="flex: 1;">
                    <h4 style="margin: 0 0 5px 0; color: #333; font-size: 16px;">{ad['title']}</h4>
                    <p style="margin: 0 0 10px 0; color: #666; font-size: 14px;">{ad['description']}</p>
                    <a href="{ad['link']}" style="
                        background-color: #007cba; 
                        color: white; 
                        padding: 6px 12px; 
                        text-decoration: none; 
                        border-radius: 4px; 
                        font-size: 12px;
                        display: inline-block;
                    ">{ad['cta']}</a>
                </div>
            </div>
        </div>
        """
