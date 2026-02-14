"""Rating value object - immutable representation of a product rating."""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Rating:
    """Immutable value object representing a product rating."""

    score: float
    count: int
    average: float

    @classmethod
    def create(cls, score: float = 0.0, count: int = 0, average: float = 0.0) -> Rating:
        return cls(
            score=score if score else 0.0,
            count=count if count else 0,
            average=average if average else 0.0,
        )

    @property
    def is_highly_rated(self) -> bool:
        """A product is considered highly rated if score >= 4.0."""
        return self.score >= 4.0

    @property
    def is_popular(self) -> bool:
        """A product is considered popular if it has significant rating count."""
        return self.count >= 50

    @property
    def has_data(self) -> bool:
        return self.score > 0 or self.count > 0

    def __str__(self) -> str:
        if not self.has_data:
            return "Puan bilgisi yok"
        return f"{self.score}/5 ({self.count} değerlendirme)"
