"""Structural tests for generated Panchang validation fixtures."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

try:
    from backend.app.api.v1.panchang import get_panchang
    from backend.app.schemas.panchang import PanchangRequest, PanchangResponse
except ModuleNotFoundError:
    get_panchang = None  # type: ignore[assignment]
    PanchangRequest = None  # type: ignore[assignment]
    PanchangResponse = None  # type: ignore[assignment]


FIXTURE_DIR = Path(__file__).parent / "fixtures"

PANCHANG_FIXTURE_CASES = {
    "jodhpur_1985_04_20": {
        "fixture": FIXTURE_DIR / "panchang_jodhpur_1985_04_20.json",
        "request": {
            "year": 1985,
            "month": 4,
            "day": 20,
            "hour": 18,
            "minute": 10,
            "second": 0,
            "timezone_offset": 5.5,
            "latitude": 26.2389,
            "longitude": 73.0243,
            "language": "hi",
            "ayanamsa": "lahiri",
        },
    },
    "delhi_2000_01_01": {
        "fixture": FIXTURE_DIR / "panchang_delhi_2000_01_01.json",
        "request": {
            "year": 2000,
            "month": 1,
            "day": 1,
            "hour": 12,
            "minute": 0,
            "second": 0,
            "timezone_offset": 5.5,
            "latitude": 28.6139,
            "longitude": 77.2090,
            "language": "hi",
            "ayanamsa": "lahiri",
        },
    },
}


@unittest.skipIf(PanchangRequest is None, "fastapi or pydantic is not installed")
class PanchangFixtureTest(unittest.TestCase):
    """Validate Panchang fixtures as structural snapshots only."""

    def test_fixture_files_exist(self) -> None:
        for case_name, case in PANCHANG_FIXTURE_CASES.items():
            with self.subTest(case=case_name):
                self.assertTrue(case["fixture"].is_file())

    def test_fixture_files_validate_against_response_schema(self) -> None:
        for case_name, case in PANCHANG_FIXTURE_CASES.items():
            with self.subTest(case=case_name):
                PanchangResponse.model_validate(_read_json(case["fixture"]))

    def test_api_output_contains_all_fixture_keys(self) -> None:
        for case_name, case in PANCHANG_FIXTURE_CASES.items():
            fixture = _read_json(case["fixture"])
            current_output = _calculate_case(case["request"])

            with self.subTest(case=case_name):
                _assert_contains_fixture_keys(self, current_output, fixture)

    def test_api_output_structure_matches_fixture_structure(self) -> None:
        for case_name, case in PANCHANG_FIXTURE_CASES.items():
            fixture = _read_json(case["fixture"])
            current_output = _calculate_case(case["request"])

            with self.subTest(case=case_name):
                self.assertEqual(_structure_of(current_output), _structure_of(fixture))

    @unittest.skip(
        "TODO: exact Panchang values require manual verification against two trusted "
        "references before this can become a golden-value test."
    )
    def test_api_output_exact_values_match_verified_fixtures(self) -> None:
        for case_name, case in PANCHANG_FIXTURE_CASES.items():
            fixture = _read_json(case["fixture"])
            current_output = _calculate_case(case["request"])

            with self.subTest(case=case_name):
                self.assertEqual(current_output, fixture)


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _calculate_case(request_payload: dict[str, object]) -> dict[str, object]:
    request = PanchangRequest(**request_payload)
    return get_panchang(request).model_dump(mode="json")


def _assert_contains_fixture_keys(
    test_case: unittest.TestCase,
    current_output: object,
    fixture: object,
    path: str = "$",
) -> None:
    if isinstance(fixture, dict):
        test_case.assertIsInstance(current_output, dict, path)
        for key, fixture_value in fixture.items():
            test_case.assertIn(key, current_output, path)
            _assert_contains_fixture_keys(
                test_case,
                current_output[key],
                fixture_value,
                f"{path}.{key}",
            )


def _structure_of(value: object) -> object:
    if isinstance(value, dict):
        return {key: _structure_of(child) for key, child in value.items()}
    if isinstance(value, list):
        return [_structure_of(item) for item in value]
    return type(value).__name__


if __name__ == "__main__":
    unittest.main()
