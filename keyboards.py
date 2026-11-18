from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu(admin=False):
    rows = [
        [KeyboardButton(text="🔎 APK qidirish"), KeyboardButton(text="📂 Kategoriyalar")],
        [KeyboardButton(text="🆕 Yangi APKlar"), KeyboardButton(text="🏆 TOP APK")],
        [KeyboardButton(text="❤️ Sevimlilar"), KeyboardButton(text="📨 APK so'rash")],
        [KeyboardButton(text="👤 Profil")]
    ]
    if admin: rows.append([KeyboardButton(text="👑 Admin panel")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

def admin_menu():
    b=InlineKeyboardBuilder()
    for text, data in [
        ("📢 Majburiy obuna","adm:channels"),("📊 Statistika","adm:stats"),
        ("📦 APK yuklash","adm:upload"),("🗂 APK boshqaruvi","adm:manage"),
        ("😀 Emoji sozlash","adm:emoji"),("📨 Xabar yuborish","adm:broadcast"),
        ("💾 Backup","adm:backup"),("⚙️ Sozlamalar","adm:settings")
    ]: b.button(text=text, callback_data=data)
    b.adjust(2)
    return b.as_markup()

def apk_card(apk, favorite=False):
    b=InlineKeyboardBuilder()
    b.button(text="⬇️ Yuklab olish", callback_data=f"get:{apk.id}")
    b.button(text="❤️ Sevimli" if not favorite else "💔 O'chirish", callback_data=f"fav:{apk.id}")
    b.button(text="⭐ Baholash", callback_data=f"rate:{apk.id}")
    b.adjust(1,2)
    return b.as_markup()

def channel_check():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_sub")]])
