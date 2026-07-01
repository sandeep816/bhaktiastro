"""Tests for reusable retrograde motion helpers."""

from __future__ import annotations

import pytest

from backend.app.astronomy import retrograde
from backend.app.kundali import chart


def test_negative_speed_is_retrograde() -> None:
    assert retrograde.is_retrograde(-0.2) is True
    assert retrograde.get_motion_status(-0.2) == "retrograde"


def test_positive_speed_is_direct() -> None:
    assert retrograde.is_retrograde(1.25) is False
    assert retrograde.get_motion_status(1.25) == "direct"


def test_zero_speed_is_stationary() -> None:
    assert retrograde.is_retrograde(0.0) is False
    assert retrograde.get_motion_status(0.0) == "stationary"


def test_helper_handles_float_values() -> None:
    assert retrograde.is_retrograde(-0.000001) is True
    assert retrograde.get_motion_status(0.000001) == "direct"


def test_invalid_speed_is_handled_safely() -> None:
    with pytest.raises(TypeError, match="speed_longitude must be a real number"):
        retrograde.is_retrograde("slow")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="speed_longitude must be finite"):
        retrograde.get_motion_status(float("nan"))


def test_kundali_chart_adds_motion_metadata_where_speed_rule_is_safe() -> None:
    result = chart.assemble_kundali_chart(
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

    planets_with_motion = {
        planet["planet"]: planet
        for planet in result["planets"]
        if "motion_status" in planet
    }
    planets_without_motion = {
        planet["planet"]: planet
        for planet in result["planets"]
        if "motion_status" not in planet
    }

    assert set(planets_with_motion) == {
        "mars",
        "mercury",
        "jupiter",
        "venus",
        "saturn",
    }
    assert set(planets_without_motion) == {"sun", "moon", "rahu", "ketu"}
    assert all(
        planet["is_retrograde"] == retrograde.is_retrograde(planet["speed"])
        for planet in planets_with_motion.values()
    )
