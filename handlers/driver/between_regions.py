

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


class DriverBetweenRegions(StatesGroup):

    region_level1 = State()
    region_level2 = State()
    region_level3 = State()
    region_level4 = State()
    region_level5 = State()
    region_level6 = State()
    region_level7 = State()
    region_level8 = State()
    region_level9 = State()

    def __init__(self):
        self.__Text_lang = None
        self.__call = None
        self.__state = None
        self.__data = None

    async def menu_from_region(self, call: types.CallbackQuery, state: FSMContext):
        await self.region_level1.set()
        await call.answer()
        async with state.proxy() as data:
            # await pg.update_type_driver(id=data['analise_id'], type_app='out')
            Text_lang = Txt.language[data.get('lang')]
            question = Text_lang.questions.driver.from_region
            markup = await inline.menu_from_region(language=data.get('lang'))
            with suppress(MessageNotModified):
                await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                            text=question, reply_markup=markup)

            print(data)

    async def menu_from_town(self, call: types.CallbackQuery, state: FSMContext):
        await self.region_level2.set()
        await call.answer()
        async with state.proxy() as data:
            dta = call.data.split('_')
            if dta[0] == 'region':
                data['from_region'] = int(dta[1])
                data['from_region_value'] = await pg.id_to_region(reg_id=data.get('from_region'), language=data.get('lang'))
                data['from_towns'] = []
                data['from_towns_value'] = []
            # text = await form.out_region(language=data.get('lang'), regions=data.get('regions_value'))
            Text_lang = Txt.language[data.get('lang')]
            question = Text_lang.questions.driver.from_town
            markup = await inline.menu_town(language=data.get('lang'), towns=data.get('from_towns_value'),
                                            reg_id=data.get('from_region'))
            # await pg.update_from_region_driver(id=data['analise_id'], from_region=data['regions'][0])
            # await pg.update_to_region_driver(id=data['analise_id'], to_region=data['regions'][1])
            # await pg.update_towns_driver(id=data['analise_id'], from_town=0, to_town=0)
            with suppress(MessageNotModified):
                await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                            text=await form.main_text(data=data, question=question),
                                            reply_markup=markup)

            print(data)

    async def menu_from_town_change(self, call: types.CallbackQuery, state: FSMContext):
        self.__call = call
        async with state.proxy() as self.__data:
            await self._from_town_prepare()
            await self._from_town()

    async def _from_town_prepare(self):
        self.__town = int(self.__call.data.split('_')[1])
        self.__town_value = await pg.id_to_town(reg_id=self.__town, language=self.__data.get('lang'))
        self.__Text_lang = Txt.language[self.__data.get('lang')]

    async def _from_town(self):
        if self.__town not in self.__data['from_towns'] and len(self.__data.get('from_towns')) < 3:
            await self._from_town_append()
        elif self.__town in self.__data['from_towns'] and len(self.__data.get('from_towns')) > 0:
            await self._from_town_remove()
        elif self.__town not in self.__data['from_towns'] and len(self.__data.get('from_towns')) == 3:
            await self._from_town_4thTown()

    async def _from_town_append(self):
        self.__data['from_towns'].append(self.__town)
        self.__data['from_towns_value'].append(self.__town_value)
        await self._from_town_message()

    async def _from_town_remove(self):
        self.__data['from_towns'].remove(self.__town)
        self.__data['from_towns_value'].remove(self.__town_value)
        await self._from_town_message()

    async def _from_town_4thTown(self):
        await self.__call.answer(show_alert=True, text=self.__Text_lang.alert.driver.fourthTown)

    async def _from_town_message(self):
        with suppress(MessageNotModified):
            question = self.__Text_lang.questions.driver.to_town
            markup = await inline.menu_town(language=self.__data.get('lang'), towns=self.__data.get('from_towns_value'),
                                            reg_id=self.__data.get('from_region'))
            await bot.edit_message_text(chat_id=self.__call.from_user.id, message_id=self.__call.message.message_id,
                                        text=await form.main_text(data=self.__data, question=question), reply_markup=markup)
            await self.__call.answer()

    async def menu_to_region(self, call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as self.__data:
            self.__call = call
            self.__Text_lang = Txt.language[self.__data.get('lang')]
            await self._to_region()

    async def _to_region(self):
        if len(self.__data.get('from_towns')) == 0:
            await self._zero_from_towns()
        else:
            await self._count_from_towns()

    async def _zero_from_towns(self):
        await self.__call.answer(show_alert=True, text=self.__Text_lang.alert.driver.zeroTowns)

    async def _count_from_towns(self):
        with suppress(MessageNotModified):
            await self.__call.answer()
            await self.region_level3.set()
            question = self.__Text_lang.questions.driver.to_region
            # text = await form.out_region(language=data.get('lang'), regions=data.get('regions_value'))
            to_region = await pg.select_to_region(from_region=self.__data.get('from_region'), driver_id=self.__call.from_user.id)
            to_region = [i[0] for i in to_region]
            markup = await inline.menu_to_region(language=self.__data.get('lang'),
                                                 from_region=self.__data.get('from_region'), to_regions=to_region)
            self.__data.pop('to_region')
            self.__data.pop('to_region_value')
            with suppress(MessageNotModified):
                await bot.edit_message_text(chat_id=self.__call.from_user.id, message_id=self.__call.message.message_id,
                                            text=await form.main_text(data=self.__data, question=question),
                                            reply_markup=markup)

    async def menu_duplicate_route(self, call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
            await call.answer(show_alert=True, text=Text_lang.alert.driver.check)

    async def menu_to_town(self, call: types.CallbackQuery, state: FSMContext):
        await self.region_level4.set()
        await call.answer()
        async with state.proxy() as data:
            dta = call.data.split('_')
            if dta[0] == 'region':
                data['to_region'] = int(dta[1])
                data['to_region_value'] = await pg.id_to_region(reg_id=data.get('to_region'), language=data.get('lang'))
                data['to_towns'] = []
                data['to_towns_value'] = []
            # text = await form.out_region(language=data.get('lang'), regions=data.get('regions_value'))
            Text_lang = Txt.language[data.get('lang')]
            question = Text_lang.questions.driver.to_town
            markup = await inline.menu_town(language=data.get('lang'), towns=data.get('to_towns_value'),
                                            reg_id=data.get('to_region'))
            with suppress(MessageNotModified):
                await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                            text=await form.main_text(data=data, question=question), reply_markup=markup)
            print(data)

    async def menu_to_town_change(self, call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as self.__data:
            self.__call = call
            await self._to_town_prepare()
            await self._to_town()

    async def _to_town_prepare(self):
        self.__town = int(self.__call.data.split('_')[1])
        self.__town_value = await pg.id_to_town(reg_id=self.__town, language=self.__data.get('lang'))
        self.__Text_lang = Txt.language[self.__data.get('lang')]

    async def _to_town(self):
        if self.__town not in self.__data['to_towns'] and len(self.__data.get('to_towns')) < 3:
            await self._to_town_append()
        elif self.__town in self.__data['to_towns'] and len(self.__data.get('to_towns')) > 0:
            await self._to_town_remove()
        elif self.__town not in self.__data['to_towns'] and len(self.__data.get('to_towns')) == 3:
            await self._to_town_4thTown()

    async def _to_town_append(self):
        self.__data['to_towns'].append(self.__town)
        self.__data['to_towns_value'].append(self.__town_value)
        await self._to_town_message()

    async def _to_town_remove(self):
        self.__data['to_towns'].remove(self.__town)
        self.__data['to_towns_value'].remove(self.__town_value)
        await self._to_town_message()

    async def _to_town_4thTown(self):
        await self.__call.answer(show_alert=True, text=self.__Text_lang.alert.driver.fourthTown)

    async def _to_town_message(self):
        with suppress(MessageNotModified):
            question = self.__Text_lang.questions.driver.to_town
            markup = await inline.menu_town(language=self.__data.get('lang'), towns=self.__data.get('to_towns_value'),
                                            reg_id=self.__data.get('to_region'))
            await bot.edit_message_text(chat_id=self.__call.from_user.id, message_id=self.__call.message.message_id,
                                        text=await form.main_text(data=self.__data, question=question), reply_markup=markup)
            await self.__call.answer()

    async def menu_cond(self, call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as self.__data:
            self.__call = call
            self.__Text_lang = Txt.language[self.__data.get('lang')]
            await self._cond()

    async def _cond(self):
        if len(self.__data.get('to_towns')) == 0:
            await self._zero_to_towns()
        else:
            await self._count_to_towns()

    async def _zero_to_towns(self):
        await self.__call.answer(show_alert=True, text=self.__Text_lang.alert.driver.zeroTowns)

    async def _count_to_towns(self):
        with suppress(MessageNotModified):
            await self.region_level5.set()
            await self.__call.answer()
            question = self.__Text_lang.questions.driver.cond
            markup = await inline.menu_cond(language=self.__data.get('lang'))
            await bot.edit_message_text(chat_id=self.__call.from_user.id, message_id=self.__call.message.message_id,
                                        text=await form.main_text(data=self.__data, question=question), reply_markup=markup)

    async def menu_price(self, call: types.CallbackQuery, state: FSMContext):
        await self.region_level6.set()
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
            print(data)

    async def menu_order(self, call: types.CallbackQuery, state: FSMContext):
        await self.region_level7.set()
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
                                        text=await form.order_between_regions(data=data),
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
                                  from_region=self.__data.get('from_region'), from_towns=self.__data.get('from_towns'),
                                  to_region=self.__data.get('to_region'), to_towns=self.__data.get('to_towns'),
                                  conditioner=self.__data.get("cond"),price=self.__data.get("price"))

    async def _mailing_driver(self):
        Text_lang = Txt.language[self.__data.get('lang')]
        with suppress(MessageToDeleteNotFound):
            await bot.delete_message(chat_id=self.__call.from_user.id, message_id=self.__call.message.message_id)
        await bot.send_message(chat_id=self.__call.message.chat.id, text=Text_lang.order.driver.driver,
                               reply_markup=await reply.online(language=self.__data.get('lang')))
        with suppress(MessageToDeleteNotFound):
            await bot.delete_message(chat_id=self.__call.from_user.id, message_id=self.__call.message.message_id - 1)

    def register_handlers_driver_between_regions(self, dp: Dispatcher):
        dp.register_callback_query_handler(self.menu_from_region, text='out',                                           state=Driver.driver_level2)
        dp.register_callback_query_handler(self.menu_from_region, text='back',                                          state=self.region_level2)
        dp.register_callback_query_handler(self.menu_from_town, lambda x: x.data.startswith("region"),                  state=self.region_level1)
        dp.register_callback_query_handler(self.menu_from_town,  text='back',                                           state=self.region_level3)

        dp.register_callback_query_handler(self.menu_from_town_change, lambda x: x.data.startswith("town"),             state=self.region_level2)

        dp.register_callback_query_handler(self.menu_to_region, text='continue',                                        state=self.region_level2)
        dp.register_callback_query_handler(self.menu_to_region, text='back',                                            state=self.region_level4)

        dp.register_callback_query_handler(self.menu_duplicate_route, text='duplicationRouteOut',                       state=self.region_level3)

        dp.register_callback_query_handler(self.menu_to_town, lambda x: x.data.startswith("region"),                    state=self.region_level3)
        dp.register_callback_query_handler(self.menu_to_town, text='back',                                              state=self.region_level5)

        dp.register_callback_query_handler(self.menu_to_town_change, lambda x: x.data.startswith("town"),               state=self.region_level4)

        dp.register_callback_query_handler(self.menu_cond, text='continue',                                             state=self.region_level4)
        dp.register_callback_query_handler(self.menu_cond, text='back',                                                 state=self.region_level6)

        dp.register_callback_query_handler(self.menu_price, lambda x: x.data.startswith("cond"),                        state=self.region_level5)
        dp.register_callback_query_handler(self.menu_price, text='back',                                                state=self.region_level7)
        #
        dp.register_callback_query_handler(self.menu_order, lambda x: x.data.startswith("price"),                       state=self.region_level6)
        dp.register_callback_query_handler(self.menu_booking, text="book",                                              state=self.region_level7)

