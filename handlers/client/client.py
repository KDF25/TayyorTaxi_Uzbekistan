import asyncio
import datetime

from contextlib import suppress
from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageNotModified, MessageToDeleteNotFound, BotBlocked
from natsort import natsorted
from pympler.asizeof import asizeof

from config import bot
from keyboards.inline.client.inline_client import InlineClient
from keyboards.inline.driver.inline_driver import InlineDriver
from keyboards.reply.reply_kb import Reply
from pgsql import pg
from text.client.form_client import FormClient
from text.client.form_new_order import FormNewOrderClient
from text.language.main import Text_main
from text.text_func import TextFunc

Txt = Text_main()
func = TextFunc()

reply = Reply()
inline = InlineClient()
inline_driver = InlineDriver()
form = FormClient()
form_new = FormNewOrderClient()


class Client(StatesGroup):
    client_level1 = State()
    client_level2 = State()
    client_level3 = State()
    client_level4 = State()
    client_level5 = State()
    client_level6 = State()
    client_level7 = State()
    client_level8 = State()
    client_level9 = State()
    client_level10 = State()
    client_level11 = State()
    client_level12 = State()

    region_level1 = State()
    town_level1 = State()

    async def menu_new_order(self, call: types.CallbackQuery, state: FSMContext):
        await self.client_level1.set()
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
            text = Text_lang.questions.driver.route
            markup = await inline.menu_route(language=data.get('lang'))
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=text, reply_markup=markup)
            await call.answer()

    def register_handlers_client(self, dp: Dispatcher):
        dp.register_callback_query_handler(self.menu_new_order, text='newRoute', state=self.client_level1)
        dp.register_callback_query_handler(self.menu_new_order, text='back', state=[self.town_level1, self.region_level1])


