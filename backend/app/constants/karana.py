"""Karana constants."""

from __future__ import annotations

from dataclasses import dataclass

KARANA_COUNT = 11
REPEATING_KARANA_TYPE = "Repeating"
FIXED_KARANA_TYPE = "Fixed"


@dataclass(frozen=True)
class Karana:
    """Immutable Karana definition."""

    index: int
    name_en: str
    name_hi: str
    name_sa: str
    type: str


KARANA_LIST: tuple[Karana, ...] = (
    Karana(1, "Bava", "बव", "Bava", REPEATING_KARANA_TYPE),
    Karana(2, "Balava", "बालव", "Balava", REPEATING_KARANA_TYPE),
    Karana(3, "Kaulava", "कौलव", "Kaulava", REPEATING_KARANA_TYPE),
    Karana(4, "Taitila", "तैतिल", "Taitila", REPEATING_KARANA_TYPE),
    Karana(5, "Gara", "गर", "Gara", REPEATING_KARANA_TYPE),
    Karana(6, "Vanija", "वणिज", "Vanija", REPEATING_KARANA_TYPE),
    Karana(7, "Vishti (Bhadra)", "विष्टि (भद्रा)", "Vishti", REPEATING_KARANA_TYPE),
    Karana(8, "Shakuni", "शकुनि", "Shakuni", FIXED_KARANA_TYPE),
    Karana(9, "Chatushpada", "चतुष्पाद", "Chatushpada", FIXED_KARANA_TYPE),
    Karana(10, "Naga", "नाग", "Naga", FIXED_KARANA_TYPE),
    Karana(11, "Kimstughna", "किंस्तुघ्न", "Kimstughna", FIXED_KARANA_TYPE),
)

REPEATING_KARANAS: tuple[Karana, ...] = KARANA_LIST[:7]
FIXED_KARANAS: tuple[Karana, ...] = KARANA_LIST[7:]
KARANAS = KARANA_LIST
