# QalamOCR

QalamOCR (قلم = "pen") is an open-source, **Arabic-first** OCR & document
extraction engine, focused on **right-to-left (RTL) handling** and
**structured table extraction**, built on top of the PaddleOCR model family
under Apache-2.0.

Status: pre-development.

See `CONTRIBUTING.md` for the contribution workflow, `CODE_OF_CONDUCT.md` for community
standards, and `NOTICE` for third-party attributions.

## Development setup

Dependencies are managed with [uv](https://docs.astral.sh/uv/) via
`pyproject.toml` + `uv.lock` (not `pip freeze` + `requirements.txt`), so
versions are pinned reproducibly and dev/runtime dependencies stay separated.

This project uses a manually created `venv/` (not uv's default `.venv/`), so
every uv command that touches the environment needs `--active` run with the
venv activated.

```bash
# one-time: create the venv
python -m venv venv

# activate (do this every session)
source venv/Scripts/activate      # Git Bash
.\venv\Scripts\Activate.ps1       # PowerShell

# add a dependency (updates pyproject.toml + uv.lock + installs it)
uv add <package>
uv add --dev <package>             # dev-only dependency

# re-sync venv/ to match pyproject.toml + uv.lock (e.g. after pulling)
uv sync --active
```

If uv isn't installed yet:

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

## Pre-commit hooks

This repo uses [pre-commit](https://pre-commit.com/) to enforce formatting, linting, and the
commit message convention (see `CLAUDE.md`). Install once per clone:

```bash
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg
pre-commit run --all-files   # first run may reformat files; re-stage and commit
```
