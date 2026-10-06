"""Apply the review's search strings to the ACL Anthology bibliography and store the results.

Usage (from literature-review/):
  python scripts/acl_filter.py exports/acl/2026-10-06/anthology+abstracts.bib.gz exports/arxiv/2026-10-06/records.json

The first argument is the file published at https://aclanthology.org/anthology+abstracts.bib.gz.
Any further arguments are records.json files from other databases: an ACL record with
the same title and an author in common is marked as a duplicate of the earlier one.

Matching is on title and abstract: case-insensitive, whole words, hyphen and space
treated alike, optional plural "s". Only @inproceedings and @article entries from
FROM_YEAR on are considered.

Writes next to the input file:
  S0.bib ... S3.bib   matching entries, copied unchanged from the source
  run.json            source file, matching rules, hit counts, duplicates
  records.json        one record per paper, tagged, ready for zotero_push.py
"""
import datetime as dt
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

from pylatexenc.latex2text import LatexNodes2Text

from dedup import mark_duplicates
from search_blocks import BLOCKS, FROM_YEAR, SEARCHES

ENTRY_START = re.compile(r"^@(\w+)\{(.*),\s*$")
FIELD = re.compile(r"^    (\w+) = ", re.M)
LATEX = LatexNodes2Text(keep_comments=True)


def term_regex(term):
    tokens = re.split(r"[-\s]+", term.strip('"'))
    return r"\b" + r"[-\s]+".join(map(re.escape, tokens)) + r"s?\b"


BLOCK_RE = {name: re.compile("|".join(term_regex(t) for t in terms), re.I)
            for name, terms in BLOCKS.items()}


def entries(path):
    """Yield (type, bibkey, raw text) for every entry of the file."""
    kind = key = None
    lines = []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            start = ENTRY_START.match(line)
            if start:
                kind, key, lines = start.group(1).lower(), start.group(2), [line]
            elif kind:
                lines.append(line)
                if line.rstrip() == "}":
                    yield kind, key, "".join(lines)
                    kind = None


def parse_fields(raw):
    body = raw.split("\n", 1)[1].rsplit("}", 1)[0]
    parts = FIELD.split(body)
    fields = {}
    for name, value in zip(parts[1::2], parts[2::2]):
        value = value.strip().rstrip(",").strip()
        if value[:1] in '"{':
            value = value[1:-1]
        fields[name.lower()] = value
    return fields


def decode(value):
    try:
        text = LATEX.latex_to_text(value)
    except Exception:
        text = value.replace("{", "").replace("}", "")
    return " ".join(text.split())


def to_record(kind, key, fields):
    names = [decode(n) for n in re.split(r"\s+and\s+", fields.get("author", "")) if n.strip()]
    creators, authors = [], []
    for name in names:
        last, _, first = (part.strip() for part in name.partition(","))
        authors.append(f"{first} {last}".strip())
        if first:
            creators.append({"firstName": first, "lastName": last, "creatorType": "author"})
        else:
            creators.append({"lastName": last, "fieldMode": 1, "creatorType": "author"})
    url = fields.get("url", "")
    item = {
        "itemType": "conferencePaper" if kind == "inproceedings" else "journalArticle",
        "title": decode(fields["title"]),
        "creators": creators,
        "abstractNote": decode(fields.get("abstract", "")),
        "date": " ".join(filter(None, [fields.get("month", "").capitalize(), fields["year"]])),
        "pages": fields.get("pages", "").replace("--", "-"),
        "DOI": fields.get("doi", ""),
        "url": url,
        "libraryCatalog": "ACL Anthology",
        "notes": [],
        "attachments": [],
    }
    if kind == "inproceedings":
        item["proceedingsTitle"] = decode(fields.get("booktitle", ""))
        item["publisher"] = decode(fields.get("publisher", ""))
        item["place"] = decode(fields.get("address", ""))
    else:
        item["publicationTitle"] = decode(fields.get("journal", ""))
        item["volume"] = fields.get("volume", "")
        item["issue"] = fields.get("number", "")
    return {
        "key": "acl:" + url.rstrip("/").rsplit("/", 1)[-1],
        "bibkey": key,
        "title": item["title"],
        "authors": authors,
        "abstract": item["abstractNote"],
        "year": fields["year"],
        "url": url,
        "tags": [],
        "item": {k: v for k, v in item.items() if v != ""},
    }


def main():
    source = Path(sys.argv[1])
    out = source.parent
    today = dt.date.today().isoformat()

    hits = {sid: [] for sid in SEARCHES}
    records = {}
    considered = without_abstract = 0
    for kind, key, raw in entries(source):
        if kind not in ("inproceedings", "article"):
            continue
        fields = parse_fields(raw)
        if int(fields["year"]) < FROM_YEAR:
            continue
        considered += 1
        text = (fields["title"] + "\n" + fields.get("abstract", "")).replace("{", "").replace("}", "")
        if not BLOCK_RE["RAG"].search(text):
            continue
        matched = [sid for sid, blocks in SEARCHES.items() if all(BLOCK_RE[b].search(text) for b in blocks)]
        if not matched:
            continue
        rec = to_record(kind, key, fields)
        rec["tags"] = [f"search:{sid}" for sid in matched] + ["db:acl", f"run:{today}"]
        records[rec["key"]] = rec
        without_abstract += "abstract" not in fields
        for sid in matched:
            hits[sid].append(raw)

    duplicates = mark_duplicates(records.values(), sys.argv[2:])

    for sid, raws in hits.items():
        (out / f"{sid}.bib").write_text("".join(raws), encoding="utf-8")
        print(f"{sid}: {len(raws)} hits")
    run = {
        "database": "ACL Anthology",
        "interface": "local filter of anthology+abstracts.bib.gz (scripts/acl_filter.py)",
        "run_date": today,
        "source_file": source.name,
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "fields": "title, abstract",
        "limits": f"year >= {FROM_YEAR}; entry types inproceedings, article",
        "matching": "case-insensitive, whole words, hyphen and space alike, optional plural s",
        "entries_considered": considered,
        "searches": {sid: {"blocks": SEARCHES[sid], "hits": len(raws)} for sid, raws in hits.items()},
        "unique_records": len(records),
        "matched_on_title_only": without_abstract,
        "compared_with": sys.argv[2:],
        "duplicates_of_other_databases": duplicates,
    }
    (out / "run.json").write_text(json.dumps(run, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "records.json").write_text(
        json.dumps(list(records.values()), indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"unique records: {len(records)} ({without_abstract} have no abstract in the source)")
    print(f"already found in another database: {len(duplicates)}")
    print(f"written to {out}")


if __name__ == "__main__":
    main()
