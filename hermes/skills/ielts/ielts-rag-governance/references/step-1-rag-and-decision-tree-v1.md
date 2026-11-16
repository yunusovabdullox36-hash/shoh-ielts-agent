# IELTSSHOKH Step 1 — RAG and Decision Tree v1

**Status:** completed governance and routing layer; corpus ingestion awaits approved source files.

## Scope

This first step establishes the source contract, retrieval guardrails, and request-routing rules. It does not publish content, connect external services, or claim that an unprovided internal fact exists.

## RAG v1 architecture

```text
Approved source
  → source inventory record
  → focused passages + metadata
  → status/validity/authority filters
  → retrieval of relevant passages
  → answer or draft with source reference and confidence
```

### Required source inventory fields

| Field | Meaning |
|---|---|
| `id` | Stable ID, e.g. `course-prices-2026-01` |
| `title` | Human-readable source name |
| `source_ref` | Backend record ID, document path, post ID or official URL |
| `owner` | Decision owner or originating organization |
| `subject` | `course`, `channel`, `brand`, `writing`, `reading`, `speaking`, `listening`, `marketing`, `team` |
| `authority` | `owner_approved`, `official_internal`, `official_public`, `approved_historical`, `unverified` |
| `status` | `active`, `archived`, `draft`, `needs_review` |
| `reviewed_at` | Date last verified |
| `valid_until` | Expiry date, if applicable |
| `access` | `internal`, `owner_only`, `public` |

### Passage rule

Split by self-contained meaning, such as one policy, one offer, one FAQ answer, or one lesson procedure. Keep the heading, source ID, date and status alongside each passage. Do not use a passage that crosses unrelated sections because it creates unsupported answers.

### Retrieval rule

1. Filter out `archived`, `draft`, expired, and unauthorized sources.
2. Prefer `owner_approved` and current `official_internal` sources.
3. Retrieve only the small set that directly answers the request.
4. Check scope, date and conflict before response.
5. If no confirmed passage exists, return a blocker rather than inferred facts.

## Decision Tree v1

```text
REQUEST
│
├─ Is it simple conversation or general study help with no specific claim?
│   └─ Yes → answer directly.
│
├─ Does it need an IELTSSHOKH fact, policy, offer, brand rule, or old decision?
│   └─ Yes → RAG retrieve.
│       ├─ Confirmed and current evidence found → answer/draft with confidence.
│       ├─ Evidence conflicts or is stale → surface conflict; request owner decision.
│       └─ No evidence → state unavailable; do not guess.
│
├─ Is it a public IELTS fact or current external information?
│   └─ Yes → retrieve primary official public source and cite it.
│
├─ Is it a learning material task with a provided source?
│   └─ Yes → preserve supplied material, build and QA artifact.
│
├─ Is it a channel draft?
│   └─ Yes → retrieve brand/claim evidence → draft → owner review.
│
└─ Does it write externally (publish, send, edit CRM, upload, delete)?
    └─ Yes → require exact approved revision and transport receipt.
```

## Output states

| State | Meaning | Required response behavior |
|---|---|---|
| `confirmed` | Active, authoritative and in-scope evidence exists | Use it and identify evidence internally. |
| `supported` | Relevant public or historical evidence exists but is not an owner decision | Qualify it; do not treat as policy. |
| `needs_review` | Conflict, expiry, missing approval or unclear scope | State the gap and seek a source/decision. |
| `blocked_action` | External change lacks exact approval | Keep as a draft; do not perform the action. |

## Acceptance tests

1. A stale price record cannot answer a current price question.
2. A draft post cannot become brand policy merely because it is retrieved.
3. Two conflicting approved records are shown as a conflict, not merged.
4. A public IELTS rule is sourced from a primary official page.
5. A channel post is produced as a draft and is not published without exact-revision approval.
6. Any answer based on corpus evidence can name its source record and confidence state.

## RAG-Anything assessment

RAG-Anything is a multimodal document-RAG framework built on LightRAG. Its documented strengths are extracting and retrieving text, images, tables, equations, audio and video with graph-plus-vector retrieval. It is **not part of RAG v1** because the initial IELTSSHOKH corpus has not yet been supplied and v1 needs only trusted, source-aware knowledge records.

Evaluate it only for a later multimodal phase when we have a real need to search scanned PDFs, chart-heavy materials, video lessons, or large mixed-format archives. Before adoption, run a bounded test corpus, pin Python/dependency versions, choose a private storage location, estimate model/OCR cost, inspect extracted text and tables, and test retrieval against this document's acceptance tests. Its project currently declares a Python 3.10+ dependency base and its default MinerU parser is constrained to Python 3.10–3.13; its own issue tracker includes ingestion-status failure reports, so a successful install alone is not sufficient evidence of reliable indexing.

Sources reviewed: https://github.com/hkuds/rag-anything ; https://github.com/hkuds/rag-anything/blob/main/pyproject.toml ; https://github.com/hkuds/rag-anything/issues/328
