"""First-run setup state, capability status and owner-approved knowledge writes for Shoh."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re


STATE_FILE = "shoh-onboarding.json"
WRITABLE = ("channel-profile.md", "audience.md", "brand-voice.md", "decisions.md")
ACTIVE = {"active", "approved", "verified"}
MAX_FILE = 65_536  # retrieval ignores larger files
# key -> question topic; the onboarding skill asks them in this order
STEPS = {
    "teacher": "Ustoz ismi va brend nomi",
    "channels": "Telegram kanallar va ularning vazifasi",
    "brand": "Til, uslub, dizayn va taqiqlar",
    "audience": "Auditoriya: daraja, maqsad, yosh",
    "model": "Qaysi AI model (Claude, ChatGPT/Codex, Gemini, OpenRouter)",
    "obsidian": "Obsidian vault bormi va yo'li",
    "google": "Gmail, Calendar, Drive ulash kerakmi",
    "telegram_account": "Kanal statistikasi uchun Telegram akkaunt yoki eksport",
    "voice": "Javoblar ovozli bo'lsinmi",
}
FEATURES = {
    "voice_in": "stt", "voice_out": "tts", "image_analysis": "vision",
    "image_generation": "image_gen", "google_apps": "connections", "reminders": "cronjob",
    "memory": "memory", "history_search": "session_search", "web": "web",
}


def _now():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _atomic_write(path: Path, text: str):
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def _load_state(profile: Path):
    try:
        data = json.loads((profile / STATE_FILE).read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _config(profile: Path):
    try:
        from ruamel.yaml import YAML
        with (profile / "config.yaml").open(encoding="utf-8") as handle:
            return YAML(typ="safe").load(handle) or {}
    except Exception:  # missing file, parser or invalid YAML: report as unknown
        return {}


def _frontmatter_status(text: str):
    lines = text.splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        return None
    end = lines.index("---", 1)
    return next((l.split(":", 1)[1].strip() for l in lines[1:end] if l.startswith("status:")), "")


def status(profile: Path, knowledge_root):
    cfg = _config(profile)
    model = cfg.get("model") or {}
    toolsets = ((cfg.get("platform_toolsets") or {}).get("telegram")
                or cfg.get("toolsets") or [])
    knowledge = {}
    root = Path(knowledge_root) if isinstance(knowledge_root, str) and knowledge_root else None
    for name in (*WRITABLE, "shoh-workflows.md"):
        try:
            text = (root / name).read_text(encoding="utf-8-sig") if root else None
            knowledge[name] = _frontmatter_status(text) if text is not None else "missing"
        except OSError:
            knowledge[name] = "missing"
    state = _load_state(profile)
    answered = {k for k, v in state.items() if k in STEPS and isinstance(v, dict)}
    pending = [{"key": k, "topic": t} for k, t in STEPS.items() if k not in answered]
    stt = (cfg.get("stt") or {})
    return {
        "status": "ok",
        "model": {"provider": model.get("provider"), "default": model.get("default")},
        "fallback_configured": bool(cfg.get("fallback_providers") or cfg.get("fallback_model")),
        "features": {k: v in toolsets for k, v in FEATURES.items()},
        "voice": {"stt_enabled": stt.get("enabled", True) is not False and "stt" in toolsets,
                  "tts_provider": (cfg.get("tts") or {}).get("provider")},
        "image_gen_provider": (cfg.get("image_gen") or {}).get("provider"),
        "knowledge_dir_configured": bool(root and root.is_dir()),
        "knowledge": knowledge,
        "onboarding_complete": bool(state.get("completed_at")) or not pending,
        "onboarding_pending": pending,
        "operator_only": "Model, API keys, Telegram admins and integrations are changed by the operator "
                         "with `hermes -p <profile> setup` / `hermes connectors connect`; report the need.",
    }


def record(profile: Path, key, value):
    if key == "complete":
        state = _load_state(profile)
        state["completed_at"] = _now()
        _atomic_write(profile / STATE_FILE, json.dumps(state, ensure_ascii=False, indent=1))
        return {"status": "saved", "onboarding_complete": True}
    if key not in STEPS:
        raise ValueError(f"key must be one of {sorted(STEPS)} or 'complete'")
    if not isinstance(value, str) or not 1 <= len(value.strip()) <= 500:
        raise ValueError("value must be 1-500 characters")
    state = _load_state(profile)
    state[key] = {"value": value.strip(), "at": _now()}
    _atomic_write(profile / STATE_FILE, json.dumps(state, ensure_ascii=False, indent=1))
    remaining = [k for k in STEPS if not isinstance(state.get(k), dict)]
    return {"status": "saved", "key": key, "remaining": remaining}


def save_knowledge(knowledge_root, file, section, text):
    if not isinstance(knowledge_root, str) or not Path(knowledge_root).is_absolute():
        return {"status": "unavailable", "message": "knowledge_dir is not configured"}
    if file not in WRITABLE:
        raise ValueError(f"file must be one of {list(WRITABLE)}")
    if not isinstance(section, str) or not re.fullmatch(r"[^\n#]{2,80}", section.strip()):
        raise ValueError("section must be a 2-80 character single-line title")
    if not isinstance(text, str) or not 5 <= len(text.strip()) <= 2000:
        raise ValueError("text must be 5-2000 characters")
    root = Path(knowledge_root).resolve()
    path = root / file
    if path.is_symlink() or path.resolve().parent != root:
        raise PermissionError("outside knowledge directory")
    old = path.read_text(encoding="utf-8-sig") if path.is_file() else ""
    body = "\n".join(line for line in text.strip().splitlines() if line.strip() != "---")
    if old and _frontmatter_status(old) is not None:
        lines = old.splitlines()
        end = lines.index("---", 1)
        head = [l for l in lines[1:end] if not l.startswith(("status:", "updated:"))]
        new = "\n".join(["---", "status: active", f"updated: {_now()[:10]}", *head, "---",
                         *lines[end + 1:]]).rstrip() + "\n"
    else:
        title = file.removesuffix(".md").replace("-", " ").capitalize()
        new = f"---\nstatus: active\nupdated: {_now()[:10]}\n---\n\n# {title}\n"
    new += f"\n## {section.strip()}\n\nSource: owner, Shoh chat, {_now()[:10]}.\n\n{body}\n"
    if len(new.encode("utf-8")) > MAX_FILE:
        return {"status": "too_large", "message": "File would exceed 64 KB; ask the operator to archive old sections."}
    if old:  # keep every prior revision for rollback; .history is never indexed
        history = root / ".history"
        history.mkdir(exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        (history / f"{file}.{stamp}").write_text(old, encoding="utf-8")
    _atomic_write(path, new)
    return {"status": "saved", "file": f"knowledge/{file}", "section": section.strip(),
            "note": "Searchable immediately with search_channel_knowledge."}
