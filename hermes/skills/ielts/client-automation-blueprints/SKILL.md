---
name: client-automation-blueprints
description: "Use when scoping Composio or n8n client workflows."
version: 1.0.0
author: IELTSSHOKH
license: Internal
metadata:
  hermes:
    tags: [composio, n8n, mcp, workflow, automation]
    related_skills: [client-integration-boundaries, channel-decision-tree, channel-analysis]
---

# Client automation blueprints

## When to Use

Use when preparing, testing or implementing a client-owned Composio or n8n automation. Apply `client-integration-boundaries` first.

## Platform routing

- Use **Composio** when an agent needs a small, named set of actions across several client SaaS accounts because it can discover tools and prompt the client for OAuth only when needed.
- Use **n8n** only when the owner explicitly chooses it for a durable multi-step workflow because it adds triggers, scheduling, transformations, logs, retries, approval gates and webhooks; it is not part of the current default stack.
- Use a direct official API or focused MCP when one service is the only target because a narrower connection reduces scope and risk.
- Do not enable both platforms merely for convenience because duplicated automation creates inconsistent data and hard-to-debug side effects.

## Portable blueprints

### A. RAG source intake

```text
Client-owned Drive/Notion folder
→ read-only source allowlist
→ document inventory
→ extract focused passages + metadata
→ needs_review queue
→ owner approval
→ active RAG corpus
```

**Composio role:** client OAuth and document discovery/read actions.
**n8n role:** scheduled delta checks, retries, inventory logs and review notifications.
**Forbidden:** indexing every accessible document or any credential/private data.

### B. Telegram channel analyst

```text
Client-authorized metric source/export
→ post + metric validation
→ immutable raw snapshot
→ metric calculations at fixed time windows
→ evidence-based weekly report
→ one experiment proposal
→ owner approval
```

**n8n role:** scheduled capture/import, storage and report delivery.
**Composio role:** only if a required analytics, spreadsheet or reporting SaaS needs client OAuth.
**Forbidden:** claiming unavailable Telegram metrics, publishing automatically, or mixing client channel data.

### C. Draft-to-approval-to-publish

```text
Brief
→ RAG-supported draft
→ owner review
→ exact approved revision ID
→ scheduled publish request
→ transport receipt
→ post record and later metric snapshot
```

**n8n role:** schedule, approval state and receipt handling.
**Composio role:** client-owned destination only when a reviewed toolkit supplies the needed action.
**Forbidden:** using a generic write tool before exact-draft approval.

### D. Lead and enquiry triage

```text
Client form or inbox
→ consent + required-field validation
→ classify intent
→ assign owner
→ draft response or create CRM record
→ human approval for outbound reply where required
→ auditable outcome
```

**Forbidden:** autonomous sales promises, payment actions or adding personal data to RAG.

## Composio configuration contract

For every client toolkit, document:

```text
client_id: stable client namespace
provider/toolkit: exact slug
purpose: named workflow only
auth owner: client
allowed tools: explicit allowlist
scopes: minimum required
mode: sandbox | production
read/write boundary: explicit
approval for writes: required | not required
revocation owner: client
```

Do not use a generic all-tools connection. For a single toolkit MCP, allow only specific action slugs. For a dynamic session/Connect flow, authorize only the action categories needed for the current workflow.

## n8n workflow contract

Every production candidate workflow must include:

```text
trigger and input schema
input validation
idempotency/deduplication method
separate test and production credentials
error route and retry limit
audit record
human approval gate before external write
success receipt and rollback/compensation path
```

Expose only necessary workflows through n8n MCP. Remember that n8n instance-level MCP can search workflow previews visible to the connected user, and all workflows explicitly MCP-enabled for that user become available to connected clients; isolate clients by instance/project/user, not only by workflow name.

## Test ladder

1. Build against mock/test data.
2. Connect one client-owned sandbox or read-only source.
3. Test one reversible read action.
4. Verify the provider-side audit trail and stored source reference.
5. Test malformed input, duplicate event and provider failure paths.
6. Obtain explicit owner approval for a single write action.
7. Re-read the exact target after any external write before reporting success.

## Deliverable

Return: workflow diagram, provider/tool list, scopes, data classes, approval boundary, test evidence, production readiness status and remaining blockers. Never represent documentation research or a draft workflow as a live automation.
