"""Tests for reusable Graha lordship helpers."""

from __future__ import annotations

import pytest

from backend.app.kundali import chart, graha_lordship


@pytest.mark.parametrize(
    ("rashi", "lord"),
    [
        ("Mesha", "Mars"),
        ("Vrishabha", "Venus"),
        ("Mithuna", "Mercury"),
        ("Karka", "Moon"),
        ("Simha", "Sun"),
        ("Kanya", "Mercury"),
        ("Tula", "Venus"),
        ("Vrischika", "Mars"),
        ("Dhanu", "Jupiter"),
        ("Makara", "Saturn"),
        ("Kumbha", "Saturn"),
        ("Meena", "Jupiter"),
    ],
)
def test_all_twelve_rashis_return_correct_lord(rashi: str, lord: str) -> None:
    assert graha_lordship.get_rashi_lord(rashi) == lord


@pytest.mark.parametrize(
    ("rashi_index", "lord"),
    [
        (1, "Mars"),
        (2, "Venus"),
        (3, "Mercury"),
        (4, "Moon"),
        (5, "Sun"),
        (6, "Mercury"),
        (7, "Venus"),
        (8, "Mars"),
        (9, "Jupiter"),
        (10, "Saturn"),
        (11, "Saturn"),
        (12, "Jupiter"),
    ],
)
def test_rashi_index_lookup_works(rashi_index: int, lord: str) -> None:
    assert graha_lordship.get_rashi_lord_by_index(rashi_index) == lord


@pytest.mark.parametrize("rashi_index", [0, 13, -1])
def test_invalid_rashi_index_is_handled_safely(rashi_index: int) -> None:
    with pytest.raises(ValueError, match="rashi_index must be between"):
        graha_lordship.get_rashi_lord_by_index(rashi_index)


def test_attach_rashi_lord_enriches_nested_rashi_without_mutating_input() -> None:
    data = {"planet": "sun", "rashi": {"index": 5, "english": "Leo"}}

    enriched = graha_lordship.attach_rashi_lord(data)

    assert enriched["rashi"]["lord"] == "Sun"
    assert data["rashi"] == {"index": 5, "english": "Leo"}


def test_chart_lagna_includes_lord_metadata() -> None:
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

    assert result["lagna"]["rashi"]["lord"] == graha_lordship.get_rashi_lord(
        result["lagna"]["rashi"]
    )
    assert all(
        planet["rashi"]["lord"] == graha_lordship.get_rashi_lord(planet["rashi"])
        for planet in result["planets"]
    )
