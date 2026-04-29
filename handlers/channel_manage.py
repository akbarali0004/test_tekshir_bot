import logging

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import LinkPreviewOptions

from keyboards import ownerMenu, back_btn, get_channel, channelsMenu, channelsListBtn, checkerDelBtn
from states import AddChannel, DelChannel
from filters import IsOwner
from data.loader import db, update_channels_cache
from utils.secondary_funk import make_channels_list


rt = Router()
rt.message.filter(IsOwner())
rt.callback_query.filter(IsOwner())


""" Majburiy obuna bo'limi """
@rt.message(F.text == "📢 Majburiy obuna")
async def send_channels_list(message:Message, state:FSMContext):
    channels = await db.get_channels()
    matn = make_channels_list(channels)
    
    await message.answer(matn, reply_markup=channelsMenu(len(channels)))
    await state.set_state(AddChannel.channels)
    await state.set_data({"channels":channels})


# Kanal qo'shish
@rt.callback_query(F.data == "add_channel", AddChannel.channels)
async def ask_channel_id(call:CallbackQuery, state:FSMContext):
    await call.message.delete()
    await call.message.answer("<b>➕ Kanal ulash</b>\n\nKanaldan biror xabarni forward qiling yokida quyidagi tugma orqali kanalni menga ulashing.", reply_markup=get_channel)
    await state.set_state(AddChannel.channel_id)


@rt.message(F.text == "↩️ Orqaga", AddChannel.channel_id)
async def back_add_channel__(message:Message, state:FSMContext):
    data = await state.get_data()
    channels = data.get("channels", [])

    matn = make_channels_list(channels)
    
    user_id = message.from_user.id
    await message.delete()
    await message.answer("Kanal qo'shish bekor qilindi", reply_markup=ownerMenu(user_id))
    await message.answer(matn, reply_markup=channelsMenu(len(channels)), link_preview_options=LinkPreviewOptions(is_disabled=True))
    await state.set_state(AddChannel.channels)


@rt.message(AddChannel.channel_id, F.forward_from_chat | F.chat_shared)
async def get_channel_id(message:Message, state:FSMContext, bot:Bot):
    if message.forward_from_chat:
        new_channel = message.forward_from_chat.id
    else:
        new_channel = message.chat_shared.chat_id

    user_id = message.from_user.id
    data = await state.get_data()
    channels = data.get("channels", [])

    # Kanal bazada bor yo'qligini tekshirish
    channel = await db.get_channel(new_channel)
    if not channel:
        chat = await bot.get_chat(chat_id=new_channel)
        username = chat.username

        if username:
            c_link = f"https://t.me/{username}"
        else:
            try:
                invite_link_obj = await bot.create_chat_invite_link(chat_id=new_channel)
                c_link = invite_link_obj.invite_link
                await db.update_channel_link(new_channel, c_link)
                await update_channels_cache()
            except Exception as e:
                c_link = None
        await db.add_channel(None, new_channel, c_link)
        channels.append((None, None, new_channel, None))
        await state.update_data(channels=channels)
        await update_channels_cache()
        await message.answer(
            "<b>Kanal muvaffaqiyatli qo'shildi ✅</b>\n\n"
            "Majburiy obuna to'g'ri ishlashi uchun bot kanalga admin qilishni unutmang ❗️",
            reply_markup=ownerMenu(user_id)
        )
    else:
        await message.answer("<b>Bu kanal avvalroq qo'shilgan ⚠️</b>", reply_markup=ownerMenu(user_id))

    matn = make_channels_list(channels)
    await message.answer(matn, reply_markup=channelsMenu(len(channels)), link_preview_options=LinkPreviewOptions(is_disabled=True))
    await state.set_state(AddChannel.channels)


@rt.message(AddChannel.channel_id)
async def send_error_channel_id(message:Message, state:FSMContext):
    await message.answer("Iltimos xabarni forward qilib yuboring !", reply_markup=back_btn)


@rt.callback_query(F.data == "back_", AddChannel.channel_id)
async def back_add_channel_(call:CallbackQuery, state:FSMContext):
    data = await state.get_data()
    channels = data.get("channels", [])

    matn = make_channels_list(channels)
    
    await call.message.delete()
    await call.message.answer("Yangi kanal qo'shilmadi.")
    await call.message.answer(matn, reply_markup=channelsMenu(len(channels)), link_preview_options=LinkPreviewOptions(is_disabled=True))
    await state.set_state(AddChannel.channels)


# Kanal uzish
@rt.callback_query(F.data == "del_channel", AddChannel.channels)
async def ask_channel_id_for_del_channel(call:CallbackQuery, state:FSMContext):
    data = await state.get_data()
    channels = data.get("channels", [])

    await call.message.delete()
    await call.message.answer("<b>➖ Kanal uzish</b>\n\nUzmoqchi bo'lgan kanalni tanlang.", reply_markup=channelsListBtn(channels))
    await state.set_state(DelChannel.channel_id)


@rt.callback_query(F.data.startswith("del_channel_"), DelChannel.channel_id)
async def get_channel_id_for_del_channel(call:CallbackQuery, state:FSMContext):
    channel_id = call.data.split('_')[2]
    id_link = f"https://t.me/c/{str(channel_id).replace('-100', '')}/1"
    
    await call.message.delete()
    await call.message.answer(f"<a href='{id_link}'>Kanalni</a> ni o'chirishni tasdiqlang.", reply_markup=checkerDelBtn(channel_id))
    await state.set_state(DelChannel.is_checked)


@rt.callback_query(F.data.startswith("yes_"), DelChannel.is_checked)
async def del_channel_yes(call:CallbackQuery, state:FSMContext):
    channel_id = call.data.split('_')[1]
    await db.delete_channel(int(channel_id))

    await update_channels_cache()

    channels = await db.get_channels()
    await state.update_data(channels=channels)

    matn = make_channels_list(channels)
    
    await call.message.delete()
    await call.message.answer("Kanal muvaffaqiyatli uzildi ✅")
    await call.message.answer(matn, reply_markup=channelsMenu(len(channels)), link_preview_options=LinkPreviewOptions(is_disabled=True))
    await state.set_state(AddChannel.channels)


@rt.callback_query(F.data == "no", DelChannel.is_checked)
async def del_channel_no(call:CallbackQuery, state:FSMContext):
    data = await state.get_data()
    channels = data.get("channels", [])

    matn = make_channels_list(channels)
    
    await call.message.delete()
    await call.message.answer("Kanal uzish bekor qilindi ❌")
    await call.message.answer(matn, reply_markup=channelsMenu(len(channels)), link_preview_options=LinkPreviewOptions(is_disabled=True))
    await state.set_state(AddChannel.channels)


@rt.callback_query(F.data == "back_del_channel", DelChannel.channel_id)
async def back_del_channel_(call:CallbackQuery, state:FSMContext):
    data = await state.get_data()
    channels = data.get("channels", [])

    matn = make_channels_list(channels)
    
    await call.message.delete()
    await call.message.answer(matn, reply_markup=channelsMenu(len(channels)), link_preview_options=LinkPreviewOptions(is_disabled=True))
    await state.set_state(AddChannel.channels)