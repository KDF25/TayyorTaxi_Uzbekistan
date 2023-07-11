from contextlib import suppress
from typing import Union

from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageNotModified

from config import bot, dp, chat_id_common as chat_id, chat_id_our
from handlers.admin.is_admin import IsAdmin, IsAdminOur
from handlers.admin.mailing import Mailing
from keyboards.inline.admin.inline_admin import InlineAdmin
from keyboards.reply.admin.reply_admin import ReplyAdmin
from text.admin.form_admin import FormAdmin
from text.language.main import Text_main

form = FormAdmin()
inline = InlineAdmin()
reply = ReplyAdmin()
Txt = Text_main()


class MenuAdmin(StatesGroup):
    menu_admin_level1 = State()

    analise_level1 = State()
    analise_level2 = State()
    analise_level3 = State()

    async def start_admin(self, message: types.Message, state: FSMContext):
        await bot.send_message(chat_id=message.from_user.id, text="Администраторская",
                               reply_markup=await reply.start_keyb())
        await self.menu_admin_level1.set()
        # print('str', await state.get_state())

    async def send_statistics(self, message: types.Message, state: FSMContext):
        await dp.bot.send_message(chat_id=chat_id, text=await form.statistics())

    async def send_stata_our(self, message: types.Message, state: FSMContext):
        await dp.bot.send_message(chat_id=message.from_user.id, text=await form.statistics())

    async def menu_mailing(self, message: types.Message, state: FSMContext):
        await bot.send_message(chat_id=message.from_user.id, text=Txt.Admin.mailing,
                               reply_markup=await reply.main_menu())
        await bot.send_message(chat_id=message.from_user.id, text="Кому хотели бы разослать?",
                               reply_markup=await inline.menu_mailing())
        await Mailing.mailing_level1.set()
        # print('1', await state.get_state())

    async def main_menu(self, message: types.Message, state: FSMContext):
        await bot.send_message(chat_id=message.from_user.id, text=Txt.Admin.menu,
                               reply_markup=await reply.start_keyb())
        await self.menu_admin_level1.set()
        # print('mm', await state.get_state())

    async def send_analise(self, message: Union[types.Message, types.CallbackQuery], state: FSMContext):
        await self.analise_level1.set()
        if isinstance(message, types.Message):
            await bot.send_message(chat_id=message.from_user.id, text="Что будем анализировать?",
                                   reply_markup=await inline.menu_analise())
        elif isinstance(message, types.CallbackQuery):
            await bot.edit_message_text(chat_id=message.from_user.id, text="Что будем анализировать?",
                                        message_id=message.message.message_id,
                                        reply_markup=await inline.menu_analise())
            await message.answer()

    async def send_analise_type(self, call: types.CallbackQuery, state: FSMContext):
        await self.analise_level2.set()
        async with state.proxy() as data:
            data['type'] = call.data.split('_')[1]
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, text="За какое время?",
                                        message_id=call.message.message_id,
                                        reply_markup=await inline.menu_analise_timeframe())
            await call.answer()

    async def send_analise_timeframe(self, call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            data['timeframe'] = call.data.split('_')[1]
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, text=await form.analise(data=data),
                                        message_id=call.message.message_id)
            await call.answer()

    @staticmethod
    async def default_function(message: types.Message, state: FSMContext):
        print(message)
        print(await state.get_state())

    def register_handlers_menu_admin(self, dp: Dispatcher):
        dp.register_message_handler(self.start_admin, IsAdmin(), commands="admin", state='*')
        dp.register_message_handler(self.send_statistics, IsAdmin(), commands="statistics", state='*')
        dp.register_message_handler(self.send_stata_our, IsAdminOur(), commands="stata_our", state='*')

        dp.register_message_handler(self.send_analise, IsAdminOur(), commands="analise", state='*')
        dp.register_callback_query_handler(self.send_analise, IsAdminOur(), text='back', state=self.analise_level2)

        dp.register_callback_query_handler(self.send_analise_type, IsAdminOur(), lambda x: x.data.startswith("analise"),
                                           state=self.analise_level1)
        dp.register_callback_query_handler(self.send_analise_timeframe, IsAdminOur(),
                                           lambda x: x.data.startswith("day"), state=self.analise_level2)

        dp.register_message_handler(self.main_menu, IsAdmin(), text=Txt.Admin.menu, state=[*Mailing.states_names])
        dp.register_message_handler(self.menu_mailing, IsAdmin(), text=Txt.Admin.mailing,
                                    state=[None, self.menu_admin_level1])
        # dp.register_message_handler(self.default_function, IsAdmin(), content_types='any', state='*')
