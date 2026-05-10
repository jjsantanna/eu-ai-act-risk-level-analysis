# CLAUDE.md

This file gives AI assistants (Claude Code, Cursor, Copilot, etc.) the
context they need to work productively in this repository. Keep it short,
factual, and current — out-of-date guidance is worse than none.

## 1. Project purpose

A single-page web tool that classifies an AI system into one of the four EU
AI Act risk tiers (**unacceptable / high / limited / minimal**) based on a
short dropdown questionnaire. For each result it shows:

- the tier in large bold type,
- a collapsible **Why?** section that quotes the relevant article(s) of
  Regulation (EU) 2024/1689 verbatim, and
- a collapsible **What now?** section with implications, action items, and
  a pointer to Bureau Veritas for compliance support.

It also surfaces the additional Chapter V obligations that apply when the
underlying model is a General-Purpose AI model (Article 53), with extra
duties for GPAI models with systemic risk (Article 55).

The classifier is deterministic — the dropdown answers map directly to Act
provisions; no machine-learning inference is performed.

## 2. Repository layout

```
.
├── CLAUDE.md      — this file
└── index.html     — the entire app: HTML form, CSS, JS classifier + verbatim Act text
```

Everything lives in `index.html`. There is no build step, package manager,
or backend. Open the file in a browser, or serve the directory with any
static-file server (e.g. `python3 -m http.server`).

Key chunks inside `index.html`:

- `ARTICLE_5_TEXT`  — verbatim quotes of Article 5(1)(a)–(h) prohibitions.
- `ANNEX_III_TEXT`  — Article 6(1) safety-component clause + the eight
  Annex III high-risk categories.
- `ARTICLE_50_TEXT` — Article 50(1)–(4) transparency obligations.
- `GPAI_TEXT`       — Articles 53(1) and 55(1) GPAI obligations.
- `TIER_CONTENT`    — the **What now?** copy (implications + actions) per tier.
- `classify(q1, q2, q3, q4)` — pure function returning `{ tier, reasons, gpaiNote }`.
- `render(result)`  — pure function that produces the result HTML.

`classify` and `render` are deliberately pure so they can be unit-tested
without a DOM.

## 3. Development workflow

| Step | Command | Notes |
|------|---------|-------|
| Run locally | `python3 -m http.server 8000` then open `http://localhost:8000/` | or just `open index.html` |
| Smoke-test classifier | `node test.js` (not yet present) | extract `<script>` block; call `classify`/`render` |
| Lint | _none_ | vanilla HTML/CSS/JS, no toolchain |
| Format | _none_ | match the existing 2-space indent and double-quoted JS strings |

There is no test suite, package manager, CI, or formatter today. If
adding any of those, document the commands here in the same commit.

## 4. Branching, commits, and pushes

- **Active development branch:** `claude/add-claude-documentation-nqFt9`.
- Never push to a different branch (including `main`) without explicit
  user permission.
- Push with `git push -u origin <branch-name>`. On transient network
  failures, retry up to 4 times with exponential backoff (2s, 4s, 8s, 16s).
  Don't retry on non-network errors — diagnose first.
- Prefer `git fetch origin <branch-name>` over a bare `git fetch`.
- Create new commits rather than amending. If a pre-commit hook fails, fix
  the underlying issue, re-stage, and create a new commit — never use
  `--no-verify`.
- Stage files explicitly by name; avoid `git add -A` / `git add .`.
- **Never open a pull request unless the user explicitly asks for one.**

## 5. Editing rules specific to this project

- **Verbatim text is verbatim.** When updating a quote in `ARTICLE_5_TEXT`,
  `ANNEX_III_TEXT`, `ARTICLE_50_TEXT` or `GPAI_TEXT`, copy from
  [Regulation (EU) 2024/1689](https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ:L_202401689)
  exactly. Don't paraphrase, summarise, or "clean up" the legalese — the
  point of the **Why?** section is that the user can audit the citation.
  If a quote is shortened with `...`, keep the ellipsis explicit.
- **Cite by article and annex number** (e.g. "Article 6(2)", "Annex III §1(a)") —
  not by paraphrase.
- **Keep the disclaimer.** The yellow notice that says this tool is not
  legal advice is not decorative; do not remove it without instruction.
- **Don't silently decide borderline cases.** If a dropdown option is
  ambiguous, prefer adding a clarifying sub-question over baking an
  assumption into the classifier.
- **No external runtime dependencies.** No CDN scripts, no fonts loaded
  from the network, no analytics — the page must work fully offline.
- **Use the regulation's own terms** — *provider*, *deployer*, *importer*,
  *distributor*, *AI system*, *placing on the market*, *putting into
  service* — over informal synonyms.

## 6. Domain conventions (EU AI Act reference)

Reference vocabulary so assistants use the correct terms:

- **Risk tiers** (descending severity):
  1. **Unacceptable risk** — prohibited practices in **Article 5**.
  2. **High risk** — **Article 6** + **Annex III**, plus AI as a safety
     component of products in **Annex I**.
  3. **Limited risk** — transparency obligations in **Article 50**.
  4. **Minimal risk** — everything else; voluntary codes of conduct
     (**Article 95**).
- **GPAI**: Chapter V — Articles 53 (general) and 55 (systemic-risk models).
- **Penalties**: Article 99 — up to €35M or 7% turnover for prohibited
  practices, €15M or 3% for most other infringements.
- **Application dates**: Article 113 — prohibitions from 2 Feb 2025;
  Article 50 transparency and most high-risk obligations from 2 Aug 2026;
  Annex I safety-component systems from 2 Aug 2027.

## 7. Conventions for changes

- Keep changes minimal and scoped to the task. No drive-by refactors.
- Don't add features, abstractions, or fallbacks the task doesn't require.
- Don't introduce dependencies or a build step without confirming first.
- When in doubt about regulatory interpretation, **ask** — do not guess.
  Misclassifying an AI system has legal consequences.
