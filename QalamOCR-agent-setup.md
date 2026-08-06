# Agent Setup Playbook — replicate the Arabic-Islamic-Rag workflow on QalamOCR

Paste this whole file to the agent in the QalamOCR VS Code window. It reproduces the project
governance, GitHub ruleset, issue/milestone/board setup, and the PR-per-issue development loop we
used successfully on another repo. Commands assume **Windows PowerShell** and the **GitHub CLI
(`gh`)**; adapt paths/tooling to the actual stack.

Repo: `Ihebdhouibi/QalamOCR`

---

## 0. Orient first (do this before anything)

1. Detect the stack: read the repo (`README`, build/config files) and tell me what it is
   (Python? Node/TS? Rust? mixed?) and how it builds/tests. Everything tool-specific below
   (linters, CI steps) must be adapted to that stack.
2. Confirm `gh auth status` works and the user has **admin** on the repo.
3. Confirm the default branch and whether `develop`/`stable-testing` already exist.
4. **Wait for the user's approval of a plan before writing code.** Produce a short plan +
   milestone/issue breakdown first (see §5).

---

## 1. Working agreement — create `CLAUDE.md` at repo root

These are the user's hard rules. Follow them yourself too.

```markdown
# CLAUDE.md — Working agreement for QalamOCR

## Rules (must follow)
1. No AI attribution. Never add "Generated with Claude", "Co-authored-by: Claude", Copilot, or any
   similar mention in commits, PRs, or code. Describe the change only.
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
```

---

## 2. Pre-commit + hygiene

Create `.pre-commit-config.yaml` (swap the language hooks for the real stack — the example shows a
Python stack; for Node use e.g. eslint/prettier hooks instead of ruff):

```yaml
minimum_pre_commit_version: "3.5.0"
default_install_hook_types: [pre-commit, commit-msg]
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: trailing-whitespace
        args: [--markdown-linebreak-ext=md]
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: [--maxkb=1024]
      - id: check-merge-conflict
      - id: mixed-line-ending
        args: [--fix=lf]
  # --- language hooks: replace with the project's real linter/formatter ---
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.16.1
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  # --- enforce the commit-message convention (custom types) ---
  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v4.4.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
        args: [feat, chore, docs, tests, bug]
```

Then run once (pin revs to valid tags automatically, install both hook types):

```powershell
pip install pre-commit    # or: pipx install pre-commit
pre-commit autoupdate
pre-commit install
pre-commit install --hook-type commit-msg
pre-commit run --all-files   # first run normalizes line endings etc.; re-stage and commit
```

Also add a `.gitattributes` with `* text=auto eol=lf` to stop CRLF/LF churn on Windows, and add the
usual ignores (`.env`, build/cache dirs) to `.gitignore`. Keep `.env.example` tracked, `.env`
ignored.

---

## 3. Branches + GitHub ruleset (the important part)

### 3.1 Create the branches
```powershell
git checkout main; git pull
git checkout -b develop;        git push -u origin develop
git checkout -b stable-testing; git push -u origin stable-testing
git checkout develop
```

### 3.2 Create ONE ruleset scoped to the protected branches only
Do NOT target `~ALL` — that blocks pushing feature branches. Target exactly the three protected
branches. Create it (adjust owner/repo):

```powershell
$body = @'
{
  "name": "protected-branches",
  "target": "branch",
  "enforcement": "active",
  "bypass_actors": [
    { "actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always" }
  ],
  "conditions": {
    "ref_name": {
      "include": ["refs/heads/main", "refs/heads/stable-testing", "refs/heads/develop"],
      "exclude": []
    }
  },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": true,
        "allowed_merge_methods": ["squash"]
      }
    }
  ]
}
'@
$body | gh api -X POST repos/Ihebdhouibi/QalamOCR/rulesets --input -
```

Key points learned:
- `bypass_actors` = **Repository admin (actor_id 5)** so the owner can merge their own PRs
  (GitHub NEVER lets you approve your own PR; without bypass a solo/lead author is blocked).
- Leave out `required_status_checks` for now. Add it AFTER the CI workflow has run once, because
  the check contexts don't exist until then. To add later, PUT the ruleset's full `rules` array
  plus:
  ```json
  { "type": "required_status_checks",
    "parameters": { "strict_required_status_checks_policy": true,
      "required_status_checks": [ { "context": "CI / lint" }, { "context": "CI / test" } ] } }
  ```
  The context name is `"<workflow name> / <job id>"` (e.g. `CI / test`), not the bare job id.
- If a push is rejected with "Changes must be made through a pull request" on a *feature* branch,
  the ruleset is mis-scoped to `~ALL`; fix `conditions.ref_name.include` to the three branches.

### 3.3 GitHub repo settings (UI, one-time)
Settings → General → Pull Requests: enable **squash merging** and **auto-delete head branches**.
Optionally set `develop` as the default branch so PRs target it and `main` stays clean.

---

## 4. CI workflow

Create `.github/workflows/ci.yml` with two jobs named **`lint`** and **`test`** (their check
contexts become `CI / lint` and `CI / test`). Trigger on PRs/pushes to
`develop`/`stable-testing`/`main`. Adapt steps to the stack; if the project needs services
(DB, etc.), add them as `services:` containers. Example skeleton (Python; adapt):

```yaml
name: CI
on:
  pull_request: { branches: [develop, stable-testing, main] }
  push: { branches: [develop, stable-testing, main] }
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11", cache: pip, cache-dependency-path: pyproject.toml }
      - run: pip install -e ".[dev]"
      - run: ruff check .
      - run: ruff format --check .
      - run: mypy src
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11", cache: pip, cache-dependency-path: pyproject.toml }
      - run: pip install -e ".[dev]"
      - run: pytest -q
```

After CI passes once, go back and add the `required_status_checks` rule (§3.2).

---

## 5. Plan, then issues / milestones / project board

1. Write a short plan and a milestone-grouped issue backlog (many small issues, each = one PR).
   Get the user's approval before creating anything.
2. Create labels, milestones, and issues with `gh`. Milestones use `gh api` (no native command);
   guard against duplicates. Pattern:

```powershell
# labels
foreach ($l in @("infra","ci","docs","tests","bug","good-first-issue")) {
  gh label create $l --repo Ihebdhouibi/QalamOCR --force 2>$null | Out-Null
}
# milestone (idempotent)
$exists = gh api "repos/Ihebdhouibi/QalamOCR/milestones?state=all" --jq '.[].title'
if ($exists -notcontains "M0 - Foundation") {
  gh api repos/Ihebdhouibi/QalamOCR/milestones -f "title=M0 - Foundation" -f "description=..." | Out-Null
}
# issue
gh issue create --repo Ihebdhouibi/QalamOCR --title "M0-01 - ..." --milestone "M0 - Foundation" `
  --label infra --body "Depends on: -  |  Branch: feature/m0-... `n Done when: ..."
```

Generate a `scripts/create_issues.ps1` that creates all of them in one run (bodies ASCII-only so
Windows PowerShell passes non-Latin text to `gh` without mangling). Run the issue-creation section
**once** (re-running duplicates issues).

3. Optional project board:
```powershell
gh auth refresh -s project
gh project create --owner Ihebdhouibi --title "QalamOCR"
# add every issue to it:
$n = <project-number>
gh issue list --repo Ihebdhouibi/QalamOCR --limit 200 --json url --jq '.[].url' |
  ForEach-Object { gh project item-add $n --owner Ihebdhouibi --url $_ }
```

---

## 6. The per-issue development loop (repeat for every issue)

```powershell
git checkout develop; git pull
git checkout -b feature/<milestone>-<slug>
# ... implement the change + tests ...
# validate locally with the stack's tools, e.g.:
#   ruff check . ; ruff format --check . ; mypy src ; pytest -q
git add <files>
git commit -m "<type>: <short imperative>"   # pre-commit runs here
# If a hook reformats files (e.g. line endings), the commit ABORTS -> re-stage and commit again:
git add -A; git commit -m "<type>: <short imperative>"
git push -u origin feature/<milestone>-<slug>
gh pr create --base develop --head feature/<milestone>-<slug> --title "<type>: ... (M#-##)" `
  --body "Implements M#-##. ... `n`nCloses #<issue>"
```

Check CI (do NOT use `gh run watch` — it opens a full-screen TUI that hijacks the terminal):
```powershell
gh run list --branch feature/<milestone>-<slug> --limit 1 --json status,conclusion | Out-String
```

Merge only when CI is green. The user usually merges; the command (admin bypass for own PRs) is:
```powershell
gh pr merge <n> --squash --delete-branch --admin
```
End every issue with the What/Why/Expect/Edge-cases summary (rule 3).

---

## 7. Gotchas we actually hit (save yourself the debugging)

- **Never run `Start-Sleep`/poll for CI.** Query `gh run list --json status,conclusion` once; if
  in progress, report and move on.
- **`gh run watch` / `gh pr checks` open a TUI (alternate buffer).** Prefer `gh run list --json`.
- **Self-approval is impossible.** You can't approve your own PR; rely on the admin bypass actor
  (§3.2) or a second reviewer. Rulesets can't be scoped by author.
- **Pre-commit line-ending fix aborts the first commit** of new files on Windows. Re-`git add`
  and commit again; add `.gitattributes` (`eol=lf`) to reduce it.
- **Ruff import order:** straight `import x` sorts before `from y import z` within a group; let
  `ruff check --fix` + `ruff format` settle it rather than hand-ordering.
- **Long non-Latin lines** trip line-length lint; let the formatter wrap, or split into a local
  variable.
- **`docker compose` interpolates HOST env vars** (`${POSTGRES_PASSWORD:-...}` picks up a real
  `POSTGRES_PASSWORD` on the machine). Keep them unset or use a `.env`.
- **A native service on the default port** (e.g. Postgres on 5432) will answer instead of your
  container; publish on an alternate host port (e.g. 5433) and match app config.
- **CI job-level env leaks into unit tests.** Tests of "default config" must clear the relevant
  env vars (e.g. via pytest `monkeypatch.delenv`) so ambient/CI values don't fail them.
- **Corpus/large data dirs must be git-ignored**; keep tiny committed fixtures for tests.

---

## 8. What to hand back to the user

- The plan + issue list for approval (before coding).
- Confirmation once branches + ruleset + CI + board exist.
- Then proceed issue-by-issue, one PR each into `develop`, pausing for the user to merge.
```
