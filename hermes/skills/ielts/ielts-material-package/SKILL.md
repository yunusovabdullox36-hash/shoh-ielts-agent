---
name: ielts-material-package
description: Use when producing study packs. Build and QA assets.
license: Proprietary
metadata:
  version: 1.0.0
  author: Channel owner and Hermes
  hermes:
    tags: [ielts, reading, writing, pdf, html]
    related_skills: [ieltsshokh-html, channel-decision-tree, memory-management]
---

# IELTS material package workflow

## When to Use

Use when the owner provides IELTS Reading or Writing source materials and asks for an interactive study artifact, question paper, answer analysis, or a coordinated asset pack.

## Default owner delivery rules

- Treat the supplied question paper, answer key, reference HTML and model-answer PDFs as evidence for the requested material. Inspect every available artifact before drafting.
- For **Reading**, deliver three coordinated assets: an interactive IELTSSHOKH HTML test, a questions-only PDF, and an answers-and-analysis PDF. The analysis must give the answer, an exact passage quote, the question-to-passage paraphrase and a concise reason.
- For **Writing**, deliver an interactive IELTSSHOKH HTML test and a questions-only PDF. Do not put model answers in the Writing PDF unless the owner explicitly overrides this rule; keep teacher-reviewed model answers and the practice toolkit in the interactive HTML.
- For **Listening**, wait for the owner’s separate delivery specification before setting a default package.

## HTML standards

- Use the `ieltsshokh-html` skill and its builder for each Writing or Reading HTML. Preserve source prompts and passage wording verbatim.
- Use the shared IELTSSHOKH skin and offline embedded visuals. Include the appropriate exam timer, fullscreen entry from a user gesture, mobile layout, autosave and review flow.
- In Reading, validate every answer against an exact marked passage excerpt; distinguish contradiction from missing information in FALSE/NOT GIVEN and NO/NOT GIVEN questions.
- In Writing, embed the exact Task 1 image supplied by the owner and preserve the attribution. If it is unavailable, ask the teacher to resend it. A separate explicitly requested redraw may be prepared as a derivative, but the exam HTML uses the original. Include teacher-reviewed models and reusable phrases.

## Context and chunking discipline

- Create a compact source ledger before drafting: test title/date, exact Task 1 and Task 2 prompts, original image-cache path, supplied question/answer files, and unresolved gaps. Keep these source facts intact across long tasks.
- Inspect long PDFs in pages. Extract the source verbatim into the structured builder payload rather than relying on a summary of an earlier page.
- When a builder payload reaches a field limit, reduce duplicated explanation text first. Never drop source prompts, passage wording, answer keys, evidence quotes, question numbering or original-image paths.
- If a full Reading test still cannot fit after compacting duplicate text, stop and report the builder limit before splitting it; do not silently turn a full test into an incomplete artifact.
- Treat a failed upload or an unavailable cache path as a file-availability problem, not as missing owner intent.

## QA before delivery

- Verify questions, word limits, numbering, answer options and answer keys against the supplied files.
- State which source files were checked and name any missing or unclear material.
- Run the builder and report its lint result before attaching the HTML.
- Do not claim a PDF was created unless a PDF-generation tool produced and verified it. Keep drafts in the owner conversation until publication approval exists.
