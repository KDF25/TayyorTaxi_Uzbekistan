import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from pgsql import pg

from text.text_func import TextFunc
from text.language.main import Text_main
from datetime_now.datetime_now import dt_now

func = TextFunc()
Txt = Text_main()


class InlineClient:
    def __init__(self):
        self.__markup = None
        self.__data = None
        self.__order = None
        self.__index = None

    async def choose_language(self):
        markup = InlineKeyboardMarkup(row_width=3)
        b_rus = InlineKeyboardButton(text=Txt.settings.rus, callback_data='rus')
        b_uzb = InlineKeyboardButton(text=Txt.settings.uzb, callback_data='uzb')
        b_ozb = InlineKeyboardButton(text=Txt.settings.ozb, callback_data='ozb')
        markup.row(b_ozb, b_rus, b_uzb)
        return markup

    async def menu_route(self, language: str):
        markup = InlineKeyboardMarkup(row_width=1)
        Text_lang = Txt.language[language]
        b1 = InlineKeyboardButton(text=Text_lang.buttons.common.out_region, callback_data="out")
        b2 = InlineKeyboardButton(text=Text_lang.buttons.common.in_region, callback_data="in")
        markup.add(b1, b2)
        return markup

    async def menu_region(self, language: str, from_region=None, back=True):
        markup = InlineKeyboardMarkup(row_width=2)
        Text_lang = Txt.language[language]
        for button in (await pg.id_and_region(language=language)):
            if button[0] != from_region:
                b_region = InlineKeyboardButton(text=button[1], callback_data=f"region_{button[0]}")
                markup.insert(b_region)
        if back is True:
            back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data=f"back")
            markup.add(back)
        return markup

    async def menu_town(self, reg_id: int, language: str):
        markup = InlineKeyboardMarkup(row_width=2)
        Text_lang = Txt.language[language]
        for button in (await pg.reg_id_to_towns(reg_id=reg_id, language=language)):
            b_region = InlineKeyboardButton(text=button[1], callback_data=f"town_{button[0]}")
            markup.insert(b_region)
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data=f"back")
        markup.add(back)
        return markup

    async def menu_town_exist(self, reg_id: int, language: str, towns: dict):
        markup = InlineKeyboardMarkup(row_width=2)
        Text_lang = Txt.language[language]
        for button in (await pg.reg_id_to_towns(reg_id=reg_id, language=language)):
            if button[0] in towns.keys():
                b_region = InlineKeyboardButton(text=f"{button[1]}({towns[button[0]]})", callback_data=f"town_{button[0]}")
            else:
                b_region = InlineKeyboardButton(text=f"{button[1]}(0)", callback_data=f"zeroTown")
            markup.insert(b_region)
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data=f"back")
        markup.add(back)
        return markup

    async def _append_parameters(self, parameter, parameters):
        if type(parameter) == datetime.date and parameter == parameters:
            parameter = str(datetime.date.strftime(parameter, "%d.%m"))
            return "✅ " + parameter
        if type(parameter) == datetime.date and parameter != parameters:
            parameter = str(datetime.date.strftime(parameter, "%d.%m"))
            return parameter
        elif type(parameter) == str and parameter in parameters:
            return "✅ " + parameter
        else:
            return parameter

    async def _append_parameter(self, parameter, parameters, value):
        if parameter == parameters:
            return "✅ " + value[parameter]
        else:
            return value[parameter]

    async def _change_date(self, new_date: str, date: str):
        new_date = new_date[0:5]
        date = date[0:5]
        if new_date == date:
            return "✅ " + new_date
        else:
            return new_date

    async def _date(self):
        for i in range(0, 3):
            j = 0 if dt_now.now().hour < 21 else 1
            date = (dt_now.now().date() + datetime.timedelta(days=i+j))
            date = datetime.date.strftime(date, "%d.%m.%Y")
            b_date = InlineKeyboardButton(text=date, callback_data=f"date_{date}")
            self.__markup.insert(b_date)

    async def _time(self, time: list):
        for i in range(0, 24, 3):
            Time = str(f"{i}:00 - {i + 3}:00")
            b_time = InlineKeyboardButton(text=await self._append_parameters(parameter=Time, parameters=time),
                                          callback_data=f"time_{Time}")
            self.__markup.insert(b_time)

    async def _datetime(self, type_app: str, language: str):
        Text_lang = Txt.language[language]
        if type_app == 'passenger':
            b_date = InlineKeyboardButton(text=Text_lang.buttons.passenger.date, callback_data="void")
            b_time = InlineKeyboardButton(text=Text_lang.buttons.passenger.time, callback_data="void")
        else:
            b_date = InlineKeyboardButton(text=Text_lang.buttons.delivery.date, callback_data="void")
            b_time = InlineKeyboardButton(text=Text_lang.buttons.delivery.time, callback_data="void")
        return b_date, b_time

    async def menu_date(self, language: str):
        self.__markup = InlineKeyboardMarkup(row_width=3)
        Text_lang = Txt.language[language]
        await self._date()
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data=f"back")
        self.__markup.add(back)
        return self.__markup

    async def menu_time(self, time: list, language: str):
        self.__markup = InlineKeyboardMarkup(row_width=2)
        Text_lang = Txt.language[language]
        await self._time(time=time)
        cont = InlineKeyboardButton(text=Text_lang.buttons.common.cont, callback_data=f"continue")
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data=f"back")
        self.__markup.add(cont).add(back)
        return self.__markup

    async def _num(self):
        Buttons = []
        for i, place in enumerate(Txt.places.places):
            b_num = InlineKeyboardButton(text=place, callback_data=f"num_{i+1}")
            Buttons.append(b_num)
        return Buttons

    async def _baggage(self, baggage: int, language: str):
        Buttons = []
        Text_lang = Txt.language[language]
        for i in range(0, 5):
            text = await self._append_parameter(parameter=i, parameters=baggage, value=Text_lang.baggage.baggage_gab)
            b_baggage = InlineKeyboardButton(text=text, callback_data=f"baggage_{i}")
            Buttons.append(b_baggage)
        return Buttons

    async def menu_number(self, language: str):
        markup = InlineKeyboardMarkup(row_width=2)
        Text_lang = Txt.language[language]
        Num = await self._num()
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data=f"back")
        markup.row(*Num)
        markup.add(back)
        return markup

    async def _package(self, language: str):
        Text_lang = Txt.language[language]
        for i in range(0, 5):
            text = Text_lang.baggage.package_gab[i]
            b_baggage = InlineKeyboardButton(text=text, callback_data=f"baggage_{i}")
            self.__markup.insert(b_baggage)

    async def menu_package(self, language: str):
        self.__markup = InlineKeyboardMarkup(row_width=2)
        Text_lang = Txt.language[language]
        await self._package(language=language)
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data=f"back")
        self.__markup.add(back)
        return self.__markup

    async def menu_share_phone(self, language: str):
        markup = InlineKeyboardMarkup(row_width=1)
        Text_lang = Txt.language[language]
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data=f"back")
        markup.add(back)
        return markup

    async def menu_car(self, data: dict):
        markup = InlineKeyboardMarkup(row_width=2)
        Text_lang = Txt.language[data.get('lang')]
        self.__data = data
        await self._model()
        for car in self.__model:
            text_car = await pg.id_to_car(car[0])
            b_car = InlineKeyboardButton(text=f"{text_car} ({car[1]})", callback_data=f"car_{car[0]}")
            markup.insert(b_car)
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data="back")
        markup.add(back)
        return markup

    async def _model(self):
        self.__model = await pg.select_distinct_car(from_region=self.__data.get("from_region"),
                                                    to_region=self.__data.get("to_region"),
                                                    from_town=self.__data.get("from_town"),
                                                    to_town=self.__data.get("to_town"),
                                                    places=self.__data.get('num'), date=self.__data.get('date'),
                                                    client_id=self.__data.get('client_id'), times=self.__data['time'])
        await self._analise()
    #     потом можно удалить анализ

    async def _analise(self):
        if len(self.__model) == 0:
            await pg.update_model(id=self.__data.get('analise_id'), car=0)

    async def menu_distinct_car(self, data: dict):
        Text_lang = Txt.language[data.get('lang')]
        markup = InlineKeyboardMarkup(row_width=1)
        self.__data = data
        await self._distinct_cars()
        for self.__index, self.__order in enumerate(self.__distinct_cars):
            await self._distinct_cars_text()
            b_order = InlineKeyboardButton(text=self.__text, callback_data=f"order_{self.__order[0]}")
            markup.insert(b_order)
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data="back")
        markup.add(back)
        return markup

    async def _distinct_cars(self):
        self.__distinct_cars = await pg.select_parametrs(from_region=self.__data.get("from_region"),
                                                         to_region=self.__data.get("to_region"),
                                                         from_town=self.__data.get("from_town"),
                                                         to_town=self.__data.get("to_town"),
                                                         places=self.__data.get('num'), date=self.__data.get("date"),
                                                         times=self.__data['time'],
                                                         client_id=self.__data.get('client_id'),
                                                         car=self.__data.get('car'))

    async def _distinct_cars_text(self):
        price = self.__data['num'] * self.__order[1]
        price = await func.num_int_to_str(num=price)
        if self.__data.get("from_region") == self.__data.get("to_region"):
            cond = str('| ❄') if self.__order[2] == 1 else ""
            self.__text = f"№ {self.__index + 1} | 💵{price} {cond}"
        else:
            cond = str('❄ | ') if self.__order[2] == 1 else ""
            self.__text = f"№ {self.__index + 1} | 💵{price} | {cond}💺{self.__order[3]}"

    async def menu_order(self, language: str):
        Text_lang = Txt.language[language]
        markup = InlineKeyboardMarkup(row_width=2)
        Common = Text_lang.buttons.common
        b = InlineKeyboardButton(text=Common.order, callback_data="book")
        back = InlineKeyboardButton(text=Common.back, callback_data="back")
        markup.add(b).add(back)
        return markup

    async def menu_choose_more(self, language: str):
        Text_lang = Txt.language[language]
        markup = InlineKeyboardMarkup(row_width=1)
        b = InlineKeyboardButton(text=Text_lang.buttons.passenger.choose_more, callback_data=f"back")
        markup.add(b)
        return markup

    async def menu_accept_order(self, order_client_id: int, language: str):
        Text_lang = Txt.language[language]
        markup = InlineKeyboardMarkup(row_width=2)
        Driver = Text_lang.buttons.driver
        b1 = InlineKeyboardButton(text=Driver.accept, callback_data=f"accept_{order_client_id}")
        b2 = InlineKeyboardButton(text=Driver.reject, callback_data=f"reject_{order_client_id}")
        markup.add(b1).add(b2)
        return markup

    async def menu_cancel(self, order_accept_id: int, language: str):
        markup = InlineKeyboardMarkup(row_width=1)
        Text_lang = Txt.language[language]
        b = InlineKeyboardButton(text=Text_lang.buttons.cancel.client, callback_data=f"cancel_{order_accept_id}")
        markup.add(b)
        return markup

    async def menu_delete(self, language: str, order_accept_id: int):
        markup = InlineKeyboardMarkup(row_width=2)
        Text_lang = Txt.language[language]
        b1 = InlineKeyboardButton(text=Text_lang.buttons.common.no, callback_data=f"no_{order_accept_id}")
        b2 = InlineKeyboardButton(text=Text_lang.buttons.common.da, callback_data=f"yes")
        markup.add(b1, b2)
        return markup