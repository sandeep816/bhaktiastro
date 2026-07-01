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
    assert 30 in varga.get_registered_vargas()

    with pytest.raises(NotImplementedError, match="D30 is registered"):
        varga.calculate_varga_position(30, 15.0)


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


def test_calculate_dasamsa_position_odd_sign_first_part_starts_same_rashi() -> None:
    result = varga.calculate_dasamsa_position(1.0)

    assert result["varga"] == "D10"
    assert result["varga_number"] == 10
    assert result["dasamsa_part"] == 1
    assert result["dasamsa_rashi"]["sanskrit"] == "Mesha"
    assert result["rashi"]["sanskrit"] == "Mesha"
    assert result["source_rashi"]["sanskrit"] == "Mesha"
    assert result["source_degree"] == 1.0
    assert result["division_index"] == 1


def test_calculate_dasamsa_position_odd_sign_last_part_counts_from_same() -> None:
    result = varga.calculate_dasamsa_position(29.0)

    assert result["dasamsa_part"] == 10
    assert result["dasamsa_rashi"]["sanskrit"] == "Makara"
    assert result["source_rashi"]["sanskrit"] == "Mesha"
    assert result["source_degree"] == 29.0
    assert result["division_index"] == 10


def test_calculate_dasamsa_position_even_sign_first_part_starts_ninth() -> None:
    result = varga.calculate_dasamsa_position(31.0)

    assert result["dasamsa_part"] == 1
    assert result["dasamsa_rashi"]["sanskrit"] == "Makara"
    assert result["source_rashi"]["sanskrit"] == "Vrishabha"
    assert result["source_degree"] == 1.0
    assert result["division_index"] == 1


def test_calculate_dasamsa_position_even_sign_last_part_counts_from_ninth() -> None:
    result = varga.calculate_dasamsa_position(59.0)

    assert result["dasamsa_part"] == 10
    assert result["dasamsa_rashi"]["sanskrit"] == "Tula"
    assert result["source_rashi"]["sanskrit"] == "Vrishabha"
    assert result["source_degree"] == 29.0
    assert result["division_index"] == 10


def test_calculate_dasamsa_position_boundary_three_degrees_starts_second_part() -> None:
    result = varga.calculate_dasamsa_position(3.0)

    assert result["dasamsa_part"] == 2
    assert result["dasamsa_rashi"]["sanskrit"] == "Vrishabha"
    assert result["source_degree"] == 3.0


def test_calculate_dasamsa_position_boundary_twenty_seven_degrees_part_ten() -> None:
    result = varga.calculate_dasamsa_position(27.0)

    assert result["dasamsa_part"] == 10
    assert result["dasamsa_rashi"]["sanskrit"] == "Makara"
    assert result["source_degree"] == 27.0


def test_calculate_dasamsa_position_wraps_from_late_rashis() -> None:
    odd_result = varga.calculate_dasamsa_position(329.0)
    even_result = varga.calculate_dasamsa_position(359.0)

    assert odd_result["source_rashi"]["sanskrit"] == "Kumbha"
    assert odd_result["dasamsa_part"] == 10
    assert odd_result["dasamsa_rashi"]["sanskrit"] == "Vrishchika"
    assert even_result["source_rashi"]["sanskrit"] == "Meena"
    assert even_result["dasamsa_part"] == 10
    assert even_result["dasamsa_rashi"]["sanskrit"] == "Simha"


def test_calculate_dasamsa_position_accepts_planet_shaped_data() -> None:
    result = varga.calculate_dasamsa_position(
        {
            "planet": "saturn",
            "sidereal_longitude": 31.0,
        }
    )

    assert result["varga_code"] == "D10"
    assert result["source_rashi"]["sanskrit"] == "Vrishabha"
    assert result["dasamsa_part"] == 1
    assert result["dasamsa_rashi"]["sanskrit"] == "Makara"


def test_calculate_dasamsa_position_rejects_invalid_input() -> None:
    with pytest.raises(TypeError, match="sidereal_longitude must be a real number"):
        varga.calculate_dasamsa_position(True)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="longitude must be finite"):
        varga.calculate_dasamsa_position(float("nan"))

    with pytest.raises(ValueError, match="data must include sidereal_longitude"):
        varga.calculate_dasamsa_position({"planet": "saturn"})


def test_calculate_dwadashamsa_position_first_part_starts_same_rashi() -> None:
    result = varga.calculate_dwadashamsa_position(1.0)

    assert result["varga"] == "D12"
    assert result["varga_number"] == 12
    assert result["dwadashamsa_part"] == 1
    assert result["dwadashamsa_rashi"]["sanskrit"] == "Mesha"
    assert result["rashi"]["sanskrit"] == "Mesha"
    assert result["source_rashi"]["sanskrit"] == "Mesha"
    assert result["source_degree"] == 1.0
    assert result["division_index"] == 1


def test_calculate_dwadashamsa_position_middle_part_counts_from_source() -> None:
    result = varga.calculate_dwadashamsa_position(13.0)

    assert result["dwadashamsa_part"] == 6
    assert result["dwadashamsa_rashi"]["sanskrit"] == "Kanya"
    assert result["source_rashi"]["sanskrit"] == "Mesha"
    assert result["source_degree"] == 13.0
    assert result["division_index"] == 6


def test_calculate_dwadashamsa_position_last_part_counts_from_source() -> None:
    result = varga.calculate_dwadashamsa_position(29.0)

    assert result["dwadashamsa_part"] == 12
    assert result["dwadashamsa_rashi"]["sanskrit"] == "Meena"
    assert result["source_rashi"]["sanskrit"] == "Mesha"
    assert result["source_degree"] == 29.0
    assert result["division_index"] == 12


def test_calculate_dwadashamsa_boundary_two_point_five_starts_second() -> None:
    result = varga.calculate_dwadashamsa_position(2.5)

    assert result["dwadashamsa_part"] == 2
    assert result["dwadashamsa_rashi"]["sanskrit"] == "Vrishabha"
    assert result["source_degree"] == 2.5


def test_calculate_dwadashamsa_boundary_twenty_seven_point_five_last() -> None:
    result = varga.calculate_dwadashamsa_position(27.5)

    assert result["dwadashamsa_part"] == 12
    assert result["dwadashamsa_rashi"]["sanskrit"] == "Meena"
    assert result["source_degree"] == 27.5


def test_calculate_dwadashamsa_position_wraps_from_late_rashis() -> None:
    kumbha_result = varga.calculate_dwadashamsa_position(329.0)
    meena_result = varga.calculate_dwadashamsa_position(359.0)

    assert kumbha_result["source_rashi"]["sanskrit"] == "Kumbha"
    assert kumbha_result["dwadashamsa_part"] == 12
    assert kumbha_result["dwadashamsa_rashi"]["sanskrit"] == "Makara"
    assert meena_result["source_rashi"]["sanskrit"] == "Meena"
    assert meena_result["dwadashamsa_part"] == 12
    assert meena_result["dwadashamsa_rashi"]["sanskrit"] == "Kumbha"


def test_calculate_dwadashamsa_position_accepts_planet_shaped_data() -> None:
    result = varga.calculate_dwadashamsa_position(
        {
            "planet": "venus",
            "sidereal_longitude": 13.0,
        }
    )

    assert result["varga_code"] == "D12"
    assert result["source_rashi"]["sanskrit"] == "Mesha"
    assert result["dwadashamsa_part"] == 6
    assert result["dwadashamsa_rashi"]["sanskrit"] == "Kanya"


def test_calculate_dwadashamsa_position_rejects_invalid_input() -> None:
    with pytest.raises(TypeError, match="sidereal_longitude must be a real number"):
        varga.calculate_dwadashamsa_position(False)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="longitude must be finite"):
        varga.calculate_dwadashamsa_position(float("inf"))

    with pytest.raises(ValueError, match="data must include sidereal_longitude"):
        varga.calculate_dwadashamsa_position({"planet": "venus"})


def test_calculate_shodasamsa_position_movable_first_part_starts_mesha() -> None:
    result = varga.calculate_shodasamsa_position(1.0)

    assert result["varga"] == "D16"
    assert result["varga_number"] == 16
    assert result["shodasamsa_part"] == 1
    assert result["shodasamsa_rashi"]["sanskrit"] == "Mesha"
    assert result["rashi"]["sanskrit"] == "Mesha"
    assert result["source_rashi"]["sanskrit"] == "Mesha"
    assert result["source_degree"] == 1.0
    assert result["division_index"] == 1


def test_calculate_shodasamsa_position_fixed_first_part_starts_simha() -> None:
    result = varga.calculate_shodasamsa_position(31.0)

    assert result["shodasamsa_part"] == 1
    assert result["shodasamsa_rashi"]["sanskrit"] == "Simha"
    assert result["source_rashi"]["sanskrit"] == "Vrishabha"
    assert result["source_rashi"]["modality"] == "Fixed"
    assert result["source_degree"] == 1.0
    assert result["division_index"] == 1


def test_calculate_shodasamsa_position_dual_first_part_starts_dhanu() -> None:
    result = varga.calculate_shodasamsa_position(61.0)

    assert result["shodasamsa_part"] == 1
    assert result["shodasamsa_rashi"]["sanskrit"] == "Dhanu"
    assert result["source_rashi"]["sanskrit"] == "Mithuna"
    assert result["source_rashi"]["modality"] == "Dual"
    assert result["source_degree"] == 1.0
    assert result["division_index"] == 1


def test_calculate_shodasamsa_position_last_part_counts_from_start() -> None:
    result = varga.calculate_shodasamsa_position(29.0)

    assert result["shodasamsa_part"] == 16
    assert result["shodasamsa_rashi"]["sanskrit"] == "Karka"
    assert result["source_rashi"]["sanskrit"] == "Mesha"
    assert result["source_degree"] == 29.0
    assert result["division_index"] == 16


def test_calculate_shodasamsa_boundary_between_parts() -> None:
    boundary = 30.0 / 16.0
    result = varga.calculate_shodasamsa_position(boundary)

    assert result["shodasamsa_part"] == 2
    assert result["shodasamsa_rashi"]["sanskrit"] == "Vrishabha"
    assert result["source_degree"] == round(boundary, 6)


def test_calculate_shodasamsa_position_wraps_from_late_rashis() -> None:
    result = varga.calculate_shodasamsa_position(329.0)

    assert result["source_rashi"]["sanskrit"] == "Kumbha"
    assert result["source_rashi"]["modality"] == "Fixed"
    assert result["shodasamsa_part"] == 16
    assert result["shodasamsa_rashi"]["sanskrit"] == "Vrishchika"


def test_calculate_shodasamsa_position_accepts_planet_shaped_data() -> None:
    result = varga.calculate_shodasamsa_position(
        {
            "planet": "mercury",
            "sidereal_longitude": 61.0,
        }
    )

    assert result["varga_code"] == "D16"
    assert result["source_rashi"]["sanskrit"] == "Mithuna"
    assert result["shodasamsa_part"] == 1
    assert result["shodasamsa_rashi"]["sanskrit"] == "Dhanu"


def test_calculate_shodasamsa_position_rejects_invalid_input() -> None:
    with pytest.raises(TypeError, match="sidereal_longitude must be a real number"):
        varga.calculate_shodasamsa_position(True)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="longitude must be finite"):
        varga.calculate_shodasamsa_position(float("nan"))

    with pytest.raises(ValueError, match="data must include sidereal_longitude"):
        varga.calculate_shodasamsa_position({"planet": "mercury"})


def test_calculate_vimshamsa_position_movable_first_part_starts_mesha() -> None:
    result = varga.calculate_vimshamsa_position(1.0)

    assert result["varga"] == "D20"
    assert result["varga_number"] == 20
    assert result["vimshamsa_part"] == 1
    assert result["vimshamsa_rashi"]["sanskrit"] == "Mesha"
    assert result["rashi"]["sanskrit"] == "Mesha"
    assert result["source_rashi"]["sanskrit"] == "Mesha"
    assert result["source_degree"] == 1.0
    assert result["division_index"] == 1


def test_calculate_vimshamsa_position_fixed_first_part_starts_dhanu() -> None:
    result = varga.calculate_vimshamsa_position(31.0)

    assert result["vimshamsa_part"] == 1
    assert result["vimshamsa_rashi"]["sanskrit"] == "Dhanu"
    assert result["source_rashi"]["sanskrit"] == "Vrishabha"
    assert result["source_rashi"]["modality"] == "Fixed"
    assert result["source_degree"] == 1.0
    assert result["division_index"] == 1


def test_calculate_vimshamsa_position_dual_first_part_starts_simha() -> None:
    result = varga.calculate_vimshamsa_position(61.0)

    assert result["vimshamsa_part"] == 1
    assert result["vimshamsa_rashi"]["sanskrit"] == "Simha"
    assert result["source_rashi"]["sanskrit"] == "Mithuna"
    assert result["source_rashi"]["modality"] == "Dual"
    assert result["source_degree"] == 1.0
    assert result["division_index"] == 1


def test_calculate_vimshamsa_position_last_part_counts_from_start() -> None:
    result = varga.calculate_vimshamsa_position(29.0)

    assert result["vimshamsa_part"] == 20
    assert result["vimshamsa_rashi"]["sanskrit"] == "Vrishchika"
    assert result["source_rashi"]["sanskrit"] == "Mesha"
    assert result["source_degree"] == 29.0
    assert result["division_index"] == 20


def test_calculate_vimshamsa_boundary_between_parts() -> None:
    boundary = 30.0 / 20.0
    result = varga.calculate_vimshamsa_position(boundary)

    assert result["vimshamsa_part"] == 2
    assert result["vimshamsa_rashi"]["sanskrit"] == "Vrishabha"
    assert result["source_degree"] == round(boundary, 6)


def test_calculate_vimshamsa_position_wraps_from_late_rashis() -> None:
    result = varga.calculate_vimshamsa_position(329.0)

    assert result["source_rashi"]["sanskrit"] == "Kumbha"
    assert result["source_rashi"]["modality"] == "Fixed"
    assert result["vimshamsa_part"] == 20
    assert result["vimshamsa_rashi"]["sanskrit"] == "Karka"


def test_calculate_vimshamsa_position_accepts_planet_shaped_data() -> None:
    result = varga.calculate_vimshamsa_position(
        {
            "planet": "jupiter",
            "sidereal_longitude": 61.0,
        }
    )

    assert result["varga_code"] == "D20"
    assert result["source_rashi"]["sanskrit"] == "Mithuna"
    assert result["vimshamsa_part"] == 1
    assert result["vimshamsa_rashi"]["sanskrit"] == "Simha"


def test_calculate_vimshamsa_position_rejects_invalid_input() -> None:
    with pytest.raises(TypeError, match="sidereal_longitude must be a real number"):
        varga.calculate_vimshamsa_position(False)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="longitude must be finite"):
        varga.calculate_vimshamsa_position(float("inf"))

    with pytest.raises(ValueError, match="data must include sidereal_longitude"):
        varga.calculate_vimshamsa_position({"planet": "jupiter"})


def test_calculate_siddhamsa_position_odd_first_part_starts_simha() -> None:
    result = varga.calculate_siddhamsa_position(1.0)

    assert result["varga"] == "D24"
    assert result["varga_number"] == 24
    assert result["varga_name"] == "Siddhamsa"
    assert result["siddhamsa_part"] == 1
    assert result["siddhamsa_rashi"]["sanskrit"] == "Simha"
    assert result["rashi"]["sanskrit"] == "Simha"
    assert result["source_rashi"]["sanskrit"] == "Mesha"
    assert result["source_degree"] == 1.0
    assert result["division_index"] == 1


def test_calculate_siddhamsa_position_even_first_part_starts_karka() -> None:
    result = varga.calculate_siddhamsa_position(31.0)

    assert result["siddhamsa_part"] == 1
    assert result["siddhamsa_rashi"]["sanskrit"] == "Karka"
    assert result["source_rashi"]["sanskrit"] == "Vrishabha"
    assert result["source_degree"] == 1.0
    assert result["division_index"] == 1


def test_calculate_siddhamsa_position_last_part_counts_from_start() -> None:
    result = varga.calculate_siddhamsa_position(29.0)

    assert result["siddhamsa_part"] == 24
    assert result["siddhamsa_rashi"]["sanskrit"] == "Karka"
    assert result["source_rashi"]["sanskrit"] == "Mesha"
    assert result["source_degree"] == 29.0
    assert result["division_index"] == 24


def test_calculate_siddhamsa_boundary_between_parts() -> None:
    boundary = 30.0 / 24.0
    result = varga.calculate_siddhamsa_position(boundary)

    assert result["siddhamsa_part"] == 2
    assert result["siddhamsa_rashi"]["sanskrit"] == "Kanya"
    assert result["source_degree"] == round(boundary, 6)


def test_calculate_siddhamsa_position_wraps_from_late_rashis() -> None:
    result = varga.calculate_siddhamsa_position(329.0)

    assert result["source_rashi"]["sanskrit"] == "Kumbha"
    assert result["siddhamsa_part"] == 24
    assert result["siddhamsa_rashi"]["sanskrit"] == "Karka"


def test_calculate_siddhamsa_position_accepts_planet_shaped_data() -> None:
    result = varga.calculate_siddhamsa_position(
        {
            "planet": "venus",
            "sidereal_longitude": 31.0,
        }
    )

    assert result["varga_code"] == "D24"
    assert result["source_rashi"]["sanskrit"] == "Vrishabha"
    assert result["siddhamsa_part"] == 1
    assert result["siddhamsa_rashi"]["sanskrit"] == "Karka"


def test_calculate_siddhamsa_position_rejects_invalid_input() -> None:
    with pytest.raises(TypeError, match="sidereal_longitude must be a real number"):
        varga.calculate_siddhamsa_position(True)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="longitude must be finite"):
        varga.calculate_siddhamsa_position(float("nan"))

    with pytest.raises(ValueError, match="data must include sidereal_longitude"):
        varga.calculate_siddhamsa_position({"planet": "venus"})


def test_calculate_bhamsa_position_movable_first_part_starts_mesha() -> None:
    result = varga.calculate_bhamsa_position(1.0)

    assert result["varga"] == "D27"
    assert result["varga_number"] == 27
    assert result["varga_name"] == "Bhamsa"
    assert result["bhamsa_part"] == 1
    assert result["bhamsa_rashi"]["sanskrit"] == "Mesha"
    assert result["rashi"]["sanskrit"] == "Mesha"
    assert result["source_rashi"]["sanskrit"] == "Mesha"
    assert result["source_degree"] == 1.0
    assert result["division_index"] == 1


def test_calculate_bhamsa_position_fixed_first_part_starts_simha() -> None:
    result = varga.calculate_bhamsa_position(31.0)

    assert result["bhamsa_part"] == 1
    assert result["bhamsa_rashi"]["sanskrit"] == "Simha"
    assert result["source_rashi"]["sanskrit"] == "Vrishabha"
    assert result["source_rashi"]["modality"] == "Fixed"
    assert result["source_degree"] == 1.0
    assert result["division_index"] == 1


def test_calculate_bhamsa_position_dual_first_part_starts_dhanu() -> None:
    result = varga.calculate_bhamsa_position(61.0)

    assert result["bhamsa_part"] == 1
    assert result["bhamsa_rashi"]["sanskrit"] == "Dhanu"
    assert result["source_rashi"]["sanskrit"] == "Mithuna"
    assert result["source_rashi"]["modality"] == "Dual"
    assert result["source_degree"] == 1.0
    assert result["division_index"] == 1


def test_calculate_bhamsa_position_last_part_counts_from_start() -> None:
    result = varga.calculate_bhamsa_position(29.0)

    assert result["bhamsa_part"] == 27
    assert result["bhamsa_rashi"]["sanskrit"] == "Mithuna"
    assert result["source_rashi"]["sanskrit"] == "Mesha"
    assert result["source_degree"] == 29.0
    assert result["division_index"] == 27


def test_calculate_bhamsa_boundary_between_parts() -> None:
    boundary = 30.0 / 27.0
    result = varga.calculate_bhamsa_position(boundary)

    assert result["bhamsa_part"] == 2
    assert result["bhamsa_rashi"]["sanskrit"] == "Vrishabha"
    assert result["source_degree"] == round(boundary, 6)


def test_calculate_bhamsa_position_wraps_from_late_rashis() -> None:
    result = varga.calculate_bhamsa_position(329.0)

    assert result["source_rashi"]["sanskrit"] == "Kumbha"
    assert result["source_rashi"]["modality"] == "Fixed"
    assert result["bhamsa_part"] == 27
    assert result["bhamsa_rashi"]["sanskrit"] == "Tula"


def test_calculate_bhamsa_position_accepts_planet_shaped_data() -> None:
    result = varga.calculate_bhamsa_position(
        {
            "planet": "mars",
            "sidereal_longitude": 61.0,
        }
    )

    assert result["varga_code"] == "D27"
    assert result["source_rashi"]["sanskrit"] == "Mithuna"
    assert result["bhamsa_part"] == 1
    assert result["bhamsa_rashi"]["sanskrit"] == "Dhanu"


def test_calculate_bhamsa_position_rejects_invalid_input() -> None:
    with pytest.raises(TypeError, match="sidereal_longitude must be a real number"):
        varga.calculate_bhamsa_position(False)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="longitude must be finite"):
        varga.calculate_bhamsa_position(float("inf"))

    with pytest.raises(ValueError, match="data must include sidereal_longitude"):
        varga.calculate_bhamsa_position({"planet": "mars"})


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
