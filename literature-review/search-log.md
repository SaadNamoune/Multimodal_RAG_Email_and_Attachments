# Search log

One row per search run. Add a row every time a string is run in a database, and paste the string exactly as it was run in the section below.

| Date | Database | Interface | ID | Fields | Limits | Hits | Export | Run by |
|---|---|---|---|---|---|---|---|---|
| 2026-10-06 | arXiv | API, `export.arxiv.org/api/query` | S0 | title, abstract | submitted 2020-01-01 to 2026-10-06 | 3 | `exports/arxiv/2026-10-06/raw/S0_*.xml` | Saad, `scripts/arxiv_search.py` |
| 2026-10-06 | arXiv | API | S1 | title, abstract | same | 270 | `…/raw/S1_*.xml` | same |
| 2026-10-06 | arXiv | API | S2 | title, abstract | same | 474 | `…/raw/S2_*.xml` | same |
| 2026-10-06 | arXiv | API | S3 | title, abstract | same | 945 | `…/raw/S3_*.xml` | same |
| 2026-10-06 | ACL Anthology | Local filter of `anthology+abstracts.bib.gz` (file dated 2026-10-05) | S0 | title, abstract | year 2020 or later; conference papers and journal articles | 1 | `exports/acl/2026-10-06/S0.bib` | Saad, `scripts/acl_filter.py` |
| 2026-10-06 | ACL Anthology | Local filter | S1 | title, abstract | same | 40 | `…/S1.bib` | same |
| 2026-10-06 | ACL Anthology | Local filter | S2 | title, abstract | same | 90 | `…/S2.bib` | same |
| 2026-10-06 | ACL Anthology | Local filter | S3 | title, abstract | same | 151 | `…/S3.bib` | same |
| 2026-10-06 | OpenAlex, IEEE- and ACM-published papers | API, `api.openalex.org/works` | S0 | title, abstract | published 2020-01-01 or later; DOI prefix 10.1109 (IEEE) or 10.1145 (ACM) | IEEE 1 · ACM 1 | `exports/openalex/2026-10-06/raw/S0_*.json` | Saad, `scripts/openalex_search.py` |
| 2026-10-06 | OpenAlex, IEEE and ACM | API | S1 | title, abstract | same | IEEE 176 · ACM 54 | `…/raw/S1_*.json` | same |
| 2026-10-06 | OpenAlex, IEEE and ACM | API | S2 | title, abstract | same | IEEE 91 · ACM 51 | `…/raw/S2_*.json` | same |
| 2026-10-06 | OpenAlex, IEEE and ACM | API | S3 | title, abstract | same | IEEE 508 · ACM 195 | `…/raw/S3_*.json` | same |

## Totals so far

| | Records |
|---|---|
| Identified on arXiv (four strings) | 1,692 |
| Identified in the ACL Anthology (four strings) | 282 |
| Identified in OpenAlex, IEEE- and ACM-published (four strings) | 1,077 |
| **Identified in total** | **3,051** |
| Duplicates removed (table at the end) | 496 |
| **Unique records to screen** | **2,555** |

Not run: Scopus, and IEEE Xplore and the ACM Digital Library themselves. IEEE and ACM publications were reached through OpenAlex instead; the limits of that are in the notes on the OpenAlex run.

## Strings exactly as run

### arXiv, 2026-10-06

S0
```
(ti:"retrieval augmented" OR abs:"retrieval augmented" OR ti:RAG OR abs:RAG) AND (ti:email OR abs:email OR ti:emails OR abs:emails OR ti:"e-mail" OR abs:"e-mail" OR ti:"e-mails" OR abs:"e-mails") AND (ti:attachment OR abs:attachment OR ti:attachments OR abs:attachments OR ti:multimodal OR abs:multimodal OR ti:"multi-modal" OR abs:"multi-modal") AND submittedDate:[202001010000 TO 202610062359]
```

S1
```
(ti:"retrieval augmented" OR abs:"retrieval augmented" OR ti:RAG OR abs:RAG) AND (ti:email OR abs:email OR ti:emails OR abs:emails OR ti:"e-mail" OR abs:"e-mail" OR ti:"e-mails" OR abs:"e-mails" OR ti:mailbox OR abs:mailbox OR ti:inbox OR abs:inbox OR ti:enterprise OR abs:enterprise OR ti:"company-internal" OR abs:"company-internal" OR ti:workplace OR abs:workplace) AND submittedDate:[202001010000 TO 202610062359]
```

S2
```
(ti:"retrieval augmented" OR abs:"retrieval augmented" OR ti:RAG OR abs:RAG) AND (ti:"knowledge conflict" OR abs:"knowledge conflict" OR ti:"knowledge conflicts" OR abs:"knowledge conflicts" OR ti:"conflicting evidence" OR abs:"conflicting evidence" OR ti:deduplication OR abs:deduplication OR ti:"near-duplicate" OR abs:"near-duplicate" OR ti:redundancy OR abs:redundancy OR ti:outdated OR abs:outdated OR ti:superseded OR abs:superseded) AND submittedDate:[202001010000 TO 202610062359]
```

S3
```
(ti:"retrieval augmented" OR abs:"retrieval augmented" OR ti:RAG OR abs:RAG) AND (ti:multimodal OR abs:multimodal OR ti:"multi-modal" OR abs:"multi-modal" OR ti:"visual document" OR abs:"visual document" OR ti:OCR OR abs:OCR) AND submittedDate:[202001010000 TO 202610062359]
```

### ACL Anthology, 2026-10-06

The Anthology has no Boolean search, so its full bibliography file was filtered locally with the same blocks. The terms of each block are those of `scripts/search_blocks.py`, identical to the arXiv strings above.

```
S0 = RAG AND EMAIL AND ATTACHMENT
S1 = RAG AND CONTEXT
S2 = RAG AND HYGIENE
S3 = RAG AND MODALITY
```

- **Source file:** `https://aclanthology.org/anthology+abstracts.bib.gz`, last modified 2026-10-05, 131,647 entries, SHA-256 `d9620aa9651f86bfb5177b3825adda20b18621239a696062d15c8befb1c7573e`.
- **Entries considered:** 68,810 conference papers and journal articles dated 2020 or later.
- **Matching rule:** a term matches in the title or abstract, case-insensitive, as whole words, with hyphen and space treated alike and an optional plural "s".

### OpenAlex, 2026-10-06

Each string was run twice, once per DOI prefix, as the `filter` parameter:

```
title_and_abstract.search:<string>,from_publication_date:2020-01-01,doi_starts_with:10.1109
title_and_abstract.search:<string>,from_publication_date:2020-01-01,doi_starts_with:10.1145
```

S0
```
("retrieval augmented" OR RAG) AND (email OR emails OR "e-mail" OR "e-mails") AND (attachment OR attachments OR multimodal OR "multi-modal")
```

S1
```
("retrieval augmented" OR RAG) AND (email OR emails OR "e-mail" OR "e-mails" OR mailbox OR inbox OR enterprise OR "company-internal" OR workplace)
```

S2
```
("retrieval augmented" OR RAG) AND ("knowledge conflict" OR "knowledge conflicts" OR "conflicting evidence" OR deduplication OR "near-duplicate" OR redundancy OR outdated OR superseded)
```

S3
```
("retrieval augmented" OR RAG) AND (multimodal OR "multi-modal" OR "visual document" OR OCR)
```

## Notes on the arXiv run

- **Seed check.** 14 of the 21 proposal references indexed on arXiv are retrieved by at least one string. Not retrieved: [1], [6], [7], [9], [15], [22], [23]. Details per reference are in `run.json`.
- **S1 by submission year.** 2021: 1 · 2023: 1 · 2024: 40 · 2025: 94 · 2026: 134.
- **Categories.** 1,583 of the 1,612 unique records have a `cs.*` primary category. The other 29 should be checked at screening for other meanings of the acronym RAG.
- **Gap check (S0).** Three records: arXiv 2504.13209, 2509.11937 (MMORE) and 2603.01990 (ATM-Bench).

## Notes on the ACL Anthology run

- **Unique records.** 273 across the four strings. Two of them have no abstract in the source and were matched on the title alone.
- **By year.** 2021: 2 · 2022: 3 · 2023: 5 · 2024: 42 · 2025: 114 · 2026: 107.
- **Overlap with arXiv.** 174 of the 273 have the same title and at least one author in common with a record of the arXiv run. They are listed in `exports/acl/2026-10-06/run.json`.
- **Gap check (S0).** One record: `2026.lanlp-1.6` (mCS-LM), not on arXiv.

## Notes on the OpenAlex run

- **What this run is.** A search of OpenAlex, an open index of scholarly works, limited to DOIs registered by IEEE and ACM. It is not a search of IEEE Xplore or of the ACM Digital Library, which cannot be queried by script.
- **Unique records.** 1,034 across the four strings: 749 published by IEEE and 285 by ACM.
- **Missing abstracts.** 64 of the 1,034 have no abstract in OpenAlex (56 IEEE, 8 ACM) and matched on the title alone. Papers whose abstract is missing in OpenAlex and whose title lacks the terms are not retrieved; their number is unknown.
- **One DOI indexed twice.** For S3 on ACM, OpenAlex returns 195 works, two of which carry the same DOI (`10.1145/3811238.3811871`). They count as one record.
- **By year.** 2021: 1 · 2022: 2 · 2023: 7 · 2024: 95 · 2025: 530 · 2026: 399.
- **Overlap.** 190 of the 1,034 have the same title and at least one author in common with an arXiv record. They are listed in `exports/openalex/2026-10-06/run.json`.
- **Non-papers.** About a dozen records are editorials, conference abstracts, reviews or front matter, to exclude at screening.
- **Gap check (S0).** Two records: `10.1109/ickecs70176.2026.11528041` (AutoMeet) and `10.1145/3805712.3808647`.

## Loaded into Zotero

The shared library for the review is the Zotero group **FrAInderl-RAG-Review**.

| Date | What | Records | Tags |
|---|---|---|---|
| 2026-10-06 | arXiv S0 and S1 | 270 | `search:S0`, `search:S1`, `db:arxiv`, `run:2026-10-06` |
| 2026-10-06 | Proposal references | 24, of which 5 are also in S1 | `seed` |
| 2026-10-06 | arXiv S2 and S3 | 1,333 new | `search:S2`, `search:S3`, `db:arxiv`, `run:2026-10-06` |
| 2026-10-06 | ACL Anthology S0 to S3 | 99 new | `search:S0` to `search:S3`, `db:acl`, `run:2026-10-06` |
| 2026-10-06 | OpenAlex S0 to S3, IEEE and ACM | 844 new | `search:S0` to `search:S3`, `db:openalex`, `publisher:ieee` or `publisher:acm`, `run:2026-10-06` |

- **Total loaded by script:** 2,565 items. That is the 2,555 unique records, plus the 10 proposal references that no string retrieves.
- **OpenAlex:** the 190 records that duplicate an arXiv record were not loaded. For those papers the arXiv record is the one in Zotero, and the published metadata is in `exports/openalex/2026-10-06/records.json`.
- **arXiv S2 and S3:** 1,342 unique records lie outside S1. Nine of them were already in the library as proposal references, so 1,333 were added.
- **ACL Anthology:** the 174 records that duplicate an arXiv record were not loaded. For those papers the arXiv record is the one in Zotero, and the published metadata is in `exports/acl/2026-10-06/records.json`.
- **Not from a logged search:** 30 items saved by hand on 2026-10-06 are also in the library. They need a row in this log, or they count as "other methods".
- **First copy:** the first 289 records were also loaded into the personal library "Ma bibliothèque" on the same day. That copy is not the working one.

## Duplicates removed

| Date | Step | Removed | Remaining |
|---|---|---|---|
| 2026-10-06 | Same arXiv ID across S0–S3, by script | 80 | 1,612 arXiv records |
| 2026-10-06 | Same Anthology ID across S0–S3, by script | 9 | 273 ACL records |
| 2026-10-06 | ACL record with the same title and an author in common with an arXiv record, by script | 174 | 99 ACL records, 1,711 in total |
| 2026-10-06 | Same DOI within the OpenAlex run (across strings, plus one DOI indexed twice), by script | 43 | 1,034 OpenAlex records |
| 2026-10-06 | OpenAlex record with the same title and an author in common with an arXiv or ACL record, by script | 190 | 844 OpenAlex records, 2,555 in total |

Duplicates whose title changed between preprint and publication are not caught by this rule. They remain to be found in Zotero or Rayyan.

## Pilot screening sample

Drawn on 2026-10-06 by `scripts/pilot_sample.py` from the 1,711 unique arXiv and ACL records, before the OpenAlex run, at random with seed 20261006: 20 records found by S1, 15 by S2 and 15 by S3. The file to import into Rayyan is `screening/pilot-50.ris`; the keys drawn are in `screening/pilot-50.json`.
