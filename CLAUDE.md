# CLAUDE.md — Working agreement for QalamOCR

## Rules (must follow)

1. No AI attribution. Never add "Generated with Claude", "Co-authored-by: Claude", Copilot, or
   any similar mention in commits, PRs, or code. Describe the change only.
2. No emojis. Anywhere: code, comments, commit messages, PR descriptions, docs.
3. Always end a task with a summary: What was done, Why, What to expect, Edge cases to handle.
4. Commit convention: `<type>: <short imperative subject>`, types only:
   `feat`, `chore`, `docs`, `tests`, `bug`.
5. Pre-commit must pass before every commit. Never bypass with `--no-verify`.

## Branching & PRs

- Model: `main` (protected, release) <- `stable-testing` (RC) <- `develop` (integration)
  <- `feature/*` or `chore/*` (one branch per issue).
- One issue = one branch = one PR into `develop`. Squash-merge. No direct commits to protected
  branches. Use the terminal git CLI for all version control.

## Definition of done

Code + tests, pre-commit clean, CI green, PR links its issue, reviewed.

## Project setup

Dependencies are managed with [uv](https://docs.astral.sh/uv/) via `pyproject.toml` + `uv.lock`.
This project uses a manually created `venv/` (not uv's default `.venv/`), so uv commands that
touch the environment need `--active` run with the venv activated. See `README.md` for the full
setup steps.
