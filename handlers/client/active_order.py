from contextlib import suppress

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageNotModified, BotBlocked
from config import bot

from keyboards.inline.client.inline_client import InlineClient
from keyboards.reply.reply_kb import Reply
from pgsql import pg

from text.client.form_active_order import FormActiveOrderClient
from text.language.main import Text_main
from text.text_func import TextFunc

reply = Reply()
inline = InlineClient()

Txt = Text_main()
func = TextFunc()

form_active = FormActiveOrderClient()


class Delete:
    def __init__(self, proxy: dict):
        self._proxy = proxy

    async def start(self):
        await self._unpack_order()
        await self._update_cancel()
        await self._mailing()

    async def _unpack_order(self):
        order = await pg.orderid_to_order_accepted_client(order_accept_id=self._proxy.get('order_accept_id'))
        self._proxy['order_driver_id'] = order[0]
        self._proxy['driver_id'] = order[1]
        self._proxy['type'] = order[3]
        self._proxy['places'] = order[10]
        tax = await func.percent_price(price=order[15])
        n = self._proxy.get('places') if self._proxy.get('places') != 0 else 1
        self._proxy['wallet_return'] = n * tax

    async def _update_cancel(self):
        await pg.update_driver_wallet_payment(driver_id=self._proxy.get('driver_id'),
                                              cash=self._proxy.get('wallet_return'))
        await pg.cancel_active_order(order_accept_id=self._proxy.get('order_accept_id'), client=True)
        await pg.update_order_driver_remove_places(order_driver_id=self._proxy.get('order_driver_id'),
                                                   places=self._proxy.get('places'))

    async def _mailing(self):
        await self._mailing_client()
        try:
            await self._mailing_driver()
        except BotBlocked:
            await pg.block_status(user_id=self._proxy.get('driver_id'), status=False)

    async def _mailing_client(self):
        Text_lang = Txt.language[self._proxy.get('lang')]
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=self._proxy.get('client_id'), message_id=self._proxy.get('message_id'),
                                        text=Text_lang.cancel.client.cancel_order)

    async def _mailing_driver(self):
        language = await pg.select_language(user_id=self._proxy.get('driver_id'))
        text = await form_active.order_cancel(order_accept_id=self._proxy.get('order_accept_id'), language=language)
        await bot.send_message(chat_id=self._proxy.get('driver_id'), text=text,
                               reply_markup=await reply.main_menu(language=language))


class ActiveOrderClient(StatesGroup):
    active_order_client = State()

    async def menu_order_cancel(self, call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            data['order_accept_id'] = int(call.data.split("_")[1])
            Text_lang = Txt.language[data.get('lang')]
        with suppress(MessageNotModified):
            markup = await inline.menu_delete(language=data.get('lang'), order_accept_id=data.get('order_accept_id'))
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=Text_lang.cancel.client.cancel_question_order, reply_markup=markup)

    async def menu_active_order(self, call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            with suppress(MessageNotModified):
                data['order_accept_id'] = int(call.data.split("_")[1])
                text = await form_active.order_view(order_accept_id=data.get('order_accept_id'), language=data.get('lang'))
                markup = await inline.menu_cancel(order_accept_id=data.get('order_accept_id'), language=data.get('lang'))
                await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                            text=text, reply_markup=markup)
        await call.answer()

    async def menu_order_delete(self, call: types.CallbackQuery, state: FSMContext):
        print(call)
        async with state.proxy() as data:
            data['message_id'] = call.message.message_id
        delete = Delete(proxy=await state.get_data())
        await delete.start()

    async def active_order_check(self, data: dict):
        exist = await pg.check_active_order_client(client_id=data.get('client_id'))
        if exist is True:
            await self._exist(data=data)
        else:
            await self._not_exist(data=data)

    async def _exist(self, data: dict):
        for order_accept_id in await pg.select_order_accepted_to_client(client_id=data.get('client_id')):
            text = await form_active.order_view(order_accept_id=order_accept_id[0], language=data.get('lang'))
            await bot.send_message(chat_id=data.get('client_id'), text=text,
                                   reply_markup=await inline.menu_cancel(order_accept_id=order_accept_id[0],
                                                                         language=data.get('lang')))
    async def _not_exist(self, data: dict):
        Text_lang = Txt.language[data.get('lang')]
        await bot.send_message(chat_id=data.get('client_id'), text=Text_lang.active_order.no_active_order,
                               reply_markup=await reply.main_menu(language=data.get('lang')))

    def register_handlers_active_order_client(self, dp: Dispatcher):
        dp.register_callback_query_handler(self.menu_order_cancel, lambda x: x.data and x.data.startswith("cancel"),    state=self.active_order_client)
        dp.register_callback_query_handler(self.menu_order_delete, lambda x: x.data and x.data.startswith("yes"),       state=self.active_order_client)
        dp.register_callback_query_handler(self.menu_active_order, lambda x: x.data and x.data.startswith("no"),        state=self.active_order_client)

