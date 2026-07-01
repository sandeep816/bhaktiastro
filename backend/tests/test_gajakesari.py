"""Tests for foundational Gajakesari Yoga detection."""

from __future__ import annotations

from typing import Any

import pytest

from backend.app.kundali import gajakesari, yoga_framework


@pytest.fixture(autouse=True)
def restore_gajakesari_detector() -> None:
    yoga_framework._YOGA_DETECTORS.clear()
    yoga_framework.register_yoga_detector(
        "gajakesari_yoga",
        gajakesari.detect_gajakesari_yoga,
    )


def test_jupiter_same_house_from_moon_returns_present() -> None:
    result = gajakesari.detect_gajakesari_yoga(_chart(moon_house=1, jupiter_house=1))

    assert result["is_present"] is True
    assert result["involved_planets"] == ["moon", "jupiter"]
    assert result["involved_houses"] == [1, 1]


def test_jupiter_fourth_from_moon_returns_present() -> None:
    result = gajakesari.detect_gajakesari_yoga(_chart(moon_house=1, jupiter_house=4))

    assert result["is_present"] is True
    assert result["involved_houses"] == [1, 4]


def test_jupiter_seventh_from_moon_returns_present() -> None:
    result = gajakesari.detect_gajakesari_yoga(_chart(moon_house=10, jupiter_house=4))

    assert result["is_present"] is True
    assert result["involved_houses"] == [10, 4]


def test_jupiter_tenth_from_moon_returns_present() -> None:
    result = gajakesari.detect_gajakesari_yoga(_chart(moon_house=10, jupiter_house=7))

    assert result["is_present"] is True
    assert result["involved_houses"] == [10, 7]


def test_jupiter_non_kendra_from_moon_returns_not_present() -> None:
    result = gajakesari.detect_gajakesari_yoga(_chart(moon_house=1, jupiter_house=2))

    assert result["is_present"] is False
    assert result["reason"] == "Jupiter is not in a Kendra from Moon."


@pytest.mark.parametrize(
    "chart_data",
    [
        {"planets": [{"planet": "jupiter", "house_number": 1}]},
        {"planets": [{"planet": "moon", "house_number": 1}]},
        {"planets": [{"planet": "moon"}, {"planet": "jupiter", "house_number": 1}]},
    ],
)
def test_missing_moon_or_jupiter_handled_safely(
    chart_data: dict[str, Any],
) -> None:
    result = gajakesari.detect_gajakesari_yoga(chart_data)

    assert result["is_present"] is False
    assert result["involved_planets"] == ["moon", "jupiter"]


def test_registered_detector_is_called_by_framework() -> None:
    results = yoga_framework.detect_yogas(_chart(moon_house=1, jupiter_house=4))

    assert list(yoga_framework.get_registered_yoga_detectors()) == [
        "gajakesari_yoga"
    ]
    assert results[0]["yoga_name"] == "Gajakesari Yoga"
    assert results[0]["is_present"] is True


def _chart(moon_house: int, jupiter_house: int) -> dict[str, Any]:
    return {
        "planets": [
            {"planet": "moon", "house_number": moon_house},
            {"planet": "jupiter", "house_number": jupiter_house},
        ]
    }
