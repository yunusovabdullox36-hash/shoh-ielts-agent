# Composio adoption roadmap v1 — channel analyst and media research

**Decision:** n8n is not part of the current default stack. Use Composio only for a named client workflow after a separate Composio consumer/project key and client-owned authorization are available.

## Integration boundary

Composio Connect is a remote streamable-HTTP MCP at `https://connect.composio.dev/mcp`. Hermes can connect only when a Composio consumer key is placed in the profile's secure secret/configuration path; no key is present in this session. Do not paste the key into chat or source-controlled files.

No client account, token or Composio connection has been created in this profile.

## Priority 1 — YouTube research and channel analytics

| Item | Decision |
|---|---|
| Toolkit | `YOUTUBE` |
| Auth | OAuth2; Composio-managed OAuth is available. |
| Initial mode | Read-only analysis only. |
| Initial capabilities | Channel/video metadata, video lists, channel statistics, video-detail batches and analytics queries where the connected account permits them. |
| Explicitly blocked initially | Uploading/deleting videos, publishing comments, playlists, channel updates, live broadcasts and subscription actions. |
| Client requirement | Client authorizes their own YouTube account; for production workloads assess their own Google OAuth app because Composio warns that managed OAuth can have shared provider quota. |

**First safe workflow:** retrieve a bounded period of owned channel/video metrics, record the source/capture time, analyse performance by format/topic/CTA, and produce a draft report. No YouTube mutation occurs.

Source: https://docs.composio.dev/toolkits/youtube

## Priority 2 — Telegram channel operations, not analytics

| Item | Decision |
|---|---|
| Toolkit | `TELEGRAM` |
| Auth | Bot API token (`API_KEY`), not managed OAuth. |
| Initial mode | Disabled until a client supplies a dedicated bot token and makes the bot a minimum-permission channel member/admin. |
| Suitable later work | Approved sending/editing/polls, chat permission checks and bot operations. |
| Not a solution for | Full Telegram channel statistics and historical analytics. |

The Composio Telegram toolkit is a Bot API integration with 18 tools and no triggers. Telegram’s detailed channel statistics are permission-limited and are governed separately by the official Telegram statistics API. Keep analytics ingestion separate from publish/bot operations.

Sources:
- https://docs.composio.dev/toolkits/telegram
- https://core.telegram.org/api/stats

## Priority 3 — Perplexity deep research, optional

| Item | Decision |
|---|---|
| Toolkit | `PERPLEXITYAI` |
| Auth | API key. |
| Initial mode | Not required while native web research covers source discovery and extraction. |
| Use later for | Bounded, cited long-form research where budget and source requirements are defined. |
| Constraints | Costs/API key required; research output remains evidence, not final authority. |

Perplexity also exposes contextual embedding tools, but do not use them for RAG until a vector storage design, privacy policy and evaluation set are approved.

Source: https://docs.composio.dev/toolkits/perplexityai

## Deferred candidates

- `GOOGLEDRIVE`, `GOOGLEDOCS`, `GOOGLESHEETS`: client-owned source ingestion and reporting after a source allowlist exists.
- `NOTION`: client-owned knowledge ingestion after page access and review lifecycle are defined.
- `GOOGLE_ANALYTICS`, `YOUTUBE`: only when a client needs verified analytics data and has granted appropriate read scopes.

## Safe Composio connection sequence

```text
1. Create/use a non-personal Composio project and store its consumer key securely.
2. Add the remote MCP URL with the secret header, then restart Hermes.
3. Verify only the seven Composio meta-tools appear.
4. Search tools for one named workflow; do not authorize an application yet.
5. Client completes OAuth/API-key connection for one service.
6. Retrieve schemas and confirm read/write/delete effects.
7. Run one bounded read-only action and verify provider-side data.
8. Add only approved write actions after exact approval rules exist.
```

## Channel analyst capability map

```text
Current without external accounts
→ official IELTS/web research, RAG governance, content analysis, report logic, design/media briefs

Composio YouTube (later)
→ owned YouTube analytics and content research

Composio Telegram (later)
→ approved bot/channel actions; separate analytics authorization needed

Perplexity (optional later)
→ budgeted deep research, not a replacement for primary-source checking
```
