"""Price value object - immutable representation of a product price."""

from __future__ import annotations
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Price:
    """Immutable value object representing a Turkish Lira price."""

    raw: str
    amount: float

    @classmethod
    def from_turkish_format(cls, raw: str) -> Price:
        """Parse Turkish price format like '1.079,98 TL' into a numeric value."""
        if not raw or not raw.strip():
            return cls(raw="", amount=0.0)

        cleaned = raw.strip()
        # Remove 'TL' suffix and whitespace
        cleaned = re.sub(r"\s*TL\s*$", "", cleaned, flags=re.IGNORECASE).strip()
        # Turkish format: dots as thousands separator, comma as decimal
        cleaned = cleaned.replace(".", "").replace(",", ".")

        try:
            amount = float(cleaned)
        except ValueError:
            amount = 0.0

        return cls(raw=raw.strip(), amount=amount)

    @property
    def is_valid(self) -> bool:
        return self.amount > 0

    def __str__(self) -> str:
        return self.raw if self.raw else "Fiyat belirtilmemiş"
