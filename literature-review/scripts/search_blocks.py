"""Concept blocks and search strings shared by every search script (protocol.md, section 5)."""

FROM_YEAR = 2020  # eligibility window starts in 2020

# Plural forms are spelled out because not every search interface stems or has wildcards.
BLOCKS = {
    "RAG": ['"retrieval augmented"', "RAG"],
    "CONTEXT": ["email", "emails", '"e-mail"', '"e-mails"', "mailbox", "inbox",
                "enterprise", '"company-internal"', "workplace"],
    "EMAIL": ["email", "emails", '"e-mail"', '"e-mails"'],
    "HYGIENE": ['"knowledge conflict"', '"knowledge conflicts"', '"conflicting evidence"',
                "deduplication", '"near-duplicate"', "redundancy", "outdated", "superseded"],
    "MODALITY": ["multimodal", '"multi-modal"', '"visual document"', "OCR"],
    "ATTACHMENT": ["attachment", "attachments", "multimodal", '"multi-modal"'],
}
SEARCHES = {
    "S0": ["RAG", "EMAIL", "ATTACHMENT"],  # gap check: expected to be near-empty
    "S1": ["RAG", "CONTEXT"],
    "S2": ["RAG", "HYGIENE"],
    "S3": ["RAG", "MODALITY"],
}
