from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from keyboards import ownerMenu, adminsMenu, back_btn, get_admin_btn, checkerDelBtn, adminsListBtn
from states import AddAdmin, DelAdmin
from filters import IsOwner
from data.loader import db
from utils.secondary_funk import make_admins_list
from data.config import ADMIN
from data.loader import update_admins_cache


rt = Router()
rt.message.filter(IsOwner())
rt.callback_query.filter(IsOwner())


# Adminlarni boshqarish
@rt.message(F.text == "👨‍💻 Adminlar")
async def send_channels_list(message:Message, state:FSMContext):
    admins = await db.get_admins()
    matn = make_admins_list(admins)
    
    await message.answer(matn, reply_markup=adminsMenu(len(admins)))
    await state.set_state(AddAdmin.admins)
    await state.set_data({"admins":admins})


# Admin qo'shish
@rt.callback_query(F.data == "add_admin", AddAdmin.admins)
async def ask_admin_id(call:CallbackQuery, state:FSMContext):
    await call.message.delete()
    await call.message.answer("<b>➕ Admin qo'shish</b>\n\nUserdan biror xabarni forward qiling yokida quyidagi tugma orqali uni menga ulashing.", reply_markup=get_admin_btn)
    await state.set_state(AddAdmin.admin_id)


@rt.message(F.text == "↩️ Orqaga", AddAdmin.admin_id)
async def back_add_admin_(message:Message, state:FSMContext):
    data = await state.get_data()
    admins = data.get("admins", [])

    matn = make_admins_list(admins)
    
    user_id = message.from_user.id
    await message.answer("Yangi admin qo'shilmadi.", reply_markup=ownerMenu(user_id))
    await message.answer(matn, reply_markup=adminsMenu(len(admins)))
    await state.set_state(AddAdmin.admins)


@rt.message(AddAdmin.admin_id, F.forward_from | F.users_shared)
async def get_admin_id(message:Message, state:FSMContext, bot:Bot):
    if message.forward_from:
        new_admin = message.forward_from.id
    else:
        new_admin = message.users_shared.users[0].user_id

    data = await state.get_data()
    admins = data.get("admins", [])

    user = await db.get_user(new_admin)
    if user:
        if not user[4] in ['owner', 'admin']:
            await db.make_admin(new_admin)
            admins.append(user)
            await state.update_data(admins=admins)
            await update_admins_cache()

            try:
                await bot.send_message(user[2], "<b>Sizga admin huquqi berilgani bilan tabriklayman</b> - 🎉\n\nQayta /start bosish orqali admin panelga o'tishingiz mumkin.")
            except Exception as e:
                print(f"Xabar yuborib bo'lmadi: {e}")

            await message.answer(f"<b><a href='tg://user?id={user[2]}'>{user[1]}</a></b> ga admin huquqi berildi va unga bu haqida xabar yuborildi - ✅", reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer("Bu foydalanuvchiga avvalroq admin huquqi berilgan ⚠️", reply_markup=ReplyKeyboardRemove())

        matn = make_admins_list(admins)
        await message.answer(matn, reply_markup=adminsMenu(len(admins)))
        await state.set_state(AddAdmin.admins)
    else:
        await message.answer("Bu foydalanuvchi botga start bosmagan. Admin huquqini berish uchun oldin foydalanuvchi botga /start bosishi kerak.")


@rt.message(AddAdmin.admin_id)
async def send_error_admin_id(message:Message, state:FSMContext):
    await message.answer("Iltimos xabarni forward qilib yuboring !", reply_markup=back_btn)


@rt.callback_query(F.data == "back_", AddAdmin.admin_id)
async def back_add_admin_(call:CallbackQuery, state:FSMContext):
    data = await state.get_data()
    admins = data.get("admins", [])

    matn = make_admins_list(admins)
    
    user_id = call.from_user.id
    await call.message.delete()
    await call.message.answer("Yangi admin qo'shilmadi.", reply_markup=ownerMenu(user_id))
    await call.message.answer(matn, reply_markup=adminsMenu(len(admins)))
    await state.set_state(AddAdmin.admins)


# Admin uzish
@rt.callback_query(F.data == "del_admin", AddAdmin.admins)
async def ask_admin_id_for_del_admin(call:CallbackQuery, state:FSMContext):
    data = await state.get_data()
    admins = data.get("admins", [])
    
    await call.message.delete()
    await call.message.answer("<b>➖ Admin o'chirish</b>\n\nBekor qilmoqchi bo'lgan adminni tanlang.", reply_markup=adminsListBtn(admins))
    await state.set_state(DelAdmin.admin_id)


@rt.callback_query(F.data.startswith("del_admin_"), DelAdmin.admin_id)
async def get_admin_id_for_del_admin(call:CallbackQuery, state:FSMContext):
    admin_id = call.data.split('_')[2]
    if int(admin_id) == ADMIN:
        await call.answer("Bot yaratuvchisini adminlikdan olib bo'lmaydi ❌", show_alert=True)
    else:
        id_link = f"tg://user?id={admin_id}"
        await call.message.delete()
        await call.message.answer(f"<a href='{id_link}'>Adminni</a> ni o'chirishni tasdiqlang.", reply_markup=checkerDelBtn(admin_id))
        await state.set_state(DelAdmin.is_checked)


@rt.callback_query(F.data.startswith("yes_"), DelAdmin.is_checked)
async def del_admin_yes(call:CallbackQuery, state:FSMContext):
    admin_id = call.data.split('_')[1]
    await db.remove_admin(int(admin_id))
    await update_admins_cache()

    admins = await db.get_admins()
    await state.update_data(admins=admins)

    matn = make_admins_list(admins)
    
    await call.message.delete()
    await call.message.answer("Admin bekor qilindi ✅")
    await call.message.answer(matn, reply_markup=adminsMenu(len(admins)))
    await state.set_state(AddAdmin.admins)


@rt.callback_query(F.data == "no", DelAdmin.is_checked)
async def del_admin_no(call:CallbackQuery, state:FSMContext):
    data = await state.get_data()
    admins = data.get("admins", [])

    matn = make_admins_list(admins)
    
    await call.message.delete()
    await call.message.answer(matn, reply_markup=adminsMenu(len(admins)))
    await state.set_state(AddAdmin.admins)


@rt.callback_query(F.data == "back_del_admin", DelAdmin.admin_id)
async def back_del_admin_(call:CallbackQuery, state:FSMContext):
    data = await state.get_data()
    admins = data.get("admins", [])

    matn = make_admins_list(admins)
    
    await call.message.delete()
    await call.message.answer(matn, reply_markup=adminsMenu(len(admins)))
    await state.set_state(AddAdmin.admins)