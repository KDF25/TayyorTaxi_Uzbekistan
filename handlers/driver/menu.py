from contextlib import suppress
from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageToDeleteNotFound, MessageNotModified

from config import bot
from handlers.driver.active_order import ActiveOrderDriver
from handlers.driver.driver import Driver
from handlers.driver.between_regions import DriverBetweenRegions
from handlers.driver.between_towns import DriverBetweenTowns
from handlers.driver.personal_cabinet import PersonalCabinet

from keyboards.inline.driver.inline_driver import InlineDriver
from keyboards.reply.reply_kb import Reply

from pgsql import pg

from text.driver.form_active_order import FormActiveOrderDriver
from text.driver.form_driver import FormDriver
from text.driver.form_registration import FormRegistration
from text.driver.form_menu import FormMenuDriver
from text.language.main import Text_main



Txt = Text_main()
reply = Reply()
inline = InlineDriver()
form = FormMenuDriver()
form_driver = FormDriver()
form_registration = FormRegistration()
form_active = FormActiveOrderDriver()
active = ActiveOrderDriver()


class MenuDriver(StatesGroup):
    menu_driver_level1 = State()
    menu_driver_level2 = State()
    menu_driver_level3 = State()
    menu_driver_level4 = State()
    menu_driver_level5 = State()
    menu_driver_level6 = State()
    menu_driver_level7 = State()
    menu_driver_level8 = State()

    def __init__(self):
        self.__id = None

    async def menu_change(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            await state.set_data(data={"lang": data.get('lang')})
            Text_lang = Txt.language[data.get('lang')]
            print(data)
        await bot.send_message(chat_id=message.from_user.id, text=Text_lang.questions.driver.change,
                               reply_markup=await reply.change(language=data.get('lang')))
        await self.menu_driver_level1.set()

    async def main_menu_driver(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            await state.set_data(data={"lang": data.get('lang')})
            Text_lang = Txt.language[data.get('lang')]
            print(data)
        await bot.send_message(chat_id=message.from_user.id, text=Text_lang.menu.main_menu,
                               reply_markup=await reply.online(language=data.get('lang')))
        await self.menu_driver_level1.set()

    async def menu_setting(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
            print(data)
        await bot.send_message(chat_id=message.from_user.id, text=Text_lang.menu.settings,
                               reply_markup=await reply.setting(language=data.get('lang')))

    async def menu_change_language(self, message: types.Message, state: FSMContext):
        new_language = message.text
        user_id = message.from_user.id
        new_language = await self.change_language(new_language=new_language, user_id=user_id)
        async with state.proxy() as data:
            data['lang'] = new_language
            Text_lang = Txt.language[data.get('lang')]
        await bot.send_message(chat_id=message.from_user.id, text=Text_lang.menu.main_menu,
                               reply_markup=await reply.online(language=data.get('lang')))

    async def change_language(self, new_language: str, user_id: int):
        if new_language == "🇷🇺 Ru":
            new_language = 'rus'
        elif new_language == "🇺🇿 Уз (кир)":
            new_language = 'uzb'
        elif new_language == "🇺🇿 Uz (lat)":
            new_language = 'ozb'
        await pg.update_language(language=new_language, user_id=user_id)
        return new_language

    async def menu_information(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
        await bot.send_message(chat_id=message.from_user.id, text=Text_lang.menu.information,
                               reply_markup=await reply.information(language=data.get('lang')))

    async def menu_about_us(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            await bot.send_message(chat_id=message.from_user.id, text=await form.about_us(language=data.get('lang')),
                                   disable_web_page_preview=False)

    async def menu_how_to_use(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            await bot.send_message(chat_id=message.from_user.id, text=await form.how_to_use(language=data.get('lang')),
                                   disable_web_page_preview=False)

    async def menu_feedback(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
        await bot.send_message(chat_id=message.from_user.id, text=Text_lang.feedback.feedback)

    async def menu_online(self, message: Union[types.Message, types.CallbackQuery], state: FSMContext):
        self.__id = message.from_user.id
        async with state.proxy() as self.__data:
            await state.set_data(data={"lang": self.__data.get('lang'), 'analise_id': self.__data.get('analise_id')})
            print((await state.get_data()))
            await self._route_exist()
            if isinstance(message, types.Message):
                # if self.__route_id is not None:
                #     self.__data['route_id'] = self.__route_id[0]
                self.__data['analise_id'] = await pg.insert_driver(user_id=message.from_user.id)
                await bot.send_message(chat_id=message.from_user.id, text=self.__Text_lang.greeting.driver,
                                       reply_markup=await reply.main_menu(language=self.__data.get('lang')))
                await bot.send_message(chat_id=message.from_user.id, reply_markup=self.__markup, text=self.__text)
            elif isinstance(message, types.CallbackQuery):
                with suppress(MessageNotModified):
                    await bot.edit_message_text(chat_id=message.from_user.id, message_id=message.message.message_id,
                                                text=self.__text, reply_markup=self.__markup)
                    await message.answer()
            await Driver.driver_level1.set()

    async def _route_exist(self):
        self.__route_id = await pg.route_exist(driver_id=self.__id)
        self.__Text_lang = Txt.language[self.__data.get('lang')]
        self.__text = await form_driver.menu_active_route(language=self.__data.get('lang'), driver_id=self.__id)
        self.__markup = await inline.menu_active_route(language=self.__data.get('lang'), driver_id=self.__id)

    async def menu_active_order(self, message: Union[types.Message, types.CallbackQuery], state: FSMContext):
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
            data['driver_id'] = message.from_user.id
        await bot.send_message(chat_id=data.get('driver_id'), text=Text_lang.menu.order,
                               reply_markup=await reply.main_menu(language=data.get('lang')))
        await active.active_order_check(data=data)
        await ActiveOrderDriver.active_order_driver.set()

    async def menu_personal_cabinet(self, message: Union[types.Message, types.CallbackQuery], state: FSMContext):
        async with state.proxy() as data:
            await state.set_data(data={"lang": data.get('lang')})
            Text_lang = Txt.language[data.get('lang')]
            data['driver_id'] = message.from_user.id
        if isinstance(message, types.Message):
            await bot.send_message(chat_id=message.from_user.id, text=Text_lang.menu.personal_cabinet,
                                   reply_markup=await reply.personal_cabinet(language=data.get('lang')))
        elif isinstance(message, types.CallbackQuery):
            with suppress(MessageToDeleteNotFound):
                await bot.delete_message(chat_id=message.from_user.id, message_id=message.message.message_id)
                await bot.send_message(chat_id=message.from_user.id, text=Text_lang.menu.personal_cabinet,
                                       reply_markup=await reply.personal_cabinet(language=data.get('lang')))
        await PersonalCabinet.personal_cabinet_level1.set()


    def register_handlers_driver_menu(self, dp: Dispatcher):
        dp.register_message_handler(self.menu_change, text=Txt.menu.change,                                             state=self.menu_driver_level1)
        dp.register_message_handler(self.main_menu_driver, text=Txt.menu.main_menu,
                                    state=[*Driver.states_names] + [*MenuDriver.states_names] +
                                          [*ActiveOrderDriver.states_names] + [*PersonalCabinet.states_names] +
                                           [*DriverBetweenRegions.states_names] + [*DriverBetweenTowns.states_names])

        dp.register_message_handler(self.main_menu_driver, text=Txt.option.no,                                          state=self.menu_driver_level1)
        dp.register_message_handler(self.menu_setting, text=Txt.menu.settings,                                          state=[*MenuDriver.states_names])
        dp.register_message_handler(self.menu_change_language, text=Txt.settings.language,                              state=self.menu_driver_level1)

        dp.register_message_handler(self.menu_information, text=Txt.menu.information,                                   state=[*MenuDriver.states_names])
        dp.register_message_handler(self.menu_about_us, text=Txt.information.about_us,                                  state=[*MenuDriver.states_names])
        dp.register_message_handler(self.menu_how_to_use, text=Txt.information.how_to_use,                              state=[*MenuDriver.states_names])
        dp.register_message_handler(self.menu_feedback, text=Txt.information.feedback,                                  state=[*MenuDriver.states_names])

        # переход в ветку на линиии
        dp.register_message_handler(self.menu_online, text=Txt.menu.online,                                             state=self.menu_driver_level1)
        dp.register_callback_query_handler(self.menu_online, text='back',                                               state=[Driver.driver_level2])

        # переход в ветку активные заказы
        dp.register_message_handler(self.menu_active_order, text=Txt.menu.order,                                        state=self.menu_driver_level1)


        # переход в ветку ЛК
        dp.register_message_handler(self.menu_personal_cabinet, text=Txt.menu.personal_cabinet,                         state=self.menu_driver_level1)
        dp.register_callback_query_handler(self.menu_personal_cabinet, lambda x: x.data and x.data.startswith("back"),
                                           state=[PersonalCabinet.wallet_level1, PersonalCabinet.change_data_level1])
