# 🎬 Kinochi Telegram Bot

Python (aiogram 3.x) va SQLAlchemy (async, SQLite) asosida qurilgan kino/serial yuklovchi Telegram bot.
Foydalanuvchi qismi + to'liq admin panel MVP versiyasi.

## Imkoniyatlar

**Foydalanuvchi:**
- 🔢 Kino kodi orqali kino olish
- 🔎 Kino nomi bo'yicha qidirish
- 📂 Kategoriyalar bo'yicha ko'rish
- 📺 Seriallar va qismlar
- 💎 Premium tizimi (promo kod orqali aktivlashtiriladi)
- 🔐 Majburiy obuna (agar admin kanal qo'shgan bo'lsa, Premium foydalanuvchilar bundan ozod)

**Admin panel** (faqat `.env` dagi `ADMIN_IDS`):
- Kinolar: qo'shish / tahrirlash / o'chirish / qidirish
- Seriallar va qismlar boshqaruvi
- Kategoriyalar
- Majburiy obuna kanallari
- Premium tariflari (kunlik/haftalik/oylik davomiyligi)
- Promo kodlar (yaratish, aktiv/noaktiv qilish, o'chirish)
- Ommaviy xabar (matn / rasm+matn / video+matn)
- Statistika

## O'rnatish

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

`.env.example` faylini `.env` deb nomlang va o'zingizning bot tokeningiz va admin ID'ingizni kiriting.

## Ishga tushirish

```bash
python bot.py
```

Bot birinchi marta ishga tushganda `kinochi.db` SQLite fayli avtomatik yaratiladi va barcha jadvallar hosil bo'ladi.
Bot qayta ishga tushirilganda ma'lumotlar saqlanib qoladi.

## Loyiha strukturasi

```
kinochi_bot/
├── bot.py                     # kirish nuqtasi (entry point)
├── config.py                  # .env o'qish
├── database/
│   ├── models.py               # SQLAlchemy modellari
│   ├── engine.py                # engine/session/init_db
│   └── requests.py              # barcha CRUD funksiyalar
├── keyboards/
│   ├── user_kb.py
│   └── admin_kb.py
├── states/
│   └── all_states.py           # barcha FSM state guruhlari
├── filters/
│   └── admin_filter.py         # IsAdmin filter
├── handlers/
│   ├── user_handlers.py
│   └── admin_handlers.py
```

Yangi funksiya qo'shish uchun: `database/models.py` ga model qo'shing → `database/requests.py` ga CRUD qo'shing →
tegishli `handlers/*.py` faylga handler qo'shing. Struktura oddiy va kengaytirishga qulay.
