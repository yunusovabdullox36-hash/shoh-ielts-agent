# Telegram channel analyst — metrics contract v1

## Purpose

Use this contract when trusted posts and metrics are available through a client-authorized backend, export or later connector. It defines what can be measured without inventing unavailable Telegram analytics.

## Minimum post record

```text
post_id
published_at
content_pillar
format                 # text, image, carousel, video, poll, quiz, link
objective              # learn, save, share, reply, lead, sale
primary_CTA
campaign_id            # optional
status                  # draft, published, deleted
```

## Minimum metric record

```text
post_id
captured_at
views
forwards               # if supplied
reactions_total        # if supplied
comments_or_replies    # if supplied and permitted
subscriber_snapshot    # optional; must have capture time
source_ref             # export, backend metric ID or provider receipt
```

## Derived metrics

Calculate only when all inputs are available and label the capture window.

| Metric | Formula | Use |
|---|---|---|
| Views at N hours | recorded views at selected N-hour snapshot | Compare similar posts at the same age. |
| View rate | `views / subscriber_snapshot × 100` | Reach proxy only; not conversion. |
| Forward rate | `forwards / views × 100` | Shareability proxy. |
| Reaction rate | `reactions_total / views × 100` | Lightweight response signal. |
| CTA conversion | `verified outcomes / CTA clicks or tracked leads × 100` | Use only with a tracked destination and consented data. |

Do not compare posts captured at different ages as if they are equivalent. Do not infer sales, active readers, demographic facts or subscriber quality from views alone.

## Telegram source limits

Telegram's official API documentation says detailed channel statistics are available to administrators of eligible channels where the `can_view_stats` flag permits it. The statistics include data such as followers, views per post, shares per post, reactions per post, growth, top hours and recent post interactions. Access and availability are permission/server-config dependent. A safe integration must use a client-authorized channel/account and must verify the returned capabilities.

Source: https://core.telegram.org/api/stats

## Analysis report structure

1. Coverage: period, number of posts, metrics captured and missing fields.
2. Observed patterns: only results directly supported by records.
3. Comparisons: same format, same objective and consistent observation window.
4. Recommendations: one variable per experiment, baseline and success metric.
5. Limits: permissions, data gaps, untracked conversions and unexplained anomalies.

## First experiment template

```text
Objective: increase 24-hour view rate for one content pillar
Baseline: median 24-hour view rate of comparable last 5 posts
Variable: opening hook only
Keep constant: topic, format, publishing time and CTA
Period: next 5 comparable posts
Decision: retain change only if median improves and no tracked outcome declines
```
