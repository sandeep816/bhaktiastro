"""Developer smoke script for the local Panchang calculation path."""

from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.api.v1.panchang import get_panchang
from backend.app.schemas.panchang import PanchangRequest


SAMPLE_PANCHANG_REQUEST = {
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
}


def calculate_sample_panchang() -> dict[str, object]:
    """Return API-shaped Panchang output for the standard Jodhpur sample."""

    request = PanchangRequest(**SAMPLE_PANCHANG_REQUEST)
    return get_panchang(request).model_dump(mode="json")


def main() -> None:
    """Print the sample Panchang response as clean JSON."""

    print(json.dumps(calculate_sample_panchang(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
