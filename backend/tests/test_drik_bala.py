"""Tests for Drik Bala foundation scoring."""

from __future__ import annotations

import json

from backend.app.strength.drik_bala import (
    DRIK_BALA_COMPONENT,
    DRIK_BALA_MAX_SCORE,
    calculate_drik_bala,
)


def test_benefic_aspect_increases_score() -> None:
    result = calculate_drik_bala(
        "sun",
        [{"from_planet": "jupiter", "aspect_type": "full", "strength": "placeholder"}],
    )

    assert result == {
        "planet": "sun",
        "component": DRIK_BALA_COMPONENT,
        "status": "positive",
        "score": 15,
        "max_score": DRIK_BALA_MAX_SCORE,
        "received_aspects": [
            {
                "from_planet": "jupiter",
                "aspect_type": "full",
                "strength": "placeholder",
                "classification": "benefic",
                "score": 15,
            }
        ],
        "reason": "Benefic received aspects outweigh malefic received aspects.",
    }


def test_malefic_aspect_decreases_score() -> None:
    result = calculate_drik_bala(
        "moon",
        [{"from_planet": "mars", "aspect_type": "eighth", "strength": 1.0}],
    )

    assert result["status"] == "negative"
    assert result["score"] == -15
    assert result["received_aspects"][0]["classification"] == "malefic"


def test_mixed_aspects_calculate_correctly() -> None:
    result = calculate_drik_bala(
        "venus",
        [
            {"from_planet": "jupiter", "aspect_type": "fifth"},
            {"from_planet": "saturn", "aspect_type": "third"},
            {"from_planet": "moon", "aspect_type": "seventh"},
        ],
    )

    assert result["status"] == "positive"
    assert result["score"] == 15
    assert [aspect["score"] for aspect in result["received_aspects"]] == [
        15,
        -15,
        15,
    ]


def test_balanced_mixed_aspects_return_mixed_status() -> None:
    result = calculate_drik_bala(
        "mercury",
        [
            {"from_planet": "venus", "aspect_type": "seventh"},
            {"from_planet": "sun", "aspect_type": "seventh"},
        ],
    )

    assert result["status"] == "mixed"
    assert result["score"] == 0


def test_score_clamps_at_max() -> None:
    result = calculate_drik_bala(
        "saturn",
        [{"from_planet": "jupiter"} for _ in range(6)],
    )

    assert result["status"] == "positive"
    assert result["score"] == 60


def test_score_clamps_at_min() -> None:
    result = calculate_drik_bala(
        "jupiter",
        [{"from_planet": "mars"} for _ in range(6)],
    )

    assert result["status"] == "negative"
    assert result["score"] == -60


def test_no_aspects_returns_neutral() -> None:
    result = calculate_drik_bala("mars")

    assert result["status"] == "neutral"
    assert result["score"] == 0
    assert result["received_aspects"] == []


def test_invalid_aspect_data_is_handled_safely() -> None:
    unsafe_strength = object()
    result = calculate_drik_bala(
        "sun",
        [
            {"aspect_type": "missing-from-planet"},
            {"from_planet": ""},
            "not-a-dict",  # type: ignore[list-item]
            {
                "from_planet": "rahu",
                "aspect_type": "shadow",
                "strength": unsafe_strength,
            },
            {"from_planet": "venus", "aspect_type": "seventh"},
        ],
    )

    assert result["status"] == "positive"
    assert result["score"] == 15
    assert result["received_aspects"] == [
        {
            "from_planet": "rahu",
            "aspect_type": "shadow",
            "strength": str(unsafe_strength),
            "classification": "unsupported",
            "score": 0,
        },
        {
            "from_planet": "venus",
            "aspect_type": "seventh",
            "strength": None,
            "classification": "benefic",
            "score": 15,
        },
    ]


def test_unsupported_target_planet_is_handled_safely() -> None:
    result = calculate_drik_bala(
        "rahu",
        [{"from_planet": "jupiter", "aspect_type": "seventh"}],
    )

    assert result["planet"] == "rahu"
    assert result["status"] == "unsupported"
    assert result["score"] == 0
    assert result["received_aspects"] == []


def test_non_list_aspect_data_is_handled_safely() -> None:
    result = calculate_drik_bala(
        "sun",
        {"from_planet": "jupiter"},  # type: ignore[arg-type]
    )

    assert result["status"] == "neutral"
    assert result["score"] == 0
    assert result["received_aspects"] == []


def test_drik_bala_result_is_json_safe() -> None:
    result = calculate_drik_bala(
        " Moon ",
        [{"from_planet": "Jupiter", "aspect_type": " Fifth ", "strength": True}],
    )

    json.dumps(result)
