"""Special Lagna summary builder."""

from __future__ import annotations

from collections.abc import Mapping
from numbers import Real
from typing import Any, TypedDict

from backend.app.kundali.arudha_lagna import ArudhaLagnaResult
from backend.app.kundali.arudha_lagna import calculate_arudha_lagna
from backend.app.kundali.bhava_cusps import BhavaCuspResult
from backend.app.kundali.bhava_cusps import calculate_bhava_cusps
from backend.app.kundali.ghati_lagna import GhatiLagnaResult
from backend.app.kundali.ghati_lagna import calculate_ghati_lagna
from backend.app.kundali.hora_lagna import HoraLagnaResult
from backend.app.kundali.hora_lagna import calculate_hora_lagna
from backend.app.kundali.upapada_lagna import UpapadaLagnaResult
from backend.app.kundali.upapada_lagna import calculate_upapada_lagna

SPECIAL_LAGNA_SUMMARY_COMPONENT = "special_lagna_summary"
SPECIAL_LAGNA_SUMMARY_STATUS = "foundation"
SPECIAL_LAGNA_COMPONENTS = (
    "arudha_lagna",
    "upapada_lagna",
    "hora_lagna",
    "ghati_lagna",
    "bhava_cusps",
)
INVALID_LAGNA_LONGITUDE = float("nan")


class SpecialLagnaSummary(TypedDict):
    """JSON-safe special Lagna summary result."""

    arudha_lagna: ArudhaLagnaResult
    upapada_lagna: UpapadaLagnaResult
    hora_lagna: HoraLagnaResult
    ghati_lagna: GhatiLagnaResult
    bhava_cusps: BhavaCuspResult
    metadata: dict[str, object]


def build_special_lagna_summary(
    chart_data: dict[str, Any],
    context: dict[str, Any] | None = None,
) -> SpecialLagnaSummary:
    """Build a foundation-level summary of supported special Lagna outputs."""

    source_chart: Mapping[str, Any] = chart_data if isinstance(chart_data, Mapping) else {}
    source_context: Mapping[str, Any] = context if isinstance(context, Mapping) else {}
    lagna_longitude = _get_lagna_longitude(source_chart)
    safe_lagna_longitude = (
        lagna_longitude if lagna_longitude is not None else INVALID_LAGNA_LONGITUDE
    )
    birth_datetime = source_context.get("birth_datetime")
    sunrise_datetime = source_context.get("sunrise_datetime")

    arudha_lagna = calculate_arudha_lagna(dict(source_chart))
    upapada_lagna = calculate_upapada_lagna(dict(source_chart))
    hora_lagna = calculate_hora_lagna(
        safe_lagna_longitude,
        birth_datetime,
        sunrise_datetime,
    )
    ghati_lagna = calculate_ghati_lagna(
        safe_lagna_longitude,
        birth_datetime,
        sunrise_datetime,
    )
    bhava_cusps = calculate_bhava_cusps(safe_lagna_longitude)

    return {
        "arudha_lagna": arudha_lagna,
        "upapada_lagna": upapada_lagna,
        "hora_lagna": hora_lagna,
        "ghati_lagna": ghati_lagna,
        "bhava_cusps": bhava_cusps,
        "metadata": {
            "calculation_status": SPECIAL_LAGNA_SUMMARY_STATUS,
            "component": SPECIAL_LAGNA_SUMMARY_COMPONENT,
            "components": list(SPECIAL_LAGNA_COMPONENTS),
            "chart_data_available": isinstance(chart_data, Mapping),
            "context_available": isinstance(context, Mapping),
            "lagna_longitude_available": lagna_longitude is not None,
            "birth_datetime_available": birth_datetime is not None,
            "sunrise_datetime_available": sunrise_datetime is not None,
        },
    }


def _get_lagna_longitude(chart_data: Mapping[str, Any]) -> float | None:
    """Return the chart Lagna longitude when present and numeric."""

    lagna = chart_data.get("lagna")
    if not isinstance(lagna, Mapping):
        return None

    for key in (
        "sidereal_longitude",
        "ascendant_longitude",
        "lagna_longitude",
        "longitude",
    ):
        value = lagna.get(key)
        if isinstance(value, bool) or not isinstance(value, Real):
            continue
        return float(value)

    return None
