from contextlib import suppress
from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageNotModified, MessageToDeleteNotFound

from config import bot
from handlers.client.client import Client
from handlers.client.delivery import Delivery
from handlers.client.between_regions import ClientBetweenRegions
from handlers.client.between_towns import ClientBetweenTowns
from handlers.driver.menu import MenuDriver
from handlers.driver.registration import RegistrationDriver
from handlers.client.active_order import ActiveOrderClient
from keyboards.inline.client.inline_client import InlineClient
from keyboards.reply.reply_kb import Reply
from pgsql import pg

from text.client.form_menu import FormMenu
from text.client.form_client import FormClient
from text.client.form_delivery import FormDelivery
from text.client.form_active_order import FormActiveOrderClient
from text.language.main import Text_main
from text.language.ru import Text_ru
from pympler.asizeof import asizeof

reply = Reply()
inline = InlineClient()

Txt =Text_main()
RU = Text_ru()

active = ActiveOrderClient()
form = FormMenu()
form_client = FormClient()
form_delivery = FormDelivery()
form_active = FormActiveOrderClient()


class Menu(StatesGroup):
    registration = State()
    menu_client_level1 = State()
    menu_client_level2 = State()

    def __init__(self):
        self.__exist_lang = None
        self.__exist = None

    async def void(self, call: types.CallbackQuery):
        await call.answer()

    # /start
    async def command_start(self, message: types.Message, state: FSMContext):
        # await self.menu_client_level1.set()
        print(message)
        self.__exist = await pg.exist_client(message.from_user.id)
        self.__exist_lang = await pg.exist_lang(message.from_user.id)
        if self.__exist is True and self.__exist_lang is True:
            await pg.block_status(user_id=message.from_user.id, status=True)
            await state.reset_data()
            await self.check_user(message=message, state=state)
        elif self.__exist is False or self.__exist_lang is False:
            await self.new_user(message=message)

    async def new_user(self, message: types.Message):
        await bot.send_message(chat_id=message.from_user.id, text=Txt.choose_language,
                               reply_markup=await inline.choose_language())
        if self.__exist is False:
            await self.rec_client(message=message)
            await self.registration.set()

    async def rec_client(self, message: types.Message):
        user_id = message.from_user.id
        name = message.from_user.first_name
        username = message.from_user.username
        deeplink = message.get_args()
        await pg.first_rec_client(user_id=user_id, name=name, username=username, status=True, deeplink=deeplink)

    async def check_user(self, message: types.Message, state: FSMContext):
        exist = await pg.exist_driver(driver_id=message.from_user.id)
        if exist is True:
            await self.start_driver(message=message, state=state)
        elif exist is False:
            await self.start_client(message=message, state=state)

    async def start_client(self, message: types.Message, state: FSMContext):
        await self.greeting_client(client_id=message.from_user.id, state=state)
        await self.menu_client_level1.set()

    async def start_driver(self, message: types.Message, state: FSMContext):
        await self.greeting_driver(driver_id=message.from_user.id, state=state)
        await MenuDriver.menu_driver_level1.set()

    async def greeting_client(self, client_id, state: FSMContext):
        async with state.proxy() as data:
            data['lang'] = await pg.select_language(user_id=client_id)
            Text_lang = Txt.language[data.get('lang')]
        await bot.send_message(chat_id=client_id, text=Text_lang.greeting.hello,
                               reply_markup=await reply.start_keyb(language=data.get('lang')))

    async def greeting_driver(self, driver_id, state: FSMContext):
        async with state.proxy() as data:
            data['lang'] = await pg.select_language(user_id=driver_id)
            Text_lang = Txt.language[data.get('lang')]
            name = await pg.name_driver(driver_id=driver_id)
            greeting = f"{Text_lang.greeting.hello} {name}"
        await bot.send_message(chat_id=driver_id, text=greeting, reply_markup=await reply.online(language=data.get('lang')))

    async def menu_choose_language(self, call: types.callback_query, state: FSMContext):
        language = call.data
        user_id = call.from_user.id
        await pg.update_language(language=language, user_id=user_id)
        await self.menu_client_level1.set()
        async with state.proxy() as data:
            data['lang'] = language
        with suppress(MessageToDeleteNotFound):
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=call.message.chat.id, text=await form.main(language=language),
                               reply_markup=await reply.start_keyb(language=language), disable_web_page_preview=True)
        print(data)
        await call.answer()
        await self.menu_client_level1.set()

    # main menu
    async def main_menu(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            await state.set_data(data={"lang": data.get('lang')})
            Text_lang = Txt.language[data.get('lang')]
        await bot.send_message(chat_id=message.from_user.id, text=Text_lang.menu.main_menu,
                               reply_markup=await reply.start_keyb(language=data.get('lang')))
        await self.menu_client_level1.set()

    # settings
    async def menu_setting(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
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
                               reply_markup=await reply.start_keyb(language=data.get('lang')))

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

    async def menu_allactive_order(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['client_id'] = message.from_user.id
            Text_lang = Txt.language[data.get('lang')]
        await bot.send_message(chat_id=data.get('client_id'), text=Text_lang.menu.order,
                               reply_markup=await reply.main_menu(language=data.get('lang')))
        await active.active_order_check(data=data)
        await ActiveOrderClient.active_order_client.set()

    async def menu_passenger(self, message: Union[types.Message, types.CallbackQuery], state: FSMContext):
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
            # question = Text_lang.questions.passenger.from_region
            await state.set_data(data={"lang": data.get('lang'), "analise_id": data.get('analise_id')})
            print(' 1 ', await state.get_data())
            if isinstance(message, types.Message):
                data['analise_id'] = await pg.insert_client(user_id=message.from_user.id, type_app='passenger')
                await bot.send_message(chat_id=message.from_user.id,  text=Text_lang.greeting.passenger,
                                       reply_markup=await reply.main_menu(language=data.get('lang')))
                await bot.send_message(chat_id=message.from_user.id, text=Text_lang.questions.driver.route,
                                       reply_markup=await inline.menu_route(language=data.get('lang')))

                                       # text=await form_client.main_text(question=question, data=await state.get_data()))
            elif isinstance(message, types.CallbackQuery):
                with suppress(MessageNotModified):
                    await bot.edit_message_text(chat_id=message.from_user.id, message_id=message.message.message_id,
                                                text=Text_lang.questions.driver.route,
                                                reply_markup=await inline.menu_route(language=data.get('lang')))
                await message.answer()
        await Client.client_level1.set()
        print(await state.get_state(), await state.get_data())

    # delivery
    async def menu_delivery(self, message: Union[types.Message, types.CallbackQuery], state: FSMContext):
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
            question = Text_lang.questions.delivery.from_region
            await state.set_data(data={"lang": data.get('lang'), "analise_id": data.get('analise_id')})
            print(' 1 ', await state.get_data())
            if isinstance(message, types.Message):
                data['analise_id'] = await pg.insert_client(user_id=message.from_user.id, type_app='delivery')
                await bot.send_message(chat_id=message.from_user.id, text=Text_lang.greeting.delivery,
                                       reply_markup=await reply.main_menu(language=data.get('lang')))
                await bot.send_message(chat_id=message.from_user.id,
                                       reply_markup=await inline.menu_region(language=data.get('lang'), back=False),
                                       text=await form_delivery.main_text(question=question, data=await state.get_data()))
            elif isinstance(message, types.CallbackQuery):
                async with state.proxy() as data:
                    data.pop("from_region")
                    data.pop("from_region_value")
                with suppress(MessageNotModified):
                    await bot.edit_message_text(chat_id=message.from_user.id, message_id=message.message.message_id,
                                                text=await form_delivery.main_text(question=question, data=data),
                                                reply_markup=await inline.menu_region(language=data.get('lang')))
                await message.answer()
            await Delivery.delivery_level1.set()
            print(await state.get_state(), await state.get_data())

    # driver
    async def menu_driver(self, message: Union[types.Message, types.CallbackQuery], state: FSMContext):
        async with state.proxy() as data:
            await state.set_data(data={"lang": data.get('lang')})
            Text_lang = Txt.language[data.get('lang')]
        if isinstance(message, types.Message):
            exist = await pg.exist_driver(driver_id=message.from_user.id)
            if exist is True:
                await self.greeting_driver(driver_id=message.from_user.id, state=state)
                await MenuDriver.menu_driver_level1.set()
            elif exist is False:
                await bot.send_message(chat_id=message.from_user.id, text=Text_lang.questions.registration.name,
                                       reply_markup=await reply.main_menu(language=data.get('lang')))
                await RegistrationDriver.registration_level1.set()
        elif isinstance(message, types.CallbackQuery):
            with suppress(MessageToDeleteNotFound):
                await bot.delete_message(chat_id=message.from_user.id, message_id=message.message.message_id)
                await bot.send_message(chat_id=message.from_user.id, text=Text_lang.questions.registration.name,
                                       reply_markup=await reply.main_menu(language=data.get('lang')))
                await bot.delete_message(chat_id=message.from_user.id, message_id=message.message.message_id-1)
                await RegistrationDriver.registration_level1.set()

    def register_handlers_client_menu(self, dp: Dispatcher):
        dp.register_message_handler(self.command_start, commands="start", state='*')
        dp.register_callback_query_handler(self.void, text='void', state="*")
        dp.register_message_handler(self.main_menu, text=Txt.menu.main_menu,
                                    state=[*Client.states_names] + [*Menu.states_names] + [*Delivery.states_names] +
                                          [*ActiveOrderClient.states_names] + [*RegistrationDriver.states_names] +
                                          [*ClientBetweenRegions.states_names] + [*ClientBetweenTowns.states_names])

        dp.register_message_handler(self.menu_setting, text=Txt.menu.settings,                                          state=self.menu_client_level1)
        dp.register_message_handler(self.menu_change_language, text=Txt.settings.language,                              state=self.menu_client_level1)

        dp.register_message_handler(self.menu_information, text=Txt.menu.information,                                   state=self.menu_client_level1)
        dp.register_message_handler(self.menu_about_us, text=Txt.information.about_us,                                  state=self.menu_client_level1)
        dp.register_message_handler(self.menu_how_to_use, text=Txt.information.how_to_use,                              state=self.menu_client_level1)
        dp.register_message_handler(self.menu_feedback, text=Txt.information.feedback,                                  state=self.menu_client_level1)

        dp.register_callback_query_handler(self.menu_choose_language, text=['rus', 'ozb', 'uzb'],                            state=self.registration)
        dp.register_message_handler(self.menu_allactive_order, text=Txt.menu.order,                                               state=self.menu_client_level1)

        # переход в водительскую ветку
        dp.register_message_handler(self.menu_driver, text=Txt.menu.driver,                                             state=self.menu_client_level1)
        dp.register_callback_query_handler(self.menu_driver, lambda x: x.data and x.data.startswith("phoneback"),       state=RegistrationDriver.registration_level2)
        # переход в клиентскую часть из водителя
        dp.register_message_handler(self.main_menu, text=Txt.option.da,                                                 state=MenuDriver.menu_driver_level1)
        # переход в пассажирскую ветку
        dp.register_message_handler(self.menu_passenger, text=Txt.menu.passenger,                                       state=self.menu_client_level1)
        dp.register_callback_query_handler(self.menu_passenger, lambda x: x.data and x.data.startswith("back"),         state=["ClientBetweenTowns:town_level1",
                                                                                                                               "ClientBetweenRegions:region_level1"])
        # переход в доставку
        dp.register_message_handler(self.menu_delivery, text=Txt.menu.delivery,                                         state=self.menu_client_level1)
        dp.register_callback_query_handler(self.menu_delivery, lambda x: x.data and x.data.startswith("back"),          state=Delivery.delivery_level2)
        # dp.register_message_handler(self.rrr, content_types="video", state="*")
