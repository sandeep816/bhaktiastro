# API

## POST /api/v1/kundali

Calculate the basic deterministic Kundali chart for one local birth date, time,
and location.

This endpoint includes Lagna, planet positions enriched with Rashi and
house-placement metadata, and placeholder house groupings. Divisional charts
are available only when explicitly requested. It does not include predictions,
interpretation text, or advanced house systems.

### Request

**URL:** `/api/v1/kundali`

**Method:** `POST`

**Content-Type:** `application/json`

Example:

```json
{
  "year": 1990,
  "month": 1,
  "day": 1,
  "hour": 12,
  "minute": 0,
  "second": 0,
  "timezone_offset": 5.5,
  "latitude": 26.9124,
  "longitude": 75.7873,
  "ayanamsa": "lahiri",
  "include_vargas": false
}
```

### Request Fields

| Field | Type | Required | Default | Validation |
| --- | --- | --- | --- | --- |
| `year` | integer | yes | - | `1900` to `2100` |
| `month` | integer | yes | - | `1` to `12` |
| `day` | integer | yes | - | `1` to `31` |
| `hour` | integer | no | `12` | `0` to `23` |
| `minute` | integer | no | `0` | `0` to `59` |
| `second` | integer | no | `0` | `0` to `59` |
| `timezone_offset` | number | no | `5.5` | `-12` to `14` |
| `latitude` | number | yes | - | `-90` to `90` |
| `longitude` | number | yes | - | `-180` to `180` |
| `ayanamsa` | string | no | `lahiri` | `lahiri` |
| `include_vargas` | boolean | no | `false` | `true` or `false` |

### Response

Successful responses return `200 OK`.

Response body:

```json
{
  "lagna": {},
  "planets": [],
  "houses": []
}
```

The Kundali API response keeps these top-level fields stable:

| Field | Type | Description |
| --- | --- | --- |
| `lagna` | object | Sidereal ascendant and Lagna Rashi metadata. |
| `planets` | array | Planet positions and optional foundation metadata. |
| `houses` | array | Twelve placeholder houses with grouped planets. |
| `vargas` | object | Optional Varga charts, present only when `include_vargas` is `true`. |

Optional planet metadata may include dignity, Mooltrikona, motion,
combustion, and Graha Drishti fields when the underlying chart data supports
them. The reusable JSON export helper can add export-only metadata, but the
public API response remains `lagna`, `planets`, and `houses` unless Vargas are
explicitly requested.

When `include_vargas` is omitted or `false`, the response omits `vargas` and
preserves the previous top-level response shape. When `include_vargas` is
`true`, `vargas` contains the supported charts `D2`, `D3`, `D7`, `D9`, `D10`,
`D12`, `D16`, `D20`, `D24`, `D27`, `D30`, `D40`, `D45`, and `D60`.

### Validation Errors

Invalid request fields return FastAPI/Pydantic validation errors with status
`422`.

Calculation errors raised by the deterministic calculation layer return:

- `400` for invalid calculation input, such as invalid date components
- `500` for runtime calculation failures, such as unavailable Swiss Ephemeris

## POST /api/v1/panchang

Calculate the basic deterministic Panchang for one local date and time.

This endpoint includes current Tithi, Nakshatra, Yoga, and Karana end times. It does not include Vara boundary end time, monthly Panchang, muhurat, or interpretation text.

### Request

**URL:** `/api/v1/panchang`

**Method:** `POST`

**Content-Type:** `application/json`

Example:

```json
{
  "date": "1985-04-20",
  "time": "18:10:00",
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

The current API schema validates `year`, `month`, `day`, `hour`, `minute`, `second`, `timezone_offset`, `latitude`, `longitude`, `language`, and `ayanamsa`. The `date` and `time` fields are included in the example for readability and match the split date/time fields.

### Request Fields

| Field | Type | Required | Default | Validation |
| --- | --- | --- | --- | --- |
| `year` | integer | yes | - | `1900` to `2100` |
| `month` | integer | yes | - | `1` to `12` |
| `day` | integer | yes | - | `1` to `31` |
| `hour` | integer | no | `12` | `0` to `23` |
| `minute` | integer | no | `0` | `0` to `59` |
| `second` | integer | no | `0` | `0` to `59` |
| `timezone_offset` | number | no | `5.5` | `-12` to `14` |
| `latitude` | number | yes | - | `-90` to `90` |
| `longitude` | number | yes | - | `-180` to `180` |
| `language` | string | no | `hi` | `hi` or `en` |
| `ayanamsa` | string | no | `lahiri` | `lahiri` |

### Response

Successful responses return `200 OK`.

Response body:

```json
{
  "julian_day": {},
  "ayanamsa": {},
  "sun": {},
  "moon": {},
  "tithi": {},
  "nakshatra": {},
  "yoga": {},
  "karana": {},
  "vara": {},
  "sunrise": {},
  "sunset": {},
  "moonrise": {},
  "moonset": {}
}
```

The `tithi`, `nakshatra`, `yoga`, and `karana` sections include consistent boundary timing fields:

| Field | Type | Description |
| --- | --- | --- |
| `degrees_remaining` | number | Degrees remaining until the current Panchang element ends. |
| `end_time_local` | string | Local ISO-8601 datetime when the current Panchang element ends. |
| `end_time_utc` | string | UTC ISO-8601 datetime with `Z` suffix when the current Panchang element ends. |

See `docs/examples/panchang_response_jodhpur.json` for a complete response generated from the current API route for Jodhpur, 20 Apr 1985, 18:10 IST.

### Validation Errors

Invalid request fields return FastAPI/Pydantic validation errors with status `422`.

Examples:

- `month` outside `1..12`
- `hour` outside `0..23`
- `timezone_offset` outside `-12..14`
- `latitude` outside `-90..90`
- `longitude` outside `-180..180`
- unsupported `language`
- unsupported `ayanamsa`

Calculation errors raised by the deterministic calculation layer return:

- `400` for invalid calculation input, such as invalid date components
- `500` for runtime calculation failures, such as unavailable Swiss Ephemeris
