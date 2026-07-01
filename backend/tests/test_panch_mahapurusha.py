"""Tests for foundational Panch Mahapurusha Yoga detection."""

from __future__ import annotations

from typing import Any

import pytest

from backend.app.kundali import panch_mahapurusha, yoga_framework


@pytest.fixture(autouse=True)
def restore_panch_mahapurusha_detector() -> None:
    yoga_framework._YOGA_DETECTORS.clear()
    yoga_framework.register_yoga_detector(
        "panch_mahapurusha_yogas",
        panch_mahapurusha.detect_panch_mahapurusha_yogas,
    )


def test_mars_in_own_sign_in_kendra_returns_ruchaka_yoga() -> None:
    result = _result_for(
        "Ruchaka Yoga",
        panch_mahapurusha.detect_panch_mahapurusha_yogas(
            _chart([_planet("mars", 1, _rashi(1, "Mesha", "Mars"))])
        ),
    )

    assert result["is_present"] is True
    assert result["involved_planets"] == ["mars"]
    assert result["involved_houses"] == [1]
    assert result["strength"] == "not_evaluated"


def test_mercury_in_exaltation_sign_in_kendra_returns_bhadra_yoga() -> None:
    result = _result_for(
        "Bhadra Yoga",
        panch_mahapurusha.detect_panch_mahapurusha_yogas(
            _chart([_planet("mercury", 4, _rashi(6, "Kanya", "Mercury"))])
        ),
    )

    assert result["is_present"] is True


def test_jupiter_in_own_sign_in_kendra_returns_hamsa_yoga() -> None:
    result = _result_for(
        "Hamsa Yoga",
        panch_mahapurusha.detect_panch_mahapurusha_yogas(
            _chart([_planet("jupiter", 7, _rashi(9, "Dhanu", "Jupiter"))])
        ),
    )

    assert result["is_present"] is True


def test_venus_in_exaltation_sign_in_kendra_returns_malavya_yoga() -> None:
    result = _result_for(
        "Malavya Yoga",
        panch_mahapurusha.detect_panch_mahapurusha_yogas(
            _chart([_planet("venus", 10, _rashi(12, "Meena", "Jupiter"))])
        ),
    )

    assert result["is_present"] is True


def test_saturn_in_own_sign_in_kendra_returns_shasha_yoga() -> None:
    result = _result_for(
        "Shasha Yoga",
        panch_mahapurusha.detect_panch_mahapurusha_yogas(
            _chart([_planet("saturn", 1, _rashi(11, "Kumbha", "Saturn"))])
        ),
    )

    assert result["is_present"] is True


def test_same_planets_outside_kendra_return_not_present() -> None:
    results = panch_mahapurusha.detect_panch_mahapurusha_yogas(
        _chart(
            [
                _planet("mars", 2, _rashi(1, "Mesha", "Mars")),
                _planet("mercury", 2, _rashi(6, "Kanya", "Mercury")),
                _planet("jupiter", 2, _rashi(9, "Dhanu", "Jupiter")),
                _planet("venus", 2, _rashi(12, "Meena", "Jupiter")),
                _planet("saturn", 2, _rashi(11, "Kumbha", "Saturn")),
            ]
        )
    )

    assert [result["is_present"] for result in results] == [
        False,
        False,
        False,
        False,
        False,
    ]
    assert all(
        result["reason"] == "Planet is not placed in a Kendra house."
        for result in results
    )


def test_missing_planet_metadata_handled_safely() -> None:
    results = panch_mahapurusha.detect_panch_mahapurusha_yogas({})

    assert len(results) == 5
    assert all(result["is_present"] is False for result in results)
    assert all(
        result["reason"] == "Planet placement metadata is missing."
        for result in results
    )


def test_missing_rashi_metadata_handled_safely() -> None:
    result = _result_for(
        "Ruchaka Yoga",
        panch_mahapurusha.detect_panch_mahapurusha_yogas(
            _chart([{"planet": "mars", "house_number": 1}])
        ),
    )

    assert result["is_present"] is False
    assert result["reason"] == "Planet Rashi metadata is missing."


def test_registered_detector_is_called_by_framework() -> None:
    results = yoga_framework.detect_yogas(
        _chart([_planet("mars", 1, _rashi(1, "Mesha", "Mars"))])
    )

    assert list(yoga_framework.get_registered_yoga_detectors()) == [
        "panch_mahapurusha_yogas"
    ]
    assert _result_for("Ruchaka Yoga", results)["is_present"] is True


def _result_for(yoga_name: str, results: list[dict[str, Any]]) -> dict[str, Any]:
    for result in results:
        if result["yoga_name"] == yoga_name:
            return result

    raise AssertionError(f"Missing result for {yoga_name}")


def _chart(planets: list[dict[str, Any]]) -> dict[str, Any]:
    return {"planets": planets}


def _planet(
    planet: str,
    house_number: int,
    rashi: dict[str, Any],
) -> dict[str, Any]:
    return {
        "planet": planet,
        "house_number": house_number,
        "rashi": rashi,
    }


def _rashi(index: int, sanskrit: str, lord: str) -> dict[str, Any]:
    return {
        "index": index,
        "sanskrit": sanskrit,
        "lord": lord,
    }
