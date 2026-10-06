"""Run the review's search strings against the arXiv API and store the results.

Usage (from literature-review/):  python scripts/arxiv_search.py

Writes to exports/arxiv/<run date>/:
  raw/*.xml      API responses exactly as received
  run.json       query strings, limits, hit counts, seed check
  records.json   one record per arXiv ID, tagged with every search that found it
"""
import datetime as dt
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from search_blocks import BLOCKS, FROM_YEAR, SEARCHES

API = "https://export.arxiv.org/api/query"
ROOT = Path(__file__).resolve().parent.parent
PAGE = 200
PAUSE = 3  # seconds between calls, as the arXiv API terms of use ask
FROM = f"{FROM_YEAR}01010000"

NS = {
    "a": "http://www.w3.org/2005/Atom",
    "os": "http://a9.com/-/spec/opensearch/1.1/",
    "x": "http://arxiv.org/schemas/atom",
}


def build_query(block_names, until):
    parts = []
    for name in block_names:
        parts.append("(" + " OR ".join(f"ti:{t} OR abs:{t}" for t in BLOCKS[name]) + ")")
    return " AND ".join(parts) + f" AND submittedDate:[{FROM} TO {until}]"


def fetch(params, dest):
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "pfe-literature-review/0.1"})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = resp.read()
        except urllib.error.HTTPError as err:
            # arXiv throttles with 429/503: wait and try again
            if err.code not in (429, 503):
                raise
            time.sleep(PAUSE * 5 * (attempt + 1))
            continue
        feed = ET.fromstring(body)
        total = int(feed.findtext("os:totalResults", namespaces=NS))
        entries = feed.findall("a:entry", NS)
        # arXiv sometimes answers a valid request with an empty page: retry
        if entries or params.get("start", 0) >= total:
            dest.write_bytes(body)
            return total, entries
        time.sleep(PAUSE * (attempt + 2))
    raise RuntimeError(f"no usable response after retries: {url}")


def clean(text):
    return " ".join((text or "").split())


def parse(entry):
    raw_id = entry.findtext("a:id", namespaces=NS)
    if "/abs/" not in raw_id:
        raise RuntimeError(f"arXiv API error: {clean(entry.findtext('a:summary', namespaces=NS))}")
    arxiv_id = re.sub(r"v\d+$", "", raw_id.split("/abs/")[1])
    return {
        "arxiv_id": arxiv_id,
        "title": clean(entry.findtext("a:title", namespaces=NS)),
        "authors": [clean(a.findtext("a:name", namespaces=NS)) for a in entry.findall("a:author", NS)],
        "abstract": clean(entry.findtext("a:summary", namespaces=NS)),
        "published": entry.findtext("a:published", namespaces=NS)[:10],
        "primary_category": entry.find("x:primary_category", NS).get("term"),
        "doi": entry.findtext("x:doi", namespaces=NS),
        "journal_ref": clean(entry.findtext("x:journal_ref", namespaces=NS)) or None,
        "url": f"https://arxiv.org/abs/{arxiv_id}",
        "tags": [],
    }


def main():
    today = dt.date.today()
    until = today.strftime("%Y%m%d") + "2359"
    out = ROOT / "exports" / "arxiv" / today.isoformat()
    (out / "raw").mkdir(parents=True, exist_ok=True)

    records = {}
    run = {
        "database": "arXiv",
        "interface": API,
        "run_date": today.isoformat(),
        "fields": "title, abstract",
        "limits": f"submittedDate {FROM} to {until} (GMT)",
        "searches": {},
    }

    for sid, block_names in SEARCHES.items():
        query = build_query(block_names, until)
        start, total, found = 0, None, {}
        while total is None or start < total:
            params = {"search_query": query, "start": start, "max_results": PAGE,
                      "sortBy": "submittedDate", "sortOrder": "ascending"}
            total, entries = fetch(params, out / "raw" / f"{sid}_{start:05d}.xml")
            for entry in entries:
                rec = parse(entry)
                found[rec["arxiv_id"]] = rec
            start += PAGE
            time.sleep(PAUSE)
        for arxiv_id, rec in found.items():
            records.setdefault(arxiv_id, rec)["tags"].append(f"search:{sid}")
        run["searches"][sid] = {"blocks": block_names, "query": query,
                                "hits_reported": total, "records_retrieved": len(found)}
        print(f"{sid}: {total} hits reported, {len(found)} records retrieved")

    for rec in records.values():
        rec["tags"] += ["db:arxiv", f"run:{today.isoformat()}"]
    run["unique_records"] = len(records)

    # Seed check: which of the proposal's references does each search find?
    seeds = [s for s in json.loads((ROOT / "seeds.json").read_text(encoding="utf-8")) if "arxiv" in s]
    _, entries = fetch({"id_list": ",".join(s["arxiv"] for s in seeds), "max_results": len(seeds)},
                       out / "raw" / "seeds.xml")
    fetched = {rec["arxiv_id"]: rec for rec in map(parse, entries)}
    run["seed_check"] = []
    for seed in seeds:
        rec = records.setdefault(seed["arxiv"], fetched[seed["arxiv"]])
        found_by = [t for t in rec["tags"] if t.startswith("search:")]
        rec["tags"].append("seed")
        rec["seed_ref"], rec["cited_as"] = seed["ref"], seed["cited_as"]
        run["seed_check"].append({"ref": seed["ref"], "arxiv_id": seed["arxiv"],
                                  "title": rec["title"], "found_by": found_by})
    hit = sum(1 for s in run["seed_check"] if s["found_by"])
    print(f"unique records across searches: {run['unique_records']}")
    print(f"seed check: {hit} of {len(seeds)} arXiv-indexed proposal references found by at least one search")

    (out / "run.json").write_text(json.dumps(run, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "records.json").write_text(
        json.dumps(list(records.values()), indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"written to {out}")


if __name__ == "__main__":
    main()
