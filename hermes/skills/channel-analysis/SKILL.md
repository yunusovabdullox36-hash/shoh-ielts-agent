---
name: channel-analysis
description: Analyze available channel posts and metrics with source coverage.
---

# Channel analysis

## Use when

The owner asks for channel performance, audience, topic or content-format analysis.

## Inputs

- Owner request and requested period
- Owner-supplied posts/export, available metrics and coverage; backend data only if a connected read tool supplies it
- Approved channel profile and brand voice via `search_channel_knowledge` (dated observations only)

## Procedure

1. State the available period, post count and missing metrics.
2. Inspect the supplied export or use an available authorized backend read tool. No verified analytics/history adapter is provided by the current channel-knowledge plugin; do not invent a tool or infer missing reach, subscribers or conversion counts.
3. Separate observed facts from recommendations and uncertainty.
4. Cite the stored post or metric references used for each material conclusion.
5. Return the analysis in the current conversation. Save through an available authorized backend only when its result confirms persistence. Do not claim storage or write a permanent memory conclusion without evidence.

## Output

Return a concise report with coverage, findings, recommendations and limits.

## Error handling

If data is missing, stale or inconsistent, return a limited analysis that names the gap. Do not infer unavailable Telegram analytics.
