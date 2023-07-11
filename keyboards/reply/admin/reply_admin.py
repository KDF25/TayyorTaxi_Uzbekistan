from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from text.language.main import Text_main

Txt =Text_main()

class ReplyAdmin:
    async def start_keyb(self):
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        b1 = KeyboardButton(text=Txt.Admin.mailing)
        markup.add(b1)
        return markup

    async def main_menu(self):
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        b1 = KeyboardButton(text=Txt.Admin.menu)
        markup.add(b1)
        return markup