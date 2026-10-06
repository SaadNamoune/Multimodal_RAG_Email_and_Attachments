"""Run the review's search strings against OpenAlex, for papers published by IEEE and ACM.

Usage (from literature-review/):
  python scripts/openalex_search.py exports/arxiv/2026-10-06/records.json exports/acl/2026-10-06/records.json

OpenAlex (https://openalex.org) is an open index of scholarly works. This run reaches
IEEE and ACM publications through it, by DOI prefix, because IEEE Xplore and the ACM
Digital Library cannot be queried by script. It is a search of OpenAlex, not of those
two databases: OpenAlex has no abstract for some papers, and those match on title only.

The arguments are records.json files of earlier runs; a record with the same title and
an author in common is marked as a duplicate of the earlier one.

Writes to exports/openalex/<run date>/:
  raw/*.json     API responses exactly as received
  run.json       query strings, limits, hit counts, duplicates
  records.json   one record per paper, tagged, ready for zotero_push.py
"""
import datetime as dt
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from dedup import mark_duplicates
from search_blocks import BLOCKS, FROM_YEAR, SEARCHES

API = "https://api.openalex.org/works"
ROOT = Path(__file__).resolve().parent.parent
PUBLISHERS = {"ieee": "10.1109", "acm": "10.1145"}  # DOI prefixes
SELECT = ("id,doi,title,publication_date,publication_year,type,language,authorships,"
          "primary_location,biblio,abstract_inverted_index")
PAGE = 200
PAUSE = 1.2  # OpenAlex allows one long Boolean query per second without an API key


def build_query(block_names):
    return " AND ".join("(" + " OR ".join(BLOCKS[name]) + ")" for name in block_names)


def fetch(params, dest):
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "pfe-literature-review/0.1"})
    for _ in range(6):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = resp.read()
        except urllib.error.HTTPError as err:
            if err.code != 429:
                raise
            time.sleep(float(err.headers.get("Retry-After", 1)) + 1)
            continue
        dest.write_bytes(body)
        time.sleep(PAUSE)
        return json.loads(body)
    raise RuntimeError(f"no usable response after retries: {url}")


def clean(text):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", "", text or "")).split())


def abstract_of(work):
    index = work.get("abstract_inverted_index") or {}
    words = sorted((pos, word) for word, positions in index.items() for pos in positions)
    return clean(" ".join(word for _, word in words))


def to_record(work):
    doi = work["doi"].removeprefix("https://doi.org/").lower()
    source = (work.get("primary_location") or {}).get("source") or {}
    biblio = work.get("biblio") or {}
    authors = [clean(a["author"]["display_name"]) for a in work.get("authorships", [])]
    creators = []
    for name in authors:
        first, _, last = name.rpartition(" ")
        if first:
            creators.append({"firstName": first, "lastName": last, "creatorType": "author"})
        else:
            creators.append({"lastName": last, "fieldMode": 1, "creatorType": "author"})
    is_journal = source.get("type") == "journal"
    pages = "-".join(filter(None, [biblio.get("first_page"), biblio.get("last_page")]))
    item = {
        "itemType": "journalArticle" if is_journal else "conferencePaper",
        "title": clean(work["title"]),
        "creators": creators,
        "abstractNote": abstract_of(work),
        "date": work.get("publication_date") or str(work["publication_year"]),
        "publicationTitle" if is_journal else "proceedingsTitle": clean(source.get("display_name")),
        "volume": biblio.get("volume") or "",
        "pages": pages,
        "DOI": doi,
        "url": work["doi"],
        "language": work.get("language") or "",
        "libraryCatalog": "OpenAlex",
        "extra": "OpenAlex: " + work["id"].rsplit("/", 1)[-1],
        "notes": [],
        "attachments": [],
    }
    if is_journal:
        item["issue"] = biblio.get("issue") or ""
    return {
        "key": f"doi:{doi}",
        "title": item["title"],
        "authors": authors,
        "abstract": item["abstractNote"],
        "year": str(work["publication_year"]),
        "url": work["doi"],
        "tags": [],
        "item": {k: v for k, v in item.items() if v != ""},
    }


def main():
    today = dt.date.today().isoformat()
    out = ROOT / "exports" / "openalex" / today
    (out / "raw").mkdir(parents=True, exist_ok=True)

    records = {}
    run = {
        "database": "OpenAlex",
        "interface": API,
        "run_date": today,
        "fields": "title, abstract (title_and_abstract.search)",
        "limits": f"from_publication_date {FROM_YEAR}-01-01; DOI prefix 10.1109 (IEEE) or 10.1145 (ACM)",
        "searches": {},
    }
    for sid, block_names in SEARCHES.items():
        query = build_query(block_names)
        for publisher, prefix in PUBLISHERS.items():
            flt = (f"title_and_abstract.search:{query},from_publication_date:{FROM_YEAR}-01-01,"
                   f"doi_starts_with:{prefix}")
            cursor, page, total, found = "*", 0, None, {}
            while cursor:
                data = fetch({"filter": flt, "per-page": PAGE, "cursor": cursor, "select": SELECT},
                             out / "raw" / f"{sid}_{publisher}_{page:02d}.json")
                total = data["meta"]["count"]
                for work in data["results"]:
                    rec = to_record(work)
                    found[rec["key"]] = rec
                cursor = data["meta"].get("next_cursor") if data["results"] else None
                page += 1
            for key, rec in found.items():
                tags = records.setdefault(key, rec)["tags"]
                tags += [t for t in (f"search:{sid}", f"publisher:{publisher}") if t not in tags]
            run["searches"][f"{sid}/{publisher}"] = {"blocks": block_names, "filter": flt,
                                                     "hits_reported": total, "records_retrieved": len(found)}
            print(f"{sid} {publisher}: {total} hits reported, {len(found)} records retrieved")

    for rec in records.values():
        rec["tags"] += ["db:openalex", f"run:{today}"]
    duplicates = mark_duplicates(records.values(), sys.argv[1:])
    run["unique_records"] = len(records)
    run["without_abstract"] = sum(1 for rec in records.values() if not rec["abstract"])
    run["compared_with"] = sys.argv[1:]
    run["duplicates_of_other_databases"] = duplicates

    (out / "run.json").write_text(json.dumps(run, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "records.json").write_text(
        json.dumps(list(records.values()), indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"unique records: {len(records)} ({run['without_abstract']} have no abstract in OpenAlex)")
    print(f"already found in another database: {len(duplicates)}")
    print(f"written to {out}")


if __name__ == "__main__":
    main()
