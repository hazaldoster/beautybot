"""ProductCatalog entity - aggregate that holds the full product collection and enables queries."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from collections import defaultdict

from chatbot.domain.entities.product import Product


@dataclass
class ProductCatalog:
    """Aggregate root that manages the entire product collection and provides query capabilities."""

    products: List[Product] = field(default_factory=list)
    _by_category: Dict[str, List[Product]] = field(default_factory=lambda: defaultdict(list), repr=False)
    _by_id: Dict[str, Product] = field(default_factory=dict, repr=False)

    def load(self, products: List[Product]) -> None:
        """Load products and build indexes."""
        self.products = products
        self._by_category = defaultdict(list)
        self._by_id = {}
        for p in products:
            if p.subcategory:
                self._by_category[p.subcategory].append(p)
            self._by_id[p.product_id] = p
            # Parse and set favorite count from social proofs
            if p.favorite_count == 0:
                p.favorite_count = p.parse_favorite_count()

    @property
    def total_products(self) -> int:
        return len(self.products)

    @property
    def categories(self) -> List[str]:
        return sorted(self._by_category.keys())

    @property
    def category_counts(self) -> Dict[str, int]:
        return {cat: len(prods) for cat, prods in sorted(self._by_category.items())}

    def get_by_id(self, product_id: str) -> Optional[Product]:
        return self._by_id.get(product_id)

    def get_by_category(self, category: str) -> List[Product]:
        return self._by_category.get(category, [])

    def top_rated(self, limit: int = 10) -> List[Product]:
        """Products with highest rating scores."""
        rated = [p for p in self.products if p.rating.has_data]
        return sorted(rated, key=lambda p: p.rating.score, reverse=True)[:limit]

    def most_commented(self, limit: int = 10) -> List[Product]:
        """Products with the most comments."""
        return sorted(self.products, key=lambda p: p.comment_count, reverse=True)[:limit]

    def most_favorited(self, limit: int = 10) -> List[Product]:
        """Products with the most favorites."""
        return sorted(self.products, key=lambda p: p.favorite_count, reverse=True)[:limit]

    def most_engaging(self, limit: int = 10) -> List[Product]:
        """Products with the highest engagement score."""
        return sorted(self.products, key=lambda p: p.engagement_score, reverse=True)[:limit]

    def trending(self) -> List[Product]:
        """Products that are currently trending."""
        return [p for p in self.products if p.is_trending]

    def polarizing(self, limit: int = 10) -> List[Product]:
        """Products with mixed/polarizing reviews."""
        return [p for p in self.products if p.star_distribution.is_polarizing][:limit]

    def top_rated_by_category(self, category: str, limit: int = 5) -> List[Product]:
        prods = self.get_by_category(category)
        rated = [p for p in prods if p.rating.has_data]
        return sorted(rated, key=lambda p: p.rating.score, reverse=True)[:limit]

    def price_range_by_category(self, category: str) -> Dict[str, float]:
        prods = [p for p in self.get_by_category(category) if p.price.is_valid]
        if not prods:
            return {"min": 0, "max": 0, "avg": 0}
        prices = [p.price.amount for p in prods]
        return {
            "min": min(prices),
            "max": max(prices),
            "avg": sum(prices) / len(prices),
        }

    def search(self, keyword: str, limit: int = 10) -> List[Product]:
        """Simple keyword search across name, description, and category."""
        keyword_lower = keyword.lower()
        results = []
        for p in self.products:
            if (
                keyword_lower in p.name.lower()
                or keyword_lower in p.description.lower()
                or keyword_lower in p.subcategory.lower()
            ):
                results.append(p)
            if len(results) >= limit:
                break
        return results
