"""Deterministic Vara lookup from a local civil date."""

from __future__ import annotations

from datetime import date
from typing import TypedDict, Union

from backend.app.constants.vara import VARA_LIST


class VaraResult(TypedDict):
    """Typed output for a Vara lookup."""

    index: int
    name_en: str
    name_hi: str
    name_sa: str
    ruling_planet: str


def get_vara(date_input: Union[date, str]) -> VaraResult:
    """Return Vara details for a local civil date.

    Args:
        date_input: Python date object or ISO date string in YYYY-MM-DD format.

    Returns:
        VaraResult containing index, English name, Hindi name,
        Sanskrit/transliteration name, and ruling planet.

    Raises:
        TypeError: If date_input is not a date object or string.
        ValueError: If date_input is a string but not a valid YYYY-MM-DD date.
    """

    local_date = _parse_date_input(date_input)
    vara_index = ((local_date.weekday() + 1) % len(VARA_LIST)) + 1
    vara = VARA_LIST[vara_index - 1]

    return {
        "index": vara.index,
        "name_en": vara.name_en,
        "name_hi": vara.name_hi,
        "name_sa": vara.name_sa,
        "ruling_planet": vara.ruling_planet,
    }


def _parse_date_input(date_input: Union[date, str]) -> date:
    """Parse and validate a Vara date input."""

    if isinstance(date_input, date):
        return date_input

    if isinstance(date_input, str):
        try:
            return date.fromisoformat(date_input)
        except ValueError as exc:
            raise ValueError(
                "date_input must be a valid ISO date string in YYYY-MM-DD format"
            ) from exc

    raise TypeError("date_input must be a date object or ISO date string")
