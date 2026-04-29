from aiogram.filters import BaseFilter
from aiogram.types import Message

from data.config import ADMIN
from data import loader


class IsDigitMessage(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.text is not None and message.text.isdigit()
    

class IsOwner(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id == ADMIN
    

class IsAdmins(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in loader.ADMINS