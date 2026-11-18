# Ultimate APK Platform

Telegram APK katalog boti. Python 3.12, aiogram 3, SQLAlchemy async va PostgreSQL/SQLite bilan ishlaydi.

## Imkoniyatlar
- APK qabul qilish (oddiy yuborish va forward), nom, tavsif va kodni alohida so'rash
- Kod yoki nom bo'yicha qidirish, kategoriyalar, yangi va mashhur APKlar
- Majburiy obuna kanallari
- Admin statistikasi, APK tahrirlash/yashirish/o'chirish
- Sevimlilar, yuklab olish tarixi, sharhlar, APK so'rovlari
- Versiya tarixi, yangilash xabari uchun kuzatuvga qo'shish
- Markaziy emoji sozlamalari (Telegram custom emoji ID qo'llab-quvvatlanadi)
- Admin broadcast, foydalanuvchini bloklash, backup eksporti
- Render health endpoint

## O'rnatish (Windows)
1. Python 3.12 o'rnating.
2. ZIPni oching va loyiha papkasida terminal oching.
3. `python -m venv .venv`
4. Windows: `.venv\\Scripts\\activate`
5. `pip install -r requirements.txt`
6. `.env.example` faylidan `.env` nusxa yarating.
7. `.env` ichida `BOT_TOKEN` va `ADMIN_IDS` ni kiriting.
8. `python main.py`

`ADMIN_IDS` ichiga Telegram raqamli ID yoziladi. Bir nechta admin: `123,456`.

## Render
GitHub'ga barcha fayllarni yuklang. Render'da Blueprint orqali `render.yaml` ni tanlang. Bot token va username qiymatlarini Environment bo'limida kiriting. Render PostgreSQL bazasini yaratadi.

## APK yuklash oqimi
Admin panel → APK yuklash. Bot APK faylini qabul qiladi, keyin nom, tavsif va kodni (avtomatik yoki qo'lda) so'raydi. Caption bo'lsa ham tavsif alohida so'raladi. Telegram file_id bazada saqlanadi.

## Premium emoji
Admin panel → Emoji sozlash. `key` va `custom_emoji_id` kiriting. ID Telegram'dagi haqiqiy Premium custom emoji ID bo'lishi kerak. ID bo'lmasa bot standart emoji ko'rsatadi. Bot API custom emoji entity'larini HTML `<tg-emoji emoji-id="...">...</tg-emoji>` orqali yuboradi.

## Muhim cheklovlar
- Telegram bot API fayllarni foydalanuvchiga yuborishda Telegramning amaldagi fayl limitlariga bo'ysunadi.
- APK metadata ajratib olish va antivirus skaneri tashqi servis yoki alohida Android/APK analiz vositasini talab qiladi; bu loyiha bunday tekshiruv bajarildi deb yolg'on ko'rsatmaydi.
- Bot faqat admin yuklagan va ulashishga haqli bo'lgan fayllarni tarqatish uchun mo'ljallangan.
- Backup admin tomonidan JSON eksport sifatida olinadi; fayllarning o'zi Telegram `file_id` ko'rinishida saqlanadi.
