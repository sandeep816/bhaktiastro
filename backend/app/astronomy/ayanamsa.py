"""Ayanamsa calculation helpers."""

from __future__ import annotations

from importlib import import_module
import math
from typing import Any, Optional

from backend.app.config import AYANAMSA_DEFAULT, AYANAMSA_OPTIONS


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


def _normalize_mode(mode: Optional[str]) -> str:
    """Normalize and validate an ayanamsa mode name."""
    selected_mode = AYANAMSA_DEFAULT if mode is None else mode
    normalized_mode = selected_mode.strip().lower()

    if normalized_mode not in AYANAMSA_OPTIONS:
        supported_modes = ", ".join(AYANAMSA_OPTIONS)
        raise ValueError(
            f"Unknown ayanamsa mode: {mode}. Supported modes: {supported_modes}"
        )

    return normalized_mode


def get_ayanamsa(jd_ut: float, mode: Optional[str] = None) -> float:
    """Calculate ayanamsa for a Julian Day UT.

    Args:
        jd_ut: Julian Day in Universal Time.
        mode: Ayanamsa mode. Supported values are `lahiri`, `raman`, and `kp`.
            If omitted, the configured default ayanamsa is used.

    Returns:
        Ayanamsa value in degrees.

    Raises:
        TypeError: If `jd_ut` is not numeric.
        ValueError: If `jd_ut` is not finite or `mode` is unsupported.
        RuntimeError: If `pyswisseph` is not installed.
    """
    if isinstance(jd_ut, bool) or not isinstance(jd_ut, (int, float)):
        raise TypeError("jd_ut must be a numeric Julian Day UT")

    jd_ut_float = float(jd_ut)
    if not math.isfinite(jd_ut_float):
        raise ValueError("jd_ut must be finite")

    normalized_mode = _normalize_mode(mode)
    swe = _load_swisseph()

    mode_to_sidereal_constant = {
        "lahiri": swe.SIDM_LAHIRI,
        "raman": swe.SIDM_RAMAN,
        "kp": swe.SIDM_KRISHNAMURTI,
    }

    swe.set_sid_mode(mode_to_sidereal_constant[normalized_mode])
    return float(swe.get_ayanamsa_ut(jd_ut_float))
