"""Find records that describe a paper already found in another database."""
import json
import re
import unicodedata
from pathlib import Path


def norm(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", text.lower())


def surnames(rec):
    return {norm(name.split()[-1]) for name in rec["authors"] if name.split()}


def mark_duplicates(records, other_paths):
    """Set rec["duplicate_of"] where an earlier run has the same title and an author in common."""
    known = {}
    for path in other_paths:
        for rec in json.loads(Path(path).read_text(encoding="utf-8")):
            if any(t.startswith("search:") for t in rec["tags"]) and "duplicate_of" not in rec:
                known.setdefault(norm(rec["title"]), []).append(rec)
    duplicates = []
    for rec in records:
        for earlier in known.get(norm(rec["title"]), []):
            if surnames(rec) & surnames(earlier):
                rec["duplicate_of"] = earlier.get("key") or f"arxiv:{earlier['arxiv_id']}"
                duplicates.append({"record": rec["key"], "duplicate_of": rec["duplicate_of"], "title": rec["title"]})
                break
    return duplicates
