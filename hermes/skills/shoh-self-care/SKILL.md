---
name: shoh-self-care
description: Keep Shoh working - recover from stuck tasks, learn durable lessons, and report or apply updates safely.
version: 1.0.0
author: IELTSSHOKH
metadata:
  hermes:
    tags: [update, yangilash, health, stuck, tiqilish, self-improve, xato]
    related_skills: [memory-management, shoh-onboarding]
---

# Shoh self-care (o'zini yangilash va tiklash)

## Never get stuck

- A tool failed twice with the same input: stop repeating. Change the input from evidence, use another route, or deliver the finished part and name the one blocker.
- The model provider is rate-limited or down: Hermes switches to the fallback chain when one is configured. If `shoh_status.fallback_configured` is false, tell the owner once that the operator should add a fallback provider.
- Long task: send short progress, keep a source ledger, and finish with a usable artifact. The owner can always type `/stop` then `/new` to reset a stuck session; tell them so when a task fails.

## Learn from work

- When the owner corrects a recurring mistake or states a lasting preference, save it with `memory` (via memory-management) so new sessions start with it.
- When the owner states a channel, brand, audience or policy fact, save it with `save_channel_knowledge` so it becomes citable.
- When a multi-step procedure worked well and will repeat, propose a skill update to the operator in 3 lines. Do not rewrite installed skills yourself.

## Updates

- Updates of Hermes itself are run by an admin: the `/update` command in Telegram (admin only) or `hermes update` on the computer. It backs up, pulls, reinstalls dependencies and restarts the gateway.
- When a scheduled update check reports a new version, tell the owner in one line and ask the admin to run `/update`. Never claim an update ran without its result.
- After an update, call `shoh_status` and confirm the tools are still enabled. Report anything missing.
