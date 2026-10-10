# KaryeraUz Namangan — vakansiya boti

osonish.uz'dagi **Namangan viloyati** vakansiyalarini avtomatik postga aylantiradi, rasm chizadi, admin tekshiruviga yuboradi va tasdiqlangandan keyin @karyerauznamangan kanaliga joylaydi.

Bot **GitHub Actions**'da bepul ishlaydi: server, karta yoki to'lov kerak emas.

## Qanday ishlaydi

1. Bot har ~10 daqiqada osonish.uz'ni tekshiradi va yangi e'lonlarni oladi.
2. Namangan viloyatidagi har bir e'lon uchun rasm va shablon bo'yicha matn tayyorlanadi.
3. Post admin chatga quyidagi tugmalar bilan keladi:
   - ✅ **Tasdiqlash** — post kanalga chiqadi.
   - ❌ **Rad etish** — post kanalga chiqmaydi.
   - ✏️ **Tahrirlash** — bot so'rov yuboradi. Unga **javob (reply)** qilib yangi matnni yuborasiz. Maslahat: post matnini nusxalab, kerakli joyini to'g'rilang. Qalin yozuv kabi formatlash saqlanadi.
   - 🔄 **Boshqa rasm** — rasmning boshqa varianti chiqadi.

> ⏱ **Muhim:** GitHub bepul rejimida bot doimiy yoqiq turmaydi, u har ~10 daqiqada "uyg'onadi". Shuning uchun tugmani bosganingizdan keyin natija **5–15 daqiqada** ko'rinadi. Bu normal holat.

## O'rnatish (bir marta, ~15 daqiqa)

### 1. Telegram bot

1. @BotFather → `/newbot` → nom bering va **tokenni** saqlab qo'ying.
2. Botni @karyerauznamangan kanaliga **admin** qilib qo'shing va "Post yuborish" huquqini bering.
3. **Admin chat**ni tanlang:
   - Tekshiruvchi bitta odam bo'lsa: botga `/start` yozing. Sizning ID'ingiz @userinfobot orqali olinadi (masalan `123456789`).
   - Tekshiruvchilar bir nechta bo'lsa: yopiq guruh oching, botni va adminlarni qo'shing. Guruh ID'sini (masalan `-1001234567890`) olish uchun guruhga @RawDataBot'ni vaqtincha qo'shing, `chat.id`ni ko'ring, keyin uni chiqarib yuboring.

### 2. GitHub

1. github.com'da ro'yxatdan o'ting va **yangi repository** oching. Uni **Public** qilib oching: Actions daqiqalari cheksiz bo'ladi. Token baribir yashirin turadi.
2. Ushbu arxivdagi barcha fayllarni repository'ga yuklang (**Add file → Upload files**). `.github` papkasi ham yuklanganini tekshiring.
3. **Settings → Secrets and variables → Actions → New repository secret** bo'limida ikkita secret qo'shing:
   - `BOT_TOKEN` — BotFather bergan token;
   - `ADMIN_CHAT_ID` — 1-bosqichdagi ID.
4. **Actions** bo'limida workflow'larni yoqing (**Enable**). Keyin **KaryeraUz bot → Run workflow** tugmasini bosing.

Birinchi ishga tushishda bot oxirgi ~300 ta e'lonni ko'rib chiqadi (~6 daqiqa). Shundan keyin faqat yangi e'lonlarni oladi.

## Sozlamalar (ixtiyoriy)

| Nima | Qayerda |
|---|---|
| Post matni shabloni | `post.py` → `build_text` |
| Rasm dizayni, ranglar, sohalar | `card.py` → `THEMES` (sohani aniqlovchi kalit so'zlar `kw` ichida) |
| Hudud | `osonish.py` → `REGION_KEYS`, `NAMANGAN_DISTRICTS` |
| Tekshirish chastotasi | `.github/workflows/bot.yml` → `cron` |
| Kanal | Settings → Variables → `CHANNEL_ID` (standart: `@karyerauznamangan`) |

## Sinab ko'rish (kompyuterda)

```
pip install -r requirements.txt
python run.py --test 116052
```

Bu buyruq vakansiyaning ajratilgan maydonlarini, tayyor post matnini chiqaradi va `test_116052.jpg` rasmini yaratadi. Telegramga hech narsa yuborilmaydi.

## Eslatmalar

- Bot faqat osonish.uz'ning ochiq sahifalari va sitemap'idan foydalanadi. Saytning `robots.txt` qoidalariga amal qilinadi: `/api/` ishlatilmaydi va so'rovlar orasida 1 soniya kutiladi.
- Ba'zi e'lonlarda mas'ul shaxs ismi saytda ko'rsatilmaydi. Bunday holatda postda faqat telefon raqami chiqadi, kerak bo'lsa ✏️ orqali qo'shasiz.
- `state.json` botning xotirasi: qaysi e'lonlar ko'rilgani va qaysilari tekshiruvda ekani shu yerda saqlanadi. Uni o'chirmang.
