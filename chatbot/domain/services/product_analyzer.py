"""ProductAnalyzer domain service - extracts meaningful insights from product data."""

from __future__ import annotations
from typing import Dict, List, Any

from chatbot.domain.entities.product_catalog import ProductCatalog
from chatbot.domain.entities.product import Product


class ProductAnalyzer:
    """Domain service that generates analytical insights from the product catalog.

    This service encapsulates the core business logic for deriving meaningful
    interpretations from product data - comments, ratings, favorites, prices, etc.
    """

    def __init__(self, catalog: ProductCatalog) -> None:
        self._catalog = catalog

    # --- Catalog-level insights ---

    def catalog_overview(self) -> Dict[str, Any]:
        """High-level overview of the entire catalog."""
        products_with_ratings = [p for p in self._catalog.products if p.rating.has_data]
        products_with_comments = [p for p in self._catalog.products if p.has_comments]

        avg_rating = 0.0
        if products_with_ratings:
            avg_rating = sum(p.rating.score for p in products_with_ratings) / len(products_with_ratings)

        return {
            "total_products": self._catalog.total_products,
            "total_categories": len(self._catalog.categories),
            "categories": self._catalog.category_counts,
            "products_with_ratings": len(products_with_ratings),
            "products_with_comments": len(products_with_comments),
            "average_rating": round(avg_rating, 2),
            "trending_count": len(self._catalog.trending()),
        }

    def category_analysis(self, category: str) -> Dict[str, Any]:
        """Deep analysis of a specific category."""
        products = self._catalog.get_by_category(category)
        if not products:
            return {"error": f"'{category}' kategorisinde ürün bulunamadı."}

        rated = [p for p in products if p.rating.has_data]
        commented = [p for p in products if p.has_comments]
        price_range = self._catalog.price_range_by_category(category)

        avg_rating = 0.0
        if rated:
            avg_rating = sum(p.rating.score for p in rated) / len(rated)

        total_comments = sum(p.comment_count for p in products)
        total_favorites = sum(p.favorite_count for p in products)

        top_rated = self._catalog.top_rated_by_category(category, limit=3)

        return {
            "category": category,
            "product_count": len(products),
            "rated_count": len(rated),
            "commented_count": len(commented),
            "average_rating": round(avg_rating, 2),
            "total_comments": total_comments,
            "total_favorites": total_favorites,
            "price_range": price_range,
            "top_rated": [p.to_summary() for p in top_rated],
        }

    # --- Comment-based insights ---

    def most_discussed_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Products generating the most discussion (comments)."""
        products = self._catalog.most_commented(limit)
        return [self._product_comment_insight(p) for p in products if p.has_comments]

    def sentiment_analysis_summary(self) -> Dict[str, Any]:
        """Overall sentiment analysis across all products with comments."""
        products_with_comments = [p for p in self._catalog.products if p.has_comments]

        all_positive = 0
        all_negative = 0
        all_neutral = 0
        total = 0

        for p in products_with_comments:
            all_positive += len(p.positive_comments)
            all_negative += len(p.negative_comments)
            all_neutral += len(p.neutral_comments)
            total += len(p.comments)

        return {
            "products_analyzed": len(products_with_comments),
            "total_comments": total,
            "positive_comments": all_positive,
            "negative_comments": all_negative,
            "neutral_comments": all_neutral,
            "positive_ratio": round(all_positive / total, 2) if total > 0 else 0,
            "negative_ratio": round(all_negative / total, 2) if total > 0 else 0,
        }

    # --- Engagement-based insights ---

    def engagement_leaders(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Products with the highest overall engagement."""
        products = self._catalog.most_engaging(limit)
        return [
            {
                "name": p.name,
                "category": p.subcategory,
                "engagement_score": p.engagement_score,
                "comment_count": p.comment_count,
                "rating": str(p.rating),
                "favorites": p.favorite_count,
            }
            for p in products
        ]

    def polarizing_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Products with the most polarizing (mixed) reviews."""
        products = self._catalog.polarizing(limit)
        return [
            {
                "name": p.name,
                "category": p.subcategory,
                "star_distribution": p.star_distribution.to_summary(),
                "sentiment": p.star_distribution.sentiment_label,
                "positive_ratio": f"{p.star_distribution.positive_ratio:.0%}",
                "negative_ratio": f"{p.star_distribution.negative_ratio:.0%}",
            }
            for p in products
        ]

    # --- Price insights ---

    def price_comparison_by_category(self) -> Dict[str, Dict[str, float]]:
        """Price ranges for each category."""
        result = {}
        for cat in self._catalog.categories:
            price_range = self._catalog.price_range_by_category(cat)
            if price_range["max"] > 0:
                result[cat] = price_range
        return result

    def best_value_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Products with the best rating-to-price ratio."""
        candidates = [
            p for p in self._catalog.products
            if p.rating.has_data and p.price.is_valid and p.rating.score >= 3.5
        ]
        # Sort by rating/price ratio (higher is better value)
        candidates.sort(key=lambda p: p.rating.score / p.price.amount, reverse=True)
        return [
            {
                "name": p.name,
                "category": p.subcategory,
                "price": str(p.price),
                "rating": str(p.rating),
                "value_score": round(p.rating.score / p.price.amount * 100, 2),
            }
            for p in candidates[:limit]
        ]

    # --- Comprehensive context for LLM ---

    def generate_llm_context(self) -> str:
        """Generate a comprehensive analytical context string for the LLM.

        This is the key method that compiles all insights into a structured
        text block that the LLM can use to answer user questions intelligently.
        """
        overview = self.catalog_overview()
        sentiment = self.sentiment_analysis_summary()
        top_commented = self.most_discussed_products(5)
        top_engaging = self.engagement_leaders(5)
        polarizing = self.polarizing_products(5)
        best_value = self.best_value_products(5)
        price_by_cat = self.price_comparison_by_category()

        sections = []

        # Section 1: Overview
        sections.append("=== KATALOG GENEL BAKIŞ ===")
        sections.append(f"Toplam ürün: {overview['total_products']}")
        sections.append(f"Toplam kategori: {overview['total_categories']}")
        sections.append(f"Puanlı ürün sayısı: {overview['products_with_ratings']}")
        sections.append(f"Yorumlu ürün sayısı: {overview['products_with_comments']}")
        sections.append(f"Ortalama puan: {overview['average_rating']}")
        sections.append(f"Trend ürün sayısı: {overview['trending_count']}")
        sections.append("")

        # Section 2: Categories
        sections.append("=== KATEGORİ DAĞILIMI ===")
        for cat, count in overview["categories"].items():
            sections.append(f"  {cat}: {count} ürün")
        sections.append("")

        # Section 3: Sentiment
        sections.append("=== GENEL DUYGU ANALİZİ ===")
        sections.append(f"Analiz edilen ürün: {sentiment['products_analyzed']}")
        sections.append(f"Toplam yorum: {sentiment['total_comments']}")
        sections.append(f"Olumlu yorumlar: {sentiment['positive_comments']} ({sentiment['positive_ratio']:.0%})")
        sections.append(f"Olumsuz yorumlar: {sentiment['negative_comments']} ({sentiment['negative_ratio']:.0%})")
        sections.append(f"Nötr yorumlar: {sentiment['neutral_comments']}")
        sections.append("")

        # Section 4: Most discussed
        sections.append("=== EN ÇOK YORUM ALAN ÜRÜNLER ===")
        for item in top_commented:
            sections.append(f"  {item['name']} ({item['category']})")
            sections.append(f"    Yorum: {item['comment_count']} | Olumlu: {item['positive_pct']} | Olumsuz: {item['negative_pct']}")
            if item.get("top_positive"):
                sections.append(f"    En beğenilen olumlu yorum: \"{item['top_positive']}\"")
            if item.get("top_negative"):
                sections.append(f"    En dikkat çeken olumsuz yorum: \"{item['top_negative']}\"")
        sections.append("")

        # Section 5: Engagement leaders
        sections.append("=== EN YÜKSEK ETKİLEŞİM ALAN ÜRÜNLER ===")
        for item in top_engaging:
            sections.append(
                f"  {item['name']} | Etkileşim: {item['engagement_score']} | "
                f"Yorum: {item['comment_count']} | Favori: {item['favorites']} | Puan: {item['rating']}"
            )
        sections.append("")

        # Section 6: Polarizing
        if polarizing:
            sections.append("=== TARTIŞMALI / KUTUPLAŞTIRICI ÜRÜNLER ===")
            for item in polarizing:
                sections.append(f"  {item['name']} ({item['category']})")
                sections.append(f"    Duygu: {item['sentiment']} | Olumlu: {item['positive_ratio']} | Olumsuz: {item['negative_ratio']}")
            sections.append("")

        # Section 7: Best value
        sections.append("=== EN İYİ FİYAT/PERFORMANS ÜRÜNLER ===")
        for item in best_value:
            sections.append(f"  {item['name']} | Fiyat: {item['price']} | Puan: {item['rating']} | Değer skoru: {item['value_score']}")
        sections.append("")

        # Section 8: Price by category
        sections.append("=== KATEGORİ BAZINDA FİYAT ARALIKLARI ===")
        for cat, pr in price_by_cat.items():
            sections.append(f"  {cat}: Min {pr['min']:.0f} TL | Max {pr['max']:.0f} TL | Ort {pr['avg']:.0f} TL")

        # Section 9: Top rated per category
        sections.append("")
        sections.append("=== KATEGORİ BAZINDA EN İYİ PUANLI ÜRÜNLER ===")
        for cat in self._catalog.categories:
            top = self._catalog.top_rated_by_category(cat, limit=3)
            if top:
                sections.append(f"  [{cat}]")
                for p in top:
                    sections.append(f"    {p.to_summary()}")

        return "\n".join(sections)

    # --- Private helpers ---

    def _product_comment_insight(self, product: Product) -> Dict[str, Any]:
        """Generate comment-level insight for a single product."""
        sentiment = product.comment_sentiment_ratio
        top_positive = ""
        top_negative = ""

        if product.positive_comments:
            # Pick the longest positive comment as most informative
            best = max(product.positive_comments, key=lambda c: len(c.text))
            top_positive = best.text[:150]

        if product.negative_comments:
            best = max(product.negative_comments, key=lambda c: len(c.text))
            top_negative = best.text[:150]

        return {
            "name": product.name,
            "category": product.subcategory,
            "comment_count": product.comment_count,
            "positive_pct": f"{sentiment['positive']:.0%}",
            "negative_pct": f"{sentiment['negative']:.0%}",
            "neutral_pct": f"{sentiment['neutral']:.0%}",
            "top_positive": top_positive,
            "top_negative": top_negative,
        }
