"""Tests for Prediction Analyzer Adapter interfaces."""

from __future__ import annotations

from copy import deepcopy
import json

from backend.app.prediction.adapters import AshtakavargaAdapter
from backend.app.prediction.adapters import DashaAdapter
from backend.app.prediction.adapters import HouseAnalyzerAdapter
from backend.app.prediction.adapters import LagnaAdapter
from backend.app.prediction.adapters import PlanetAnalyzerAdapter
from backend.app.prediction.adapters import StrengthAdapter
from backend.app.prediction.adapters import YogaAdapter


def test_planet_adapter_reads_planet_values() -> None:
    adapter = PlanetAnalyzerAdapter(_sample_chart())

    mars = adapter.get_planet("Mars")

    assert mars is not None
    assert mars["planet"] == "Mars"
    assert adapter.get_house("mars") == 10
    assert adapter.get_rashi("mars") == "Makara"
    assert adapter.get_longitude("mars") == 278.25


def test_house_adapter_reads_house_values() -> None:
    adapter = HouseAnalyzerAdapter(_sample_chart())

    house = adapter.get_house(10)

    assert house is not None
    assert house["house_number"] == 10
    assert adapter.get_house_lord(10) == "Saturn"


def test_strength_adapter_reads_strength_values() -> None:
    adapter = StrengthAdapter(_sample_strength())

    strength = adapter.get_strength("Jupiter")

    assert strength is not None
    assert strength["summary_status"] == "favorable"
    assert adapter.get_strength_percentage("jupiter") == 72.5


def test_dasha_adapter_reads_current_dasha() -> None:
    adapter = DashaAdapter(_sample_dasha())

    current = adapter.get_current_dasha()

    assert current is not None
    assert adapter.get_lord("mahadasha") == "Saturn"
    assert adapter.get_lord("antardasha") == "Mercury"


def test_ashtakavarga_adapter_reads_summary_values() -> None:
    adapter = AshtakavargaAdapter(_sample_ashtakavarga())

    sarvashtakavarga = adapter.get_sarvashtakavarga()

    assert sarvashtakavarga is not None
    assert adapter.get_house_bindus(10) == 35
    assert adapter.get_planet_bav("Sun") == {"houses": {"10": 5}, "total_bindus": 5}


def test_lagna_adapter_reads_lagna_values() -> None:
    adapter = LagnaAdapter(_sample_chart(), _sample_special_lagna())

    lagna = adapter.get_lagna()
    arudha = adapter.get_special_lagna("arudha_lagna")

    assert lagna is not None
    assert lagna["rashi"]["sanskrit"] == "Mesha"
    assert arudha is not None
    assert arudha["arudha_rashi"] == "Simha"


def test_yoga_adapter_reads_yoga_values() -> None:
    adapter = YogaAdapter(_sample_yogas())

    yoga = adapter.get_yoga("Gajakesari Yoga")

    assert yoga is not None
    assert yoga["strength"] == "not_evaluated"
    assert adapter.has_yoga("gajakesari_yoga") is True


def test_adapters_handle_missing_values_safely() -> None:
    assert PlanetAnalyzerAdapter({}).get_planet("Mars") is None
    assert PlanetAnalyzerAdapter({}).get_house("Mars") is None
    assert HouseAnalyzerAdapter({}).get_house(1) is None
    assert HouseAnalyzerAdapter({}).get_house_lord(1) is None
    assert StrengthAdapter({}).get_strength("Mars") is None
    assert DashaAdapter({}).get_current_dasha() is None
    assert AshtakavargaAdapter({}).get_house_bindus(1) is None
    assert LagnaAdapter({}).get_lagna() is None
    assert YogaAdapter([]).has_yoga("missing") is None


def test_adapters_do_not_mutate_input() -> None:
    chart = _sample_chart()
    original = deepcopy(chart)
    adapter = PlanetAnalyzerAdapter(chart)
    returned = adapter.get_planet("Mars")

    assert returned is not None
    returned["house_number"] = 1

    assert chart == original


def test_adapter_outputs_are_json_serializable() -> None:
    payload = {
        "planet": PlanetAnalyzerAdapter(_sample_chart()).get_planet("Mars"),
        "house": HouseAnalyzerAdapter(_sample_chart()).get_house(10),
        "strength": StrengthAdapter(_sample_strength()).get_strength("Jupiter"),
        "dasha": DashaAdapter(_sample_dasha()).get_current_dasha(),
        "ashtakavarga": AshtakavargaAdapter(
            _sample_ashtakavarga()
        ).get_sarvashtakavarga(),
        "lagna": LagnaAdapter(_sample_chart()).get_lagna(),
        "yoga": YogaAdapter(_sample_yogas()).get_yoga("Gajakesari Yoga"),
    }

    json.dumps(payload)


def _sample_chart() -> dict[str, object]:
    mars = {
        "planet": "Mars",
        "sidereal_longitude": 278.25,
        "rashi": {"sanskrit": "Makara", "english": "Capricorn", "index": 10},
        "house_number": 10,
    }

    return {
        "lagna": {
            "rashi": {"sanskrit": "Mesha", "english": "Aries", "index": 1},
            "sidereal_longitude": 12.5,
        },
        "planets": [mars],
        "houses": [
            {
                "house_number": 10,
                "planets": [mars],
                "rashi": {"sanskrit": "Makara", "lord": "Saturn"},
            }
        ],
    }


def _sample_strength() -> dict[str, object]:
    return {
        "planets": [
            {
                "planet": "Jupiter",
                "shadbala": {
                    "strength_percentage": 72.5,
                    "status": "strong",
                },
                "summary_status": "favorable",
            }
        ]
    }


def _sample_dasha() -> dict[str, object]:
    return {
        "current_dasha": {
            "mahadasha": {"lord": "Saturn"},
            "antardasha": {"planet": "Mercury"},
        }
    }


def _sample_ashtakavarga() -> dict[str, object]:
    return {
        "sarvashtakavarga": {
            "houses": {1: 24, 10: 35},
            "total_bindus": 59,
        },
        "bhinnashtakavarga": {
            "sun": {
                "houses": {10: 5},
                "total_bindus": 5,
            }
        },
    }


def _sample_special_lagna() -> dict[str, object]:
    return {
        "arudha_lagna": {
            "arudha_lagna": 5,
            "arudha_rashi": "Simha",
        }
    }


def _sample_yogas() -> list[dict[str, object]]:
    return [
        {
            "yoga_name": "Gajakesari Yoga",
            "is_present": True,
            "strength": "not_evaluated",
        }
    ]
