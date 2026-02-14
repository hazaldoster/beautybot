"""Comment value object - immutable representation of a user comment."""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Comment:
    """Immutable value object representing a single user comment."""

    user_name: str
    rate: int
    text: str
    date: str
    is_trusted: bool
    likes: int

    @classmethod
    def from_dict(cls, data: dict) -> Comment:
        return cls(
            user_name=data.get("userFullName", "Anonim"),
            rate=int(data.get("rate", 0)),
            text=data.get("comment", ""),
            date=data.get("date", ""),
            is_trusted=data.get("is_trusted", False),
            likes=int(data.get("likes", 0)),
        )

    @property
    def is_positive(self) -> bool:
        return self.rate >= 4

    @property
    def is_negative(self) -> bool:
        return self.rate <= 2

    @property
    def is_neutral(self) -> bool:
        return self.rate == 3

    def __str__(self) -> str:
        return f"[{self.rate}/5] {self.text[:80]}..." if len(self.text) > 80 else f"[{self.rate}/5] {self.text}"
