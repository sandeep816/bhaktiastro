# Accuracy

## Panchang Fixtures

The current Panchang fixture files are structural fixtures. They are generated
from the current local API output and are used to keep the response shape
stable while Phase 2 calculations continue to mature.

Current structural fixtures:

- `backend/tests/fixtures/panchang_jodhpur_1985_04_20.json`
- `backend/tests/fixtures/panchang_delhi_2000_01_01.json`

These files do not yet certify exact astronomical or Panchang values. They
should not be treated as verified golden values until each value has been
manually checked against trusted external references.

## Pending Exact Validation

Exact-value validation is pending for:

- Julian Day and UTC conversion
- Ayanamsa
- Sun and Moon longitudes
- Tithi, Nakshatra, Yoga, and Karana values
- Boundary end times
- Sunrise, sunset, moonrise, and moonset times

Before exact-value tests are enabled, values must be verified against at least
two trusted references where practical, such as:

- Jagannatha Hora
- Drik Panchang
- Astro-Seek
- A trusted printed Panchang

Until that manual verification is complete, exact-value fixture tests must
remain skipped with a clear TODO reason. Structural fixture tests may pass, but
that only means the API response shape matches the saved fixture shape.
