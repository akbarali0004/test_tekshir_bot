from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def test_start_btn(test_code:int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🚀 Boshlash", callback_data=f"start_test_{test_code}")
            ]
        ]
    )

def test_refresh_start_btn(test_code:int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 Qayta Boshlash", callback_data=f"start_refresh_test_{test_code}")
            ]
        ]
    )

def currentResults(test_code):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Natijalar", callback_data=f"current_results_{test_code}"),
                InlineKeyboardButton(text="🏁 Yakunlash", callback_data=f"stop_test_{test_code}")
            ]
        ]
    )


def refresh_current_results(test_code:int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 Yangilash", callback_data=f"refresh_{test_code}")
            ],
            [
                InlineKeyboardButton(text="🏁 Yakunlash", callback_data=f"stop_test_{test_code}")
            ]
        ]
    )


def channelsMenu(length:int):
    btn = [[InlineKeyboardButton(text="➕ Kanal ulash", callback_data="add_channel")]]
    if length > 0:
        btn.append([InlineKeyboardButton(text="➖ Kanal uzish", callback_data="del_channel")])
    return InlineKeyboardMarkup(inline_keyboard=btn)


back_btn = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Bekor qilish", callback_data="back_")
        ]
    ]
)


def channelsListBtn(channels:list) -> InlineKeyboardButton:
    btn = []
    for i, channel in enumerate(channels, 1):
        btn.append([InlineKeyboardButton(text=f"{channel[1] or f'Kanal {i}'}", callback_data=f"del_channel_{channel[2]}")])

    btn.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_del_channel")])

    return InlineKeyboardMarkup(inline_keyboard=btn)


def checkerDelBtn(id:int) -> InlineKeyboardButton:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ha", callback_data=f"yes_{id}"),
                InlineKeyboardButton(text="❌ Yo'q", callback_data="no")
            ]
        ]
    )


""" Admin lar bo'limi uchun """
def adminsMenu(length:int):
    btn = [[InlineKeyboardButton(text="➕ Admin qo'shish", callback_data="add_admin")]]
    if length > 0:
        btn.append([InlineKeyboardButton(text="➖ Admin o'chirish", callback_data="del_admin")])
    return InlineKeyboardMarkup(inline_keyboard=btn)


def adminsListBtn(admins:list) -> InlineKeyboardButton:
    btn = []
    for i, admin in enumerate(admins, 1):
        btn.append([InlineKeyboardButton(text=f"{admin[1] or f'Admin {i}'}", callback_data=f"del_admin_{admin[2]}")])

    btn.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_del_admin")])

    return InlineKeyboardMarkup(inline_keyboard=btn)



def get_tests_pagination_btns(page: int, total_pages: int):
    builder = InlineKeyboardBuilder()
    
    # Oldingi sahifa tugmasi
    if page > 1:
        builder.add(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"mytests_{page-1}"))
    
    # Keyingi sahifa tugmasi
    if page < total_pages:
        builder.add(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"mytests_{page+1}"))
        
    return builder.as_markup()


update_name = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Ismni o'zgartirish", callback_data="rename_user")
        ]
    ]
)