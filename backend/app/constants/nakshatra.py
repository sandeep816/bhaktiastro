"""Nakshatra constants."""

from __future__ import annotations

from dataclasses import dataclass

FULL_CIRCLE_DEGREES = 360.0
NAKSHATRA_COUNT = 27
NAKSHATRA_SPAN_DEGREES = FULL_CIRCLE_DEGREES / NAKSHATRA_COUNT


@dataclass(frozen=True)
class Nakshatra:
    """Immutable Nakshatra definition."""

    index: int
    name_en: str
    name_hi: str
    name_sa: str
    ruling_planet: str
    start_degree: float
    end_degree: float


_NAKSHATRA_NAMES: tuple[tuple[str, str, str, str], ...] = (
    ("Ashwini", "अश्विनी", "Ashvini", "ketu"),
    ("Bharani", "भरणी", "Bharani", "venus"),
    ("Krittika", "कृत्तिका", "Krittika", "sun"),
    ("Rohini", "रोहिणी", "Rohini", "moon"),
    ("Mrigashira", "मृगशीर्ष", "Mrigashirsha", "mars"),
    ("Ardra", "आर्द्रा", "Ardra", "rahu"),
    ("Punarvasu", "पुनर्वसु", "Punarvasu", "jupiter"),
    ("Pushya", "पुष्य", "Pushya", "saturn"),
    ("Ashlesha", "आश्लेषा", "Ashlesha", "mercury"),
    ("Magha", "मघा", "Magha", "ketu"),
    ("Purva Phalguni", "पूर्व फाल्गुनी", "Purva Phalguni", "venus"),
    ("Uttara Phalguni", "उत्तर फाल्गुनी", "Uttara Phalguni", "sun"),
    ("Hasta", "हस्त", "Hasta", "moon"),
    ("Chitra", "चित्रा", "Chitra", "mars"),
    ("Swati", "स्वाती", "Swati", "rahu"),
    ("Vishakha", "विशाखा", "Vishakha", "jupiter"),
    ("Anuradha", "अनुराधा", "Anuradha", "saturn"),
    ("Jyeshtha", "ज्येष्ठा", "Jyeshtha", "mercury"),
    ("Moola", "मूल", "Mula", "ketu"),
    ("Purva Ashadha", "पूर्वाषाढ़ा", "Purva Ashadha", "venus"),
    ("Uttara Ashadha", "उत्तराषाढ़ा", "Uttara Ashadha", "sun"),
    ("Shravana", "श्रवण", "Shravana", "moon"),
    ("Dhanishtha", "धनिष्ठा", "Dhanishtha", "mars"),
    ("Shatabhisha", "शतभिषा", "Shatabhisha", "rahu"),
    ("Purva Bhadrapada", "पूर्व भाद्रपदा", "Purva Bhadrapada", "jupiter"),
    ("Uttara Bhadrapada", "उत्तर भाद्रपदा", "Uttara Bhadrapada", "saturn"),
    ("Revati", "रेवती", "Revati", "mercury"),
)

NAKSHATRA_LIST: tuple[Nakshatra, ...] = tuple(
    Nakshatra(
        index=index,
        name_en=name_en,
        name_hi=name_hi,
        name_sa=name_sa,
        ruling_planet=ruling_planet,
        start_degree=index * NAKSHATRA_SPAN_DEGREES,
        end_degree=(index + 1) * NAKSHATRA_SPAN_DEGREES,
    )
    for index, (name_en, name_hi, name_sa, ruling_planet) in enumerate(
        _NAKSHATRA_NAMES
    )
)

NAKSHATRAS = NAKSHATRA_LIST
