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
from handlers.client.client import Client
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


class Mailing:
    def __init__(self, proxy: dict):
        self._proxy = proxy

    async def start(self):
        await self._client()
        try:
            await self._driver()
        except BotBlocked:
            print("block mail")
            await self._block()

    async def _client(self):
        Text_lang = Txt.language[self._proxy.get('lang')]
        with suppress(MessageNotModified):
            markup = await inline.menu_choose_more(language=self._proxy.get('lang'))
            await bot.edit_message_text(chat_id=self._proxy.get('client_id'), message_id=self._proxy.get('message_id'),
                                        text=Text_lang.order.client.passenger, reply_markup=markup)

    async def _driver(self):
        language = await pg.select_language(user_id=self._proxy.get('driver_id'))
        markup = await inline.menu_accept_order(order_client_id=self._proxy.get('order_client_id'), language=language)
        text = await form.order_driver(data=self._proxy, language=language)
        await bot.send_message(chat_id=self._proxy.get("driver_id"), text=text, reply_markup=markup)

    async def _block(self):
        await asyncio.sleep(120)
        await pg.block_status(user_id=self._proxy.get('driver_id'), status=False)
        try:
            await self._close_order()
        except BotBlocked:
            print("block driver block")
            await pg.block_status(user_id=self._proxy.get('client_id'), status=False)

    async def _close_order(self):
        print('not_accept')
        language = await pg.select_language(user_id=self._proxy.get('client_id'))
        Text_lang = Txt.language[language]
        text = await form_new.order_cancel(language=language, name=self._proxy.get('name'),
                                           car=self._proxy.get('car_value'))
        await pg.delay_passenger(order_client_id=self._proxy.get('order_client_id'))
        await bot.send_message(chat_id=self._proxy.get('client_id'), text=Text_lang.menu.passenger,
                               reply_markup=await reply.main_menu(language=self._proxy.get('lang')))
        await bot.send_message(chat_id=self._proxy.get('client_id'), text=text,
                               reply_markup=await inline_driver.menu_choose_more(
                                   order_client_id=self._proxy.get('order_client_id'), language=self._proxy.get('lang')))


class Delay:
    def __init__(self, proxy: dict):
        self._proxy = proxy

    async def start(self):
        # 7200 sec
        await asyncio.sleep(7200)
        await self._accept_check()

    async def _accept_check(self):
        if await self._check() is False:
            try:
                await self._close_order()
            except BotBlocked:
                print("block accept check")
                await pg.block_status(user_id=self._proxy.get('client_id'), status=False)

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
        print('not_accept')
        language = await pg.select_language(user_id=self._proxy.get('client_id'))
        Text_lang = Txt.language[language]
        text = await form_new.order_cancel(language=language, name=self._proxy.get('name'),
                                           car=self._proxy.get('car_value'))
        await pg.delay_passenger(order_client_id=self._proxy.get('order_client_id'))
        await bot.send_message(chat_id=self._proxy.get('client_id'), text=Text_lang.menu.passenger,
                               reply_markup=await reply.main_menu(language=self._proxy.get('lang')))
        await bot.send_message(chat_id=self._proxy.get('client_id'), text=text,
                               reply_markup=await inline_driver.menu_choose_more(
                                   order_client_id=self._proxy.get('order_client_id'), language=self._proxy.get('lang')))


class ClientBetweenTowns(StatesGroup):
    town_level1 = State()
    town_level2 = State()
    town_level3 = State()
    town_level4 = State()
    town_level5 = State()
    town_level6 = State()
    town_level7 = State()
    town_level8 = State()
    town_level9 = State()
    town_level10 = State()
    town_level11 = State()
    town_level12 = State()


    async def menu_region(self, call: types.CallbackQuery, state: FSMContext):
        await self.town_level1.set()
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
            question = Text_lang.questions.passenger.from_region
            data.pop("from_region")
            data.pop("from_region_value")
            data.pop("to_region")
            data.pop("to_region_value")
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=await form.main_text(question=question, data=data),
                                        reply_markup=await inline.menu_region(language=data.get('lang')))
        await call.answer()

    async def menu_from_town(self, call: types.CallbackQuery, state: FSMContext):
        await self.town_level2.set()
        async with state.proxy() as data:
            dta = call.data.split('_')
            Text_lang = Txt.language[data.get('lang')]
            question = Text_lang.questions.passenger.from_town
            if dta[0] == "region":
                data['type'] = "passenger"
                data['client_id'] = int(call.from_user.id)
                data["from_region"] = int(dta[1])
                data["to_region"] = data.get("from_region")
                data["from_region_value"] = await pg.id_to_region(reg_id=data.get("from_region"),
                                                                  language=data.get('lang'))
                data["to_region_value"] = data.get("from_region_value")
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

    async def menu_date(self, call: types.CallbackQuery, state: FSMContext):
        await self.town_level3.set()
        async with state.proxy() as data:
            dta = call.data.split('_')
            if dta[0] == "town":
                data["from_town"] = int(dta[1])
                data["from_town_value"] = await pg.id_to_town(reg_id=data.get("from_town"), language=data.get('lang'))
            elif dta[0] == "back":
                data.pop('date')
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=await form.menu_date(data=data),
                                        reply_markup=await inline.menu_date(language=data.get('lang')))
        print(data)
        await call.answer()

    async def menu_time(self, call: types.CallbackQuery, state: FSMContext):
        await self.town_level4.set()
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
                                        reply_markup=await inline.menu_time(time=data.get('time'),language=data.get('lang')))
        print(asizeof(data), data)
        await call.answer()

    # async def menu_datetime(self, call: types.CallbackQuery, state: FSMContext):
    #     await self.town_level3.set()
    #     async with state.proxy() as data:
    #         dta = call.data.split('_')
    #         if dta[0] == "town":
    #             data["from_town"] = int(dta[1])
    #             data["from_town_value"] = await pg.id_to_town(reg_id=data.get("from_town"), language=data.get('lang'))
    #             data['time'] = await func.time()
    #             data['date'] = await func.date()
    #             # await pg.update_to_region(id=data['analise_id'], to_region=data['to_region'])
    #         # if dta[0] == "town":
    #         #     data["to_town"] = int(dta[1])
    #         #     data["to_town_value"] = await pg.id_to_town(reg_id=data.get("to_town"), language=data.get('lang'))
    #         #     data['time'] = await func.time()
    #         #     data['date'] = await func.date()
    #         #     await pg.update_to_town(id=data['analise_id'], to_town=data['to_town'])
    #         elif dta[0] == "back":
    #             data.pop('num')
    #     with suppress(MessageNotModified):
    #         await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
    #                                     text=await form.menu_datetime(data=data),
    #                                     reply_markup=await inline.menu_datetime(date=data.get('date'),
    #                                                                             time=data.get('time'),
    #                                                                             language=data.get('lang'),
    #                                                                             type_app=data.get('type')))
    #     print(data)
    #     await call.answer()
    #
    # async def menu_date_change(self, call: types.CallbackQuery, state: FSMContext):
    #     async with state.proxy() as data:
    #         dta = call.data.split('_')
    #         data['date'] = dta[1]
    #     with suppress(MessageNotModified):
    #         await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
    #                                     text=await form.menu_datetime(data=data),
    #                                     reply_markup=await inline.menu_datetime(date=data.get('date'),
    #                                                                             time=data.get('time'),
    #                                                                             language=data.get('lang'),
    #                                                                             type_app=data.get('type')))
    #     print(data)
    #     await call.answer()
    #
    # async def menu_time_change(self, call: types.CallbackQuery, state: FSMContext):
    #     async with state.proxy() as data:
    #         time = str(call.data.split('_')[1])
    #         if time in data['time'] and len(data.get('time')) > 1:
    #             data['time'].remove(time)
    #         elif time not in data['time']:
    #             data['time'].append(time)
    #             data['time'] = natsorted(data.get('time'))
    #     with suppress(MessageNotModified):
    #         await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
    #                                     text=await form.menu_datetime(data=data),
    #                                     reply_markup=await inline.menu_datetime(date=data.get('date'),
    #                                                                             time=data.get('time'),
    #                                                                             language=data.get('lang'),
    #                                                                             type_app=data.get('type')))
    #     print(asizeof(data), data)
    #     await call.answer()

    async def menu_number(self, call: types.CallbackQuery, state: FSMContext):
        await self.town_level5.set()
        async with state.proxy() as data:
            # dta = call.data.split('_')
            await pg.update_datetime(id=data['analise_id'], date=data['date'], time=data['time'])
            # data['date'] = dta[1]
            # data['num'] = int(dta[1])
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=await form.menu_num_baggage(data=data),
                                        reply_markup=await inline.menu_number(language=data.get('lang')))
        print(data)
        await call.answer()

    async def menu_to_town(self, call: types.CallbackQuery, state: FSMContext):
        await self.town_level6.set()
        async with state.proxy() as self.__data:
            dta = call.data.split('_')
            Text_lang = Txt.language[self.__data.get('lang')]
            question = Text_lang.questions.passenger.to_town
            if dta[0] == "num":
                self.__data["num"] = int(dta[1])
                # data["to_region_value"] = await pg.id_to_region(reg_id=data.get("to_region"), language=data.get('lang'))
                # await pg.update_to_region(id=data['analise_id'], to_region=data['to_region'])
            elif dta[0] == "back":
                self.__data.pop("to_town")
                self.__data.pop("to_town_value")
            await self._select_towns()
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=await form.main_text(question=question, data=self.__data),
                                        reply_markup=await inline.menu_town_exist(reg_id=self.__data.get("to_region"),
                                                                                  language=self.__data.get('lang'),
                                                                                  towns=self.__towns))
        print(self.__data)
        await call.answer()

    async def _select_towns(self):
        towns = await pg.select_between_towns(from_region=self.__data.get("from_region"),
                                                from_towns=self.__data.get("from_town"),
                                                to_region=self.__data.get("to_region"),
                                                places=self.__data.get('num'),
                                                date=self.__data.get("date"), times=self.__data.get('time'),
                                                client_id=self.__data.get('client_id'))
        # towns = []
        self.__towns = {}
        for i in towns:
            self.__towns[i[0]] = i[1]

    async def menu_model(self, call: types.CallbackQuery, state: FSMContext):
        await self.town_level7.set()
        async with state.proxy() as data:
            dta = call.data.split('_')
            if dta[0] == "town":
                data["to_town"] = int(dta[1])
                data["to_town_value"] = await pg.id_to_town(reg_id=int(dta[1]), language=data.get('lang'))
                # await pg.update_model(id=data['analise_id'], car=data["car"])
            elif dta[0] == "back":
                data.pop('car')
                data.pop('car_value')
            with suppress(MessageNotModified):
                await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                            text=await form.car_text(data=data),
                                            reply_markup=await inline.menu_car(data=data))
            await call.answer()

    async def menu_zero_town(self, call: types.CallbackQuery, state: FSMContext):
        # await self.town_level5.set()
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
            await call.answer(show_alert=True, text=Text_lang.alert.passenger.zeroTown)

    async def menu_distinct_car(self, call: types.CallbackQuery, state: FSMContext):
        await self.town_level8.set()
        async with state.proxy() as data:
            dta = call.data.split('_')
            if dta[0] == "car":
                data["car"] = int(dta[1])
                data["car_value"] = await pg.id_to_car(car_id=int(dta[1]))
                await pg.update_model(id=data['analise_id'], car=data["car"])
            elif dta[0] == "back":
                data.pop("order")
                data.pop('driver_id')
                data.pop('conditioner')
                data.pop('price')
                data.pop('cost')
        print(data)
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=await form.model_text(data=data),
                                        reply_markup=await inline.menu_distinct_car(data=data))
        await call.answer()

    async def menu_order(self, call: types.CallbackQuery, state: FSMContext):
        await self.town_level9.set()
        async with state.proxy() as data:
            dta = call.data.split('_')
            if dta[0] == "order":
                await self._date(date=data.get("date"))
                data["route_id"] = int(dta[1])
                order = await pg.select_route_params(route_id=data.get("route_id"))
                data['driver_id'] = order[0]
                data['name'] = order[1]
                data['places'] = (await pg.select_places(route_id=data.get("route_id"),
                                                         from_region=data.get("from_region"),
                                                         to_region=data.get("to_region"), date=self.__date))[0][0]
                data['conditioner'] = order[2]
                data['price'] = order[3]
                data['cost'] = order[3] * data.get('num')
                await pg.update_driver(id=data['analise_id'], driver_id=data['driver_id'], price=data['price'])
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=await form.order_passenger(data=data),
                                        reply_markup=await inline.menu_order(language=data.get('lang')))
        await call.answer()

    async def _date(self, date):
        self.__date = datetime.datetime.strptime(date, "%d.%m.%Y").date()

    async def _booking(self, state: FSMContext):
        async with state.proxy() as data:
            await self._order_driver_exist(data=await state.get_data())
            data['order_driver_id'] = self.__condition[0]
            data['order_client_id'] = await pg.order_client_rec(order_driver_id=data.get('order_driver_id'),
                                                                client_id=data.get("client_id"),
                                                                type_trip=data.get("type"),
                                                                from_region=data.get("from_region"),
                                                                from_town=data.get("from_town"),
                                                                to_region=data.get("to_region"),
                                                                to_town=data.get("to_town"),
                                                                date_trip=self.__date, time_trip=data.get("time"),
                                                                baggage=0, places=data.get("num"),
                                                                trip=0, phone=data.get('phone_client'),
                                                                route_id=data.get("route_id"), cost=data.get("cost"))
            # data['order_client_id'] = await pg.parametrs_to_order_id_client(client_id=data.get("client_id"),
            #                                                                 order_driver_id=data.get("order_driver_id"))

    async def _order_driver_exist(self, data):
        self.__data = data
        await self._date(date=self.__data.get("date"))
        await self._condition()
        if self.__condition is None:
            await self._not_exist()

    async def _condition(self):
        self.__condition = await pg.select_order_driver_id(route_id=self.__data['route_id'],
                                                           from_region=self.__data['from_region'],
                                                           to_region=self.__data['to_region'], date=self.__date)

    async def _not_exist(self):
        await pg.default_order_driver(route_id=self.__data['route_id'], from_region=self.__data['from_region'],
                                      from_town=self.__data['from_town'], to_town=self.__data['to_town'],
                                      to_region=self.__data['to_region'], date=self.__date)
        await self._condition()

    async def menu_booking(self, call: types.CallbackQuery, state: FSMContext):
        await self.next()
        await call.answer()
        async with state.proxy() as self.__data:
            Text_lang = Txt.language[self.__data.get('lang')]
            if self.__data.get('phone_client') is None:
                with suppress(MessageToDeleteNotFound):
                    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
                await bot.send_message(chat_id=call.message.chat.id, text=Text_lang.menu.passenger,
                                       reply_markup=await reply.share_phone(language=self.__data.get('lang')))
                with suppress(MessageToDeleteNotFound):
                    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id - 1)
                message_1 = await bot.send_message(chat_id=call.from_user.id, text=Text_lang.questions.passenger.phone,
                                                   reply_markup=await inline.menu_share_phone(language=self.__data.get('lang')))
                self.__data['message_id'] = message_1.message_id
            else:
                with suppress(MessageToDeleteNotFound):
                    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
                await self._book(state=state)

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

    async def menu_phone_contact(self, message: Union[types.Message, types.CallbackQuery], state: FSMContext):
        self.__message = message
        self.__number = int(message.contact.phone_number)
        await self._book(state=state)

    async def _book(self, state: FSMContext):
        await self.next()
        async with state.proxy() as self.__data:
            if self.__data.get('phone_client') is None:
                self.__data['phone_client'] = self.__number
                # await pg.update_phone_client(row_id=self.__data.get('row_id'))
        # await pg.update_book_client(row_id=self.__data.get('row_id'))
        await self._booking(state=state)
        mailing = Mailing(proxy=await state.get_data())
        delay = Delay(proxy=await state.get_data())
        await mailing.start()
        await self.town_level1.set()
        await delay.start()

    def register_handlers_client_between_towns(self, dp: Dispatcher):
        dp.register_callback_query_handler(self.menu_region, text='in',                                                 state=Client.client_level1)
        dp.register_callback_query_handler(self.menu_region, text='back',                                               state=self.town_level2)

        dp.register_callback_query_handler(self.menu_from_town, lambda x: x.data.startswith("region"),                  state=self.town_level1)
        dp.register_callback_query_handler(self.menu_from_town, text='back',                                            state=self.town_level3)

        dp.register_callback_query_handler(self.menu_date, lambda x: x.data.startswith("town"),                         state=self.town_level2)
        dp.register_callback_query_handler(self.menu_date, text='back',                                                 state=self.town_level4)

        dp.register_callback_query_handler(self.menu_time, lambda x: x.data.startswith("date"),                         state=self.town_level3)
        dp.register_callback_query_handler(self.menu_time, text='back',                                                 state=self.town_level5)

        dp.register_callback_query_handler(self.menu_time_change, lambda x: x.data and x.data.startswith("time"),       state=self.town_level4)

        # dp.register_callback_query_handler(self.menu_datetime, lambda x: x.data.startswith("town"),                     state=self.town_level2)
        # dp.register_callback_query_handler(self.menu_datetime, text='back',                                             state=self.town_level4)
        #
        # dp.register_callback_query_handler(self.menu_date_change, lambda x: x.data and x.data.startswith("date"),       state=self.town_level3)
        # dp.register_callback_query_handler(self.menu_time_change, lambda x: x.data and x.data.startswith("time"),       state=self.town_level3)

        dp.register_callback_query_handler(self.menu_number, text='continue',                                           state=self.town_level4)
        dp.register_callback_query_handler(self.menu_number, text='back',                                               state=self.town_level6)

        dp.register_callback_query_handler(self.menu_to_town, lambda x: x.data.startswith("num"),                       state=self.town_level5)
        dp.register_callback_query_handler(self.menu_to_town, text='back',                                              state=self.town_level7)

        dp.register_callback_query_handler(self.menu_zero_town, text='zeroTown',                                        state=self.town_level6)

        dp.register_callback_query_handler(self.menu_model, lambda x: x.data.startswith("town"),                        state=self.town_level6)
        dp.register_callback_query_handler(self.menu_model, text='back',                                                state=self.town_level8)

        dp.register_callback_query_handler(self.menu_distinct_car, lambda x: x.data and x.data.startswith("car"),       state=self.town_level7)
        dp.register_callback_query_handler(self.menu_distinct_car, text='back',                                         state=self.town_level9)
        #
        dp.register_callback_query_handler(self.menu_order, lambda x: x.data and x.data.startswith("order"),            state=self.town_level8)
        dp.register_callback_query_handler(self.menu_order, text='back',                                                state=self.town_level10)

        dp.register_callback_query_handler(self.menu_booking, lambda x: x.data and x.data.startswith("book"),           state=self.town_level9)
        #

        dp.register_message_handler(self.menu_phone_text, content_types=["text"],                                       state=self.town_level10)
        dp.register_message_handler(self.menu_phone_contact, content_types=["contact"],                                 state=self.town_level10)

