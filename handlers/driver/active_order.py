import datetime
from contextlib import suppress

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageNotModified, BotBlocked

from config import bot
from handlers.driver.driver import Driver
from keyboards.inline.driver.inline_driver import InlineDriver
from keyboards.reply.reply_kb import Reply
from pgsql import pg

from text.driver.form_active_order import FormActiveOrderDriver
from text.client.form_new_order import FormNewOrderClient
from text.text_func import TextFunc
from text.language.main import Text_main

Txt = Text_main()
func = TextFunc()

form = FormActiveOrderDriver()
form_new = FormNewOrderClient()
reply = Reply()
inline = InlineDriver()
driver = Driver()


class Delete:
    def __init__(self, proxy: dict):
        self._proxy = proxy

    async def start(self):
        await self._unpack()
        await self._update()
        await self._mailing()

    async def _unpack(self):
        await self._unpack_order()
        await self._unpack_driver()

    async def _unpack_order(self):
        order = await pg.orderid_to_order_accepted_driver(order_accept_id=self._proxy.get('order_accept_id'))
        self._proxy['places'], self._proxy['client_id'], self._proxy['type'], self._proxy['order_client_id'], \
        self._proxy['driver_id'] = order[11], order[1], order[4], order[0], order[2]
        self._proxy['lang_client'] = await pg.select_language(user_id=self._proxy.get('client_id'))

    async def _unpack_driver(self):
        self._proxy['name'], phone, car = await pg.select_parametrs_driver(driver_id=self._proxy.get('driver_id'))
        self._proxy['car'] = await pg.id_to_car(car_id=car)

    async def _update(self):
        await pg.update_order_driver_remove_places(order_driver_id=self._proxy.get('order_driver_id'),
                                                   places=self._proxy.get('places'))
        await pg.cancel_active_order(order_accept_id=self._proxy.get('order_accept_id'), driver=True)

    async def _mailing(self):
        await self._mailing_driver()
        try:
            await self._mailing_client()
        except BotBlocked:
            print('cancel')
            await pg.block_status(user_id=self._proxy.get('client_id'), status=False)

    async def _mailing_driver(self):
        Text_lang = Txt.language[self._proxy.get("lang")]
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=self._proxy.get('driver_id'), message_id=self._proxy.get('message_id'),
                                        text=Text_lang.active_order.driver.cancel_order)

    async def _mailing_client(self):
        if self._proxy.get('type') == "passenger":
            await self._mailing_passenger()
        elif self._proxy.get('type') == "delivery":
            await self._mailing_delivery()

    async def _mailing_passenger(self):
        Text_lang = Txt.language[self._proxy.get("lang_client")]
        await bot.send_message(chat_id=self._proxy.get('client_id'), text=Text_lang.menu.passenger,
                               reply_markup=await reply.main_menu(language=self._proxy.get('lang_client')))
        await bot.send_message(chat_id=self._proxy.get('client_id'),
                               text=await form_new.order_delete(name=self._proxy.get('name'),
                                                                car=self._proxy.get('car'),
                                                                language=self._proxy.get("lang_client")),
                               reply_markup=await inline.menu_choose_more(
                                   order_client_id=self._proxy.get('order_client_id'),
                                   language=self._proxy.get("lang_client")))

    async def _mailing_delivery(self):
        Text_lang = Txt.language[self._proxy.get("lang_client")]
        await bot.send_message(chat_id=self._proxy.get('client_id'), text=Text_lang.menu.delivery,
                               reply_markup=await reply.main_menu(language=self._proxy.get("lang_client")))
        await bot.send_message(chat_id=self._proxy.get('client_id'),
                               text=await form_new.order_delete(name=self._proxy.get('name'),
                                                                car=self._proxy.get('car'),
                                                                language=self._proxy.get("lang_client")),
                               reply_markup=await inline.menu_find_more(
                                   order_client_id=self._proxy.get('order_client_id'),
                                   language=self._proxy.get("lang_client")))


class ActiveOrderDriver(StatesGroup):
    active_order_driver = State()

    async def active_order_check(self, data: dict):
        exist = await pg.check_active_order_driver(driver_id=data.get('driver_id'))
        if exist is True:
            await self._exist(data=data)
        else:
            await self._not_exist(data=data)

    async def _exist(self, data: dict):
        self.__date = None
        for order_accept_id, date_trip in await pg.select_order_accepted_to_driver(driver_id=data.get('driver_id')):
            if date_trip != self.__date:
                date = datetime.date.strftime(date_trip, "%d.%m.%y")
                date = f"👇🗓🗓🗓<b>{date}</b>🗓🗓🗓👇"
                await bot.send_message(chat_id=data.get('driver_id'), text=date)
            self.__date = date_trip
            text = await form.active_order_driver(order_accept_id=order_accept_id, language=data.get('lang'))
            markup = await inline.menu_active_order_view(order_accept_id=order_accept_id, language=data.get('lang'))
            await bot.send_message(chat_id=data.get('driver_id'),  text=text, reply_markup=markup)

    async def _not_exist(self, data: dict):
        Text_lang = Txt.language[data.get('lang')]
        await bot.send_message(chat_id=data.get('driver_id'), text=Text_lang.active_order.no_active_order,
                               reply_markup=await reply.main_menu(language=data.get('lang')))

    async def menu_active_order(self, call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            data['order_accept_id'] = int(call.data.split("_")[1])
            with suppress(MessageNotModified):
                text = await form.active_order_driver(order_accept_id=data.get('order_accept_id'), language=data.get('lang'))
                markup = await inline.menu_active_order_view(order_accept_id=data.get('order_accept_id'),
                                                             language=data.get('lang'))
                await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                            text=text, reply_markup=markup)
        await call.answer()

    async def menu_order_cancel(self, call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            data['order_accept_id'] = int(call.data.split("_")[1])
            Text_lang = Txt.language[data.get('lang')]
        with suppress(MessageNotModified):
            markup = await inline.menu_active_order_cancel(language=data.get('lang'),
                                                           order_accept_id=data.get('order_accept_id'))
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=Text_lang.cancel.driver.driver, reply_markup=markup)
        await call.answer()

    async def menu_order_delete(self, call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            data['message_id'] = call.message.message_id
        delete = Delete(proxy=await state.get_data())
        await delete.start()

    def register_handlers_active_order_driver(self, dp: Dispatcher):
        dp.register_callback_query_handler(self.menu_active_order, lambda x: x.data and x.data.startswith("back"), state=self.active_order_driver)
        dp.register_callback_query_handler(self.menu_order_cancel, lambda x: x.data and x.data.startswith("cancel"),   state=self.active_order_driver)
        dp.register_callback_query_handler(self.menu_order_delete, lambda x: x.data and x.data.startswith("delete"),   state=self.active_order_driver)
