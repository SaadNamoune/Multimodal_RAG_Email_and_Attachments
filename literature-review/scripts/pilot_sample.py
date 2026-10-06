"""Draw the pilot screening sample and write it as RIS, for import into Rayyan.

Usage (from literature-review/):
  python scripts/pilot_sample.py exports/arxiv/2026-10-06 exports/acl/2026-10-06

Takes 20 records found by S1, 15 by S2 and 15 by S3, at random with a fixed seed,
among the records loaded into Zotero. Writes screening/pilot-50.ris and
screening/pilot-50.json (the keys drawn, per stratum).
"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STRATA = [("search:S1", 20), ("search:S2", 15), ("search:S3", 15)]
SEED = 20261006


def ris(rec):
    is_arxiv = "arxiv_id" in rec
    kind = "UNPB" if is_arxiv else ("CONF" if rec["item"]["itemType"] == "conferencePaper" else "JOUR")
    lines = [f"TY  - {kind}", f"ID  - {rec['key']}", f"TI  - {rec['title']}"]
    for name in rec["authors"]:
        first, _, last = name.rpartition(" ")
        lines.append(f"AU  - {last}, {first}" if first else f"AU  - {last}")
    lines += [f"PY  - {rec['year']}", f"AB  - {rec['abstract']}", f"UR  - {rec['url']}"]
    lines += [f"KW  - {tag}" for tag in rec["tags"] if tag.startswith(("search:", "db:"))]
    return "\n".join(lines + ["ER  - ", ""])


def main():
    pool = []
    for run_dir in sys.argv[1:]:
        for rec in json.loads((Path(run_dir) / "records.json").read_text(encoding="utf-8")):
            if "duplicate_of" in rec or not any(t.startswith("search:") for t in rec["tags"]):
                continue
            rec.setdefault("key", f"arxiv:{rec.get('arxiv_id')}")
            rec.setdefault("year", rec.get("published", "")[:4])
            pool.append(rec)
    pool.sort(key=lambda rec: rec["key"])

    rng = random.Random(SEED)
    drawn, taken = {}, set()
    for tag, size in STRATA:
        candidates = [rec for rec in pool if tag in rec["tags"] and rec["key"] not in taken]
        drawn[tag] = rng.sample(candidates, size)
        taken.update(rec["key"] for rec in drawn[tag])

    out = ROOT / "screening"
    out.mkdir(exist_ok=True)
    sample = [rec for recs in drawn.values() for rec in recs]
    (out / "pilot-50.ris").write_text("\n".join(ris(rec) for rec in sample), encoding="utf-8")
    (out / "pilot-50.json").write_text(json.dumps(
        {"seed": SEED, "pool": len(pool), "strata": {tag: [rec["key"] for rec in recs] for tag, recs in drawn.items()}},
        indent=1), encoding="utf-8")
    print(f"{len(sample)} records drawn from a pool of {len(pool)} -> {out / 'pilot-50.ris'}")


if __name__ == "__main__":
    main()
