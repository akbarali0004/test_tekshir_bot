from datetime import datetime
import contextlib

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from keyboards import test_duration_btn, test_start_btn, currentResults, refresh_current_results
from states import CreateTest
from filters import IsAdmins
from data.loader import db
from utils.secondary_funk import make_results_list

rt = Router()
rt.message.filter(IsAdmins())
rt.callback_query.filter(IsAdmins())


""" TEST YARATISH """
@rt.message(F.text == "➕ Test yaratish")
async def create_test(message:Message, state:FSMContext):
    await message.answer("<b>Test nomini kiriting:</b>\n\n<b>Namuna:</b> <i>Matematika</i>")
    await state.set_state(CreateTest.title)


@rt.message(F.text, CreateTest.title)
async def get_new_test_name(message:Message, state:FSMContext):
    await message.answer(f"<b>{message.text}</b> testi uchun javoblarni yuboring:\n\n<b>Namuna:</b>\n<i>abcd...\nyoki\n1a2b3c4d...</i>")
    await state.set_data({"test_title": message.text})
    await state.set_state(CreateTest.answers)


@rt.message(F.text, CreateTest.answers)
async def get_new_test_answer(message:Message, state:FSMContext):
    data = await state.get_data()
    test_title = data.get("test_title", "Nomsiz test")

    user = await db.get_user(message.from_user.id)
    test_code = await db.add_test(test_title, message.text, user[2])

    now = datetime.now()
    sana = now.strftime("%d.%m.%Y") # 26.04.2026
    vaqt = now.strftime("%H:%M")

    await message.answer("<b>Test yaratildi ✅</b>\n\n"
                         f"<b>✍️ Test:</b> {test_title}\n"
                         f"<b>👨‍🏫 Muallif:</b> {user[1]}\n"
                         f"<b>🔢 Test kodi:</b> <code>{test_code}</code>\n"
                         f"<b>❓ Savollar:</b> {len(message.text)} ta\n"
                         "<b>⏳ Holati:</b> boshlanmagan\n\n"
                         f"<i>📆 {sana} ⏰ {vaqt}</i>",
                         reply_markup=test_start_btn(test_code))
    await state.clear()
    
    # await message.answer("Test davomiyligini kiriting.\n\n"
    #                      "Quyidan tanlashingiz yokida qo'lda namunadagi kabi kiritishingiz mumkin.\n"
    #                      "Namuna: 1soat, 1kun, 1hafta, ...", reply_markup=test_duration_btn)
    # await state.set_state(CreateTest.duration)


# @rt.message(F.text, CreateTest.duration)
# async def get_new_test_start_time(message:Message, state:FSMContext):
#     await message.answer("<b>Matematika</b> testi\n\n"
#                          "Test kodi: <code>111</code>\n"
#                          "Savollar: 15 ta\n"
#                          "Davomiyligi: 3 soat\n"
#                          "Holati: Boshlanmagan\n", reply_markup=test_btn)
#     await state.clear()
    

@rt.callback_query(F.data.startswith("start_test_"))
@rt.callback_query(F.data.startswith("start_refresh_test_"))
async def start_test(call:CallbackQuery):
    if call.data.startswith("start_refresh_test_"):
        test_code = call.data.split('_')[3]
        await db.del_results(int(test_code))
    else:
        test_code = call.data.split('_')[2]
    

    await db.test_update_status(test_code, "active")
    test = await db.get_test(int(test_code))
    test_title = test[1]
    tests = test[2]
    await call.message.delete()
    await call.message.answer(f"<b>🔔 {test_title}</b> testi boshlandi.\n\n"
                              f"<b>🔢 Test kodi:</b> <code>{test_code}</code>\n"
                              f"<b>❓ Savollar:</b> {len(tests)} ta\n"
                              "<b>⏳ Holati:</b> boshlangan\n\n",
                              reply_markup=currentResults(test_code))


@rt.callback_query(F.data.startswith("current_results_"))
async def current_results_info(call:CallbackQuery):
    test_code = call.data.split('_')[2]
    results  = await db.get_results(int(test_code))

    matn = make_results_list(results)

    await call.message.delete()
    await call.message.answer("<b>📈 Joriy Natijalar</b>\n\n"
                              f"<b>🔢 Test kodi:</b> <code>{test_code}</code>\n"
                              f"<b>👥 Qatnashuvchilar:</b> {len(results)} ta\n"
                              "<b>⏳ Holati:</b> boshlangan\n\n"
                              "<b>Natijalar:</b>\n"
                              "---------------------\n" + matn,
                              reply_markup=refresh_current_results(test_code))


@rt.callback_query(F.data.startswith("refresh_"))
async def current_info(call:CallbackQuery):
    await call.answer()
    test_code = call.data.split('_')[1]
    results  = await db.get_results(int(test_code))

    matn = make_results_list(results)
    
    await call.message.delete()
    await call.message.answer("<b>📈 Joriy Natijalar</b>\n\n"
                            f"<b>🔢 Test kodi:</b> <code>{test_code}</code>\n"
                            f"<b>👥 Qatnashuvchilar:</b> {len(results)} ta\n"
                            "<b>⏳ Holati:</b> boshlangan\n\n"
                            "<b>Natijalar:</b.\n"
                            "---------------------\n"
                            f"{matn}",
                            reply_markup=refresh_current_results(test_code))


@rt.callback_query(F.data.startswith("stop_test_"))
async def finished_test_ans(call: CallbackQuery):
    test_code = call.data.split('_')[2]
    
    # 1. Test statusini 'closed' (yakunlangan)ga o'zgartiramiz
    await db.test_update_status(test_code, "closed")
    
    # 2. Test va natijalar ma'lumotlarini olamiz
    test = await db.get_test(int(test_code))
    results = await db.get_results(int(test_code))
    
    test_title = test[1]
    participants_count = len(results)
    
    # 3. Umumiy o'rtacha natijani hisoblash (percentage larning o'rtachasi)
    total_percentage = 0
    if participants_count > 0:
        total_percentage = sum(row[2] for row in results) / participants_count # row[2] bu percentage
    
    # 4. Natijalar ro'yxatini shakllantirish
    matn = make_results_list(results)
    if not matn:
        matn = "Ishtirokchilar mavjud emas."

    # 5. Xabarni chiqarish
    await call.message.delete() # Oldingi menyuni o'chiramiz
    
    response_text = (
        f"🏁 <b>{test_title} testi yakunlandi.</b>\n\n"
        f"<b>🔢 Test kodi:</b> <code>{test_code}</code>\n"
        f"<b>👥 Qatnashganlar:</b> {participants_count} ta\n"
        f"<b>📊 Umumiy o'rtacha natija:</b> {total_percentage:.1f}%\n\n"
        f"<b>Natijalar:</b>\n"
        f"---------------------\n"
        f"{matn}"
    )
    
    await call.message.answer(response_text)


