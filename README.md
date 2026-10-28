# EU AI ACT simplified risk level analysis

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
├── README.md      — this file
├── content.xlsx   — SOURCE OF TRUTH: all text, links, questions, options, tiers and rules
├── template.html  — page layout, CSS and the generic classify/render JS (placeholders like {{footer}})
├── build.py       — reads content.xlsx, validates it, fills template.html → index.html
└── index.html     — GENERATED, committed so the site works without a build server
```

**Never edit `index.html` by hand** — edit `content.xlsx` (content) or
`template.html` (layout/behaviour) and run `python3 build.py`.

Sheets in `content.xlsx` (its own **README** sheet explains them for editors):

- `page`         — header, disclaimer, deadline notice, labels, call-to-action, footer.
- `links`        — every URL, referenced from text as `[label](link_id)`.
- `questions`    — the questions, in display order.
- `options`      — answer options per question: `effect` (a tier_id, `addon`, or
  empty), `provision`, `verbatim` Act text, `note` (add-ons), `enabled`.
- `tiers`        — risk tiers, most → least severe; the last is the default result
  and carries the fallback provision/verbatim.
- `tier_details` — the **What now?** bullets (`implications` / `actions`) per tier.

Classification rule (`classify(answers)` in `template.html`): the result is the
most severe tier among the selected options' effects; every selected option of
that tier is quoted under **Why?**; `addon` options (GPAI) are appended below.
Text cells support `**bold**`, `*italic*`, `[label](link_id or https://…)`;
`verbatim` cells are shown as plain text.

`classify` and `render` are deliberately pure so they can be unit-tested
without a DOM.

## 3. Development workflow

| Step | Command | Notes |
|------|---------|-------|
| Build | `python3 build.py` | after any change to `content.xlsx` or `template.html`; standard library only, exits 1 with sheet/row errors |
| Run locally | `python3 -m http.server 8000` then open `http://localhost:8000/` | or just `open index.html` |
| Deployed | https://jjsantanna.duckdns.org/eu-ai-act-risk-classifier/ | nginx container `eu-ai-act-risk-classifier` serves this folder read-only (`~/apps/docker-compose.yml`); only `index.html` is public, so rebuilding is enough to publish |
| Smoke-test classifier | `node test.js` (not yet present) | extract `<script>` block; call `classify`/`render` |
| Lint | _none_ | vanilla HTML/CSS/JS, no toolchain |
| Format | _none_ | match the existing 2-space indent and double-quoted JS strings |

There is no test suite, package manager, CI, or formatter today; the only build step is `build.py`. If
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

- **Verbatim text is verbatim.** When updating a `verbatim` cell in
  `content.xlsx` (sheets `options` and `tiers`), copy from
  [Regulation (EU) 2024/1689](https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ:L_202401689)
  exactly. Don't paraphrase, summarise, or "clean up" the legalese — the
  point of the **Why?** section is that the user can audit the citation.
  If a quote is shortened with `...`, keep the ellipsis explicit.
- **Cite by article and annex number** (e.g. "Article 6(2)", "Annex III §1(a)") —
  not by paraphrase.
- **Keep the disclaimer.** The `disclaimer` row in the `page` sheet (not legal
  advice) is not decorative; do not remove it without instruction. `build.py`
  refuses to build without it.
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
- **Application dates** (Article 113, as amended by Regulation (EU) 2026/1744,
  the "Digital Omnibus on AI", in force since July 2026):
  - prohibitions (Article 5) from 2 Feb 2025; the two prohibitions added by the
    Omnibus (non-consensual intimate imagery, child sexual abuse material) from
    2 Dec 2026;
  - Article 50 transparency from 2 Aug 2026 (not postponed); systems placed on
    the market before that date have until 2 Dec 2026 for Article 50(2) marking;
  - Annex III high-risk obligations from 2 Dec 2027 (was 2 Aug 2026);
  - Annex I safety-component systems from 2 Aug 2028 (was 2 Aug 2027).

## 7. Conventions for changes

- Keep changes minimal and scoped to the task. No drive-by refactors.
- Don't add features, abstractions, or fallbacks the task doesn't require.
- Don't introduce dependencies or a build step without confirming first.
- When in doubt about regulatory interpretation, **ask** — do not guess.
  Misclassifying an AI system has legal consequences.
