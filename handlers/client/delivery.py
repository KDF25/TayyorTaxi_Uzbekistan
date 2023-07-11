import asyncio
import datetime
from contextlib import suppress

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageNotModified, MessageToDeleteNotFound, BotBlocked
from natsort import natsorted

from config import bot
from keyboards.inline.client.inline_client import InlineClient
from keyboards.reply.reply_kb import Reply
from pgsql import pg
from text.client.form_delivery import FormDelivery
from text.language.main import Text_main
from text.text_func import TextFunc

Txt = Text_main()
func = TextFunc()

reply = Reply()
inline = InlineClient()
form = FormDelivery()


class MailingBooking:
    def __init__(self, message: types.Message, proxy: dict):
        self.__route_id = None
        self.__driver_id = None
        self._proxy = proxy
        self._call = message

    async def start(self):
        await self._order_check()
        await self._mailing_client()

    async def _order_check(self):
        await self._orders()
        self._proxy['len'] = len(self.__orders)
        if len(self.__orders) != 0:
            await self._order_record()

    async def _orders(self):
        self.__orders = await pg.select_driver_to_delivery(from_region=self._proxy.get("from_region"),
                                                           from_towns=self._proxy.get("from_town"),
                                                           to_region=self._proxy.get("to_region"),
                                                           to_towns=self._proxy.get("to_town"),
                                                           date=self._proxy.get("date"), times=self._proxy.get("time"),
                                                           client_id=self._proxy.get("client_id"))
        print(self.__orders)
        self._proxy['date'] = datetime.datetime.strptime(self._proxy.get("date"), "%d.%m.%Y").date()

    async def _order_record(self):
        for self.__route_id, self.__driver_id in self.__orders:
            print(self.__route_id, self.__driver_id in self.__orders)
            await self._order_driver_exist()
            self._proxy['order_driver_id'], self._proxy['driver_id'], self._proxy['route_id'] = \
                self.__condition[0], self.__driver_id, self.__route_id
            await self._booking()
            await self._mailing_to_drivers()

    async def _order_driver_exist(self):
        await self._condition()
        if self.__condition is None:
            await self._not_exist()

    async def _condition(self):
        self.__condition = await pg.select_order_driver_id(route_id=self.__route_id,
                                                           from_region=self._proxy.get("from_region"),
                                                           to_region=self._proxy.get("to_region"),
                                                           date=self._proxy.get('date'))

    async def _not_exist(self):
        await pg.default_order_driver(route_id=self.__route_id, from_region=self._proxy.get("from_region"),
                                      from_town=self._proxy.get("from_town"), to_town=self._proxy.get("to_town"),
                                      to_region=self._proxy.get("to_region"), date=self._proxy.get("date"))
        await self._condition()

    async def _booking(self):
        self._proxy['order_client_id'] = await pg.order_client_rec(order_driver_id=self._proxy.get('order_driver_id'),
                                                                   client_id=self._proxy.get("client_id"),
                                                                   type_trip=self._proxy.get("type"),
                                                                   from_region=self._proxy.get("from_region"),
                                                                   from_town=self._proxy.get("from_town"),
                                                                   to_region=self._proxy.get("to_region"),
                                                                   to_town=self._proxy.get("to_town"),
                                                                   date_trip=self._proxy.get("date"),
                                                                   time_trip=self._proxy.get("time"),
                                                                   baggage=self._proxy.get("baggage"), places=0, trip=0,
                                                                   phone=self._proxy.get('phone_client'),
                                                                   route_id=self._proxy.get("route_id"),
                                                                   cost=self._proxy.get("cost"))
        # self._proxy['order_client_id'] = await pg.parametrs_to_order_id_client(
        #     client_id=self._proxy.get("client_id"), order_driver_id=self._proxy.get('order_driver_id'))

    async def _mailing_to_drivers(self):
        try:
            await self._mailing_driver()
        except BotBlocked:
            print("block_mail del")
            await pg.block_status(user_id=self._proxy.get('driver_id'), status=False)

    async def _mailing_driver(self):
        language = await pg.select_language(user_id=self._proxy.get('driver_id'))
        await bot.send_message(chat_id=self._proxy.get('driver_id'),
                               text=await form.order_driver(language=language, data=self._proxy),
                               reply_markup=await inline.menu_accept_order(
                                   order_client_id=self._proxy.get('order_client_id'), language=language))

    async def _mailing_client(self):
        Text_lang = Txt.language[self._proxy.get('lang')]
        with suppress(MessageToDeleteNotFound):
            await bot.delete_message(chat_id=self._call.from_user.id, message_id=self._call.message_id)
        await bot.send_message(chat_id=self._call.chat.id, text=Text_lang.order.client.delivery,
                               reply_markup=await reply.start_keyb(language=self._proxy.get('lang')))
        with suppress(MessageToDeleteNotFound):
            await bot.delete_message(chat_id=self._call.from_user.id, message_id=self._call.message_id - 1)


class Delay:
    def __init__(self, proxy: dict):
        self._proxy = proxy

    async def start(self):
        print('delay')
        await self._order_driver_exist()
        if self.__condition is False:
            print('no')
            await self._no_drivers()
        elif self.__condition is True:
            print('yes')
            await self._no_accept()

    async def _order_driver_exist(self):
        self.__condition = await pg.order_driver_exist(from_region=self._proxy.get("from_region"),
                                                       to_region=self._proxy.get("to_region"),
                                                       date=self._proxy.get("date"), times=self._proxy.get("time"))


    async def _no_drivers(self):
        try:
            print('set', datetime.datetime.now())
            # 180 sec
            await asyncio.sleep(180)
            print('get', datetime.datetime.now())
            await self._mail()
        except BotBlocked:
            print("block no orders")
            await pg.block_status(user_id=self._proxy.get('client_id'), status=False)

    async def _mail(self):
        Text_lang = Txt.language[self._proxy.get('lang')]
        await bot.send_message(chat_id=self._proxy.get('client_id'), text=Text_lang.cancel.client.delivery,
                               reply_markup=await reply.main_menu(language=self._proxy.get('lang')))

    async def _no_accept(self):
        try:
            # 7200 sec
            await asyncio.sleep(7200)
            await self._accept_check()
        except BotBlocked:
            print("block no order accept")
            await pg.block_status(user_id=self._proxy.get('client_id'), status=False)

    async def _accept_check(self):
        check = await self._check()
        if check is False:
            await self._close_order()

    async def _check(self):
        self._proxy['date'] = datetime.datetime.strptime(self._proxy.get("date"), "%d.%m.%Y").date()
        check = await pg.check_order_accept(client_id=self._proxy.get('client_id'),
                                            type_of_application=self._proxy.get('type'),
                                            from_region=self._proxy.get('from_region'),
                                            from_town=self._proxy.get('from_town'),
                                            to_region=self._proxy.get('to_region'),
                                            to_town=self._proxy.get('to_town'),
                                            date_trip=self._proxy.get('date'),
                                            time_trip=self._proxy.get('time'),
                                            trip=self._proxy.get('trip'))
        return check

    async def _close_order(self):
        await pg.delay_delivery(client_id=self._proxy.get('client_id'), type_of_application=self._proxy.get('type'),
                                from_region=self._proxy.get('from_region'), from_town=self._proxy.get('from_town'),
                                to_region=self._proxy.get('to_region'), to_town=self._proxy.get('to_town'),
                                date_trip=self._proxy.get('date'), time_trip=self._proxy.get('time'),
                                trip=self._proxy.get('trip'))
        await self._mail()


class Delivery(StatesGroup):
    delivery_level1 = State()
    delivery_level2 = State()
    delivery_level3 = State()
    delivery_level4 = State()
    delivery_level5 = State()
    delivery_level6 = State()
    delivery_level7 = State()
    delivery_level8 = State()
    delivery_level9 = State()
    delivery_level10 = State()
    delivery_level11 = State()

    def __init__(self):
        self.__call = None

    async def menu_from_town(self, call: types.CallbackQuery, state: FSMContext):
        await self.delivery_level2.set()
        async with state.proxy() as data:
            dta = call.data.split('_')
            Text_lang = Txt.language[data.get('lang')]
            question = Text_lang.questions.delivery.from_town
            if dta[0] == "region":
                data['type'] = "delivery"
                data['client_id'] = int(call.from_user.id)
                data["from_region"] = int(dta[1])
                data["from_region_value"] = await pg.id_to_region(reg_id=data.get("from_region"),
                                                                  language=data.get('lang'))
                await pg.update_from_region(id=data['analise_id'], from_region=data['from_region'])
            elif dta[0] == "back":
                data.pop("from_town")
                data.pop("from_town_value")
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=await form.main_text(question=question, data=data),
                                        reply_markup=await inline.menu_town(reg_id=data.get("from_region"),
                                                                            language=data.get('lang')))
        print(data)
        await call.answer()

    async def menu_to_region(self, call: types.CallbackQuery, state: FSMContext):
        await self.delivery_level3.set()
        async with state.proxy() as data:
            dta = call.data.split('_')
            Text_lang = Txt.language[data.get('lang')]
            question = Text_lang.questions.delivery.to_region
            if dta[0] == "town":
                data["from_town"] = int(dta[1])
                data["from_town_value"] = await pg.id_to_town(reg_id=data.get("from_town"),
                                                              language=data.get('lang'))
                await pg.update_from_town(id=data['analise_id'], from_town=data['from_town'])
            elif dta[0] == "back":
                data.pop("to_region")
                data.pop("to_region_value")
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=await form.main_text(question=question, data=data),
                                        reply_markup=await inline.menu_region(language=data.get('lang')))
        print(data)
        await call.answer()

    async def menu_to_town(self, call: types.CallbackQuery, state: FSMContext):
        await self.delivery_level4.set()
        async with state.proxy() as data:
            dta = call.data.split('_')
            Text_lang = Txt.language[data.get('lang')]
            question = Text_lang.questions.delivery.to_town
            if dta[0] == "region":
                data["to_region"] = int(dta[1])
                data["to_region_value"] = await pg.id_to_region(reg_id=data.get("to_region"), language=data.get('lang'))
                await pg.update_to_region(id=data['analise_id'], to_region=data['to_region'])
            elif dta[0] == "back":
                data.pop("to_town")
                data.pop("to_town_value")
                data.pop("time")
                data.pop("date")
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=await form.main_text(question=question, data=data),
                                        reply_markup=await inline.menu_town(reg_id=data.get("to_region"),
                                                                            language=data.get('lang')))
        print(data)
        await call.answer()

    async def menu_date(self, call: types.CallbackQuery, state: FSMContext):
        await self.delivery_level5.set()
        async with state.proxy() as data:
            dta = call.data.split('_')
            if dta[0] == "town":
                data["to_town"] = int(dta[1])
                data["to_town_value"] = await pg.id_to_town(reg_id=data.get("to_town"), language=data.get('lang'))
            elif dta[0] == "back":
                data.pop('date')
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=await form.menu_date(data=data),
                                        reply_markup=await inline.menu_date(language=data.get('lang')))
        print(data)
        await call.answer()

    async def menu_time(self, call: types.CallbackQuery, state: FSMContext):
        await self.delivery_level6.set()
        async with state.proxy() as data:
            dta = call.data.split('_')
            if dta[0] == "date":
                data["date"] = dta[1]
                data['time'] = await func.time()
                # await pg.update_to_region(id=data['analise_id'], to_region=data['to_region'])
            elif dta[0] == "back":
                data.pop('num')
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=await form.menu_time(data=data),
                                        reply_markup=await inline.menu_time(time=data.get('time'), language=data.get('lang')))
        print(data)
        await call.answer()

    async def menu_time_change(self, call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            time = str(call.data.split('_')[1])
            if time in data['time'] and len(data.get('time')) > 1:
                data['time'].remove(time)
            elif time not in data['time']:
                data['time'].append(time)
                data['time'] = natsorted(data.get('time'))
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=await form.menu_time(data=data),
                                        reply_markup=await inline.menu_time(time=data.get('time'),
                                                                            language=data.get('lang')))
        await call.answer()

    async def menu_baggage(self, call: types.CallbackQuery, state: FSMContext):
        await self.delivery_level7.set()
        async with state.proxy() as data:
            await pg.update_datetime(id=data['analise_id'], date=data['date'], time=data['time'])
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=await form.menu_package(data=data),
                                        reply_markup=await inline.menu_package(language=data.get('lang')))
        print(data)
        await call.answer()

    async def menu_share_phone(self, call: types.CallbackQuery, state: FSMContext):
        await self.delivery_level8.set()
        async with state.proxy() as data:
            dta = call.data.split('_')
            if dta[0] == 'baggage':
                data['baggage'] = int(dta[1])
                price = Txt.money.price.package_price[data.get('baggage')]
                price = await func.price_func(price=price, reg_1=data.get('from_region'), reg_2=data.get('to_region'))
                data['price'] = price
                data['cost'] = price
                with suppress(MessageNotModified):
                    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                                text=await form.order_delivery(data=data),
                                                reply_markup=await inline.menu_order(language=data.get('lang')))
            else:
                Text_lang = Txt.language[data.get('lang')]
                with suppress(MessageToDeleteNotFound):
                    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
                await bot.send_message(chat_id=call.message.chat.id, text=Text_lang.greeting.delivery,
                                       reply_markup=await reply.main_menu(language=data.get('lang')))
                with suppress(MessageToDeleteNotFound):
                    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id - 1)
                await bot.send_message(chat_id=call.from_user.id, text=await form.order_delivery(data=data),
                                       reply_markup=await inline.menu_order(language=data.get('lang')))
        print(data)
        await call.answer()

    async def menu_booking_delivery(self, call: types.CallbackQuery, state: FSMContext):
        await self.delivery_level9.set()
        await call.answer()
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
            with suppress(MessageToDeleteNotFound):
                await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await bot.send_message(chat_id=call.message.chat.id, text=Text_lang.greeting.delivery,
                                   reply_markup=await reply.share_phone(language=data.get('lang')))
            with suppress(MessageToDeleteNotFound):
                await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id - 1)
            await bot.send_message(chat_id=call.from_user.id, text=Text_lang.questions.share_number,
                                   reply_markup=await inline.menu_share_phone(language=data.get('lang')))

    async def menu_phone_text(self, message: types.Message, state: FSMContext):
        self.__message = message
        async with state.proxy() as data:
            try:
                Text_lang = Txt.language[data.get('lang')]
                self.__number = int(message.text.replace(" ", ""))
                number_len = len(str(self.__number))
                number_start = str(self.__number)[0:3]
                if number_len == 12 and number_start == '998':
                    await self._book(state=state)
                else:
                    await bot.send_message(chat_id=message.from_user.id, text=Text_lang.alert.phone.alert)
            except ValueError:
                await bot.send_message(chat_id=message.from_user.id, text=Text_lang.alert.phone.alert)

    async def menu_phone_contact(self, message: types.Message, state: FSMContext):
        self.__message = message
        self.__number = int(message.contact.phone_number)
        await self._book(state=state)

    async def _book(self, state: FSMContext):
        # await self.next()
        async with state.proxy() as self.__data:
            if self.__data.get('phone_client') is None:
                self.__data['phone_client'] = self.__number
                # await pg.update_phone_client(row_id=self.__data.get('row_id'))
        # await pg.update_book_client(row_id=self.__data.get('row_id'))
        mail_book = MailingBooking(message=self.__message, proxy=await state.get_data())
        delay = Delay(proxy=await state.get_data())
        await mail_book.start()
        await state.set_state("Menu:menu_client_level1")
        await delay.start()


    async def default(self, call: types.CallbackQuery, state: FSMContext):
        print(call.data, await state.get_state())

    def register_handlers_delivery(self, dp: Dispatcher):
        dp.register_callback_query_handler(self.menu_from_town, lambda x: x.data.startswith("region"),                  state=self.delivery_level1)
        dp.register_callback_query_handler(self.menu_from_town,  text='back',                                           state=self.delivery_level3)

        dp.register_callback_query_handler(self.menu_to_region, lambda x: x.data.startswith("town"),                    state=self.delivery_level2)
        dp.register_callback_query_handler(self.menu_to_region,  text='back',                                           state=self.delivery_level4)

        dp.register_callback_query_handler(self.menu_to_town, lambda x: x.data.startswith("region"),                    state=self.delivery_level3)
        dp.register_callback_query_handler(self.menu_to_town,  text='back',                                             state=self.delivery_level5)

        dp.register_callback_query_handler(self.menu_date, lambda x: x.data.startswith("town"),                         state=self.delivery_level4)
        dp.register_callback_query_handler(self.menu_date,  text='back',                                                state=self.delivery_level6)

        dp.register_callback_query_handler(self.menu_time, lambda x: x.data.startswith("date"),                         state=self.delivery_level5)
        dp.register_callback_query_handler(self.menu_time,  text='back',                                                state=self.delivery_level7)

        dp.register_callback_query_handler(self.menu_time_change, lambda x: x.data.startswith("time"),                  state=self.delivery_level6)

        dp.register_callback_query_handler(self.menu_baggage, lambda x: x.data.startswith("continue"),                  state=self.delivery_level6)
        dp.register_callback_query_handler(self.menu_baggage,  text='back',                                             state=self.delivery_level8)

        dp.register_callback_query_handler(self.menu_share_phone, lambda x: x.data.startswith("baggage"),               state=self.delivery_level7)
        dp.register_callback_query_handler(self.menu_share_phone,  text='back',                                         state=self.delivery_level9)

        dp.register_callback_query_handler(self.menu_booking_delivery, lambda x: x.data and x.data.startswith("book"),  state=self.delivery_level8)

        dp.register_message_handler(self.menu_phone_text, content_types=["text"],                                       state=self.delivery_level9)
        dp.register_message_handler(self.menu_phone_contact, content_types=["contact"],                                 state=self.delivery_level9)
