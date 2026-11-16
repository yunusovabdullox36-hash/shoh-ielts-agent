---
name: find-skills
description: Find a reviewed skill for a teacher's next task.
---

# Find skills

Use `find_shoh_skill` with a short Uzbek or English description when the task does not already have a clear matching skill. The helper returns installed reviewed workflows, not executable capabilities. Load the selected workflow with `skill_view` and check the actual tool list before promising its output.

When `ambiguous` is true, compare the requested output to the candidate descriptions. Combine workflows when appropriate, such as a marketing brief followed by a media script. Ask the owner only if the deliverable itself is ambiguous. A `no_match` result means this lexical catalog did not match; inspect the installed skill list or answer the supported part directly. Do not install a remote skill or claim a nonexistent tool to fill the gap. Operator reference: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills.
