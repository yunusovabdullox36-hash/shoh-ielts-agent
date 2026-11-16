# Dedicated Hermes profile template

`SOUL.md` is copied into the **new, dedicated** client profile during onboarding. Hermes creates and owns its `memories/`, `sessions/`, `logs/`, `cron/`, `config.yaml`, `.env` and `auth.json` at that profile path.

Use the reviewed plan from `channel-manager hermes-profile-plan` before creating a profile. The current plan uses `--no-skills` and does not clone another profile. The client completes model and Telegram authentication through Hermes' own setup flow. This project must never copy credentials from the development machine or another Hermes profile. Verify the installed CLI help before applying onboarding commands.

After template installation, start a fresh Hermes session or verify a prompt refresh. Do not assume project `AGENTS.md` is loaded merely because it exists: check the configured working directory and actual session context. See `../DELIVERY.md` for the current capability boundary and handover checks.
