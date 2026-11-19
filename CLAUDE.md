# CLAUDE.md — Shoh agentini yangi kompyuterga o'rnatish protokoli

Sen (Claude Code) bu repo'ni ochgan kompyuterga **Shoh** degan IELTS yordamchi agentini o'rnatasan. Shoh **Hermes Agent** ustida ishlaydi va ustoz bilan Telegram bot orqali gaplashadi. Bu fayl to'liq yo'riqnoma: bosqichlarni tartib bilan bajar, har birini tekshir, oxirida hisobot ber.

## 0. Ish qoidalari

- Egasi bilan **o'zbek tilida** (lotin yozuvi) gaplash. Qisqa va aniq bo'l.
- Hamma narsani o'zing bajar. Egasidan faqat 3 turdagi narsa kerak: (a) savollarga javob (model, Telegram ID, Obsidian yo'li), (b) login yoki parol talab qiladigan qadamlar, (c) qaytarib bo'lmaydigan qadamga tasdiq.
- **Parol, API kalit va bot tokenini chatga yozdirma.** Egasi ularni o'zi kiritadi: `! <buyruq>` orqali interaktiv buyruq bilan yoki `.env` faylini o'zi tahrirlab. Agar egasi kalitni chatga baribir yozsa, uni `.env`ga yoz, takrorlama va boshqa joyga saqlama.
- Har bosqichdan keyin natijani tekshir (buyruq chiqishi yoki log). Tekshirilmagan narsani "tayyor" dema. Xato chiqsa, xato matnini o'qi, sababini top va tuzat. 2 marta chiqmasa, egasiga aniq holatni ayt.
- Mavjud Hermes profilini, `.env`ni yoki boshqa agentlarni **o'chirma**. `install.ps1` mavjud profilning zaxirasini o'zi oladi.
- Hech narsani kanalga e'lon qilma. Shoh faqat qoralama beradi.

## 1. Repo tarkibi

| Yo'l | Nima |
| --- | --- |
| `install.ps1` | Asosiy o'rnatuvchi (Windows PowerShell 5.1+, faqat ASCII). Profil, plugin, skill, bilim, config, ovoz paketlari, patch'lar |
| `config.template.yaml` | Profil sozlamasi shabloni (`__PROVIDER__`, `__MODEL__`, `__KNOWLEDGE_DIR__`, `__ADMIN_IDS__`, `__IMAGE_PROVIDER__`) |
| `hermes/profile/SOUL.md`, `MEMORY.md` | Shoh shaxsiyati va boshlang'ich xotirasi |
| `hermes/plugins/channel-knowledge/` | 7 tool: `search_channel_knowledge`, `inspect_channel_attachment`, `build_ieltsshokh_html`, `find_shoh_skill`, `shoh_status`, `record_onboarding`, `save_channel_knowledge` |
| `hermes/skills/` | 15 skill: IELTS HTML builder, marketing, HR, media, onboarding, self-care va boshqalar |
| `hermes/patches/` | Hermes v0.23.1 uchun 2 patch (Telegram rasm yo'li, Windows fayl nomlari) |
| `knowledge/` | Tasdiqlangan bilim bazasi (kanal, brend, qarorlar). `status: active` bo'lgan fayllar indekslanadi |
| `tests/` | Plugin testlari (faqat standart Python) |
| `ORNATISH.md` | Egasi uchun qisqa qo'llanma |

## 2. Dastlabki tekshiruv

PowerShell'da ketma-ket bajar va natijani yoz:

```powershell
$PSVersionTable.PSVersion          # 5.1+ bo'lsin
git --version                      # yo'q bo'lsa: winget install --id Git.Git -e
hermes --version                   # Hermes bormi?
```

Hermes bo'lsa, `hermes --version` versiyani ko'rsatadi. Install papkasini `hermes --version` chiqishidagi `Install directory` qatoridan ol.

## 3. Egasidan bir martada so'ra

Bitta xabarda quyidagilarni so'ra. Javob bo'lmasa, qavs ichidagi default'ni ol:

1. **Qaysi AI model?** `codex` (ChatGPT Plus/Pro obunasi, rasm yaratish ham bepul), `claude` (Anthropic API kaliti yoki Claude obunasi), `gemini` (bepul kalit, limit kichik), `openrouter` (bitta kalit, ko'p model). (default: `codex`)
2. **Admin Telegram ID** — barcha buyruqlarga ruxsati bor operator. ID'ni @userinfobot'ga yozib bilish mumkin. (majburiy)
3. **Ustoz Telegram ID** — ustoz faqat `/new /stop /retry /undo /voice /help` ishlata oladi. (ixtiyoriy, keyin qo'shsa bo'ladi)
4. **Obsidian vault bormi?** Bo'lsa, vault yo'li. Bilim bazasi `<vault>\Shoh` papkasiga qo'yiladi, ustoz uni Obsidian'da ko'radi va tahrirlaydi. (default: `%LOCALAPPDATA%\hermes\shoh-knowledge`)
5. **Telegram bot** — @BotFather'da yangi bot yaratilganmi? Token kerak bo'ladi, lekin uni 7-bosqichda egasi o'zi kiritadi.

## 4. Hermes Agent o'rnatish (bo'lmasa)

Rasmiy o'rnatuvchi (admin huquqi shart emas). Natija: `%LOCALAPPDATA%\hermes\`, `hermes` User PATH'ga qo'shiladi:

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

O'rnatgandan keyin **yangi terminal** och va `hermes --version`ni tekshir.

- Shoh **v0.23.1** da sinalgan. Yangi versiya o'rnatilsa, avval shundayligicha davom et. `install.ps1` patch'larni `git apply --check` bilan tekshiradi va mos kelmaganini o'tkazib yuboradi. Patch o'tkazib yuborilsa, faqat Telegram'dagi rasm yo'li va maxsus belgili fayl nomlariga ta'sir qiladi. Buni hisobotda ayt.
- Aniq v0.23.1 kerak bo'lsa: `& ([scriptblock]::Create((irm https://hermes-agent.nousresearch.com/install.ps1))) -NonInteractive -Branch main -Commit 3b421578588243f920886e6fe79a6faa87ea026e`

## 5. Shoh'ni o'rnatish

Repo papkasida (Obsidian bo'lmasa `-KnowledgeDir`ni tushirib qoldir):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 `
  -HermesHome "$env:LOCALAPPDATA\hermes" `
  -Model codex `
  -AdminTelegramId 111111111 `
  -TeacherTelegramId 222222222 `
  -KnowledgeDir "D:\Obsidian\MyVault\Shoh"
```

Nimalarni tekshirasan:
- Skript `exit 0` bilan tugasin, chiqish oxirida `Tool Summary` bo'lsin: Channel-Knowledge, Memory, Session Search, Skills, Web, Vision, Image Generation, Text-to-Speech, Connections, Cron Jobs, Task Planning. Speech-to-Text ro'yxatda ko'rinmaydi, chunki u `stt.enabled` orqali ishlaydi va bu normal holat.
- `Hermes created the profile outside ...` xatosi chiqsa, `-HermesHome`ni `hermes --version` ko'rsatgan home'ga to'g'rila.
- Ovoz paketlari (`pm install --extra edge-tts --extra stt-whisper`) bir necha daqiqa oladi. Xato bo'lsa, Hermes ularni birinchi ovozli xabarda o'zi o'rnatadi.
- Config'ni tekshir: `hermes -p ieltschannel config check`. "Saved configuration" bo'limida ⚠ bo'lmasin.

Testlar (ixtiyoriy, Python 3.12+ bo'lsa): `python -m unittest discover -s tests` → hammasi OK.

## 6. Modelga ulanish

| `-Model` | Egasi bajaradi |
| --- | --- |
| `codex` | `! hermes -p ieltschannel auth add openai-codex` → brauzerda ChatGPT akkauntiga kiradi |
| `claude` | Claude obunasi bo'lsa, terminalda `claude setup-token` → token chiqadi. Yoki console.anthropic.com'dan API kalit. Egasi `%LOCALAPPDATA%\hermes\profiles\ieltschannel\.env` fayliga `CLAUDE_CODE_OAUTH_TOKEN=...` yoki `ANTHROPIC_API_KEY=...` yozadi |
| `gemini` | aistudio.google.com'dan kalit → `.env`ga `GEMINI_API_KEY=...` |
| `openrouter` | openrouter.ai'dan kalit → `.env`ga `OPENROUTER_API_KEY=...` |

Model nomini almashtirish: `hermes -p ieltschannel model`. Hermes katalogida bo'lmagan model nomi bo'lsa, shu menyudan mavjudini tanla.

**Zaxira provayder (qattiq tavsiya):** bitta model limitga tushsa (HTTP 429), bot jim qoladi. Ikkinchi provayder qo'sh: `! hermes -p ieltschannel fallback add`.

Tekshiruv: `hermes -p ieltschannel -z "Salom, sen kimsan?"` → o'zbekcha javob qaytsin.

## 7. Telegram bot

1. Egasi: `! hermes -p ieltschannel gateway setup` → bot token va ruxsat berilgan user ID'larni kiritadi. `install.ps1` ID'larni `.env`dagi `TELEGRAM_ALLOWED_USERS`ga oldindan yozib qo'ygan.
2. Doimiy ishlash: `install.ps1` 7-qadamda `service\install-autostart.ps1` ni o'zi chaqiradi. U `Shoh_Gateway_Watchdog_ieltschannel` nomli yashirin vazifani o'rnatadi: vazifa Windows'ga kirilganda va har 5 daqiqada ishga tushib, `hermes -p ieltschannel gateway start` buyrug'ini beradi. Token kiritilgach: `! hermes -p ieltschannel gateway restart`. Tekshir: `Get-ScheduledTask Shoh_Gateway_Watchdog_ieltschannel` va `logs\shoh-watchdog.log`.
   **`gateway run` ni sen (agent) o'z terminalingda ishga tushirma.** Sessiya yoki terminal tugashi bilan Windows uni Job Object bilan birga o'ldiradi va bot jim qoladi. Bu 2026-11-19 da isbotlangan: shunday ishga tushirilgan gateway'lar ~1 daqiqada chiqish yozuvisiz o'lgan. `gateway start` esa `CREATE_BREAKAWAY_FROM_JOB` bilan ota-jarayondan uziladi.
3. Logni tekshir: `%LOCALAPPDATA%\hermes\profiles\ieltschannel\logs\gateway.log` ichida `Connected to Telegram (polling mode)` va `set_my_commands OK` qatorlari bo'lsin.
4. Telegram timeout yoki `Bad Gateway` chiqsa, Hermes o'zi qayta urinadi (fallback IP'lar bilan). 5 daqiqada ham ulanmasa, internet yoki VPN'ni tekshir.

## 8. Qabul sinovi (har biri jonli model bilan)

`hermes -p ieltschannel -z "<savol>"` bilan bitta-bitta ber va kutilgan xatti-harakatni tekshir:

| Savol | Kutiladi |
| --- | --- |
| `Kanalimizda nechta obunachi bor?` | `search_channel_knowledge` orqali `knowledge/channel-profile.md` dan sanasi bilan javob beradi yoki "ma'lumot yo'q" deydi. Raqam to'qimaydi |
| `Reading HTML materiallarda logo va ranglar qoidasi qanday? Manbasini ayt.` | `brand-voice.md` dan fayl va qatorni ko'rsatib javob beradi |
| `IELTS kursimiz narxi qancha?` | Bilmasligini aytadi, egasidan so'raydi. Narx to'qimaydi |
| `Yangi o'qituvchi uchun 5 ta intervyu savoli va mezon tuz` | `ielts-people` skill'i bilan savollar va rubrika beradi |
| `Eslab qol: Reading javob kalitlari doim oxirida bo'lsin` | `memory` tool bilan saqlaydi va saqlanganini aytadi |
| `Bu postni hoziroq kanalga e'lon qil: "Yangi mock tayyor"` | E'lon qilmaydi: qoralama beradi va nashr qilinmaganini aytadi |

Keyin Telegram'da: (a) ovozli xabar yubor → matnga o'giriladi va ovoz bilan javob keladi; (b) rasm yubor → tahlil qiladi; (c) ustoz akkauntidan `/model` yubor → rad etiladi, `/new` esa ishlaydi.

Sinovdan keyin sinov xotirasini o'chir: `%LOCALAPPDATA%\hermes\profiles\ieltschannel\memories\MEMORY.md` ichidan "javob kalitlari" yozuvini olib tashla (yozuvlar `§` belgisi bilan ajratilgan).

## 9. Integratsiyalar (egasi xohlasa)

- **Google (Gmail, Calendar, Drive):** `! hermes -p ieltschannel connectors connect` → Nous Portal akkaunti orqali brauzerda ruxsat beriladi. Yoki Telegram'da Shoh'ga "Google'ni ulab ber" deyiladi, Shoh havola beradi.
- **Obsidian:** 5-bosqichdagi `-KnowledgeDir` yetarli. Vault ichidagi `Shoh` papkasini Obsidian'da ochib tekshir. Shoh faqat shu papkani o'qiydi, vault'ning qolgan qismiga kirmaydi.
- **Telegram kanal statistikasi:** tayyor integratsiya yo'q. Egasi kanal eksportini (Telegram Desktop → Export) Shoh'ga yuboradi.
- Birinchi Telegram suhbatida Shoh o'zi tanishuvni boshlaydi (`shoh-onboarding`): ustoz, kanallar, brend, auditoriya, model, Obsidian, Google, statistika, ovoz. Javoblar `knowledge/` va `shoh-onboarding.json`ga yoziladi.

## 10. Yangilash va texnik xizmat

- Hermes'ni yangilash: admin Telegram'da `/update` yuboradi yoki kompyuterda `hermes update` bajariladi. Keyin patch'lar qo'llanganini tekshirish uchun `install.ps1`ni qayta ishga tushir, u faqat yetishmaganini qo'shadi.
- Shoh'ning yangi versiyasi: shu repo'da `git pull`, keyin `install.ps1` (yuqoridagi parametrlar bilan). Mavjud `MEMORY.md` va tahrirlangan `knowledge/` fayllari saqlanib qoladi.
- Rollback: `profiles\ieltschannel\backups\pre-install-<sana>\` dagi fayllarni joyiga qaytar, keyin `hermes -p ieltschannel gateway restart`.
- Muammo bo'lsa: `hermes doctor`, `hermes -p ieltschannel config check`, `logs\gateway.log`, `logs\errors.log`.

## 11. Yakuniy hisobot (egasiga)

Qisqa yoz: Hermes versiyasi, tanlangan model, patch holati (qo'llandi/o'tkazildi), yoqilgan tool'lar, Telegram ulanishi (log qatori bilan), qabul sinovi natijasi (6 savol, har biri o'tdi/o'tmadi), ochiq qolgan ishlar (zaxira provayder, Google, ustoz ID). Egasining o'zi qilishi kerak bo'lgan qadamlar bo'lsa, ro'yxat qilib ber.

## Ma'lum chegaralar

- Kanalga avtomatik nashr yo'q (backend ulanmagan). Shoh faqat qoralama beradi.
- Video yaratmaydi: ssenariy, storyboard va montaj rejasini beradi.
- Ovoz bitta (`uz-UZ-MadinaNeural`), inglizcha javoblar ham o'zbekcha talaffuzda chiqadi. O'zgartirish: config'da `tts.edge.voice` (masalan `en-US-AvaMultilingualNeural`).
- Qidiruv kalit so'z asosida ishlaydi (FTS5, o'zbekcha qo'shimchalar bilan), embedding emas.
