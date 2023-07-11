from contextlib import suppress

from aiogram import types, Dispatcher
from aiogram.utils.exceptions import MessageNotModified, MessageToDeleteNotFound

from config import dp, bot, storage
from keyboards.inline.driver.inline_driver import InlineDriver
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.reply.reply_kb import Reply

from text.driver.form_registration import FormRegistration
from pgsql import pg
from typing import Union
from text.language.main import Text_main

Txt = Text_main()
form = FormRegistration()
reply = Reply()
inline = InlineDriver()


class RegistrationDriver(StatesGroup):
    registration_level1 = State()
    registration_level2 = State()
    registration_level3 = State()
    registration_level4 = State()
    registration_level5 = State()
    registration_level6 = State()
    registration_level7 = State()
    registration_level8 = State()

    async def menu_name(self, message: Union[types.Message, types.CallbackQuery], state: FSMContext):
        async with state.proxy() as data:
            if isinstance(message, types.Message):
                data['user_id'] = message.from_user.id
                data['username'] = message.from_user.username
                data['name'] = message.text
                text_send1, text_send2 = await form.greeting(language=data.get('lang'), name=data.get('name'))
                await bot.send_message(chat_id=message.from_user.id, text=text_send1,
                                       reply_markup=await reply.share_phone(language=data.get('lang')))
                await bot.send_message(chat_id=message.from_user.id, text=text_send2,
                                       reply_markup=await inline.menu_share_phone(language=data.get('lang')))
                await self.next()
            elif isinstance(message, types.CallbackQuery):
                print(data)
                text_send1, text_send2 = await form.greeting(language=data.get('lang'), name=data.get('name'))
                with suppress(MessageToDeleteNotFound):
                    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message.message_id)
                await bot.send_message(chat_id=message.from_user.id, text=text_send1,
                                       reply_markup=await reply.share_phone(language=data.get('lang')))
                with suppress(MessageToDeleteNotFound):
                    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message.message_id - 1)
                await bot.send_message(chat_id=message.from_user.id, text=text_send2,
                                       reply_markup=await inline.menu_share_phone(language=data.get('lang')))
                await self.previous()
                await message.answer()

    async def phone_accept(self, message: types.Message, state: FSMContext, number):
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
            data["phone"] = number
            await bot.send_message(chat_id=message.from_user.id, text=Text_lang.menu.driver,
                                   reply_markup=await reply.main_menu(language=data.get('lang')))
            await bot.send_message(chat_id=message.from_user.id, text=Text_lang.questions.registration.auto,
                                   reply_markup=await inline.menu_car(language=data.get('lang')))

    async def menu_phone_text(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
            try:
                number = int(message.text.replace(" ", ""))
                number_len = len(str(number))
                number_start = str(number)[0:3]
                if number_len == 12 and number_start == '998':
                    await self.next()
                    await self.phone_accept(message=message, state=state, number=number)
                else:
                    await bot.send_message(chat_id=message.from_user.id, text=Text_lang.alert.phone.alert)
            except ValueError:
                await bot.send_message(chat_id=message.from_user.id, text=Text_lang.alert.phone.alert)

    async def menu_phone_contact(self, message: Union[types.Message, types.CallbackQuery], state:FSMContext):
        print(message)
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
            if isinstance(message, types.Message):
                number = int(message.contact.phone_number)
                await self.next()
                await self.phone_accept(message=message, state=state, number=number)
            elif isinstance(message, types.CallbackQuery):
                await self.previous()
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=message.message.message_id,
                                            text=Text_lang.questions.registration.auto,
                                            reply_markup=await inline.menu_car(language=data.get('lang')))
                await message.answer()

    async def menu_agreement(self, call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            dta = call.data.split('_')
            data['car'] = int(dta[1])
            data['car_value'] = await pg.id_to_car(car_id=int(dta[1]))
        if dta[0] == 'car':
            await self.next()
        elif dta[0] == 'back':
            await self.previous()
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=await form.agreement(name=data.get("name"), phone=data.get("phone"),
                                                                  car=data.get("car_value"), language=data.get('lang')),
                                        reply_markup=await inline.menu_agreement(language=data.get('lang')),
                                        disable_web_page_preview=True)
        await call.answer()
        print(data)

    async def menu_registration(self, call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
            await pg.first_rec_driver(driver_id=call.from_user.id, name=data.get("name"), username=data.get('username'),
                                      wallet=Txt.money.wallet.wallet, phone=data.get('phone'), car=data.get("car"))
        with suppress(MessageToDeleteNotFound):
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id-1)
        video = Text_lang.video.video_driver
        await bot.send_video(chat_id=call.from_user.id, video=video, caption=Text_lang.video.driver)
        await bot.send_message(chat_id=call.from_user.id, text=await form.finish(data=data),
                               reply_markup=await reply.online(language=data.get('lang')),
                               disable_web_page_preview=True)
        await state.set_state("MenuDriver:menu_driver_level1")
        print("ok", await state.get_state())

    def register_handlers_registration(self, dp: Dispatcher):
        dp.register_message_handler(self.menu_name, content_types="text",                                               state=self.registration_level1)
        dp.register_callback_query_handler(self.menu_name, lambda x: x.data and x.data.startswith("back"),              state=self.registration_level3)

        dp.register_message_handler(self.menu_phone_text, content_types="text",                                         state=self.registration_level2)
        dp.register_message_handler(self.menu_phone_contact, content_types="contact",                                   state=self.registration_level2)
        dp.register_callback_query_handler(self.menu_phone_contact, lambda x: x.data and x.data.startswith("back"),     state=self.registration_level4)

        dp.register_callback_query_handler(self.menu_agreement, lambda x: x.data and x.data.startswith("car"),          state=self.registration_level3)
        dp.register_callback_query_handler(self.menu_agreement, lambda x: x.data and x.data.startswith("back"),         state=self.registration_level5)

        dp.register_callback_query_handler(self.menu_registration, lambda x: x.data and x.data.startswith("agree"),     state=self.registration_level4)

