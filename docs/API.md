# Engine HTTP API

This is the concise route guide for the current FastAPI application. The
authoritative contract, exact nested schemas, known gaps, and Playground
handoff are in
[SPEC-HTTP-API-001](specifications/HTTP-API.md).

Application entry point: `backend.app.main:app`

| Surface | Path |
| --- | --- |
| API base path | `/api/v1` |
| OpenAPI | `/openapi.json` |
| Swagger UI | `/docs` |
| Swagger OAuth redirect helper | `/docs/oauth2-redirect` |
| ReDoc | `/redoc` |

The current API has no authentication and no CORS middleware. The approved
Playground boundary is a Next.js server-side proxy; direct browser-to-Engine
calls are unsupported. The API accepts numeric UTC offsets, not IANA timezone
identifiers or DST rules.

## Routes

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/health` | process liveness and application version |
| `POST` | `/api/v1/panchang` | basic deterministic Panchang |
| `POST` | `/api/v1/kundali` | basic Kundali with opt-in sections |
| `POST` | `/api/v1/dasha` | Vimshottari Dasha timeline |

No Matchmaking, Reporting, Interpretation, or standalone Prediction HTTP route
currently exists.

## Health

`GET /api/v1/health` returns:

```json
{
  "status": "ok",
  "app": "BhaktiAstro",
  "version": "0.1.0"
}
```

The configured `app` and `version` values may differ. This is liveness and
version information only, not calculation readiness or dependency health.

## Panchang

`POST /api/v1/panchang`

```json
{
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
  "ayanamsa": "lahiri"
}
```

| Field | Required | Default | Bounds/values |
| --- | --- | --- | --- |
| `year` | yes | — | integer `1900..2100` |
| `month` | yes | — | integer `1..12` |
| `day` | yes | — | integer `1..31` |
| `hour` | no | `12` | integer `0..23` |
| `minute`, `second` | no | `0` | integer `0..59` |
| `timezone_offset` | no | `5.5` | number `-12..14` |
| `latitude` | yes | — | number `-90..90` |
| `longitude` | yes | — | number `-180..180` |
| `language` | no | `"hi"` | `"hi"` or `"en"` |
| `ayanamsa` | no | `"lahiri"` | `"lahiri"` |

`date`, `time`, and every other unknown field produce framework `422`.
`ayanamsa="lahiri"` is forwarded through the main and boundary calculations.
`language` remains accepted for compatibility but is OpenAPI-deprecated because
the response always returns fixed multilingual fields; consumers should omit
it and select presentation labels from the response.

A successful response has these required top-level fields:

```text
julian_day, ayanamsa, sun, moon, tithi, nakshatra, yoga,
karana, vara, sunrise, sunset, moonrise, moonset
```

Rise/set local and UTC values may be `null` when an event is not found. The
Jodhpur files under `docs/examples/` are current Engine snapshots, not
independently verified Golden references. All response floats must be finite;
invalid calculation output is rejected rather than converted.

## Kundali

`POST /api/v1/kundali`

Kundali uses Panchang's split date/time components, numeric offset, coordinates,
and Lahiri-only `ayanamsa`, but has no `language`. It adds these optional
boolean flags, all defaulting to `false`:

```text
include_vargas
include_strength
include_ashtakavarga
include_special_lagnas
include_predictions
```

The route forwards `ayanamsa` and all five flags. Required response keys are
`lagna`, `planets`, and `houses`. Requested sections are emitted as `vargas`,
`strength`, `ashtakavarga`, `special_lagna`, and `predictions`. Several of
these optional sections remain open dictionaries at the HTTP schema boundary;
see the canonical specification before adopting them.

## Dasha

`POST /api/v1/dasha`

```json
{
  "date": "1990-01-01",
  "time": "12:00:00",
  "timezone_offset": 5.5,
  "latitude": 26.9124,
  "longitude": 75.7873,
  "ayanamsa": "lahiri",
  "target_datetime": "2026-07-03T12:00:00",
  "include_antardasha": true,
  "include_pratyantardasha": false
}
```

`date`, `latitude`, and `longitude` are required. `time` defaults to noon,
`timezone_offset` to `5.5`, `ayanamsa` to `"lahiri"`,
`include_antardasha` to `true`, and `include_pratyantardasha` to `false`.
`target_date` and `target_datetime` are nullable; `target_datetime` takes
precedence when both are supplied.

The Dasha `ayanamsa` field is accepted but not forwarded to its Panchang
dependency. A successful response contains `birth_datetime`,
`target_datetime`, `mahadasha_timeline`, `current_dasha`, and `metadata`.

## Validation and errors

| Status | Current meaning |
| --- | --- |
| `200` | successful response |
| `422` | framework-generated request validation errors |
| `400` | caught calculation `TypeError` or `ValueError` |
| `500` | caught calculation `RuntimeError` or other server failure |

Panchang application failures use this exact versioned root envelope:

```json
{
  "schema_version": "1.0",
  "error": "panchang_input_invalid",
  "message": "Panchang calculation input was invalid.",
  "details": []
}
```

Panchang error identifiers are `panchang_input_invalid`,
`panchang_calculation_failed`, `panchang_response_invalid`, and
`internal_server_error`. Details contain only stable `code` and `path` fields;
internal exception text and request values are not returned. Framework `422`
keeps its standard `detail` list. Kundali and Dasha retain their legacy
calculation error bodies until separate tasks.

## Playground use

Health is safe only as a liveness check. Fixed-offset Lahiri Panchang is
approved as the first real-data candidate through a Next.js server-side proxy;
direct browser calls remain unsupported. Kundali and Dasha are not approved
for Playground v0. See the
[readiness matrix and handoff](specifications/HTTP-API.md#playground-integration-readiness).
