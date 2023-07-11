import datetime
from contextlib import suppress

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageNotModified, MessageToDeleteNotFound


from config import bot
from keyboards.inline.client.inline_client import InlineClient
from keyboards.inline.driver.inline_driver import InlineDriver
from keyboards.reply.reply_kb import Reply
from pgsql import pg

from text.client.form_client import FormClient
from text.client.form_delivery import FormDelivery
from text.text_func import TextFunc
from text.language.main import Text_main


Txt = Text_main()
func = TextFunc()

reply = Reply()
inline = InlineClient()
inline_driver = InlineDriver()
form_passenger = FormClient()
form_delivery = FormDelivery()

class NewOrderClient(StatesGroup):
    new_order_client = State()

    async def menu_new_order_passenger(self, call: types.CallbackQuery, state: FSMContext):
        print(call.data)
        await state.reset_data()
        await self.unpack(call=call, state=state)
        await state.set_state("Client:client_level9")
        print('2', await state.get_data())
        async with state.proxy() as data:
            with suppress(MessageNotModified):
                await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                            text=await form_passenger.car_text(data=data),
                                            reply_markup=await inline.menu_car(data=data))
        await call.answer()

    async def menu_new_order_delivery(self, call: types.CallbackQuery, state: FSMContext):
        print(call.data)
        await state.reset_data()
        await self.unpack(call=call, state=state)
        async with state.proxy() as data:
            Text_lang = Txt.language[data.get('lang')]
        await state.set_state("Delivery:delivery_level9")
        print('1', await state.get_data())
        with suppress(MessageToDeleteNotFound):
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=call.from_user.id, text=Text_lang.greeting.delivery,
                               reply_markup=await reply.main_menu(language=data.get('lang')))
        await bot.send_message(chat_id=call.from_user.id, text=await form_delivery.order_delivery(data=data),
                               reply_markup=await inline.menu_order(language=data.get('lang')))
        await call.answer()

    async def unpack_call(self, call: types.CallbackQuery, state: FSMContext):
        print(call)
        order_client_id = int(call.data.split('_')[1])
        async with state.proxy() as data:
            data['lang'] = await pg.select_language(user_id=int(call.from_user.id))
            data['client_id'] = int(call.from_user.id)
            data['order_client_id'] = order_client_id

    async def unpack_new_order(self, state: FSMContext):
        async with state.proxy() as data:
            data['phone_client'], data['type'], data['from_region'], data['from_town'], data['to_region'], \
            data['to_town'], date, data['time'], data['num'], data['baggage'], data['trip'], data['cost'],\
                data['route_id'] = await pg.new_order_client(order_client_id=data.get('order_client_id'))
            data['date'] = datetime.date.strftime(date, "%d.%m.%Y")
            car, data['price'] = await pg.new_params(route_id=data['route_id'])
            data['from_region_value'], data["from_town_value"], data['to_region_value'], data["to_town_value"], \
            car = await func.id_to_value(data=data, language=data.get('lang'))

    async def unpack(self, call: types.CallbackQuery, state: FSMContext):
        await self.unpack_call(call=call, state=state)
        await self.unpack_new_order(state=state)

    async def clean(self, state: FSMContext):
        async with state.proxy() as data:
            if data.get('type') == 'passenger':
                await self.clean_passenger(state=state)
            elif data.get('type') == 'delivery':
                await self.clean_delivery(state=state)

    async def clean_passenger(self, state: FSMContext):
        async with state.proxy() as data:
            data.pop('price')
            data.pop('cost')

    async def clean_delivery(self, state: FSMContext):
        async with state.proxy() as data:
            data.pop('car')
            data.pop('car_value')

    def register_handlers_new_order_client(self, dp: Dispatcher):
        dp.register_callback_query_handler(self.menu_new_order_passenger, lambda x: x.data and x.data.startswith("passenger"),  state='*')
        dp.register_callback_query_handler(self.menu_new_order_delivery, lambda x: x.data and x.data.startswith("delivery"),     state="*")