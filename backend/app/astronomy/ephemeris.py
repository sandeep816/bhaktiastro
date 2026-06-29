"""Swiss Ephemeris loader and verification helpers."""

from __future__ import annotations

from importlib import import_module
import math
from pathlib import Path
from typing import Any

from backend.app.config import EPHE_PATH

VERIFICATION_JD_UT = 2460000.0
MIN_LONGITUDE_DEGREES = 0.0
MAX_LONGITUDE_DEGREES = 360.0


def _load_swisseph() -> Any:
    """Load the Swiss Ephemeris module.

    Returns:
        Imported `swisseph` module.

    Raises:
        RuntimeError: If `pyswisseph` is not installed.
    """
    try:
        return import_module("swisseph")
    except ImportError as exc:
        raise RuntimeError(
            "Swiss Ephemeris package 'pyswisseph' is required"
        ) from exc


def set_ephe_path() -> None:
    """Set the Swiss Ephemeris data path from project configuration.

    Raises:
        FileNotFoundError: If the configured ephemeris path does not exist.
        NotADirectoryError: If the configured ephemeris path is not a directory.
        RuntimeError: If `pyswisseph` is not installed.
    """
    ephe_path = Path(EPHE_PATH).expanduser()
    if not ephe_path.exists():
        raise FileNotFoundError(f"Swiss Ephemeris path does not exist: {ephe_path}")

    if not ephe_path.is_dir():
        raise NotADirectoryError(
            f"Swiss Ephemeris path is not a directory: {ephe_path}"
        )

    swe = _load_swisseph()
    swe.set_ephe_path(str(ephe_path))


def verify_ephemeris() -> bool:
    """Verify Swiss Ephemeris by calculating a valid Sun longitude.

    Returns:
        True if Swiss Ephemeris returns a finite Sun longitude in the
        `[0, 360)` range; otherwise False.

    Raises:
        RuntimeError: If `pyswisseph` is not installed.
    """
    swe = _load_swisseph()

    try:
        data, _ = swe.calc_ut(VERIFICATION_JD_UT, swe.SUN)
    except Exception:
        return False

    if not data:
        return False

    longitude = data[0]
    return (
        isinstance(longitude, (int, float))
        and math.isfinite(float(longitude))
        and MIN_LONGITUDE_DEGREES <= float(longitude) < MAX_LONGITUDE_DEGREES
    )
