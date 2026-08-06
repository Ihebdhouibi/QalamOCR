# Contributing to QalamOCR

Thanks for your interest in QalamOCR, an open-source, Arabic-first OCR and document-extraction
engine. This document covers environment setup, the branch/PR workflow, and sign-off
requirements. See `CLAUDE.md` for the full working agreement (commit conventions, no AI
attribution, no emojis, definition of done).

## Development environment

Dependencies are managed with [uv](https://docs.astral.sh/uv/) via `pyproject.toml` + `uv.lock`.

```bash
# one-time: create the venv
python -m venv venv

# activate (do this every session)
source venv/Scripts/activate      # Git Bash
.\venv\Scripts\Activate.ps1       # PowerShell

# install/sync dependencies, including dev tools (ruff, mypy, pytest)
uv sync --active --all-groups

# add a dependency later
uv add --active <package>
uv add --active --dev <package>   # dev-only dependency
```

Install the pre-commit hooks once per clone:

```bash
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg
```

## Branching and pull requests

- Branch model: `main` (protected, release) <- `stable-testing` (RC) <- `develop`
  (integration) <- `feature/*` or `chore/*` (one branch per issue).
- One issue = one branch = one pull request into `develop`. Squash-merge only. No direct
  commits to `main`, `stable-testing`, or `develop`.
- Commit messages: `<type>: <short imperative subject>`, types only: `feat`, `chore`, `docs`,
  `tests`, `bug`. Enforced by the `commit-msg` pre-commit hook.
- Open your PR against `develop` and link the issue it closes (e.g. `Closes #12`).

## Sign-off (DCO)

Commits must be signed off to certify you have the right to submit the change under the
project's license (Apache-2.0):

```bash
git commit -s -m "feat: short imperative subject"
```

This adds a `Signed-off-by:` trailer with your name and email to the commit message.

## Definition of done

Code plus tests, pre-commit clean, CI green (`CI / lint` and `CI / test`), PR links its issue,
and the PR has been reviewed.
