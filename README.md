# BhaktiAstro

BhaktiAstro is an open-source, local Python-based Vedic Astrology Engine for Panchang, Janam Kundali, Dasha, Yoga/Dosha, Muhurat, Matchmaking, reports, and future BhaktiRas integration.

The project is built around one core principle: deterministic calculation first, interpretation later. Astronomy and astrology calculations must run locally with Python and Swiss Ephemeris / `pyswisseph`; AI is allowed only as a later explanation layer and must never calculate or override astrology data.

## Current Status

This repository is in Phase 0 project setup.

Created so far:
- Project folder structure
- Python package markers
- `pyproject.toml`
- `requirements.txt`
- `requirements-dev.txt`
- `.gitignore`
- `.env.example`
- Basic `backend/app/config.py`
- Basic `backend/app/logging.py`

Application calculation code is not implemented yet.

## Project Rules

- One task at a time.
- One task equals one commit.
- Never guess astrology formulas.
- AI must not calculate astrology.
- Do deterministic astronomy first, deterministic astrology second, interpretation later.
- No paid astrology API for core calculations.
- Timezone input must be explicit.
- Any unverified formula must remain incomplete until source-verified.

See [CODEX_INSTRUCTIONS.md](CODEX_INSTRUCTIONS.md), [FEATURES_v3.md](FEATURES_v3.md), [CALCULATIONS.md](CALCULATIONS.md), and [PROJECT_PHASES.md](PROJECT_PHASES.md) for the full project contract.

## Architecture

```text
backend/app/
├── astronomy/       Pure astronomical calculations
├── astrology/       Deterministic Vedic astrology calculations
├── constants/       Static domain data and mappings
├── rules/           Deterministic Yoga/Dosha/rule detection
├── interpretation/  Text interpretation only, no calculations
├── reports/         HTML/PDF/report generation
├── schemas/         Pydantic request/response models
├── api/v1/          Versioned FastAPI routes
└── database/        Future persistence layer
```

Additional folders:
- `backend/tests/fixtures/`: Golden fixtures and reference outputs.
- `data/ephe/`: Swiss Ephemeris data files, not committed.
- `frontend/`: Future templates and static assets.
- `docs/`: Project documentation.
- `reports/`: Generated reports, not committed.

## Requirements

- Python 3.11+
- FastAPI
- Pydantic v2
- `pyswisseph`
- Pytest
- Ruff
- Black

Runtime dependencies are listed in [requirements.txt](requirements.txt). Development dependencies are listed in [requirements-dev.txt](requirements-dev.txt).

## Environment

Copy `.env.example` to `.env` locally when runtime configuration is needed. Do not commit `.env`.

Important settings:
- `APP_NAME`
- `APP_ENV`
- `APP_VERSION`
- `DEFAULT_LANGUAGE`
- `DEFAULT_AYANAMSA`
- `DEFAULT_TIMEZONE`
- `DATABASE_URL`
- `EPHE_PATH`
- `LOG_LEVEL`

## Swiss Ephemeris

Swiss Ephemeris data files belong in:

```text
data/ephe/
```

These files are intentionally ignored by git. The expected files for the initial setup are:

```text
seas_18.se1
semo_18.se1
sepl_18.se1
```

## Development

Install dependencies only when working on the dependency setup task:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Run tests when testable code exists:

```bash
pytest
```

### Run Panchang smoke test

Print a local Panchang sample response without starting the FastAPI server:

```bash
python scripts/smoke_panchang.py
```

Run formatting and linting when configured in the task:

```bash
black .
ruff check .
```

## Accuracy Policy

Calculations must be verified against trusted references such as:
- Jagannatha Hora
- Astro-Seek
- Drik Panchang
- Trusted printed Panchang or classical source

If a formula is not verified, do not implement guessed behavior. Use a TODO and skipped test until the formula is source-verified.

## License

License information is currently declared in `pyproject.toml`.
