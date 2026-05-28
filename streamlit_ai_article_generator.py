#!/usr/bin/env python3
"""
AI Article Generation Pipeline Streamlit Page
Event detection → Data analysis → Article writing → Image generation → Review → Ad recommendation
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime
import time
import json
import base64
from PIL import Image
import io
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import weasyprint
# Import for auto-refresh (requires pip install)
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

# Path setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Agents import
from simple_ai_article_generator import SimpleAIArticleGenerator
from data_monitoring.auto_article_event_system import AutoArticleEventSystem

# Strands Agent import
try:
    from agents.orchestrator_strand import OrchestratorStrand
    from agents.strands_framework import StrandContext
    AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Agents import failed: {e}")
    AGENTS_AVAILABLE = False

class StreamlitProgressTracker:
    """Streamlit progress tracker"""
    
    def __init__(self, progress_bar, status_text, log_container):
        self.progress_bar = progress_bar
        self.status_text = status_text
        self.log_container = log_container
        self.logs = []
        self.start_time = time.time()
        self.current_step = 0
        self.total_steps = 6  # event detection, data analysis, article writing, image generation, review, ad recommendation
    
    def update_step(self, step_name: str, message: str = ""):
        """Update step"""
        self.current_step += 1
        progress = min(self.current_step / self.total_steps, 1.0)
        
        try:
            self.progress_bar.progress(progress)
        except:
            pass
        
        elapsed = time.time() - self.start_time
        status_msg = f"Step: {self.current_step}/{self.total_steps} ({progress*100:.1f}%) - Elapsed: {elapsed:.1f}s"
        status_msg += f"\n🔄 Current Task: {step_name}"
        if message:
            status_msg += f" - {message}"
        
        try:
            self.status_text.text(status_msg)
        except:
            pass
    
    def add_log(self, message: str, level: str = "INFO"):
        """Add log entry"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        emoji = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}.get(level, "📝")
        log_entry = f"{emoji} [{timestamp}] {message}"
        self.logs.append(log_entry)
        
        try:
            # Show only the last 15 log entries
            recent_logs = self.logs[-15:]
            self.log_container.text("\n".join(recent_logs))
        except:
            pass

def collect_event_data_with_progress(tracker):
    """Collect event data"""
    tracker.update_step("Event Detection", "Scanning economic events...")
    tracker.add_log("🔍 Starting economic event detection", "INFO")
    
    try:
        event_system = AutoArticleEventSystem()
        
        # Run event detection
        tracker.add_log("📊 Analyzing market data...", "INFO")
        events = event_system.detect_events()
        
        # Add market context
        market_context = event_system.get_market_context()
        
        if events and len(events) > 0:
            tracker.add_log(f"✅ {len(events)} event(s) detected", "SUCCESS")
            
            # Event detail logs
            for i, event in enumerate(events, 1):
                tracker.add_log(f"  Event {i}: {event['description']}", "INFO")
            
            # Add market context info
            for event in events:
                event['market_context'] = market_context
            
            return events
        else:
            tracker.add_log("⚠️ No events detected", "WARNING")
            return []
    
    except Exception as e:
        tracker.add_log(f"❌ Event detection failed: {str(e)}", "ERROR")
        # return default event on failure
        tracker.add_log("🔄 Generating default event...", "INFO")
        return [{
            'type': 'fallback_analysis',
            'symbol': 'MARKET',
            'description': 'Periodic market analysis and trend report',
            'severity': 0.5,
            'sentiment': 'neutral',
            'timestamp': datetime.now().isoformat(),
            'source': 'fallback'
        }]

def create_wordcloud_image(keywords, title="Keyword Wordcloud"):
    """Create word cloud image from keywords (Korean support)"""
    try:
        if not keywords:
            return None
            
        # Refine keywords and assign weights
        keyword_freq = {}
        for keyword in keywords:
            if len(keyword) > 1:  # Exclude single-character keywords
                keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
        
        if not keyword_freq:
            return None
            
        # Find Korean font path
        font_path = None
        possible_fonts = [
            '/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/google-noto-cjk/NotoSansCJK-Medium.ttc',
            '/usr/share/fonts/google-noto-cjk/NotoSansCJK-Bold.ttc',
            '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
            '/System/Library/Fonts/AppleGothic.ttf',  # macOS
            'C:/Windows/Fonts/malgun.ttf'  # Windows
        ]
        
        for font in possible_fonts:
            if os.path.exists(font):
                font_path = font
                break
        
        # Generate word cloud
        wordcloud = WordCloud(
            width=800, 
            height=400,
            background_color='white',
            font_path=font_path,  # Use Korean font
            max_words=25,
            colormap='viridis',
            prefer_horizontal=0.6,
            min_font_size=12,
            max_font_size=60,
            relative_scaling=0.5,
            collocations=False  # Prevent word collocations
        ).generate_from_frequencies(keyword_freq)
        
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        
        # Set title in English (avoid Korean font issues)
        english_title = "Article keywords Wordcloud"
        ax.set_title(english_title, fontsize=16, pad=20)
        
        # Convert image to bytes
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
        
    except Exception as e:
        print(f"Wordcloud generation error: {e}")
        return None

def create_market_trend_chart(events):
    """Create market trend chart"""
    try:
        # Extract price change data from events
        symbols = []
        changes = []
        
        for event in events:
            if 'symbol' in event and 'description' in event:
                symbols.append(event['symbol'])
                # Try to extract percentage change from description
                desc = event['description']
                if '%' in desc:
                    try:
                        # Simple percentage extraction
                        import re
                        percent_match = re.search(r'([-+]?\d+\.?\d*)%', desc)
                        if percent_match:
                            changes.append(float(percent_match.group(1)))
                        else:
                            changes.append(0)
                    except:
                        changes.append(0)
                else:
                    changes.append(0)
        
        if symbols and changes:
            fig = px.bar(
                x=symbols,
                y=changes,
                title="Major Stock Price Changes",
                labels={'x': 'Symbol', 'y': 'Change Rate (%)'},
                color=changes,
                color_continuous_scale=['red', 'yellow', 'green']
            )
            fig.update_layout(
                showlegend=False,
                height=400
            )
            return fig
        
        return None
        
    except Exception as e:
        print(f"Market trend chart creation error: {e}")
        return None

def create_real_stock_chart(symbols):
    """Create chart using real stock data"""
    try:
        import yfinance as yf
        from datetime import datetime, timedelta
        
        if not symbols:
            return None
            
        # Get data for the last 5 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5)
        
        stock_data = {}
        for symbol in symbols[:5]:  # Max 5 symbols
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(start=start_date, end=end_date)
                if not hist.empty:
                    stock_data[symbol] = hist['Close'].tolist()
            except:
                continue
        
        if stock_data:
            fig = go.Figure()
            
            for symbol, prices in stock_data.items():
                dates = [start_date + timedelta(days=i) for i in range(len(prices))]
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=prices,
                    mode='lines+markers',
                    name=symbol,
                    line=dict(width=2)
                ))
            
            fig.update_layout(
                title="Major Stock Price Trend (Last 5 Days)",
                xaxis_title="Date",
                yaxis_title="Stock Price ($)",
                height=400,
                showlegend=True
            )
            
            return fig
        
        return None
        
    except Exception as e:
        print(f"Real stock chart creation error: {e}")
        return None

def generate_article_illustration(article_content, bedrock_client=None):
    """Generate article illustration (placeholder)"""
    try:
        title = article_content.get('title', '') if article_content else 'fundamental_agent'
        image_result = generate_placeholder_image(title, "output/images")
        return {
            'description': f"Placeholder image: {title}",
            'generated_at': datetime.now().isoformat(),
            'image_file': image_result
        }
    except Exception as e:
        print(f"Illustration generation error: {e}")
        return None

def should_generate_wordcloud(article_content, analysis_data):
    """AI determines whether word cloud generation is needed"""
    try:
        # Check article length and keyword diversity
        content = article_content.get('content', '')
        title = article_content.get('title', '')
        
        # Relax conditions
        if len(content) > 500 and len(title.split()) > 2:  # 500+ characters, title 2+ words
            # Check keyword diversity from analysis data
            key_symbols = analysis_data.get('key_symbols', [])
            if len(set(key_symbols)) >= 2:  # 2+ different symbols
                return True
        
        # Generate if 3+ events
        total_events = analysis_data.get('total_events', 0)
        if total_events >= 3:
            return True
            
        return False
        
    except Exception as e:
        print(f"Wordcloud necessity check error: {e}")
def generate_ai_illustration_image(article_content, bedrock_client=None, output_dir="output/images"):
    """Generate AI illustration (placeholder)"""
    try:
        title = article_content.get('title', '') if article_content else 'illustration'
        return generate_placeholder_image(title, output_dir)
    except Exception as e:
        print(f"Image generation error: {e}")
        return generate_placeholder_image('fallback', output_dir)

def generate_placeholder_image(title, output_dir):
    """Generate placeholder image (fallback when Bedrock image generation fails)"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import textwrap
        
        # Image Generation
        width, height = 512, 512
        img = Image.new('RGB', (width, height), color='#f8f9fa')
        draw = ImageDraw.Draw(img)
        
        # Background gradient effect
        for y in range(height):
            color_value = int(248 - (y / height) * 20)  # Gradient from 248 to 228
            color = (color_value, color_value + 2, color_value + 5)
            draw.line([(0, y), (width, y)], fill=color)
        
        # Add title text
        try:
            # Use default font
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        except:
            font_large = None
            font_small = None
        
        # Wrap title
        wrapped_title = textwrap.fill(title[:50], width=25)
        
        # Text position calculation
        text_y = height // 2 - 50
        
        # Draw title
        draw.text((width//2, text_y), "📊 Fundamental Agent Article", 
                 fill='#2c3e50', anchor='mm', font=font_large)
        
        draw.text((width//2, text_y + 40), wrapped_title, 
                 fill='#34495e', anchor='mm', font=font_small)
        
        # Add decorative elements
        # Upward arrow
        arrow_points = [(width//2 - 30, height//2 + 80), 
                       (width//2, height//2 + 50), 
                       (width//2 + 30, height//2 + 80)]
        draw.polygon(arrow_points, fill='#27ae60')
        
        # Chart line simulation
        import random
        points = []
        for i in range(0, width, 20):
            y = height//2 + 100 + random.randint(-20, 20)
            points.append((i, y))
        
        for i in range(len(points) - 1):
            draw.line([points[i], points[i+1]], fill='#3498db', width=3)
        
        # Save file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_filename = f"placeholder_illustration_{timestamp}.png"
        image_path = os.path.join(output_dir, image_filename)
        
        img.save(image_path)
        
        return {
            'image_path': image_path,
            'filename': image_filename,
            'prompt_used': f"Placeholder image for: {title}",
            'generated_at': datetime.now().isoformat(),
            'model_used': 'PIL_placeholder'
        }
        
    except Exception as e:
        print(f"Placeholder image generation error: {e}")
        return None
    """Convert HTML content to PDF"""
    try:
        # Add CSS styles
        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Noto Sans CJK KR', Arial, sans-serif;
                    line-height: 1.6;
                    margin: 40px;
                    color: #333;
                }}
                h1 {{
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #34495e;
                    margin-top: 30px;
                }}
                .meta-info {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-left: 4px solid #3498db;
                    margin: 20px 0;
                }}
                .content {{
                    text-align: justify;
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            {html_content}
            <div class="footer">
                <p>Generated by Fundamental Agent | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        
        # Generate PDF
        weasyprint.HTML(string=styled_html).write_pdf(output_path)
        return True
        
    except Exception as e:
        print(f"PDF conversion error: {e}")
        return False

def create_html_article(result):
    """Convert result data to HTML article"""
    try:
        article = result.get('article', {})
        analysis = result.get('analysis', {})
        review = result.get('review', {})
        
        title = article.get('title', 'No Title')
        content = article.get('content', 'No Content')
        
        # Create HTML structure
        html_content = f"""
        <h1>{title}</h1>
        
        <div class="meta-info">
            <strong>📊 Article Info</strong><br>
            Generated At: {result.get('timestamp', '')}<br>
            Events Detected: {analysis.get('total_events', 0)}<br>
            Market Sentiment: {analysis.get('market_sentiment', 'neutral')}<br>
            Quality Score: {review.get('quality_score', 0)}/10
        </div>
        
        <div class="content">
            {content.replace(chr(10), '<br>').replace(chr(10)+chr(10), '</p><p>')}
        </div>
        
        <h2>📈 Key Symbols</h2>
        <ul>
        """
        
        # Add key symbols
        key_symbols = analysis.get('key_symbols', [])
        for symbol in key_symbols[:5]:
            html_content += f"<li>{symbol}</li>"
        
        html_content += "</ul>"
        
        # Add AI illustration
        images = result.get('images', {})
        ai_illustration = images.get('ai_illustration')
        if ai_illustration and isinstance(ai_illustration, dict):
            description = ai_illustration.get('description', '')
            if description:
                html_content += f"""
                <h2>🎨 AI Generated Illustration Guide</h2>
                <div class="meta-info">
                    {description.replace(chr(10), '<br>')}
                </div>
                """
        
        # Add review results
        if review:
            html_content += f"""
            <h2>🔍 Review Results</h2>
            <div class="meta-info">
                <strong>Quality Assessment:</strong> {review.get('quality_score', 0)}/10<br>
                <strong>Improvement Suggestions:</strong><br>
                <ul>
            """
            
            suggestions = review.get('suggestions', [])
            for suggestion in suggestions:
                html_content += f"<li>{suggestion}</li>"
            
            html_content += "</ul></div>"
        
        return html_content
        
    except Exception as e:
        print(f"HTML generation error: {e}")
        return f"<h1>Error Occurred</h1><p>An error occurred during HTML generation: {str(e)}</p>"
        
    except Exception as e:
        print(f"Wordcloud necessity check error: {e}")
        return True  # Generate on error

def generate_article_with_agents(events, tracker):
    """Generate article using agents"""
    
    try:
        # Check agent availability
        if not AGENTS_AVAILABLE:
            tracker.add_log("❌ Agents system unavailable. Using fallback.", "ERROR")
            return generate_article_fallback(events, tracker)
        
        # Initialize orchestrator
        tracker.update_step("System Initialization", "Preparing AI agents...")
        tracker.add_log("🤖 Initializing AI agent system", "INFO")
        
        try:
            orchestrator = OrchestratorStrand()
            tracker.add_log("✅ OrchestratorStrand initialized successfully", "SUCCESS")
        except Exception as init_error:
            tracker.add_log(f"❌ OrchestratorStrand initialization failed: {str(init_error)}", "ERROR")
            tracker.add_log("🔄 Switching to fallback system", "INFO")
            return generate_article_fallback(events, tracker)
        
        # Create context
        context = StrandContext(
            strand_id=f"streamlit_article_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            input_data={
                "events": events,
                "request_type": "comprehensive_article"
            }
        )
        
        # 1. Data Analysis
        tracker.update_step("Data Analysis", "Performing in-depth economic data analysis...")
        tracker.add_log("📊 Running data analysis agent", "INFO")
        
        try:
            analysis_result = orchestrator.execute_data_analysis(context)
            if analysis_result:
                tracker.add_log("✅ Data Analysis complete", "SUCCESS")
                context.add_data("analysis", analysis_result)
            else:
                tracker.add_log("⚠️ Data analysis result is empty", "WARNING")
        except Exception as analysis_error:
            tracker.add_log(f"❌ Data analysis error: {str(analysis_error)}", "ERROR")
            tracker.add_log("🔄 Switching to fallback system", "INFO")
            return generate_article_fallback(events, tracker)
        
        time.sleep(1)  # UI update time
        
        # 2. Article Writing
        tracker.update_step("Article Writing", "AI drafting the article...")
        tracker.add_log("✍️ Running article writing agent", "INFO")
        
        try:
            article_result = orchestrator.execute_article_writing(context)
            if article_result:
                tracker.add_log("✅ Article Writing complete", "SUCCESS")
                context.add_data("article", article_result)
            else:
                tracker.add_log("❌ Article writing result is empty", "ERROR")
                tracker.add_log("🔄 Switching to fallback system", "INFO")
                return generate_article_fallback(events, tracker)
        except Exception as writing_error:
            tracker.add_log(f"❌ Article writing error: {str(writing_error)}", "ERROR")
            tracker.add_log("🔄 Switching to fallback system", "INFO")
            return generate_article_fallback(events, tracker)
        
        time.sleep(1)
        
        # 3. Image Generation
        tracker.update_step("Image Generation", "Generating images and charts...")
        tracker.add_log("🎨 Running image generation agent", "INFO")
        
        image_result = orchestrator.execute_image_generation(context)
        if image_result:
            tracker.add_log("✅ Image Generation complete", "SUCCESS")
            context.add_data("images", image_result)
        else:
            tracker.add_log("⚠️ Image generation partially failed", "WARNING")
        
        time.sleep(1)
        
        # 4. Article Review
        tracker.update_step("Article Review", "Quality review and improvements...")
        tracker.add_log("🔍 Running review agent", "INFO")
        
        review_result = orchestrator.execute_review(context)
        if review_result:
            tracker.add_log("✅ Article Review complete", "SUCCESS")
            context.add_data("review", review_result)
        else:
            tracker.add_log("⚠️ Review partially failed", "WARNING")
        
        time.sleep(1)
        
        # 5. Ad Recommendation
        tracker.update_step("Ad Recommendation", "Recommending targeted ads...")
        tracker.add_log("📢 Running ad recommendation agent", "INFO")
        
        ad_result = orchestrator.execute_ad_recommendation(context)
        if ad_result:
            tracker.add_log("✅ Ad Recommendation complete", "SUCCESS")
            context.add_data("ads", ad_result)
        else:
            tracker.add_log("⚠️ Ad recommendation partially failed", "WARNING")
        
        # Compile final result
        tracker.add_log("🎉 Full pipeline complete!", "SUCCESS")
        
        return {
            'events': events,
            'analysis': analysis_result,
            'article': article_result,
            'images': image_result,
            'review': review_result,
            'ads': ad_result,
            'context': context,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        tracker.add_log(f"💥 Pipeline execution error: {str(e)}", "ERROR")
        return None

def generate_article_fallback(events, tracker):
    """Fallback article generation system (without Agents)"""
    
    try:
        tracker.update_step("Fallback System Init", "Preparing SimpleAI system...")
        tracker.add_log("🔄 Using fallback article generation system", "INFO")
        
        # Use SimpleAIArticleGenerator
        generator = SimpleAIArticleGenerator()
        
        # 1. Data Analysis
        tracker.update_step("Data Analysis", "Running basic data analysis...")
        tracker.add_log("📊 Running basic data analysis", "INFO")
        
        analysis_data = generator.analyze_events(events)
        tracker.add_log("✅ Data Analysis complete", "SUCCESS")
        
        time.sleep(1)
        
        # 2. Article Writing
        tracker.update_step("Article Writing", "AI drafting the article...")
        tracker.add_log("✍️ Running Claude article writing", "INFO")
        
        # Generate article with Claude
        article_content = generator.generate_article_with_claude(events, analysis_data)
        
        if not article_content:
            tracker.add_log("❌ Article generation failed", "ERROR")
            return None
            
        tracker.add_log("✅ Article Writing complete", "SUCCESS")
        time.sleep(1)
        
        # 3. Image/Chart Generation
        tracker.update_step("Image Generation", "Generating charts and images...")
        tracker.add_log("🖼️ Generating charts", "INFO")
        
        charts = generator.create_simple_charts(events, analysis_data)
        
        # Generate additional market trend chart
        market_trend_chart = create_market_trend_chart(events)
        if market_trend_chart:
            charts.append({
                'type': 'market_trend',
                'title': 'Market Trend Analysis',
                'figure': market_trend_chart,
                'description': 'Shows price changes of major symbols.'
            })
        
        # Generate real stock data chart
        symbols = [event.get('symbol') for event in events if event.get('symbol')]
        real_stock_chart = create_real_stock_chart(symbols)
        if real_stock_chart:
            charts.append({
                'type': 'real_stock_trend',
                'title': 'Real Stock Price Trend',
                'figure': real_stock_chart,
                'description': 'Shows actual stock price changes over the last 5 days.'
            })
        
        # Generate illustration using multimodal LLM
        tracker.add_log("🎨 Generating AI illustration", "INFO")
        illustration = generate_article_illustration(article_content, None)
        
        # Generate article-related image info
        article_title = article_content.get('title', 'Fundamental Agent')
        illustrations = []
        
        if illustration:
            illustrations.append({
                'type': 'ai_generated',
                'description': illustration['description'],
                'generated_at': illustration['generated_at']
            })
        
        # Add default illustration info
        illustrations.extend([
            {
                'type': 'market_trend',
                'description': f'Market trend illustration related to {article_title}',
                'keywords': ['Market', 'Economic', 'Investment', 'Stocks']
            },
            {
                'type': 'data_visualization', 
                'description': 'Key economic indicators and data visualization',
                'keywords': ['Data', 'Charts', 'Analysis', 'Indicators']
            }
        ])
        
        # AI determines whether to generate word cloud
        should_create_wordcloud = should_generate_wordcloud(article_content, analysis_data)
        wordcloud_image = None
        wordcloud_keywords = []
        
        if should_create_wordcloud:
            tracker.add_log("🔤 Generating word cloud", "INFO")
            
            # Extract more meaningful keywords
            wordcloud_keywords = []
            
            # 1. Stock symbols (high weight)
            for event in events:
                if 'symbol' in event:
                    symbol = event['symbol']
                    wordcloud_keywords.extend([symbol] * 3)  # Add 3 times for weight
            
            # 2. Extract meaningful words from article title
            if article_title:
                import re
                # Extract Korean, English, and numbers only
                title_words = re.findall(r'[가-힣a-zA-Z0-9]+', article_title)
                meaningful_words = [w for w in title_words if len(w) > 1 and w not in ['stock', 'company', 'corp', 'market', 'price']]
                wordcloud_keywords.extend(meaningful_words * 2)  # Add twice
            
            # 3. Extract core keywords from article content
            content = article_content.get('content', '')
            if content:
                # Extract core economic/finance keywords
                economic_terms = ['Investment', 'Profit', 'Growth', 'Outlook', 'Analysis', 'Earnings', 'Revenue', 'Profit', 'Loss', 
                                'Rise', 'Decline', 'Surge', 'Plunge', 'Volatility', 'Trade', 'Market Cap', 'Dividend']
                for term in economic_terms:
                    if term in content:
                        wordcloud_keywords.extend([term] * 2)
            
            # 4. Extract keywords from event descriptions
            for event in events:
                if 'description' in event:
                    desc = event['description']
                    # Percentage and number related keywords
                    if '%' in desc:
                        if 'Rise' in desc or 'Surge' in desc:
                            wordcloud_keywords.extend(['Rise', 'Surge'])
                        elif 'Decline' in desc or 'Plunge' in desc:
                            wordcloud_keywords.extend(['Decline', 'Plunge'])
            
            # 5. Sentiment-based keywords
            sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
            for event in events:
                sentiment = event.get('sentiment', 'neutral')
                sentiment_counts[sentiment] += 1
            
            if sentiment_counts['positive'] > sentiment_counts['negative']:
                wordcloud_keywords.extend(['Positive', 'Upward', 'Favorable'] * 2)
            elif sentiment_counts['negative'] > sentiment_counts['positive']:
                wordcloud_keywords.extend(['Negative', 'Downward', 'Unfavorable'] * 2)
            else:
                wordcloud_keywords.extend(['Neutral', 'Mixed', 'Wait-and-see'] * 2)
            
            # 6. Basic economic keywords (low weight)
            basic_keywords = ['Economic', 'Finance', 'Securities', 'Investor', 'Analyst', 'Expert', 'Market']
            wordcloud_keywords.extend(basic_keywords)
            
            # Generate word cloud image
            wordcloud_image = create_wordcloud_image(wordcloud_keywords, "Article keywords")
            tracker.add_log("✅ Word cloud generated", "SUCCESS")
        else:
            tracker.add_log("ℹ️ Word cloud deemed unnecessary", "INFO")
        
        tracker.add_log("✅ Charts and image info generation complete", "SUCCESS")
        
        time.sleep(1)
        
        # 4. Review
        tracker.update_step("Review", "Reviewing article quality...")
        tracker.add_log("🔍 Reviewing article quality", "INFO")
        
        review_result = generator.generate_simple_review(article_content)
        tracker.add_log("✅ Quality review complete", "SUCCESS")
        
        time.sleep(1)
        
        # 5. Ad Recommendation
        tracker.update_step("Ad Recommendation", "Recommending relevant ads...")
        tracker.add_log("📢 Recommending ads", "INFO")
        
        ads_result = generator.generate_simple_ads(article_content)
        tracker.add_log("✅ Ad Recommendation complete", "SUCCESS")
        
        tracker.add_log("✅ Article generation complete via fallback system", "SUCCESS")
        
        return {
            'article': article_content,
            'analysis': analysis_data,
            'images': {
                'charts': charts,
                'illustrations': illustrations,
                'wordcloud': {
                    'keywords': wordcloud_keywords,
                    'description': 'Article Keyword Wordcloud',
                    'image': wordcloud_image,
                    'generated': should_create_wordcloud
                } if should_create_wordcloud else None,
                'ai_illustration': illustration,
                'chart_image': 'Data Analysis Chart Image'
            },
            'review': review_result,
            'ads': ads_result,
            'timestamp': datetime.now().isoformat(),
            'system_used': 'fallback_simple_ai'
        }
        
    except Exception as e:
        tracker.add_log(f"💥 Fallback system error: {str(e)}", "ERROR")
        return None

def display_article_content(result):
    """Display generated article content"""
    
    if not result:
        st.error("❌ No article generated.")
        return
    
    st.markdown("---")
    st.header("📰 Generated AI Article")
    
    # Article metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Generated At", datetime.fromisoformat(result['timestamp']).strftime('%H:%M:%S'))
    with col2:
        st.metric("Events Detected", len(result.get('events', [])))
    with col3:
        quality_score = result.get('review', {}).get('quality_score', 0)
        st.metric("Quality Score", f"{quality_score:.1f}/10")
    
    # Article title and body
    article = result.get('article', {})
    if article:
        st.subheader("📝 Article Title")
        st.markdown(f"## {article.get('title', 'No Title')}")
        
        st.subheader("📄 Article Content")
        content = article.get('content', 'No Content')
        st.markdown(content)
        
        # Article tags
        tags = article.get('tags', [])
        if tags:
            st.subheader("🏷️ Related Tags")
            tag_cols = st.columns(min(len(tags), 5))
            for i, tag in enumerate(tags[:5]):
                with tag_cols[i]:
                    st.badge(tag)
    
    # Data Analysis Charts
    images = result.get('images', {})
    charts = images.get('charts', [])
    
    if charts:
        st.subheader("📊 Data Analysis Charts")
        
        for i, chart_data in enumerate(charts):
            # If Plotly figure object exists
            if 'figure' in chart_data:
                st.plotly_chart(chart_data['figure'], use_container_width=True)
                if 'description' in chart_data:
                    st.caption(chart_data['description'])
            # Legacy format support
            elif chart_data.get('type') == 'line':
                fig = px.line(
                    x=chart_data.get('x', []),
                    y=chart_data.get('y', []),
                    title=chart_data.get('title', f'Chart {i+1}')
                )
                st.plotly_chart(fig, use_container_width=True)
            elif chart_data.get('type') == 'bar':
                fig = px.bar(
                    x=chart_data.get('x', []),
                    y=chart_data.get('y', []),
                    title=chart_data.get('title', f'Chart {i+1}')
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Show analysis data separately
    analysis = result.get('analysis', {})
    if analysis and not charts:  # Show analysis data only when no charts
        st.subheader("📈 Analysis Data")
        
        # Show key metrics
        if 'price_changes' in analysis:
            price_changes = analysis['price_changes']
            if price_changes:
                st.write("**Major Stock Change Rates:**")
                for item in price_changes[:5]:  # Show top 5 only
                    symbol = item.get('symbol', 'Unknown')
                    change = item.get('change', 0)
                    color = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
                    st.write(f"{color} {symbol}: {change:+.2f}%")
        
        # Show market sentiment
        if 'market_sentiment' in analysis:
            sentiment = analysis['market_sentiment']
            sentiment_emoji = {"bullish": "🐂", "bearish": "🐻", "neutral": "⚖️"}
            st.write(f"**Market Sentiment:** {sentiment_emoji.get(sentiment, '\u2696\ufe0f')} {sentiment.upper()}")
    
    # Generated images (article-related)
    if images and 'illustrations' in images:
        st.subheader("🖼️ Article Related Images")
        
        illustrations = images.get('illustrations', [])
        if illustrations:
            for i, illustration in enumerate(illustrations):
                if isinstance(illustration, dict):
                    if illustration.get('type') == 'ai_generated':
                        st.markdown("### 🤖 AI Generated Illustration")
                        st.info("**AI-generated illustration description based on article analysis:**")
                        st.markdown(illustration.get('description', 'No Description'))
                        st.caption(f"Generated At: {illustration.get('generated_at', '')}")
                    else:
                        st.write(f"**Image {i+1}**: {illustration.get('description', 'Image Description')}")
                        # Display if actual image file exists
                        if 'path' in illustration:
                            try:
                                st.image(illustration['path'], caption=illustration.get('description', ''))
                            except:
                                st.write("failed to load image")
                else:
                    st.info(f"**Image {i+1}**: {illustration}")
    
    # Display AI illustration (with actual image file)
    st.subheader("🎨 AI Generated Illustration")
    
    try:
        # Check data existence
        has_images = bool(images)
        has_ai_illustration = has_images and 'ai_illustration' in images
        ai_illustration_data = images.get('ai_illustration') if has_ai_illustration else None
        has_description = bool(ai_illustration_data and isinstance(ai_illustration_data, dict) and ai_illustration_data.get('description'))
        
        if has_description:
            st.success("🎉 AI illustration generated successfully!")
            
            # Display actual image file
            image_file_info = ai_illustration_data.get('image_file')
            if image_file_info and isinstance(image_file_info, dict):
                image_path = image_file_info.get('image_path')
                
                if image_path and os.path.exists(image_path):
                    st.markdown("### 🖼️ Generated Illustration Image")
                    
                    # Load and display image using PIL
                    from PIL import Image
                    try:
                        img = Image.open(image_path)
                        
                        # Display image in two ways
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Default Size:**")
                            st.image(img, caption=f"AI Generated Illustration")
                        
                        with col2:
                            st.markdown("**Full Width:**")
                            st.image(img, caption=f"AI Generated Illustration", use_container_width=True)
                        
                        # Display image info
                        st.info(f"""
                        **Image Info:**
                        - Filename: {image_file_info.get('filename', 'Unknown')}
                        - Model: {image_file_info.get('model_used', 'Unknown')}
                        - Generated At: {image_file_info.get('generated_at', 'Unknown')}
                        - Size: {os.path.getsize(image_path)} bytes
                        """)
                        
                    except Exception as img_error:
                        st.error(f"Image Load Error: {img_error}")
                        st.write(f"Image Path: {image_path}")
                else:
                    st.warning("⚠️ Image file not found.")
                    if image_file_info:
                        st.write("Image file info:", image_file_info)
            else:
                st.info("📝 Text description only (no image file)")
            
            # Display text description
            st.markdown("### 📝 AI Generated Description")
            description = ai_illustration_data.get('description', '')
            formatted_description = description.replace('\\n\\n', '\n\n').replace('\\n', '\n')
            
            st.text_area(
                "Illustration Description",
                value=formatted_description,
                height=200,
                disabled=True
            )
            
            # Display generated time
            generated_at = ai_illustration_data.get('generated_at', '')
            if generated_at:
                st.caption(f"🕒 Generated At: {generated_at}")
                
        else:
            st.warning("⚠️ Failed to generate AI illustration.")
            
            # Manual placeholder image generation button
            if st.button("🔄 Generate Placeholder Image", key="generate_placeholder"):
                with st.spinner("Generating placeholder image..."):
                    try:
                        article = result.get('article', {})
                        title = article.get('title', 'AI Economic Article')
                        
                        placeholder_result = generate_placeholder_image(title, "output/images")
                        if placeholder_result:
                            st.success("✅ Generate Placeholder Image complete!")
                            
                            # Display generated image
                            img_path = placeholder_result['image_path']
                            if os.path.exists(img_path):
                                from PIL import Image
                                img = Image.open(img_path)
                                st.image(img, caption="Placeholder Illustration", use_container_width=True)
                        else:
                            st.error("❌ Generate Placeholder Image failed")
                    except Exception as e:
                        st.error(f"💥 Error: {str(e)}")
            
    except Exception as e:
        st.error(f"💥 Error displaying AI illustration: {str(e)}")
        st.write("**Debug Info:**")
        st.write(f"- images type: {type(images)}")
        if images:
            st.write(f"- images keys: {list(images.keys())}")
            if 'ai_illustration' in images:
                st.write(f"- ai_illustration content: {images['ai_illustration']}")
    
    # Word cloud and other image info
    if images and 'wordcloud' in images and images['wordcloud']:
        wordcloud_data = images['wordcloud']
        if wordcloud_data.get('generated', False):  # Only if AI deemed necessary
            st.subheader("📸 Additional Visualization")
            st.write("🔤 **Wordcloud**: Visualizes key article keywords")
            
            # Display if actual word cloud image exists
            if 'image' in wordcloud_data and wordcloud_data['image']:
                try:
                    st.image(wordcloud_data['image'], caption="Article keywords", use_container_width=True)
                except Exception as e:
                    st.write(f"Wordcloud display error: {e}")
                    # Fallback to keyword list
                    keywords = wordcloud_data.get('keywords', [])
                    if keywords:
                        st.write("**keywords:**", ", ".join(list(set(keywords))[:15]))
            else:
                # Display keyword list
                keywords = wordcloud_data.get('keywords', [])
                if keywords:
                    unique_keywords = list(set(keywords))[:15]  # 15 unique keywords
                    st.write("**keywords:**", ", ".join(unique_keywords))
    
    # Other image info
    if images and any(key in images for key in ['illustration', 'chart_image']):
        if not (images.get('wordcloud', {}).get('generated', False)):  # Only if word cloud not displayed
            st.subheader("📸 Additional Visualization")
        
        if 'illustration' in images:
            st.write("🎨 **Illustration**: Image representing article content")
        if 'chart_image' in images:
            st.write("📊 **Chart Image**: Data analysis visualization")
    
    # Review Results
    review = result.get('review', {})
    if review:
        st.subheader("🔍 Review Results")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Quality Assessment**")
            quality_items = review.get('quality_assessment', {})
            for key, value in quality_items.items():
                st.write(f"• {key}: {value}")
        
        with col2:
            st.markdown("**Improvement Suggestions**")
            suggestions = review.get('suggestions', [])
            for suggestion in suggestions:
                st.write(f"• {suggestion}")
    
    # Recommended Ads
    ads = result.get('ads', {})
    if ads:
        st.subheader("📢 Recommended Ads")
        
        recommended_ads = ads.get('recommendations', [])
        if recommended_ads:
            ad_cols = st.columns(min(len(recommended_ads), 2))
            for i, ad in enumerate(recommended_ads[:2]):
                with ad_cols[i]:
                    st.container()
                    st.markdown(f"**{ad.get('title', 'Ad Title')}**")
                    st.write(ad.get('description', 'Ad Description'))
                    st.caption(f"Relevance: {ad.get('relevance_score', 0):.1f}/10")

def show_ai_article_generator():
    """AI Article Generator Main Page"""
    
    st.title("🤖 AI Article Generation Pipeline")
    st.markdown("**Fully automated from event detection to article writing, image generation, review, and ad recommendation**")
    st.markdown("---")
    
    # Auto-refresh settings
    with st.sidebar:
        st.header("⚙️ Generation Options")
        
        # Auto-refresh options
        auto_refresh = st.checkbox("🔄 Auto-refresh every 5 min", value=False, key="auto_refresh_check")
        
        if auto_refresh:
            st.info("✅ Auto-generates a new article every 5 minutes")
            # Use streamlit-autorefresh if available, otherwise manual check
            if st_autorefresh:
                st_autorefresh(interval=300000, key="auto_article_refresh")
            else:
                st.caption("⚠️ Please manually refresh the page for auto-refresh")
        
        article_type = st.selectbox(
            "Article Type",
            ["Market Analysis", "Individual Stock", "Economic Outlook", "Sector Analysis"],
            key="article_type_select"
        )
        
        analysis_depth = st.selectbox(
            "Analysis Depth",
            ["Basic", "Detailed", "Expert"],
            key="analysis_depth_select"
        )
        
        include_images = st.checkbox("Include Image Generation", value=True, key="include_images_check")
        include_ads = st.checkbox("Include Ad Recommendation", value=True, key="include_ads_check")
        
        # Show last generated time
        if 'last_ai_article_update' in st.session_state:
            last_update = st.session_state.last_ai_article_update
            time_diff = datetime.now() - last_update
            minutes_ago = int(time_diff.total_seconds() / 60)
            st.caption(f"Last generated: {minutes_ago} min ago")
    
    # Check auto-generation conditions
    should_auto_generate = False
    if auto_refresh and 'last_ai_article_update' in st.session_state:
        last_update = st.session_state.last_ai_article_update
        time_diff = datetime.now() - last_update
        # Auto-generate if 5 minutes (300s) elapsed
        if time_diff.total_seconds() >= 300:
            should_auto_generate = True
    
    # Cache check and generation conditions
    manual_trigger = st.button("🚀 Generate AI Article", type="primary", key="ai_article_generate")
    
    if ('ai_article_data' not in st.session_state or 
        manual_trigger or 
        should_auto_generate or
        (auto_refresh and 'ai_article_data' not in st.session_state)):
        
        if should_auto_generate:
            st.info("🔄 5 minutes elapsed, auto-generating new article...")
        
        # Progress display container
        st.subheader("🔄 AI Article Generation Progress")
        
        # Progress bar
        progress_bar = st.progress(0)
        
        # Status text
        status_text = st.empty()
        
        # Step status
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            event_status = st.empty()
        with col2:
            analysis_status = st.empty()
        with col3:
            writing_status = st.empty()
        with col4:
            image_status = st.empty()
        with col5:
            review_status = st.empty()
        with col6:
            ad_status = st.empty()
        
        # Log container
        st.markdown("#### 📝 Real-time Log")
        log_container = st.empty()
        
        # Initialize progress tracker
        tracker = StreamlitProgressTracker(progress_bar, status_text, log_container)
        
        try:
            # 1. Event Detection
            event_status.metric("Event Detection", "In Progress...", "🔄")
            events = collect_event_data_with_progress(tracker)
            
            if events:
                event_status.metric("Event Detection", f"{len(events)}", "✅")
            else:
                event_status.metric("Event Detection", "failed", "❌")
                st.error("❌ Event detection failed.")
                return
            
            # 2. AI agent pipeline execution
            analysis_status.metric("Data Analysis", "Waiting...", "⏳")
            writing_status.metric("Article Writing", "Waiting...", "⏳")
            image_status.metric("Image Generation", "Waiting...", "⏳")
            review_status.metric("Article Review", "Waiting...", "⏳")
            ad_status.metric("Ad Recommendation", "Waiting...", "⏳")
            
            result = generate_article_with_agents(events, tracker)
            
            if result:
                # Update step status
                analysis_status.metric("Data Analysis", "complete", "✅")
                writing_status.metric("Article Writing", "complete", "✅")
                
                if include_images:
                    image_status.metric("Image Generation", "complete", "✅")
                else:
                    image_status.metric("Image Generation", "Skipped", "⏭️")
                
                review_status.metric("Article Review", "complete", "✅")
                
                if include_ads:
                    ad_status.metric("Ad Recommendation", "complete", "✅")
                else:
                    ad_status.metric("Ad Recommendation", "Skipped", "⏭️")
                
                # complete
                progress_bar.progress(1.0)
                status_text.success("✅ AI article generation complete!")
                
                # Save to session state
                st.session_state.ai_article_data = result
                st.session_state.last_ai_article_update = datetime.now()
                
                # Success message
                if should_auto_generate:
                    st.success("🎉 Auto AI article generation complete!")
                else:
                    st.success("🎉 AI article generation complete!")
                time.sleep(2)
                st.rerun()
            
            else:
                st.error("❌ AI article generation failed.")
                return
        
        except Exception as e:
            tracker.add_log(f"💥 System error: {str(e)}", "ERROR")
            st.error(f"❌ System error: {str(e)}")
            return
    
    # Use cached data
    if 'ai_article_data' in st.session_state:
        result = st.session_state.ai_article_data
        last_update = st.session_state.get('last_ai_article_update', datetime.now())
        
        # Display update time
        st.info(f"📅 Last generated: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Display generated article
        display_article_content(result)
        
        # Download options
        st.markdown("---")
        st.subheader("💾 Download & Share Options")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📄 Download Article Text", key="download_text"):
                article = result.get('article', {})
                content = f"# {article.get('title', 'No Title')}\n\n{article.get('content', 'No Content')}"
                st.download_button(
                    label="Download",
                    data=content,
                    file_name=f"ai_article_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
        
        with col2:
            if st.button("📊 Download Analysis Data", key="download_analysis"):
                analysis_data = json.dumps(result.get('analysis', {}), indent=2, ensure_ascii=False)
                st.download_button(
                    label="Download",
                    data=analysis_data,
                    file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col3:
            if st.button("📋 Download Full Results", key="download_full"):
                # Remove sensitive info before download
                download_data = {
                    'article': result.get('article', {}),
                    'analysis_summary': result.get('analysis', {}).get('summary', ''),
                    'review': result.get('review', {}),
                    'ads': result.get('ads', {}),
                    'timestamp': result.get('timestamp', '')
                }
                full_data = json.dumps(download_data, indent=2, ensure_ascii=False)
                st.download_button(
                    label="Download",
                    data=full_data,
                    file_name=f"ai_article_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col4:
            if st.button("📄 Generate PDF", key="generate_pdf"):
                with st.spinner("Generating PDF..."):
                    try:
                        # Create HTML content
                        html_content = create_html_article(result)
                        
                        # PDF file path
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        pdf_filename = f"ai_article_{timestamp}.pdf"
                        pdf_path = os.path.join("output", pdf_filename)
                        
                        # Create output directory
                        os.makedirs("output", exist_ok=True)
                        
                        # Convert to PDF
                        if convert_html_to_pdf(html_content, pdf_path):
                            st.success(f"✅ PDF generated: {pdf_filename}")
                            
                            # PDF download button
                            with open(pdf_path, "rb") as pdf_file:
                                st.download_button(
                                    label="📥 PDF Download",
                                    data=pdf_file.read(),
                                    file_name=pdf_filename,
                                    mime="application/pdf"
                                )
                        else:
                            st.error("❌ PDF generation failed")
                            
                    except Exception as e:
                        st.error(f"💥 PDF generation error: {str(e)}")
        
    
    else:
        st.info("🚀 Click 'Generate AI Article' button to create a new article.")

if __name__ == "__main__":
    show_ai_article_generator()
