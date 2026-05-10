# CLAUDE.md

> **Status: starter / scaffold.** This repository is freshly initialized — at
> the time this file was written it contained no code, no README, and no
> default branch. The sections below marked **TODO** are placeholders. The
> next contributor (human or AI) who lands real code should replace each TODO
> with concrete information discovered from the actual codebase, then delete
> this banner.

This file gives AI assistants (Claude Code, Cursor, Copilot, etc.) the
context they need to work productively in this repository. Keep it short,
factual, and current — out-of-date guidance is worse than none.

---

## 1. Project purpose

Based on the repository name, this project is intended to analyze AI systems
against the **risk tiers defined by the EU AI Act** (Regulation (EU)
2024/1689). The likely scope is one or more of:

- Classifying AI systems / use cases into the four risk tiers.
- Producing a structured report or evidence pack for a given system.
- Tooling that helps developers or compliance teams self-assess.

**TODO:** Once a README, design doc, or initial implementation exists,
replace this section with the confirmed problem statement, primary inputs,
primary outputs, and intended users.

## 2. Repository layout

**TODO:** No source files exist yet. Once code lands, run `ls -la` and
`find . -maxdepth 3 -type f -not -path './.git/*'` and document the top-level
structure here — for each directory, one line on what lives in it.

## 3. Development workflow

**TODO:** Fill in once tooling is chosen. Use this template:

| Step | Command | Notes |
|------|---------|-------|
| Install dependencies | `TODO` | e.g. `uv sync`, `pip install -e .`, `npm install` |
| Run tests | `TODO` | e.g. `pytest`, `npm test` |
| Lint | `TODO` | e.g. `ruff check .`, `eslint .` |
| Format | `TODO` | e.g. `ruff format .`, `prettier -w .` |
| Type-check | `TODO` | e.g. `mypy`, `pyright`, `tsc --noEmit` |
| Run the app | `TODO` | entry point and required env vars |

Until this table is filled in, an assistant should **not** invent commands —
ask the user or inspect the project files (`pyproject.toml`,
`package.json`, `Makefile`, etc.) to discover the real ones.

## 4. Branching, commits, and pushes

These rules are active right now and apply even before real code is added.

- **Active development branch:** `claude/add-claude-documentation-nqFt9`.
  All work in the current task lands here.
- Never push to a different branch (including `main`) without explicit user
  permission.
- Always push with `git push -u origin <branch-name>`. On transient network
  failures, retry up to 4 times with exponential backoff (2s, 4s, 8s, 16s).
  Do not retry on non-network errors — diagnose first.
- Prefer fetching specific branches: `git fetch origin <branch-name>`.
- Create new commits rather than amending. If a pre-commit hook fails, fix
  the underlying issue, re-stage, and create a new commit — never use
  `--no-verify`.
- Stage files explicitly by name; avoid `git add -A` / `git add .` so that
  secrets or large artifacts are not committed by accident.
- **Never open a pull request unless the user explicitly asks for one.**

## 5. Domain conventions (EU AI Act reference)

This is reference-only vocabulary so assistants use the correct terms. It is
not a substitute for the regulation text and should be revised once the
project defines its own canonical terminology.

- **Risk tiers** (descending severity):
  1. **Unacceptable risk** — prohibited practices listed in **Article 5**
     (e.g. social scoring by public authorities, untargeted scraping for
     facial-recognition databases, certain biometric categorization).
  2. **High risk** — systems covered by **Article 6** and **Annex III**
     (e.g. biometrics, critical infrastructure, education, employment,
     essential services, law enforcement, migration, justice, democratic
     processes), plus AI as a safety component of products in Annex I.
  3. **Limited risk** — transparency obligations (e.g. chatbots, deepfakes,
     emotion-recognition disclosures) under **Article 50**.
  4. **Minimal risk** — everything else; voluntary codes of conduct.
- **General-Purpose AI (GPAI) models** have their own obligations (Chapter
  V); models with **systemic risk** have additional ones.
- Prefer the regulation's own terms — *provider*, *deployer*, *importer*,
  *distributor*, *AI system*, *placing on the market*, *putting into
  service* — over informal synonyms.
- When citing the Act, use article and annex numbers (e.g. "Article 6(2),
  Annex III §1(a)") rather than paraphrases.

**TODO:** Once the project picks a canonical data model (which fields
describe a system under analysis, which schema the output uses, etc.),
document it here and link to the source files.

## 6. Conventions for changes

Until project-specific conventions exist, follow these defaults:

- Keep changes minimal and scoped to the task. No drive-by refactors.
- Don't add features, abstractions, fallbacks, or comments that the task
  doesn't require.
- Don't introduce dependencies without confirming with the user.
- When in doubt about scope, regulatory interpretation, or design choice,
  **ask** — do not guess. EU AI Act classifications have legal
  implications; an assistant should never silently decide a borderline
  case.

## 7. For AI assistants: how to maintain this file

When you do real work in this repository:

1. Replace each **TODO** above with the concrete answer you discovered
   (commands actually run, paths actually present, conventions actually
   followed).
2. Delete the status banner at the top of the file once the document
   reflects reality.
3. Keep the file short. If a section grows beyond a screen, split the
   detail into a dedicated doc and link to it.
4. If you change a workflow command (e.g. switch test runner), update
   section 3 in the same commit — stale instructions here will mislead the
   next assistant.
