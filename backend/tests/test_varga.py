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
    assert 10 in varga.get_registered_vargas()

    with pytest.raises(NotImplementedError, match="D10 is registered"):
        varga.calculate_varga_position(10, 15.0)


def test_calculate_hora_position_odd_sign_first_half_returns_sun_hora() -> None:
    result = varga.calculate_hora_position(10.0)

    assert result["varga"] == "D2"
    assert result["varga_number"] == 2
    assert result["hora_lord"] == "Sun"
    assert result["hora_rashi"]["sanskrit"] == "Simha"
    assert result["rashi"]["sanskrit"] == "Simha"
    assert result["source_rashi"]["sanskrit"] == "Mesha"
    assert result["source_degree"] == 10.0
    assert result["division_index"] == 1


def test_calculate_hora_position_odd_sign_second_half_returns_moon_hora() -> None:
    result = varga.calculate_hora_position(20.0)

    assert result["hora_lord"] == "Moon"
    assert result["hora_rashi"]["sanskrit"] == "Karka"
    assert result["source_rashi"]["sanskrit"] == "Mesha"
    assert result["source_degree"] == 20.0
    assert result["division_index"] == 2


def test_calculate_hora_position_even_sign_first_half_returns_moon_hora() -> None:
    result = varga.calculate_hora_position(40.0)

    assert result["hora_lord"] == "Moon"
    assert result["hora_rashi"]["sanskrit"] == "Karka"
    assert result["source_rashi"]["sanskrit"] == "Vrishabha"
    assert result["source_degree"] == 10.0
    assert result["division_index"] == 1


def test_calculate_hora_position_even_sign_second_half_returns_sun_hora() -> None:
    result = varga.calculate_hora_position(50.0)

    assert result["hora_lord"] == "Sun"
    assert result["hora_rashi"]["sanskrit"] == "Simha"
    assert result["source_rashi"]["sanskrit"] == "Vrishabha"
    assert result["source_degree"] == 20.0
    assert result["division_index"] == 2


def test_calculate_hora_position_boundary_fifteen_degrees_starts_second_half() -> None:
    odd_result = varga.calculate_hora_position(15.0)
    even_result = varga.calculate_hora_position(45.0)

    assert odd_result["hora_lord"] == "Moon"
    assert odd_result["hora_rashi"]["sanskrit"] == "Karka"
    assert odd_result["source_degree"] == 15.0
    assert odd_result["division_index"] == 2
    assert even_result["hora_lord"] == "Sun"
    assert even_result["hora_rashi"]["sanskrit"] == "Simha"
    assert even_result["source_degree"] == 15.0
    assert even_result["division_index"] == 2


def test_calculate_hora_position_accepts_planet_shaped_data() -> None:
    result = varga.calculate_hora_position(
        {
            "planet": "moon",
            "sidereal_longitude": 40.0,
        }
    )

    assert result["varga_code"] == "D2"
    assert result["hora_lord"] == "Moon"
    assert result["hora_rashi"]["sanskrit"] == "Karka"


def test_calculate_hora_position_normalizes_longitude() -> None:
    wrapped = varga.calculate_hora_position(360.0)
    negative = varga.calculate_hora_position(-1.0)

    assert wrapped["source_longitude"] == 0.0
    assert wrapped["hora_lord"] == "Sun"
    assert negative["source_longitude"] == 359.0
    assert negative["source_rashi"]["sanskrit"] == "Meena"
    assert negative["hora_lord"] == "Sun"


def test_calculate_hora_position_rejects_invalid_input() -> None:
    with pytest.raises(TypeError, match="sidereal_longitude must be a real number"):
        varga.calculate_hora_position(False)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="longitude must be finite"):
        varga.calculate_hora_position(float("inf"))

    with pytest.raises(ValueError, match="data must include sidereal_longitude"):
        varga.calculate_hora_position({"planet": "sun"})


def test_calculate_drekkana_position_first_ten_degrees_returns_same_rashi() -> None:
    result = varga.calculate_drekkana_position(5.0)

    assert result["varga"] == "D3"
    assert result["varga_number"] == 3
    assert result["drekkana_part"] == 1
    assert result["drekkana_rashi"]["sanskrit"] == "Mesha"
    assert result["rashi"]["sanskrit"] == "Mesha"
    assert result["source_rashi"]["sanskrit"] == "Mesha"
    assert result["source_degree"] == 5.0
    assert result["division_index"] == 1


def test_calculate_drekkana_position_second_ten_degrees_returns_fifth_rashi() -> None:
    result = varga.calculate_drekkana_position(15.0)

    assert result["drekkana_part"] == 2
    assert result["drekkana_rashi"]["sanskrit"] == "Simha"
    assert result["source_rashi"]["sanskrit"] == "Mesha"
    assert result["source_degree"] == 15.0
    assert result["division_index"] == 2


def test_calculate_drekkana_position_third_ten_degrees_returns_ninth_rashi() -> None:
    result = varga.calculate_drekkana_position(25.0)

    assert result["drekkana_part"] == 3
    assert result["drekkana_rashi"]["sanskrit"] == "Dhanu"
    assert result["source_rashi"]["sanskrit"] == "Mesha"
    assert result["source_degree"] == 25.0
    assert result["division_index"] == 3


def test_calculate_drekkana_position_boundary_ten_degrees_starts_second_part() -> None:
    result = varga.calculate_drekkana_position(10.0)

    assert result["drekkana_part"] == 2
    assert result["drekkana_rashi"]["sanskrit"] == "Simha"
    assert result["source_degree"] == 10.0


def test_calculate_drekkana_boundary_twenty_degrees_starts_third_part() -> None:
    result = varga.calculate_drekkana_position(20.0)

    assert result["drekkana_part"] == 3
    assert result["drekkana_rashi"]["sanskrit"] == "Dhanu"
    assert result["source_degree"] == 20.0


def test_calculate_drekkana_position_wraps_from_late_rashis() -> None:
    second_part = varga.calculate_drekkana_position(315.0)
    third_part = varga.calculate_drekkana_position(355.0)

    assert second_part["source_rashi"]["sanskrit"] == "Kumbha"
    assert second_part["drekkana_part"] == 2
    assert second_part["drekkana_rashi"]["sanskrit"] == "Mithuna"
    assert third_part["source_rashi"]["sanskrit"] == "Meena"
    assert third_part["drekkana_part"] == 3
    assert third_part["drekkana_rashi"]["sanskrit"] == "Vrishchika"


def test_calculate_drekkana_position_accepts_planet_shaped_data() -> None:
    result = varga.calculate_drekkana_position(
        {
            "planet": "mars",
            "sidereal_longitude": 45.0,
        }
    )

    assert result["varga_code"] == "D3"
    assert result["source_rashi"]["sanskrit"] == "Vrishabha"
    assert result["drekkana_part"] == 2
    assert result["drekkana_rashi"]["sanskrit"] == "Kanya"


def test_calculate_drekkana_position_rejects_invalid_input() -> None:
    with pytest.raises(TypeError, match="sidereal_longitude must be a real number"):
        varga.calculate_drekkana_position(True)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="longitude must be finite"):
        varga.calculate_drekkana_position(float("nan"))

    with pytest.raises(ValueError, match="data must include sidereal_longitude"):
        varga.calculate_drekkana_position({"planet": "mars"})


def test_calculate_saptamsa_position_odd_sign_first_part_starts_same_rashi() -> None:
    result = varga.calculate_saptamsa_position(1.0)

    assert result["varga"] == "D7"
    assert result["varga_number"] == 7
    assert result["saptamsa_part"] == 1
    assert result["saptamsa_rashi"]["sanskrit"] == "Mesha"
    assert result["rashi"]["sanskrit"] == "Mesha"
    assert result["source_rashi"]["sanskrit"] == "Mesha"
    assert result["source_degree"] == 1.0
    assert result["division_index"] == 1


def test_calculate_saptamsa_position_odd_sign_last_part_wraps_from_start() -> None:
    result = varga.calculate_saptamsa_position(29.0)

    assert result["saptamsa_part"] == 7
    assert result["saptamsa_rashi"]["sanskrit"] == "Tula"
    assert result["source_rashi"]["sanskrit"] == "Mesha"
    assert result["source_degree"] == 29.0
    assert result["division_index"] == 7


def test_calculate_saptamsa_position_even_sign_first_part_starts_seventh() -> None:
    result = varga.calculate_saptamsa_position(31.0)

    assert result["saptamsa_part"] == 1
    assert result["saptamsa_rashi"]["sanskrit"] == "Vrishchika"
    assert result["source_rashi"]["sanskrit"] == "Vrishabha"
    assert result["source_degree"] == 1.0
    assert result["division_index"] == 1


def test_calculate_saptamsa_position_even_sign_last_part_counts_from_seventh() -> None:
    result = varga.calculate_saptamsa_position(59.0)

    assert result["saptamsa_part"] == 7
    assert result["saptamsa_rashi"]["sanskrit"] == "Vrishabha"
    assert result["source_rashi"]["sanskrit"] == "Vrishabha"
    assert result["source_degree"] == 29.0
    assert result["division_index"] == 7


def test_calculate_saptamsa_position_boundary_between_parts() -> None:
    boundary = 30.0 / 7.0
    result = varga.calculate_saptamsa_position(boundary)

    assert result["saptamsa_part"] == 2
    assert result["saptamsa_rashi"]["sanskrit"] == "Vrishabha"
    assert result["source_degree"] == round(boundary, 6)


def test_calculate_saptamsa_position_wraps_from_late_rashis() -> None:
    odd_result = varga.calculate_saptamsa_position(329.0)
    even_result = varga.calculate_saptamsa_position(359.0)

    assert odd_result["source_rashi"]["sanskrit"] == "Kumbha"
    assert odd_result["saptamsa_part"] == 7
    assert odd_result["saptamsa_rashi"]["sanskrit"] == "Simha"
    assert even_result["source_rashi"]["sanskrit"] == "Meena"
    assert even_result["saptamsa_part"] == 7
    assert even_result["saptamsa_rashi"]["sanskrit"] == "Meena"


def test_calculate_saptamsa_position_accepts_planet_shaped_data() -> None:
    result = varga.calculate_saptamsa_position(
        {
            "planet": "jupiter",
            "sidereal_longitude": 31.0,
        }
    )

    assert result["varga_code"] == "D7"
    assert result["source_rashi"]["sanskrit"] == "Vrishabha"
    assert result["saptamsa_part"] == 1
    assert result["saptamsa_rashi"]["sanskrit"] == "Vrishchika"


def test_calculate_saptamsa_position_rejects_invalid_input() -> None:
    with pytest.raises(TypeError, match="sidereal_longitude must be a real number"):
        varga.calculate_saptamsa_position(False)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="longitude must be finite"):
        varga.calculate_saptamsa_position(float("inf"))

    with pytest.raises(ValueError, match="data must include sidereal_longitude"):
        varga.calculate_saptamsa_position({"planet": "jupiter"})


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
