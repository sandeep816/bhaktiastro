"""Tests for the local Panchang smoke script."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "smoke_panchang.py"
REQUIRED_OUTPUT_KEYS = {
    "tithi",
    "nakshatra",
    "yoga",
    "karana",
    "vara",
    "sunrise",
    "sunset",
}


def _runtime_dependencies_available() -> bool:
    return all(
        importlib.util.find_spec(module_name) is not None
        for module_name in ("fastapi", "pydantic", "swisseph")
    )


@unittest.skipUnless(
    _runtime_dependencies_available(),
    "Panchang runtime dependencies are not installed",
)
class PanchangSmokeScriptTest(unittest.TestCase):
    """Validate the developer Panchang smoke script."""

    def test_script_imports_successfully(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "smoke_panchang_under_test",
            SCRIPT_PATH,
        )
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        self.assertTrue(callable(module.calculate_sample_panchang))
        self.assertTrue(callable(module.main))

    def test_script_runs_and_prints_required_panchang_sections(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH)],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        output = json.loads(result.stdout)

        self.assertTrue(REQUIRED_OUTPUT_KEYS.issubset(output.keys()))


if __name__ == "__main__":
    unittest.main()
