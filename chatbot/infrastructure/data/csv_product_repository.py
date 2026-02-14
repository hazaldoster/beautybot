"""CSV Product Repository - loads product data from CSV file into domain entities."""

from __future__ import annotations
import csv
import json
import sys
from pathlib import Path
from typing import List

# Increase CSV field size limit for large comment JSON fields
csv.field_size_limit(sys.maxsize)

from chatbot.domain.entities.product import Product
from chatbot.domain.entities.product_catalog import ProductCatalog
from chatbot.domain.value_objects.price import Price
from chatbot.domain.value_objects.rating import Rating
from chatbot.domain.value_objects.comment import Comment
from chatbot.domain.value_objects.star_distribution import StarDistribution


class CsvProductRepository:
    """Infrastructure service that loads product data from CSV and maps to domain entities."""

    def __init__(self, csv_path: str) -> None:
        self._csv_path = Path(csv_path)
        if not self._csv_path.exists():
            raise FileNotFoundError(f"CSV dosyası bulunamadı: {csv_path}")

    def load_catalog(self) -> ProductCatalog:
        """Load all products from CSV and return a populated ProductCatalog."""
        products = self._load_products()
        catalog = ProductCatalog()
        catalog.load(products)
        return catalog

    def _load_products(self) -> List[Product]:
        """Parse CSV rows into Product domain entities."""
        products = []

        with open(self._csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                product = self._map_row_to_product(row)
                if product:
                    products.append(product)

        return products

    def _map_row_to_product(self, row: dict) -> Product | None:
        """Map a single CSV row to a Product entity."""
        try:
            product_id = row.get("product_id", "").strip()
            name = row.get("name", "").strip()

            if not product_id or not name:
                return None

            # Parse price
            price = Price.from_turkish_format(row.get("price", ""))

            # Parse rating
            rating = Rating.create(
                score=self._safe_float(row.get("rating_score", row.get("rating", ""))),
                count=self._safe_int(row.get("total_rating_count", row.get("rating_count", ""))),
                average=self._safe_float(row.get("average_rating", "")),
            )

            # Parse star distribution
            star_dist = StarDistribution.create(
                star_0=self._safe_int(row.get("star_0_count", "")),
                star_1=self._safe_int(row.get("star_1_count", "")),
                star_2=self._safe_int(row.get("star_2_count", "")),
                star_3=self._safe_int(row.get("star_3_count", "")),
                star_4=self._safe_int(row.get("star_4_count", "")),
                star_5=self._safe_int(row.get("star_5_count", "")),
            )

            # Parse comments
            comments = self._parse_comments(row.get("comments", ""))

            # Parse social proofs
            social_proofs = [
                row.get(f"social_proof_{i}", "").strip()
                for i in range(1, 5)
                if row.get(f"social_proof_{i}", "").strip()
            ]

            return Product(
                product_id=product_id,
                name=name,
                url=row.get("url", "").strip(),
                subcategory=row.get("subcategory", "").strip(),
                description=row.get("description", "").strip(),
                price=price,
                rating=rating,
                star_distribution=star_dist,
                comments=comments,
                social_proofs=social_proofs,
                color=row.get("Renk", "").strip() or None,
                origin=row.get("Menşei", "").strip() or None,
                total_comment_count=self._safe_int(row.get("total_comment_count", "")),
                total_questions=self._safe_int(row.get("total_questions", "")),
            )
        except Exception as e:
            # Skip malformed rows silently
            print(f"Uyarı: Satır işlenirken hata: {e}")
            return None

    def _parse_comments(self, raw: str) -> List[Comment]:
        """Parse JSON comment array from CSV field."""
        if not raw or raw.strip() in ("", "[]"):
            return []
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                return [Comment.from_dict(c) for c in data if isinstance(c, dict)]
        except (json.JSONDecodeError, TypeError):
            pass
        return []

    @staticmethod
    def _safe_float(value: str) -> float:
        if not value or not str(value).strip():
            return 0.0
        try:
            return float(str(value).strip())
        except ValueError:
            return 0.0

    @staticmethod
    def _safe_int(value: str) -> int:
        if not value or not str(value).strip():
            return 0
        try:
            return int(float(str(value).strip()))
        except ValueError:
            return 0
