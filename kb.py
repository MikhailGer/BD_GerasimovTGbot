from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove, )
from aiogram.utils.keyboard import ReplyKeyboardBuilder

admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/select_all", callback_data="/select_all"),
         KeyboardButton(text="/insert", callback_data="/insert")],
        [KeyboardButton(text="/get_object_by_id", callback_data="/get_object_by_id"),
         KeyboardButton(text="/get_object_by_age", callback_data="/get_object_by_age")],
        [KeyboardButton(text="/get_object_by_username", callback_data="/get_object_by_username"),
         KeyboardButton(text="/delete_object_by_id", callback_data="/delete_object_by_id")],
        [KeyboardButton(text="/change_object_by_id", callback_data="/change_username_by_id"),
         KeyboardButton(text="/backup", callback_data="/backup")],
        [KeyboardButton(text="/change_DB", callback_data="/change_DB"),
         KeyboardButton(text="/deselect_DB", callback_data="/deselect_DB")
         ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)
user_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/register", callback_data="/insert"),
         ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

back_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/back", callback_data="/back"),
         ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/start", callback_data="/start"),
         ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


def create_keyboard(buttons_data):
    builder = ReplyKeyboardBuilder()
    for button_text in buttons_data:
        [builder.button(text=button_text)]

    return builder.as_markup(resize_keyboard=True)
