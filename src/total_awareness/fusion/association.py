from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class AssociationScore:
    source: str
    target: str
    score: float
    reason: str


def angular_difference_deg(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)


def bearing_compatibility(observed_deg: float, predicted_deg: float, sigma_deg: float = 12.0) -> float:
    """Gaussian compatibility score for two bearings."""
    delta = angular_difference_deg(observed_deg, predicted_deg)
    return math.exp(-0.5 * (delta / sigma_deg) ** 2)
