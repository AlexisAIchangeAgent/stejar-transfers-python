# stejar-transfers-python

Training material. Invented bank. Stejar Bank SA, its customers and its figures are invented.

Transfer-fee service of Stejar Bank: `POST /fees` returns the fee of a transfer in MDL,
`GET /health` returns `{"status": "ok"}`. Python 3.10+, FastAPI.

## Getting started

Windows 11: use PowerShell. macOS: use Terminal. Run every command from the repository folder.

```
git clone https://github.com/AlexisAIchangeAgent/stejar-transfers-python.git
cd stejar-transfers-python
```

Or download the ZIP of the latest release on GitHub (Releases, then Source code (zip)), unzip it,
and open a terminal in the folder. Step 3 then creates the git repository: the training commits
in it.

| Step | Windows | macOS |
|---|---|---|
| 1. Check the tools (changes nothing) | `powershell -ExecutionPolicy Bypass -File .\check.ps1` | `bash check.sh` |
| 2. Only if a line says KO: install the missing tools, open a new terminal, run step 1 again | `powershell -ExecutionPolicy Bypass -File .\install-tools.ps1` | `bash install-tools.sh` |
| 3. Install the dependencies of the project (network, a few minutes) | `powershell -ExecutionPolicy Bypass -File .\setup.ps1` | `bash setup.sh` |
| 4. Start Claude Code | `claude` | `claude` |

Step 3 ends with "Ready for cycle 1". If your IT team installs the tools for you, give them
`INSTALL-TOOLS.md`.

## Before the training

Run these once, with network access. During the training, Claude Code works without network.

`setup.ps1` (Windows) and `setup.sh` (macOS) run these steps for you, then the unit tests: see
Getting started above. The commands below do the same by hand.

```
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m playwright install chromium
```

On Windows (PowerShell or cmd), use `.venv\Scripts\python` instead of `.venv/bin/python`, here
and in every command below.

The dev install also brings the Claude Agent SDK used in `privacy-agent/`.

## Build

```
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
```

On Windows:

```
py -3 -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
```

`py -3` uses the newest Python installed; `py -3.10` or `py -3.12` picks another one, and
`python -m venv .venv` works too. With `make` (macOS, Linux): `make install`. `make` is not
installed on Windows: run the commands.

## Run

macOS and Linux:

```
.venv/bin/python -m uvicorn stejar_transfers.main:app --reload --port 8000
curl -X POST localhost:8000/fees -H "Content-Type: application/json" \
  -d '{"amount": 2000.00, "currency": "MDL", "type": "standard", "customer_segment": "retail"}'
```

Windows, PowerShell (in Windows PowerShell 5.1 `curl` is an alias of `Invoke-WebRequest`, so the
`curl` line above does not work). Start the service, then call it from a second terminal:

```
.venv\Scripts\python -m uvicorn stejar_transfers.main:app --reload --port 8000
Invoke-RestMethod -Method Post -Uri http://localhost:8000/fees -ContentType "application/json" -Body '{"amount": 2000.00, "currency": "MDL", "type": "standard", "customer_segment": "retail"}'
```

Windows, cmd (`curl.exe` ships with Windows 10 and 11; inner quotes are escaped):

```
curl -X POST localhost:8000/fees -H "Content-Type: application/json" -d "{\"amount\": 2000.00, \"currency\": \"MDL\", \"type\": \"standard\", \"customer_segment\": \"retail\"}"
```

Without `RATES_BASE_URL` in the environment, the service uses a fixed EUR to MDL rate
(19.8765) and makes no network call.

## Test

```
.venv/bin/python -m pytest                   # unit tests (tests/unit)
.venv/bin/python -m behave                   # BDD features (features/), instant fee steps not written yet
.venv/bin/python -m ruff check .             # lint
.venv/bin/python -m ruff format --check .    # format check
```

On Windows, `.venv\Scripts\python -m behave` reports the 46 steps of `instant-fee.feature` as
undefined and exits with code 1: this is expected until the step definitions are written.
With this behave version (1.3.3) the 9 scenarios are counted as `error`, not `failed`.

Playwright browser, needed for the Playwright tests of the training:

```
.venv/bin/python -m playwright install chromium
```

`make test`, `make bdd`, `make lint` and `make playwright-install` do the same on macOS and
Linux. `make` is not installed on Windows: run the commands above.

## Folder map

| Folder | Content |
|---|---|
| `src/stejar_transfers/` | the service: `api/`, `domain/`, `clients/` |
| `tests/unit/` | pytest unit tests |
| `features/` | behave features, `steps/`, `environment.py` |
| `crm/` | static page of the internal CRM |
| `incidents/` | incident tickets |
| `docs/` | service documentation, published tariff, `adr/` |
| `privacy-agent/` | GDPR intake policy and synthetic requests |
| `docs/pipeline/` | CI pipeline, not active yet: cycle 3 copies it to `.github/workflows/` |

See `CLAUDE.md` for the conventions.
