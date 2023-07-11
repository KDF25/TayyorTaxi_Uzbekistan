import datetime
from string import Template
from pgsql import pg

from text.text_func import TextFunc
from text.language.main import Text_main

Txt = Text_main()
func = TextFunc()


class FormDriver:
    def __init__(self):
        self.__Delivery = None
        self.__route_id = None
        self.__language = None
        self.__driver_id = None
        self.__Text_lang = None
        self.__data = None
        self.__text = None
        self.__from_town = ""
        self.__to_town = ""

    async def main_text(self, data: dict, question: str):
        Text_lang = Txt.language[data.get('lang')]
        form = Text_lang.chain.driver
        question_text1 = ''
        question_text2 = ''
        if data.get("from_region", None) is not None:
            from_region = data.get("from_region_value")
            from_town = str(', '.join(i for i in data.get("from_towns_value")))
            if data.get("to_region", None) is not None:
                to_region = data.get("to_region_value")
                to_town = str(', '.join(i for i in data.get("to_towns_value")))
                question_text2 = f'🅱️ <b>{form.to_place}</b>: {to_region} ({to_town})\n'
            question_text1 = f'🅰️ <b>{form.from_place}</b>: {from_region} ({from_town})\n'

        question_text = f"{question_text1}" \
                        f"{question_text2}" \
                        f"\n{question}"
        return question_text

    async def menu_active_route(self, language: str, driver_id: int):
        self.__language = language
        Text_lang = Txt.language[language]
        mainText = Text_lang.chain.driver.allRoute
        for route in (await pg.all_route_driver(driver_id=driver_id)):
            await self._route_text(route=route)
            price = await func.num_int_to_str(num=route[5])
            mainText += f"\n\n<b>{self.__text}</b>\n" \
                        f"{Text_lang.chain.driver.price2} – <b>{price}</b> {Text_lang.symbol.sum}"
        return mainText

    async def _route_text(self, route: list):
        if route[1] != route[3]:
            self.__text = await pg.id_to_region(reg_id=route[1], language=self.__language)
            self.__text += f" - {await pg.id_to_region(reg_id=route[3], language=self.__language)}"
        else:
            self.__text = await pg.id_to_town(reg_id=route[2][0], language=self.__language)
            self.__text += f" - {await pg.id_to_town(reg_id=route[4][0], language=self.__language)}"
            self.__text += f" - {await pg.id_to_town(reg_id=route[2][0], language=self.__language)}"

    async def route_cancel(self, language: str, route_id: int):
        self.__language = language
        self.__route_id = route_id
        self.__Text_lang = Txt.language[self.__language]
        await self._region_or_town()
        text = Template("<b>$route:</b>\n"
                        "$way\n\n"
                        "$onepass - <b>$price1</b> $sum")
        text = text.substitute(route=self.__Text_lang.chain.driver.route, way=self.__way,
                               onepass=self.__Text_lang.chain.driver.price2, price1=self.__price,
                               sum=self.__Text_lang.symbol.sum)
        return text

    async def _region_or_town(self):
        self.__from_region, self.__from_towns, self.__to_region, self.__to_towns, self.__price = \
            await pg.route_id_to_route(route_id=self.__route_id)
        self.__price = await func.num_int_to_str(num=self.__price)
        if self.__from_region != self.__to_region:
            self.__from_region = await pg.id_to_region(reg_id=self.__from_region, language=self.__language)
            self.__to_region = await pg.id_to_region(reg_id=self.__to_region, language=self.__language)
            self.__from_town = [await pg.id_to_town(reg_id=i, language=self.__language) for i in self.__from_towns]
            self.__from_town = (', '.join(i for i in self.__from_town))
            self.__to_town = [await pg.id_to_town(reg_id=i, language=self.__language) for i in self.__to_towns]
            self.__to_town = (', '.join(i for i in self.__to_town))
            self.__way = Template("🅰️ <b>$from_place</b>: $from_region ($from_town)\n"
                                  "🅱️ <b>$to_place</b>: $to_region ($to_town)")
            self.__way = self.__way.substitute(from_place=self.__Text_lang.chain.passenger.from_place,
                                               from_region=self.__from_region, from_town=self.__from_town,
                                               to_place=self.__Text_lang.chain.passenger.to_place,
                                               to_region=self.__to_region, to_town=self.__to_town)
        else:
            self.__way1 = await pg.id_to_town(reg_id=self.__from_towns[0], language=self.__language)
            self.__way2 = await pg.id_to_town(reg_id=self.__to_towns[0], language=self.__language)
            self.__way = Template("$way1 - $way2 - $way1")
            self.__way = self.__way.substitute(way1=self.__way1, way2=self.__way2)

    async def menu_towns(self, language: str, region: str):
        Text_lang = Txt.language[language]
        text = Template("<b>$region</b>\n\n"
                        "$question")
        text = text.substitute(region=region, question=Text_lang.questions.driver.towns)
        return text

    async def menu_cond(self, language: str, towns: list):
        Text_lang = Txt.language[language]
        text = Template("<b>$route:</b>\n"
                        "$town1-$town2-$town1\n\n"
                        "$question")
        text = text.substitute(route=Text_lang.chain.driver.route, town1=towns[0],
                               town2=towns[1], question=Text_lang.questions.driver.cond)
        return text

    async def order_between_regions(self, data: dict):
        self.__data = data
        self.__Text_lang = Txt.language[self.__data.get('lang')]
        Driver = self.__Text_lang.chain.driver
        Cond = self.__Text_lang.option.option[self.__data.get("cond")]
        await self._unpack_between_regions()
        text = Template("🤵‍♂ <b>$name</b>: $driver_name\n"
                        "📱 <b>$phone</b>: +$phone_driver\n"
                        "🚙 <b>$car</b>: $driver_car\n\n"
                        "<b>$route:</b>\n"
                        "🅰️ <b>$from_place</b>: $from_region, ($from_town)\n"
                        "🅱️ <b>$to_place</b>: $to_region, ($to_town)\n\n"
                        "<b>$conditioner</b>: $driver_conditioner\n\n"
                        "$onepass - <b>$price</b> $sum\n\n"
                        "$alright")
        text = text.substitute(name=Driver.name, driver_name=data.get("name"),
                               phone=Driver.phone, phone_driver=data.get("phone_driver"),
                               car=Driver.car, driver_car=data.get("car_value"), route=Driver.route,
                               from_place=self.__Text_lang.chain.passenger.from_place,
                               from_region=self.__from_region, from_town=self.__from_town,
                               to_place=self.__Text_lang.chain.passenger.to_place,
                               to_region=self.__to_region, to_town=self.__to_town,
                               conditioner=Driver.conditioner, driver_conditioner=Cond,
                               onepass=self.__Text_lang.chain.driver.price2, price=self.__price,
                               sum=self.__Text_lang.symbol.sum, alright=Driver.alright)
        return text

    async def _unpack_between_regions(self):
        self.__from_region = self.__data.get("from_region_value")
        self.__from_town = str(', '.join(i for i in self.__data.get("from_towns_value")))
        self.__to_region = self.__data.get("to_region_value")
        self.__to_town = str(', '.join(i for i in self.__data.get("to_towns_value")))
        self.__price = await func.num_int_to_str(num=self.__data.get("price"))

    async def order_between_towns(self, data: dict):
        self.__data = data
        self.__Text_lang = Txt.language[self.__data.get('lang')]
        Driver = self.__Text_lang.chain.driver
        Cond = self.__Text_lang.option.option[self.__data.get("cond")]
        await self._unpack_between_towns()
        text = Template("🤵‍♂ <b>$name</b>: $driver_name\n"
                        "📱 <b>$phone</b>: +$phone_driver\n"
                        "🚙 <b>$car</b>: $driver_car\n\n"
                        "<b>$route:</b>\n"
                        "$town1-$town2-$town1\n\n"
                        "<b>$conditioner</b>: $driver_conditioner\n\n"
                        "$onepass - <b>$price</b> $sum\n\n"
                        "$alright")
        text = text.substitute(name=Driver.name, driver_name=data.get("name"),
                               phone=Driver.phone, phone_driver=data.get("phone_driver"),
                               car=Driver.car, driver_car=data.get("car_value"), route=Driver.route,
                               town1=self.__towns[0], town2=self.__towns[1],
                               conditioner=Driver.conditioner, driver_conditioner=Cond,
                               onepass=self.__Text_lang.chain.driver.price2, price=self.__price,
                               sum=self.__Text_lang.symbol.sum, alright=Driver.alright)
        return text

    async def _unpack_between_towns(self):
        self.__towns = self.__data.get("towns_value")
        self.__price = await func.num_int_to_str(num=self.__data.get("price"))

    async def new_order_driver(self, data: dict):
        self.__data = data
        if self.__data.get('type') == 'passenger':
            await self.driver_passenger()
        elif self.__data.get('type') == "delivery":
            await self.driver_delivery()
        return self.__text

    async def driver_passenger(self):
        await self._upack_for_driver()
        text = Template("$accept_order\n\n"
                        "🔻 <b>$client_info</b> 🔻\n\n"
                        "📱 <b>$phone</b>: +$phone_client\n"
                        "🅰️ <b>$from_place</b>: $from_region, $from_town\n"
                        "🅱️ <b>$to_place</b>: $to_region, $to_town\n\n"
                        "🗓 <b>$date</b>: $date_trip\n"
                        "⏰ <b>$time</b>: $time_trip\n\n"
                        "💵$cost1 $client_places $cost2 - <b>$final_cost</b> $sum\n"
                        "$trip\n\n"
                        "⚠️$active_orders")
        self.__text = text.substitute(accept_order=self.__Text_lang.order.driver.accept,
                                      client_info=self.__Text_lang.order.driver.info,
                                      phone=self.__Text_lang.chain.passenger.phone, phone_client=self.__phone_client,
                                      from_place=self.__Text_lang.chain.passenger.from_place,
                                      from_region=self.__from_region, from_town=self.__from_town,
                                      to_place=self.__Text_lang.chain.passenger.to_place,
                                      to_region=self.__to_region, to_town=self.__to_town,
                                      date=self.__Text_lang.chain.passenger.date, date_trip=self.__date,
                                      time=self.__Text_lang.chain.passenger.time, time_trip=self.__time,
                                      place=self.__Text_lang.chain.passenger.num, place_client=self.__places,
                                      cost1=self.__Text_lang.chain.passenger.cost1, client_places=self.__places,
                                      cost2=self.__Text_lang.chain.passenger.cost2,
                                      final_cost=self.__cost, sum=self.__Text_lang.symbol.sum,
                                      trip=self.__Text_lang.chain.passenger.trip,
                                      active_orders=self.__Text_lang.order.active_orders)

    async def driver_delivery(self):
        await self._upack_for_driver()
        text = Template("$accept_order\n\n"
                        "🔻 <b>$client_info</b> 🔻\n\n"
                        "📱 <b>$phone</b>: +$phone_client\n"
                        "🅰️ <b>$from_place</b>: $from_region, $from_town\n"
                        "🅱️ <b>$to_place</b>: $to_region, $to_town\n\n"
                        "🗓 <b>$date</b>: $date_trip\n"
                        "⏰ <b>$time</b>: $time_trip\n"
                        "🧰 <b>$baggage</b>: $baggage_client\n\n"
                        "💵 $cost - <b>$cost_final $sum</b>\n"
                        "$trip\n\n"
                        "⚠️$active_orders")
        self.__text = text.substitute(accept_order=self.__Text_lang.order.driver.accept,
                                      client_info=self.__Text_lang.order.driver.info,
                                      phone=self.__Text_lang.chain.delivery.phone, phone_client=self.__phone_client,
                                      from_place=self.__Text_lang.chain.delivery.from_place,
                                      from_region=self.__from_region, from_town=self.__from_town,
                                      to_place=self.__Text_lang.chain.delivery.to_place,
                                      to_region=self.__to_region, to_town=self.__to_town,
                                      date=self.__Text_lang.chain.delivery.date, date_trip=self.__date,
                                      time=self.__Text_lang.chain.delivery.time, time_trip=self.__time,
                                      baggage=self.__Text_lang.chain.delivery.baggage, baggage_client=self.__package,
                                      trip=self.__Text_lang.chain.delivery.trip, cost=self.__Text_lang.chain.driver.cost,
                                      sum=self.__Text_lang.symbol.sum,
                                      cost_final=self.__cost, active_orders=self.__Text_lang.order.active_orders)

    async def _upack_for_driver(self):
        self.__Text_lang = Txt.language[self.__data.get("lang_client")]
        self.__from_region, self.__from_town, self.__to_region, self.__to_town, self.__car = \
            await func.id_to_value(data=self.__data, language=self.__data.get('lang_client'))
        self.__package = self.__Text_lang.baggage.package_gab[self.__data.get('baggage')]
        self.__phone_client = self.__data.get("phone_client")
        self.__date = datetime.date.strftime(self.__data.get("date"), "%d.%m")
        self.__time = await func.sort_time(time=self.__data.get("time"))
        self.__places = self.__data.get("num")
        self.__cost = await func.num_int_to_str(num=self.__data.get("cost"))
        self.__places = Txt.places.places_dict[self.__places]

    async def new_order_client(self, data: dict):
        self.__data = data
        if self.__data.get('type') == 'passenger':
            await self.client_passenger()
        elif self.__data.get('type') == "delivery":
            await self.client_delivery()
        return self.__text

    async def client_passenger(self):
        await self._upack_for_client()
        text = Template("$accept\n\n"
                        "🤵‍♂ <b>$name</b>: $driver_name\n"
                        "📱 <b>$phone</b>: +$driver_phone\n"
                        "🚙 <b>$car</b>: $driver_car\n\n"
                        "🔻 <b>$client_info</b> 🔻\n\n"
                        "📱 <b>$phone</b>: +$client_phone\n"
                        "🅰️ <b>$from_place</b>: $from_region, $from_town\n"
                        "🅱️ <b>$to_place</b>: $to_region, $to_town\n\n"
                        "🗓 <b>$date</b>: $date_trip\n"
                        "⏰ <b>$time</b>: $time_trip\n\n"
                        "💵$cost1 $client_places $cost2 - <b>$final_cost</b> $sum\n"
                        "$trip\n\n"
                        "⚠️$active_orders")
        self.__text = text.substitute(accept=self.__Text_lang.order.client.accept,
                                      name=self.__Text_lang.chain.passenger.driver, driver_name=self.__name,
                                      car=self.__Text_lang.chain.passenger.car, driver_car=self.__car,
                                      client_info=self.__Text_lang.chain.passenger.info,
                                      phone=self.__Text_lang.chain.passenger.phone, client_phone=self.__phone_client,
                                      driver_phone=self.__phone_driver,
                                      from_place=self.__Text_lang.chain.passenger.from_place,
                                      from_region=self.__from_region, from_town=self.__from_town,
                                      to_place=self.__Text_lang.chain.passenger.to_place,
                                      to_region=self.__to_region, to_town=self.__to_town,
                                      date=self.__Text_lang.chain.passenger.date, date_trip=self.__date,
                                      time=self.__Text_lang.chain.passenger.time, time_trip=self.__time,
                                      cost1=self.__Text_lang.chain.passenger.cost1, client_places=self.__places,
                                      cost2=self.__Text_lang.chain.passenger.cost2, final_cost=self.__cost,
                                      sum=self.__Text_lang.symbol.sum, trip=self.__Text_lang.chain.passenger.trip,
                                      active_orders=self.__Text_lang.order.active_orders)

    async def client_delivery(self):
        await self._upack_for_client()
        text = Template("$accept\n\n"
                        "🤵‍♂ <b>$name</b>: $driver_name\n"
                        "📱 <b>$phone</b>: +$driver_phone\n"
                        "🚙 <b>$car</b>: $driver_car\n\n"
                        "🔻 <b>$client_info</b>🔻\n\n"
                        "📱 <b>$phone</b>: +$client_phone\n"
                        "🅰️ <b>$from_place</b>: $from_region, $from_town\n"
                        "🅱️ <b>$to_place</b>: $to_region, $to_town\n\n"
                        "🗓 <b>$date</b>: $date_trip\n"
                        "⏰ <b>$time</b>: $time_trip\n"
                        "🧰 <b>$baggage</b>: $baggage_client\n\n"
                        "💵 $cost — <b>$cost_final</b> $sum\n"
                        "$trip\n\n"
                        "⚠️$active_orders")
        self.__text = text.substitute(accept=self.__Text_lang.order.client.accept,
                                      name=self.__Text_lang.chain.delivery.driver, driver_name=self.__name,
                                      car=self.__Text_lang.chain.delivery.car, driver_car=self.__car,
                                      driver_phone=self.__phone_driver,
                                      client_info=self.__Text_lang.chain.delivery.info,
                                      phone=self.__Text_lang.chain.delivery.phone, client_phone=self.__phone_client,
                                      from_place=self.__Text_lang.chain.delivery.from_place,
                                      from_region=self.__from_region, from_town=self.__from_town,
                                      to_place=self.__Text_lang.chain.delivery.to_place,
                                      to_region=self.__to_region, to_town=self.__to_town,
                                      date=self.__Text_lang.chain.delivery.date, date_trip=self.__date,
                                      time=self.__Text_lang.chain.delivery.time, time_trip=self.__time,
                                      baggage=self.__Text_lang.chain.delivery.baggage, baggage_client=self.__package,
                                      trip=self.__Text_lang.chain.delivery.trip,
                                      cost=self.__Text_lang.chain.delivery.cost, sum=self.__Text_lang.symbol.sum,
                                      cost_final=self.__cost, active_orders=self.__Text_lang.order.active_orders)

    async def _upack_for_client(self):
        self.__Text_lang = Txt.language[self.__data.get("lang_client")]
        self.__from_region, self.__from_town, self.__to_region, self.__to_town, self.__car = \
            await func.id_to_value(data=self.__data, language=self.__data.get('lang_client'))
        self.__package = self.__Text_lang.baggage.package_gab[self.__data.get('baggage')]
        self.__cond = self.__Text_lang.option.option[self.__data.get("cond")]
        self.__phone_client = self.__data.get("phone_client")
        self.__name = self.__data.get("name")
        self.__phone_driver = self.__data.get("phone_driver")
        self.__date = datetime.date.strftime(self.__data.get("date"), "%d.%m")
        self.__time = await func.sort_time(time=self.__data.get("time"))
        self.__places = self.__data.get("num")
        self.__cost = await func.num_int_to_str(num=self.__data.get("cost"))
        self.__places = Txt.places.places_dict[self.__places]

