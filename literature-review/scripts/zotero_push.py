"""Send records from a search run to the Zotero desktop app, which must be running.

Usage (from literature-review/):
  python scripts/zotero_push.py exports/arxiv/2026-10-06 "FrAInderl-RAG-Review" seed search:S0 search:S1
  python scripts/zotero_push.py exports/acl/2026-10-06 "FrAInderl-RAG-Review" db:acl

Sends every record that carries at least one of the given tags, plus the hand-entered
references in seeds.json when "seed" is given. Records marked as duplicates of another
database's records are left out. The named library must be the one
selected in the Zotero window; items land in it, or in the collection selected inside
it. zotero-pushed.json remembers what was sent to each library, so nothing is sent
twice.
"""
import json
import sys
import urllib.request
import uuid
from pathlib import Path

ZOTERO = "http://127.0.0.1:23119/connector/"
ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "zotero-pushed.json"
BATCH = 50


def call(endpoint, payload):
    req = urllib.request.Request(
        ZOTERO + endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "X-Zotero-Connector-API-Version": "3"},
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        return resp.status, json.loads(resp.read() or b"null")


def to_item(rec):
    creators = []
    for name in rec["authors"]:
        first, _, last = name.rpartition(" ")
        if first:
            creators.append({"firstName": first, "lastName": last, "creatorType": "author"})
        else:
            creators.append({"lastName": last, "fieldMode": 1, "creatorType": "author"})
    extra = []
    if rec.get("journal_ref"):
        extra.append(f"Journal reference on arXiv: {rec['journal_ref']}")
    if rec.get("cited_as"):
        extra.append(f"Proposal reference [{rec['seed_ref']}], cited as: {rec['cited_as']}")
    item = {
        "itemType": "preprint",
        "title": rec["title"],
        "creators": creators,
        "abstractNote": rec["abstract"],
        "date": rec["published"],
        "repository": "arXiv",
        "archiveID": f"arXiv:{rec['arxiv_id']}",
        "url": rec["url"],
        "libraryCatalog": "arXiv.org",
        "extra": "\n".join(extra),
        "tags": [{"tag": t} for t in rec["tags"]],
        "notes": [],
        "attachments": [],
    }
    if rec.get("doi"):
        item["DOI"] = rec["doi"]
    return item


def check_selected(library):
    _, target = call("getSelectedCollection", {})
    if target["libraryName"] != library or not target["editable"]:
        sys.exit(f'Select the library "{library}" in Zotero first (selected now: "{target["libraryName"]}")')
    return target


def main():
    run_dir, library, wanted = Path(sys.argv[1]), sys.argv[2], set(sys.argv[3:])
    target = check_selected(library)
    ledger = json.loads(LEDGER.read_text(encoding="utf-8")) if LEDGER.exists() else {}
    pushed = set(ledger.get(library, []))

    queue, duplicates = [], 0
    for rec in json.loads((run_dir / "records.json").read_text(encoding="utf-8")):
        key = rec.get("key") or f"arxiv:{rec['arxiv_id']}"
        if not wanted & set(rec["tags"]) or key in pushed:
            continue
        if "duplicate_of" in rec:  # same paper already loaded from another database
            duplicates += 1
            continue
        item = dict(rec["item"], tags=[{"tag": t} for t in rec["tags"]]) if "item" in rec else to_item(rec)
        queue.append((key, item))
    if duplicates:
        print(f"{duplicates} records skipped: marked as duplicates of another database's records")
    if "seed" in wanted:
        for seed in json.loads((ROOT / "seeds.json").read_text(encoding="utf-8")):
            key = f"ref:{seed['ref']}"
            if "item" in seed and key not in pushed:
                item = dict(seed["item"], tags=[{"tag": "seed"}], notes=[], attachments=[])
                item["extra"] = "\n".join(filter(None, [item.get("extra"), f"Proposal reference [{seed['ref']}]"]))
                queue.append((key, item))

    print(f"Zotero target: {target['libraryName']} / {target['name']} - {len(queue)} items to send")

    for i in range(0, len(queue), BATCH):
        batch = queue[i:i + BATCH]
        items = [dict(item, id=key) for key, item in batch]
        check_selected(library)  # the selection can change in the Zotero window between batches
        status, _ = call("saveItems", {"sessionID": uuid.uuid4().hex, "uri": "https://arxiv.org/", "items": items})
        pushed.update(key for key, _ in batch)
        ledger[library] = sorted(pushed)
        LEDGER.write_text(json.dumps(ledger, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"  sent {i + len(batch)}/{len(queue)} (HTTP {status})")


if __name__ == "__main__":
    main()
