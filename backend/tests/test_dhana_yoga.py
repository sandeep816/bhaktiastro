"""Tests for foundational Dhana Yoga detection."""

from __future__ import annotations

from typing import Any

import pytest

from backend.app.kundali import dhana_yoga, yoga_framework


@pytest.fixture(autouse=True)
def restore_dhana_yoga_detector() -> None:
    yoga_framework._YOGA_DETECTORS.clear()
    yoga_framework.register_yoga_detector(
        "dhana_yoga",
        dhana_yoga.detect_dhana_yoga,
    )


def test_second_lord_and_eleventh_lord_same_house_returns_present() -> None:
    result = dhana_yoga.detect_dhana_yoga(
        _chart(
            houses=[
                {"house_number": 2, "lord": "venus"},
                {"house_number": 11, "lord": "saturn"},
            ],
            planets=[
                {"planet": "venus", "house_number": 5},
                {"planet": "saturn", "house_number": 5},
            ],
        )
    )

    assert result["is_present"] is True
    assert result["yoga_name"] == "Dhana Yoga"
    assert result["involved_planets"] == ["venus", "saturn"]
    assert result["involved_houses"] == [2, 11, 5]
    assert result["strength"] == "not_evaluated"


def test_no_association_returns_not_present() -> None:
    result = dhana_yoga.detect_dhana_yoga(
        _chart(
            houses=[
                {"house_number": 2, "lord": "venus"},
                {"house_number": 11, "lord": "saturn"},
            ],
            planets=[
                {"planet": "venus", "house_number": 5},
                {"planet": "saturn", "house_number": 6},
            ],
        )
    )

    assert result["is_present"] is False
    assert result["reason"] == (
        "Second lord and eleventh lord do not share the same house."
    )


def test_missing_lordship_data_handled_safely() -> None:
    result = dhana_yoga.detect_dhana_yoga(
        _chart(
            houses=[
                {"house_number": 2},
                {"house_number": 11},
            ],
            planets=[
                {"planet": "venus", "house_number": 5},
                {"planet": "saturn", "house_number": 5},
            ],
        )
    )

    assert result["is_present"] is False
    assert result["reason"] == "House lord metadata is missing."


def test_missing_specific_house_lord_handled_safely() -> None:
    result = dhana_yoga.detect_dhana_yoga(
        _chart(
            houses=[
                {"house_number": 2, "lord": "venus"},
                {"house_number": 9, "lord": "mars"},
            ],
            planets=[
                {"planet": "venus", "house_number": 5},
                {"planet": "mars", "house_number": 5},
            ],
        )
    )

    assert result["is_present"] is False
    assert result["reason"] == "Second or eleventh house lord metadata is missing."


def test_missing_house_placement_handled_safely() -> None:
    result = dhana_yoga.detect_dhana_yoga(
        _chart(
            houses=[
                {"house_number": 2, "lord": "venus"},
                {"house_number": 11, "lord": "saturn"},
            ],
            planets=[
                {"planet": "venus"},
                {"planet": "saturn"},
            ],
        )
    )

    assert result["is_present"] is False
    assert result["reason"] == "Planet house placement metadata is missing."


def test_missing_lord_placement_handled_safely() -> None:
    result = dhana_yoga.detect_dhana_yoga(
        _chart(
            houses=[
                {"house_number": 2, "lord": "venus"},
                {"house_number": 11, "lord": "saturn"},
            ],
            planets=[
                {"planet": "venus", "house_number": 5},
                {"planet": "mars", "house_number": 5},
            ],
        )
    )

    assert result["is_present"] is False
    assert result["reason"] == (
        "Second or eleventh lord house placement metadata is missing."
    )


def test_registered_detector_is_called_by_framework() -> None:
    results = yoga_framework.detect_yogas(
        _chart(
            houses=[
                {"house_number": 2, "lord": "venus"},
                {"house_number": 11, "lord": "saturn"},
            ],
            planets=[
                {"planet": "venus", "house_number": 5},
                {"planet": "saturn", "house_number": 5},
            ],
        )
    )

    assert list(yoga_framework.get_registered_yoga_detectors()) == ["dhana_yoga"]
    assert results[0]["yoga_name"] == "Dhana Yoga"
    assert results[0]["is_present"] is True


def _chart(
    houses: list[dict[str, Any]],
    planets: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "houses": houses,
        "planets": planets,
    }
