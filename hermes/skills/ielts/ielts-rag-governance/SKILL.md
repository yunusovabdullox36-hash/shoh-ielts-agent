---
name: ielts-rag-governance
description: "Use when retrieving IELTS knowledge. Require evidence."
version: 1.0.0
author: IELTSSHOKH
license: Internal
metadata:
  hermes:
    tags: [rag, knowledge-base, retrieval, sources, approval]
    related_skills: [channel-decision-tree, memory-management, ielts-design-quality]
---

# IELTSSHOKH RAG governance

## When to Use

Use this skill when a request depends on IELTSSHOKH facts, channel policy, brand decisions, course information, approved learning material, or past approved content.

## 1. Keep authority separated

- Treat owner-approved decisions, dated official documents, and approved knowledge records as authoritative because RAG must retrieve evidence rather than amplify guesses.
- Treat drafts, old posts, public web pages, and unverified messages as evidence with a stated confidence level because they may be stale or wrong.
- Do not turn a retrieved passage into a permanent policy without owner review because retrieval is not approval.

## 2. Use this source hierarchy

1. Owner-approved policy, brand decision, price, schedule, course or team record.
2. Current official IELTSSHOKH document or backend record with review date.
3. Official public authority for public facts such as IELTS policy.
4. Approved historical channel post, marked as historical.
5. Unverified draft or public reference, marked `needs_review`.

If competing sources disagree, prefer the newer higher-authority source and show the conflict rather than silently combining them.

## 3. Store each knowledge record with compact metadata

```text
id: stable identifier
text: smallest self-contained passage
source: owner | internal_document | official_public | approved_post | draft
source_ref: document path, post ID, or public URL
subject: writing | reading | speaking | listening | course | channel | marketing | team | brand
status: active | archived | draft | needs_review
approved_by: owner name or null
reviewed_at: YYYY-MM-DD or null
valid_until: YYYY-MM-DD or null
confidence: confirmed | supported | unverified
```

Do not index secrets, credentials, private learner data, or payment data because RAG retrieval can expose indexed text in unrelated replies.

## 4. Retrieve before answering

1. Classify the request: factual answer, learning explanation, channel draft, internal decision, or action request.
2. Filter by subject, `active` status, validity date, and source authority.
3. Retrieve the smallest relevant passages, not an entire document, because focused evidence reduces hallucination and stale context.
4. Check the evidence answers the exact question, including date, audience, and scope.
5. Respond from retrieved evidence. If it is absent or conflicting, name the gap and request an owner decision or authoritative source.

## 5. Route through the decision tree

| Request type | RAG outcome | Next route |
|---|---|---|
| Simple conversation | No retrieval unless a specific IELTS fact is claimed | Direct answer |
| Learning material | Retrieve approved pedagogy or supplied source | Build and QA material |
| Channel draft | Retrieve active brand voice, audience and claims | Draft for owner review |
| Price, schedule, offer, teacher, policy | Require current confirmed record | Answer or flag as unavailable |
| Public IELTS fact | Retrieve official public source | Cite evidence |
| Publication or external write | Retrieve exact approved draft revision | Backend approval and receipt |

## 6. Output contract

For knowledge-dependent work, state only what matters:

```text
Evidence used: <source refs or “none available”>
Confidence: confirmed | supported | needs review
Result: <answer, draft, or blocker>
```

Never claim a draft was published, an action occurred, or a fact is current without the required backend receipt or source evidence.

## Initial corpus checklist

Start the knowledge base with these owner-reviewed collections:

- channel profile, audience, voice, rubrics, CTA and publishing policy;
- courses, offers, prices, schedules, instructors and FAQs;
- approved IELTS teaching methodology and reusable lesson formats;
- approved marketing claims, testimonials and evidence;
- brand kit: logo, colors, type, templates, visual do/don't rules;
- team SOPs and approval responsibilities.

Mark anything missing, date-sensitive, or unverified as `needs_review` instead of using it as active knowledge.
