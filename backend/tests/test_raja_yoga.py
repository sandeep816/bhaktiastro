"""Tests for foundational Raja Yoga detection."""

from __future__ import annotations

from typing import Any

import pytest

from backend.app.kundali import raja_yoga, yoga_framework


@pytest.fixture(autouse=True)
def restore_raja_yoga_detector() -> None:
    yoga_framework._YOGA_DETECTORS.clear()
    yoga_framework.register_yoga_detector(
        "raja_yoga",
        raja_yoga.detect_raja_yoga,
    )


def test_kendra_lord_and_trikona_lord_same_house_returns_present() -> None:
    result = raja_yoga.detect_raja_yoga(
        _chart(
            houses=[
                {"house_number": 4, "lord": "moon"},
                {"house_number": 5, "lord": "sun"},
            ],
            planets=[
                {"planet": "moon", "house_number": 10},
                {"planet": "sun", "house_number": 10},
            ],
        )
    )

    assert result["is_present"] is True
    assert result["yoga_name"] == "Raja Yoga"
    assert result["involved_planets"] == ["moon", "sun"]
    assert result["involved_houses"] == [4, 5, 10]
    assert result["strength"] == "not_evaluated"


def test_no_association_returns_not_present() -> None:
    result = raja_yoga.detect_raja_yoga(
        _chart(
            houses=[
                {"house_number": 4, "lord": "moon"},
                {"house_number": 5, "lord": "sun"},
            ],
            planets=[
                {"planet": "moon", "house_number": 10},
                {"planet": "sun", "house_number": 11},
            ],
        )
    )

    assert result["is_present"] is False
    assert result["reason"] == "No Kendra lord and Trikona lord share the same house."


def test_missing_lordship_data_handled_safely() -> None:
    result = raja_yoga.detect_raja_yoga(
        _chart(
            houses=[
                {"house_number": 4},
                {"house_number": 5},
            ],
            planets=[
                {"planet": "moon", "house_number": 10},
                {"planet": "sun", "house_number": 10},
            ],
        )
    )

    assert result["is_present"] is False
    assert result["reason"] == "House lord metadata is missing."


def test_missing_house_placement_handled_safely() -> None:
    result = raja_yoga.detect_raja_yoga(
        _chart(
            houses=[
                {"house_number": 4, "lord": "moon"},
                {"house_number": 5, "lord": "sun"},
            ],
            planets=[
                {"planet": "moon"},
                {"planet": "sun"},
            ],
        )
    )

    assert result["is_present"] is False
    assert result["reason"] == "Planet house placement metadata is missing."


def test_alternate_lord_keys_are_supported() -> None:
    result = raja_yoga.detect_raja_yoga(
        _chart(
            houses=[
                {"house_number": 7, "house_lord": "venus"},
                {"house_number": 9, "lord_planet": "mars"},
            ],
            planets=[
                {"planet": "venus", "house_number": 1},
                {"planet": "mars", "house_number": 1},
            ],
        )
    )

    assert result["is_present"] is True
    assert result["involved_planets"] == ["venus", "mars"]


def test_registered_detector_is_called_by_framework() -> None:
    results = yoga_framework.detect_yogas(
        _chart(
            houses=[
                {"house_number": 4, "lord": "moon"},
                {"house_number": 5, "lord": "sun"},
            ],
            planets=[
                {"planet": "moon", "house_number": 10},
                {"planet": "sun", "house_number": 10},
            ],
        )
    )

    assert list(yoga_framework.get_registered_yoga_detectors()) == ["raja_yoga"]
    assert results[0]["yoga_name"] == "Raja Yoga"
    assert results[0]["is_present"] is True


def _chart(
    houses: list[dict[str, Any]],
    planets: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "houses": houses,
        "planets": planets,
    }
