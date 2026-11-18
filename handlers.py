import json, secrets, logging
from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, Document
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, func, desc
from app.db import Session
from app.models import User, APK, Channel, Favorite, Download, Review, Request, EmojiMap, APKVersion, Setting
from app.states import UploadAPK, SearchAPK, RequestAPK, AddChannel, EmojiEdit, Broadcast
from app.keyboards import main_menu, admin_menu, apk_card, channel_check
from app.utils import is_admin, human_size, DEFAULTS
from app.config import settings

router=Router()
log=logging.getLogger(__name__)

async def register_user(m: Message):
    async with Session() as s:
        u=await s.get(User,m.from_user.id)
        if not u:
            s.add(User(id=m.from_user.id, username=m.from_user.username, full_name=m.from_user.full_name))
        else:
            u.username=m.from_user.username
            u.full_name=m.from_user.full_name
        await s.commit()

async def missing_channels(bot: Bot, uid: int):
    async with Session() as s:
        channels=(await s.scalars(select(Channel))).all()
    missing=[]
    for c in channels:
        try:
            member=await bot.get_chat_member(c.chat_id,uid)
            if member.status in ("left","kicked"): missing.append(c)
        except Exception:
            missing.append(c)
    return missing

async def show_apk(target, apk, user_id, bot=None):
    text=(f"<b>{apk.name}</b>\n\n{apk.description}\n\n"
          f"🆔 Kod: <code>{apk.code}</code>\n"
          f"📁 Kategoriya: {apk.category}\n"
          f"🔢 Versiya: {apk.version}\n"
          f"💾 Hajmi: {human_size(apk.file_size)}\n"
          f"⬇️ Yuklab olingan: {apk.downloads}")
    async with Session() as s:
        fav=await s.scalar(select(Favorite).where(Favorite.user_id==user_id,Favorite.apk_id==apk.id))
    await target.answer(text, reply_markup=apk_card(apk,bool(fav)))

@router.message(F.text=="/start")
async def start(m: Message, bot: Bot, state: FSMContext):
    await state.clear()
    await register_user(m)
    miss=await missing_channels(bot,m.from_user.id)
    if miss:
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        b=InlineKeyboardBuilder()
        for c in miss:
            if c.url: b.button(text=f"📢 {c.title or c.url}",url=c.url)
        b.button(text="✅ Tekshirish",callback_data="check_sub"); b.adjust(1)
        await m.answer("Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:",reply_markup=b.as_markup())
        return
    await m.answer(f"Assalomu alaykum, <b>{m.from_user.full_name}</b>!\nAPK katalogiga xush kelibsiz.",reply_markup=main_menu(is_admin(m.from_user.id)))

@router.callback_query(F.data=="check_sub")
async def check_sub(c: CallbackQuery,bot:Bot):
    miss=await missing_channels(bot,c.from_user.id)
    if miss: await c.answer("Hali barcha kanallarga obuna bo'lmagansiz.",show_alert=True)
    else:
        await c.message.answer("Obuna tasdiqlandi. /start bosing.",reply_markup=main_menu(is_admin(c.from_user.id)))
        await c.answer()

@router.message(F.text=="👑 Admin panel")
async def admin_panel(m:Message):
    if not is_admin(m.from_user.id): return
    await m.answer("<b>ADMIN PANEL</b>",reply_markup=admin_menu())

@router.callback_query(F.data.startswith("adm:"))
async def admin_actions(c:CallbackQuery,state:FSMContext,bot:Bot):
    if not is_admin(c.from_user.id): return await c.answer("Ruxsat yo'q",show_alert=True)
    action=c.data.split(":")[1]
    if action=="upload":
        await state.set_state(UploadAPK.file); await c.message.answer("APK faylini yuboring yoki forward qiling."); 
    elif action=="stats":
        async with Session() as s:
            users=await s.scalar(select(func.count()).select_from(User))
            apks=await s.scalar(select(func.count()).select_from(APK))
            downs=await s.scalar(select(func.count()).select_from(Download))
            today=await s.scalar(select(func.count()).select_from(User).where(func.date(User.created_at)==datetime.utcnow().date()))
        await c.message.answer(f"📊 <b>Statistika</b>\nFoydalanuvchilar: {users}\nBugun qo'shilganlar: {today}\nAPKlar: {apks}\nYuklab olishlar: {downs}")
    elif action=="channels":
        await state.set_state(AddChannel.chat_id); await c.message.answer("Kanal ID yoki @username yuboring:")
    elif action=="emoji":
        await state.set_state(EmojiEdit.key); await c.message.answer("Emoji kalitini yuboring (masalan: hello, search, apk, download, success, error, warning, star, admin, heart):")
    elif action=="broadcast":
        await state.set_state(Broadcast.message); await c.message.answer("Barcha foydalanuvchilarga yuboriladigan xabarni kiriting:")
    elif action=="backup":
        async with Session() as s:
            rows=(await s.scalars(select(APK))).all()
            data=[{"id":x.id,"code":x.code,"name":x.name,"description":x.description,"file_id":x.file_id,"category":x.category,"downloads":x.downloads} for x in rows]
        import io
        f=io.BytesIO(json.dumps(data,ensure_ascii=False,indent=2).encode()); f.name="apk_backup.json"
        await c.message.answer_document(f,caption="APK katalogi backup (Telegram file_id bilan).")
    elif action=="manage":
        async with Session() as s:
            rows=(await s.scalars(select(APK).order_by(desc(APK.id)).limit(20))).all()
        if not rows: await c.message.answer("Hozircha APK yo'q.")
        else:
            for a in rows:
                await c.message.answer(f"{a.name} — <code>{a.code}</code> | {a.category}\nHolat: {'Yashirilgan' if a.hidden else 'Faol'}\nTahrirlash: /editapk {a.code}\nYashirish/almashtirish: /hideapk {a.code}\nO'chirish: /delapk {a.code}")
    elif action=="settings":
        await c.message.answer("Sozlamalar: /setwelcome matn\nTexnik konfiguratsiya .env orqali boshqariladi.")
    await c.answer()

@router.message(UploadAPK.file, F.document)
async def upload_file(m:Message,state:FSMContext):
    d=m.document
    if not (d.file_name or "").lower().endswith(".apk") and d.mime_type not in ("application/vnd.android.package-archive","application/octet-stream"):
        await m.answer("Faqat APK hujjatini yuboring."); return
    if d.file_size and d.file_size>settings.max_file_size_mb*1024*1024:
        await m.answer(f"Fayl hajmi {settings.max_file_size_mb} MB limitdan katta."); return
    await state.update_data(file_id=d.file_id,file_name=d.file_name or "app.apk",file_size=d.file_size or 0)
    await state.set_state(UploadAPK.name)
    await m.answer("APK nomini alohida kiriting:")

@router.message(UploadAPK.file)
async def upload_wrong(m:Message): await m.answer("APK faylini document sifatida yuboring. Forward ham mumkin.")

@router.message(UploadAPK.name)
async def upload_name(m:Message,state:FSMContext):
    if not m.text: return await m.answer("APK nomini matn ko'rinishida yuboring.")
    await state.update_data(name=m.text.strip()); await state.set_state(UploadAPK.description)
    await m.answer("Endi APK uchun izoh/tavsifni alohida yozing. Fayl caption'i hisobga olinmaydi:")

@router.message(UploadAPK.description)
async def upload_desc(m:Message,state:FSMContext):
    if not m.text: return await m.answer("Tavsifni alohida matn ko'rinishida yuboring.")
    await state.update_data(description=m.text.strip()); await state.set_state(UploadAPK.code)
    await m.answer("Kod kiriting yoki <code>auto</code> deb yozing:")

@router.message(UploadAPK.code)
async def upload_code(m:Message,state:FSMContext):
    code=(m.text or "").strip()
    data=await state.get_data()
    if code.lower()=="auto" or not code: code="APK"+secrets.token_hex(4).upper()
    async with Session() as s:
        if await s.scalar(select(APK).where(APK.code==code)):
            return await m.answer("Bu kod band. Boshqa kod kiriting:")
    await state.update_data(code=code); await state.set_state(UploadAPK.category)
    await m.answer("Kategoriya nomini yozing (masalan: O'yinlar, Ijtimoiy, Foto-video):")

@router.message(UploadAPK.category)
async def upload_category(m:Message,state:FSMContext):
    data=await state.get_data()
    async with Session() as s:
        a=APK(code=data["code"],name=data["name"],description=data["description"],file_id=data["file_id"],file_name=data["file_name"],file_size=data["file_size"],category=(m.text or "Boshqa").strip())
        s.add(a); await s.commit()
    await state.clear()
    await m.answer(f"✅ APK saqlandi!\nNomi: {a.name}\nKodi: <code>{a.code}</code>\nKategoriya: {a.category}")

@router.message(F.text=="🔎 APK qidirish")
async def ask_search(m:Message,state:FSMContext):
    await state.set_state(SearchAPK.query); await m.answer("APK kodi yoki nomini yuboring:")

@router.message(SearchAPK.query)
async def search(m:Message,state:FSMContext):
    q=(m.text or "").strip()
    async with Session() as s:
        rows=(await s.scalars(select(APK).where(APK.hidden==False, (APK.code==q) | APK.name.ilike(f"%{q}%")).limit(10))).all()
    await state.clear()
    if not rows: return await m.answer("Hech narsa topilmadi. Boshqa nom yoki kod bilan urinib ko'ring.")
    for a in rows: await show_apk(m,a,m.from_user.id)

@router.message(F.text=="📂 Kategoriyalar")
async def categories(m:Message):
    async with Session() as s:
        cats=(await s.scalars(select(APK.category).where(APK.hidden==False).distinct())).all()
    if not cats: return await m.answer("Kategoriyalar hozircha bo'sh.")
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    b=InlineKeyboardBuilder()
    for cat in cats: b.button(text=f"📁 {cat}",callback_data="cat:"+cat[:50])
    b.adjust(2); await m.answer("Kategoriyani tanlang:",reply_markup=b.as_markup())

@router.callback_query(F.data.startswith("cat:"))
async def category_list(c:CallbackQuery):
    cat=c.data[4:]
    async with Session() as s: rows=(await s.scalars(select(APK).where(APK.category==cat,APK.hidden==False).limit(15))).all()
    for a in rows: await show_apk(c.message,a,c.from_user.id)
    await c.answer()

@router.message(F.text=="🆕 Yangi APKlar")
async def latest(m:Message):
    async with Session() as s: rows=(await s.scalars(select(APK).where(APK.hidden==False).order_by(desc(APK.id)).limit(10))).all()
    if not rows: return await m.answer("Hozircha APK mavjud emas.")
    for a in rows: await show_apk(m,a,m.from_user.id)

@router.message(F.text=="🏆 TOP APK")
async def top(m:Message):
    async with Session() as s: rows=(await s.scalars(select(APK).where(APK.hidden==False).order_by(desc(APK.downloads)).limit(10))).all()
    if not rows: return await m.answer("Hozircha reyting bo'sh.")
    for a in rows: await show_apk(m,a,m.from_user.id)

@router.callback_query(F.data.startswith("get:"))
async def get_apk(c:CallbackQuery,bot:Bot):
    aid=int(c.data.split(":")[1])
    async with Session() as s:
        a=await s.get(APK,aid)
        if not a or a.hidden: return await c.answer("APK mavjud emas.",show_alert=True)
        a.downloads+=1; s.add(Download(user_id=c.from_user.id,apk_id=aid)); await s.commit()
    await bot.send_document(c.from_user.id,a.file_id,caption=f"<b>{a.name}</b>\nKod: <code>{a.code}</code>\nVersiya: {a.version}")
    await c.answer("APK yuborildi!")

@router.callback_query(F.data.startswith("fav:"))
async def favorite(c:CallbackQuery):
    aid=int(c.data.split(":")[1])
    async with Session() as s:
        old=await s.scalar(select(Favorite).where(Favorite.user_id==c.from_user.id,Favorite.apk_id==aid))
        if old: await s.delete(old); msg="Sevimlilardan olib tashlandi."
        else: s.add(Favorite(user_id=c.from_user.id,apk_id=aid)); msg="Sevimlilarga qo'shildi."
        await s.commit()
    await c.answer(msg,show_alert=True)

@router.message(F.text=="❤️ Sevimlilar")
async def favorites(m:Message):
    async with Session() as s:
        favs=(await s.scalars(select(Favorite).where(Favorite.user_id==m.from_user.id))).all()
        rows=[]
        for f in favs:
            a=await s.get(APK,f.apk_id)
            if a and not a.hidden: rows.append(a)
    if not rows: return await m.answer("Sevimlilar ro'yxati bo'sh.")
    for a in rows: await show_apk(m,a,m.from_user.id)

@router.message(F.text=="📨 APK so'rash")
async def request_start(m:Message,state:FSMContext):
    await state.set_state(RequestAPK.title); await m.answer("Qaysi ilova kerak? Nomini yozing:")

@router.message(RequestAPK.title)
async def request_save(m:Message,state:FSMContext,bot:Bot):
    async with Session() as s:
        r=Request(user_id=m.from_user.id,title=(m.text or "")[:256]); s.add(r); await s.commit()
    await state.clear(); await m.answer("So'rovingiz adminga yuborildi. Rahmat!")
    for aid in settings.admin_ids:
        try: await bot.send_message(aid,f"📨 Yangi APK so'rovi #{r.id}\n{r.title}\nUser: <code>{r.user_id}</code>")
        except Exception: pass

@router.message(F.text=="👤 Profil")
async def profile(m:Message):
    async with Session() as s:
        u=await s.get(User,m.from_user.id)
        downs=await s.scalar(select(func.count()).select_from(Download).where(Download.user_id==m.from_user.id))
        favs=await s.scalar(select(func.count()).select_from(Favorite).where(Favorite.user_id==m.from_user.id))
    await m.answer(f"<b>Profil</b>\nIsm: {m.from_user.full_name}\nID: <code>{m.from_user.id}</code>\nYuklab olingan: {downs}\nSevimlilar: {favs}")

@router.message(F.text.startswith("/editapk "))
async def edit_apk(m:Message):
    if not is_admin(m.from_user.id): return
    code=m.text.split(maxsplit=1)[1]
    async with Session() as s: a=await s.scalar(select(APK).where(APK.code==code))
    if not a: return await m.answer("Kod topilmadi.")
    await m.answer(f"Joriy: {a.name}\nYangi nom uchun: /renameapk {code} | Yangi nom")

@router.message(F.text.startswith("/renameapk "))
async def rename_apk(m:Message):
    if not is_admin(m.from_user.id): return
    try: _,rest=m.text.split(" ",1); code,name=rest.split("|",1)
    except ValueError: return await m.answer("Format: /renameapk KOD | Yangi nom")
    async with Session() as s:
        a=await s.scalar(select(APK).where(APK.code==code.strip()))
        if not a: return await m.answer("Kod topilmadi.")
        a.name=name.strip(); await s.commit()
    await m.answer("Nom yangilandi.")

@router.message(F.text.startswith("/hideapk "))
async def hide_apk(m:Message):
    if not is_admin(m.from_user.id): return
    code=m.text.split(maxsplit=1)[1]
    async with Session() as s:
        a=await s.scalar(select(APK).where(APK.code==code))
        if not a: return await m.answer("Kod topilmadi.")
        a.hidden=not a.hidden; await s.commit()
    await m.answer("APK holati o'zgartirildi.")

@router.message(F.text.startswith("/delapk "))
async def delete_apk(m:Message):
    if not is_admin(m.from_user.id): return
    code=m.text.split(maxsplit=1)[1]
    async with Session() as s:
        a=await s.scalar(select(APK).where(APK.code==code))
        if not a: return await m.answer("Kod topilmadi.")
        await s.delete(a); await s.commit()
    await m.answer("APK o'chirildi.")

@router.message(AddChannel.chat_id)
async def channel_id(m:Message,state:FSMContext):
    await state.update_data(chat_id=m.text.strip()); await state.set_state(AddChannel.url)
    await m.answer("Kanal havolasini yuboring (https://t.me/...):")

@router.message(AddChannel.url)
async def channel_url(m:Message,state:FSMContext):
    data=await state.get_data()
    async with Session() as s:
        old=await s.scalar(select(Channel).where(Channel.chat_id==data["chat_id"]))
        if not old: s.add(Channel(chat_id=data["chat_id"],title=data["chat_id"],url=m.text.strip()))
        await s.commit()
    await state.clear(); await m.answer("Kanal qo'shildi. Bot kanalga admin qilib qo'yilishi kerak.")

@router.message(EmojiEdit.key)
async def emoji_key(m:Message,state:FSMContext):
    key=(m.text or "").strip()
    await state.update_data(key=key); await state.set_state(EmojiEdit.custom_id)
    await m.answer("Custom emoji ID yuboring. Standart emoji qaytarish uchun: 0")

@router.message(EmojiEdit.custom_id)
async def emoji_id(m:Message,state:FSMContext):
    data=await state.get_data(); cid=(m.text or "").strip()
    async with Session() as s:
        item=await s.get(EmojiMap,data["key"])
        if not item: item=EmojiMap(key=data["key"],emoji=DEFAULTS.get(data["key"],"✨")); s.add(item)
        item.custom_id="" if cid=="0" else cid
        await s.commit()
    await state.clear(); await m.answer("Emoji sozlamasi saqlandi. Eslatma: faqat haqiqiy Telegram custom emoji ID ishlaydi.")

@router.message(Broadcast.message)
async def broadcast(m:Message,bot:Bot,state:FSMContext):
    if not is_admin(m.from_user.id): return
    await state.clear()
    async with Session() as s: ids=(await s.scalars(select(User.id).where(User.blocked==False))).all()
    ok=0
    for uid in ids:
        try: await bot.copy_message(uid,m.chat.id,m.message_id); ok+=1
        except Exception: pass
    await m.answer(f"Xabar yuborish yakunlandi: {ok}/{len(ids)}")

@router.message(F.text.startswith("/setwelcome "))
async def set_welcome(m:Message):
    if not is_admin(m.from_user.id): return
    value=m.text.split(" ",1)[1]
    async with Session() as s:
        item=await s.get(Setting,"welcome")
        if not item: s.add(Setting(key="welcome",value=value))
        else: item.value=value
        await s.commit()
    await m.answer("Xush kelibsiz xabari saqlandi.")
