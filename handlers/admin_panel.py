from datetime import datetime
import contextlib

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards import get_tests_pagination_btns, currentResults, test_start_btn, update_name, test_refresh_start_btn
from states import AdminStates, ReNameUser
from filters import IsAdmins
from data.loader import db
from utils.secondary_funk import make_results_list

rt = Router()
rt.message.filter(IsAdmins())
rt.callback_query.filter(IsAdmins())


""" TEST larni ko'rish """
@rt.message(F.text == "📋 Testlarim")
@rt.callback_query(F.data.startswith("mytests_"))
async def admin_my_tests(event: Message | CallbackQuery):
    # Agar callback bo'lsa sahifani olamiz, aks holda 1-sahifa
    page = 1
    if isinstance(event, CallbackQuery):
        page = int(event.data.split("_")[1])
        await event.answer()

    admin_id = event.from_user.id
    limit = 10
    offset = (page - 1) * limit

    # Bazadan testlarni va umumiy sonini olamiz
    tests = await db.get_admin_tests_paginated(admin_id, limit, offset)
    total_tests = await db.get_admin_tests_count(admin_id)
    total_pages = (total_tests + limit - 1) // limit

    if not tests:
        text = "Sizda hali testlar mavjud emas."
        if isinstance(event, Message):
            await event.answer(text)
        else:
            await event.message.edit_text(text)
        return

    text = "📋 <b>Siz yaratgan testlar:</b>\n\n"
    for i, test in enumerate(tests, offset + 1):
        # test[0]-id, test[1]-title
        text += f"{i}. {test[1]} (Kod: {test[0]}) - /test_{test[0]}\n"

    reply_markup = get_tests_pagination_btns(page, total_pages)

    if isinstance(event, Message):
        await event.answer(text, reply_markup=reply_markup)
    else:
        await event.message.edit_text(text, reply_markup=reply_markup)


@rt.message(F.text.startswith("/test_"))
async def show_test_details(message: Message):
    try:
        test_id = int(message.text.split("_")[1])
    except (IndexError, ValueError):
        return

    test = await db.get_test(test_id) # test_code emas, jadvaldagi ID bo'yicha
    if not test:
        await message.answer("❌ Test topilmadi.")
        return
    sana = test[5].split(' ')[0]
    vaqt = test[5].split(' ')[1]
    results = await db.get_results(int(test_id))
    participants_count = len(results)

    total_percentage = 0
    if participants_count > 0:
        total_percentage = sum(row[2] for row in results) / participants_count # row[2] bu percentage

    user = await db.get_user(message.from_user.id)

    # Bu yerda o'sha test uchun "Natijalar", "Statistika", "To'xtatish" tugmalarini chiqaring
    test_title = test[1]
    test_code = test[0] # Agar kod 3-indexda bo'lsa
    test_answers = test[2]
    status = test[3]

    if status == "waiting":
        await message.answer("<b>Test yaratildi ✅</b>\n\n"
                         f"<b>✍️ Test:</b> {test_title}\n"
                         f"<b>👨‍🏫 Muallif:</b> {user[1]}\n"
                         f"<b>🔢 Test kodi:</b> <code>{test_code}</code>\n"
                         f"<b>❓ Savollar:</b> {len(test_answers)} ta\n"
                         "<b>⏳ Holati:</b> Boshlanmagan\n\n"
                         f"<i>📆 {sana} ⏰ {vaqt}</i>",
                         reply_markup=test_start_btn(test_code))
    elif status == "active":
        matn = make_results_list(results)
        text = (
            f"📋 <b>Test ma'lumotlari</b>\n\n"
            f"<b>Nomi:</b> {test_title}\n"
            f"<b>Kodi:</b> <code>{test_code}</code>\n"
            f"<b>👥 Qatnashganlar:</b> {participants_count} ta\n"
            f"<b>Holati:</b> Boshlangan\n\n"
            f"<b>Natijalar:</b>\n"
            f"---------------------\n"
            f"{matn}"
        )
        await message.answer(text, reply_markup=currentResults(test_code))
    elif status == "closed":
        text = (
            f"📋 <b>Test ma'lumotlari</b>\n\n"
            f"<b>Nomi:</b> {test_title}\n"
            f"<b>Kodi:</b> <code>{test_code}</code>\n"
            f"<b>👥 Qatnashganlar:</b> {participants_count} ta\n"
            f"<b>📊 Umumiy o'rtacha natija:</b> {total_percentage:.1f}%\n\n"
            f"<b>Holati:</b> Yakunlangan"
        )
        await message.answer(text)
        # await message.answer(text, reply_markup=test_refresh_start_btn(test_code))


""" Statistikani ko'rish """
@rt.message(F.text == "📈 Statistika") # Rasmda grafik emojisi bor edi
async def admin_statistics(message: Message):
    # Ma'lumotlarni bazadan olamiz
    users_count = await db.count_users()
    tests_count = await db.count_all_tests()
    admins_count = await db.count_admins()
    channels_count = await db.count_channels()
    
    # Bugungi sanani ko'rsatish (ixtiyoriy, lekin professional ko'rinadi)
    from datetime import datetime
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    text = (
        "<b>📈 Botning umumiy statistikasi</b>\n\n"
        f"👤 <b>Foydalanuvchilar:</b> {users_count} ta\n"
        f"📝 <b>Jami testlar:</b> {tests_count} ta\n"
        f"👨‍💻 <b>Adminlar:</b> {admins_count} ta\n"
        f"📢 <b>Majburiy kanallar:</b> {channels_count} ta\n\n"
        "----------------------------------\n"
        f"<i>🕒 Yangilangan vaqt: {now}</i>"
    )
    
    await message.answer(text)


""" Xabar yuborish """
@rt.message(F.text == "✉️ Xabar yuborish")
async def start_broadcast(message: Message, state: FSMContext):
    await message.answer("Barcha foydalanuvchilarga yuboriladigan xabarni kiriting:")
    await state.set_state(AdminStates.waiting_for_broadcast)

@rt.message(AdminStates.waiting_for_broadcast)
async def send_broadcast(message: Message, state: FSMContext):
    users = await db.get_all_users() # barcha tg_id larni olish
    count = 0
    
    for user_id in users:
        try:
            await message.copy_to(chat_id=user_id[0])
            count += 1
        except Exception:
            continue
            
    await message.answer(f"✅ Xabar {count} ta foydalanuvchiga yuborildi.")
    await state.clear()


""" Admin profile """
@rt.message(F.text == "👤 Profile")
async def admin_profile(message: Message):
    user = await db.get_user(message.from_user.id)
    role = user[4]
    joined_date = user[3].split(' ')[0] if user[3] else "Noma'lum"
    
    text = (
        f"<b>👤 Admin Profili</b>\n\n"
        f"<b>Ism:</b> {user[1]}\n"
        f"<b>Daraja:</b> {role}\n"
        f"<b>Botga a'zo bo'lingan:</b> {joined_date}"
    )
    await message.answer(text, reply_markup=update_name)