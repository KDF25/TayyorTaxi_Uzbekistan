

from contextlib import suppress

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageNotModified, MessageToDeleteNotFound, BotBlocked

from config import bot
from keyboards.inline.driver.inline_driver import InlineDriver
from keyboards.reply.reply_kb import Reply
from pgsql import pg

from text.driver.form_driver import FormDriver
from text.driver.form_active_order import FormActiveOrderDriver
from text.language.main import Text_main
from text.text_func import TextFunc

Txt = Text_main()
func = TextFunc()
form = FormDriver()
form_active = FormActiveOrderDriver()
reply = Reply()
inline = InlineDriver()


class Driver(StatesGroup):
    driver_level1 = State()
    driver_level2 = State()

    route_cancel = State()
    update_price = State()

    region_level1 = State()
    town_level1 = State()


    def __init__(self):
        self.__call = None
        self.__state = None
        self.__data = None

    async def menu_cancel_start(self, call: types.CallbackQuery, state: FSMContext):
        await self.route_cancel.set()
        dta = call.data.split('_')
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
            # await pg.update_cancel_driver(id=data['analise_id'])
            markup = await inline.menu_route_choose(language=data.get('lang'), route_id=int(dta[1]))
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=Text_lang.questions.driver.sure, reply_markup=markup)
            await call.answer()

    async def menu_cancel_finish(self, call: types.CallbackQuery, state: FSMContext):
        await state.set_state("MenuDriver:menu_driver_level1")
        async with state.proxy() as data:
            dta = call.data.split('_')
            Text_lang = Txt.language[data.get('lang')]
            if dta[0] == 'yes':
                text = Text_lang.order.driver.route_cancel
                await pg.route_cancel(driver_id=call.from_user.id, route_id=int(dta[1]))
                await pg.orders_driver_cancel(route_id=data.get('route_id'))
                await pg.update_delete_driver(id=data['analise_id'])
            elif dta[0] == 'no':
                text = Text_lang.menu.main_menu
        with suppress(MessageToDeleteNotFound):
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await bot.send_message(chat_id=call.from_user.id, text=text,
                                   reply_markup=await reply.online(language=data.get('lang')))

    async def menu_all_route(self, call: types.CallbackQuery, state: FSMContext):
        await self.driver_level2.set()
        async with state.proxy() as data:
            dta = call.data.split('_')
            print("fff", dta)
            if dta[0] == 'route':
                data['route_id'] = int(dta[1])
        text = await form.route_cancel(language=data.get('lang'), route_id=data.get('route_id'))
        markup = await inline.menu_route_cancel(language=data.get('lang'), route_id=data.get('route_id'))
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text,
                                        reply_markup=markup)
            await call.answer()
            print(data)

    async def menu_new_route(self, call: types.CallbackQuery, state: FSMContext):
        await self.driver_level2.set()
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
            text = Text_lang.questions.driver.route
            markup = await inline.menu_route(language=data.get('lang'))
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=text, reply_markup=markup)
            await call.answer()

    async def menu_price_start(self, call: types.CallbackQuery, state: FSMContext):
        await self.update_price.set()
        async with state.proxy() as data:
            dta = call.data.split('_')
            Text_lang = Txt.language[data.get('lang')]
            # await pg.update_cancel_driver(id=data['analise_id'])
            markup = await inline.menu_price_update(language=data.get('lang'), route_id=int(dta[1]))
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=Text_lang.questions.driver.price, reply_markup=markup)
            await call.answer()

    async def menu_price_finish(self, call: types.CallbackQuery, state: FSMContext):
        await self.driver_level2.set()
        async with state.proxy() as data:
            dta = call.data.split('_')
            await pg.price_update(driver_id=call.from_user.id, route_id=int(dta[2]), price=int(dta[1]))
            text = await form.route_cancel(language=data.get('lang'), route_id=data.get('route_id'))
            markup = await inline.menu_route_cancel(language=data.get('lang'), route_id=data.get('route_id'))
            # markup = await inline.menu_route_choose(language=data.get('lang'), route_id=int(dta[1]))
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text,
                                        reply_markup=markup)
            await call.answer()

    def register_handlers_driver(self, dp: Dispatcher):
        dp.register_callback_query_handler(self.menu_cancel_start, lambda x: x.data.startswith("cancel"),               state=self.driver_level2)
        dp.register_callback_query_handler(self.menu_cancel_finish, lambda x: x.data.startswith("yes"),                 state=self.route_cancel)
        dp.register_callback_query_handler(self.menu_cancel_finish, text='no',                                          state=self.route_cancel)

        dp.register_callback_query_handler(self.menu_all_route, lambda x: x.data.startswith("route"),                   state=self.driver_level1)
        dp.register_callback_query_handler(self.menu_all_route, text='back', state=[self.route_cancel, self.update_price])

        dp.register_callback_query_handler(self.menu_price_start, lambda x: x.data.startswith("updatePrice"),           state=self.driver_level2)
        dp.register_callback_query_handler(self.menu_price_finish, lambda x: x.data.startswith("updatePrice"),          state=self.update_price)

        dp.register_callback_query_handler(self.menu_new_route, text='newRoute',                                        state=self.driver_level1)
        dp.register_callback_query_handler(self.menu_new_route, text='back',                                            state=["DriverBetweenTowns:town_level1",
                                                                                                                               "DriverBetweenRegions:region_level1"])
