from contextlib import suppress
from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageToDeleteNotFound, MessageNotModified
from payme_api.get_check import GetCheck
from click_api.get_url import GetUrl
from config import bot
from handlers.driver.driver import Driver
from keyboards.inline.driver.inline_driver import InlineDriver
from keyboards.reply.reply_kb import Reply
from pgsql import pg
from datetime_now.datetime_now import dt_now

from text.driver.form_personal_data import FormPersonalData
from text.language.main import Text_main

Txt = Text_main()
form = FormPersonalData()
reply = Reply()
inline = InlineDriver()
driver = Driver()


class PersonalCabinet(StatesGroup):
    personal_cabinet_level1 = State()

    change_data_level1 = State()
    change_name_level1 = State()
    change_car_level1 = State()
    change_phone_level1 = State()

    wallet_level1 = State()
    wallet_level2 = State()
    wallet_level3 = State()
    wallet_level4 = State()
    wallet_level5 = State()

    async def menu_personal_data(self, message:  Union[types.Message, types.CallbackQuery], state: FSMContext):
        await self.change_data_level1.set()
        if isinstance(message, types.Message):
            driver_id = message.from_user.id
            name, phone_driver, car = await pg.select_parametrs_driver(driver_id=driver_id)
            async with state.proxy() as data:
                data['driver_id'] = driver_id
                data['name'] = name
                data['phone_driver'] = phone_driver
                data['car'] = car
                Text_lang = Txt.language[data.get('lang')]
            text_personal_data = await form.personal_data_form(driver_id=driver_id, name=name, car=car,
                                                               phone_driver=phone_driver, language=data.get('lang'))
            await bot.send_message(chat_id=message.from_user.id,
                                   text=Text_lang.buttons.personal_cabinet.data.data,
                                   reply_markup=await reply.main_menu(language=data.get('lang')))
            await bot.send_message(chat_id=message.from_user.id, text=text_personal_data,
                                   reply_markup=await inline.menu_personal_data(language=data.get('lang')))
        elif isinstance(message, types.CallbackQuery):
            async with state.proxy() as data:
                Text_lang = Txt.language[data.get('lang')]
                text_personal_data = await form.personal_data_form(driver_id=data.get('driver_id'), car=data.get('car'),
                                                                   name=data.get('name'), language=data.get('lang'),
                                                                   phone_driver=data.get('phone_driver'))
            with suppress(MessageNotModified):
                await bot.edit_message_text(chat_id=message.from_user.id,
                                            message_id=message.message.message_id, text=text_personal_data,
                                            reply_markup=await inline.menu_personal_data(language=data.get('lang')))

    async def menu_new_data(self, call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            data['type'] = call.data.split('_')[1]
            text = await form.change_data_form(type_payment=data.get('type'), language=data.get('lang'))
        if data.get('type') == 'car':
            await self.change_car_level1.set()
            with suppress(MessageNotModified):
                await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text,
                                            reply_markup=await inline.menu_car(language=data.get('lang')))
        elif data.get('type') == 'name':
            await self.change_name_level1.set()
            with suppress(MessageNotModified):
                await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text,
                                            reply_markup=await inline.menu_back(language=data.get('lang')))
        elif data.get("type") == "phone":
            await self.change_phone_level1.set()
            with suppress(MessageToDeleteNotFound):
                await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
                await bot.send_message(chat_id=call.from_user.id, text=text,
                                        reply_markup=await reply.share_phone(language=data.get('lang')))
        print(data)
        await call.answer()


    async def menu_new_name_rec(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
            data['name'] = message.text
            await pg.update_drivers_name(driver_id=data.get('driver_id'), name=data.get('name'))
            await pg.update_route_driver_name(driver_id=data.get('driver_id'), name=data.get('name'))
            with suppress(MessageToDeleteNotFound):
                await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id-1)
            await bot.send_message(chat_id=message.from_user.id,
                                   text=Text_lang.chain.personal_cabinet.new_data_rec,
                                   reply_markup=await reply.personal_cabinet(language=data.get('lang')))
            await self.personal_cabinet_level1.set()
            print(data)

    async def menu_new_car_rec(self, call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
            data['car'] = int(call.data.split('_')[1])
            await pg.update_drivers_car(driver_id=data.get('driver_id'), car=data.get('car'))
            await pg.update_route_driver_car(driver_id=data.get('driver_id'), car=data.get('car'))
            await pg.update_orders_accepted_car(driver_id=data.get('driver_id'), car=data.get('car'))
            await call.answer()
            with suppress(MessageToDeleteNotFound):
                await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await bot.send_message(chat_id=call.from_user.id,
                                   text=Text_lang.chain.personal_cabinet.new_data_rec,
                                   reply_markup=await reply.personal_cabinet(language=data.get('lang')))
            await self.personal_cabinet_level1.set()
            print(data)



    async def phone_accept(self, message: types.Message, state:FSMContext, number):
        async with state.proxy() as data:
            data["phone"] = number
            Text_lang = Txt.language[data.get('lang')]
        await pg.update_drivers_phone(driver_id=data.get('driver_id'), phone=data.get('phone'))
        await pg.update_route_driver_phone(driver_id=data.get('driver_id'), phone=data.get('phone'))
        await pg.update_orders_accepted_phone(driver_id=data.get('driver_id'), phone=data.get('phone'))
        await bot.send_message(chat_id=message.from_user.id,
                               text=Text_lang.chain.personal_cabinet.new_data_rec,
                               reply_markup=await reply.personal_cabinet(language=data.get('lang')))

    async def menu_new_phone_rec(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
            if data.get('type') == 'phone':
                try:
                    number = int(message.contact.phone_number)
                    await self.phone_accept(message=message, state=state, number=number)
                    await self.personal_cabinet_level1.set()
                except AttributeError:
                    try:
                        type(int(message.text.replace(" ", "")))
                        number = int(message.text.replace(" ", ""))
                        number_len = len(str(number))
                        number_start = str(number)[0:3]
                        if number_len == 12 and number_start == '998':
                            await self.phone_accept(message=message, state=state, number=number)
                            await self.personal_cabinet_level1.set()
                        else:
                            await bot.send_message(chat_id=message.from_user.id, text=Text_lang.alert.phone.alert)
                    except ValueError:
                        await bot.send_message(chat_id=message.from_user.id, text=Text_lang.alert.phone.alert)

    # wallet

    async def menu_wallet(self, message:  Union[types.Message, types.CallbackQuery], state: FSMContext):
        await self.wallet_level1.set()
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
            driver_id = message.from_user.id
            wallet = await pg.select_wallets(driver_id=driver_id)
            data['driver_id'] = driver_id
            data['wallet'] = [i for i in wallet]
            text_wallet = await form.wallet_form(driver_id=data.get('driver_id'), wallet=data.get('wallet'),
                                                 language=data.get('lang'))
            markup = await inline.menu_balance(language=data.get('lang'))
            if isinstance(message, types.Message):
                # driver_id = message.from_user.id
                # wallet = await pg.select_wallets(driver_id=driver_id)
                # data['driver_id'] = driver_id
                # data['wallet'] = [i for i in wallet]
                # text_wallet = await form.wallet_form(driver_id=driver_id, wallet=wallet, language=data.get('lang'))
                await bot.send_message(chat_id=message.from_user.id,
                                       text=Text_lang.buttons.personal_cabinet.wallet.wallet,
                                       reply_markup=await reply.main_menu(language=data.get('lang')))
                await bot.send_message(chat_id=message.from_user.id, text=text_wallet, reply_markup=markup)
            elif isinstance(message, types.CallbackQuery):
                # wallet = await pg.select_wallets(driver_id=data.get('driver_id'))
                # data['wallet'] = [i for i in wallet]
                # text_wallet = await form.wallet_form(driver_id=data.get('driver_id'), wallet=data.get('wallet'),
                #                                      language=data.get('lang'))
                with suppress(MessageNotModified):
                    await bot.edit_message_text(chat_id=message.from_user.id, message_id=message.message.message_id,
                                                text=text_wallet, reply_markup=markup)
                    await message.answer()
        print(data)

    async def menu_amount(self, call: types.CallbackQuery, state: FSMContext):
        await self.wallet_level2.set()
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=Text_lang.chain.personal_cabinet.payment,
                                        reply_markup=await inline.menu_cash(language=data.get('lang')))
            await call.answer()


    async def menu_pay_way(self, call: types.CallbackQuery, state: FSMContext):
        await self.wallet_level3.set()
        async with state.proxy() as data:
            dta = call.data.split('_')
            if dta[0] == 'cash':
                data['cash'] = int(call.data.split('_')[1])
        text = await form.pay_way_form(driver_id=data.get("driver_id"), cash=data.get('cash'), language=data.get('lang'))
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text,
                                        reply_markup=await inline.menu_pay_way(language=data.get('lang')))
            await call.answer()

    async def menu_payme(self, call: types.CallbackQuery, state: FSMContext):
        await self.wallet_level4.set()
        async with state.proxy() as data:
            if call.data == 'Payme':
                data['type'] = call.data
            await pg.wallet_pay(driver_id=call.from_user.id, cash=data["cash"], type_of_payment='Payme', status=False)
            check = GetCheck(amount=data["cash"], driver_id=call.from_user.id)
            await pg.start_order_from_check(check=await check.rec_check_to_database())
        text = await form.payment_form(cash=data.get('cash'), type_payment=data.get('type'), language=data.get('lang'))
        markup = await inline.payme_url(url=await check.return_url(), language=data.get('lang'))
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=text, reply_markup=markup)
            await call.answer()

    async def menu_click(self, call: types.CallbackQuery, state: FSMContext):
        await self.wallet_level4.set()
        async with state.proxy() as data:
            if call.data == 'Click':
                data['type'] = call.data
            await pg.wallet_pay(driver_id=call.from_user.id, cash=data["cash"], type_of_payment="Click", status=False)
            geturl = GetUrl(driver_id=call.from_user.id, amount=data["cash"])
            await pg.add_click_order(order=await geturl.add_order())
        text = await form.payment_form(cash=data.get('cash'), type_payment=data.get('type'), language=data.get('lang'))
        markup = await inline.click_url(language=data.get('lang'), url=await geturl.return_url())
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text,
                                        reply_markup=markup)
            await call.answer()

    async def menu_paynet(self, call: types.CallbackQuery, state: FSMContext):
        await self.wallet_level4.set()
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=Text_lang.quiz.main, reply_markup=await inline.menu_quiz(language=data.get('lang')))
            await call.answer()

    async def menu_quiz(self, call: types.CallbackQuery, state: FSMContext):
        await self.wallet_level3.set()
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
            text = await form.pay_way_form(driver_id=data.get("driver_id"), cash=data.get('cash'),
                                           language=data.get('lang'))
            if await pg.exist_quiz(driver_id=call.from_user.id) is False:
                await pg.add_quiz(driver_id=call.from_user.id)
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text,
                                        reply_markup=await inline.menu_pay_way(language=data.get('lang')))
            await call.answer(text=Text_lang.quiz.thanks, show_alert=True)

    def register_handlers_personal_cabinet(self, dp: Dispatcher):

        # personal data
        dp.register_message_handler(self.menu_personal_data, text=Txt.personal_cabinet.data,                            state=self.personal_cabinet_level1)
        dp.register_callback_query_handler(self.menu_personal_data, lambda x: x.data and x.data.startswith("back"),     state=[self.change_car_level1,
                                                                                                                               self.change_name_level1,
                                                                                                                               self.change_phone_level1])

        dp.register_callback_query_handler(self.menu_new_data, lambda x: x.data and x.data.startswith("change"),        state=self.change_data_level1)

        dp.register_message_handler(self.menu_new_name_rec, content_types="text",                                       state=self.change_name_level1)
        dp.register_callback_query_handler(self.menu_new_car_rec, lambda x: x.data and x.data.startswith("car"),        state=self.change_car_level1)
        dp.register_message_handler(self.menu_new_phone_rec, content_types="text",                                      state=self.change_phone_level1)
        dp.register_message_handler(self.menu_new_phone_rec, content_types="contact",                                   state=self.change_phone_level1)

        # wallet
        dp.register_message_handler(self.menu_wallet, text=Txt.personal_cabinet.wallet,                                 state=self.personal_cabinet_level1)
        dp.register_callback_query_handler(self.menu_wallet, lambda x: x.data and x.data.startswith("walletback"),      state=self.wallet_level2)

        dp.register_callback_query_handler(self.menu_amount, lambda x: x.data and x.data.startswith("balance"),         state=self.wallet_level1)
        dp.register_callback_query_handler(self.menu_amount, lambda x: x.data and x.data.startswith("walletback"),      state=self.wallet_level3)

        dp.register_callback_query_handler(self.menu_pay_way, lambda x: x.data and x.data.startswith("cash"),           state=self.wallet_level2)
        dp.register_callback_query_handler(self.menu_pay_way, lambda x: x.data and x.data.startswith("walletback"),     state=self.wallet_level4)

        dp.register_callback_query_handler(self.menu_payme, text='Payme',                                               state=self.wallet_level3)
        dp.register_callback_query_handler(self.menu_click, text='Click',                                               state=self.wallet_level3)
        dp.register_callback_query_handler(self.menu_paynet, text='Paynet',                                             state=self.wallet_level3)
        dp.register_callback_query_handler(self.menu_quiz, text="quizback",                                             state=self.wallet_level4)
        # dp.register_callback_query_handler(self.menu_pay, lambda x: x.data and x.data.startswith("pay"),                state=self.wallet_level4)







