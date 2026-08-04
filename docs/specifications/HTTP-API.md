# SPEC-HTTP-API-001 - BhaktiAstro Engine HTTP API Contract

| Metadata | Value |
| --- | --- |
| Status | approved |
| Specification version | 1.0 |
| Owning domain | Engine HTTP transport |
| Implementation status | current routes documented; Playground prerequisites and runtime gaps remain |
| Route version | `v1`, expressed by the `/api/v1` path prefix |
| Governing ADRs | [ADR-001](../architecture/ADR-001-Project-Principles.md), [ADR-002](../architecture/ADR-002-Astrology-Calculation-Standards.md), [ADR-003](../architecture/ADR-003-Validation-Standards.md), [ADR-004](../architecture/ADR-004-Public-API-Contracts.md), [ADR-005](../architecture/ADR-005-Testing-Standards.md) |
| Related specification | [SPEC-API-STABILITY-001](API-STABILITY.md) |
| Consumer | BhaktiAstro Playground, after the blocking prerequisites in this specification |
| Compatibility impact | documentation-only audit; no runtime or consumer behavior changed |

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
| `POST` | `/api/v1/panchang` | `PanchangRequest` | `PanchangResponse` | `calculate_basic_panchang` | partially available; blocked for approved browser integration |
| `POST` | `/api/v1/kundali` | `KundaliRequest` | `KundaliResponse` | `assemble_kundali_chart` | implemented but excluded from Playground v0 |
| `POST` | `/api/v1/dasha` | `DashaRequest` | `DashaResponse` | Panchang plus `build_dasha_timeline` | implemented but excluded from Playground v0 |

There are no additional Engine endpoints. FastAPI's documentation and OpenAPI
routes are framework surfaces, not Engine calculation endpoints.

## Common transport and validation behavior

Requests are JSON and successful calculation responses are JSON with status
`200`. The three request models use Pydantic's non-strict defaults:

- compatible input coercion is currently allowed, including ISO strings for
  Dasha dates/times and ordinary Pydantic numeric/boolean coercions;
- no request model declares `extra="forbid"`, so unknown request properties are
  currently ignored rather than rejected;
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

The response schemas use ordinary `float` fields and do not declare
finite-number constraints. Underlying calculators validate many inputs and are
expected to emit finite values, but the HTTP schema itself provides no complete
finite-number guarantee and there is no dedicated finite-JSON contract test.

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
| `language` | `"hi"` or `"en"` | no | `"hi"` | literal | **no** |
| `ayanamsa` | `"lahiri"` | no | `"lahiri"` | only current literal | **no** |

`date` and `time` are not request fields. Because extras are ignored, old
examples containing them may appear to work while those properties are
discarded.

The ignored `ayanamsa` currently happens to agree with the calculation layer's
configured/default Lahiri path. That coincidence must not be treated as
effective forwarding. The ignored `language` has no effect.

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

The route returns `200`, framework `422`, mapped `400`, or mapped `500` as
described in the error contract. Its documented structural fixture is a
current Engine snapshot, not an independently verified Golden reference.

**Suitability:** this is the smallest useful Playground result, but real-data
integration remains blocked until the minimum gate in this specification is
implemented.

## Kundali contract

### Request: `KundaliRequest`

The date/time, numeric offset, latitude, longitude, and `ayanamsa` fields have
the same types, requiredness, defaults, bounds, and current coercive/extra-ignore
behavior as Panchang, except there is no `language`.

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
| calculation `TypeError` or `ValueError` caught by a route | `400` | `{"detail": "<exception text>"}` |
| calculation `RuntimeError` caught by a route | `500` | `{"detail": "<exception text>"}` |
| missing route / unsupported method | `404` / `405` | framework default detail response |
| unhandled exception or response-validation failure | normally `500` | framework/server behavior; no Engine envelope |

Health has no domain error behavior. There are no stable machine-readable
Engine error codes, correlation identifiers, documented issue ordering, or one
uniform envelope. Exception text can expose implementation details and is not
a compatibility-safe discriminator. Only the broad route mappings above are
implemented; the exact framework validation issue shape is dependency-version
behavior, not an approved BhaktiAstro error schema.

### Minimum required future contract

Before Playground real-data integration, a focused runtime task must define
and test an Engine-owned JSON error model with a stable code, safe message, and
field issues where relevant; map validation and calculation failures
consistently; and prevent the consumer from depending on raw exception text.
The first Panchang integration may support a deliberately small error-code
vocabulary, but it must distinguish invalid input, calculation/dependency
failure, and unexpected server failure.

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
| Panchang | yes, only `"lahiri"` | no; calculation uses its configured/default path |
| Kundali | yes, only `"lahiri"` | yes, forwarded as `ayanamsa_mode` |
| Dasha | yes, only `"lahiri"` | no; dependent Panchang calculation uses its default |

Because only Lahiri is schema-valid today, ignored fields normally yield the
same current mode. This is still a forwarding defect: future literal expansion
or a changed default would make identical-looking requests produce
incompatible results.

## Language and localization

Only Panchang accepts `language`, with `"hi"` default and `"hi"`/`"en"`
allowed. The route does not forward it and the calculation has no language
parameter. Responses expose the schema's fixed multilingual name fields,
generally `name_en`, `name_hi`, and `name_sa`, while the planet summary exposes
`rashi_name_hi`. No locale negotiation, translated error contract, or
language-specific response projection exists.

The Playground must select among explicitly returned fields and provide its
own presentation labels. It must not assume that sending `language` changes
the payload or translate missing Engine domain values.

## CORS and browser access

No `CORSMiddleware` or equivalent policy exists. Direct server-to-server calls
are not subject to browser CORS enforcement. A browser Playground served from
a different origin cannot rely on direct calls succeeding; local development
on separate ports is also cross-origin.

Before a direct-browser integration, the Engine needs an explicit,
environment-specific allowlist of Playground origins, methods, and headers.
Production must not use an unrestricted credentialed policy. Alternatively,
the Playground can make server-side calls through its own same-origin backend;
that architecture avoids browser-to-Engine CORS but does not remove the need
to define the trusted server boundary. This task does not choose or implement
either deployment architecture.

## API base URL policy

Consumers target the versioned base path `/api/v1`. The origin must come from
deployment environment configuration and must never be hardcoded to a
production hostname in Playground source. No such consumer environment
variable is added by this documentation task.

- local development expects an explicitly configured Engine origin and either
  an Engine CORS allowlist or a Playground server-side proxy;
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
| Panchang | partially available | route and strict response model exist; forwarding, errors, CORS, timezone and accuracy caveats remain |
| Kundali | partially available | route exists; broad optional/open sections and v0 exclusions remain |
| Dasha | partially available | route exists; ignored Ayanamsha and fixed-offset dependency remain |
| Matchmaking | unavailable | no HTTP route |
| Reporting | unavailable | no HTTP route |
| Interpretation | unavailable | no HTTP route |
| Prediction | partially available internally, unavailable as standalone HTTP | only optional Kundali projection exists; no dedicated route or populated public rule contract |
| IANA timezone/DST | unavailable | numeric fixed offsets only |
| Stable error contract | unavailable | framework details and exception strings only |
| Browser CORS | blocked | no middleware/policy |
| Authentication | deferred | no authentication implemented or required for v0 documentation |
| Route version guarantee | available | existing calculation routes use `/api/v1`; evolution governed here and by API Stability |
| Body schema version guarantee | unavailable | calculation bodies contain no schema ID/version |
| Calculation readiness health | unavailable | liveness does not probe dependencies |

“Partially available” does not mean approved for Playground use.

## Minimum Playground v0 integration

The smallest safe first real-data slice is:

1. `GET /api/v1/health` for liveness display only; and
2. `POST /api/v1/panchang` for one fixed-offset Lahiri Panchang result.

Approval to begin that slice is conditional on completing the blocking runtime
alignment task below. The Panchang request must use only `year`, `month`,
`day`, `hour`, `minute`, `second`, `timezone_offset`, `latitude`, and
`longitude`. Until forwarding is fixed, the consumer must not use
`language` or treat `ayanamsa` as effective input.

The consumed response is limited to the required Panchang top-level fields
listed above. The UI must tolerate `null` rise/set times, treat health as
liveness only, and surface API failure rather than manufacture a successful
result.

Before integration:

- configure the Engine origin outside source and use `/api/v1`;
- choose and implement either explicit CORS for the Playground origin or a
  server-side same-origin proxy;
- implement the minimum stable error model and client handling;
- reject unknown request fields and verify exact forwarding;
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
| `HTTP-GAP-001` | high | Panchang docs/request | old guide included non-fields `date`/`time`; extras are ignored | keep split fields and reject unknowns | misleading requests can appear accepted | yes |
| `HTTP-GAP-002` | high | all POST requests | request extras ignored; coercive validation | define strictness and implement unknown-field rejection | typos can silently change meaning | yes |
| `HTTP-GAP-003` | high | Panchang | `language` accepted but unused | forward with defined semantics or remove/deprecate field | locale request is ineffective | yes for use of field |
| `HTTP-GAP-004` | high | Panchang, Dasha | `ayanamsa` accepted but not forwarded | forward and test, or remove/deprecate field | future mode/default drift | yes |
| `HTTP-GAP-005` | critical | browser boundary | no CORS policy | choose direct-browser allowlist or server proxy | cross-origin calls fail | yes |
| `HTTP-GAP-006` | high | all routes | no stable error envelope/codes | define minimum Engine error schema and mapping | reliable client error handling impossible | yes |
| `HTTP-GAP-007` | high | all calculations | numeric offsets only; no IANA/DST resolution | define future zone/disambiguation policy | London/New York unsafe | yes for international support |
| `HTTP-GAP-008` | medium | health | liveness only | add separate readiness/dependency contract if needed | health may be green while calculations fail | no for local v0 if represented honestly |
| `HTTP-GAP-009` | medium | response bodies | no schema ID/version | decide body-version strategy under API Stability | compatibility detection is limited | no for narrow v0 |
| `HTTP-GAP-010` | medium | float responses | no complete finite-number schema/transport test | constrain and test finite JSON output | rare serialization failure is not contractually excluded | yes |
| `HTTP-GAP-011` | medium | Kundali optional sections | several nested sections are `dict[str, Any]` | define strict versioned models before consumer approval | unstable broad payload | yes for Kundali |
| `HTTP-GAP-012` | high | Matchmaking/Reporting/Interpretation | implemented Python domains have no HTTP routes | design only through future authorized tasks | unavailable to Playground | yes for those capabilities |
| `HTTP-GAP-013` | medium | API guide | Dasha and health were omitted; Panchang example drifted | keep guide synchronized with this canonical spec | discovery and usage errors | resolved by this documentation task |
| `HTTP-GAP-014` | medium | readiness/accuracy | route fixtures are structural/regression evidence, not Golden references | complete governed independent evidence before accuracy claims | UI must avoid verified-accuracy claims | yes for such claims |
| `HTTP-GAP-015` | low | localization | mixed fixed multilingual fields; language has no projection contract | define transport versus presentation localization ownership | client cannot rely on locale-shaped data | no for fixed-field v0 |

## Smallest future runtime sequence

The next Engine task should be one focused **Panchang HTTP contract alignment**
change:

1. make request-extra behavior explicit and reject unknown fields;
2. decide and implement effective `language` and `ayanamsa` semantics (forward
   or deliberately deprecate/remove through the compatibility process);
3. introduce the minimum Engine-owned error response and mappings;
4. add finite-number response validation/serialization tests;
5. add route, OpenAPI, forwarding, and backward-compatibility contract tests;
6. choose either a narrow configured CORS allowlist or document and verify the
   Playground server-proxy deployment boundary; and
7. keep the first supported time contract fixed-offset and explicit.

These belong together only insofar as they gate one narrow Panchang consumer.
IANA timezone support, readiness probes, and body schema-version fields can be
separate follow-up decisions. Playground Panchang integration follows the gate;
other domain endpoints do not.

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

This specification makes no runtime or test change. It adds no endpoint, CORS
middleware, authentication, rate limiting, API key, environment variable,
database, cache, fake API data, Playground code, public Python export, or
calculation behavior.

## Playground handoff

| Consumer question | Answer |
| --- | --- |
| Base path | configured Engine origin plus `/api/v1`; never hardcode production origin |
| Safe now | health for liveness inspection only |
| First conditional result | Panchang, after the blocking alignment gate |
| Blocked/excluded | Kundali, Dasha, Matchmaking, Reporting, Interpretation, Prediction |
| Request/response source | this specification, then generated OpenAPI/runtime schemas; escalate discrepancies |
| Environment expectation | consumer-owned, deployment-specific Engine origin; no variable is created here |
| CORS dependency | absent; direct browser requires allowlist, otherwise use an approved server proxy |
| Error limitation | no stable Engine envelope or machine-readable codes |
| Time limitation | numeric fixed offset only; initial v0 should be `5.5`, no IANA/DST claim |
| Next Engine task | focused Panchang HTTP contract alignment and contract tests |

## Validation basis

Version 1.0 was produced by reviewing application inclusion and route
decorators, request/response schemas, route-to-calculation forwarding,
Panchang/Kundali/Dasha calculation entry points, existing API/schema tests,
generated-OpenAPI configuration source, current API documentation,
SPEC-API-STABILITY-001, Playground prerequisites, and cross-document links.
Runtime behavior was not changed.

## Change history

| Version | Change |
| --- | --- |
| 1.0 | Initial authoritative audit of the existing Engine HTTP API and minimum conditional Playground v0 contract. |
