---
name: client-integration-boundaries
description: "Use before connecting client accounts. Preserve ownership."
version: 1.0.0
author: IELTSSHOKH
license: Internal
metadata:
  hermes:
    tags: [integrations, oauth, mcp, freelancing, security]
    related_skills: [hermes-agent, ielts-rag-governance]
---

# Client integration boundaries

## When to Use

Use before adding an MCP server, OAuth connector, API key, webhook, automation platform, or external account for client work.

## Owner preference

Prepare reusable capabilities independently first. Do not permanently bind this agent to the owner's personal accounts. For freelance or client work, each client keeps ownership of their own account, credentials, data, approvals, billing and revocation path.

## Rules

- Use sandbox, test data, public documentation, or a dedicated non-production integration during preparation because personal and client accounts must not become hidden dependencies.
- Request the minimum scopes and begin read-only where possible because least privilege limits accidental changes and data exposure.
- Create separate environment, connection and data namespace per client because one client's data must never enter another client's workflow or RAG corpus.
- Never ask for, repeat, index or persist access tokens, API keys, private messages, student data or payment records in chat or RAG because transcripts and retrieval can expose them. Treat a credential disclosed in chat as compromised, instruct its owner to rotate it, and accept the replacement only through a secure secret store.
- Prefer a dedicated Telegram bot with explicit numeric user/chat allowlists over logging into an owner's personal Telegram user account because a bot gives a narrower, revocable authority boundary.
- Confirm whether an integration can read, write, send, publish, delete, or trigger automations before enabling it because capabilities can exceed the apparent use case.
- Require a client-approved connection for every production account because the client must control consent and revocation.
- Identify the exact profile, gateway or connection ID before disabling or removing it because ambiguous references can disrupt an unrelated client or agent.
- Record provider, scopes, data classes, connection owner, environment, renewal/revocation method and permitted actions because support and audit require traceability.
- Keep drafting, analysis and test actions separate from external publishing or mutation because production changes need exact owner approval and a receipt.

## Platform selection guide

| Need | Preferred evaluation path |
|---|---|
| Agent needs many OAuth tools in one product | Evaluate Composio with per-client sessions and scoped connections. |
| Visual multi-step automation / webhooks / data transformation | Evaluate n8n; self-hosting may offer more deployment control but creates operations responsibility. |
| Quick no-code client automation | Evaluate Zapier when its available applications and managed workflow model fit the client. |
| One specialized system | Prefer its official API or a narrow MCP connector over a broad all-purpose integration platform. |

Do not select a platform based on the app count alone. Evaluate target services, auth ownership, needed scopes, cost, logging, data location, reliability, test mode and client offboarding.

## Connection acceptance checklist

```text
[ ] Client/account owner identified
[ ] No credential was shared in chat; any exposed credential was rotated
[ ] Sandbox or production explicitly selected
[ ] Required tools/actions listed
[ ] Minimum scopes documented
[ ] Read/write/publish/delete capabilities confirmed
[ ] Data classes and retention understood
[ ] Approval rule documented
[ ] Revocation/offboarding tested or documented
[ ] One-client isolation confirmed
```

## Delivery

For each proposed connector, return a compact assessment: purpose, provider, account owner, scopes, data access, actions, risks, test result and recommendation. Do not claim connection success until the provider confirms a connected account and a safe test action succeeds.
