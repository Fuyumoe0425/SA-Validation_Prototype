"""Visualization module for generating charts and network graphs.

This module provides functionality to:
- Generate citation network visualizations
- Create timeline charts of research developments
- Produce architecture diagrams
- Export interactive visualizations using matplotlib, networkx, and plotly
"""

import logging
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
import json
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import numpy as np
from collections import Counter, defaultdict

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    logging.warning("Plotly not available. Interactive visualizations will be disabled.")


logger = logging.getLogger(__name__)


class Visualizer:
    """Creates visualizations for research paper analysis."""
    
    def __init__(self, output_dir: str = "./visualizations"):
        """Initialize the visualizer.
        
        Args:
            output_dir: Directory to save visualization outputs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style for matplotlib
        plt.style.use('seaborn-v0_8-darkgrid' if 'seaborn-v0_8-darkgrid' in plt.style.available else 'default')
    
    def create_citation_network(self, papers: Dict[str, Any], 
                               citations: List[Dict[str, str]],
                               output_file: str = "citation_network.png",
                               interactive: bool = True) -> None:
        """Create a citation network visualization.
        
        Args:
            papers: Dictionary of papers {paper_id: paper_data}
            citations: List of citation edges {from: paper_id, to: paper_id}
            output_file: Output filename
            interactive: Whether to create interactive plotly version
        """
        # Create directed graph
        G = nx.DiGraph()
        
        # Add nodes
        for paper_id, paper in papers.items():
            G.add_node(paper_id, 
                      title=paper.get('title', 'Unknown'),
                      year=paper.get('year', 0),
                      citations=paper.get('citationCount', 0))
        
        # Add edges
        for citation in citations:
            if citation['from'] in G.nodes and citation['to'] in G.nodes:
                G.add_edge(citation['from'], citation['to'])
        
        logger.info(f"Citation network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        
        if interactive and PLOTLY_AVAILABLE:
            self._create_interactive_network(G, output_file.replace('.png', '.html'))
        
        # Create static visualization
        fig, ax = plt.subplots(figsize=(16, 12))
        
        # Use spring layout for positioning
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
        
        # Node sizes based on citation count
        node_sizes = [G.nodes[node].get('citations', 1) * 10 + 100 for node in G.nodes()]
        
        # Node colors based on year
        years = [G.nodes[node].get('year', 2020) for node in G.nodes()]
        
        # Draw network
        nx.draw_networkx_edges(G, pos, alpha=0.3, edge_color='gray', 
                              arrows=True, arrowsize=10, ax=ax)
        nodes = nx.draw_networkx_nodes(G, pos, node_size=node_sizes, 
                                      node_color=years, cmap='viridis',
                                      alpha=0.8, ax=ax)
        
        # Add colorbar for years
        if years:
            plt.colorbar(nodes, ax=ax, label='Publication Year')
        
        ax.set_title('Citation Network', fontsize=16, fontweight='bold')
        ax.axis('off')
        
        plt.tight_layout()
        output_path = self.output_dir / output_file
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved citation network to {output_path}")
    
    def _create_interactive_network(self, G: nx.DiGraph, output_file: str) -> None:
        """Create interactive network visualization using plotly."""
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
        
        # Create edge traces
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Create node traces
        node_x = []
        node_y = []
        node_text = []
        node_size = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            title = G.nodes[node].get('title', 'Unknown')
            year = G.nodes[node].get('year', 'N/A')
            citations = G.nodes[node].get('citations', 0)
            
            node_text.append(f"{title[:50]}...<br>Year: {year}<br>Citations: {citations}")
            node_size.append(np.sqrt(citations) * 5 + 10)
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            text=node_text,
            marker=dict(
                size=node_size,
                color=[G.nodes[node].get('year', 2020) for node in G.nodes()],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title='Year')
            )
        )
        
        # Create figure
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title='Interactive Citation Network',
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=0, l=0, r=0, t=40),
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                       ))
        
        output_path = self.output_dir / output_file
        fig.write_html(str(output_path))
        logger.info(f"Saved interactive network to {output_path}")
    
    def create_timeline_chart(self, papers: List[Dict[str, Any]], 
                             output_file: str = "timeline.png") -> None:
        """Create a timeline chart of papers by year.
        
        Args:
            papers: List of paper dictionaries
            output_file: Output filename
        """
        # Extract years
        years = []
        for paper in papers:
            year = paper.get('year')
            if year:
                years.append(int(year))
        
        if not years:
            logger.warning("No year information available for timeline")
            return
        
        # Count papers by year
        year_counts = Counter(years)
        sorted_years = sorted(year_counts.keys())
        counts = [year_counts[year] for year in sorted_years]
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(14, 6))
        
        ax.bar(sorted_years, counts, color='steelblue', alpha=0.7, edgecolor='black')
        ax.plot(sorted_years, counts, color='darkred', marker='o', linewidth=2, markersize=6)
        
        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Papers', fontsize=12, fontweight='bold')
        ax.set_title('Research Timeline: Papers by Year', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Add value labels on bars
        for year, count in zip(sorted_years, counts):
            ax.text(year, count + 0.5, str(count), ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        output_path = self.output_dir / output_file
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved timeline chart to {output_path}")
    
    def create_relevance_distribution(self, analyses: List[Dict[str, Any]],
                                     output_file: str = "relevance_distribution.png") -> None:
        """Create a distribution chart of relevance scores.
        
        Args:
            analyses: List of paper analysis results
            output_file: Output filename
        """
        scores = [a.get('relevance_score', 0) for a in analyses if 'relevance_score' in a]
        
        if not scores:
            logger.warning("No relevance scores available")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Histogram
        ax1.hist(scores, bins=10, color='teal', alpha=0.7, edgecolor='black')
        ax1.set_xlabel('Relevance Score', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Frequency', fontsize=12, fontweight='bold')
        ax1.set_title('Distribution of Relevance Scores', fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3, linestyle='--')
        
        # Box plot
        ax2.boxplot(scores, vert=True)
        ax2.set_ylabel('Relevance Score', fontsize=12, fontweight='bold')
        ax2.set_title('Relevance Score Statistics', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3, linestyle='--')
        
        # Add statistics
        stats_text = f"Mean: {np.mean(scores):.2f}\nMedian: {np.median(scores):.2f}\nStd: {np.std(scores):.2f}"
        ax2.text(1.15, np.mean(scores), stats_text, fontsize=10, 
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        output_path = self.output_dir / output_file
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved relevance distribution to {output_path}")
    
    def create_architecture_diagram(self, components: List[Dict[str, str]],
                                   connections: List[Dict[str, str]],
                                   output_file: str = "architecture.png") -> None:
        """Create an architecture diagram.
        
        Args:
            components: List of components with 'name' and 'type'
            connections: List of connections with 'from' and 'to'
            output_file: Output filename
        """
        G = nx.DiGraph()
        
        # Add nodes with types
        for comp in components:
            G.add_node(comp['name'], comp_type=comp.get('type', 'component'))
        
        # Add edges
        for conn in connections:
            if conn['from'] in G.nodes and conn['to'] in G.nodes:
                G.add_edge(conn['from'], conn['to'])
        
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Layout
        pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
        
        # Color map for component types
        type_colors = {
            'data': 'lightblue',
            'service': 'lightgreen',
            'api': 'lightyellow',
            'ui': 'lightcoral',
            'component': 'lightgray'
        }
        
        node_colors = [type_colors.get(G.nodes[node].get('comp_type', 'component'), 'lightgray') 
                      for node in G.nodes()]
        
        # Draw
        nx.draw_networkx_edges(G, pos, alpha=0.5, edge_color='gray', 
                              arrows=True, arrowsize=20, ax=ax, width=2)
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                              node_size=3000, alpha=0.9, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', ax=ax)
        
        # Legend
        legend_patches = [mpatches.Patch(color=color, label=comp_type.capitalize()) 
                         for comp_type, color in type_colors.items()]
        ax.legend(handles=legend_patches, loc='upper left', fontsize=10)
        
        ax.set_title('System Architecture Diagram', fontsize=16, fontweight='bold')
        ax.axis('off')
        
        plt.tight_layout()
        output_path = self.output_dir / output_file
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved architecture diagram to {output_path}")
    
    def create_summary_dashboard(self, papers: List[Dict[str, Any]],
                                analyses: List[Dict[str, Any]],
                                output_file: str = "dashboard.html") -> None:
        """Create an interactive dashboard summarizing all data.
        
        Args:
            papers: List of papers
            analyses: List of analysis results
            output_file: Output filename
        """
        if not PLOTLY_AVAILABLE:
            logger.warning("Plotly not available. Cannot create dashboard.")
            return
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Papers by Year', 'Relevance Scores', 
                          'Top Venues', 'Citation Counts'),
            specs=[[{'type': 'bar'}, {'type': 'box'}],
                   [{'type': 'bar'}, {'type': 'scatter'}]]
        )
        
        # Papers by year
        years = [p.get('year') for p in papers if p.get('year')]
        if years:
            year_counts = Counter(years)
            fig.add_trace(
                go.Bar(x=list(year_counts.keys()), y=list(year_counts.values()),
                      name='Papers', marker_color='steelblue'),
                row=1, col=1
            )
        
        # Relevance scores
        scores = [a.get('relevance_score', 0) for a in analyses if 'relevance_score' in a]
        if scores:
            fig.add_trace(
                go.Box(y=scores, name='Relevance', marker_color='teal'),
                row=1, col=2
            )
        
        # Top venues
        venues = [p.get('venue', 'Unknown') for p in papers if p.get('venue')]
        if venues:
            venue_counts = Counter(venues).most_common(10)
            fig.add_trace(
                go.Bar(y=[v[0] for v in venue_counts], x=[v[1] for v in venue_counts],
                      orientation='h', name='Venues', marker_color='lightgreen'),
                row=2, col=1
            )
        
        # Citation counts
        citations = [(p.get('year', 2020), p.get('citationCount', 0)) 
                    for p in papers if p.get('citationCount')]
        if citations:
            fig.add_trace(
                go.Scatter(x=[c[0] for c in citations], y=[c[1] for c in citations],
                          mode='markers', name='Citations', 
                          marker=dict(size=8, color='darkred')),
                row=2, col=2
            )
        
        fig.update_layout(height=800, showlegend=False, 
                         title_text="Research Analysis Dashboard",
                         title_font_size=20)
        
        output_path = self.output_dir / output_file
        fig.write_html(str(output_path))
        logger.info(f"Saved dashboard to {output_path}")
