# Validation Plan

## Purpose

This document defines the future accuracy verification framework for BhaktiAstro
astronomical and Panchang calculations. It is a milestone framework only.

No calculation is marked verified by this document. Exact-value verification
must be done manually against trusted references before any skipped validation
test is enabled.

## Validation Sources

Approved reference sources for future manual validation:

- Drik Panchang
- Jagannatha Hora
- Parashara's Light
- Swiss Ephemeris reference values

At least two trusted references should be used where practical. Any disagreement
between references must be recorded before accepting a result.

## Status Values

| Status | Meaning |
| --- | --- |
| `pending` | Framework exists, but no manual verification has been completed. |
| `in_review` | Manual comparison is underway. |
| `verified` | Result has been reviewed against trusted references and accepted. |
| `failed` | Result differs beyond tolerance and requires investigation. |

## Validation Checklist

| Calculation | Expected Accuracy | Tolerance | Reference Source | Verification Status | Verification Date | Reviewer | Result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Julian Day | Match known Julian Day UT values after explicit local-to-UTC conversion. | `0.001` day for current MVP known-value checks; tighter tolerance may be added after review. | Swiss Ephemeris reference values; Jagannatha Hora where applicable. | pending | TBD | TBD | TBD |
| Ayanamsa | Match selected ayanamsa mode value for the same Julian Day. | Within documented expected range now; exact degree tolerance TBD during manual review. | Swiss Ephemeris reference values; Jagannatha Hora. | pending | TBD | TBD | TBD |
| Planet Longitude | Sidereal longitudes match reference chart output. | MVP: `0.05` degrees; stable: `0.01` degrees. | Jagannatha Hora; Swiss Ephemeris reference values; Parashara's Light. | pending | TBD | TBD | TBD |
| Tithi | Tithi number, paksha, progress, and boundary match reference Panchang. | Boundary MVP: `5` minutes; stable: `2` minutes. | Drik Panchang; Jagannatha Hora; printed Panchang if available. | pending | TBD | TBD | TBD |
| Nakshatra | Nakshatra, pada, progress, and boundary match reference Panchang. | Boundary MVP: `5` minutes; stable: `2` minutes. | Drik Panchang; Jagannatha Hora; printed Panchang if available. | pending | TBD | TBD | TBD |
| Yoga | Panchang Yoga and boundary match reference Panchang. | Boundary MVP: `5` minutes; stable: `2` minutes. | Drik Panchang; Jagannatha Hora; printed Panchang if available. | pending | TBD | TBD | TBD |
| Karana | Karana and boundary match verified traditional sequence and reference Panchang. | Boundary MVP: `5` minutes; stable: `2` minutes. | Drik Panchang; Jagannatha Hora; printed Panchang if available. | pending | TBD | TBD | TBD |
| Vara | Weekday/vara assignment matches documented rule for the selected phase. | Exact civil weekday for MVP; future sunrise-based vara tolerance TBD. | Drik Panchang; printed Panchang if available. | pending | TBD | TBD | TBD |
| Sunrise | Local sunrise time matches reference for date and coordinates. | MVP: `2` minutes; stable: `1` minute. | Drik Panchang; Swiss Ephemeris reference values. | pending | TBD | TBD | TBD |
| Sunset | Local sunset time matches reference for date and coordinates. | MVP: `2` minutes; stable: `1` minute. | Drik Panchang; Swiss Ephemeris reference values. | pending | TBD | TBD | TBD |
| Moonrise | Local moonrise time matches reference for date and coordinates, including no-event cases. | MVP: `2` minutes; stable: `1` minute. | Drik Panchang; Swiss Ephemeris reference values. | pending | TBD | TBD | TBD |
| Moonset | Local moonset time matches reference for date and coordinates, including no-event cases. | MVP: `2` minutes; stable: `1` minute. | Drik Panchang; Swiss Ephemeris reference values. | pending | TBD | TBD | TBD |

## Test Policy

Validation tests live under `backend/tests/validation/`.

Until manual verification is complete:

- tests must call `pytest.skip()` with a clear reason;
- tests must not compare against unverified exact values;
- tests must not be treated as proof of calculation accuracy;
- fixture values may be used for structure checks only.

When a calculation is manually verified:

1. Record the reference sources used.
2. Record the verification date.
3. Record the reviewer.
4. Record the accepted tolerance.
5. Replace the skipped placeholder with an exact comparison test.
6. Update this document's status and result fields.
