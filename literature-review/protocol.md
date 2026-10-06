# Literature review protocol — draft v0.1

**Project:** Multimodal RAG for Enterprise Email and Attachments (PFE 3358)
**Reviewers:** Saad Namoune, Chourouk Chaker · **Supervisor:** Ekaterina Mashina
**Date:** 2026-10-06 · **Status:** draft for discussion on 2026-10-08

Everything below is a proposal. Points marked **[decide]** are collected in section 8.

## 1. Review type and reporting standard

Proposed: a **scoping review**, reported with PRISMA-ScR (Tricco et al., 2018), with the search reported as PRISMA-S asks and the PRISMA 2020 flow diagram in its "databases, registers and other sources" version. **[decide]**

Reason: the project spans four sub-areas with different kinds of studies, and the aim is to map what exists and document a gap, not to pool results. The PRISMA 2020 items on risk of bias, effect measures and certainty of evidence do not apply and will be marked as such.

## 2. Review questions

| | Question | Thesis RQ |
|---|---|---|
| LQ1 | Which datasets and benchmarks exist for RAG over email or other enterprise data, and what do they annotate (threads, metadata, attachments, duplicates, conflicts)? | RQ4 |
| LQ2 | How do RAG systems represent the links between a message, its attachments, its thread and its metadata? | RQ2 |
| LQ3 | How are duplicates, redundancy and knowledge conflicts, especially temporal ones, detected, resolved and evaluated in RAG? | RQ1 |
| LQ4 | How are images and visually rich documents integrated into RAG (multimodal embedding, OCR, captioning, fusion), and how do the options compare? | RQ3 |

## 3. Eligibility criteria

| | Include | Exclude |
|---|---|---|
| Period | Published or posted from 2020-01-01, the year RAG was introduced | Earlier work, except as background |
| Language | English | Other languages |
| Type | Peer-reviewed papers and arXiv preprints **[decide]** | Abstracts, posters, tutorials, papers under 4 pages |
| Topic | Addresses at least one of LQ1–LQ4 | Email classification (spam, phishing, routing) without retrieval-augmented generation; security or privacy attacks on RAG where email is only the example |
| Evidence | Presents a system, dataset, benchmark or empirical evaluation | No evaluation |
| Versions | The published version when one exists | The preprint of a paper that was later published |

Surveys are kept for citation searching and are not charted.

Why preprints are proposed: in the arXiv run of S1, 228 of 270 records were submitted in 2025 or 2026, and 9 of the proposal's 24 references are arXiv-only.

## 4. Information sources

| Source | Why | Access | Status |
|---|---|---|---|
| arXiv | Preprints; most of this field appears here first | Open API | Run on 2026-10-06 |
| Scopus | Broad index of peer-reviewed venues | Institutional **[decide]** | To run |
| IEEE Xplore | IEEE conferences and journals | Search is open, by hand only | Not run; reached through OpenAlex |
| ACM Digital Library | SIGIR, CIKM, KDD and other ACM venues | Search is open, by hand only | Not run; reached through OpenAlex |
| OpenAlex | Open index of scholarly works, including IEEE and ACM publications | Open API | Run on 2026-10-06 for IEEE- and ACM-published papers **[decide]** |
| ACL Anthology | ACL, EMNLP, NAACL, COLING | Open, but no Boolean search | Run on 2026-10-06 by script; method to confirm **[decide]** |
| Other methods | The 24 references of the proposal; backward and forward citation searching from included papers | — | References loaded |

For the ACL Anthology, the proposal is to filter its full bibliography file (`anthology+abstracts.bib.gz`, which includes abstracts) with the same concept blocks by script, so the search is reproducible. A first run on 2026-10-06 gave 273 unique records, 174 of which are also in the arXiv results.

IEEE Xplore and the ACM Digital Library cannot be queried by script. A first run on 2026-10-06 reached their publications through OpenAlex instead, by DOI prefix: 1,034 unique records, 190 of which are also in the arXiv results. OpenAlex has no abstract for 64 of them, so its recall is lower than a search in the two databases themselves.

## 5. Search strategy

Concept blocks, searched in title and abstract (and keywords where the database has them):

| Block | Terms |
|---|---|
| RAG | "retrieval augmented" OR RAG |
| CONTEXT | email\* OR e-mail\* OR mailbox OR inbox OR enterprise OR "company-internal" OR workplace |
| EMAIL | email\* OR e-mail\* |
| HYGIENE | "knowledge conflict\*" OR "conflicting evidence" OR deduplication OR "near-duplicate" OR redundancy OR outdated OR superseded |
| MODALITY | multimodal OR "multi-modal" OR "visual document" OR OCR |
| ATTACHMENT | attachment\* OR multimodal OR "multi-modal" |

| ID | String | Serves |
|---|---|---|
| S1 | RAG AND CONTEXT | LQ1, LQ2 |
| S2 | RAG AND HYGIENE | LQ3 |
| S3 | RAG AND MODALITY | LQ4 |
| S0 | RAG AND EMAIL AND ATTACHMENT | Gap check: expected to be nearly empty |

The strings are adapted to each database's syntax, and each adapted string is written into `search-log.md` exactly as run, with the date, limits and hit count.

**Validation against known papers.** 21 of the proposal's 24 references are indexed on arXiv. The strings retrieve 14 of them. The 7 they miss are background or method papers:

- [1] RAG, [6] Ragnarök and [15] RAGAS are general RAG works with no topic term.
- [7] training-data deduplication, [9] CLIP, [22] ConflictBank and [23] fusion functions are not RAG papers.

These seven enter through "other methods". Whether LQ3 needs a second string without the RAG block, to catch work like ConflictBank, is open. **[decide]**

## 6. Selection process

1. All records go into the Zotero group library FrAInderl-RAG-Review. Duplicates are removed and the number removed is logged.
2. Both reviewers screen titles and abstracts independently against section 3. A pilot on 50 records, drawn at random across S1 to S3, calibrates the criteria first. Agreement is reported as Cohen's kappa. Disagreements are settled by discussion, then by the supervisor.
3. Full texts of the remaining reports are assessed, and one exclusion reason is recorded for each report excluded.

Tool for blind dual screening: Rayyan, or separate tag prefixes per reviewer in Zotero. **[decide]**

## 7. Data charting

One row per included paper: reference, year and venue; review question(s) addressed; data type (email, enterprise, documents); modalities; dataset or benchmark used or introduced; method; metrics; main result; limitations; relevance to the thesis RQs.

## 8. Open decisions for 2026-10-08

1. Scoping review (PRISMA-ScR) or full systematic review?
2. Are arXiv preprints eligible?
3. Is the 2020 start date acceptable?
4. Which subscription databases can THD give access to (Scopus, Web of Science)?
5. How should the ACL Anthology be searched?
6. Is OpenAlex acceptable for reaching IEEE and ACM publications, or must IEEE Xplore and the ACM Digital Library be searched directly?
7. S3 accounts for 1,573 of the 2,555 unique records so far. Narrow it, or keep it broad although RQ3 is a stretch goal?
8. Does LQ3 need a string without the RAG block?
9. Which screening tool, and who arbitrates disagreements?
