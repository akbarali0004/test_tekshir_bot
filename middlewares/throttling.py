from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest
from typing import Dict
import asyncio
import time

class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, limit: float = 1.0):
        """
        Xabarlarni cheklash middleware.
        :param limit: Har bir foydalanuvchi uchun minimal vaqt oralig‘i (soniyalarda).
        """
        super().__init__()
        self.rate_limit = limit
        self.users_last_request: Dict[int, float] = {}

    async def __call__(self, handler, event: Message, data: Dict):
        user_id = event.from_user.id
        current_time = time.time()

        # Foydalanuvchining oxirgi so'rov vaqtini olish
        last_request_time = self.users_last_request.get(user_id, 0)

        if current_time - last_request_time < self.rate_limit:
            try:
                # Juda ko'p so'rovlar bo'lganda javob
                await event.answer("Too many requests. Please wait a moment.")
            except TelegramBadRequest:
                pass  # Agar xabar yuborishda xato bo‘lsa, e'tiborsiz qoldiramiz
            return  # Xabarni ishlov berishni to'xtatish

        # Foydalanuvchi vaqtini yangilash
        self.users_last_request[user_id] = current_time

        # Keyingi handlerni chaqirish
        return await handler(event, data)
