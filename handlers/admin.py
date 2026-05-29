from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import STATUSES, COMPLAINT_TYPES, ADMIN_IDS
import database as db

router = Router()

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

class AdminComment(StatesGroup):
    waiting_comment = State()

def admin_main_menu():
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="🆕 Yangi murojaatlar")],
        [KeyboardButton(text="⏳ Jarayondagi"), KeyboardButton(text="✔️ Bajarilganlar")],
        [KeyboardButton(text="📋 Barcha murojaatlar")],
    ], resize_keyboard=True)

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer(
        "👮 <b>Admin panel</b>\n\nXush kelibsiz, admin!",
        parse_mode="HTML",
        reply_markup=admin_main_menu()
    )

@router.message(F.text == "📊 Statistika")
async def statistics(message: Message):
    if not is_admin(message.from_user.id):
        return
    stats = await db.get_statistics()
    await message.answer(
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{stats['users']}</b>\n\n"
        f"📋 Jami murojaatlar: <b>{stats['total']}</b>\n"
        f"🆕 Yangi: <b>{stats['yangi']}</b>\n"
        f"✅ Qabul qilingan: <b>{stats['qabul_qilindi']}</b>\n"
        f"⏳ Jarayonda: <b>{stats['jarayonda']}</b>\n"
        f"✔️ Bajarilgan: <b>{stats['bajarildi']}</b>",
        parse_mode="HTML",
        reply_markup=admin_main_menu()
    )

@router.message(F.text.in_(["🆕 Yangi murojaatlar", "⏳ Jarayondagi", "✔️ Bajarilganlar", "📋 Barcha murojaatlar"]))
async def view_complaints(message: Message):
    if not is_admin(message.from_user.id):
        return

    status_map = {
        "🆕 Yangi murojaatlar": "yangi",
        "⏳ Jarayondagi": "jarayonda",
        "✔️ Bajarilganlar": "bajarildi",
        "📋 Barcha murojaatlar": None,
    }
    status = status_map.get(message.text)
    complaints = await db.get_all_complaints(status)

    if not complaints:
        await message.answer("📭 Murojaatlar topilmadi.", reply_markup=admin_main_menu())
        return

    for c in complaints[:10]:
        type_label = COMPLAINT_TYPES.get(c["complaint_type"], c["complaint_type"])
        status_label = STATUSES.get(c["status"], c["status"])
        text = (
            f"🔢 <b>Murojaat #{c['id']}</b>\n"
            f"📋 Tur: {type_label}\n"
            f"📍 Manzil: {c['location_text']}\n"
            f"💬 Izoh: {c['description'] or 'Yo\'q'}\n"
            f"📅 Sana: {c['created_at']}\n"
            f"🔖 Holat: {status_label}"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Qabul", callback_data=f"admin_accept_{c['id']}"),
                InlineKeyboardButton(text="❌ Rad", callback_data=f"admin_reject_{c['id']}"),
            ],
            [
                InlineKeyboardButton(text="⏳ Jarayonda", callback_data=f"admin_progress_{c['id']}"),
                InlineKeyboardButton(text="✔️ Bajarildi", callback_data=f"admin_done_{c['id']}"),
            ],
        ])
        if c["photo_id"]:
            await message.answer_photo(c["photo_id"], caption=text, parse_mode="HTML", reply_markup=kb)
        else:
            await message.answer(text, parse_mode="HTML", reply_markup=kb)

# ─── INLINE TUGMALAR ─────────────────────────────────────────────────────────

async def update_status(call: CallbackQuery, complaint_id: int, new_status: str, bot: Bot, comment: str = None):
    await db.update_complaint_status(complaint_id, new_status, comment)
    complaint = await db.get_complaint_by_id(complaint_id)
    status_label = STATUSES.get(new_status, new_status)

    await call.answer(f"{status_label} ✓")
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(f"✅ Murojaat #{complaint_id} holati: <b>{status_label}</b>", parse_mode="HTML")

    # Foydalanuvchiga xabar yuborish
    if complaint:
        user_text = (
            f"📬 <b>Murojaatingiz holati yangilandi</b>\n\n"
            f"🔢 Murojaat #{complaint_id}\n"
            f"🔖 Yangi holat: <b>{status_label}</b>\n"
        )
        if comment:
            user_text += f"💬 Admin izohi: {comment}"
        try:
            await bot.send_message(complaint["telegram_id"], user_text, parse_mode="HTML")
        except:
            pass

@router.callback_query(F.data.startswith("admin_accept_"))
async def accept_complaint(call: CallbackQuery, bot: Bot):
    if not is_admin(call.from_user.id):
        return
    complaint_id = int(call.data.split("_")[-1])
    await update_status(call, complaint_id, "qabul_qilindi", bot)

@router.callback_query(F.data.startswith("admin_reject_"))
async def reject_complaint(call: CallbackQuery, bot: Bot, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    complaint_id = int(call.data.split("_")[-1])
    await state.update_data(complaint_id=complaint_id, action="rad_etildi")
    await state.set_state(AdminComment.waiting_comment)
    await call.message.answer(f"❌ Murojaat #{complaint_id} uchun rad sababi yozing:")
    await call.answer()

@router.callback_query(F.data.startswith("admin_progress_"))
async def progress_complaint(call: CallbackQuery, bot: Bot):
    if not is_admin(call.from_user.id):
        return
    complaint_id = int(call.data.split("_")[-1])
    await update_status(call, complaint_id, "jarayonda", bot)

@router.callback_query(F.data.startswith("admin_done_"))
async def done_complaint(call: CallbackQuery, bot: Bot):
    if not is_admin(call.from_user.id):
        return
    complaint_id = int(call.data.split("_")[-1])
    await update_status(call, complaint_id, "bajarildi", bot)

@router.message(AdminComment.waiting_comment)
async def get_admin_comment(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    complaint_id = data.get("complaint_id")
    action = data.get("action", "rad_etildi")
    await state.clear()

    await db.update_complaint_status(complaint_id, action, message.text)
    status_label = STATUSES.get(action, action)
    await message.answer(f"✅ Murojaat #{complaint_id} holati: <b>{status_label}</b>", parse_mode="HTML")

    complaint = await db.get_complaint_by_id(complaint_id)
    if complaint:
        try:
            await bot.send_message(
                complaint["telegram_id"],
                f"📬 <b>Murojaatingiz holati yangilandi</b>\n\n"
                f"🔢 Murojaat #{complaint_id}\n"
                f"🔖 Holat: <b>{status_label}</b>\n"
                f"💬 Sabab: {message.text}",
                parse_mode="HTML"
            )
        except:
            pass
