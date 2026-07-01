"""Tests for divisional chart Varga foundations."""

from __future__ import annotations

import pytest

from backend.app.kundali import varga


def test_normalize_varga_number_accepts_registered_integer_and_code() -> None:
    assert varga.normalize_varga_number(9) == 9
    assert varga.normalize_varga_number("D9") == 9
    assert varga.normalize_varga_number(" d9 ") == 9
    assert varga.normalize_varga_number("2") == 2


def test_normalize_varga_number_rejects_invalid_number() -> None:
    with pytest.raises(ValueError, match="Unsupported Varga number"):
        varga.normalize_varga_number(8)


def test_placeholder_varga_is_registered_but_not_implemented() -> None:
    assert 2 in varga.get_registered_vargas()

    with pytest.raises(NotImplementedError, match="D2 is registered"):
        varga.calculate_varga_position(2, 15.0)


@pytest.mark.parametrize(
    ("longitude", "expected_rashi_index", "expected_sanskrit"),
    [
        (0.0, 1, "Mesha"),
        (3.333334, 2, "Vrishabha"),
        (30.0, 10, "Makara"),
        (60.0, 7, "Tula"),
        (330.0, 4, "Karka"),
    ],
)
def test_calculate_navamsa_position_uses_classical_start_rules(
    longitude: float,
    expected_rashi_index: int,
    expected_sanskrit: str,
) -> None:
    result = varga.calculate_varga_position("D9", longitude)

    assert result["varga_number"] == 9
    assert result["varga_code"] == "D9"
    assert result["varga_name"] == "Navamsa"
    assert result["rashi_index"] == expected_rashi_index
    assert result["rashi"]["sanskrit"] == expected_sanskrit


def test_calculate_navamsa_position_preserves_float_degree_inside_varga_rashi() -> None:
    result = varga.calculate_varga_position(9, 1.25)

    assert result["source_longitude"] == 1.25
    assert result["division_index"] == 1
    assert result["rashi_index"] == 1
    assert result["rashi_degree"] == 11.25
    assert result["varga_longitude"] == 11.25


def test_calculate_navamsa_position_accepts_planet_shaped_data() -> None:
    result = varga.calculate_navamsa_position(
        {
            "planet": "sun",
            "sidereal_longitude": 30.0,
            "rashi": {"index": 2, "sanskrit": "Vrishabha"},
        }
    )

    assert result["varga_number"] == 9
    assert result["source_longitude"] == 30.0
    assert result["rashi_index"] == 10
    assert result["rashi"]["sanskrit"] == "Makara"


def test_calculate_navamsa_position_normalizes_longitude() -> None:
    wrapped = varga.calculate_navamsa_position(360.0)
    negative = varga.calculate_navamsa_position(-1.0)

    assert wrapped["source_longitude"] == 0.0
    assert wrapped["rashi_index"] == 1
    assert negative["source_longitude"] == 359.0
    assert negative["rashi_index"] == 12


def test_calculate_navamsa_position_rejects_invalid_longitude() -> None:
    with pytest.raises(TypeError, match="sidereal_longitude must be a real number"):
        varga.calculate_navamsa_position(True)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="longitude must be finite"):
        varga.calculate_navamsa_position(float("nan"))


def test_calculate_navamsa_position_rejects_mapping_without_longitude() -> None:
    with pytest.raises(ValueError, match="data must include sidereal_longitude"):
        varga.calculate_navamsa_position({"planet": "sun"})


def test_build_varga_chart_generates_navamsa_lagna_and_planets() -> None:
    result = varga.build_varga_chart(
        {
            "lagna": {"sidereal_longitude": 0.0},
            "planets": [
                {"planet": "sun", "sidereal_longitude": 0.0},
                {"planet": "moon", "sidereal_longitude": 30.0},
            ],
        },
        "D9",
    )

    assert result["varga_number"] == 9
    assert result["varga_code"] == "D9"
    assert result["varga_name"] == "Navamsa"
    assert result["lagna"]["rashi"]["sanskrit"] == "Mesha"
    assert [planet["planet"] for planet in result["planets"]] == ["sun", "moon"]
    assert result["planets"][0]["varga_position"]["rashi_index"] == 1
    assert result["planets"][1]["varga_position"]["rashi_index"] == 10


def test_build_varga_chart_does_not_mutate_source_chart() -> None:
    chart_data = {
        "lagna": {"sidereal_longitude": 0.0},
        "planets": [{"planet": "sun", "sidereal_longitude": 0.0}],
    }

    varga.build_varga_chart(chart_data, 9)

    assert chart_data == {
        "lagna": {"sidereal_longitude": 0.0},
        "planets": [{"planet": "sun", "sidereal_longitude": 0.0}],
    }


def test_build_varga_chart_rejects_invalid_chart_data() -> None:
    with pytest.raises(TypeError, match="chart_data must be a mapping"):
        varga.build_varga_chart([], 9)  # type: ignore[arg-type]


def test_build_varga_chart_rejects_planet_without_sidereal_longitude() -> None:
    with pytest.raises(ValueError, match="missing sidereal_longitude"):
        varga.build_varga_chart({"planets": [{"planet": "sun"}]}, 9)
