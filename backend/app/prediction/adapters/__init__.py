"""Read-only Prediction Analyzer Adapter interfaces."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from numbers import Integral, Real
from typing import Any


class PlanetAnalyzerAdapter:
    """Read-only access to planet entries from Kundali chart output."""

    def __init__(self, chart_data: Mapping[str, Any] | None) -> None:
        self._chart_data = chart_data if isinstance(chart_data, Mapping) else {}

    def get_planet(self, planet: str) -> dict[str, Any] | None:
        """Return a JSON-safe planet entry by name."""

        planet_key = _normalize_key(planet)
        if not planet_key:
            return None

        for planet_data in _get_sequence(self._chart_data.get("planets")):
            if not isinstance(planet_data, Mapping):
                continue
            if _normalize_key(planet_data.get("planet")) == planet_key:
                safe_planet = _make_json_safe(planet_data)
                return safe_planet if isinstance(safe_planet, dict) else None

        return None

    def get_house(self, planet: str) -> int | None:
        """Return the house number for a planet when present."""

        planet_data = self.get_planet(planet)
        if planet_data is None:
            return None

        return _get_int(planet_data.get("house_number"))

    def get_rashi(self, planet: str) -> str | None:
        """Return the Rashi name for a planet when present."""

        planet_data = self.get_planet(planet)
        if planet_data is None:
            return None

        return _extract_rashi_name(planet_data.get("rashi"))

    def get_longitude(self, planet: str) -> float | None:
        """Return the sidereal longitude for a planet when present."""

        planet_data = self.get_planet(planet)
        if planet_data is None:
            return None

        return _get_float(
            _first_present(planet_data, "sidereal_longitude", "longitude")
        )


class HouseAnalyzerAdapter:
    """Read-only access to house entries from Kundali chart output."""

    def __init__(self, chart_data: Mapping[str, Any] | None) -> None:
        self._chart_data = chart_data if isinstance(chart_data, Mapping) else {}

    def get_house(self, number: int) -> dict[str, Any] | None:
        """Return a JSON-safe house entry by house number."""

        house_number = _get_int(number)
        if house_number is None:
            return None

        for house_data in _get_sequence(self._chart_data.get("houses")):
            if not isinstance(house_data, Mapping):
                continue
            if _get_int(house_data.get("house_number")) == house_number:
                safe_house = _make_json_safe(house_data)
                return safe_house if isinstance(safe_house, dict) else None

        return None

    def get_house_lord(self, number: int) -> str | None:
        """Return a house lord when already present in house metadata."""

        house_data = self.get_house(number)
        if house_data is None:
            return None

        for key in ("lord", "house_lord", "rashi_lord"):
            value = house_data.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

        rashi = house_data.get("rashi")
        if isinstance(rashi, Mapping):
            for key in ("lord", "rashi_lord"):
                value = rashi.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()

        return None


class DashaAdapter:
    """Read-only access to Dasha output."""

    def __init__(self, dasha_data: Mapping[str, Any] | None) -> None:
        self._dasha_data = dasha_data if isinstance(dasha_data, Mapping) else {}

    def get_current_dasha(self) -> dict[str, Any] | None:
        """Return current Dasha data when present."""

        current = self._dasha_data.get("current_dasha", self._dasha_data)
        if not isinstance(current, Mapping) or not current:
            return None

        safe_current = _make_json_safe(current)
        return safe_current if isinstance(safe_current, dict) else None

    def get_lord(self, level: str) -> str | None:
        """Return a lord for a Dasha level such as mahadasha or antardasha."""

        current = self.get_current_dasha()
        if current is None:
            return None

        period = current.get(_normalize_key(level))
        if not isinstance(period, Mapping):
            return None

        value = _first_present(period, "lord", "planet", "dasha_lord")
        return value.strip() if isinstance(value, str) and value.strip() else None


class StrengthAdapter:
    """Read-only access to Planet Strength Summary output."""

    def __init__(self, strength_data: Mapping[str, Any] | None) -> None:
        self._strength_data = strength_data if isinstance(strength_data, Mapping) else {}

    def get_strength(self, planet: str) -> dict[str, Any] | None:
        """Return a JSON-safe strength entry for a planet."""

        planet_key = _normalize_key(planet)
        if not planet_key:
            return None

        for planet_entry in _get_sequence(self._strength_data.get("planets")):
            if not isinstance(planet_entry, Mapping):
                continue
            if _normalize_key(planet_entry.get("planet")) == planet_key:
                safe_entry = _make_json_safe(planet_entry)
                return safe_entry if isinstance(safe_entry, dict) else None

        return None

    def get_strength_percentage(self, planet: str) -> float | None:
        """Return Shadbala strength percentage for a planet when present."""

        strength = self.get_strength(planet)
        if strength is None:
            return None

        shadbala = strength.get("shadbala")
        if not isinstance(shadbala, Mapping):
            return None

        return _get_float(shadbala.get("strength_percentage"))


class AshtakavargaAdapter:
    """Read-only access to Ashtakavarga summary output."""

    def __init__(self, ashtakavarga_data: Mapping[str, Any] | None) -> None:
        self._ashtakavarga_data = (
            ashtakavarga_data if isinstance(ashtakavarga_data, Mapping) else {}
        )

    def get_sarvashtakavarga(self) -> dict[str, Any] | None:
        """Return Sarvashtakavarga output when present."""

        sarvashtakavarga = self._ashtakavarga_data.get("sarvashtakavarga")
        if not isinstance(sarvashtakavarga, Mapping):
            return None

        safe_sav = _make_json_safe(sarvashtakavarga)
        return safe_sav if isinstance(safe_sav, dict) else None

    def get_house_bindus(self, house_number: int) -> int | None:
        """Return Sarvashtakavarga bindus for a house when present."""

        house = _get_int(house_number)
        sarvashtakavarga = self.get_sarvashtakavarga()
        if house is None or sarvashtakavarga is None:
            return None

        houses = sarvashtakavarga.get("houses")
        if not isinstance(houses, Mapping):
            return None

        return _get_int(houses.get(house, houses.get(str(house))))

    def get_planet_bav(self, planet: str) -> dict[str, Any] | None:
        """Return Bhinnashtakavarga output for a planet when present."""

        planet_key = _normalize_key(planet)
        bhinnashtakavarga = self._ashtakavarga_data.get("bhinnashtakavarga")
        if not planet_key or not isinstance(bhinnashtakavarga, Mapping):
            return None

        bav = bhinnashtakavarga.get(planet_key)
        if not isinstance(bav, Mapping):
            return None

        safe_bav = _make_json_safe(bav)
        return safe_bav if isinstance(safe_bav, dict) else None


class LagnaAdapter:
    """Read-only access to Lagna and Special Lagna output."""

    def __init__(
        self,
        chart_data: Mapping[str, Any] | None,
        special_lagna_data: Mapping[str, Any] | None = None,
    ) -> None:
        self._chart_data = chart_data if isinstance(chart_data, Mapping) else {}
        self._special_lagna_data = (
            special_lagna_data if isinstance(special_lagna_data, Mapping) else {}
        )

    def get_lagna(self) -> dict[str, Any] | None:
        """Return chart Lagna data when present."""

        lagna = self._chart_data.get("lagna")
        if not isinstance(lagna, Mapping):
            return None

        safe_lagna = _make_json_safe(lagna)
        return safe_lagna if isinstance(safe_lagna, dict) else None

    def get_special_lagna(self, name: str) -> dict[str, Any] | None:
        """Return a named special Lagna component when present."""

        component = self._special_lagna_data.get(_normalize_key(name))
        if not isinstance(component, Mapping):
            return None

        safe_component = _make_json_safe(component)
        return safe_component if isinstance(safe_component, dict) else None


class YogaAdapter:
    """Read-only access to yoga detector output."""

    def __init__(self, yoga_data: Sequence[Mapping[str, Any]] | None) -> None:
        self._yoga_data = yoga_data if isinstance(yoga_data, Sequence) else []

    def get_yoga(self, name: str) -> dict[str, Any] | None:
        """Return a yoga result by name when present."""

        yoga_key = _normalize_key(name)
        if not yoga_key:
            return None

        for yoga in self._yoga_data:
            if not isinstance(yoga, Mapping):
                continue
            candidate_name = yoga.get("yoga_name", yoga.get("name"))
            if _normalize_key(candidate_name) == yoga_key:
                safe_yoga = _make_json_safe(yoga)
                return safe_yoga if isinstance(safe_yoga, dict) else None

        return None

    def has_yoga(self, name: str) -> bool | None:
        """Return yoga presence when the result is available."""

        yoga = self.get_yoga(name)
        if yoga is None:
            return None

        value = yoga.get("is_present")
        return value if isinstance(value, bool) else None


def _get_sequence(value: object) -> Sequence[Any]:
    """Return a sequence value or an empty tuple."""

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return value

    return ()


def _normalize_key(value: object) -> str:
    """Normalize free-form identifiers into stable lowercase keys."""

    return str(value or "").strip().casefold().replace(" ", "_")


def _extract_rashi_name(rashi_data: object) -> str | None:
    """Extract a Rashi name from string or mapping data."""

    if isinstance(rashi_data, str) and rashi_data.strip():
        return rashi_data.strip()

    if not isinstance(rashi_data, Mapping):
        return None

    for key in ("sanskrit", "english", "hindi", "name"):
        value = rashi_data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    return None


def _first_present(source: Mapping[str, Any], *keys: str) -> object:
    """Return the first non-None value from a mapping."""

    for key in keys:
        value = source.get(key)
        if value is not None:
            return value

    return None


def _get_int(value: object) -> int | None:
    """Return an integer value when safe."""

    if isinstance(value, bool) or not isinstance(value, Integral):
        return None

    return int(value)


def _get_float(value: object) -> float | None:
    """Return a finite float value when safe."""

    if isinstance(value, bool) or not isinstance(value, Real):
        return None

    numeric_value = float(value)
    if not math.isfinite(numeric_value):
        return None

    return numeric_value


def _make_json_safe(value: object) -> Any:
    """Return a JSON-safe copy of adapter output values."""

    if value is None or isinstance(value, (str, bool)):
        return value

    if isinstance(value, Real):
        numeric_value = _get_float(value)
        if numeric_value is None:
            return None
        if isinstance(value, Integral):
            return int(value)
        return numeric_value

    if isinstance(value, Mapping):
        return {str(key): _make_json_safe(nested) for key, nested in value.items()}

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [_make_json_safe(item) for item in value]

    return str(value)


__all__ = [
    "AshtakavargaAdapter",
    "DashaAdapter",
    "HouseAnalyzerAdapter",
    "LagnaAdapter",
    "PlanetAnalyzerAdapter",
    "StrengthAdapter",
    "YogaAdapter",
]
