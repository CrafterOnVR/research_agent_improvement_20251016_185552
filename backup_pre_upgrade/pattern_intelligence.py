"""
Advanced Pattern Recognition and Intelligence System.

This module provides sophisticated pattern recognition capabilities that can
identify trends, relationships, and insights without requiring AI models.
"""

import re
import json
import time
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import networkx as nx
from dataclasses import dataclass
import math


@dataclass
class PatternMatch:
    """Represents a pattern match with confidence score."""
    pattern: str
    matches: List[str]
    confidence: float
    context: str
    category: str


@dataclass
class IntelligenceInsight:
    """Represents an intelligence insight derived from patterns."""
    insight_type: str
    description: str
    confidence: float
    supporting_evidence: List[str]
    implications: List[str]


class AdvancedPatternIntelligence:
    """Advanced pattern recognition and intelligence system."""
    
    def __init__(self):
        self.pattern_library = self._initialize_pattern_library()
        self.relationship_graph = nx.DiGraph()
        self.temporal_patterns = defaultdict(list)
        self.semantic_clusters = defaultdict(list)
        self.insight_history = []
        
    def _initialize_pattern_library(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive pattern library."""
        return {
            "technical_patterns": {
                "algorithms": [
                    r'\b(algorithm|algo)\b.*\b(complexity|efficiency|optimization)\b',
                    r'\b(O\(n\)|O\(log n\)|O\(n²\)|big O)\b',
                    r'\b(recursive|iterative|dynamic programming)\b'
                ],
                "frameworks": [
                    r'\b(framework|library|toolkit|SDK)\b',
                    r'\b(React|Vue|Angular|Django|Flask|Spring)\b',
                    r'\b(API|REST|GraphQL|microservices)\b'
                ],
                "data_patterns": [
                    r'\b(database|SQL|NoSQL|MongoDB|PostgreSQL)\b',
                    r'\b(data structure|array|list|tree|graph|hash)\b',
                    r'\b(machine learning|ML|AI|neural network)\b'
                ]
            },
            "business_patterns": {
                "market_indicators": [
                    r'\b(market|industry|sector|vertical)\b',
                    r'\b(revenue|profit|ROI|growth|expansion)\b',
                    r'\b(competition|competitive|market share)\b'
                ],
                "trend_indicators": [
                    r'\b(trending|popular|emerging|growing|declining)\b',
                    r'\b(adoption|usage|penetration|adoption rate)\b',
                    r'\b(innovation|breakthrough|disruption)\b'
                ]
            },
            "temporal_patterns": {
                "time_indicators": [
                    r'\b(202[0-9]|recently|currently|now|today)\b',
                    r'\b(historical|legacy|traditional|modern)\b',
                    r'\b(future|upcoming|next|emerging)\b'
                ],
                "development_stages": [
                    r'\b(alpha|beta|stable|production|deprecated)\b',
                    r'\b(version|v\d+\.\d+|release|update)\b',
                    r'\b(development|testing|deployment|maintenance)\b'
                ]
            },
            "quality_patterns": {
                "performance": [
                    r'\b(performance|speed|latency|throughput)\b',
                    r'\b(optimization|efficiency|scalability)\b',
                    r'\b(benchmark|metrics|measurement)\b'
                ],
                "reliability": [
                    r'\b(reliability|stability|robustness|fault tolerance)\b',
                    r'\b(error|bug|issue|problem|limitation)\b',
                    r'\b(testing|quality assurance|validation)\b'
                ]
            }
        }
    
    def analyze_content_patterns(self, content: str) -> List[PatternMatch]:
        """Analyze content for various patterns."""
        pattern_matches = []
        
        for category, patterns in self.pattern_library.items():
            for subcategory, pattern_list in patterns.items():
                for pattern in pattern_list:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        confidence = self._calculate_pattern_confidence(pattern, matches, content)
                        pattern_match = PatternMatch(
                            pattern=pattern,
                            matches=matches,
                            confidence=confidence,
                            context=content[:200] + "..." if len(content) > 200 else content,
                            category=f"{category}.{subcategory}"
                        )
                        pattern_matches.append(pattern_match)
        
        return sorted(pattern_matches, key=lambda x: x.confidence, reverse=True)
    
    def generate_intelligence_insights(self, content: str, context: Dict[str, Any] = None) -> List[IntelligenceInsight]:
        """Generate intelligence insights from content analysis."""
        insights = []
        
        # Analyze patterns
        pattern_matches = self.analyze_content_patterns(content)
        
        # Generate insights based on patterns
        insights.extend(self._generate_technical_insights(pattern_matches))
        insights.extend(self._generate_business_insights(pattern_matches))
        insights.extend(self._generate_temporal_insights(pattern_matches))
        insights.extend(self._generate_quality_insights(pattern_matches))
        
        # Generate relationship insights
        insights.extend(self._generate_relationship_insights(pattern_matches))
        
        # Generate trend insights
        insights.extend(self._generate_trend_insights(pattern_matches, context))
        
        return sorted(insights, key=lambda x: x.confidence, reverse=True)
    
    def _calculate_pattern_confidence(self, pattern: str, matches: List[str], content: str) -> float:
        """Calculate confidence score for pattern matches."""
        base_confidence = len(matches) / len(content.split()) * 100
        
        # Boost confidence for specific patterns
        if re.search(r'\b(important|critical|key|essential)\b', content, re.IGNORECASE):
            base_confidence *= 1.5
        
        if re.search(r'\b(performance|optimization|efficiency)\b', content, re.IGNORECASE):
            base_confidence *= 1.3
        
        # Reduce confidence for very common words
        common_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for']
        if any(word in matches for word in common_words):
            base_confidence *= 0.5
        
        return min(base_confidence, 100.0)
    
    def _generate_technical_insights(self, pattern_matches: List[PatternMatch]) -> List[IntelligenceInsight]:
        """Generate technical insights from pattern analysis."""
        insights = []
        
        # Algorithm insights
        algo_matches = [m for m in pattern_matches if 'algorithms' in m.category]
        if algo_matches:
            insights.append(IntelligenceInsight(
                insight_type="technical",
                description=f"Content contains {len(algo_matches)} algorithmic references, suggesting technical depth",
                confidence=sum(m.confidence for m in algo_matches) / len(algo_matches),
                supporting_evidence=[m.pattern for m in algo_matches],
                implications=["Technical expertise required", "Performance considerations important"]
            ))
        
        # Framework insights
        framework_matches = [m for m in pattern_matches if 'frameworks' in m.category]
        if framework_matches:
            insights.append(IntelligenceInsight(
                insight_type="technical",
                description=f"Multiple frameworks mentioned: {', '.join(set([match for m in framework_matches for match in m.matches]))}",
                confidence=sum(m.confidence for m in framework_matches) / len(framework_matches),
                supporting_evidence=[m.pattern for m in framework_matches],
                implications=["Technology stack considerations", "Integration complexity"]
            ))
        
        return insights
    
    def _generate_business_insights(self, pattern_matches: List[PatternMatch]) -> List[IntelligenceInsight]:
        """Generate business insights from pattern analysis."""
        insights = []
        
        # Market insights
        market_matches = [m for m in pattern_matches if 'market_indicators' in m.category]
        if market_matches:
            insights.append(IntelligenceInsight(
                insight_type="business",
                description="Strong market and business context identified",
                confidence=sum(m.confidence for m in market_matches) / len(market_matches),
                supporting_evidence=[m.pattern for m in market_matches],
                implications=["Commercial viability important", "Market positioning relevant"]
            ))
        
        # Trend insights
        trend_matches = [m for m in pattern_matches if 'trend_indicators' in m.category]
        if trend_matches:
            insights.append(IntelligenceInsight(
                insight_type="business",
                description="Trend indicators suggest dynamic market conditions",
                confidence=sum(m.confidence for m in trend_matches) / len(trend_matches),
                supporting_evidence=[m.pattern for m in trend_matches],
                implications=["Market timing important", "Competitive landscape dynamic"]
            ))
        
        return insights
    
    def _generate_temporal_insights(self, pattern_matches: List[PatternMatch]) -> List[IntelligenceInsight]:
        """Generate temporal insights from pattern analysis."""
        insights = []
        
        # Time-based insights
        time_matches = [m for m in pattern_matches if 'time_indicators' in m.category]
        if time_matches:
            current_year = datetime.now().year
            year_mentions = []
            for match in time_matches:
                year_mentions.extend(re.findall(r'202[0-9]', str(match.matches)))
            
            if year_mentions:
                recent_years = [int(year) for year in year_mentions if int(year) >= current_year - 2]
                if recent_years:
                    insights.append(IntelligenceInsight(
                        insight_type="temporal",
                        description=f"Recent temporal references found: {', '.join(map(str, recent_years))}",
                        confidence=80.0,
                        supporting_evidence=year_mentions,
                        implications=["Current relevance", "Recent developments"]
                    ))
        
        return insights
    
    def _generate_quality_insights(self, pattern_matches: List[PatternMatch]) -> List[IntelligenceInsight]:
        """Generate quality insights from pattern analysis."""
        insights = []
        
        # Performance insights
        perf_matches = [m for m in pattern_matches if 'performance' in m.category]
        if perf_matches:
            insights.append(IntelligenceInsight(
                insight_type="quality",
                description="Performance considerations are prominent",
                confidence=sum(m.confidence for m in perf_matches) / len(perf_matches),
                supporting_evidence=[m.pattern for m in perf_matches],
                implications=["Performance optimization important", "Benchmarking required"]
            ))
        
        # Reliability insights
        reliability_matches = [m for m in pattern_matches if 'reliability' in m.category]
        if reliability_matches:
            insights.append(IntelligenceInsight(
                insight_type="quality",
                description="Reliability and stability are key concerns",
                confidence=sum(m.confidence for m in reliability_matches) / len(reliability_matches),
                supporting_evidence=[m.pattern for m in reliability_matches],
                implications=["Quality assurance critical", "Testing requirements high"]
            ))
        
        return insights
    
    def _generate_relationship_insights(self, pattern_matches: List[PatternMatch]) -> List[IntelligenceInsight]:
        """Generate relationship insights from pattern analysis."""
        insights = []
        
        # Find co-occurring patterns
        co_occurrence = defaultdict(int)
        for match in pattern_matches:
            for other_match in pattern_matches:
                if match != other_match:
                    key = tuple(sorted([match.category, other_match.category]))
                    co_occurrence[key] += 1
        
        # Generate insights for strong relationships
        for (cat1, cat2), count in co_occurrence.items():
            if count > 1:
                insights.append(IntelligenceInsight(
                    insight_type="relationship",
                    description=f"Strong relationship between {cat1} and {cat2} patterns",
                    confidence=min(count * 20, 100),
                    supporting_evidence=[f"Co-occurrence count: {count}"],
                    implications=[f"Integration between {cat1} and {cat2} important"]
                ))
        
        return insights
    
    def _generate_trend_insights(self, pattern_matches: List[PatternMatch], context: Dict[str, Any] = None) -> List[IntelligenceInsight]:
        """Generate trend insights from pattern analysis."""
        insights = []
        
        # Analyze pattern frequency over time if context provided
        if context and 'historical_data' in context:
            historical_data = context['historical_data']
            trend_analysis = self._analyze_temporal_trends(historical_data)
            
            for trend, confidence in trend_analysis.items():
                insights.append(IntelligenceInsight(
                    insight_type="trend",
                    description=f"Trend identified: {trend}",
                    confidence=confidence,
                    supporting_evidence=["Historical pattern analysis"],
                    implications=["Future planning considerations", "Strategic positioning"]
                ))
        
        return insights
    
    def _analyze_temporal_trends(self, historical_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze temporal trends in historical data."""
        trends = {}
        
        # Simple trend analysis based on pattern frequency over time
        if len(historical_data) > 1:
            # Calculate trend direction
            early_patterns = sum(len(d.get('patterns', [])) for d in historical_data[:len(historical_data)//2])
            late_patterns = sum(len(d.get('patterns', [])) for d in historical_data[len(historical_data)//2:])
            
            if late_patterns > early_patterns * 1.2:
                trends["Increasing complexity"] = 80.0
            elif late_patterns < early_patterns * 0.8:
                trends["Simplification trend"] = 80.0
            else:
                trends["Stable patterns"] = 60.0
        
        return trends
    
    def build_knowledge_graph(self, content_list: List[str]) -> nx.DiGraph:
        """Build knowledge graph from multiple content pieces."""
        graph = nx.DiGraph()
        
        for i, content in enumerate(content_list):
            pattern_matches = self.analyze_content_patterns(content)
            
            # Add nodes for each unique concept
            concepts = set()
            for match in pattern_matches:
                concepts.update(match.matches)
            
            for concept in concepts:
                if not graph.has_node(concept):
                    graph.add_node(concept, type="concept", frequency=0)
                
                # Update frequency
                graph.nodes[concept]['frequency'] += 1
            
            # Add edges for co-occurring concepts
            for match in pattern_matches:
                for other_match in pattern_matches:
                    if match != other_match:
                        for concept1 in match.matches:
                            for concept2 in other_match.matches:
                                if concept1 != concept2:
                                    if graph.has_edge(concept1, concept2):
                                        graph[concept1][concept2]['weight'] += 1
                                    else:
                                        graph.add_edge(concept1, concept2, weight=1)
        
        return graph
    
    def find_central_concepts(self, graph: nx.DiGraph, top_n: int = 10) -> List[Tuple[str, float]]:
        """Find central concepts in the knowledge graph."""
        centrality_scores = nx.pagerank(graph)
        return sorted(centrality_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    def identify_concept_clusters(self, graph: nx.DiGraph) -> List[List[str]]:
        """Identify concept clusters in the knowledge graph."""
        try:
            # Use community detection algorithm
            import networkx.algorithms.community as nx_comm
            communities = nx_comm.greedy_modularity_communities(graph)
            return [list(community) for community in communities]
        except ImportError:
            # Fallback to simple clustering
            return self._simple_clustering(graph)
    
    def _simple_clustering(self, graph: nx.DiGraph) -> List[List[str]]:
        """Simple clustering fallback."""
        clusters = []
        visited = set()
        
        for node in graph.nodes():
            if node not in visited:
                cluster = [node]
                visited.add(node)
                
                # Add connected nodes
                for neighbor in graph.neighbors(node):
                    if neighbor not in visited:
                        cluster.append(neighbor)
                        visited.add(neighbor)
                
                clusters.append(cluster)
        
        return clusters
    
    def generate_research_recommendations(self, insights: List[IntelligenceInsight], 
                                        graph: nx.DiGraph) -> List[str]:
        """Generate research recommendations based on insights and graph."""
        recommendations = []
        
        # High-confidence insights
        high_conf_insights = [i for i in insights if i.confidence > 70]
        for insight in high_conf_insights:
            recommendations.append(f"Focus on {insight.insight_type}: {insight.description}")
        
        # Central concepts
        central_concepts = self.find_central_concepts(graph, 5)
        for concept, score in central_concepts:
            recommendations.append(f"Investigate {concept} (centrality: {score:.2f})")
        
        # Concept clusters
        clusters = self.identify_concept_clusters(graph)
        for i, cluster in enumerate(clusters[:3]):
            recommendations.append(f"Explore cluster {i+1}: {', '.join(cluster[:3])}")
        
        return recommendations
    
    def export_intelligence_report(self, insights: List[IntelligenceInsight], 
                                 graph: nx.DiGraph, 
                                 recommendations: List[str]) -> Dict[str, Any]:
        """Export comprehensive intelligence report."""
        central_concepts = self.find_central_concepts(graph, 10)
        clusters = self.identify_concept_clusters(graph)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "insights": [
                {
                    "type": insight.insight_type,
                    "description": insight.description,
                    "confidence": insight.confidence,
                    "evidence": insight.supporting_evidence,
                    "implications": insight.implications
                }
                for insight in insights
            ],
            "central_concepts": [
                {"concept": concept, "centrality": score}
                for concept, score in central_concepts
            ],
            "concept_clusters": clusters,
            "recommendations": recommendations,
            "graph_stats": {
                "nodes": graph.number_of_nodes(),
                "edges": graph.number_of_edges(),
                "density": nx.density(graph)
            }
        }
