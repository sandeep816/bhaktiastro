"""Tithi constants."""

from __future__ import annotations

from dataclasses import dataclass

FULL_CIRCLE_DEGREES = 360.0
TITHI_COUNT = 30
TITHI_SPAN_DEGREES = FULL_CIRCLE_DEGREES / TITHI_COUNT
SHUKLA_PAKSHA = "Shukla"
KRISHNA_PAKSHA = "Krishna"


@dataclass(frozen=True)
class Tithi:
    """Immutable Tithi definition."""

    number: int
    name_en: str
    name_hi: str
    name_sa: str
    paksha: str
    start_angle: float
    end_angle: float


_TITHI_NAMES: tuple[tuple[str, str, str], ...] = (
    ("Pratipada", "प्रतिपदा", "Pratipada"),
    ("Dwitiya", "द्वितीया", "Dvitiya"),
    ("Tritiya", "तृतीया", "Tritiya"),
    ("Chaturthi", "चतुर्थी", "Chaturthi"),
    ("Panchami", "पंचमी", "Panchami"),
    ("Shashthi", "षष्ठी", "Shashthi"),
    ("Saptami", "सप्तमी", "Saptami"),
    ("Ashtami", "अष्टमी", "Ashtami"),
    ("Navami", "नवमी", "Navami"),
    ("Dashami", "दशमी", "Dashami"),
    ("Ekadashi", "एकादशी", "Ekadashi"),
    ("Dwadashi", "द्वादशी", "Dvadashi"),
    ("Trayodashi", "त्रयोदशी", "Trayodashi"),
    ("Chaturdashi", "चतुर्दशी", "Chaturdashi"),
    ("Purnima", "पूर्णिमा", "Purnima"),
    ("Pratipada", "प्रतिपदा", "Pratipada"),
    ("Dwitiya", "द्वितीया", "Dvitiya"),
    ("Tritiya", "तृतीया", "Tritiya"),
    ("Chaturthi", "चतुर्थी", "Chaturthi"),
    ("Panchami", "पंचमी", "Panchami"),
    ("Shashthi", "षष्ठी", "Shashthi"),
    ("Saptami", "सप्तमी", "Saptami"),
    ("Ashtami", "अष्टमी", "Ashtami"),
    ("Navami", "नवमी", "Navami"),
    ("Dashami", "दशमी", "Dashami"),
    ("Ekadashi", "एकादशी", "Ekadashi"),
    ("Dwadashi", "द्वादशी", "Dvadashi"),
    ("Trayodashi", "त्रयोदशी", "Trayodashi"),
    ("Chaturdashi", "चतुर्दशी", "Chaturdashi"),
    ("Amavasya", "अमावस्या", "Amavasya"),
)


TITHI_LIST: tuple[Tithi, ...] = tuple(
    Tithi(
        number=index + 1,
        name_en=name_en,
        name_hi=name_hi,
        name_sa=name_sa,
        paksha=SHUKLA_PAKSHA if index < 15 else KRISHNA_PAKSHA,
        start_angle=index * TITHI_SPAN_DEGREES,
        end_angle=(index + 1) * TITHI_SPAN_DEGREES,
    )
    for index, (name_en, name_hi, name_sa) in enumerate(_TITHI_NAMES)
)

TITHIS = TITHI_LIST
