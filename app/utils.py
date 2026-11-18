from html import escape
from app.config import settings
from app.db import Session
from app.models import EmojiMap
from sqlalchemy import select

DEFAULTS = {"hello":"👋","search":"🔎","apk":"📦","download":"⬇️","success":"✅","error":"❌","warning":"⚠️","star":"⭐","admin":"👑","heart":"❤️"}
async def em(key):
    async with Session() as s:
        item = await s.get(EmojiMap, key)
        if item and item.custom_id:
            return f'<tg-emoji emoji-id="{escape(item.custom_id)}">{item.emoji or DEFAULTS.get(key,"✨")}</tg-emoji>'
        return (item.emoji if item else DEFAULTS.get(key, "✨"))
def is_admin(uid): return uid in settings.admin_ids
def human_size(n):
    if not n: return "Noma'lum"
    for unit in ("B","KB","MB","GB"):
        if n < 1024: return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"
