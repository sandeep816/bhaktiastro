"""Tests for ayanamsa calculation."""

from __future__ import annotations

from types import SimpleNamespace
import sys

import pytest

from backend.app.astronomy import ayanamsa


class FakeSwissEphemeris(SimpleNamespace):
    """Small fake matching the Swiss Ephemeris calls used by ayanamsa."""

    SIDM_LAHIRI = 1
    SIDM_RAMAN = 2
    SIDM_KRISHNAMURTI = 3

    def __init__(self) -> None:
        super().__init__()
        self.selected_mode = None
        self.requested_jd_ut = None
        self.ayanamsa_value = 23.72

    def set_sid_mode(self, mode: int) -> None:
        self.selected_mode = mode

    def get_ayanamsa_ut(self, jd_ut: float) -> float:
        self.requested_jd_ut = jd_ut
        return self.ayanamsa_value


@pytest.fixture
def fake_swisseph(monkeypatch: pytest.MonkeyPatch) -> FakeSwissEphemeris:
    fake = FakeSwissEphemeris()
    monkeypatch.setitem(sys.modules, "swisseph", fake)
    return fake


def test_get_ayanamsa_uses_configured_default_lahiri(
    fake_swisseph: FakeSwissEphemeris,
) -> None:
    value = ayanamsa.get_ayanamsa(2446176.027777)

    assert value == 23.72
    assert fake_swisseph.selected_mode == fake_swisseph.SIDM_LAHIRI
    assert fake_swisseph.requested_jd_ut == 2446176.027777


@pytest.mark.parametrize(
    ("mode", "expected_sidereal_mode"),
    [
        ("lahiri", FakeSwissEphemeris.SIDM_LAHIRI),
        ("raman", FakeSwissEphemeris.SIDM_RAMAN),
        ("kp", FakeSwissEphemeris.SIDM_KRISHNAMURTI),
    ],
)
def test_get_ayanamsa_supports_documented_modes(
    fake_swisseph: FakeSwissEphemeris,
    mode: str,
    expected_sidereal_mode: int,
) -> None:
    ayanamsa.get_ayanamsa(2446176.027777, mode)

    assert fake_swisseph.selected_mode == expected_sidereal_mode


def test_get_ayanamsa_normalizes_mode_name(
    fake_swisseph: FakeSwissEphemeris,
) -> None:
    ayanamsa.get_ayanamsa(2446176.027777, " Lahiri ")

    assert fake_swisseph.selected_mode == fake_swisseph.SIDM_LAHIRI


def test_get_ayanamsa_rejects_unknown_mode(
    fake_swisseph: FakeSwissEphemeris,
) -> None:
    with pytest.raises(ValueError, match="Unknown ayanamsa mode"):
        ayanamsa.get_ayanamsa(2446176.027777, "unknown")


def test_get_ayanamsa_rejects_non_numeric_jd(
    fake_swisseph: FakeSwissEphemeris,
) -> None:
    with pytest.raises(TypeError, match="jd_ut must be a numeric"):
        ayanamsa.get_ayanamsa("2446176.027777")  # type: ignore[arg-type]


def test_get_ayanamsa_rejects_non_finite_jd(
    fake_swisseph: FakeSwissEphemeris,
) -> None:
    with pytest.raises(ValueError, match="jd_ut must be finite"):
        ayanamsa.get_ayanamsa(float("nan"))


def test_get_ayanamsa_reports_missing_swisseph(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_import_error(module_name: str) -> None:
        raise ImportError(module_name)

    monkeypatch.setattr(ayanamsa, "import_module", raise_import_error)

    with pytest.raises(RuntimeError, match="pyswisseph"):
        ayanamsa.get_ayanamsa(2446176.027777)
