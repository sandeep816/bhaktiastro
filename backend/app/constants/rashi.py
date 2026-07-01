"""Rashi constants."""

from __future__ import annotations

from dataclasses import dataclass

FULL_CIRCLE_DEGREES = 360.0
RASHI_COUNT = 12
RASHI_SPAN_DEGREES = FULL_CIRCLE_DEGREES / RASHI_COUNT


@dataclass(frozen=True)
class Rashi:
    """Immutable Rashi definition."""

    index: int
    english: str
    hindi: str
    sanskrit: str
    lord: str
    element: str
    modality: str
    start_degree: float
    end_degree: float


_RASHI_DATA: tuple[tuple[str, str, str, str, str, str], ...] = (
    ("Aries", "मेष", "Mesha", "Mars", "Fire", "Movable"),
    ("Taurus", "वृषभ", "Vrishabha", "Venus", "Earth", "Fixed"),
    ("Gemini", "मिथुन", "Mithuna", "Mercury", "Air", "Dual"),
    ("Cancer", "कर्क", "Karka", "Moon", "Water", "Movable"),
    ("Leo", "सिंह", "Simha", "Sun", "Fire", "Fixed"),
    ("Virgo", "कन्या", "Kanya", "Mercury", "Earth", "Dual"),
    ("Libra", "तुला", "Tula", "Venus", "Air", "Movable"),
    ("Scorpio", "वृश्चिक", "Vrishchika", "Mars", "Water", "Fixed"),
    ("Sagittarius", "धनु", "Dhanu", "Jupiter", "Fire", "Dual"),
    ("Capricorn", "मकर", "Makara", "Saturn", "Earth", "Movable"),
    ("Aquarius", "कुम्भ", "Kumbha", "Saturn", "Air", "Fixed"),
    ("Pisces", "मीन", "Meena", "Jupiter", "Water", "Dual"),
)

RASHI_LIST: tuple[Rashi, ...] = tuple(
    Rashi(
        index=index + 1,
        english=english,
        hindi=hindi,
        sanskrit=sanskrit,
        lord=lord,
        element=element,
        modality=modality,
        start_degree=index * RASHI_SPAN_DEGREES,
        end_degree=(index + 1) * RASHI_SPAN_DEGREES,
    )
    for index, (english, hindi, sanskrit, lord, element, modality) in enumerate(
        _RASHI_DATA
    )
)

RASHIS = RASHI_LIST

