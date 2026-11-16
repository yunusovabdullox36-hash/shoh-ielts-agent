# MCP candidate registry v1 — client-safe preparation

**Status:** researched; no external account, OAuth grant, API key, webhook or MCP endpoint has been connected from this profile.

## Selection principle

Add a connector only when it solves a named workflow, has a verified provider source, uses the minimum permissions, and can be kept separate for each client. A broad catalog is not a reason to enable broad access.

## Tier 0 — already useful without a client connection

| Capability | Status | Why |
|---|---|---|
| Public web research and source checking | Available | Supports official-source research without client credentials. |
| RAG governance and public IELTS source register | Available | Supports source-aware factual answers and drafts. |
| Channel-analysis workflow | Available | Defines evidence-based analysis when posts and metrics are provided. |
| Design/media governance | Available | Produces briefs, scripts and quality gates without publishing externally. |

## Tier 1 — client connector candidates

| Candidate | Use case | Account boundary | Decision |
|---|---|---|---|
| Composio Connect MCP | Dynamic discovery and use of client-authorized SaaS tools such as Google Drive, Docs, Sheets, Notion, CRM and analytics services. | Every client completes their own OAuth connection; use an allowlist of tools/scopes. | **Evaluate first** when a named client needs several SaaS integrations. |
| n8n MCP server | Workflows, webhooks, schedules, data transformation, approval pipelines and durable execution. | Each client uses their own n8n instance/project; expose only explicit workflows to MCP. | **Evaluate first** for multi-step automation. |
| Narrow official API or focused MCP | One system such as a CRM, database or storage provider. | Client-owned token and separate environment. | **Prefer** over a broad tool hub when the workflow has one target system. |

## Tier 2 — deferred capabilities

| Capability | Trigger to evaluate | Why deferred |
|---|---|---|
| Google Drive / Docs ingestion | Client needs RAG from a named folder/document library. | Requires client OAuth and a source allowlist. |
| Notion knowledge ingestion | Client has approved Notion pages as its knowledge source. | Requires page-level access and source lifecycle rules. |
| CRM / form lead routing | Client defines fields, consent policy, lead owner and follow-up rules. | Write actions have business impact. |
| Telegram analytics ingestion | Client grants appropriate channel/account authorization and agrees on metrics to store. | Official detailed channel statistics are permission-limited; do not use unverified third-party analytics APIs. |
| Publishing connector | Owner approves exact draft and publishing policy. | Publish/write action needs review and receipt. |

## Provider notes

### Composio

Composio Connect provides a remote MCP endpoint and meta-tools for discovery, schema lookup, connection management and execution. Its documentation says an OAuth authorization link is generated when an app is first required, and the connection persists after approval. For client work, use per-client identities and restrict allowed tools; do not expose an all-tools server.

Sources:
- https://docs.composio.dev/docs/composio-connect
- https://docs.composio.dev/docs/single-toolkit-mcp

### n8n

n8n supports built-in, community and generic HTTP integrations, and its instance-level MCP server can expose selected workflows to MCP clients. Its docs state that workflows/agents must be explicitly available in MCP; use this explicit exposure as the permission boundary. n8n's protected/read-only mode can block non-read-only MCP tools.

Sources:
- https://docs.n8n.io/integrations
- https://docs.n8n.io/connect/connect-to-n8n-mcp-server
- https://docs.n8n.io/connect/connect-to-n8n-mcp-server/mcp-server-tools-reference

## Required pre-connection test

```text
1. Define one client workflow and exact expected result.
2. Create a separate test client/environment.
3. Allow only read-only tools for the first test.
4. Complete client-owned authorization.
5. Execute one safe, reversible test action.
6. Verify provider-side result and audit log.
7. Add write/publish capability only after explicit approval.
```

## Current recommendation

Do not connect any personal account now. Continue building portable RAG, analysis, content, audit and media capabilities. Add Composio or n8n only when an approved client workflow defines the target account, data, permissions and owner.