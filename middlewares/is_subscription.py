import logging
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Callable, Awaitable, Dict, Any, Union
from data.loader import db, update_channels_cache
import data.loader as loader

class SubscriptionMiddleware(BaseMiddleware):      
    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:
        if not event.from_user:
            return await handler(event, data)
        
        if event.from_user.id in loader.ADMINS:
            return await handler(event, data)

        should_check = False

        old_command = 'start'
        
        if isinstance(event, Message) and event.text:
            if event.text.strip() == "/start":
                should_check = True
            elif event.text == "✅ Javobni tekshirish":
                old_command = 'tekshir'
                should_check = True
        
        elif isinstance(event, CallbackQuery):
            if event.data.startswith("check_subs:"):
                old_command = event.data.split(':')[1]
                should_check = True

        if not should_check:
            return await handler(event, data)

        channels = loader.CHANNELS 
        
        if not channels:
            return await handler(event, data)

        bot = data["bot"]
        user_id = event.from_user.id
        builder = InlineKeyboardBuilder()
        unsubscribed = []

        for ch in channels:
            c_title = ch[1] if ch[1] else "Kanal"
            c_id = ch[2]
            c_link = ch[3]

            try:
                member = await bot.get_chat_member(chat_id=c_id, user_id=user_id)
                if member.status in ("left", "kicked"):
                    if not c_link:
                        chat = await bot.get_chat(chat_id=c_id)
                        username = chat.username

                        if username:
                            c_link = f"https://t.me/{username}"
                        else:
                            try:
                                invite_link_obj = await bot.create_chat_invite_link(chat_id=c_id)
                                c_link = invite_link_obj.invite_link
                                await db.update_channel_link(c_id, c_link)
                                await update_channels_cache()
                            except Exception as e:
                                logging.error(f"Link yaratishda xato ({c_id}): {e}")
                                c_link = f"https://t.me/c/{str(c_id).replace('-100', '')}/1"

                    unsubscribed.append({"title": c_title, "link": c_link})

            except Exception as e:
                logging.error(f"Kanalni tekshirishda xato ({c_id}): {e}")
                continue
        
        if unsubscribed:
            for i, item in enumerate(unsubscribed, 1):
                builder.row(InlineKeyboardButton(text=f"kanal {i}", url=item['link']))
            
            builder.row(InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data=f"check_subs:{old_command}"))
            
            text = "<b>⚠️ Botdan foydalanish uchun quyidagi kanallarga obuna bo'lishingiz shart:</b>"
            
            if isinstance(event, Message):
                await event.answer(text, reply_markup=builder.as_markup())
            else:
                await event.answer("Siz hali hamma kanallarga a'zo emassiz!", show_alert=True)
                try:
                    await event.message.edit_text(text, reply_markup=builder.as_markup())
                except:
                    pass
            return 

        return await handler(event, data)