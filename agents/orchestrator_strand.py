"""
Orchestrator Strand Agent
Manages and coordinates the entire Fundamental Agent generation workflow
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import asyncio

from .strands_framework import BaseStrandAgent, StrandContext, StrandMessage, MessageType, StrandOrchestrator, orchestrator
from .data_analysis_strand import DataAnalysisStrand
from .forex_analyst_strand import ForexAnalystStrand
from .article_writer_strand import ArticleWriterStrand
from .review_strand import ReviewStrand
from .image_generator_strand import ImageGeneratorStrand
from .ad_recommendation_strand import AdRecommendationStrand

class OrchestratorStrand(BaseStrandAgent):
    """Orchestrator Strand Agent"""
    
    def __init__(self):
        super().__init__(
            agent_id="orchestrator",
            name="Orchestrator Agent"
        )
        
        self.capabilities = [
            "workflow_management",
            "agent_coordination",
            "quality_control",
            "output_generation",
            "system_monitoring"
        ]
        
        # Initialize and register sub-agents
        self._initialize_agents()
        
        # Set up output directories
        self.output_dirs = {
            'articles': 'output/automated_articles',
            'streamlit': 'streamlit_articles',
            'charts': 'output/charts',
            'images': 'output/images'
        }
        
        for dir_path in self.output_dirs.values():
            os.makedirs(dir_path, exist_ok=True)
    
    def _initialize_agents(self):
        """Initialize and register sub-agents"""
        
        # Create agent instances
        self.data_analyst = DataAnalysisStrand()
        self.forex_analyst = ForexAnalystStrand()
        self.article_writer = ArticleWriterStrand()
        self.reviewer = ReviewStrand()
        self.image_generator = ImageGeneratorStrand()
        self.ad_recommender = AdRecommendationStrand()
        
        # Register with global orchestrator
        orchestrator.register_agent(self.data_analyst)
        orchestrator.register_agent(self.forex_analyst)
        orchestrator.register_agent(self.article_writer)
        orchestrator.register_agent(self.reviewer)
        orchestrator.register_agent(self.image_generator)
        orchestrator.register_agent(self.ad_recommender)
        
        self.logger.info("✅ All sub-agents initialized")
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return self.capabilities
    
    async def process(self, context: StrandContext, message: Optional[StrandMessage] = None) -> Dict[str, Any]:
        """Process entire workflow (async)"""
        
        event_data = context.input_data.get('event')
        if not event_data:
            raise Exception("No event data to process")
        
        symbol = event_data.get('symbol', 'Unknown')
        self.logger.info(f"🚀 {symbol} full workflow started")
        
        try:
            # Define workflow
            workflow = [
                'data_analyst',      # 1. Data analysis
                'forex_analyst',     # 2. Forex analysis (for forex events)
                'article_writer',    # 3. Article writing
                'reviewer',          # 4. Article review
                'image_generator',   # 5. Image generation
                'ad_recommender'     # 6. Ad recommendation
            ]
            
            # Execute strand
            strand_id = f"news_generation_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            result_context = await orchestrator.execute_strand(strand_id, context.input_data, workflow)
            
            if result_context.status.value == 'completed':
                # Create final package
                final_package = await self._create_final_package(result_context)
                
                self.logger.info(f"✅ {symbol} full workflow completed")
                return final_package
            else:
                raise Exception(f"Workflow execution failed: {result_context.status}")
                
        except Exception as e:
            self.logger.error(f"❌ {symbol} workflow failed: {str(e)}")
            raise
    
    def execute_data_analysis(self, context: StrandContext) -> Dict[str, Any]:
        """Execute data analysis"""
        try:
            self.logger.info("📊 Data analysis started")
            
            # Execute data analysis agent
            analysis_message = StrandMessage(
                message_type=MessageType.REQUEST,
                content="Data analysis request",
                data=context.input_data
            )
            
            # Execute synchronously (Streamlit compatibility)
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.data_analyst.process(context, analysis_message)
                )
                self.logger.info("✅ Data analysis completed")
                return result
            finally:
                loop.close()
                
        except Exception as e:
            self.logger.error(f"❌ Data analysis failed: {str(e)}")
            return {}
    
    def execute_article_writing(self, context: StrandContext) -> Dict[str, Any]:
        """Execute article writing"""
        try:
            self.logger.info("✍️ Article writing started")
            
            writing_message = StrandMessage(
                message_type=MessageType.REQUEST,
                content="Article writing request",
                data=context.input_data
            )
            
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.article_writer.process(context, writing_message)
                )
                self.logger.info("✅ Article writing completed")
                return result
            finally:
                loop.close()
                
        except Exception as e:
            self.logger.error(f"❌ Article writing failed: {str(e)}")
            return {}
    
    def execute_image_generation(self, context: StrandContext) -> Dict[str, Any]:
        """Execute image generation"""
        try:
            self.logger.info("🎨 Image generation started")
            
            image_message = StrandMessage(
                message_type=MessageType.REQUEST,
                content="Image generation request",
                data=context.input_data
            )
            
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.image_generator.process(context, image_message)
                )
                self.logger.info("✅ Image generation completed")
                return result
            finally:
                loop.close()
                
        except Exception as e:
            self.logger.error(f"❌ Image generation failed: {str(e)}")
            return {}
    
    def execute_review(self, context: StrandContext) -> Dict[str, Any]:
        """Execute article review"""
        try:
            self.logger.info("🔍 Article review started")
            
            review_message = StrandMessage(
                message_type=MessageType.REQUEST,
                content="Article review request",
                data=context.input_data
            )
            
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.reviewer.process(context, review_message)
                )
                self.logger.info("✅ Article review completed")
                return result
            finally:
                loop.close()
                
        except Exception as e:
            self.logger.error(f"❌ Article review failed: {str(e)}")
            return {}
    
    def execute_ad_recommendation(self, context: StrandContext) -> Dict[str, Any]:
        """Execute ad recommendation"""
        try:
            self.logger.info("📢 Ad recommendation started")
            
            ad_message = StrandMessage(
                message_type=MessageType.REQUEST,
                content="Ad recommendation request",
                data=context.input_data
            )
            
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.ad_recommender.process(context, ad_message)
                )
                self.logger.info("✅ Ad recommendation completed")
                return result
            finally:
                loop.close()
                
        except Exception as e:
            self.logger.error(f"❌ Ad recommendation failed: {str(e)}")
            return {}
        """Execute data analysis"""
        try:
            self.logger.info("📊 Data analysis started")
            
            # Execute data analysis agent
            analysis_message = StrandMessage(
                message_type=MessageType.REQUEST,
                content="Data analysis request",
                data=context.input_data
            )
            
            # Execute synchronously (Streamlit compatibility)
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.data_analyst.process(context, analysis_message)
                )
                self.logger.info("✅ Data analysis completed")
                return result
            finally:
                loop.close()
                
        except Exception as e:
            self.logger.error(f"❌ Data analysis failed: {str(e)}")
            return {}
    
    def execute_article_writing(self, context: StrandContext) -> Dict[str, Any]:
        """Execute article writing"""
        try:
            self.logger.info("✍️ Article writing started")
            
            writing_message = StrandMessage(
                message_type=MessageType.REQUEST,
                content="Article writing request",
                data=context.input_data
            )
            
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.article_writer.process(context, writing_message)
                )
                self.logger.info("✅ Article writing completed")
                return result
            finally:
                loop.close()
                
        except Exception as e:
            self.logger.error(f"❌ Article writing failed: {str(e)}")
            return {}
    
    def execute_image_generation(self, context: StrandContext) -> Dict[str, Any]:
        """Execute image generation"""
        try:
            self.logger.info("🎨 Image generation started")
            
            image_message = StrandMessage(
                message_type=MessageType.REQUEST,
                content="Image generation request",
                data=context.input_data
            )
            
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.image_generator.process(context, image_message)
                )
                self.logger.info("✅ Image generation completed")
                return result
            finally:
                loop.close()
                
        except Exception as e:
            self.logger.error(f"❌ Image generation failed: {str(e)}")
            return {}
    
    def execute_review(self, context: StrandContext) -> Dict[str, Any]:
        """Execute article review"""
        try:
            self.logger.info("🔍 Article review started")
            
            review_message = StrandMessage(
                message_type=MessageType.REQUEST,
                content="Article review request",
                data=context.input_data
            )
            
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.reviewer.process(context, review_message)
                )
                self.logger.info("✅ Article review completed")
                return result
            finally:
                loop.close()
                
        except Exception as e:
            self.logger.error(f"❌ Article review failed: {str(e)}")
            return {}
    
    def execute_ad_recommendation(self, context: StrandContext) -> Dict[str, Any]:
        """Execute ad recommendation"""
        try:
            self.logger.info("📢 Ad recommendation started")
            
            ad_message = StrandMessage(
                message_type=MessageType.REQUEST,
                content="Ad recommendation request",
                data=context.input_data
            )
            
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.ad_recommender.process(context, ad_message)
                )
                self.logger.info("✅ Ad recommendation completed")
                return result
            finally:
                loop.close()
                
        except Exception as e:
            self.logger.error(f"❌ Ad recommendation failed: {str(e)}")
            return {}
    
    async def process(self, context: StrandContext, message: Optional[StrandMessage] = None) -> Dict[str, Any]:
        """Process entire workflow"""
        
        event_data = context.input_data.get('event')
        if not event_data:
            raise Exception("No event data to process")
        
        symbol = event_data.get('symbol', 'Unknown')
        self.logger.info(f"🚀 {symbol} full workflow started")
        
        try:
            # Define workflow
            workflow = [
                'data_analyst',      # 1. Data analysis
                'forex_analyst',     # 2. Forex analysis (for forex events)
                'article_writer',    # 3. Article writing
                'reviewer',          # 4. Article review
                'image_generator',   # 5. Image generation
                'ad_recommender'     # 6. Ad recommendation
            ]
            
            # Execute strand
            strand_id = f"news_generation_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            result_context = await orchestrator.execute_strand(strand_id, context.input_data, workflow)
            
            if result_context.status.value == 'completed':
                # Create final package
                final_package = await self._create_final_package(result_context)
                
                # Generate output files
                output_files = await self._generate_output_files(final_package)
                
                # Generate Streamlit page
                streamlit_page = await self._generate_streamlit_page(final_package)

                result = {
                    'status': 'success',
                    'package': final_package,
                    'output_files': output_files,
                    'streamlit_page': streamlit_page,
                    'execution_time': (datetime.now() - result_context.created_at).total_seconds(),
                    'strand_id': strand_id
                }
                
                self.logger.info(f"✅ {symbol} full workflow completed")
                return result
            else:
                raise Exception(f"Workflow execution failed: {result_context.error}")
                
        except Exception as e:
            self.logger.error(f"❌ Workflow execution failed: {e}")
            raise

    async def _create_final_package(self, context: StrandContext) -> Dict[str, Any]:
        """Create final package"""
        
        # Collect results from each agent
        data_analysis = context.results.get('data_analyst', {})
        forex_analysis = context.results.get('forex_analyst', {})
        article = context.results.get('article_writer', {})
        review_result = context.results.get('reviewer', {})
        images = context.results.get('image_generator', {})
        advertisements = context.results.get('ad_recommender', {})
        
        # Event data
        event_data = context.input_data.get('event', {})
        
        # Build final package
        package = {
            'event': event_data,
            'data_analysis': data_analysis,
            'forex_analysis': forex_analysis,
            'article': article,
            'review_result': review_result,
            'images': images,
            'advertisements': advertisements.get('recommended_ads', []),
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'strand_id': context.strand_id,
                'processing_time_seconds': (datetime.now() - context.created_at).total_seconds(),
                'quality_score': review_result.get('overall_score', 0),
                'agent_versions': {
                    'data_analyst': '1.0.0',
                    'article_writer': '1.0.0',
                    'reviewer': '1.0.0',
                    'image_generator': '1.0.0',
                    'ad_recommender': '1.0.0'
                }
            }
        }
        
        return package
    
    async def _generate_output_files(self, package: Dict[str, Any]) -> Dict[str, str]:
        """Generate output files"""
        
        symbol = package['event'].get('symbol', 'Unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        output_files = {}
        
        try:
            # 1. Save JSON file
            json_filename = f"{symbol}_{timestamp}.json"
            json_filepath = os.path.join(self.output_dirs['articles'], json_filename)
            
            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(package, f, ensure_ascii=False, indent=2, default=str)
            
            output_files['json'] = json_filepath
            
            # 2. Generate HTML file
            html_content = await self._generate_html_article(package)
            html_filename = f"{symbol}_{timestamp}.html"
            html_filepath = os.path.join(self.output_dirs['articles'], html_filename)
            
            with open(html_filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            output_files['html'] = html_filepath
            
            self.logger.info(f"📁 Output files generated: {len(output_files)} files")
            return output_files
            
        except Exception as e:
            self.logger.error(f"❌ Output file generation failed: {e}")
            return output_files
    
    async def _generate_html_article(self, package: Dict[str, Any]) -> str:
        """Generate HTML article"""
        
        article = package.get('article', {})
        event = package.get('event', {})
        images = package.get('images', {})
        ads = package.get('advertisements', [])
        review = package.get('review_result', {})
        
        # Extract variable to avoid backslash issues in f-string
        newline_br = '<br>'
        
        html_template = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article.get('title', 'Fundamental Agent')}</title>
    <style>
        body {{ font-family: 'Malgun Gothic', sans-serif; line-height: 1.6; margin: 0; padding: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .header {{ background: #f4f4f4; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .title {{ font-size: 24px; font-weight: bold; color: #333; margin-bottom: 10px; }}
        .meta {{ color: #666; font-size: 14px; }}
        .lead {{ font-size: 18px; font-weight: 500; color: #444; margin: 20px 0; }}
        .content {{ margin: 20px 0; }}
        .conclusion {{ background: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .image {{ text-align: center; margin: 20px 0; }}
        .ads {{ background: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .ad-item {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
        .quality-score {{ background: #d4edda; padding: 10px; border-radius: 5px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title">{article.get('title', 'Fundamental Agent')}</div>
            <div class="meta">
                Symbol: {event.get('symbol', 'N/A')} | 
                Event: {event.get('event_type', 'N/A')} | 
                Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            </div>
        </div>
        
        <div class="lead">{article.get('lead', '')}</div>
        
        {f"<div class='image'><img src='{images.get('main_image', '')}' alt='Article Image' style='max-width: 100%; height: auto;'></div>" if images.get('main_image') else ""}
        
        <div class="content">
            {article.get('body', '').replace(chr(10), newline_br)}
        </div>
        
        <div class="conclusion">
            <strong>Conclusion:</strong><br>
            {article.get('conclusion', '')}
        </div>
        
        {f"<div class='quality-score'><strong>Quality Score:</strong> {review.get('overall_score', 'N/A')}/10</div>" if review.get('overall_score') else ""}
        
        <div class="ads">
            <h3>Related Services</h3>
            {"".join([f"<div class='ad-item'><strong>{ad.get('title', '')}</strong>{newline_br}{ad.get('description', '')}{newline_br}<em>{ad.get('cta', '')}</em></div>" for ad in ads[:3]])}
        </div>
        
        <div class="meta" style="margin-top: 30px; text-align: center; color: #999;">
            This article was automatically generated by the Fundamental Agent System.{newline_br}
            We recommend additional analysis and expert consultation for investment decisions.
        </div>
    </div>
</body>
</html>""".strip()
        
        return html_template
    
    async def _generate_streamlit_page(self, package: Dict[str, Any]) -> str:
        """Generate Streamlit page"""
        
        symbol = package['event'].get('symbol', 'Unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"article_{symbol}_{timestamp}.py"
        filepath = os.path.join(self.output_dirs['streamlit'], filename)
        
        try:
            article = package.get('article', {})
            event = package.get('event', {})
            images = package.get('images', {})
            ads = package.get('advertisements', [])
            review = package.get('review_result', {})
            data_analysis = package.get('data_analysis', {})
            
            # Collect chart paths
            chart_paths = data_analysis.get('chart_paths', [])
            
            # Streamlit code template (f-string workaround)
            streamlit_template = '''#!/usr/bin/env python3
"""
Auto-generated economic article page
{symbol} - {title}
"""

import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os

# Page configuration
st.set_page_config(
    page_title="{title}",
    page_icon="\U0001f4c8",
    layout="wide"
)

def main():
    """Main function"""
    
    # Header
    st.title("\U0001f4c8 {title}")
    st.markdown("---")
    
    # Article metadata
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Symbol", "{symbol}")
    
    with col2:
        st.metric("Event", "{event_type}")
    
    with col3:
        st.metric("Quality Score", "{quality_score}/10")
    
    with col4:
        st.metric("Generated At", "{gen_time}")
    
    # Article image
    {image_code}
    
    # Article body
    st.markdown("## \U0001f4f0 Article Content")
    st.markdown("""{lead}

{body}

## Conclusion

{conclusion}

---
*This article was automatically generated by the Fundamental Agent System. We recommend additional analysis and expert consultation for investment decisions.*
""")
    
    # Data charts
    st.markdown("## \U0001f4ca Related Data")
    
    # Display charts
    chart_paths = {chart_paths_list}
    chart_paths = [path for path in chart_paths if os.path.exists(path)]
    
    if chart_paths:
        for i, chart_path in enumerate(chart_paths):
            st.markdown(f"### 📊 Chart {{i+1}}")
            try:
                if chart_path.endswith('.html'):
                    # Display HTML file as iframe
                    with open(chart_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    components.html(html_content, height=600, scrolling=True)
                elif chart_path.endswith(('.png', '.jpg', '.jpeg')):
                    # Display image file
                    st.image(chart_path, caption=f"Chart {{i+1}}", use_column_width=True)
                else:
                    st.info(f"Chart file: {{os.path.basename(chart_path)}}")
            except Exception as e:
                st.error(f"Chart loading error: {{str(e)}}")
                st.info(f"Chart file path: {{chart_path}}")
    else:
        st.info("No charts available for this article.")
    
    # Review results
    {review_code}
    
    # Ad recommendation
    st.markdown("## \U0001f4e2 Related Services")
    ads_data = {ads_data}
    
    if ads_data:
        for i, ad in enumerate(ads_data[:3]):
            with st.expander(f"{{ad.get('title', f'Service {{i+1}}')}}", expanded=False):
                st.write(ad.get('description', ''))
                if ad.get('cta'):
                    st.button(ad.get('cta', 'View Details'), key=f"ad_{{i}}")
    else:
        st.info("No recommended services available.")

if __name__ == "__main__":
    main()
'''
            
            # Prepare template variables
            image_code = ""
            if images.get('article_image'):
                article_image_path = images.get('article_image', '')
                image_code += f'''
    # Article-related image
    if os.path.exists("{article_image_path}"):
        st.image("{article_image_path}", caption="Article Illustration", use_column_width=True)
    '''
            
            if images.get('event_image'):
                event_image_path = images.get('event_image', '')
                image_code += f'''
    if os.path.exists("{event_image_path}"):
        st.image("{event_image_path}", caption="Event Analysis Chart", use_column_width=True)
    '''
            
            if images.get('wordcloud'):
                wordcloud_path = images.get('wordcloud', '')
                image_code += f'''
    if os.path.exists("{wordcloud_path}"):
        st.image("{wordcloud_path}", caption="Article Keyword Word Cloud", use_column_width=True)
    '''
            
            if not image_code:
                image_code = "    # No image"
            
            review_code = ""
            if review:
                review_code = '''st.markdown("## \U0001f50d Review Results")
    st.json(''' + str(review) + ''')'''
            
            # Format template
            streamlit_code = streamlit_template.format(
                symbol=symbol,
                title=article.get('title', 'Fundamental Agent'),
                event_type=event.get('event_type', 'N/A').upper(),
                quality_score=review.get('overall_score', 'N/A'),
                gen_time=datetime.now().strftime('%H:%M'),
                image_code=image_code,
                lead=article.get('lead', ''),
                body=article.get('body', ''),
                conclusion=article.get('conclusion', ''),
                chart_paths_list=chart_paths,
                review_code=review_code,
                ads_data=ads
            )
            
            # Add ad section after article
            ads_section = '''
    # Recommended Services and Products
    
    st.markdown("---")
    st.markdown("### Personalized Recommendations")
    
    ads_data = ''' + str(ads) + '''
    
    if ads_data and len(ads_data) >= 3:
        # Display 3 ads in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ad = ads_data[0]
            st.markdown(f"#### 🔹 {ad.get('title', 'Service 1')}")
            st.write(ad.get('description', ''))
            if ad.get('cta'):
                st.button(ad.get('cta', 'View Details'), key="ad_1", use_container_width=True)
            st.markdown(f"**Category:** {ad.get('category', 'general')}")
            if ad.get('match_reasons'):
                st.markdown(f"**Reason:** {', '.join(ad.get('match_reasons', [])[:2])}")
        
        with col2:
            ad = ads_data[1]
            st.markdown(f"#### 🔹 {ad.get('title', 'Service 2')}")
            st.write(ad.get('description', ''))
            if ad.get('cta'):
                st.button(ad.get('cta', 'View Details'), key="ad_2", use_container_width=True)
            st.markdown(f"**Category:** {ad.get('category', 'general')}")
            if ad.get('match_reasons'):
                st.markdown(f"**Reason:** {', '.join(ad.get('match_reasons', [])[:2])}")
        
        with col3:
            ad = ads_data[2]
            st.markdown(f"#### 🔹 {ad.get('title', 'Service 3')}")
            st.write(ad.get('description', ''))
            if ad.get('cta'):
                st.button(ad.get('cta', 'View Details'), key="ad_3", use_container_width=True)
            st.markdown(f"**Category:** {ad.get('category', 'general')}")
            if ad.get('match_reasons'):
                st.markdown(f"**Reason:** {', '.join(ad.get('match_reasons', [])[:2])}")
    else:
        st.info("No services currently available for recommendation.")
    
    st.markdown("---")
    st.markdown("*The recommendations above were automatically selected by AI based on article content analysis.*")
'''
            
            # Replace existing ad section with the new one
            streamlit_code = streamlit_code.replace(
                '''    # Ad recommendation
    st.markdown("## \U0001f4e2 Related Services")
    ads_data = ''' + str(ads) + '''
    
    if ads_data:
        for i, ad in enumerate(ads_data[:3]):
            with st.expander(f"{ad.get('title', f'Service {i+1}')}", expanded=False):
                st.write(ad.get('description', ''))
                if ad.get('cta'):
                    st.button(ad.get('cta', 'View Details'), key=f"ad_{i}")
    else:
        st.info("No recommended services available.")''',
                ads_section
            )
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(streamlit_code)
            
            self.logger.info(f"📄 Streamlit page generated: {filename}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"❌ Streamlit page generation failed: {e}")
            return ""
    
    async def process_multiple_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process multiple events concurrently"""
        
        self.logger.info(f"🔄 Starting concurrent processing of {len(events)} event(s)")
        
        tasks = []
        for i, event in enumerate(events):
            context = StrandContext(
                strand_id=f"multi_event_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                input_data={'event': event}
            )
            tasks.append(self.process(context))
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_results = []
            failed_count = 0
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"❌ Event {i+1} processing failed: {result}")
                    failed_count += 1
                else:
                    successful_results.append(result)
            
            self.logger.info(f"✅ Multi-event processing completed: {len(successful_results)} succeeded, {failed_count} failed")
            return successful_results
            
        except Exception as e:
            self.logger.error(f"❌ Multi-event processing failed: {e}")
            return []
    
    def get_system_status(self) -> Dict[str, Any]:
        """Query system status"""
        
        return {
            'orchestrator_status': 'active',
            'registered_agents': list(orchestrator.agents.keys()),
            'agent_capabilities': orchestrator.list_agents(),
            'output_directories': self.output_dirs,
            'last_check': datetime.now().isoformat()
        }

# Global orchestrator instance
main_orchestrator = OrchestratorStrand()
