---
name: shoh-onboarding
description: First-run setup conversation. Learn the teacher, channels, brand and audience, and ask about model, Obsidian, Google, Telegram and voice.
version: 1.0.0
author: IELTSSHOKH
metadata:
  hermes:
    tags: [onboarding, setup, first-run, sozlash, integratsiya]
    related_skills: [memory-management, channel-decision-tree]
---

# Shoh onboarding (birinchi tanishuv)

## When to Use

`shoh_status` shows `onboarding_complete: false`, or the owner says "sozla", "qaytadan tanishaylik", "setup". If the owner arrives with a concrete task, do the task first and offer setup at the end in one line.

## Procedure

1. Call `shoh_status`. Greet in plain Uzbek in two sentences: who you are and that a few short questions will tune you. Report only real abilities from `features`.
2. Ask ONE question at a time, following `onboarding_pending` order. Keep each question short with an example answer. Accept "keyin" (later) or "kerak emas" (not needed) as a valid answer and record it.
3. After each answer:
   - `record_onboarding` with the key and a compact summary.
   - For teacher, channels, brand and audience facts the owner stated, also call `save_channel_knowledge` (channels -> channel-profile.md, brand -> brand-voice.md, audience -> audience.md, policy -> decisions.md). Never save guesses.
4. Topic notes:
   - **model**: report the current `model.provider`. Explain options in one line each: Claude (Anthropic API key or Claude subscription token), ChatGPT/Codex (subscription login), Gemini (free key, limited), OpenRouter (one key, many models). Recommend a second provider as fallback so Shoh never stops on a rate limit. The operator applies it with `hermes -p ieltschannel model` and `hermes fallback add`; you cannot change keys yourself.
   - **obsidian**: Shoh reads approved notes, not the whole vault. If the owner has a vault, record its path; the operator points `knowledge_dir` to a `Shoh` folder inside it, so the same notes are editable in Obsidian.
   - **google**: if `features.google_apps` is true, offer to connect Gmail/Calendar/Drive with `manage_connections` (the owner signs in through the returned link). Otherwise record the wish for the operator.
   - **telegram_account**: channel statistics need an export or an operator integration; record which channels and metrics matter.
   - **voice**: if `features.voice_out` is true, tell the owner `/voice tts` turns voice replies on and `/voice off` turns them off. Voice messages from the owner are always transcribed when `voice_in` is true.
5. When every step is answered, call `record_onboarding` with key `complete`, then give a 5-line summary: what was saved, what the operator still needs to do, and 3 example requests the owner can send now.

## Rules

- Never ask for passwords, API keys, bot tokens or codes in chat. Those go to the operator's setup command.
- Never present an integration as connected until a tool result confirms it.
- Keep the whole onboarding under 10 short messages.
