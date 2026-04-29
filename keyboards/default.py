from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonRequestChat, KeyboardButtonRequestUser


# For Users
user_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="✅ Javobni tekshirish"),
            KeyboardButton(text="📊 Natijalarim")
        ],
        [
            KeyboardButton(text="ℹ️ Bot haqida"),
            KeyboardButton(text="👤 Profile")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


# For admins
owner_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="➕ Test yaratish"),
            KeyboardButton(text="📋 Testlarim")
        ],
        [
            KeyboardButton(text="📢 Majburiy obuna"),
            KeyboardButton(text="👨‍💻 Adminlar")
        ],
        [
            KeyboardButton(text="✉️ Xabar yuborish")
        ],
        [
            KeyboardButton(text="📈 Statistika"),
            KeyboardButton(text="👤 Profile")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="➕ Test yaratish"),
            KeyboardButton(text="📋 Testlarim")
        ],
        [
            KeyboardButton(text="✉️ Xabar yuborish")
        ],
        [
            KeyboardButton(text="📈 Statistika"),
            KeyboardButton(text="👤 Profile")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


test_duration_btn = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="3 soat"),
            KeyboardButton(text="5 soat"),
            KeyboardButton(text="10 soat")
        ],
        [
            KeyboardButton(text="1 kun"),
            KeyboardButton(text="3 kun"),
            KeyboardButton(text="1 hafta")
        ]
    ], resize_keyboard=True
)


get_channel = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="📢 Kanal tanlash", 
                request_chat=KeyboardButtonRequestChat(
                    request_id=1,
                    chat_is_channel=True,
                ))
        ],
        [
            KeyboardButton(text="↩️ Orqaga")
        ]
    ], resize_keyboard=True
)


get_admin_btn = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="👤 Foydalanuvchini tanlash", 
                request_user=KeyboardButtonRequestUser(
                    request_id=1,
                    user_is_bot=False,
                    max_quantity=1
                ))
        ],
        [
            KeyboardButton(text="↩️ Orqaga")
        ]
    ], resize_keyboard=True
)