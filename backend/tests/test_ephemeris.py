"""Tests for Swiss Ephemeris loader helpers."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import sys

import pytest

from backend.app.astronomy import ephemeris


class FakeSwissEphemeris(SimpleNamespace):
    """Small fake matching the Swiss Ephemeris calls used by the loader."""

    SUN = 0

    def __init__(self) -> None:
        super().__init__()
        self.ephe_path = None
        self.longitude = 123.456
        self.raise_on_calc = False

    def set_ephe_path(self, ephe_path: str) -> None:
        self.ephe_path = ephe_path

    def calc_ut(self, jd_ut: float, planet_id: int) -> tuple[tuple[float], int]:
        if self.raise_on_calc:
            raise RuntimeError("calculation failed")
        return (self.longitude,), 0


@pytest.fixture
def fake_swisseph(monkeypatch: pytest.MonkeyPatch) -> FakeSwissEphemeris:
    fake = FakeSwissEphemeris()
    monkeypatch.setitem(sys.modules, "swisseph", fake)
    return fake


def test_set_ephe_path_uses_configured_directory(
    tmp_path: Path,
    fake_swisseph: FakeSwissEphemeris,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(ephemeris, "EPHE_PATH", str(tmp_path))

    ephemeris.set_ephe_path()

    assert fake_swisseph.ephe_path == str(tmp_path)


def test_set_ephe_path_rejects_missing_directory(
    tmp_path: Path,
    fake_swisseph: FakeSwissEphemeris,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(ephemeris, "EPHE_PATH", str(tmp_path / "missing"))

    with pytest.raises(FileNotFoundError, match="Swiss Ephemeris path"):
        ephemeris.set_ephe_path()


def test_set_ephe_path_rejects_file_path(
    tmp_path: Path,
    fake_swisseph: FakeSwissEphemeris,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ephe_file = tmp_path / "not-a-directory"
    ephe_file.write_text("", encoding="utf-8")
    monkeypatch.setattr(ephemeris, "EPHE_PATH", str(ephe_file))

    with pytest.raises(NotADirectoryError, match="not a directory"):
        ephemeris.set_ephe_path()


def test_verify_ephemeris_returns_true_for_valid_sun_longitude(
    fake_swisseph: FakeSwissEphemeris,
) -> None:
    assert ephemeris.verify_ephemeris() is True


def test_verify_ephemeris_returns_false_for_invalid_longitude(
    fake_swisseph: FakeSwissEphemeris,
) -> None:
    fake_swisseph.longitude = 360.0

    assert ephemeris.verify_ephemeris() is False


def test_verify_ephemeris_returns_false_when_calculation_fails(
    fake_swisseph: FakeSwissEphemeris,
) -> None:
    fake_swisseph.raise_on_calc = True

    assert ephemeris.verify_ephemeris() is False
