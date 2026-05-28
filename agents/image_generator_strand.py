"""
Image Generation Strand Agent
Generates article-related images based on content
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
from wordcloud import WordCloud
import re

from .strands_framework import BaseStrandAgent, StrandContext, StrandMessage, MessageType

class ImageGeneratorStrand(BaseStrandAgent):
    """Image Generation Strand Agent"""
    
    def __init__(self):
        super().__init__(
            agent_id="image_generator",
            name="Image Generation Agent"
        )
        
        # Set output directory
        self.images_dir = "output/images"
        os.makedirs(self.images_dir, exist_ok=True)
        
        self.capabilities = [
            "article_illustration",
            "data_visualization",
            "wordcloud_generation",
            "chart_annotation",
            "infographic_creation"
        ]
        
        # Image style settings
        plt.style.use('default')
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 12
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return self.capabilities
    
    async def process(self, context: StrandContext, message: Optional[StrandMessage] = None) -> Dict[str, Any]:
        """Process image generation"""
        
        # Collect required data
        event_data = context.input_data.get('event')
        article = await self.get_shared_data(context, 'article')
        data_analysis = await self.get_shared_data(context, 'data_analysis')
        
        if not event_data or not article:
            raise Exception("No data for image generation")
        
        symbol = event_data.get('symbol', 'Unknown')
        event_type = event_data.get('event_type', 'unknown')
        
        self.logger.info("🖼️ Article image generation started")
        
        try:
            # 1. Generate article-based image
            article_image = await self._generate_article_based_image(article, symbol, event_data)
            
            # 2. Generate event-type image
            event_image = None
            if event_type == 'volume_spike':
                event_image = await self._create_volume_spike_image(symbol, event_data, data_analysis)
            elif event_type == 'price_change':
                event_image = await self._create_price_change_image(symbol, event_data, data_analysis)
            elif event_type == 'high_volatility':
                event_image = await self._create_volatility_image(symbol, event_data, data_analysis)
            else:
                event_image = await self._create_default_image(symbol, event_data, article)
            
            # 3. Generate wordcloud
            wordcloud_path = await self._create_wordcloud(article, symbol)
            
            result = {
                'article_image': article_image,  # Article content based image
                'event_image': event_image,      # Event type specific image
                'wordcloud': wordcloud_path,     # Word cloud
                'image_type': event_type,
                'created_at': datetime.now().isoformat()
            }
            
            # Save to shared memory
            await self.set_shared_data(context, 'article_images', result)
            
            self.logger.info(f"✅ Article image generation completed: {len([x for x in result.values() if x and isinstance(x, str) and x.endswith('.png')])}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Image generation failed: {e}")
            raise
    
    async def _generate_article_based_image(self, article: Dict[str, Any], symbol: str, event_data: Dict[str, Any]) -> str:
        """Generate article-based image"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{symbol}_article_illustration_{timestamp}.png"
        filepath = os.path.join(self.images_dir, filename)
        
        try:
            # Extract image prompt from article
            image_prompt = article.get('image_prompt', '')
            
            if not image_prompt:
                # Generate prompt from article content
                title = article.get('title', '')
                body = article.get('body', '')
                
                # Extract keywords
                keywords = []
                if 'price' in body.lower():
                    keywords.append('stock price chart')
                if 'volume' in body.lower():
                    keywords.append('trading volume')
                if 'market' in body.lower():
                    keywords.append('financial market')
                if symbol:
                    keywords.append(f'{symbol} stock')
                
                image_prompt = f"professional financial illustration, {', '.join(keywords)}, modern business style, blue and green color scheme"
            
            # Text-based image generation (information image instead of AI image generation)
            fig, ax = plt.subplots(1, 1, figsize=(12, 8))
            
            # Background settings
            ax.set_facecolor('#f8f9fa')
            fig.patch.set_facecolor('#ffffff')
            
            # Title
            title_text = article.get('title', 'Fundamental Agent')
            ax.text(0.5, 0.85, title_text, ha='center', va='center',
                   fontsize=20, fontweight='bold', transform=ax.transAxes,
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.8))
            
            # Lead summary
            lead_text = article.get('lead', '')[:200] + "..."
            ax.text(0.5, 0.65, lead_text, ha='center', va='center',
                   fontsize=14, transform=ax.transAxes, wrap=True,
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.7))
            
            # Symbol and event info
            info_text = f"Symbol: {symbol}\nEvent: {event_data.get('event_type', 'N/A')}\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            ax.text(0.5, 0.35, info_text, ha='center', va='center',
                   fontsize=12, transform=ax.transAxes,
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.7))
            
            # Image prompt display
            if image_prompt:
                ax.text(0.5, 0.15, f"Image concept: {image_prompt[:100]}...", 
                       ha='center', va='center', fontsize=10, 
                       transform=ax.transAxes, style='italic',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgray', alpha=0.5))
            
            # Decorative elements
            ax.add_patch(patches.Rectangle((0.05, 0.05), 0.9, 0.9, 
                                         linewidth=3, edgecolor='navy', 
                                         facecolor='none', transform=ax.transAxes))
            
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            plt.tight_layout()
            plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            
            self.logger.info(f"📰 Article-based image generated: {filename}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Article-based image generation failed: {e}")
            return await self._create_simple_fallback_image(symbol, "Article Illustration", timestamp)
    
    async def _create_volume_spike_image(self, symbol: str, event_data: Dict[str, Any], data_analysis: Optional[Dict[str, Any]]) -> str:
        """Create volume spike image"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{symbol}_volume_spike_{timestamp}.png"
        filepath = os.path.join(self.images_dir, filename)
        
        try:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            
            # Top: Volume comparison chart
            if data_analysis and data_analysis.get('statistics', {}).get('volume_ratio'):
                volume_ratio = data_analysis['statistics']['volume_ratio']
                
                categories = ['Avg Volume', 'Current Volume']
                values = [1.0, volume_ratio]
                colors = ['lightblue', 'red' if volume_ratio > 2 else 'orange']
                
                bars = ax1.bar(categories, values, color=colors, alpha=0.7)
                ax1.set_title(f'{symbol} Volume Comparison', fontsize=16, fontweight='bold')
                ax1.set_ylabel('Volume Ratio')
                ax1.grid(True, alpha=0.3)
                
                # Value display
                for bar, value in zip(bars, values):
                    height = bar.get_height()
                    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                            f'{value:.1f}x', ha='center', va='bottom', fontweight='bold')
            
            # Bottom: Event info
            ax2.axis('off')
            
            # Info box creation
            info_text = f"""
Volume Spike Event

Symbol: {symbol}
Event Time: {event_data.get('timestamp', 'Unknown')[:19]}
Severity: {event_data.get('severity', 'Unknown').upper()}
Description: {event_data.get('description', 'N/A')}
            """.strip()
            
            # Add text box
            props = dict(boxstyle='round', facecolor='lightgray', alpha=0.8)
            ax2.text(0.05, 0.95, info_text, transform=ax2.transAxes, fontsize=11,
                    verticalalignment='top', bbox=props, family='monospace')
            
            plt.tight_layout()
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Volume spike image generation failed: {e}")
            # 간단한 폴백 이미지 생성
            return await self._create_simple_fallback_image(symbol, "Volume Spike", timestamp)
    
    async def _create_price_change_image(self, symbol: str, event_data: Dict[str, Any], data_analysis: Optional[Dict[str, Any]]) -> str:
        """Create price change image"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{symbol}_price_change_{timestamp}.png"
        filepath = os.path.join(self.images_dir, filename)
        
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
            
            # Left: Price change arrow
            change_percent = event_data.get('change_percent', 0)
            
            if change_percent > 0:
                # Up arrow
                ax1.arrow(0.5, 0.2, 0, 0.6, head_width=0.1, head_length=0.1, 
                         fc='green', ec='green', linewidth=3)
                ax1.text(0.5, 0.1, f'+{change_percent:.1f}%', ha='center', va='center',
                        fontsize=20, fontweight='bold', color='green')
                direction_text = "rise"
                color = 'green'
            else:
                # Down arrow
                ax1.arrow(0.5, 0.8, 0, -0.6, head_width=0.1, head_length=0.1,
                         fc='red', ec='red', linewidth=3)
                ax1.text(0.5, 0.9, f'{change_percent:.1f}%', ha='center', va='center',
                        fontsize=20, fontweight='bold', color='red')
                direction_text = "decline"
                color = 'red'
            
            ax1.set_xlim(0, 1)
            ax1.set_ylim(0, 1)
            ax1.set_title(f'{symbol} Price {direction_text}', fontsize=16, fontweight='bold')
            ax1.axis('off')
            
            # Right: Technical info
            ax2.axis('off')
            
            info_lines = [f"{symbol} Price Change Analysis", ""]
            
            if data_analysis:
                raw_data = data_analysis.get('raw_data', {})
                if raw_data.get('current_price'):
                    info_lines.append(f"Current Price: ${raw_data['current_price']:.2f}")
                
                technical = data_analysis.get('technical_indicators', {})
                if technical.get('rsi'):
                    rsi = technical['rsi']
                    rsi_status = "overbought" if rsi > 70 else "oversold" if rsi < 30 else "neutral"
                    info_lines.append(f"RSI: {rsi:.1f} ({rsi_status})")
                
                if technical.get('sma_20'):
                    info_lines.append(f"20-day SMA: ${technical['sma_20']:.2f}")
            
            info_lines.extend(["", f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}"])
            
            info_text = "\n".join(info_lines)
            ax2.text(0.05, 0.95, info_text, transform=ax2.transAxes, fontsize=12,
                    verticalalignment='top', family='monospace')
            
            plt.tight_layout()
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Price change image creation failed: {e}")
            return await self._create_simple_fallback_image(symbol, "Price Change", timestamp)
    
    async def _create_volatility_image(self, symbol: str, event_data: Dict[str, Any], data_analysis: Optional[Dict[str, Any]]) -> str:
        """Create volatility image"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{symbol}_volatility_{timestamp}.png"
        filepath = os.path.join(self.images_dir, filename)
        
        try:
            fig, ax = plt.subplots(1, 1, figsize=(10, 8))
            
            # Volatility gauge creation
            if data_analysis and data_analysis.get('statistics', {}).get('volatility_annualized'):
                volatility = data_analysis['statistics']['volatility_annualized'] * 100
            else:
                volatility = 25.0  # 기본값
            
            # Gauge chart creation
            theta = np.linspace(0, np.pi, 100)
            
            # Background arc
            ax.plot(np.cos(theta), np.sin(theta), 'k-', linewidth=8, alpha=0.3)
            
            # Color sections by volatility level
            low_theta = theta[theta <= np.pi/3]
            med_theta = theta[(theta > np.pi/3) & (theta <= 2*np.pi/3)]
            high_theta = theta[theta > 2*np.pi/3]
            
            ax.plot(np.cos(low_theta), np.sin(low_theta), 'g-', linewidth=8, label='Low (0-20%)')
            ax.plot(np.cos(med_theta), np.sin(med_theta), 'y-', linewidth=8, label='Medium (20-40%)')
            ax.plot(np.cos(high_theta), np.sin(high_theta), 'r-', linewidth=8, label='High (40%+)')
            
            # Current volatility position indicator
            vol_angle = np.pi * (1 - min(volatility / 60, 1))  # 60%를 최대로 정규화
            needle_x = np.cos(vol_angle)
            needle_y = np.sin(vol_angle)
            
            ax.arrow(0, 0, needle_x*0.8, needle_y*0.8, head_width=0.05, head_length=0.05,
                    fc='black', ec='black', linewidth=3)
            
            # Central volatility value display
            ax.text(0, -0.3, f'{volatility:.1f}%', ha='center', va='center',
                   fontsize=24, fontweight='bold')
            ax.text(0, -0.45, 'Annualized Volatility', ha='center', va='center',
                   fontsize=14)
            
            ax.set_xlim(-1.2, 1.2)
            ax.set_ylim(-0.6, 1.2)
            ax.set_aspect('equal')
            ax.axis('off')
            ax.set_title(f'{symbol} Volatility Analysis', fontsize=18, fontweight='bold', pad=20)
            ax.legend(loc='upper right')
            
            # Additional info text
            info_text = f"""
Volatility Level: {'High' if volatility > 40 else 'Medium' if volatility > 20 else 'Low'}
Risk Level: {'High Risk' if volatility > 40 else 'Medium Risk' if volatility > 20 else 'Low Risk'}
Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            """.strip()
            
            ax.text(-1.1, -0.5, info_text, fontsize=10, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
            
            plt.tight_layout()
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Volatility image creation failed: {e}")
            return await self._create_simple_fallback_image(symbol, "Volatility Analysis", timestamp)
    
    async def _create_default_image(self, symbol: str, event_data: Dict[str, Any], article: Dict[str, Any]) -> str:
        """Create default image"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{symbol}_default_{timestamp}.png"
        filepath = os.path.join(self.images_dir, filename)
        
        try:
            fig, ax = plt.subplots(1, 1, figsize=(10, 6))
            
            # Simple info display image
            ax.text(0.5, 0.7, symbol, ha='center', va='center',
                   fontsize=36, fontweight='bold', transform=ax.transAxes)
            
            ax.text(0.5, 0.5, article.get('title', 'Fundamental Agent'), ha='center', va='center',
                   fontsize=16, transform=ax.transAxes, wrap=True)
            
            ax.text(0.5, 0.3, f"Event: {event_data.get('event_type', 'Unknown')}", 
                   ha='center', va='center', fontsize=14, transform=ax.transAxes)
            
            ax.text(0.5, 0.1, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                   ha='center', va='center', fontsize=12, transform=ax.transAxes)
            
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            # Background color
            ax.add_patch(patches.Rectangle((0, 0), 1, 1, facecolor='lightblue', alpha=0.3))
            
            plt.tight_layout()
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Default image creation failed: {e}")
            return await self._create_simple_fallback_image(symbol, "Fundamental Agent", timestamp)
    
    async def _create_wordcloud(self, article: Dict[str, Any], symbol: str) -> Optional[str]:
        """Create wordcloud"""
        
        try:
            # Extract article text
            text_parts = []
            if article.get('title'):
                text_parts.append(article['title'])
            if article.get('body'):
                text_parts.append(article['body'])
            if article.get('conclusion'):
                text_parts.append(article['conclusion'])
            
            full_text = ' '.join(text_parts)
            
            if not full_text or len(full_text) < 50:
                return None
            
            # Stopword removal and text cleaning
            stopwords = {
                'the', 'a', 'an', 'in', 'on', 'of', 'to', 'for', 'and', 'or',
                'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
                'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
                'may', 'might', 'shall', 'can', 'need', 'dare', 'ought', 'used'
            }
            
            # Extract only Korean and English
            clean_text = re.sub(r'[^가-힣a-zA-Z\s]', ' ', full_text)
            words = clean_text.split()
            filtered_words = [word for word in words if len(word) > 1 and word not in stopwords]
            
            if len(filtered_words) < 10:
                return None
            
            # Wordcloud generation
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{symbol}_wordcloud_{timestamp}.png"
            filepath = os.path.join(self.images_dir, filename)
            
            wordcloud = WordCloud(
                width=800, height=400,
                background_color='white',
                max_words=50,
                font_path=None,  # 시스템 기본 폰트 사용
                colormap='viridis'
            ).generate(' '.join(filtered_words))
            
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title(f'{symbol} Article Keywords', fontsize=16, fontweight='bold', pad=20)
            plt.tight_layout()
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Wordcloud creation failed: {e}")
            return None
    
    async def _create_simple_fallback_image(self, symbol: str, title: str, timestamp: str) -> str:
        """Create simple fallback image"""
        
        filename = f"{symbol}_fallback_{timestamp}.png"
        filepath = os.path.join(self.images_dir, filename)
        
        try:
            fig, ax = plt.subplots(1, 1, figsize=(8, 6))
            
            ax.text(0.5, 0.6, symbol, ha='center', va='center',
                   fontsize=32, fontweight='bold', transform=ax.transAxes)
            
            ax.text(0.5, 0.4, title, ha='center', va='center',
                   fontsize=18, transform=ax.transAxes)
            
            ax.text(0.5, 0.2, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                   ha='center', va='center', fontsize=12, transform=ax.transAxes)
            
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            plt.tight_layout()
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Fallback image creation failed: {e}")
            # Last resort: create empty file
            with open(filepath, 'w') as f:
                f.write("Image generation failed")
            return filepath
