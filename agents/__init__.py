"""
Fundamental Agent System built on the Strand Agent framework
"""

# Strands framework
from .strands_framework import BaseStrandAgent, StrandContext, StrandMessage, MessageType, StrandOrchestrator, orchestrator

# Strand Agents
try:
    from .data_analysis_strand import DataAnalysisStrand
    from .article_writer_strand import ArticleWriterStrand
    from .review_strand import ReviewStrand
    from .image_generator_strand import ImageGeneratorStrand
    from .ad_recommendation_strand import AdRecommendationStrand
    from .orchestrator_strand import OrchestratorStrand, main_orchestrator
    
    __all__ = [
        # Framework
        'BaseStrandAgent',
        'StrandContext', 
        'StrandMessage',
        'MessageType',
        'StrandOrchestrator',
        'orchestrator',
        
        # Strand Agents
        'DataAnalysisStrand',
        'ArticleWriterStrand', 
        'ReviewStrand',
        'ImageGeneratorStrand',
        'AdRecommendationStrand',
        'OrchestratorStrand',
        'main_orchestrator'
    ]
    
except ImportError as e:
    print(f"⚠️ Agent import error: {e}")
    
    # Export only basic framework
    __all__ = [
        'BaseStrandAgent',
        'StrandContext', 
        'StrandMessage',
        'MessageType',
        'StrandOrchestrator',
        'orchestrator'
    ]
