"""Panchang Yoga constants."""

from __future__ import annotations

from dataclasses import dataclass

FULL_CIRCLE_DEGREES = 360.0
YOGA_COUNT = 27
YOGA_SPAN_DEGREES = FULL_CIRCLE_DEGREES / YOGA_COUNT


@dataclass(frozen=True)
class Yoga:
    """Immutable Panchang Yoga definition."""

    index: int
    name_en: str
    name_hi: str
    name_sa: str
    start_degree: float
    end_degree: float


_YOGA_NAMES: tuple[tuple[str, str, str], ...] = (
    ("Vishkambha", "विष्कम्भ", "Vishkambha"),
    ("Priti", "प्रीति", "Priti"),
    ("Ayushman", "आयुष्मान", "Ayushman"),
    ("Saubhagya", "सौभाग्य", "Saubhagya"),
    ("Shobhan", "शोभन", "Shobhana"),
    ("Atiganda", "अतिगण्ड", "Atiganda"),
    ("Sukarman", "सुकर्मा", "Sukarma"),
    ("Dhriti", "धृति", "Dhriti"),
    ("Shoola", "शूल", "Shula"),
    ("Ganda", "गण्ड", "Ganda"),
    ("Vriddhi", "वृद्धि", "Vriddhi"),
    ("Dhruva", "ध्रुव", "Dhruva"),
    ("Vyaghata", "व्याघात", "Vyaghata"),
    ("Harshana", "हर्षण", "Harshana"),
    ("Vajra", "वज्र", "Vajra"),
    ("Siddhi", "सिद्धि", "Siddhi"),
    ("Vyatipata", "व्यतीपात", "Vyatipata"),
    ("Variyan", "वरीयान", "Variyan"),
    ("Parigha", "परिघ", "Parigha"),
    ("Shiva", "शिव", "Shiva"),
    ("Siddha", "सिद्ध", "Siddha"),
    ("Sadhya", "साध्य", "Sadhya"),
    ("Shubha", "शुभ", "Shubha"),
    ("Shukla", "शुक्ल", "Shukla"),
    ("Brahma", "ब्रह्म", "Brahma"),
    ("Indra", "इन्द्र", "Indra"),
    ("Vaidhriti", "वैधृति", "Vaidhriti"),
)


YOGA_LIST: tuple[Yoga, ...] = tuple(
    Yoga(
        index=index + 1,
        name_en=name_en,
        name_hi=name_hi,
        name_sa=name_sa,
        start_degree=index * YOGA_SPAN_DEGREES,
        end_degree=(index + 1) * YOGA_SPAN_DEGREES,
    )
    for index, (name_en, name_hi, name_sa) in enumerate(_YOGA_NAMES)
)

YOGAS = YOGA_LIST
