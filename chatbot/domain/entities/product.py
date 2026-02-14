"""Product entity - the core aggregate root of the domain."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

from chatbot.domain.value_objects.price import Price
from chatbot.domain.value_objects.rating import Rating
from chatbot.domain.value_objects.comment import Comment
from chatbot.domain.value_objects.star_distribution import StarDistribution


@dataclass
class Product:
    """Core domain entity representing a beauty product with all its data."""

    product_id: str
    name: str
    url: str
    subcategory: str
    description: str
    price: Price
    rating: Rating
    star_distribution: StarDistribution
    comments: List[Comment] = field(default_factory=list)
    social_proofs: List[str] = field(default_factory=list)
    color: Optional[str] = None
    origin: Optional[str] = None
    total_comment_count: int = 0
    total_questions: int = 0
    favorite_count: int = 0

    # --- Derived insight properties ---

    @property
    def comment_count(self) -> int:
        return max(self.total_comment_count, len(self.comments))

    @property
    def has_comments(self) -> bool:
        return len(self.comments) > 0

    @property
    def positive_comments(self) -> List[Comment]:
        return [c for c in self.comments if c.is_positive]

    @property
    def negative_comments(self) -> List[Comment]:
        return [c for c in self.comments if c.is_negative]

    @property
    def neutral_comments(self) -> List[Comment]:
        return [c for c in self.comments if c.is_neutral]

    @property
    def comment_sentiment_ratio(self) -> dict:
        """Returns sentiment breakdown of comments."""
        total = len(self.comments)
        if total == 0:
            return {"positive": 0, "negative": 0, "neutral": 0}
        return {
            "positive": len(self.positive_comments) / total,
            "negative": len(self.negative_comments) / total,
            "neutral": len(self.neutral_comments) / total,
        }

    @property
    def most_liked_comment(self) -> Optional[Comment]:
        if not self.comments:
            return None
        return max(self.comments, key=lambda c: c.likes)

    @property
    def engagement_score(self) -> float:
        """Composite engagement score based on comments, ratings, favorites, and questions."""
        score = 0.0
        score += min(self.comment_count / 10, 5.0)  # max 5 from comments
        score += min(self.rating.count / 20, 3.0)    # max 3 from rating count
        score += min(self.favorite_count / 500, 2.0)  # max 2 from favorites
        return round(score, 2)

    @property
    def is_trending(self) -> bool:
        """A product is trending if it has high engagement and good ratings."""
        return self.engagement_score >= 5.0 and self.rating.is_highly_rated

    def parse_favorite_count(self) -> int:
        """Extract favorite count from social proof texts."""
        import re
        for sp in self.social_proofs:
            if not sp:
                continue
            match = re.search(r"(\d+[\d.]*)\s*kişi\s*favoriledi", sp)
            if match:
                return int(match.group(1).replace(".", ""))
        return 0

    def to_summary(self) -> str:
        """Generate a concise summary of the product for LLM context."""
        parts = [
            f"Ürün: {self.name}",
            f"Kategori: {self.subcategory}",
            f"Fiyat: {self.price}",
            f"Puan: {self.rating}",
        ]
        if self.star_distribution.total > 0:
            parts.append(f"Genel duygu: {self.star_distribution.sentiment_label}")
        if self.comment_count > 0:
            parts.append(f"Yorum sayısı: {self.comment_count}")
        if self.favorite_count > 0:
            parts.append(f"Favori: {self.favorite_count} kişi")
        if self.color:
            parts.append(f"Renk: {self.color}")
        return " | ".join(parts)
