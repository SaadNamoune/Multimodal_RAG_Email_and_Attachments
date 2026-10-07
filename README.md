# Multimodal RAG for Enterprise Email and Attachments

Thesis project (PFE 3358) on retrieval-augmented generation (RAG) over enterprise email: messages, their threads and metadata, and their attachments, including images and visually rich documents.

**Authors:** Saad Namoune, Chourouk Chaker · **Supervisor:** Ekaterina Mashina

The repository currently holds the literature review. The system itself is not in the repository yet.

## Literature review

`literature-review/` is a scoping review, reported with PRISMA-ScR. It answers four questions:

| | Question | Thesis RQ |
|---|---|---|
| LQ1 | Which datasets and benchmarks exist for RAG over email or other enterprise data? | RQ4 |
| LQ2 | How do RAG systems represent the links between a message, its attachments, its thread and its metadata? | RQ2 |
| LQ3 | How are duplicates, redundancy and knowledge conflicts detected, resolved and evaluated in RAG? | RQ1 |
| LQ4 | How are images and visually rich documents integrated into RAG? | RQ3 |

| Path | Contents |
|---|---|
| `protocol.md` | Review protocol: questions, eligibility criteria, sources, search strategy, selection and charting. Rendered as `protocol.pdf`. |
| `search-log.md` | Every search exactly as run, with date, limits and hit count, plus totals and duplicates removed. Rendered as `search-log.pdf`. |
| `seeds.json` | The proposal's 24 references, used to check that the searches find known papers. |
| `scripts/` | The search, deduplication, Zotero and screening scripts (below). |
| `exports/<database>/<date>/` | Raw API responses (`raw/`), `run.json` (queries, counts, duplicates) and `records.json` (one tagged record per paper). |
| `screening/` | The 50-record pilot sample, as RIS for Rayyan and as JSON. |
| `zotero-pushed.json` | Records already sent to each Zotero library, so nothing is sent twice. |

### Status (2026-10-06)

The search has been run on arXiv, the ACL Anthology, and IEEE and ACM papers reached through OpenAlex. It found 3,051 records. After 496 duplicates were removed, 2,555 unique records remain to screen. They are loaded in the Zotero group library **FrAInderl-RAG-Review**. Scopus has not been run yet. The open decisions are listed in section 8 of `protocol.md`.

## Running the scripts

Python 3. Run everything from `literature-review/`:

```bash
cd literature-review
pip install -r requirements.txt
```

| Step | Command |
|---|---|
| Search arXiv | `python scripts/arxiv_search.py` |
| Filter the ACL Anthology | `python scripts/acl_filter.py exports/acl/<date>/anthology+abstracts.bib.gz exports/arxiv/<date>/records.json` |
| Search OpenAlex (IEEE, ACM) | `python scripts/openalex_search.py exports/arxiv/<date>/records.json exports/acl/<date>/records.json` |
| Send to Zotero | `python scripts/zotero_push.py exports/<database>/<date> "FrAInderl-RAG-Review" <tags...>` |
| Draw the pilot sample | `python scripts/pilot_sample.py exports/arxiv/<date> exports/acl/<date>` |
| Render Markdown to PDF | `python scripts/md_to_pdf.py protocol.md search-log.md` |

The search terms are defined once, in `scripts/search_blocks.py`, and every search script uses them.

- **ACL filter:** download `https://aclanthology.org/anthology+abstracts.bib.gz` first. Git does not track this file because it is 42 MB; its date and SHA-256 are in `run.json`.
- **`zotero_push.py`:** the Zotero desktop app must be running, with the target library selected.
- **`md_to_pdf.py`:** expects Chrome at its default Windows path.
