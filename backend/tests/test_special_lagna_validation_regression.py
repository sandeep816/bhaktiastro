"""Validation and regression coverage for Special Lagna foundations."""

from __future__ import annotations

from datetime import datetime
import json

from backend.app.api.v1.kundali import get_kundali
from backend.app.kundali.arudha_lagna import calculate_arudha_lagna
from backend.app.kundali.bhava_cusps import calculate_bhava_cusps
from backend.app.kundali.ghati_lagna import calculate_ghati_lagna
from backend.app.kundali.hora_lagna import calculate_hora_lagna
from backend.app.kundali.special_lagna_summary import build_special_lagna_summary
from backend.app.kundali.upapada_lagna import calculate_upapada_lagna
from backend.app.schemas.kundali import KundaliRequest


def test_missing_lagna_data_is_handled_safely() -> None:
    result = build_special_lagna_summary({"planets": []}, _sample_context())

    assert result["arudha_lagna"]["metadata"]["missing_fields"] == ["lagna_rashi"]
    assert result["upapada_lagna"]["metadata"]["missing_fields"] == ["lagna_rashi"]
    assert result["hora_lagna"]["metadata"]["missing_fields"] == ["lagna_longitude"]
    assert result["ghati_lagna"]["metadata"]["missing_fields"] == ["lagna_longitude"]
    assert result["bhava_cusps"]["metadata"]["missing_fields"] == ["lagna_longitude"]
    assert_json_safe(result)


def test_missing_lagna_lord_placement_is_handled_safely() -> None:
    result = calculate_arudha_lagna(
        {
            "lagna": {"rashi_index": 1},
            "planets": [{"planet": "venus", "house_number": 2}],
        }
    )

    assert result["arudha_lagna"] is None
    assert result["lagna_lord"] == "mars"
    assert result["lagna_lord_house"] is None
    assert result["metadata"]["calculation_status"] == "missing_data"
    assert result["metadata"]["missing_fields"] == ["lagna_lord_house"]
    assert_json_safe(result)


def test_missing_birth_datetime_is_handled_safely() -> None:
    result = build_special_lagna_summary(
        _sample_chart(),
        {"sunrise_datetime": datetime(2026, 1, 1, 6, 0, 0)},
    )

    assert result["metadata"]["birth_datetime_available"] is False
    assert result["hora_lagna"]["metadata"]["missing_fields"] == ["birth_datetime"]
    assert result["ghati_lagna"]["metadata"]["missing_fields"] == ["birth_datetime"]
    assert_json_safe(result)


def test_missing_sunrise_datetime_is_handled_safely() -> None:
    result = build_special_lagna_summary(
        _sample_chart(),
        {"birth_datetime": datetime(2026, 1, 1, 8, 0, 0)},
    )

    assert result["metadata"]["sunrise_datetime_available"] is False
    assert result["hora_lagna"]["metadata"]["missing_fields"] == ["sunrise_datetime"]
    assert result["ghati_lagna"]["metadata"]["missing_fields"] == ["sunrise_datetime"]
    assert_json_safe(result)


def test_invalid_longitude_is_handled_safely() -> None:
    hora = calculate_hora_lagna(
        lagna_longitude=float("nan"),
        birth_datetime=datetime(2026, 1, 1, 8, 0, 0),
        sunrise_datetime=datetime(2026, 1, 1, 6, 0, 0),
    )
    ghati = calculate_ghati_lagna(
        lagna_longitude=float("nan"),
        birth_datetime=datetime(2026, 1, 1, 8, 0, 0),
        sunrise_datetime=datetime(2026, 1, 1, 6, 0, 0),
    )
    cusps = calculate_bhava_cusps(float("nan"))

    assert hora["metadata"]["missing_fields"] == ["lagna_longitude"]
    assert ghati["metadata"]["missing_fields"] == ["lagna_longitude"]
    assert cusps["metadata"]["missing_fields"] == ["lagna_longitude"]
    assert_json_safe(hora)
    assert_json_safe(ghati)
    assert_json_safe(cusps)


def test_invalid_house_number_is_handled_safely() -> None:
    arudha = calculate_arudha_lagna(
        {
            "lagna": {"rashi_index": 1},
            "planets": [{"planet": "mars", "house_number": True}],
        }
    )
    upapada = calculate_upapada_lagna(
        {
            "lagna": {"rashi_index": 1},
            "planets": [{"planet": "jupiter", "house_number": "12"}],
        }
    )

    assert arudha["metadata"]["missing_fields"] == ["lagna_lord_house"]
    assert upapada["metadata"]["missing_fields"] == ["source_lord_house"]
    assert_json_safe(arudha)
    assert_json_safe(upapada)


def test_missing_chart_planet_data_is_handled_safely() -> None:
    result = build_special_lagna_summary(
        {"lagna": {"rashi_index": 1}},
        _sample_context(),
    )

    assert result["arudha_lagna"]["metadata"]["missing_fields"] == [
        "lagna_lord_house"
    ]
    assert result["upapada_lagna"]["metadata"]["missing_fields"] == [
        "source_lord_house"
    ]
    assert_json_safe(result)


def test_arudha_lagna_output_is_json_safe_and_structural() -> None:
    result = calculate_arudha_lagna(_sample_chart())

    assert_required_keys(
        result,
        {
            "arudha_lagna",
            "arudha_rashi",
            "lagna_rashi",
            "lagna_lord",
            "lagna_lord_house",
            "calculation_steps",
            "metadata",
        },
    )
    assert result["arudha_lagna"] in range(1, 13)
    assert_rashi_metadata(result["arudha_rashi"])
    assert_json_safe(result)


def test_upapada_lagna_output_is_json_safe_and_structural() -> None:
    result = calculate_upapada_lagna(_sample_chart())

    assert_required_keys(
        result,
        {
            "upapada_lagna",
            "upapada_rashi",
            "source_house",
            "source_rashi",
            "source_lord",
            "source_lord_house",
            "calculation_steps",
            "metadata",
        },
    )
    assert result["upapada_lagna"] in range(1, 13)
    assert_rashi_metadata(result["upapada_rashi"])
    assert_json_safe(result)


def test_hora_lagna_output_is_json_safe_and_normalized() -> None:
    result = calculate_hora_lagna(
        lagna_longitude=350.0,
        birth_datetime=datetime(2026, 1, 1, 8, 0, 0),
        sunrise_datetime=datetime(2026, 1, 1, 6, 0, 0),
    )

    assert_required_keys(
        result,
        {
            "hora_lagna_longitude",
            "rashi",
            "rashi_index",
            "rashi_degree",
            "elapsed_time",
            "calculation_steps",
            "metadata",
        },
    )
    assert_normalized_longitude(result["hora_lagna_longitude"])
    assert_rashi_metadata(result["rashi"])
    assert_json_safe(result)


def test_ghati_lagna_output_is_json_safe_and_normalized() -> None:
    result = calculate_ghati_lagna(
        lagna_longitude=350.0,
        birth_datetime=datetime(2026, 1, 1, 8, 0, 0),
        sunrise_datetime=datetime(2026, 1, 1, 6, 0, 0),
    )

    assert_required_keys(
        result,
        {
            "ghati_lagna_longitude",
            "rashi",
            "rashi_index",
            "rashi_degree",
            "elapsed_time",
            "elapsed_ghatis",
            "calculation_steps",
            "metadata",
        },
    )
    assert_normalized_longitude(result["ghati_lagna_longitude"])
    assert_rashi_metadata(result["rashi"])
    assert_json_safe(result)


def test_bhava_cusps_output_is_json_safe_and_structural() -> None:
    result = calculate_bhava_cusps(350.0)

    assert_required_keys(result, {"house_cusps", "house_system", "metadata"})
    assert len(result["house_cusps"]) == 12
    assert [cusp["house_number"] for cusp in result["house_cusps"]] == list(
        range(1, 13)
    )
    for cusp in result["house_cusps"]:
        assert_normalized_longitude(cusp["cusp_longitude"])
        assert_rashi_metadata(cusp["rashi"])
        assert {"rashi_index", "rashi_degree"} <= set(cusp)
    assert_json_safe(result)


def test_special_lagna_summary_output_is_json_safe_and_structural() -> None:
    result = build_special_lagna_summary(_sample_chart(), _sample_context())

    assert_required_keys(
        result,
        {
            "arudha_lagna",
            "upapada_lagna",
            "hora_lagna",
            "ghati_lagna",
            "bhava_cusps",
            "metadata",
        },
    )
    assert len(result["bhava_cusps"]["house_cusps"]) == 12
    assert_normalized_longitude(result["hora_lagna"]["hora_lagna_longitude"])
    assert_normalized_longitude(result["ghati_lagna"]["ghati_lagna_longitude"])
    assert_json_safe(result)


def test_kundali_api_with_include_special_lagnas_is_json_safe() -> None:
    response = get_kundali(_jaipur_request(include_special_lagnas=True))
    data = response.model_dump(mode="json")

    assert "special_lagna" in data
    assert_required_keys(
        data["special_lagna"],
        {
            "arudha_lagna",
            "upapada_lagna",
            "hora_lagna",
            "ghati_lagna",
            "bhava_cusps",
            "metadata",
        },
    )
    assert len(data["special_lagna"]["bhava_cusps"]["house_cusps"]) == 12
    assert_json_safe(data)


def test_kundali_api_without_special_lagnas_remains_backward_compatible() -> None:
    response = get_kundali(_jaipur_request())
    data = response.model_dump(mode="json")

    assert set(data) == {"lagna", "planets", "houses"}
    assert "special_lagna" not in data
    assert_json_safe(data)


def assert_required_keys(result: dict[str, object], keys: set[str]) -> None:
    assert keys <= set(result)


def assert_normalized_longitude(value: object) -> None:
    assert isinstance(value, int | float)
    assert 0.0 <= float(value) < 360.0


def assert_rashi_metadata(rashi: object) -> None:
    assert isinstance(rashi, dict)
    assert {"index", "english", "hindi", "sanskrit"} <= set(rashi)


def assert_json_safe(result: object) -> None:
    json.dumps(result)


def _sample_chart() -> dict[str, object]:
    return {
        "lagna": {
            "rashi_index": 1,
            "sidereal_longitude": 10.0,
        },
        "planets": [
            {"planet": "mars", "house_number": 2},
            {"planet": "jupiter", "house_number": 2},
        ],
    }


def _sample_context() -> dict[str, datetime]:
    return {
        "birth_datetime": datetime(2026, 1, 1, 8, 0, 0),
        "sunrise_datetime": datetime(2026, 1, 1, 6, 0, 0),
    }


def _jaipur_request(*, include_special_lagnas: bool = False) -> KundaliRequest:
    return KundaliRequest(
        year=1990,
        month=1,
        day=1,
        hour=12,
        minute=0,
        second=0,
        timezone_offset=5.5,
        latitude=26.9124,
        longitude=75.7873,
        ayanamsa="lahiri",
        include_special_lagnas=include_special_lagnas,
    )
