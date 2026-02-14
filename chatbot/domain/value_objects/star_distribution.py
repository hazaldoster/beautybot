"""Star distribution value object - immutable representation of star rating breakdown."""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class StarDistribution:
    """Immutable value object representing star rating distribution."""

    star_0: int
    star_1: int
    star_2: int
    star_3: int
    star_4: int
    star_5: int

    @classmethod
    def create(
        cls,
        star_0: int = 0,
        star_1: int = 0,
        star_2: int = 0,
        star_3: int = 0,
        star_4: int = 0,
        star_5: int = 0,
    ) -> StarDistribution:
        return cls(
            star_0=star_0 or 0,
            star_1=star_1 or 0,
            star_2=star_2 or 0,
            star_3=star_3 or 0,
            star_4=star_4 or 0,
            star_5=star_5 or 0,
        )

    @property
    def total(self) -> int:
        return self.star_0 + self.star_1 + self.star_2 + self.star_3 + self.star_4 + self.star_5

    @property
    def positive_ratio(self) -> float:
        """Ratio of 4-5 star ratings to total."""
        if self.total == 0:
            return 0.0
        return (self.star_4 + self.star_5) / self.total

    @property
    def negative_ratio(self) -> float:
        """Ratio of 0-2 star ratings to total."""
        if self.total == 0:
            return 0.0
        return (self.star_0 + self.star_1 + self.star_2) / self.total

    @property
    def is_polarizing(self) -> bool:
        """Product is polarizing if both high and low ratings are significant."""
        if self.total < 5:
            return False
        return self.positive_ratio > 0.3 and self.negative_ratio > 0.2

    @property
    def sentiment_label(self) -> str:
        if self.total == 0:
            return "veri yok"
        if self.positive_ratio >= 0.7:
            return "çok olumlu"
        if self.positive_ratio >= 0.5:
            return "olumlu"
        if self.negative_ratio >= 0.5:
            return "olumsuz"
        return "karışık"

    def to_summary(self) -> str:
        if self.total == 0:
            return "Yıldız dağılımı verisi yok"
        lines = [
            f"5 yıldız: {self.star_5} ({self._pct(self.star_5)}%)",
            f"4 yıldız: {self.star_4} ({self._pct(self.star_4)}%)",
            f"3 yıldız: {self.star_3} ({self._pct(self.star_3)}%)",
            f"2 yıldız: {self.star_2} ({self._pct(self.star_2)}%)",
            f"1 yıldız: {self.star_1} ({self._pct(self.star_1)}%)",
        ]
        return "\n".join(lines)

    def _pct(self, count: int) -> str:
        if self.total == 0:
            return "0"
        return f"{count / self.total * 100:.0f}"
