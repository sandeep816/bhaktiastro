"""Tests for rise/set calculation helpers."""

from __future__ import annotations

from types import SimpleNamespace
import sys
import unittest
from unittest.mock import patch

from backend.app.astronomy import rise_set


class FakeSwissEphemeris(SimpleNamespace):
    """Small fake for Swiss Ephemeris rise/set calls."""

    SUN = 0
    MOON = 1
    GREG_CAL = 1
    FLG_SWIEPH = 2
    CALC_RISE = 1
    CALC_SET = 2
    BIT_DISC_CENTER = 256
    SUNRISE_JD = 2461220.529560185
    SUNSET_JD = 2461221.078240741
    MOONRISE_JD = 2461221.11412037
    MOONSET_JD = 2461220.646585648

    def __init__(self) -> None:
        super().__init__()
        self.ephe_path = None
        self.not_found = False
        self.calls: list[tuple[float, int, int, tuple[float, float, float], int]] = []

    def set_ephe_path(self, ephe_path: str) -> None:
        self.ephe_path = ephe_path

    def julday(
        self,
        year: int,
        month: int,
        day: int,
        utc_hour: float,
        calendar: int,
    ) -> float:
        return 2461220.2708333335

    def rise_trans(
        self,
        tjdut: float,
        body: int,
        rsmi: int,
        geopos: tuple[float, float, float],
        flags: int,
    ) -> tuple[int, tuple[float, ...]]:
        self.calls.append((tjdut, body, rsmi, geopos, flags))
        if self.not_found:
            return -2, ()

        if body == self.MOON and rsmi & self.CALC_RISE:
            return 0, (self.MOONRISE_JD,)
        if body == self.MOON:
            return 0, (self.MOONSET_JD,)
        if rsmi & self.CALC_RISE:
            return 0, (self.SUNRISE_JD,)

        return 0, (self.SUNSET_JD,)

    def revjul(
        self,
        jd_ut: float,
        calendar: int,
    ) -> tuple[int, int, int, float]:
        if jd_ut == self.SUNRISE_JD:
            return 2026, 6, 29, 0.7094444444
        if jd_ut == self.MOONRISE_JD:
            return 2026, 6, 29, 14.7388888889
        if jd_ut == self.MOONSET_JD:
            return 2026, 6, 29, 3.5180555556

        return 2026, 6, 29, 13.8708333333


class RiseSetTest(unittest.TestCase):
    """Validate rise/set outputs."""

    def setUp(self) -> None:
        self.fake_swisseph = FakeSwissEphemeris()
        self.swisseph_patch = patch.dict(
            sys.modules,
            {"swisseph": self.fake_swisseph},
        )
        self.swisseph_patch.start()

    def tearDown(self) -> None:
        self.swisseph_patch.stop()

    def test_jodhpur_date_returns_sunrise(self) -> None:
        result = rise_set.get_sunrise(2026, 6, 29, 26.2389, 73.0243, 5.5)

        self.assertEqual(result["event"], "sunrise")
        self.assertEqual(result["local_time"], "06:12:34")
        self.assertEqual(result["utc_datetime"], "2026-06-29T00:42:34Z")
        self.assertEqual(result["timezone_offset"], 5.5)
        self.assertEqual(self.fake_swisseph.calls[-1][2], 257)
        self.assertEqual(self.fake_swisseph.calls[-1][3], (73.0243, 26.2389, 0.0))

    def test_jodhpur_date_returns_sunset(self) -> None:
        result = rise_set.get_sunset(2026, 6, 29, 26.2389, 73.0243, 5.5)

        self.assertEqual(result["event"], "sunset")
        self.assertEqual(result["local_time"], "19:22:15")
        self.assertEqual(result["utc_datetime"], "2026-06-29T13:52:15Z")
        self.assertEqual(self.fake_swisseph.calls[-1][2], 258)

    def test_jodhpur_date_returns_moonrise(self) -> None:
        result = rise_set.get_moonrise(2026, 6, 29, 26.2389, 73.0243, 5.5)

        self.assertEqual(result["event"], "moonrise")
        self.assertEqual(result["local_time"], "20:14:20")
        self.assertEqual(result["utc_datetime"], "2026-06-29T14:44:20Z")
        self.assertEqual(result["timezone_offset"], 5.5)
        self.assertEqual(self.fake_swisseph.calls[-1][1], self.fake_swisseph.MOON)
        self.assertEqual(self.fake_swisseph.calls[-1][2], 257)
        self.assertEqual(self.fake_swisseph.calls[-1][3], (73.0243, 26.2389, 0.0))

    def test_jodhpur_date_returns_moonset(self) -> None:
        result = rise_set.get_moonset(2026, 6, 29, 26.2389, 73.0243, 5.5)

        self.assertEqual(result["event"], "moonset")
        self.assertEqual(result["local_time"], "09:01:05")
        self.assertEqual(result["utc_datetime"], "2026-06-29T03:31:05Z")
        self.assertEqual(self.fake_swisseph.calls[-1][1], self.fake_swisseph.MOON)
        self.assertEqual(self.fake_swisseph.calls[-1][2], 258)

    def test_invalid_latitude_raises_clear_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "latitude must be between"):
            rise_set.get_moonrise(2026, 6, 29, 91.0, 73.0243, 5.5)

    def test_invalid_longitude_raises_clear_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "longitude must be between"):
            rise_set.get_moonset(2026, 6, 29, 26.2389, 181.0, 5.5)

    def test_event_not_found_does_not_crash(self) -> None:
        self.fake_swisseph.not_found = True

        result = rise_set.get_moonrise(2026, 6, 29, 70.0, 73.0243, 5.5)

        self.assertEqual(
            result,
            {
                "event": "moonrise",
                "local_time": None,
                "utc_datetime": None,
                "timezone_offset": 5.5,
            },
        )


if __name__ == "__main__":
    unittest.main()
