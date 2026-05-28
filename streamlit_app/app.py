"""
Fundamental Agent Streamlit Dashboard
"""

import streamlit as st
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from streamlit_app.visualization_utils import ChartGenerator, NewsImageGenerator, AdGenerator
from agents.orchestrator_strand import main_orchestrator, StrandContext
from event_detection_slack_system import EventMonitoringSystem
from config.settings import load_config


class EconomicNewsDashboard:
    """Fundamental Agent Dashboard Class"""
    
    def __init__(self):
        self.chart_generator = ChartGenerator()
        self.image_generator = NewsImageGenerator()
        self.ad_generator = AdGenerator()
        self.output_dir = "../output"
        
        # Page config
        st.set_page_config(
            page_title="Fundamental Agent Dashboard",
            page_icon="📈",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS
        self.load_custom_css()
    
    def load_custom_css(self):
        """Load custom CSS"""
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(90deg, #1f77b4 0%, #ff7f0e 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .article-container {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 8px;
            color: white;
            text-align: center;
        }
        
        .news-headline {
            font-size: 2rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 1rem;
            line-height: 1.2;
        }
        
        .news-lead {
            font-size: 1.2rem;
            color: #666;
            margin-bottom: 1.5rem;
            font-style: italic;
        }
        
        .news-content {
            font-size: 1rem;
            line-height: 1.6;
            color: #444;
            text-align: justify;
        }
        
        .tag {
            background-color: #e9ecef;
            color: #495057;
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.875rem;
            margin-right: 0.5rem;
            display: inline-block;
        }
        
        .sidebar-section {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        
        .ad-container {
            border-left: 4px solid #007cba;
            padding-left: 1rem;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def run(self):
        """Run main application"""
        # Header
        st.markdown("""
        <div class="main-header">
            <h1>📈 Fundamental Agent Dashboard</h1>
            <p>Intelligent economic analysis powered by Strands Agents</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar
        self.create_sidebar()
        
        # Main content
        self.create_main_content()
    
    def create_sidebar(self):
        """Create sidebar"""
        st.sidebar.markdown("## 🎛️ Control Panel")
        
        # New article button
        if st.sidebar.button("🚀 Generate New Article", type="primary"):
            self.generate_new_article()
        
        # Article list
        st.sidebar.markdown("## 📰 Article List")
        article_files = self.get_article_files()
        
        if article_files:
            selected_file = st.sidebar.selectbox(
                "Select Article",
                article_files,
                format_func=lambda x: self.format_filename(x)
            )
            st.session_state['selected_article'] = selected_file
        else:
            st.sidebar.warning("No articles generated.")
            st.session_state['selected_article'] = None
        
        # Settings
        st.sidebar.markdown("## ⚙️ Settings")
        
        show_charts = st.sidebar.checkbox("📊 Show Charts", value=True)
        show_images = st.sidebar.checkbox("🖼️ Show Images", value=True)
        show_ads = st.sidebar.checkbox("📢 Show Ads", value=True)
        
        st.session_state.update({
            'show_charts': show_charts,
            'show_images': show_images,
            'show_ads': show_ads
        })
        
        # System info
        st.sidebar.markdown("## ℹ️ System Info")
        st.sidebar.info(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    def create_main_content(self):
        """Create main content"""
        if 'selected_article' not in st.session_state or not st.session_state['selected_article']:
            self.show_welcome_screen()
            return
        
        # Load selected article
        article_data = self.load_article_data(st.session_state['selected_article'])
        if not article_data:
            st.error("Could not load article data.")
            return
        
        # Display article
        self.display_article(article_data)
    
    def show_welcome_screen(self):
        """Show welcome screen"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 3rem;">
                <h2>🎯 Welcome to the Fundamental Agent System!</h2>
                <p style="font-size: 1.2rem; color: #666;">
                    An intelligent economic article generation system powered by AWS Bedrock and Strands Agents.
                </p>
                <br>
                <p>Click the <strong>"Generate New Article"</strong> button in the sidebar to get started.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Feature introduction
            st.markdown("### 🚀 Key Features")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("""
                - 📊 **Real-time Data Collection**
                - 🤖 **AI-based Article Writing**
                - 📈 **Interactive Charts**
                - 🖼️ **Auto Image Generation**
                """)
            
            with col_b:
                st.markdown("""
                - 🎯 **Content Optimization**
                - 📢 **Targeted Ads**
                - 📱 **Responsive Design**
                - 🔄 **Real-time Updates**
                """)
    
    def display_article(self, article_data: Dict[str, Any]):
        """Display article"""
        # Article metadata
        collected_data = article_data.get('collected_data', {})
        articles = article_data.get('optimized_articles', article_data.get('articles', []))
        
        if not articles:
            st.error("No articles to display.")
            return
        
        article_info = articles[0]
        article = article_info.get('optimized_article', article_info.get('article', {}))
        
        # Display metrics
        self.display_metrics(collected_data)
        
        # Display charts
        if st.session_state.get('show_charts', True):
            self.display_charts(collected_data)
        
        # Article body
        self.display_article_content(article, article_info)
        
        # Display ads
        if st.session_state.get('show_ads', True):
            self.display_ads(article)
    
    def display_metrics(self, collected_data: Dict[str, Any]):
        """Display metrics"""
        st.markdown("## 📊 Market Overview")
        
        stock_data = collected_data.get('stock_data', {})
        economic_data = collected_data.get('economic_data', {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        # S&P 500
        if '^GSPC' in stock_data:
            sp500 = stock_data['^GSPC']
            with col1:
                st.metric(
                    "S&P 500",
                    f"{sp500.get('current_price', 0):.2f}",
                    f"{sp500.get('change_percent', 0):.2f}%"
                )
        
        # Nasdaq
        if '^IXIC' in stock_data:
            nasdaq = stock_data['^IXIC']
            with col2:
                st.metric(
                    "Nasdaq",
                    f"{nasdaq.get('current_price', 0):.2f}",
                    f"{nasdaq.get('change_percent', 0):.2f}%"
                )
        
        # VIX
        if 'VIX' in economic_data:
            vix = economic_data['VIX']
            with col3:
                st.metric(
                    "VIX",
                    f"{vix.get('value', 0):.2f}",
                    vix.get('interpretation', '')
                )
        
        # Dollar Index
        if 'DXY' in economic_data:
            dxy = economic_data['DXY']
            with col4:
                st.metric(
                    "Dollar Index",
                    f"{dxy.get('value', 0):.2f}",
                    dxy.get('interpretation', '')
                )
    
    def display_charts(self, collected_data: Dict[str, Any]):
        """Display charts"""
        st.markdown("## 📈 Market Analysis")
        
        stock_data = collected_data.get('stock_data', {})
        economic_data = collected_data.get('economic_data', {})
        
        # Chart tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Stock Status", "Change Rate", "Sector Performance", "VIX Index"])
        
        with tab1:
            fig1 = self.chart_generator.create_stock_price_chart(stock_data)
            st.plotly_chart(fig1, use_container_width=True)
        
        with tab2:
            fig2 = self.chart_generator.create_change_percentage_chart(stock_data)
            st.plotly_chart(fig2, use_container_width=True)
        
        with tab3:
            fig3 = self.chart_generator.create_sector_performance_chart(stock_data)
            st.plotly_chart(fig3, use_container_width=True)
        
        with tab4:
            col1, col2 = st.columns([1, 1])
            with col1:
                fig4 = self.chart_generator.create_vix_fear_greed_gauge(economic_data)
                st.plotly_chart(fig4, use_container_width=True)
            with col2:
                fig5 = self.chart_generator.create_market_cap_pie_chart(stock_data)
                st.plotly_chart(fig5, use_container_width=True)
    
    def display_article_content(self, article: Dict[str, Any], article_info: Dict[str, Any]):
        """Display article content"""
        st.markdown("## 📰 Economic News")
        
        # Article container
        with st.container():
            # Headline
            st.markdown(f'<div class="news-headline">{article.get("headline", "No Title")}</div>', 
                       unsafe_allow_html=True)
            
            # Lead
            if article.get('lead'):
                st.markdown(f'<div class="news-lead">{article.get("lead")}</div>', 
                           unsafe_allow_html=True)
            
            # Display images
            if st.session_state.get('show_images', True):
                self.display_article_images(article)
            
            # Body
            content = article.get('content', '')
            if content:
                # Parse JSON content if needed
                try:
                    if content.startswith('{') and content.endswith('}'):
                        content_json = json.loads(content)
                        actual_content = content_json.get('content', content)
                    else:
                        actual_content = content
                except:
                    actual_content = content
                
                st.markdown(f'<div class="news-content">{actual_content.replace("<br>", "<br/>")}</div>', 
                           unsafe_allow_html=True)
            
            # Conclusion
            if article.get('conclusion'):
                st.markdown("### 💡 Conclusion")
                st.info(article.get('conclusion'))
            
            # Tags
            if article.get('tags'):
                st.markdown("### 🏷️ Tags")
                tags_html = ''.join([f'<span class="tag">{tag}</span>' for tag in article.get('tags', [])])
                st.markdown(tags_html, unsafe_allow_html=True)
            
            # Quality info
            quality_check = article_info.get('quality_check', {})
            if quality_check:
                st.markdown("### 📊 Article Quality Info")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Overall Score", f"{quality_check.get('overall_score', 0)}/100")
                with col2:
                    st.metric("Accuracy", f"{quality_check.get('scores', {}).get('accuracy', 0)}/100")
                with col3:
                    st.metric("Readability", f"{quality_check.get('scores', {}).get('clarity', 0)}/100")
    
    def display_article_images(self, article: Dict[str, Any]):
        """Display article images"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Article illustration
            illustration_url = self.image_generator.generate_article_illustration(
                article.get('content', ''), 
                'market_summary'
            )
            if illustration_url:
                st.image(illustration_url, caption="Article Illustration", use_column_width=True)
        
        with col2:
            # Word cloud
            wordcloud_img = self.image_generator.create_wordcloud_from_article(
                article.get('content', '')
            )
            if wordcloud_img:
                st.image(wordcloud_img, caption="Keyword Cloud", use_column_width=True)
    
    def display_ads(self, article: Dict[str, Any]):
        """Display ads"""
        st.markdown("## 📢 Recommended Services")
        
        # Contextual ad generation
        ads = self.ad_generator.generate_contextual_ads(
            article.get('content', ''),
            article.get('tags', [])
        )
        
        if ads:
            cols = st.columns(len(ads))
            for i, ad in enumerate(ads):
                with cols[i]:
                    ad_html = self.ad_generator.create_ad_html(ad)
                    st.markdown(ad_html, unsafe_allow_html=True)
    
    def generate_new_article(self):
        """Generate new article via Strands pipeline"""
        with st.spinner("Generating a new article..."):
            try:
                import asyncio
                monitor = EventMonitoringSystem()
                scan = monitor.run_single_scan()
                events = scan.get('events', [])

                if not events:
                    st.warning("No active events detected. Using default symbol (SPY).")
                    event = {'symbol': 'SPY', 'event_type': 'market_summary', 'severity': 'low',
                             'description': 'General market overview', 'change_percent': 0,
                             'timestamp': datetime.now().isoformat()}
                else:
                    ev = events[0]
                    event = {
                        'symbol': ev.get('symbol', 'SPY'),
                        'event_type': ev.get('type', 'market_summary'),
                        'severity': ev.get('severity', 'low'),
                        'description': ev.get('title', ev.get('description', '')),
                        'change_percent': ev.get('change_percent', 0),
                        'timestamp': ev.get('timestamp', datetime.now().isoformat()),
                    }

                context = StrandContext(
                    strand_id=f"streamlit_{event['symbol']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    input_data={'event': event}
                )

                result = asyncio.run(main_orchestrator.process(context))
                st.success(f"Article generated for {event['symbol']}!")
                st.rerun()

            except Exception as e:
                st.error(f"Error generating article: {str(e)}")
    
    def get_article_files(self) -> List[str]:
        """Get article file list"""
        output_path = os.path.join(os.path.dirname(__file__), self.output_dir)
        
        if not os.path.exists(output_path):
            return []
        
        files = []
        for filename in os.listdir(output_path):
            if filename.startswith('pipeline_result_') and filename.endswith('.json'):
                files.append(filename)
        
        return sorted(files, reverse=True)
    
    def load_article_data(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load article data"""
        try:
            file_path = os.path.join(os.path.dirname(__file__), self.output_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"File load error: {str(e)}")
            return None
    
    def format_filename(self, filename: str) -> str:
        """Format filename"""
        # pipeline_result_20250804_075502.json -> 2025-08-04 07:55:02
        try:
            timestamp_part = filename.replace('pipeline_result_', '').replace('.json', '')
            date_part = timestamp_part[:8]
            time_part = timestamp_part[9:]
            
            formatted_date = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]}"
            formatted_time = f"{time_part[:2]}:{time_part[2:4]}:{time_part[4:6]}"
            
            return f"{formatted_date} {formatted_time}"
        except:
            return filename


def main():
    """Main function"""
    dashboard = EconomicNewsDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
