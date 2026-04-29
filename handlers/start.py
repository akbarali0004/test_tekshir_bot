from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

from keyboards import user_menu, admin_menu, ownerMenu
from states import RegisterState
from data.loader import db

rt = Router()


@rt.message(CommandStart())
async def start_handler(message: Message, state:FSMContext):
    user_id = message.from_user.id
    user = await db.get_user(user_id)

    await state.clear()

    if user:
        full_name = user[1]
        role = user[4]

        if role == 'owner':
            await message.answer(f"Xush kelibsiz, Admin <b>{full_name}</b>!\n\nBoshqaruv paneli ishga tushdi.", reply_markup=ownerMenu(user_id))
        elif role == 'admin':
            await message.answer(f"Xush kelibsiz, Admin <b>{full_name}</b>!\n\nBoshqaruv paneli ishga tushdi.", reply_markup=admin_menu)
        else:
            await message.answer(f"Xush kelibsiz, <b>{full_name}</b>!\n\nQuyidagi paneldan foydalanishingiz mumkin.", reply_markup=user_menu)
    else:
        await db.add_user(message.from_user.id, message.from_user.full_name)
        await message.answer("<b>👋🏻 Assalomu aleykum </b>")
        await message.answer("Ism familiyangizni kiriting.\n\n"
                            "Agar ism familiyangizni kiritmasangiz sizni tanitish uchun telegram nomingizdan foydalanamiz, "
                            "buning uchun yuboring - /skip")
        await state.set_state(RegisterState.name)


@rt.callback_query(F.data == "check_subs:start")
async def handler(call: CallbackQuery, state:FSMContext):
    user_id = call.message.from_user.id
    user = await db.get_user(user_id)

    await call.message.delete()
    await state.clear()

    if user:
        full_name = user[1]
        role = user[4]

        if role == 'owner':
            await call.message.answer(f"Xush kelibsiz, Admin <b>{full_name}</b>!\n\nBoshqaruv paneli ishga tushdi.", reply_markup=ownerMenu(user_id))
        elif role == 'admin':
            await call.message.answer(f"Xush kelibsiz, Admin <b>{full_name}</b>!\n\nBoshqaruv paneli ishga tushdi.", reply_markup=admin_menu)
        else:
            await call.message.answer(f"Xush kelibsiz, <b>{full_name}</b>!\n\nQuyidagi paneldan foydalanishingiz mumkin.", reply_markup=user_menu)
    else:
        await db.add_user(call.from_user.id, call.from_user.full_name)
        await call.message.answer("<b>👋🏻 Assalomu aleykum </b>")
        await call.message.answer("Ism familiyangizni kiriting.\n\n"
                            "Agar ism familiyangizni kiritmasangiz sizni tanitish uchun telegram nomingizdan foydalanamiz, "
                            "buning uchun yuboring - /skip")
        await state.set_state(RegisterState.name)


@rt.message(Command("skip"), RegisterState.name)
async def skip_name(message:Message, state:FSMContext):
    await message.answer(f"Xush kelibsiz, <b>{message.from_user.full_name}</b>!\n\nQuyidagi paneldan foydalanishingiz mumkin.", reply_markup=user_menu)
    await state.clear()


@rt.message(F.text, RegisterState.name)
async def get_user_name(message:Message, state:FSMContext):
    user_id = message.from_user.id
    full_name = message.text
    await db.update_fullname(user_id, full_name)

    await message.answer(f"Rahmat, <b>{full_name}</b>! Ro'yxatdan o'tdingiz.\n\nQuyidagi paneldan foydalanishingiz mumkin.", reply_markup=user_menu)
    await state.clear()