from aiogram import types
from src.models.models import rooms

def get_verse_keyboard():
    inline_keyboard = [
        [
            types.InlineKeyboardButton(text="1", callback_data='verse_1'),
            types.InlineKeyboardButton(text="2", callback_data='verse_2'),
            types.InlineKeyboardButton(text="3", callback_data='verse_3')
        ],
        [
            types.InlineKeyboardButton(text="4", callback_data='verse_4'),
            types.InlineKeyboardButton(text="5", callback_data='verse_5'),
            types.InlineKeyboardButton(text="6", callback_data='verse_6')
        ]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

def get_confirm_keyboard():
    inline_keyboard = [
        [
            types.InlineKeyboardButton(text="✅ Підтвердити", callback_data='confirm_room'),
            types.InlineKeyboardButton(text="❌ Скасувати", callback_data='cancel_room')
        ]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

def get_room_management_keyboard(room_number):
    is_closed = rooms[room_number]['closed']
    
    inline_keyboard = [
        [
            types.InlineKeyboardButton(
                text="🔓 Відкрити кімнату" if is_closed else "🚪 Закрити кімнату",
                callback_data='toggle_room'
            )
        ],
        [
            types.InlineKeyboardButton(text="⏹ Завершити диктант", callback_data='finish_dictation')
        ]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
