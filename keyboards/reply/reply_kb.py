from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from text.language.ru import Text_ru
from text.language.main import Text_main


RU = Text_ru()
Txt =Text_main()

class Reply:
    async def start_keyb(self, language: str):
        Text_lang = Txt.language[language]
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        b1 = KeyboardButton(text=Text_lang.menu.passenger)
        b2 = KeyboardButton(text=Text_lang.menu.delivery)
        b3 = KeyboardButton(text=Text_lang.menu.information)
        b4 = KeyboardButton(text=Text_lang.menu.order)
        b5 = KeyboardButton(text=Text_lang.menu.driver)
        b6 = KeyboardButton(text=Text_lang.menu.settings)
        markup.add(b1, b2, b3, b4, b5, b6)
        return markup

    async def main_menu(self, language: str):
        Text_lang = Txt.language[language]
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        b1 = KeyboardButton(text=Text_lang.menu.main_menu)
        markup.add(b1)
        return markup

    async def online(self, language: str):
        Text_lang = Txt.language[language]
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        b1 = KeyboardButton(text=Text_lang.menu.online)
        b2 = KeyboardButton(text=Text_lang.menu.order)
        b3 = KeyboardButton(text=Text_lang.menu.personal_cabinet)
        b4 = KeyboardButton(text=Text_lang.menu.information)
        b5 = KeyboardButton(text=Text_lang.menu.settings)
        b6 = KeyboardButton(text=Text_lang.menu.change)
        markup.add(b1).add(b2, b3, b4, b5).add(b6)
        return markup


    async def setting(self, language: str):
        Text_lang = Txt.language[language]
        b1 = KeyboardButton(text=Txt.settings.ozb)
        b2 = KeyboardButton(text=Txt.settings.rus)
        b3 = KeyboardButton(text=Txt.settings.uzb)
        b4 = KeyboardButton(text=Text_lang.menu.main_menu)
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(b1, b2, b3).add(b4)
        return markup

    async def information(self, language: str):
        Text_lang = Txt.language[language]
        b1 = KeyboardButton(text=Text_lang.information.about_us)
        b2 = KeyboardButton(text=Text_lang.information.how_to_use2)
        b3 = KeyboardButton(text=Text_lang.information.feedback)
        b4 = KeyboardButton(text=Text_lang.menu.main_menu)
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(b1, b2).add(b3).add(b4)
        return markup

    async def share_phone(self, language: str):
        Text_lang = Txt.language[language]
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        b1 = KeyboardButton(text=Text_lang.buttons.common.phone, request_contact=True)
        b2 = KeyboardButton(text=Text_lang.menu.main_menu)
        markup.add(b1,b2)
        return markup

    async def change(self, language: str):
        Text_lang = Txt.language[language]
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        b1 = KeyboardButton(text=Text_lang.buttons.common.da)
        b2 = KeyboardButton(text=Text_lang.buttons.common.no)
        b3 = KeyboardButton(text=Text_lang.menu.main_menu)
        markup.add(b2, b1).add(b3)
        return markup

    async def personal_cabinet(self, language: str):
        Text_lang = Txt.language[language]
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        b1 = KeyboardButton(text=Text_lang.buttons.personal_cabinet.data.data)
        b2 = KeyboardButton(text=Text_lang.buttons.personal_cabinet.wallet.wallet)
        b3 = KeyboardButton(text=Text_lang.menu.main_menu)
        markup.add(b1, b2, b3)
        return markup