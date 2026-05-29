from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import COMPLAINT_TYPES, STATUSES, ADMIN_IDS
import database as db

router = Router()

class ComplaintForm(StatesGroup):
    choosing_type = State()
    sending_location = State()
    sending_description = State()
    sending_photo = State()

def main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📝 Murojaat yuborish")],
        [KeyboardButton(text="📋 Mening murojaatlarim")],
        [KeyboardButton(text="ℹ️ Yordam")],
    ], resize_keyboard=True)

def complaint_types_keyboard():
    buttons = []
    for key, label in COMPLAINT_TYPES.items():
        buttons.append([InlineKeyboardButton(text=label, callback_data=f"type_{key}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def location_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📍 Lokatsiya yuborish", request_location=True)],
        [KeyboardButton(text="✏️ Manzilni yozish")],
        [KeyboardButton(text="❌ Bekor qilish")],
    ], resize_keyboard=True)

def skip_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="⏭ O'tkazib yuborish")],
        [KeyboardButton(text="❌ Bekor qilish")],
    ], resize_keyboard=True)

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await db.save_user(message.from_user.id, message.from_user.full_name)
    await message.answer(
        f"🌿 <b>MGAS botiga xush kelibsiz!</b>\n\n"
        f"Salom, <b>{message.from_user.full_name}</b>!\n\n"
        f"Toza makon – toza kelajak! 🌱\n"
        f"Chiqindi bilan bog'liq muammolarni birgalikda yechamiz!\n\n"
        f"Quyidagi tugmalardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=main_menu()
    )

@router.message(F.text == "ℹ️ Yordam")
async def help_handler(message: Message):
    await message.answer(
        "ℹ️ <b>Yordam</b>\n\n"
        "📝 <b>Murojaat yuborish</b> — chiqindi bilan bog'liq muammo haqida xabar bering\n"
        "📋 <b>Mening murojaatlarim</b> — yuborgan murojaatlaringiz holati\n\n"
        "<b>Murojaat turlari:</b>\n"
        "🗑 Chiqindi olinmagan\n"
        "♻️ Noto'g'ri chiqindi\n"
        "🚮 Konteyner to'lgan\n"
        "🚛 Texnika muammosi\n"
        "👷 Xodim muammosi\n"
        "📋 Boshqa muammo\n\n"
        "📞 Muammo bo'lsa: @mgas_support",
        parse_mode="HTML",
        reply_markup=main_menu()
    )

@router.message(F.text == "❌ Bekor qilish")
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Bekor qilindi.", reply_markup=main_menu())

# ─── MUROJAAT YUBORISH ────────────────────────────────────────────────────────

@router.message(F.text == "📝 Murojaat yuborish")
async def start_complaint(message: Message, state: FSMContext):
    await state.set_state(ComplaintForm.choosing_type)
    await message.answer(
        "📋 <b>Muammo turini tanlang:</b>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer("👇", reply_markup=complaint_types_keyboard())

@router.callback_query(F.data.startswith("type_"), ComplaintForm.choosing_type)
async def type_chosen(call: CallbackQuery, state: FSMContext):
    type_key = call.data.replace("type_", "")
    type_label = COMPLAINT_TYPES.get(type_key, "Noma'lum")
    await state.update_data(complaint_type=type_key, complaint_type_label=type_label)
    await state.set_state(ComplaintForm.sending_location)
    await call.message.edit_reply_markup()
    await call.message.answer(
        f"✅ Tanlandi: <b>{type_label}</b>\n\n"
        f"📍 <b>Manzilni yuboring:</b>\n"
        f"Lokatsiya tugmasini bosing yoki manzilni yozing.",
        parse_mode="HTML",
        reply_markup=location_keyboard()
    )
    await call.answer()

@router.message(ComplaintForm.sending_location, F.location)
async def location_received(message: Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude
    await state.update_data(latitude=lat, longitude=lon, location_text=f"{lat:.5f}, {lon:.5f}")
    await state.set_state(ComplaintForm.sending_description)
    await message.answer(
        "✅ Lokatsiya qabul qilindi!\n\n"
        "💬 <b>Muammo haqida qisqacha yozing</b> (ixtiyoriy):",
        parse_mode="HTML",
        reply_markup=skip_keyboard()
    )

@router.message(ComplaintForm.sending_location, F.text == "✏️ Manzilni yozish")
async def ask_manual_address(message: Message):
    await message.answer("✏️ Manzilni yozing (masalan: Navbahor MFY, 12-uy):", reply_markup=ReplyKeyboardRemove())

@router.message(ComplaintForm.sending_location, F.text)
async def manual_address(message: Message, state: FSMContext):
    if message.text in ["❌ Bekor qilish", "⏭ O'tkazib yuborish"]:
        return
    await state.update_data(latitude=None, longitude=None, location_text=message.text)
    await state.set_state(ComplaintForm.sending_description)
    await message.answer(
        f"✅ Manzil: <b>{message.text}</b>\n\n"
        f"💬 <b>Muammo haqida qisqacha yozing</b> (ixtiyoriy):",
        parse_mode="HTML",
        reply_markup=skip_keyboard()
    )

@router.message(ComplaintForm.sending_description)
async def description_received(message: Message, state: FSMContext):
    description = "" if message.text == "⏭ O'tkazib yuborish" else message.text
    await state.update_data(description=description)
    await state.set_state(ComplaintForm.sending_photo)
    await message.answer(
        "📸 <b>Rasm yuboring</b> (ixtiyoriy):\n"
        "Muammo joyining rasmini yuboring yoki o'tkazib yuboring.",
        parse_mode="HTML",
        reply_markup=skip_keyboard()
    )

@router.message(ComplaintForm.sending_photo, F.photo)
async def photo_received(message: Message, state: FSMContext, bot: Bot):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)
    await finish_complaint(message, state, bot)

@router.message(ComplaintForm.sending_photo, F.text == "⏭ O'tkazib yuborish")
async def skip_photo(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(photo_id=None)
    await finish_complaint(message, state, bot)

async def finish_complaint(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    complaint_id = await db.save_complaint(
        telegram_id=message.from_user.id,
        complaint_type=data.get("complaint_type"),
        location_text=data.get("location_text", "Noma'lum"),
        lat=data.get("latitude"),
        lon=data.get("longitude"),
        description=data.get("description", ""),
        photo_id=data.get("photo_id"),
    )
    await state.clear()

    type_label = data.get("complaint_type_label", "Noma'lum")
    location = data.get("location_text", "Noma'lum")
    description = data.get("description") or "Izoh yo'q"

    await message.answer(
        f"✅ <b>Murojaatingiz qabul qilindi!</b>\n\n"
        f"🔢 Murojaat raqami: <b>#{complaint_id}</b>\n"
        f"📋 Tur: {type_label}\n"
        f"📍 Manzil: {location}\n"
        f"💬 Izoh: {description}\n\n"
        f"Murojaatingiz tez orada ko'rib chiqiladi. 🙏",
        parse_mode="HTML",
        reply_markup=main_menu()
    )

    # Adminlarga xabar yuborish
    admin_text = (
        f"🆕 <b>Yangi murojaat #{complaint_id}</b>\n\n"
        f"👤 Foydalanuvchi: {message.from_user.full_name} (@{message.from_user.username or 'noname'})\n"
        f"🆔 ID: <code>{message.from_user.id}</code>\n"
        f"📋 Tur: {type_label}\n"
        f"📍 Manzil: {location}\n"
        f"💬 Izoh: {description}"
    )
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"admin_accept_{complaint_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"admin_reject_{complaint_id}"),
        ],
        [InlineKeyboardButton(text="⏳ Jarayonda", callback_data=f"admin_progress_{complaint_id}")],
        [InlineKeyboardButton(text="✔️ Bajarildi", callback_data=f"admin_done_{complaint_id}")],
    ])

    for admin_id in ADMIN_IDS:
        try:
            if data.get("photo_id"):
                await bot.send_photo(admin_id, data["photo_id"], caption=admin_text, parse_mode="HTML", reply_markup=admin_kb)
            else:
                await bot.send_message(admin_id, admin_text, parse_mode="HTML", reply_markup=admin_kb)
        except Exception as e:
            print(f"Admin {admin_id} ga yuborishda xatolik: {e}")

# ─── MENING MUROJAATLARIM ─────────────────────────────────────────────────────

@router.message(F.text == "📋 Mening murojaatlarim")
async def my_complaints(message: Message):
    complaints = await db.get_user_complaints(message.from_user.id)
    if not complaints:
        await message.answer("📭 Sizda hali murojaatlar yo'q.", reply_markup=main_menu())
        return

    text = "📋 <b>Sizning murojaatlaringiz:</b>\n\n"
    for c in complaints[:10]:
        status_label = STATUSES.get(c["status"], c["status"])
        type_label = COMPLAINT_TYPES.get(c["complaint_type"], c["complaint_type"])
        text += (
            f"🔢 <b>#{c['id']}</b> — {type_label}\n"
            f"📍 {c['location_text']}\n"
            f"📅 {c['created_at']}\n"
            f"🔖 Holat: {status_label}\n"
        )
        if c["admin_comment"]:
            text += f"💬 Admin izohi: {c['admin_comment']}\n"
        text += "\n"

    await message.answer(text, parse_mode="HTML", reply_markup=main_menu())
