"""Reusable helpers for longitudinal motion status."""

from __future__ import annotations

import math
from numbers import Real
from typing import Literal

MotionStatus = Literal["retrograde", "direct", "stationary"]


def is_retrograde(speed_longitude: float) -> bool:
    """Return whether longitudinal speed indicates retrograde motion."""

    return _validate_speed(speed_longitude) < 0


def get_motion_status(speed_longitude: float) -> MotionStatus:
    """Return retrograde, direct, or stationary from longitudinal speed."""

    speed = _validate_speed(speed_longitude)
    if speed < 0:
        return "retrograde"

    if speed > 0:
        return "direct"

    return "stationary"


def _validate_speed(speed_longitude: float) -> float:
    """Validate speed as a finite real number."""

    if isinstance(speed_longitude, bool) or not isinstance(speed_longitude, Real):
        raise TypeError("speed_longitude must be a real number")

    speed = float(speed_longitude)
    if not math.isfinite(speed):
        raise ValueError("speed_longitude must be finite")

    return speed
