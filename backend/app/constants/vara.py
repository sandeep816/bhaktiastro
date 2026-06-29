"""Vara weekday constants."""

from __future__ import annotations

from dataclasses import dataclass

VARA_COUNT = 7


@dataclass(frozen=True)
class Vara:
    """Immutable Vara definition."""

    index: int
    name_en: str
    name_hi: str
    name_sa: str
    ruling_planet: str


VARA_LIST: tuple[Vara, ...] = (
    Vara(1, "Sunday", "रविवार", "Ravivara", "sun"),
    Vara(2, "Monday", "सोमवार", "Somavara", "moon"),
    Vara(3, "Tuesday", "मंगलवार", "Mangalavara", "mars"),
    Vara(4, "Wednesday", "बुधवार", "Budhavara", "mercury"),
    Vara(5, "Thursday", "गुरुवार", "Guruvara", "jupiter"),
    Vara(6, "Friday", "शुक्रवार", "Shukravara", "venus"),
    Vara(7, "Saturday", "शनिवार", "Shanivara", "saturn"),
)

VARAS = VARA_LIST
