---
name: memory-management
description: Maintain channel knowledge and Hermes memory with source-aware updates.
---

# Memory management

## Use when

The owner gives a durable channel preference, approves a policy decision, or asks to record a verified lesson.

## Procedure

1. Identify the target store.
   - Hermes memory (`memory` tool) holds compact verified preferences and durable operational lessons, for example "owner wants Reading answer keys at the end".
   - `knowledge/` holds reviewed channel profile, audience, brand voice and owner decisions. Shoh reads it with `search_channel_knowledge` but cannot edit it. For a new policy decision, return a proposed row for `decisions.md` for the operator to add.
   - Full drafts, learner data, task state and credentials never go into memory.
2. Check the source, date, scope and confidence.
3. Save the smallest durable fact with the `memory` tool, including scope and source/date where material. Check the result; do not assume a failed write persisted. If the tool is missing or fails, return the compact proposed record and say it was not saved. Do not use `skill_manage` as a substitute memory store.
4. Preserve the evidence reference and review date for a policy or strategic conclusion.
5. Saved memory is loaded into new sessions; the current session may keep its earlier prompt. Do not claim Obsidian access or automatic model learning.

## Error handling

Do not persist an unsupported analysis result as knowledge. If authority or evidence is missing, keep it in the current task result as a proposal for owner review.
