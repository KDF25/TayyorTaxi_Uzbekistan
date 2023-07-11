

from contextlib import suppress

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageNotModified, MessageToDeleteNotFound, BotBlocked

from config import bot
from handlers.driver.driver import Driver
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


class DriverBetweenTowns(StatesGroup):

    town_level1 = State()
    town_level2 = State()
    town_level3 = State()
    town_level4 = State()
    town_level5 = State()
    town_level6 = State()
    town_level7 = State()
    town_level8 = State()
    town_level9 = State()

    def __init__(self):
        self.__town = None
        self.__Text_lang = None
        self.__call = None
        self.__state = None
        self.__data = None

    async def menu_region(self, call: types.CallbackQuery, state: FSMContext):
        await self.town_level1.set()
        await call.answer()
        async with state.proxy() as data:
            # await pg.update_type_driver(id=data['analise_id'], type_app='out')
            Text_lang = Txt.language[data.get('lang')]
            text = Text_lang.questions.driver.route
            markup = await inline.menu_from_region(language=data.get('lang'))
            with suppress(MessageNotModified):
                await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text,
                                            reply_markup=markup)

            print(data)

    async def menu_towns(self, call: types.CallbackQuery, state: FSMContext):
        await self.town_level2.set()
        async with state.proxy() as self.__data:
            dta = call.data.split('_')
            self.__call = call
            if dta[0] == 'region':
                self.__data['regions'] = int(dta[1])
                self.__data['regions_value'] = await pg.id_to_region(reg_id=self.__data.get('regions'),
                                                                     language=self.__data.get('lang'))
            self.__data['towns'] = []
            self.__data['towns_value'] = []
            await self._towns()
            await self._towns_not_full()
            await self._towns_message()

    async def menu_duplicate_route(self, call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
            await call.answer(show_alert=True, text=Text_lang.alert.driver.check)

    async def menu_cond(self, call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as self.__data:
            self.__call = call
            self.__Text_lang = Txt.language[self.__data.get('lang')]
            await self._towns()
            await self._towns_count()
            await self._towns_message()

    async def _towns(self):
        dta = self.__call.data.split('_')
        if dta[0] == 'town':
            self.__town = int(dta[1])
            await self._towns_change()

    async def _towns_change(self):
        if self.__town not in self.__data['towns'] and len(self.__data['towns']) < 2:
            await self._towns_append()
        elif self.__town in self.__data['towns'] and len(self.__data['towns']) > 0:
            await self._towns_remove()

    async def _towns_append(self):
        self.__data['towns'].append(self.__town)
        self.__data['towns_value'].append(await pg.id_to_town(reg_id=self.__town, language=self.__data.get('lang')))

    async def _towns_remove(self):
        self.__data['towns'].remove(self.__town)
        self.__data['towns_value'].remove(await pg.id_to_town(reg_id=self.__town, language=self.__data.get('lang')))

    async def _towns_count(self):
        if len(self.__data['towns']) < 2:
            await self._towns_not_full()
        elif len(self.__data['towns']) == 2:
            await self.town_level3.set()
            await self._towns_full()

    async def _towns_not_full(self):
        town = await pg.select_to_towns(driver_id=self.__call.from_user.id, region=self.__data.get('regions'))
        town = [i[0] for i in town]
        self.__text = await form.menu_towns(language=self.__data.get('lang'), region=self.__data.get('regions_value'))
        self.__markup = await inline.menu_towns(language=self.__data.get('lang'), towns=self.__data.get('towns_value'),
                                                reg_id=self.__data.get('regions'), all_towns=town)

    async def _towns_full(self):
        self.__text = await form.menu_cond(language=self.__data.get('lang'), towns=self.__data.get('towns_value'))
        self.__markup = await inline.menu_cond(language=self.__data.get('lang'))

    async def _towns_message(self):
        with suppress(MessageNotModified):
            await self.__call.answer()
            await bot.edit_message_text(chat_id=self.__call.from_user.id, message_id=self.__call.message.message_id,
                                        text=self.__text, reply_markup=self.__markup)

    async def menu_price(self, call: types.CallbackQuery, state: FSMContext):
        await self.town_level4.set()
        await call.answer()
        async with state.proxy() as data:
            dta = call.data.split('_')
            Text_lang = Txt.language[data.get('lang')]
            if dta[0] == 'cond':
                data['cond'] = int(dta[1])
                # await pg.update_conditioner(id=data['analise_id'], conditioner=data['cond'])
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=Text_lang.questions.driver.price,
                                        reply_markup=await inline.menu_price(language=data.get('lang')))
            await call.answer()
        print(data)
        await call.answer()

    async def menu_order(self, call: types.CallbackQuery, state: FSMContext):
        await self.town_level5.set()
        await call.answer()
        async with state.proxy() as data:
            dta = call.data.split('_')
            data['price'] = int(dta[1])
            # await pg.update_price(id=data['analise_id'], price=data['price'])
            name, phone, car = await pg.select_parametrs_driver(driver_id=call.from_user.id)
            car_value = await pg.id_to_car(car_id=car)
            data['driver_id'] = call.from_user.id
            data['name'] = name
            data['phone_driver'] = phone
            data['car'] = car
            data['car_value'] = car_value
            # text = await form.order_driver(data=await state.get_data())
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=await form.order_between_towns(data=data),
                                        reply_markup=await inline.menu_order(language=data.get('lang')))
            await call.answer()
        print(data)
        await call.answer()

    # booking
    async def menu_booking(self, call: types.CallbackQuery, state: FSMContext):
        self.__call = call
        async with state.proxy() as self.__data:
            # await pg.update_ordered_driver(id=self.__data['analise_id'])
            await self._booking()
            await self._mailing_driver()
            await state.set_state("MenuDriver:menu_driver_level1")
            await state.set_data(data={"lang": self.__data.get('lang')})

    async def _booking(self):
        await pg.order_driver_rec(driver_id=self.__data.get("driver_id"), name=self.__data.get('name'),
                                  phone=self.__data.get('phone_driver'), car=self.__data.get('car'),
                                  from_region=self.__data.get('regions'), from_towns=[self.__data.get('towns')[0]],
                                  to_region=self.__data.get('regions'), to_towns=[self.__data.get('towns')[1]],
                                  conditioner=self.__data.get("cond"),
                                  price=self.__data.get("price"))

    async def _mailing_driver(self):
        Text_lang = Txt.language[self.__data.get('lang')]
        with suppress(MessageToDeleteNotFound):
            await bot.delete_message(chat_id=self.__call.from_user.id, message_id=self.__call.message.message_id)
        await bot.send_message(chat_id=self.__call.message.chat.id, text=Text_lang.order.driver.driver,
                               reply_markup=await reply.online(language=self.__data.get('lang')))
        with suppress(MessageToDeleteNotFound):
            await bot.delete_message(chat_id=self.__call.from_user.id, message_id=self.__call.message.message_id - 1)

    def register_handlers_driver_between_towns(self, dp: Dispatcher):
        dp.register_callback_query_handler(self.menu_region, text='in',                                                 state=Driver.driver_level2)
        dp.register_callback_query_handler(self.menu_region, text='back',                                               state=self.town_level2)

        dp.register_callback_query_handler(self.menu_towns, lambda x: x.data.startswith("region"),                      state=self.town_level1)
        dp.register_callback_query_handler(self.menu_towns,  text='back',                                               state=self.town_level3)

        dp.register_callback_query_handler(self.menu_duplicate_route, text='duplicationRouteIn',                        state=self.town_level2)

        dp.register_callback_query_handler(self.menu_cond, lambda x: x.data.startswith("town"),                         state=self.town_level2)
        dp.register_callback_query_handler(self.menu_cond, text='back',                                                 state=self.town_level4)

        dp.register_callback_query_handler(self.menu_price, lambda x: x.data.startswith("cond"),                        state=self.town_level3)
        dp.register_callback_query_handler(self.menu_price, text='back',                                                state=self.town_level5)
        #
        dp.register_callback_query_handler(self.menu_order, lambda x: x.data.startswith("price"),                       state=self.town_level4)
        dp.register_callback_query_handler(self.menu_booking, text="book",                                              state=self.town_level5)

