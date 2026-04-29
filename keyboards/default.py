from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonRequestChat, KeyboardButtonRequestUser
from data.config import ADMIN


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
def ownerMenu(user_id:int):
    btn = [
        [
            KeyboardButton(text="➕ Test yaratish"),
            KeyboardButton(text="📋 Testlarim")
        ]
    ]

    if user_id == ADMIN:
        btn.append(
            [
                KeyboardButton(text="📢 Majburiy obuna"),
                KeyboardButton(text="👨‍💻 Adminlar")
            ])
        
    btn.append(
        [
            KeyboardButton(text="✉️ Xabar yuborish")
        ])
    btn.append(
        [
            KeyboardButton(text="📈 Statistika"),
            KeyboardButton(text="👤 Profile")
        ])
    
    return ReplyKeyboardMarkup(
        keyboard=btn,
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


create_test_back = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="↩️ Orqaga"),
            
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