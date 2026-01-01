"""Paper collection module for gathering papers from Semantic Scholar and arXiv APIs.

This module provides functionality to:
- Query Semantic Scholar and arXiv APIs
- Implement retry logic with exponential backoff
- Cache API responses to minimize redundant requests
- Track progress for long-running collection tasks
"""

import time
import json
import logging
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import hashlib


logger = logging.getLogger(__name__)


class PaperCollector:
    """Collects academic papers from multiple sources with caching and retry logic."""
    
    SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1"
    ARXIV_API = "http://export.arxiv.org/api/query"
    
    def __init__(self, cache_dir: str = "./cache", api_key: Optional[str] = None):
        """Initialize the paper collector.
        
        Args:
            cache_dir: Directory to store cached API responses
            api_key: Optional Semantic Scholar API key for higher rate limits
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.api_key = api_key
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()
        retry_strategy = Retry(
            total=5,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def _get_cache_key(self, query: str, source: str) -> str:
        """Generate a cache key for a query."""
        key_string = f"{source}:{query}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _load_from_cache(self, cache_key: str, max_age_hours: int = 24) -> Optional[Dict]:
        """Load cached data if it exists and is not expired."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        # Check cache age
        file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
        if datetime.now() - file_time > timedelta(hours=max_age_hours):
            logger.info(f"Cache expired for key {cache_key}")
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                logger.info(f"Loading from cache: {cache_key}")
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"Invalid cache file: {cache_file}")
            return None
    
    def _save_to_cache(self, cache_key: str, data: Dict) -> None:
        """Save data to cache."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved to cache: {cache_key}")
    
    def search_semantic_scholar(self, query: str, limit: int = 100, 
                                fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search Semantic Scholar for papers.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            fields: List of fields to include in response
            
        Returns:
            List of paper dictionaries
        """
        if fields is None:
            fields = [
                'paperId', 'title', 'abstract', 'year', 'authors',
                'citationCount', 'referenceCount', 'publicationDate',
                'venue', 'url', 'citations', 'references'
            ]
        
        cache_key = self._get_cache_key(f"{query}:{limit}:{','.join(fields)}", "semantic_scholar")
        
        # Try to load from cache
        cached_data = self._load_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        # Make API request
        url = f"{self.SEMANTIC_SCHOLAR_API}/paper/search"
        headers = {}
        if self.api_key:
            headers['x-api-key'] = self.api_key
        
        all_papers = []
        offset = 0
        
        with requests.Session() as session:
            while len(all_papers) < limit:
                params = {
                    'query': query,
                    'limit': min(100, limit - len(all_papers)),
                    'offset': offset,
                    'fields': ','.join(fields)
                }
                
                try:
                    logger.info(f"Querying Semantic Scholar (offset={offset})...")
                    response = session.get(url, params=params, headers=headers, timeout=30)
                    response.raise_for_status()
                    
                    data = response.json()
                    papers = data.get('data', [])
                    
                    if not papers:
                        break
                    
                    all_papers.extend(papers)
                    offset += len(papers)
                    
                    # Rate limiting - be respectful
                    time.sleep(1)
                    
                except requests.exceptions.RequestException as e:
                    logger.error(f"Error querying Semantic Scholar: {e}")
                    break
        
        # Save to cache
        self._save_to_cache(cache_key, all_papers)
        logger.info(f"Collected {len(all_papers)} papers from Semantic Scholar")
        
        return all_papers
    
    def search_arxiv(self, query: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Search arXiv for papers.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of paper dictionaries
        """
        cache_key = self._get_cache_key(f"{query}:{max_results}", "arxiv")
        
        # Try to load from cache
        cached_data = self._load_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        # Make API request
        params = {
            'search_query': query,
            'start': 0,
            'max_results': max_results,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        try:
            logger.info(f"Querying arXiv for: {query}")
            response = self.session.get(self.ARXIV_API, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse XML response
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            # Namespace handling
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            papers = []
            for entry in root.findall('atom:entry', ns):
                paper = {
                    'id': entry.find('atom:id', ns).text,
                    'title': entry.find('atom:title', ns).text.strip(),
                    'summary': entry.find('atom:summary', ns).text.strip(),
                    'published': entry.find('atom:published', ns).text,
                    'updated': entry.find('atom:updated', ns).text,
                    'authors': [author.find('atom:name', ns).text 
                               for author in entry.findall('atom:author', ns)],
                    'url': entry.find('atom:id', ns).text
                }
                papers.append(paper)
            
            # Save to cache
            self._save_to_cache(cache_key, papers)
            logger.info(f"Collected {len(papers)} papers from arXiv")
            
            return papers
            
        except Exception as e:
            logger.error(f"Error querying arXiv: {e}")
            return []
    
    def get_paper_details(self, paper_id: str, source: str = "semantic_scholar") -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific paper.
        
        Args:
            paper_id: Paper identifier
            source: Source API ('semantic_scholar' or 'arxiv')
            
        Returns:
            Paper details dictionary or None if not found
        """
        cache_key = self._get_cache_key(f"details:{paper_id}", source)
        
        # Try to load from cache
        cached_data = self._load_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        if source == "semantic_scholar":
            url = f"{self.SEMANTIC_SCHOLAR_API}/paper/{paper_id}"
            headers = {}
            if self.api_key:
                headers['x-api-key'] = self.api_key
            
            try:
                response = self.session.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                paper = response.json()
                
                # Save to cache
                self._save_to_cache(cache_key, paper)
                return paper
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching paper details: {e}")
                return None
        
        return None
    
    def collect_citation_network(self, seed_paper_ids: List[str], 
                                 depth: int = 2) -> Dict[str, Any]:
        """Collect citation network starting from seed papers.
        
        Args:
            seed_paper_ids: List of paper IDs to start from
            depth: How many citation levels to traverse
            
        Returns:
            Dictionary containing papers and citation relationships
        """
        papers = {}
        citations = []
        visited = set()
        to_visit = [(pid, 0) for pid in seed_paper_ids]
        
        while to_visit:
            paper_id, current_depth = to_visit.pop(0)
            
            if paper_id in visited or current_depth >= depth:
                continue
            
            visited.add(paper_id)
            
            # Get paper details
            paper = self.get_paper_details(paper_id)
            if not paper:
                continue
            
            papers[paper_id] = paper
            
            # Add citations
            if 'citations' in paper and current_depth < depth - 1:
                for cited_paper in paper.get('citations', [])[:10]:  # Limit to avoid explosion
                    cited_id = cited_paper.get('paperId')
                    if cited_id:
                        citations.append({'from': paper_id, 'to': cited_id})
                        to_visit.append((cited_id, current_depth + 1))
            
            # Rate limiting
            time.sleep(1)
            
            logger.info(f"Progress: {len(visited)} papers collected")
        
        return {
            'papers': papers,
            'citations': citations,
            'metadata': {
                'seed_papers': seed_paper_ids,
                'depth': depth,
                'total_papers': len(papers),
                'total_citations': len(citations),
                'collected_at': datetime.now().isoformat()
            }
        }
