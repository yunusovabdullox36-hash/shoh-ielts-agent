# Shoh: IELTSSHOKH Telegram yordamchi agenti. O'rnatish

Shoh — Hermes Agent ustida ishlaydigan agent. U ustoz bilan Telegram orqali o'zbekcha gaplashadi va quyidagilarni qiladi:

- Writing va Reading materiallarini IELTSSHOKH CDI uslubidagi interaktiv HTML ko'rinishida yasaydi.
- Yuborilgan PDF/HTML/rasmni o'qiydi va tahlil qiladi.
- Kanal, brend va qarorlar bazasidan manba (fayl + qator) bilan javob beradi.
- Marketing, xodim yollash va media (reels, rasm) bo'yicha reja va qoralama tayyorlaydi.
- Ustozning doimiy talablarini eslab qoladi (`memory`) va oldingi suhbatlardan qidiradi (`session_search`).

## Talablar

- Windows 10/11, Hermes Agent **v0.23.1** (git o'rnatmasi) va Git.
- Model akkaunti: standart sozlama `openai-codex` / `gpt-5.6-terra` (ChatGPT obunasi). Boshqa provayder ham ishlaydi: `hermes -p ieltschannel model`.
- Telegram bot tokeni (@BotFather) va ustozning Telegram user ID raqami.
- PDF o'qish uchun Poppler (`pdftotext`). Windows Hermes Git to'plamida bor.

## O'rnatish (5 daqiqa)

```powershell
# Paket papkasida:
powershell -ExecutionPolicy Bypass -File .\install.ps1 -HermesHome "D:\Hermes" `
  -Model claude -AdminTelegramId 111111111 -TeacherTelegramId 222222222 `
  -KnowledgeDir "D:\ObsidianVault\Shoh"
```

| Parametr | Ma'nosi |
| --- | --- |
| `-Model` | `codex` (ChatGPT obunasi), `claude` (Anthropic kaliti yoki Claude obuna tokeni), `gemini`, `openrouter`. Keyin `hermes -p ieltschannel model` bilan almashtiriladi |
| `-AdminTelegramId` | barcha `/buyruq`larga ruxsati bor operator |
| `-TeacherTelegramId` | ustoz: faqat `/new /stop /retry /undo /voice /help` |
| `-KnowledgeDir` | Obsidian vault ichidagi papka bo'lsa, ustoz eslatmalarni Obsidian'da ham ko'radi va tahrirlaydi |

**Ovoz:** ustoz yuborgan ovozli xabarni Whisper lokal, bepul matnga o'giradi va o'zbek yoki ingliz tilini o'zi aniqlaydi. Ovozli xabarga Shoh ham ovoz bilan javob beradi (Edge TTS, bepul). `/voice off` buyrug'i ovozni o'chiradi.
**Rasm:** yuborilgan rasmni tahlil qiladi, rasm yaratadi (`codex` modelida obuna orqali bepul).
**Birinchi suhbat:** Shoh o'zi tanishuvni boshlaydi: ustoz, kanallar, brend, auditoriya, model, Obsidian, Google (Gmail/Calendar/Drive), Telegram statistikasi, ovoz. Javoblarni bilim bazasiga yozadi.
**Yangilash:** admin Telegram'da `/update` yuboradi yoki kompyuterda `hermes update` ishga tushiradi. Mahalliy patch'lar saqlanadi, gateway o'zi qayta ishga tushadi.

Skript quyidagilarni bajaradi:

1. `ieltschannel` profilini yaratadi. Profil allaqachon bo'lsa, avval uning zaxirasini oladi.
2. SOUL, xotira, `channel-knowledge` plugini va 14 ta skill'ni o'rnatadi. Mavjud `MEMORY.md` saqlanib qoladi.
3. `knowledge/` fayllarini ko'chiradi. Mijoz tahrirlagan fayllar ustidan yozilmaydi.
4. `config.yaml`ni yozadi. Ichida maxfiy kalit yo'q.
5. Hermes manba kodiga 2 ta patch qo'llaydi (Telegram rasm yo'li va Windows uchun xavfsiz fayl nomlari). Har bir patch avval `--check` bilan tekshiriladi.
6. Yoqilgan vositalar ro'yxatini chiqaradi.
7. Botni avtomatik ishga tushirishni o'rnatadi. Bu `Shoh_Gateway_Watchdog_ieltschannel` nomli vazifa bo'lib, ikki holatda ishlaydi: Windows'ga kirilganda va har 5 daqiqada. Bot yashirin ishlaydi, terminal oynasi ochiq turmaydi. Kompyuter o'chib yonsa yoki bot yiqilsa, u 5 daqiqa ichida o'zi qayta ishga tushadi. Kerak bo'lmasa `-NoAutostart` bilan o'tkazib yuboriladi.

Keyingi qadamlarni egasi o'zi bajaradi, chunki parol va token faqat unda bo'ladi:

```powershell
hermes -p ieltschannel model           # model akkauntiga kirish
hermes -p ieltschannel gateway setup   # Telegram bot token + ruxsat berilgan user ID
hermes -p ieltschannel -z "Kanal brend qoidalari qanday?"   # tezkor sinov
hermes -p ieltschannel gateway restart # tokenni qo'llash (avtostart allaqachon o'rnatilgan)
```

> ⚠️ Botni `gateway run` buyrug'i bilan terminalda ishga tushirmang. Bunday holatda terminal yopilsa yoki uni ochgan agent sessiyasi tugasa, bot jim o'ladi va o'zi qayta ishga tushmaydi. Botni avtomatik ishga tushirish vazifasi o'zi boshqaradi.

**Bot javob bermasa:**
- `D:\Hermes\logs\shoh-watchdog.log` faylini oching. Unda bot qachon va nima sababdan qayta ishga tushgani yozilgan.
- `hermes -p ieltschannel gateway status` buyrug'ini bering.
- Kompyuter o'chiq bo'lsa bot ishlamaydi. Botning 24/7 ishlashi uchun doim yoniq kompyuter yoki server kerak.
- Avtostartni qayta o'rnatish: `powershell -ExecutionPolicy Bypass -File .\service\install-autostart.ps1 -HermesHome "D:\Hermes"`.
- Avtostartni o'chirish: shu buyruqqa `-Uninstall` qo'shiladi.

## Bilim bazasini to'ldirish

`knowledge/` papkasidagi fayllar Shoh uchun tasdiqlangan manba hisoblanadi:

| Fayl | Mazmuni |
| --- | --- |
| `channel-profile.md` | kanallar, maqsad, chegaralar |
| `brand-voice.md` | til, dizayn, logo, ranglar, taqiqlar |
| `audience.md` | auditoriya bo'yicha dalilli kuzatuvlar |
| `decisions.md` | egasi qabul qilgan qarorlar |
| `shoh-workflows.md` | ish tartiblari |

Shoh faylni faqat boshida `status: active` (yoki `approved`, `verified`) yozilgan bo'lsa o'qiydi. `pending-...` statusli fayl indeksga kirmaydi. Fayl tahrirlangach, qayta indekslash keyingi qidiruvda avtomatik bo'ladi, restart kerak emas.

## Chegaralar (mijozga ochiq aytiladi)

- **Kanalga avtomatik nashr yo'q.** Shoh qoralama tayyorlaydi, ustoz o'zi joylaydi.
- Rasm yoki video **yaratmaydi**: brief, ssenariy va montaj rejasini beradi.
- PDF eksport Writing simulyatorining o'zida bor. Boshqa materiallar uchun PDF render yo'q.
- Qidiruv kalit so'z asosida ishlaydi (FTS5, o'zbekcha qo'shimchalar va sinonimlar bilan), embedding emas. Shaxsiy fayllar yoki Obsidian'ga kirmaydi.
- Writing bahosi rasmiy band score emas, faqat mashq uchun fikr-mulohaza.

## Qaytarish (rollback)

O'rnatishdan oldin olingan zaxira `profiles\ieltschannel\backups\pre-install-<sana>` papkasida turadi. Fayllarni joyiga qaytarib, `hermes -p ieltschannel gateway restart` buyrug'ini bering. Patch'ni bekor qilish: `git -C <hermes-agent> apply -R <patch>`.
