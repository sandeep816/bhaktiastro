"""Tests for Lagna/Ascendant foundation calculation."""

from __future__ import annotations

from types import SimpleNamespace
import sys

import pytest

from backend.app.kundali import lagna


class FakeSwissEphemeris(SimpleNamespace):
    """Small fake for Ascendant house calculation."""

    def __init__(self, ascendant: float) -> None:
        super().__init__()
        self.ascendant = ascendant
        self.calls: list[tuple[float, float, float, bytes]] = []

    def houses_ex(
        self,
        jd_ut: float,
        latitude: float,
        longitude: float,
        house_system: bytes,
    ) -> tuple[tuple[float, ...], tuple[float, ...]]:
        self.calls.append((jd_ut, latitude, longitude, house_system))
        return (), (self.ascendant, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)


def test_calculate_lagna_returns_ascendant_longitude_and_rashi_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_swe = FakeSwissEphemeris(ascendant=47.25)
    fake_julian = SimpleNamespace(julian_day_ut=2451543.770833)
    monkeypatch.setitem(sys.modules, "swisseph", fake_swe)
    monkeypatch.setattr(lagna.julian, "calculate_julian_day", lambda *args: fake_julian)
    monkeypatch.setattr(lagna.ayanamsa, "get_ayanamsa", lambda *args: 24.0)

    result = lagna.calculate_lagna(
        1990,
        1,
        1,
        12,
        0,
        0,
        5.5,
        26.9124,
        75.7873,
    )

    assert result["ascendant_longitude"] == 23.25
    assert result["sidereal_longitude"] == 23.25
    assert result["tropical_longitude"] == 47.25
    assert result["ayanamsa"] == 24.0
    assert result["rashi"]["english"] == "Aries"
    assert result["rashi_index"] == 1
    assert result["rashi_degree"] == 23.25
    assert fake_swe.calls == [(2451543.770833, 26.9124, 75.7873, b"P")]


def test_calculate_lagna_normalizes_sidereal_longitude(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_swe = FakeSwissEphemeris(ascendant=10.0)
    fake_julian = SimpleNamespace(julian_day_ut=2451543.770833)
    monkeypatch.setitem(sys.modules, "swisseph", fake_swe)
    monkeypatch.setattr(lagna.julian, "calculate_julian_day", lambda *args: fake_julian)
    monkeypatch.setattr(lagna.ayanamsa, "get_ayanamsa", lambda *args: 24.0)

    result = lagna.calculate_lagna(
        1990,
        1,
        1,
        12,
        0,
        0,
        5.5,
        26.9124,
        75.7873,
    )

    assert 0.0 <= result["ascendant_longitude"] < 360.0
    assert result["ascendant_longitude"] == 346.0
    assert result["rashi"]["english"] == "Pisces"
    assert result["rashi_degree"] == 16.0


def test_calculate_lagna_does_not_break_for_jaipur_sample_birth_data() -> None:
    result = lagna.calculate_lagna(
        1990,
        1,
        1,
        12,
        0,
        0,
        5.5,
        26.9124,
        75.7873,
    )

    assert 0.0 <= result["ascendant_longitude"] < 360.0
    assert result["sidereal_longitude"] == result["ascendant_longitude"]
    assert 0.0 <= result["tropical_longitude"] < 360.0
    assert result["ayanamsa"] > 0.0
    assert set(result["rashi"]) == {
        "index",
        "english",
        "hindi",
        "sanskrit",
        "lord",
        "element",
        "modality",
        "start_degree",
        "end_degree",
        "degree_in_rashi",
    }
    assert result["rashi_index"] == result["rashi"]["index"]
    assert result["rashi_degree"] == result["rashi"]["degree_in_rashi"]


def test_calculate_lagna_rejects_invalid_coordinates() -> None:
    with pytest.raises(ValueError, match="latitude must be between"):
        lagna.calculate_lagna(1990, 1, 1, 12, 0, 0, 5.5, 91.0, 75.7873)

    with pytest.raises(ValueError, match="longitude must be between"):
        lagna.calculate_lagna(1990, 1, 1, 12, 0, 0, 5.5, 26.9124, 181.0)
