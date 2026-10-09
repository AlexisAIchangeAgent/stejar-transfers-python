# CLAUDE.md: stejar-transfers-python

Training material: invented bank, invented data. Stejar Bank SA does not exist.

## Purpose

HTTP service of Stejar Bank that computes the fee of a customer transfer before the customer
confirms it. `POST /fees` takes an amount, a currency (MDL or EUR), a transfer type (standard
or instant) and a customer segment (retail or premium), and returns the fee in MDL with the
rule applied. EUR amounts are converted with a rate from a third-party exchange-rate API.
The published tariff is `docs/fee-rules.md`.

## Stack

- Python 3.10+ (CI runs 3.11). Packaging: `pyproject.toml` (setuptools), src layout.
- FastAPI + uvicorn; pydantic v2 (through FastAPI); simplejson (Decimal to JSON number).
- Dev tools (extra `dev`): pytest, httpx2 (FastAPI TestClient), behave, ruff; declared but not
  used yet: pact-python, pytest-playwright.
- `requirements-dev.txt` installs `-e .[dev]`.

## Folder map

```
src/stejar_transfers/
  main.py              create_app() factory and the module-level `app` for uvicorn
  config.py            Settings, read from environment variables
  api/                 routes.py (GET /health, POST /fees), schemas.py (bodies)
  domain/              models.py (enums, value objects), fees.py (FeeCalculator)
  clients/             exchange_rate.py (ExchangeRateClient, Http and Fixed clients)
tests/unit/            pytest unit tests, conftest.py
features/              behave: instant-fee.feature, environment.py, steps/ (no step yet)
crm/customer-lookup.html   static page of the internal CRM (for Playwright)
incidents/             incident tickets
docs/                  README-service.md, fee-rules.md, adr/ (empty)
privacy-agent/         GDPR intake agent material: policy.md, requests/, output/
docs/pipeline/ci.yml       pipeline, not active yet (cycle 3 copies it to .github/workflows/): unit tests on push and PR, manual fake deploy
```

## Commands

macOS and Linux shown; on Windows (PowerShell or cmd) use `.venv\Scripts\python`. `make` targets
run the same commands, but `make` is not installed on Windows: run the command of the table.

| Task | Command | make |
|---|---|---|
| Set up | `python3 -m venv .venv` (Windows: `py -3 -m venv .venv`) then `.venv/bin/python -m pip install -r requirements-dev.txt` | `make install` |
| Run | `.venv/bin/python -m uvicorn stejar_transfers.main:app --reload --port 8000` | `make run` |
| Unit tests | `.venv/bin/python -m pytest` | `make test` |
| One test | `.venv/bin/python -m pytest tests/unit/test_standard_mdl_fee.py -k minimum` | |
| BDD tests | `.venv/bin/python -m behave` | `make bdd` |
| Lint | `.venv/bin/python -m ruff check .` and `.venv/bin/python -m ruff format --check .` | `make lint` |
| Format | `.venv/bin/python -m ruff format .` and `.venv/bin/python -m ruff check --fix .` | `make format` |
| Playwright browser | `.venv/bin/python -m playwright install chromium` | `make playwright-install` |

- pytest runs `tests/unit` only (`testpaths` in `pyproject.toml`).
- behave runs `features/`. Today every scenario of `instant-fee.feature` has undefined steps,
  so behave exits with code 1. This is expected until the step definitions are written.
- The service reads `RATES_BASE_URL`, `RATES_API_KEY` and `RATES_TIMEOUT_SECONDS` from the
  environment. Without `RATES_BASE_URL` it uses `FixedRateClient` (rate 19.8765, no network).
  The `.env` file is not loaded automatically.

## Coding conventions

- PEP 8, ruff rules E, F, I, B, UP, SIM, line length 100, code formatted with `ruff format`.
- snake_case for modules, functions and variables; PascalCase for classes; UPPER_CASE for
  constants. Type hints on public functions.
- Package `stejar_transfers`, one sub-package per layer: `api`, `domain`, `clients`.
- Enums are `StrEnum`; value objects are frozen dataclasses (`domain/models.py`).
- Money: always `decimal.Decimal`, never `float`. Build it from strings (`Decimal("0.01")`),
  quantize to 2 decimals with an explicit rounding mode. Rounding rules come from
  `docs/fee-rules.md`. Fees are in MDL.
- The API writes `fee` as a JSON number through `DecimalJSONResponse` (no float conversion).
- Configuration only from environment variables, through `config.Settings`.

## Test conventions

- Unit tests in `tests/unit/`, files `test_<topic>.py`, functions
  `test_<subject>_<expected behaviour>`, e.g. `test_standard_mdl_fee_has_a_minimum_of_5`.
- Arrange, act, assert, separated by blank lines when a test has several steps.
- Parametrize cases with `pytest.mark.parametrize`.
- Fixtures in `tests/unit/conftest.py`: `calculator` (FeeCalculator) and `client`
  (FastAPI TestClient), both with a `FixedRateClient` at rate 20.0000.
- No network call in tests: use `FixedRateClient` or a fake implementing `ExchangeRateClient`.
- Compare money as `Decimal`; parse API JSON with `json.loads(..., parse_float=Decimal)`.
- BDD: features in `features/`, step definitions in `features/steps/*.py`. `environment.py`
  gives each scenario `context.client` (TestClient) and `context.rate_client`
  (`FixedRateClient`, rate 19.8765).

## Architecture boundaries

- `api -> domain -> clients`. Never the other way.
- `api` maps HTTP bodies to domain objects and back.
- `domain` holds the fee rules. It has no HTTP: no FastAPI, no urllib, no web framework.
  It depends on the `ExchangeRateClient` protocol, not on a concrete client.
- `clients` talks to third parties. `main.py` chooses the client (`HttpExchangeRateClient`
  when `RATES_BASE_URL` is set, otherwise `FixedRateClient`).
- `main.py` maps errors to HTTP: `UnsupportedTransferError` becomes 422 `{"error": ...}`,
  `ExchangeRateError` becomes 502 `{"error": "exchange rate unavailable"}`.

## Not implemented yet

- Instant transfer fee: `POST /fees` with `"type": "instant"` returns HTTP 422
  `{"error": "instant transfers not supported yet"}`. The acceptance criteria are in
  `features/instant-fee.feature`; no step definition exists yet.
- No Pact or Playwright test yet (dependencies installed). No agent code in `privacy-agent/`.

## Do not edit without asking

- `.github/workflows/`
- `.env` (fake values, committed on purpose for the training)
- `privacy-agent/requests/`

## Definition of done

- Unit tests green: `.venv/bin/python -m pytest`.
- BDD green for the features in scope: `.venv/bin/python -m behave`, no undefined
  step; a scenario left red is named in the commit message, with its reason.
- `ruff check .` and `ruff format --check .` clean; no new warning in the pytest output.
- New behaviour comes with tests; money stays in `Decimal`; layer boundaries respected.
