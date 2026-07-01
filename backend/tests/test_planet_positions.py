"""Tests for planetary position calculation."""

from __future__ import annotations

from types import SimpleNamespace
import sys

import pytest

from backend.app.astronomy import planet_positions


class FakeSwissEphemeris(SimpleNamespace):
    """Small fake matching the Swiss Ephemeris calls used by planet positions."""

    SUN = 0
    MOON = 1
    MERCURY = 2
    VENUS = 3
    MARS = 4
    JUPITER = 5
    SATURN = 6
    MEAN_NODE = 10
    FLG_SWIEPH = 1
    FLG_SPEED = 2

    def __init__(self) -> None:
        super().__init__()
        self.calls: list[tuple[float, int, int]] = []
        self.positions = {
            self.SUN: (30.45, 0.0, 0.0, 0.983),
            self.MOON: (60.0, 0.0, 0.0, 13.1),
            self.MARS: (100.0, 0.0, 0.0, -0.2),
            self.MERCURY: (120.0, 0.0, 0.0, 1.0),
            self.JUPITER: (200.0, 0.0, 0.0, 0.08),
            self.VENUS: (250.0, 0.0, 0.0, 1.2),
            self.SATURN: (300.0, 0.0, 0.0, -0.05),
            self.MEAN_NODE: (350.0, 0.0, 0.0, 0.01),
        }

    def calc_ut(
        self,
        jd_ut: float,
        planet_id: int,
        flags: int,
    ) -> tuple[tuple[float, ...], int]:
        self.calls.append((jd_ut, planet_id, flags))
        return self.positions[planet_id], 0


@pytest.fixture
def fake_swisseph(monkeypatch: pytest.MonkeyPatch) -> FakeSwissEphemeris:
    fake = FakeSwissEphemeris()
    monkeypatch.setitem(sys.modules, "swisseph", fake)
    return fake


def test_get_planet_positions_returns_all_nine_planets(
    fake_swisseph: FakeSwissEphemeris,
) -> None:
    positions = planet_positions.get_planet_positions(2446176.027777, 23.72)

    assert [position["planet"] for position in positions] == [
        "sun",
        "moon",
        "mars",
        "mercury",
        "jupiter",
        "venus",
        "saturn",
        "rahu",
        "ketu",
    ]
    assert len(fake_swisseph.calls) == 8


def test_get_planet_positions_calculates_sidereal_rashi_and_dms(
    fake_swisseph: FakeSwissEphemeris,
) -> None:
    positions = planet_positions.get_planet_positions(2446176.027777, 23.72)
    sun = next(position for position in positions if position["planet"] == "sun")

    assert sun["tropical_longitude"] == 30.45
    assert sun["sidereal_longitude"] == 6.73
    assert sun["rashi_index"] == 0
    assert sun["rashi_name_hi"] == "मेष"
    assert sun["degree_in_rashi"] == 6.73
    assert sun["dms"] == {"degrees": 6, "minutes": 43, "seconds": 48.0}


def test_get_planet_positions_maps_boundary_longitude_with_rashi_engine(
    fake_swisseph: FakeSwissEphemeris,
) -> None:
    fake_swisseph.positions[fake_swisseph.SUN] = (53.72, 0.0, 0.0, 0.983)

    positions = planet_positions.get_planet_positions(2446176.027777, 23.72)
    sun = next(position for position in positions if position["planet"] == "sun")

    assert sun["sidereal_longitude"] == 30.0
    assert sun["rashi_index"] == 1
    assert sun["rashi_name_hi"] == "वृषभ"
    assert sun["degree_in_rashi"] == 0.0
    assert sun["dms"] == {"degrees": 0, "minutes": 0, "seconds": 0.0}


def test_internal_rashi_data_uses_kundali_rashi_result() -> None:
    rashi_data = planet_positions._rashi_data_from_longitude(375.234)

    assert rashi_data["rashi"]["index"] == 1
    assert rashi_data["rashi"]["english"] == "Aries"
    assert rashi_data["rashi_index"] == 0
    assert rashi_data["rashi_degree"] == 15.234


def test_get_planet_positions_sets_retrograde_using_project_rules(
    fake_swisseph: FakeSwissEphemeris,
) -> None:
    fake_swisseph.positions[fake_swisseph.SUN] = (30.45, 0.0, 0.0, -1.0)
    fake_swisseph.positions[fake_swisseph.MOON] = (60.0, 0.0, 0.0, -1.0)
    positions = planet_positions.get_planet_positions(2446176.027777, 23.72)

    by_planet = {position["planet"]: position for position in positions}
    assert by_planet["sun"]["retrograde"] is False
    assert by_planet["moon"]["retrograde"] is False
    assert by_planet["mars"]["retrograde"] is True
    assert by_planet["saturn"]["retrograde"] is True
    assert by_planet["rahu"]["retrograde"] is True
    assert by_planet["ketu"]["retrograde"] is True


def test_get_planet_positions_calculates_ketu_from_rahu(
    fake_swisseph: FakeSwissEphemeris,
) -> None:
    positions = planet_positions.get_planet_positions(2446176.027777, 23.72)
    rahu = next(position for position in positions if position["planet"] == "rahu")
    ketu = next(position for position in positions if position["planet"] == "ketu")

    assert rahu["sidereal_longitude"] == 326.28
    assert ketu["sidereal_longitude"] == 146.28
    assert ketu["rashi_index"] == 4


def test_get_planet_positions_uses_swiss_ephemeris_flags(
    fake_swisseph: FakeSwissEphemeris,
) -> None:
    planet_positions.get_planet_positions(2446176.027777, 23.72)

    expected_flags = fake_swisseph.FLG_SWIEPH | fake_swisseph.FLG_SPEED
    assert all(call[2] == expected_flags for call in fake_swisseph.calls)


def test_get_planet_positions_rejects_non_finite_jd(
    fake_swisseph: FakeSwissEphemeris,
) -> None:
    with pytest.raises(ValueError, match="jd_ut must be finite"):
        planet_positions.get_planet_positions(float("nan"), 23.72)


def test_get_planet_positions_rejects_non_numeric_ayanamsa(
    fake_swisseph: FakeSwissEphemeris,
) -> None:
    with pytest.raises(TypeError, match="ayanamsa must be numeric"):
        planet_positions.get_planet_positions(
            2446176.027777,
            "lahiri",  # type: ignore[arg-type]
        )
