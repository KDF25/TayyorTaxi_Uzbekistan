import datetime
from contextlib import suppress

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageToDeleteNotFound, MessageNotModified, BotBlocked

from config import bot
from keyboards.inline.driver.inline_driver import InlineDriver
from keyboards.reply.reply_kb import Reply
from pgsql import pg
from text.driver.form_active_order import FormActiveOrderDriver
from text.driver.form_driver import FormDriver
from text.client.form_new_order import FormNewOrderClient
from text.language.main import Text_main
from text.text_func import TextFunc

Txt = Text_main()
func = TextFunc()
form = FormDriver()
form_active = FormActiveOrderDriver()
form_new = FormNewOrderClient()
reply = Reply()
inline = InlineDriver()


class Accept:
    def __init__(self, call: types.CallbackQuery, proxy: dict):
        self.__time = None
        self.__client_id = None
        self._call = call
        self._proxy = proxy

    async def start(self):
        print('success')
        try:
            await self._update()
            await self._mailing()
            await self._booking()
            await self._check()
        except BotBlocked:
            print('alert block')
            await pg.block_status(user_id=self._proxy.get('client_id'), status=False)
            Text_lang = Txt.language[self._proxy.get('lang')]
            await pg.update_orders_client_rejected(order_client_id=self._proxy.get('order_client_id'))
            await self._call.answer(text=Text_lang.alert.driver.accept_order_late, show_alert=True)

    # booking
    async def _booking(self):
        await pg.order_accepted_rec(order_client_id=self._proxy.get('order_client_id'),
                                    order_driver_id=self._proxy.get('order_driver_id'),
                                    client_id=self._proxy.get('client_id'), driver_id=self._proxy.get('driver_id'),
                                    phone_client=self._proxy.get('phone_client'),
                                    phone_driver=self._proxy.get('phone_driver'),
                                    type_of_application=self._proxy.get('type'),
                                    from_region=self._proxy.get('from_region'), from_town=self._proxy.get('from_town'),
                                    to_region=self._proxy.get('to_region'), to_town=self._proxy.get('to_town'),
                                    date_trip=self._proxy.get('date'), time_trip=self._proxy.get('time'),
                                    places=self._proxy.get('num'), baggage=self._proxy.get('baggage'),
                                    trip=self._proxy.get('trip'), car=self._proxy.get('car'),
                                    conditioner=self._proxy.get('cond'), price=self._proxy.get('price'),
                                    cost=self._proxy.get('cost'))

    # update
    async def _update(self):
        await self._update_passenger()
        await self._update_order()
        await self._update_wallet()

    async def _update_passenger(self):
        if self._proxy.get('type') == 'passenger':
            await self._update_places()
            await self._update_time()

    async def _update_places(self):
        await pg.update_order_driver_add_places(order_driver_id=self._proxy.get('order_driver_id'),
                                                places=self._proxy.get('num'))

    async def _update_time(self):
        await pg.update_order_time(order_driver_id=self._proxy.get('order_driver_id'), time=self._proxy.get('time'))

    async def _update_order(self):
        self._proxy['date'] = datetime.datetime.strptime(self._proxy.get('date'), "%d.%m.%Y")
        await pg.update_orders_client_accepted(order_client_id=self._proxy.get('order_client_id'))
        await pg.update_orders_client_cancel(route_id=self._proxy.get('route_id'),
                                             client_id=self._proxy.get('client_id'),
                                             type_of_application=self._proxy.get('type'), trip=self._proxy.get('trip'),
                                             from_region=self._proxy.get('from_region'),
                                             from_town=self._proxy.get('from_town'),
                                             to_region=self._proxy.get('to_region'), to_town=self._proxy.get('to_town'),
                                             date_trip=self._proxy.get('date'), time_trip=self._proxy.get('time'))

    async def _update_wallet(self):
        await self._change_wallet()
        await pg.update_driver_wallet_accept(driver_id=self._proxy.get('driver_id'), wallet=self.__wallet)

    async def _change_wallet(self):
        self.__wallet = await pg.select_every_wallet(driver_id=self._proxy.get('driver_id'))
        self.__wallet = [i for i in self.__wallet]
        price = self._proxy.get('order_price')
        if self.__wallet[2] == self.__wallet[1] == 0:
            self.__wallet[0] -= price
        elif self.__wallet[2] >= 0:
            if self.__wallet[2] >= price:
                self.__wallet[2] -= price
            elif self.__wallet[2] < price:
                price -= self.__wallet[2]
                self.__wallet[2] = 0
                if self.__wallet[1] >= price:
                    self.__wallet[1] -= price
                elif self.__wallet[1] < price:
                    price -= self.__wallet[1]
                    self.__wallet[1] = 0
                    self.__wallet[0] -= price

    # mailing
    async def _mailing(self):
        await self._mailing_client()
        await self._mailing_driver()

    async def _mailing_client(self):
        text_client = await form.new_order_client(data=self._proxy)
        await bot.send_message(chat_id=self._proxy.get('client_id'), text=text_client,
                               reply_markup=await reply.main_menu(language=self._proxy.get('lang')))

    async def _mailing_driver(self):
        with suppress(MessageToDeleteNotFound):
            await bot.delete_message(chat_id=self._proxy.get('driver_id'), message_id=self._proxy.get('message_id'))
        await bot.send_message(chat_id=self._proxy.get('driver_id'), text=await form.new_order_driver(data=self._proxy))

    ############
    async def _check(self):
        await self._wallet_check()
        if self._proxy.get('type') == 'passenger':
            await self._full_car_check()

    async def _wallet_check(self):
        if await self._wallet() is False:
            await self._mailing_wallet()

    async def _wallet(self):
        wallet = await pg.select_all_wallet(driver_id=self._proxy.get('driver_id'))
        tax = Txt.money.wallet.tax
        return bool(wallet >= tax)

    async def _mailing_wallet(self):
        Text_lang = Txt.language[self._proxy.get('lang')]
        text_alert = Text_lang.alert.driver.insufficient_funds2
        await bot.send_message(chat_id=self._proxy.get('driver_id'), text=text_alert,
                               reply_markup=await reply.main_menu(language=self._proxy.get('lang')))

    async def _full_car_check(self):
        free_places = await pg.check_places_orders_driver(order_driver_id=self._proxy.get('order_driver_id'))
        if free_places == 0:
            await self._full_car()

    async def _full_car(self):
        orders = await pg.select_order_accept_driver(driver_id=self._proxy.get('driver_id'),
                                                     date=self._proxy.get('date'),
                                                     from_region=self._proxy.get('from_region'),
                                                     to_region=self._proxy.get('to_region'), type="passenger")
        for order_accept_id, self.__client_id, self.__time, type_app, baggage, cost, places, trip in orders:
            try:
                await self._mailing_full_car()
            except BotBlocked:
                await pg.block_status(user_id=self.__client_id, status=False)

    async def _mailing_full_car(self):
        language = await pg.select_language(user_id=self.__client_id)
        await bot.send_message(chat_id=self.__client_id, reply_markup=await reply.main_menu(language=language),
                               text=await form_active.car_full(date=self._proxy.get('date'), time=self.__time,
                                                               language=language))


class Reject:
    def __init__(self, proxy: dict):
        self._proxy = proxy

    async def start(self):
        await self._update_reject()
        await self._mailing()

    async def _update_reject(self):
        await pg.update_orders_client_rejected(order_client_id=self._proxy.get('order_client_id'))

    async def _mailing(self):
        await self._mailing_driver()
        try:
            await self._mailing_client()
        except BotBlocked:
            print('reject')
            await pg.block_status(user_id=self._proxy.get('client_id'), status=False)

    async def _mailing_driver(self):
        Text_lang = Txt.language[self._proxy.get('lang')]
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=self._proxy.get('driver_id'), message_id=self._proxy.get('message_id'),
                                        text=Text_lang.order.driver.reject)

    async def _mailing_client(self):
        if self._proxy.get('type') == "passenger":
            await self._mailing_passenger()
        elif self._proxy.get('type') == "delivery":
            if await self._reject_check() is False:
                await self._mailing_delivery()

    async def _mailing_passenger(self):
        Text_lang = Txt.language[self._proxy.get('lang_client')]
        await bot.send_message(chat_id=self._proxy.get('client_id'), text=Text_lang.menu.passenger,
                               reply_markup=await reply.main_menu(language=self._proxy.get('lang_client')))
        await bot.send_message(chat_id=self._proxy.get('client_id'),
                               text=await form_new.order_cancel(language=self._proxy.get('lang_client'),
                                                                name=self._proxy.get('name'),
                                                                car=self._proxy.get('car_value')),
                               reply_markup=await inline.menu_choose_more(
                                   order_client_id=self._proxy.get('order_client_id'),
                                   language=self._proxy.get('lang_client')))

    async def _mailing_delivery(self):
        Text_lang = Txt.language[self._proxy.get('lang_client')]
        await bot.send_message(chat_id=self._proxy.get('client_id'), text=Text_lang.cancel.client.delivery,
                               reply_markup=await reply.main_menu(language=self._proxy.get('lang_client')))

    async def _reject_check(self):
        self._proxy['date'] = datetime.datetime.strptime(self._proxy.get('date'), "%d.%m.%Y")
        check = await pg.check_order_reject(client_id=self._proxy.get('client_id'),
                                            type_of_application=self._proxy.get('type'),
                                            from_region=self._proxy.get('from_region'),
                                            from_town=self._proxy.get('from_town'),
                                            to_region=self._proxy.get('to_region'), to_town=self._proxy.get('to_town'),
                                            date_trip=self._proxy.get('date'), time_trip=self._proxy.get('time'),
                                            trip=self._proxy.get('trip'))
        return check


class Unpack:
    def __init__(self, call: types.CallbackQuery, proxy: dict):
        self._call = call
        self._proxy = proxy

    async def start(self):
        await self._unpack_call()
        await self._unpack_new_order()
        await self._unpack_driver()
        return self._proxy

    async def _unpack_call(self):
        self._proxy['order_client_id'] = int(self._call.data.split("_")[1])
        self._proxy['driver_id'] = self._call.from_user.id
        self._proxy['lang'] = await pg.select_language(user_id=self._call.from_user.id)
        self._proxy['message_id'] = self._call.message.message_id

    async def _unpack_new_order(self):
        self._proxy['order_driver_id'], self._proxy['client_id'], self._proxy['type'], \
        self._proxy['from_region'], self._proxy['from_town'], self._proxy['to_region'], self._proxy['to_town'], \
        date, self._proxy['time'], self._proxy['baggage'], self._proxy['num'], self._proxy['trip'], \
        self._proxy['phone_client'], self._proxy['route_id'],  self._proxy['cost'] = \
            await pg.new_order_driver(order_client_id=self._proxy['order_client_id'])
        self._proxy['date'] = datetime.date.strftime(date, "%d.%m.%Y")
        self._proxy['lang_client'] = await pg.select_language(user_id=self._proxy.get('client_id'))

    async def _unpack_driver(self):
        self._proxy['name'], self._proxy['phone_driver'], self._proxy['car'], self._proxy['cond'], \
        self._proxy['price'] = await pg.select_parameters_route(route_id=self._proxy.get('route_id'))
        self._proxy['car_value'] = await pg.id_to_car(car_id=self._proxy.get('car'))
        if self._proxy['type'] == 'delivery':
            self._proxy['price'] = self._proxy['cost'] - Txt.money.price.package_way_price[self._proxy['trip']]


class Condition:
    def __init__(self, proxy: dict):
        self._proxy = proxy

    async def places_check(self):
        num = self._proxy.get('num')
        if self._proxy.get('from_region') == self._proxy.get('to_region'):
            return True
        else:
            free_places = await pg.check_places_orders_driver(order_driver_id=self._proxy.get('order_driver_id'))
            return free_places >= num

    async def active_check(self):
        return await pg.select_order_client_check(order_client_id=self._proxy.get('order_client_id'))

    async def price_check(self):
        wallet = await pg.select_all_wallet(driver_id=self._proxy.get('driver_id'))
        order_price = await self.order_price()

        return wallet >= order_price

    async def order_price(self):
        place = self._proxy.get('num') if self._proxy.get('num') != 0 else 1
        tax = await func.percent_price(price=self._proxy.get('price'))
        order_price = place * tax
        return order_price


class NewOrderDriver(StatesGroup):
    new_order_driver = State()

    def __init__(self):
        self.__call = None
        self.__data = None

    async def menu_accept_order(self, call: types.CallbackQuery, state: FSMContext):
        unpack = Unpack(call=call, proxy=await state.get_data())
        await state.set_data(data=await unpack.start())
        self.__data = await state.get_data()
        self.__call = call
        condition = Condition(proxy=await state.get_data())
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
            data['order_price'] = await condition.order_price()
            condition_active = await condition.active_check()
            condition_places = await condition.places_check()
            condition_wallet = await condition.price_check()
        if condition_active is True and condition_places is True and condition_wallet is True:
            accept = Accept(call=call, proxy=await state.get_data())
            await accept.start()
            await call.answer()
        elif condition_places is False:
            await call.answer(text=Text_lang.alert.driver.places_error3, show_alert=True)
        elif condition_wallet is False:
            await call.answer(text=Text_lang.alert.driver.insufficient_funds, show_alert=True)
        elif condition_active is False:
            await call.answer(text=Text_lang.alert.driver.accept_order_late, show_alert=True)
        await state.set_state("MenuDriver:menu_driver_level1")
        print("accept", await state.get_data())

    async def menu_reject_order(self, call: types.CallbackQuery, state: FSMContext):
        unpack = Unpack(call=call, proxy=await state.get_data())
        await state.set_data(data=await unpack.start())
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
        condition_active = await pg.select_order_client_check(order_client_id=data.get('order_client_id'))
        if condition_active is True:
            reject = Reject(proxy=await state.get_data())
            await reject.start()
            await call.answer()
        elif condition_active is False:
            await call.answer(text=Text_lang.alert.driver.accept_order_late, show_alert=True)
        await state.set_state("MenuDriver:menu_driver_level1")

    def register_handlers_new_order_driver(self, dp: Dispatcher):
        dp.register_callback_query_handler(self.menu_accept_order, lambda x: x.data and x.data.startswith("accept"),    state="*")
        dp.register_callback_query_handler(self.menu_reject_order, lambda x: x.data and x.data.startswith("reject"),    state="*")