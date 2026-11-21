# Shoh — IELTSSHOKH uchun Telegram AI yordamchi

Shoh — IELTS ustozining Telegram'dagi yordamchisi. U [Hermes Agent](https://github.com/NousResearch/hermes-agent) ustida ishlaydi. Imkoniyatlari:

- **Ovoz (Audio & Voice):** Ustoz yuborgan audio va ovozli xabarlarni to'liq qabul qiladi, tushunadi (Whisper orqali o'zbek/ingliz tilini avto-aniqlaydi) va o'zi ham tabiiy ovoz bilan javob qaytara oladi.
- **Multimodal (Vision & Files):** PDF, rasmlar, jadvallarni o'qiydi va tahlil qiladi.
- **IELTS Materiallari:** IELTSSHOKH CDI uslubida Writing va Reading HTML materiallarini avtomatlashtirilgan tarzda tayyorlaydi.
- **Kanal va brend bilimi:** Tasdiqlangan bilim bazasiga asoslanib qoralamalar beradi.
- **Xotira va adaptatsiya:** Ustoz talablarini doimiy eslab qoladi.

## Yangi kompyuterga o'rnatish (Claude Code bilan)

1. Kompyuterda [Claude Code](https://claude.com/claude-code) bo'lsin (desktop yoki terminal).
2. Unga shu xabarni yuboring:

```text
Shu repo'ni clone qil va ichidagi CLAUDE.md bo'yicha Shoh agentini shu kompyuterga to'liq o'rnat:
https://github.com/yunusovabdullox36-hash/shoh-ielts-agent
Har bosqichni tekshir, men bilan o'zbekcha gaplash, oxirida hisobot ber.
```

Claude Code quyidagilarni o'zi bajaradi: Hermes'ni o'rnatadi, agentni joylaydi, model va Telegram ulashda yo'l ko'rsatadi, Obsidian'ni bog'laydi va qabul sinovini o'tkazadi. Sizdan faqat model tanlovi, Telegram ID'lar va login qadamlari so'raladi.

Repo private. Yangi kompyuterdagi GitHub akkauntining bu repo'ga kirish huquqi bo'lishi kerak: `gh auth login`, mijoz akkaunti bo'lsa uni collaborator qilib qo'shing.

## Qo'lda o'rnatish

[ORNATISH.md](ORNATISH.md) ni ko'ring. Qisqasi:

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
powershell -ExecutionPolicy Bypass -File .\install.ps1 -HermesHome "$env:LOCALAPPDATA\hermes" -Model codex -AdminTelegramId <ID>
```
