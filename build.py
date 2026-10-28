#!/usr/bin/env python3
"""Build index.html from content.xlsx + template.html.

All text, links, questions, options, tiers and classification rules live in
content.xlsx (see its "README" sheet). This script only reads the workbook,
validates it and fills the template. Standard library only — no installs.

Usage: python3 build.py [--xlsx content.xlsx] [--template template.html] [--out index.html]
"""
import argparse
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
PR = "{http://schemas.openxmlformats.org/package/2006/relationships}"

REQUIRED_COLUMNS = {
    "page": ["key", "value"],
    "links": ["link_id", "url"],
    "questions": ["question_id", "title", "hint"],
    "options": ["question_id", "option_id", "label", "effect", "provision", "verbatim", "note", "enabled"],
    "tiers": ["tier_id", "headline", "color", "color_dark", "fallback_provision", "fallback_verbatim"],
    "tier_details": ["tier_id", "section", "text"],
}
REQUIRED_PAGE_KEYS = [
    "page_title", "header_title", "header_intro", "disclaimer", "notice", "button_label",
    "result_label", "why_title", "why_intro", "whatnow_title", "implications_title",
    "actions_title", "cta", "addon_view_label", "regulation_cite", "footer",
]
SECTIONS = ["implications", "actions"]
ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")

errors = []


# --- Reading the workbook (plain .xlsx = zip of XML files) -------------------

def col_index(ref):
    n = 0
    for ch in re.match(r"[A-Z]+", ref).group(0):
        n = n * 26 + ord(ch) - 64
    return n - 1


def text_of(node):
    """Text of a <si> or <is> node: plain <t> plus rich-text runs <r><t>."""
    if node is None:
        return ""
    parts = [t.text or "" for t in node.findall(M + "t")]
    parts += [t.text or "" for t in node.findall(M + "r/" + M + "t")]
    return "".join(parts)


def read_workbook(path):
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        shared = []
        if "xl/sharedStrings.xml" in names:
            shared = [text_of(si) for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(M + "si")]

        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        targets = {r.get("Id"): r.get("Target") for r in rels.iter(PR + "Relationship")}
        sheets = {}
        for sheet in ET.fromstring(z.read("xl/workbook.xml")).iter(M + "sheet"):
            target = targets[sheet.get(R_ID)]
            target = target.lstrip("/") if target.startswith("/") else "xl/" + target
            rows = []
            for row in ET.fromstring(z.read(target)).iter(M + "row"):
                cells = {}
                for c in row.findall(M + "c"):
                    kind, v = c.get("t"), c.find(M + "v")
                    if kind == "s":
                        val = shared[int(v.text)]
                    elif kind == "inlineStr":
                        val = text_of(c.find(M + "is"))
                    elif kind == "b":
                        val = "TRUE" if v is not None and v.text == "1" else "FALSE"
                    else:
                        val = v.text if v is not None and v.text is not None else ""
                    cells[col_index(c.get("r"))] = val
                width = max(cells) + 1 if cells else 0
                rows.append((int(row.get("r")), [cells.get(i, "") for i in range(width)]))
            sheets[sheet.get("name")] = rows
    return sheets


def table(sheets, name):
    """Rows of a sheet as dicts keyed by the header row; blank rows skipped."""
    if name not in sheets:
        errors.append(f'Sheet "{name}" is missing.')
        return []
    rows = sheets[name]
    if not rows:
        errors.append(f'Sheet "{name}" is empty.')
        return []
    header = [h.strip().lower() for h in rows[0][1]]
    missing = [c for c in REQUIRED_COLUMNS[name] if c not in header]
    if missing:
        errors.append(f'Sheet "{name}": missing column(s) {", ".join(missing)}.')
        return []
    out = []
    for rownum, values in rows[1:]:
        rec = {h: (values[i].strip() if i < len(values) else "") for i, h in enumerate(header) if h}
        if any(rec.values()):
            rec["_where"] = f"{name}!row {rownum}"
            out.append(rec)
    return out


# --- Text formatting ------------------------------------------------------------

def markup(text, links, where):
    """Escape, then apply the small markup documented in the README sheet:
    **bold**, *italic*, [label](link_id or https://url), line breaks."""
    s = html.escape(text, quote=False)

    def link(m):
        label, target = m.group(1), m.group(2)
        if re.match(r"^(https?://|mailto:)", target):
            url = target
        elif target in links:
            url = links[target]
        else:
            errors.append(f'{where}: unknown link id "{target}" (add it to the "links" sheet).')
            url = "#"
        return f'<a href="{html.escape(url)}" target="_blank" rel="noopener">{label}</a>'

    s = LINK_RE.sub(link, s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![*\w])\*(?!\s)([^*]+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", s)
    return s.replace("\n", "<br>")


def plain(text):
    return html.escape(text, quote=False)


def is_enabled(value):
    return value.strip().upper() not in ("FALSE", "0", "NO", "N")


# --- Build ----------------------------------------------------------------------

def build(xlsx, template_path, out_path):
    sheets = read_workbook(xlsx)

    links = {}
    for r in table(sheets, "links"):
        if not ID_RE.match(r["link_id"]):
            errors.append(f'{r["_where"]}: invalid link_id "{r["link_id"]}".')
        elif not re.match(r"^(https?://|mailto:)", r["url"]):
            errors.append(f'{r["_where"]}: url must start with https:// or mailto:.')
        links[r["link_id"]] = r["url"]

    page = {r["key"]: r for r in table(sheets, "page")}
    for key in REQUIRED_PAGE_KEYS:
        if key not in page or (not page[key]["value"] and key != "notice"):
            errors.append(f'Sheet "page": key "{key}" is missing or empty.')
    if errors:
        return fail()

    page_html = {k: markup(page[k]["value"], links, page[k]["_where"]) for k in REQUIRED_PAGE_KEYS}

    def P(key):
        return page_html[key]

    tiers, tier_index = [], {}
    for r in table(sheets, "tiers"):
        w = r["_where"]
        if not ID_RE.match(r["tier_id"]) or r["tier_id"] == "addon":
            errors.append(f'{w}: invalid tier_id "{r["tier_id"]}".')
        for c in ("color", "color_dark"):
            if not COLOR_RE.match(r[c]):
                errors.append(f'{w}: {c} must look like #1a2b3c.')
        if not r["headline"]:
            errors.append(f"{w}: headline is empty.")
        tier_index[r["tier_id"]] = len(tiers)
        tiers.append({
            "id": r["tier_id"],
            "headline": r["headline"],
            "implications": [],
            "actions": [],
            "fallback": {
                "cite": plain(page["regulation_cite"]["value"] + ", " + r["fallback_provision"]),
                "text": plain(r["fallback_verbatim"]),
            },
            "_colors": (r["color"], r["color_dark"]),
        })
    if not tiers:
        errors.append('Sheet "tiers" has no tiers.')
        return fail()
    if not tiers[-1]["fallback"]["text"]:
        errors.append(f'Sheet "tiers": the last tier ("{tiers[-1]["id"]}") is the default result '
                      "and needs fallback_provision and fallback_verbatim.")

    for r in table(sheets, "tier_details"):
        w = r["_where"]
        if r["tier_id"] not in tier_index:
            errors.append(f'{w}: unknown tier_id "{r["tier_id"]}".')
        elif r["section"] not in SECTIONS:
            errors.append(f'{w}: section must be one of {", ".join(SECTIONS)}.')
        elif r["text"]:
            tiers[tier_index[r["tier_id"]]][r["section"]].append(markup(r["text"], links, w))

    questions = []
    for r in table(sheets, "questions"):
        if not ID_RE.match(r["question_id"]):
            errors.append(f'{r["_where"]}: invalid question_id "{r["question_id"]}".')
        questions.append(r)
    qids = [q["question_id"] for q in questions]
    if len(set(qids)) != len(qids):
        errors.append('Sheet "questions": question_id values must be unique.')

    options = {q: {} for q in qids}
    option_rows = {q: [] for q in qids}
    for r in table(sheets, "options"):
        w = r["_where"]
        if not is_enabled(r["enabled"]):
            print(f'  skipped (enabled = FALSE): {r["question_id"]} / {r["option_id"]}')
            continue
        q, oid, effect = r["question_id"], r["option_id"], r["effect"]
        if q not in options:
            errors.append(f'{w}: unknown question_id "{q}".')
            continue
        if not re.match(r"^[A-Za-z0-9_-]+$", oid):
            errors.append(f'{w}: invalid option_id "{oid}".')
        if oid in options[q]:
            errors.append(f'{w}: duplicate option_id "{oid}" in question "{q}".')
        if not r["label"]:
            errors.append(f"{w}: label is empty.")
        if effect and effect != "addon" and effect not in tier_index:
            errors.append(f'{w}: effect "{effect}" is not a tier_id, "addon" or blank.')
        if effect and (not r["provision"] or not r["verbatim"]):
            errors.append(f"{w}: options with an effect need provision and verbatim.")
        if effect == "addon" and not r["note"]:
            errors.append(f"{w}: addon options need a note.")
        if not option_rows[q] and effect:
            errors.append(f'{w}: the first option of "{q}" is the default answer and must have no effect.')
        option_rows[q].append(r)
        if effect:
            opt = {
                "effect": effect,
                "cite": plain(page["regulation_cite"]["value"] + ", " + r["provision"]),
                "text": plain(r["verbatim"]),
            }
            if effect == "addon":
                opt["note"] = markup(r["note"], links, w)
                opt["view"] = plain(page["addon_view_label"]["value"].replace("{provision}", r["provision"]))
            options[q][oid] = opt
    for q in qids:
        if not option_rows[q]:
            errors.append(f'Question "{q}" has no enabled options.')

    if errors:
        return fail()

    # Static HTML pieces
    fieldsets = []
    for n, q in enumerate(questions, 1):
        opts = "\n".join(
            f'      <option value="{html.escape(o["option_id"])}">{plain(o["label"])}</option>'
            for o in option_rows[q["question_id"]])
        hint = f'\n    <p class="hint">{markup(q["hint"], links, q["_where"])}</p>' if q["hint"] else ""
        fieldsets.append(
            f'  <fieldset>\n    <legend>{n}. {markup(q["title"], links, q["_where"])}</legend>{hint}\n'
            f'    <select id="{q["question_id"]}">\n{opts}\n    </select>\n  </fieldset>\n')

    tier_css = "\n".join(
        f'.risk-banner[data-tier="{t["id"]}"] {{ background: linear-gradient(135deg, {t["_colors"][0]}, {t["_colors"][1]}); }}'
        for t in tiers)
    for t in tiers:
        del t["_colors"]

    content = {
        "questions": qids,
        "options": options,
        "tiers": tiers,
        "labels": {k: P(k) for k in ("result_label", "why_title", "why_intro", "whatnow_title",
                                     "implications_title", "actions_title", "cta")},
    }
    content_json = json.dumps(content, ensure_ascii=False, indent=1).replace("</", "<\\/")
    notice = page["notice"]["value"]

    values = {
        "generated_comment": "<!-- GENERATED by build.py from content.xlsx + template.html. "
                             "Do not edit by hand: edit content.xlsx and run `python3 build.py`. -->",
        "page_title": plain(page["page_title"]["value"]),
        "tier_css": tier_css,
        "header_title": P("header_title"),
        "header_intro": P("header_intro"),
        "disclaimer": P("disclaimer"),
        "notice_block": f'\n<div class="notice">\n  {P("notice")}\n</div>\n' if notice else "",
        "questions": "\n".join(fieldsets),
        "button_label": P("button_label"),
        "footer": P("footer"),
        "content_json": content_json,
    }
    out = Path(template_path).read_text(encoding="utf-8")
    for key, val in values.items():
        out = out.replace("{{" + key + "}}", val)
    leftover = re.findall(r"\{\{\w+\}\}", out)
    if leftover:
        errors.append(f"template.html has unknown placeholder(s): {', '.join(sorted(set(leftover)))}")
        return fail()

    Path(out_path).write_text(out, encoding="utf-8")
    n_opts = sum(len(v) for v in option_rows.values())
    print(f"Built {out_path}: {len(questions)} questions, {n_opts} options, {len(tiers)} tiers.")
    return 0


def fail():
    print("Build failed — fix these in content.xlsx:", file=sys.stderr)
    for e in errors:
        print("  - " + e, file=sys.stderr)
    return 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--xlsx", default=HERE / "content.xlsx")
    ap.add_argument("--template", default=HERE / "template.html")
    ap.add_argument("--out", default=HERE / "index.html")
    a = ap.parse_args()
    sys.exit(build(a.xlsx, a.template, a.out))
