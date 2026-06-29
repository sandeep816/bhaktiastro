# API

## POST /api/v1/panchang

Calculate the basic deterministic Panchang for one local date and time.

This endpoint does not include monthly Panchang, boundary end times, muhurat, or interpretation text.

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
