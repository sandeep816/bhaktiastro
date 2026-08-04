# SPEC-HTTP-API-001 - BhaktiAstro Engine HTTP API Contract

| Metadata | Value |
| --- | --- |
| Status | approved |
| Specification version | 1.1 |
| Owning domain | Engine HTTP transport |
| Implementation status | Panchang v0 alignment implemented; server-proxy boundary selected; Playground integration not started |
| Route version | `v1`, expressed by the `/api/v1` path prefix |
| Governing ADRs | [ADR-001](../architecture/ADR-001-Project-Principles.md), [ADR-002](../architecture/ADR-002-Astrology-Calculation-Standards.md), [ADR-003](../architecture/ADR-003-Validation-Standards.md), [ADR-004](../architecture/ADR-004-Public-API-Contracts.md), [ADR-005](../architecture/ADR-005-Testing-Standards.md) |
| Related specification | [SPEC-API-STABILITY-001](API-STABILITY.md) |
| Consumer | BhaktiAstro Playground through the approved server-proxy boundary |
| Compatibility impact | Panchang now rejects unknown fields, forwards Lahiri, rejects non-finite output, and uses versioned technical errors; routes and successful response shape are unchanged |

## Purpose and authority

This is the permanent canonical contract for the Engine's HTTP boundary. It
records what the FastAPI application actually exposes, where schemas and
runtime forwarding disagree, and the minimum contract that must exist before
the Playground consumes real Engine data.

[SPEC-API-STABILITY-001](API-STABILITY.md) governs compatibility,
deprecation, identifiers, ordering, schemas, and error stability across public
surfaces. That specification deliberately did not design REST route
versioning; this specification adds the HTTP-specific route and consumer
boundary without changing any existing version. The
[source-of-truth and conflict process](../architecture/INDEX.md#source-of-truth-and-conflict-resolution)
applies. Runtime, schemas, generated OpenAPI, this specification, and the
concise [API guide](../API.md) must be reconciled through focused tasks when
they disagree.

This approval means the current state and required future decisions are
authoritatively documented. It does **not** approve the current API as
production-ready or authorize Playground integration beyond the readiness
gate below.

## Actual application contract

The application object is `backend.app.main:app`. It is a FastAPI application
whose title and application/deployment version come from `APP_NAME` and
`APP_VERSION`. The current defaults are `BhaktiAstro` and `0.1.0`.

| Surface | Current value |
| --- | --- |
| Versioned API prefix | `/api/v1` |
| OpenAPI JSON | `/openapi.json` |
| Swagger UI | `/docs` |
| Swagger OAuth redirect helper | `/docs/oauth2-redirect` |
| ReDoc | `/redoc` |
| Authentication | none |
| CORS middleware | none |

FastAPI also registers these framework-generated documentation surfaces:
`GET /openapi.json`, `GET /docs`, `GET /docs/oauth2-redirect`, and
`GET /redoc`. They expose no astrology calculation and have no Engine request
or response model. Only route decorators included by `backend/app/main.py`
establish Engine endpoints. The existence of Matchmaking, Reporting,
Interpretation, or Prediction modules does not expose those domains over HTTP.

### Endpoint inventory

| Method | Exact route | Request model | Response model | Calculation dependency | Playground status |
| --- | --- | --- | --- | --- | --- |
| `GET` | `/api/v1/health` | none | unversioned `dict[str, str]` | none | available for liveness inspection; not readiness |
| `POST` | `/api/v1/panchang` | `PanchangRequest` | `PanchangResponse` | `calculate_basic_panchang` | approved for the next fixed-offset Playground v0 server-proxy integration |
| `POST` | `/api/v1/kundali` | `KundaliRequest` | `KundaliResponse` | `assemble_kundali_chart` | implemented but excluded from Playground v0 |
| `POST` | `/api/v1/dasha` | `DashaRequest` | `DashaResponse` | Panchang plus `build_dasha_timeline` | implemented but excluded from Playground v0 |

There are no additional Engine endpoints. FastAPI's documentation and OpenAPI
routes are framework surfaces, not Engine calculation endpoints.

## Common transport and validation behavior

Requests are JSON and successful calculation responses are JSON with status
`200`. The three request models retain Pydantic's documented compatible scalar
coercions. Panchang now declares `extra="forbid"`; Kundali and Dasha retain
their earlier extra-ignore behavior:

- compatible input coercion is currently allowed, including ISO strings for
  Dasha dates/times and ordinary Pydantic numeric/boolean coercions;
- unknown Panchang properties produce the standard framework `422` validation
  failure, while unknown Kundali and Dasha properties are still ignored;
- declared bounds and literal values are validated before route execution; and
- calendar component ranges do not prove a real date. For example, a
  schema-valid impossible date can reach the calculation layer and become
  `400`.

These coercions are observed implementation behavior, not a new long-term
stability promise. ADR-003's stricter trust-boundary policy is not fully
implemented at this HTTP request boundary.

All nested response models inherit `extra="forbid"`. Route results are
validated into the declared response model before serialization. Fields
represented with Pydantic Core `MISSING` are omitted when the producing feature
is not requested. JSON object key order follows model declaration in current
serialization, but consumers must identify object fields by name. Array order
is calculation-defined where noted; no general sorting or canonical transport
ordering layer exists.

Panchang response models reject `NaN` and positive or negative infinity, and
the route verifies the validated tree with `json.dumps(..., allow_nan=False)`
before returning it. Invalid calculation output produces the stable Panchang
technical error contract rather than null/string repair. Kundali and Dasha do
not gain this HTTP-wide guarantee from the Panchang-only task.

No Panchang, Kundali, or Dasha response body contains a domain schema
identifier or schema-version field. OpenAPI component names such as
`PanchangRequest` and `PanchangResponse` describe runtime models; they are not
domain schema identifiers. Dasha metadata identifies `engine="dasha"` and
`system="vimshottari"` but has no schema version.

## Health

### `GET /api/v1/health`

The current `200` response is exactly:

```json
{
  "status": "ok",
  "app": "BhaktiAstro",
  "version": "0.1.0"
}
```

The `app` and `version` values are configuration-dependent. This route is:

- a basic process/application **liveness** signal;
- application/deployment version information;
- **not** readiness, because it probes no calculation path;
- **not** dependency health, because it does not check Swiss Ephemeris or any
  other dependency.

It has no explicit Pydantic response model, schema identifier, or separate
degraded state. A `200` therefore must not be interpreted as proof that
Panchang calculations can succeed.

## Panchang contract

### Request: `PanchangRequest`

| Field | JSON type | Required | Default | Validation | Forwarded |
| --- | --- | --- | --- | --- | --- |
| `year` | integer | yes | — | `1900..2100` | yes |
| `month` | integer | yes | — | `1..12` | yes |
| `day` | integer | yes | — | `1..31` | yes |
| `hour` | integer | no | `12` | `0..23` | yes |
| `minute` | integer | no | `0` | `0..59` | yes |
| `second` | integer | no | `0` | `0..59` | yes |
| `timezone_offset` | number | no | `5.5` | `-12..14` decimal UTC hours | yes |
| `latitude` | number | yes | — | `-90..90`, north positive | yes |
| `longitude` | number | yes | — | `-180..180`, east positive | yes |
| `language` | `"hi"` or `"en"` | no | `"hi"` | deprecated compatibility literal | not a calculation input |
| `ayanamsa` | `"lahiri"` | no | `"lahiri"` | only current literal | **yes**, as `ayanamsa_mode` |

`date` and `time` are not request fields. They and every other unknown property
now fail with framework `422`; they are not discarded.

The route forwards Lahiri through the Panchang assembly, initial positions, and
all Tithi, Nakshatra, Yoga, and Karana boundary calculations. The successful
response shape is unchanged.

`language` remains accepted for backward compatibility but is deprecated in
OpenAPI because calculation and response projection do not support it. The
replacement is to omit the field and select from the fixed multilingual
response fields in presentation code. Deprecation begins with application
version `0.1.0`; removal requires a separate breaking-change task after at
least two subsequent published releases and 90 days. With no qualifying
release cadence, removal is not eligible.

### Response: `PanchangResponse`

All top-level fields are required:

| Field | Nested family |
| --- | --- |
| `julian_day` | `utc_datetime`, `julian_day_ut` |
| `ayanamsa` | `value` |
| `sun`, `moon` | planet key, tropical/sidereal longitude, zero-based Rashi index, Hindi Rashi name, degree/DMS, speed, retrograde |
| `tithi` | number, English/Hindi/Sanskrit names, Paksha, angular progress, remaining degrees, local/UTC end time |
| `nakshatra` | zero-based index, names, Pada, ruling planet, degree boundaries/progress, local/UTC end time |
| `yoga` | index, names, degree boundaries/progress, local/UTC end time |
| `karana` | index, names, type, half-Tithi index, angular progress, local/UTC end time |
| `vara` | one-based index, names, ruling planet |
| `sunrise`, `sunset`, `moonrise`, `moonset` | event, nullable local time, nullable UTC datetime, numeric offset |

Rise/set `local_time` and `utc_datetime` can both be `null` when an event is
not found. Other Panchang sections are required and non-null. The response
always exposes its currently implemented multilingual name fields; it does not
select or filter them according to `language`.

The route returns `200`, framework `422`, stable application `400`, or stable
application `500` as described in the error contract. Its documented
structural fixture is a current Engine snapshot, not an independently verified
Golden reference.

**Suitability:** this is the approved smallest Playground result through the
selected server-side proxy boundary, subject to the fixed-offset and
non-Golden limitations below.

## Kundali contract

### Request: `KundaliRequest`

The date/time, numeric offset, latitude, longitude, and `ayanamsa` fields have
the same types, requiredness, defaults, bounds, and scalar coercion behavior as
Panchang, except there is no `language`. Kundali still ignores unknown fields;
the Panchang-only strict-extra change does not apply to it.

| Additional field | JSON type | Required | Default | Forwarded result |
| --- | --- | --- | --- | --- |
| `include_vargas` | boolean | no | `false` | `include_vargas` |
| `include_strength` | boolean | no | `false` | `include_strength` |
| `include_ashtakavarga` | boolean | no | `false` | `include_ashtakavarga` |
| `include_special_lagnas` | boolean | no | `false` | `include_special_lagna` |
| `include_predictions` | boolean | no | `false` | `include_prediction_framework` |

Unlike Panchang and Dasha, Kundali forwards `ayanamsa` as `ayanamsa_mode`.
Only `"lahiri"` is accepted by the current request schema.

### Response: `KundaliResponse`

Required top-level fields are:

- `lagna`: tropical and sidereal ascendant longitudes, Ayanamsha value, Rashi
  metadata and index/degree;
- `planets`: ordered calculator output with position, Rashi and house
  placement plus nullable dignity, Mooltrikona, motion, combustion, and aspect
  metadata; and
- `houses`: the 12 current placeholder house groupings and their planet lists.

The following keys are omitted unless requested:

- `vargas`: keyed Varga chart objects. Current implemented codes are `D2`,
  `D3`, `D7`, `D9`, `D10`, `D12`, `D16`, `D20`, `D24`, `D27`, `D30`, `D40`,
  `D45`, and `D60`;
- `strength`, `ashtakavarga`, and `special_lagna`: open nested dictionaries
  (`dict[str, Any]`) at this HTTP schema boundary; and
- `predictions`: the route extracts the nested `predictions` object from the
  internal prediction-framework output.

The optional open dictionaries are not strict, independently versioned HTTP
result schemas. Houses are explicitly a foundation/placeholder representation.
The route has the common `200`/`422`/`400`/`500` behavior.

**Suitability:** implemented and test-covered as an Engine route, but not
approved for Playground v0 because its broad optional/open sections, accuracy
status, and transport prerequisites need focused consumer contracts.

## Dasha contract

### Request: `DashaRequest`

| Field | JSON type | Required | Default | Validation/current interpretation |
| --- | --- | --- | --- | --- |
| `date` | ISO date string | yes | — | local birth calendar date |
| `time` | ISO time string | no | `"12:00:00"` | local birth time |
| `timezone_offset` | number | no | `5.5` | `-12..14` fixed UTC hours |
| `latitude` | number | yes | — | `-90..90` |
| `longitude` | number | yes | — | `-180..180` |
| `ayanamsa` | `"lahiri"` | no | `"lahiri"` | accepted but **not forwarded** |
| `target_date` | ISO date string or `null` | no | `null` | optional local lookup date |
| `target_datetime` | ISO datetime string or `null` | no | `null` | takes precedence over `target_date` |
| `include_antardasha` | boolean | no | `true` | controls nested Antardasha arrays |
| `include_pratyantardasha` | boolean | no | `false` | effective only through included Antardashas |

Birth date and time are combined with a fixed-offset timezone. A naive
`target_datetime` receives the request offset; an aware target retains its own
supplied offset. A `target_date` is combined with the birth `time` and request
offset. Microseconds are removed.

The route calls Panchang to derive the zero-based birth Nakshatra index and
Moon sidereal longitude, then builds a Vimshottari timeline. Latitude and
longitude are therefore forwarded to the Panchang dependency. The Dasha
request's `ayanamsa` is not forwarded to that dependency.

### Response: `DashaResponse`

Required top-level fields are:

- `birth_datetime`: ISO datetime string with the fixed request offset;
- `target_datetime`: ISO datetime string or `null`;
- `mahadasha_timeline`: ordered Mahadasha periods;
- `current_dasha`: lookup object or `null`; and
- `metadata`: exactly `engine="dasha"` and `system="vimshottari"`.

Each period includes start/end datetime strings and `duration_years`.
Mahadashas also include `dasha_lord` and `is_birth_dasha`; their
`antardashas` key is omitted when not included. Antardashas identify both
lords; their `pratyantardashas` key is omitted when not included.
`current_dasha` contains the target and nullable active Maha/Antar/Pratyantar
periods. Timeline order is chronological calculation output.

The route has the common `200`/`422`/`400`/`500` behavior.

**Suitability:** implemented, but excluded from Playground v0 because its
timezone and ignored-Ayanamsha limitations compound Panchang dependency risk.

## Error contract

### Current implemented behavior

| Condition | Status | Current body |
| --- | --- | --- |
| Pydantic/FastAPI request validation | `422` | framework-generated `{"detail": [validation issue objects...]}` |
| Panchang calculation `TypeError` or `ValueError` | `400` | stable `TechnicalErrorResponse` with `error="panchang_input_invalid"` |
| Panchang calculation `RuntimeError` | `500` | stable envelope with `error="panchang_calculation_failed"` |
| invalid/non-finite Panchang calculation output | `500` | stable envelope with `error="panchang_response_invalid"` and safe field details |
| unexpected Panchang route failure | `500` | stable envelope with `error="internal_server_error"` |
| Kundali/Dasha caught calculation failures | `400` / `500` | legacy `{"detail": "<exception text>"}` |
| missing route / unsupported method | `404` / `405` | framework default detail response |
| other unhandled failure | normally `500` | framework/server behavior |

The Panchang application envelope is:

```json
{
  "schema_version": "1.0",
  "error": "panchang_input_invalid",
  "message": "Panchang calculation input was invalid.",
  "details": []
}
```

`schema_version`, `error`, `message`, and `details` are exact root fields.
Details are ordered objects containing `code` and a string/integer `path`.
Current detail codes are `invalid_response_value` and `non_finite_number`.
Messages are safe fixed text; exception text, request values, stack traces, and
environment paths are not emitted. Framework `422` remains deliberately
unwrapped.

Health has no domain error behavior. This envelope is currently guaranteed for
Panchang application failures only; there is no uniform Engine-wide envelope,
correlation identifier, or stable Kundali/Dasha error code.

Production concerns such as correlation IDs, observability linkage,
rate-limit errors, authentication errors, and a wider domain-code catalogue
remain deferred.

## Time and timezone contract

Panchang and Kundali accept split local calendar/time components plus a numeric
UTC offset in decimal hours. Dasha accepts ISO local date/time values plus that
same style of offset. The Julian Day path subtracts the numeric offset to
derive UTC. Rise/set output applies the supplied numeric offset. Dasha creates
fixed-offset timezone-aware datetimes.

The current HTTP API:

- does not accept IANA identifiers such as `Europe/London` or
  `America/New_York`;
- does not resolve historical or future daylight-saving rules;
- does not detect or disambiguate repeated local times during a fall-back;
- does not reject nonexistent local times during a spring-forward; and
- relies on the caller to supply the correct offset for the intended place and
  instant.

Therefore London and New York are not safely representable from civil time and
location alone. A caller may externally determine and send an offset for an
unambiguous instant, but the API cannot prove that it is historically correct
or preserve the zone identity. Future international support requires an
explicit IANA-zone contract and policy for ambiguous/nonexistent times; it
must not silently infer a zone from coordinates.

Playground v0 must be explicitly fixed-offset only. Its initial supported
configuration should be Lahiri with `+05:30` (`timezone_offset: 5.5`) and must
not describe that limitation as general timezone support.

## Ayanamsha

Repository configuration defaults to Lahiri. The public field is currently
spelled `ayanamsa`; this specification uses “Ayanamsha” in prose but preserves
the existing field identifier.

| Endpoint | Accepts field | Runtime applies request value |
| --- | --- | --- |
| Panchang | yes, only `"lahiri"` | yes; forwarded through all Panchang sidereal and boundary paths |
| Kundali | yes, only `"lahiri"` | yes, forwarded as `ayanamsa_mode` |
| Dasha | yes, only `"lahiri"` | no; dependent Panchang calculation uses its default |

Panchang's former accepted-but-unused mismatch is resolved without widening the
HTTP literal. Dasha still accepts but does not forward its own field; no Dasha
behavior changed in this task.

## Language and localization

Only Panchang accepts `language`, with `"hi"` default and `"hi"`/`"en"`
allowed. The field is retained but OpenAPI-deprecated under the compatibility
plan above because the calculation has no language parameter. Responses expose
fixed multilingual name fields, generally `name_en`, `name_hi`, and `name_sa`,
while the planet summary exposes `rashi_name_hi`. No locale negotiation,
translated error contract, or language-specific response projection exists.

The Playground must select among explicitly returned fields and provide its
own presentation labels. It must not assume that sending `language` changes
the payload or translate missing Engine domain values.

## CORS and browser access

No `CORSMiddleware` or equivalent policy exists. Direct server-to-server calls
are not subject to browser CORS enforcement. A browser Playground served from
a different origin cannot rely on direct calls succeeding; local development
on separate ports is also cross-origin.

The approved first-integration boundary is **server proxy**: the Playground
must call the Engine from a Next.js server-side route and expose only its own
same-origin consumer endpoint to the browser. Direct browser-to-Engine access
remains unsupported. No CORS middleware, wildcard origin, credential policy,
or Engine CORS environment variable is added. A future direct-browser design
would require a separate approved allowlist task.

## API base URL policy

Consumers target the versioned base path `/api/v1`. The origin must come from
deployment environment configuration and must never be hardcoded to a
production hostname in Playground source. No such consumer environment
variable is added by this documentation task.

- local development expects an explicitly configured server-only Engine origin
  used by the Playground server proxy;
- production expects HTTPS, an environment-specific origin, and the same
  chosen server-side/browser boundary;
- browser-visible configuration is appropriate only for a deliberately public
  direct-browser API; secrets must never be placed in a public environment
  variable; and
- joining the configured origin with `/api/v1` must avoid duplicating or
  stripping the version segment.

## Playground integration readiness

| Capability | Classification | Reason |
| --- | --- | --- |
| Health | available | liveness/version response exists; not readiness |
| Panchang | available for fixed-offset v0 server integration | strict request, Lahiri forwarding, finite response, and stable technical errors are implemented |
| Kundali | partially available | route exists; broad optional/open sections and v0 exclusions remain |
| Dasha | partially available | route exists; ignored Ayanamsha and fixed-offset dependency remain |
| Matchmaking | unavailable | no HTTP route |
| Reporting | unavailable | no HTTP route |
| Interpretation | unavailable | no HTTP route |
| Prediction | partially available internally, unavailable as standalone HTTP | only optional Kundali projection exists; no dedicated route or populated public rule contract |
| IANA timezone/DST | unavailable | numeric fixed offsets only |
| Stable Panchang error contract | available | version `1.0`; framework `422` remains separate |
| Engine-wide stable errors | unavailable | Kundali and Dasha retain legacy errors |
| Browser CORS | intentionally unsupported | selected Playground boundary is a Next.js server proxy |
| Authentication | deferred | no authentication implemented or required for v0 documentation |
| Route version guarantee | available | existing calculation routes use `/api/v1`; evolution governed here and by API Stability |
| Body schema version guarantee | unavailable | calculation bodies contain no schema ID/version |
| Calculation readiness health | unavailable | liveness does not probe dependencies |

“Partially available” does not mean approved for Playground use.

## Minimum Playground v0 integration

The smallest safe first real-data slice is:

1. `GET /api/v1/health` for liveness display only; and
2. `POST /api/v1/panchang` for one fixed-offset Lahiri Panchang result.

The Engine alignment gate for this slice is complete. The Panchang request uses
`year`, `month`, `day`, `hour`, `minute`, `second`, `timezone_offset`,
`latitude`, `longitude`, and effective `ayanamsa="lahiri"`. Playground should
omit the deprecated `language` field and select returned multilingual labels.

The consumed response is limited to the required Panchang top-level fields
listed above. The UI must tolerate `null` rise/set times, treat health as
liveness only, and surface API failure rather than manufacture a successful
result.

The next Playground integration must:

- configure a server-only Engine origin outside source and use `/api/v1`;
- implement a Next.js same-origin server proxy, not direct browser calls;
- handle framework `422` separately from technical error schema `1.0`;
- state fixed-offset-only behavior, initially `5.5`/India, with no London,
  New York, IANA-zone, or DST claim; and
- label structural snapshots as non-Golden until governed independent
  accuracy evidence exists.

Explicit v0 exclusions are Kundali, Dasha, Matchmaking, Reporting,
Interpretation, Prediction, authentication, user accounts, persisted birth
data, client-side astrology calculations, and fake successful fallback data.

## Gap register

| ID | Severity | Affected surface | Current behavior | Required decision | Playground impact | Blocking |
| --- | --- | --- | --- | --- | --- | --- |
| `HTTP-GAP-001` | high | Panchang docs/request | split fields retained; `date`/`time` now rejected | resolved by strict request and corrected example | no silent discard | resolved |
| `HTTP-GAP-002` | high | POST requests | Panchang rejects extras; Kundali/Dasha still ignore | align other routes only in their own tasks | no Panchang impact | resolved for v0 |
| `HTTP-GAP-003` | high | Panchang | field retained and OpenAPI-deprecated; fixed multilingual output remains | follow deprecation window; consumer omits field | no silent localization claim | resolved for v0 |
| `HTTP-GAP-004` | high | Panchang, Dasha | Panchang forwards Lahiri; Dasha remains unchanged | align Dasha in a separate task | no Panchang impact | resolved for v0 |
| `HTTP-GAP-005` | critical | browser boundary | no CORS by design; server proxy selected | Playground implements proxy | direct browser remains unsupported | resolved for v0 |
| `HTTP-GAP-006` | high | application errors | Panchang has schema `1.0`; Kundali/Dasha remain legacy | expand only in domain tasks | reliable Panchang handling available | resolved for v0 |
| `HTTP-GAP-007` | high | all calculations | numeric offsets only; no IANA/DST resolution | define future zone/disambiguation policy | London/New York unsafe | yes for international support |
| `HTTP-GAP-008` | medium | health | liveness only | add separate readiness/dependency contract if needed | health may be green while calculations fail | no for local v0 if represented honestly |
| `HTTP-GAP-009` | medium | response bodies | no schema ID/version | decide body-version strategy under API Stability | compatibility detection is limited | no for narrow v0 |
| `HTTP-GAP-010` | medium | float responses | Panchang rejects and tests non-finite output; other routes unchanged | expand only in domain tasks | safe Panchang JSON | resolved for v0 |
| `HTTP-GAP-011` | medium | Kundali optional sections | several nested sections are `dict[str, Any]` | define strict versioned models before consumer approval | unstable broad payload | yes for Kundali |
| `HTTP-GAP-012` | high | Matchmaking/Reporting/Interpretation | implemented Python domains have no HTTP routes | design only through future authorized tasks | unavailable to Playground | yes for those capabilities |
| `HTTP-GAP-013` | medium | API guide | Dasha and health were omitted; Panchang example drifted | keep guide synchronized with this canonical spec | discovery and usage errors | resolved by this documentation task |
| `HTTP-GAP-014` | medium | readiness/accuracy | route fixtures are structural/regression evidence, not Golden references | complete governed independent evidence before accuracy claims | UI must avoid verified-accuracy claims | yes for such claims |
| `HTTP-GAP-015` | low | localization | mixed fixed multilingual fields; language has no projection contract | define transport versus presentation localization ownership | client cannot rely on locale-shaped data | no for fixed-field v0 |

## Next safe integration sequence

The next task is the Playground's narrow server-side integration of health
liveness and fixed-offset Panchang. It must configure the Engine origin on the
server, proxy only the approved routes, distinguish framework `422` from the
technical envelope, and surface failure without mock fallback. No further
Engine runtime change is required for that narrow slice.

IANA timezone support, readiness probes, body schema-version fields, direct
browser CORS, and other domain endpoints remain separate future decisions.

## Mock-data policy

- Playground must never fabricate astrology results.
- Structural mock data must be visibly labelled as structural/mock.
- Existing Engine snapshots and regression fixtures are not Golden references.
- API errors must remain errors; the consumer must not silently substitute a
  fake successful payload.
- Astrology calculations must not be duplicated client-side.

## Security and privacy

Birth date/time and coordinates are sensitive personal data even though the
current API has no authentication or persistence layer. Current routes accept
JSON bodies and do not intentionally store them. Future integrations must:

- send birth data and coordinates in request bodies, never query strings;
- use HTTPS outside local development;
- avoid logging full payloads, exact coordinates, or derived astrology output
  by default; use redaction and retention limits;
- avoid browser persistence unless a separately approved product requirement
  defines consent, purpose, retention, deletion, and access boundaries;
- keep analytics free of exact birth data, coordinates, and response payloads;
- avoid embedding payloads in URLs, referrers, crash reports, or telemetry;
- treat any future authentication as a separate authorization and data-
  ownership boundary, not as proof that sensitive logging is safe; and
- never expose server secrets through browser configuration.

No authentication, API key, rate limiting, database, caching, or storage
policy is introduced here.

## Versioning and compatibility

Four versions remain distinct:

| Version | Current HTTP meaning |
| --- | --- |
| Route version | `v1` in `/api/v1`; changes require explicit compatibility review |
| Schema version | absent from current calculation bodies; OpenAPI model names are not a substitute |
| Package/application version | `APP_VERSION`, currently defaulting to `0.1.0`, exposed by FastAPI and health |
| Artifact/domain version | owned by domain artifacts where defined; not emitted by these calculation routes |

An application release does not automatically change route, schema, or domain
artifact versions. Additive versus breaking decisions, deprecation, vocabulary
stability, and migration follow
[SPEC-API-STABILITY-001](API-STABILITY.md). This document does not silently
upgrade or promise semantic versioning for existing bodies.

## Documentation ownership

- this file is the permanent canonical HTTP contract and gap register;
- [docs/API.md](../API.md) is the concise user/developer route guide;
- `/openapi.json` is the generated description of the running application;
- Pydantic schemas and route functions are the implementation;
- domain specifications own calculation/domain meaning; and
- a discrepancy requires a focused resolution task, tests, and updates to all
  affected sources. Generated OpenAPI alone cannot legitimize an unintended
  runtime field.

## Required future contract tests

Future runtime tasks must cover:

- exact route presence, methods, `/api/v1` prefix, and absence of accidental
  domain routes;
- request requiredness, defaults, bounds, declared coercion, and unknown-field
  rejection;
- exact field forwarding, including language/Ayanamsha decisions and Kundali
  option-name mappings;
- response required/optional/null behavior and strict nested schemas;
- stable error status, envelope, codes, and safe message behavior;
- configured CORS preflight and allowed/disallowed origins, if direct-browser;
- health liveness and any separately introduced readiness behavior;
- generated OpenAPI paths, components, request/response schemas, and version;
- local-to-UTC fixed-offset conversion, Dasha target precedence, and future
  IANA/DST ambiguity/nonexistence policy when implemented;
- finite-number validation and JSON serialization;
- response ordering where specifically promised; and
- backward compatibility under SPEC-API-STABILITY-001.

## Explicit exclusions

Version 1.1 changes only the existing Panchang transport alignment and
Ayanamsha parameter propagation; it changes no astrology formula. It adds no
endpoint, CORS middleware, authentication, rate limiting, API key, environment
variable, database, cache, fake API data, Playground code, or public package
export.

## Playground handoff

| Consumer question | Answer |
| --- | --- |
| Base path | configured Engine origin plus `/api/v1`; never hardcode production origin |
| Safe now | health liveness and fixed-offset Panchang through a server proxy |
| First result | Panchang with effective `ayanamsa="lahiri"` and deprecated language omitted |
| Blocked/excluded | Kundali, Dasha, Matchmaking, Reporting, Interpretation, Prediction |
| Request/response source | this specification, then generated OpenAPI/runtime schemas; escalate discrepancies |
| Environment expectation | consumer-owned, deployment-specific Engine origin; no variable is created here |
| Browser boundary | direct Engine access unsupported; Next.js server proxy required |
| Error contract | framework `422`; Panchang technical schema `1.0` for application failures |
| Time limitation | numeric fixed offset only; initial v0 should be `5.5`, no IANA/DST claim |
| Next task | Playground health/Panchang server-proxy integration |

## Validation basis

Version 1.1 was implemented by reviewing application inclusion and route
decorators, request/response schemas, route-to-calculation forwarding,
Panchang/Kundali/Dasha calculation entry points, existing API/schema tests,
generated-OpenAPI configuration source, current API documentation,
SPEC-API-STABILITY-001, Playground prerequisites, and cross-document links.
Focused and full regression evidence is recorded in the implementation commit.

## Change history

| Version | Change |
| --- | --- |
| 1.1 | Implemented the Panchang v0 alignment: strict extras, effective Lahiri forwarding, language deprecation, technical error schema `1.0`, finite JSON enforcement, and server-proxy boundary. |
| 1.0 | Initial authoritative audit of the existing Engine HTTP API and minimum conditional Playground v0 contract. |
