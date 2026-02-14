"""Data Transfer Objects for passing insights between layers."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class ProductInsightDTO:
    """DTO for individual product insights."""

    name: str
    category: str
    price: str
    rating: str
    comment_count: int
    sentiment: str
    engagement_score: float
    highlights: List[str] = field(default_factory=list)


@dataclass
class CategoryInsightDTO:
    """DTO for category-level insights."""

    category: str
    product_count: int
    average_rating: float
    total_comments: int
    price_range: Dict[str, float] = field(default_factory=dict)
    top_products: List[str] = field(default_factory=list)


@dataclass
class InsightDTO:
    """DTO for the complete analysis results."""

    catalog_overview: Dict[str, Any] = field(default_factory=dict)
    sentiment_summary: Dict[str, Any] = field(default_factory=dict)
    top_commented: List[Dict[str, Any]] = field(default_factory=list)
    top_engaging: List[Dict[str, Any]] = field(default_factory=list)
    polarizing: List[Dict[str, Any]] = field(default_factory=list)
    best_value: List[Dict[str, Any]] = field(default_factory=list)
    category_insights: List[CategoryInsightDTO] = field(default_factory=list)
    llm_context: str = ""
