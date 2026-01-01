"""LLM-based paper analysis module using OpenAI API.

This module provides functionality to:
- Analyze papers using OpenAI's GPT models
- Extract technical insights and key findings
- Identify MiroFish integration points
- Generate structured summaries and recommendations
"""

import os
import json
import logging
from typing import List, Dict, Optional, Any
from pathlib import Path
import time
import openai
from openai import OpenAI


logger = logging.getLogger(__name__)


class LLMAnalyzer:
    """Analyzes academic papers using OpenAI's language models."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview",
                 cache_dir: str = "./cache/llm"):
        """Initialize the LLM analyzer.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: OpenAI model to use
            cache_dir: Directory to cache analysis results
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY env var")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, paper_id: str, analysis_type: str) -> Path:
        """Get cache file path for an analysis."""
        return self.cache_dir / f"{paper_id}_{analysis_type}.json"
    
    def _load_from_cache(self, paper_id: str, analysis_type: str) -> Optional[Dict]:
        """Load cached analysis if available."""
        cache_path = self._get_cache_path(paper_id, analysis_type)
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    logger.info(f"Loading cached analysis: {cache_path}")
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"Invalid cache file: {cache_path}")
        return None
    
    def _save_to_cache(self, paper_id: str, analysis_type: str, data: Dict) -> None:
        """Save analysis to cache."""
        cache_path = self._get_cache_path(paper_id, analysis_type)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved analysis to cache: {cache_path}")
    
    def _call_openai(self, messages: List[Dict[str, str]], 
                     temperature: float = 0.3,
                     max_tokens: int = 2000) -> str:
        """Make a call to OpenAI API with error handling."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def analyze_paper(self, paper: Dict[str, Any], use_cache: bool = True) -> Dict[str, Any]:
        """Perform comprehensive analysis of a paper.
        
        Args:
            paper: Paper dictionary with title, abstract, and other metadata
            use_cache: Whether to use cached results
            
        Returns:
            Dictionary containing analysis results
        """
        paper_id = paper.get('paperId', paper.get('id', 'unknown'))
        
        # Check cache
        if use_cache:
            cached = self._load_from_cache(paper_id, 'comprehensive')
            if cached:
                return cached
        
        title = paper.get('title', 'No title')
        abstract = paper.get('abstract', paper.get('summary', 'No abstract available'))
        
        prompt = f"""Analyze the following academic paper and provide a comprehensive analysis:

Title: {title}

Abstract: {abstract}

Please provide:
1. **Key Contributions**: Main contributions and innovations
2. **Technical Approach**: Methods, algorithms, or techniques used
3. **Strengths**: What makes this work valuable
4. **Limitations**: Potential weaknesses or gaps
5. **Relevance Score** (1-10): How relevant is this to software architecture validation
6. **Integration Opportunities**: Specific ways this could integrate with MiroFish (a software architecture validation framework)

Format your response as JSON with the following structure:
{{
  "key_contributions": ["contribution1", "contribution2", ...],
  "technical_approach": "description",
  "strengths": ["strength1", "strength2", ...],
  "limitations": ["limitation1", "limitation2", ...],
  "relevance_score": <number>,
  "integration_opportunities": ["opportunity1", "opportunity2", ...],
  "summary": "brief summary"
}}"""
        
        messages = [
            {"role": "system", "content": "You are an expert in software architecture and research analysis. Provide detailed, technical insights."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            logger.info(f"Analyzing paper: {title}")
            response = self._call_openai(messages, temperature=0.3)
            
            # Parse JSON response
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
            
            analysis = json.loads(response)
            analysis['paper_id'] = paper_id
            analysis['analyzed_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            
            # Save to cache
            if use_cache:
                self._save_to_cache(paper_id, 'comprehensive', analysis)
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response was: {response}")
            return {
                'error': 'Failed to parse analysis',
                'raw_response': response
            }
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {'error': str(e)}
    
    def extract_mirofish_integration_points(self, paper: Dict[str, Any], 
                                           use_cache: bool = True) -> Dict[str, Any]:
        """Extract specific MiroFish integration points from a paper.
        
        Args:
            paper: Paper dictionary
            use_cache: Whether to use cached results
            
        Returns:
            Dictionary with integration recommendations
        """
        paper_id = paper.get('paperId', paper.get('id', 'unknown'))
        
        # Check cache
        if use_cache:
            cached = self._load_from_cache(paper_id, 'mirofish')
            if cached:
                return cached
        
        title = paper.get('title', 'No title')
        abstract = paper.get('abstract', paper.get('summary', 'No abstract available'))
        
        prompt = f"""Given the following academic paper, identify specific integration points with MiroFish, a software architecture validation framework.

MiroFish Context:
- Validates software architectures against quality attributes
- Uses AI/ML for pattern recognition and anomaly detection
- Provides automated architecture analysis and recommendations
- Supports multiple architecture styles and views

Paper:
Title: {title}
Abstract: {abstract}

Provide specific integration recommendations in JSON format:
{{
  "validation_techniques": ["technique1", "technique2"],
  "ai_ml_applications": ["application1", "application2"],
  "architecture_patterns": ["pattern1", "pattern2"],
  "quality_attributes": ["attribute1", "attribute2"],
  "implementation_steps": ["step1", "step2"],
  "expected_benefits": ["benefit1", "benefit2"],
  "challenges": ["challenge1", "challenge2"],
  "priority": "high|medium|low"
}}"""
        
        messages = [
            {"role": "system", "content": "You are an expert in software architecture validation and framework integration."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            logger.info(f"Extracting MiroFish integration points: {title}")
            response = self._call_openai(messages, temperature=0.2)
            
            # Parse JSON response
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
            
            integration = json.loads(response)
            integration['paper_id'] = paper_id
            integration['analyzed_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            
            # Save to cache
            if use_cache:
                self._save_to_cache(paper_id, 'mirofish', integration)
            
            return integration
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return {
                'error': 'Failed to parse integration points',
                'raw_response': response
            }
        except Exception as e:
            logger.error(f"Integration analysis failed: {e}")
            return {'error': str(e)}
    
    def batch_analyze(self, papers: List[Dict[str, Any]], 
                     analysis_type: str = 'comprehensive',
                     delay: float = 1.0) -> List[Dict[str, Any]]:
        """Analyze multiple papers in batch.
        
        Args:
            papers: List of paper dictionaries
            analysis_type: Type of analysis ('comprehensive' or 'mirofish')
            delay: Delay between API calls to respect rate limits
            
        Returns:
            List of analysis results
        """
        results = []
        total = len(papers)
        
        for i, paper in enumerate(papers, 1):
            logger.info(f"Analyzing paper {i}/{total}")
            
            try:
                if analysis_type == 'mirofish':
                    result = self.extract_mirofish_integration_points(paper)
                else:
                    result = self.analyze_paper(paper)
                
                results.append(result)
                
                # Rate limiting
                if i < total:
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Failed to analyze paper {i}: {e}")
                results.append({
                    'paper_id': paper.get('paperId', paper.get('id', 'unknown')),
                    'error': str(e)
                })
        
        return results
    
    def summarize_findings(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize findings from multiple paper analyses.
        
        Args:
            analyses: List of analysis results
            
        Returns:
            Summary dictionary
        """
        prompt = f"""Summarize the following research paper analyses into a cohesive overview:

{json.dumps(analyses, indent=2)}

Provide:
1. **Overall Themes**: Common themes across papers
2. **Key Insights**: Most important technical insights
3. **Research Gaps**: Areas that need more investigation
4. **Recommendations**: Prioritized recommendations for MiroFish integration

Format as JSON:
{{
  "overall_themes": ["theme1", "theme2"],
  "key_insights": ["insight1", "insight2"],
  "research_gaps": ["gap1", "gap2"],
  "recommendations": [{{
    "priority": "high|medium|low",
    "title": "recommendation title",
    "description": "detailed description"
  }}]
}}"""
        
        messages = [
            {"role": "system", "content": "You are a research synthesis expert."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self._call_openai(messages, temperature=0.4, max_tokens=3000)
            
            # Parse JSON response
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
            
            summary = json.loads(response)
            return summary
            
        except Exception as e:
            logger.error(f"Failed to summarize findings: {e}")
            return {'error': str(e)}
