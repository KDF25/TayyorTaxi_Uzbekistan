import datetime
from string import Template
from pgsql import pg

from text.text_func import TextFunc
from text.language.main import Text_main

Txt = Text_main()
func = TextFunc()


class FormActiveOrderClient:

    # active order view
    def __init__(self):
        self.__text = None
        self.__language = None
        self.__order_accept_id = None

    async def order_view(self, order_accept_id: int, language: str):
        self.__language = language
        self.__order_accept_id = order_accept_id
        await self._unpack_view()
        if self.__type == "passenger":
            await self.order_passenger()
        elif self.__type == "delivery":
            await self.order_delivery()
        return self.__text

    async def _unpack_view(self):
        self.__Text_lang = Txt.language[self.__language]
        self.__order_driver_id, self.__driver_id, self.__phone_driver, self.__type, \
        self.__from_region, self.__from_town, self.__to_region, self.__to_town, self.__date, self.__time, self.__places, \
        self.__baggage, self.__trip, self.__car, self.__cond, self.__price, self.__cost = \
            await pg.orderid_to_order_accepted_client(order_accept_id=self.__order_accept_id)
        self.__from_region = await pg.id_to_region(reg_id=self.__from_region, language=self.__language)
        self.__from_town = await pg.id_to_town(reg_id=self.__from_town, language=self.__language)
        self.__to_region = await pg.id_to_region(reg_id=self.__to_region, language=self.__language)
        self.__to_town = await pg.id_to_town(reg_id=self.__to_town, language=self.__language)
        self.__car = await pg.id_to_car(car_id=self.__car)
        self.__date = datetime.date.strftime(self.__date, "%d.%m")
        self.__time = await func.sort_time(time=self.__time)
        self.__package = self.__Text_lang.baggage.package_gab[self.__baggage]
        # self.__price_package = self.__cost - Txt.money.price.trip_price[self.__trip]
        # self.__price_package = await func.num_int_to_str(num=self.__price_package)
        self.__price = await func.num_int_to_str(num=self.__price)
        self.__cost = await func.num_int_to_str(num=self.__cost)
        self.__name = (await pg.select_parametrs_driver(driver_id=self.__driver_id))[0]
        self.__cond = self.__Text_lang.option.option[self.__cond]
        self.__type_order = self.__Text_lang.order.driver.type_order[self.__type]
        self.__places = Txt.places.places_dict[self.__places]

    async def order_passenger(self):
        order = Template("$type\n\n"
                         "🤵‍♂<b>$driver</b>: $driver_name\n"
                         "🚙<b>$car</b>: $driver_car\n"
                         "📱<b>$phone</b>: +$driver_phone\n\n"                         
                         "🔻<b>$client_info</b>🔻\n\n"
                         "🅰️<b>$from_place</b>: $from_region, $from_town\n"
                         "🅱️<b>$to_place</b>: $to_region, $to_town\n\n"
                         "🗓<b>$date</b>: $date_trip\n"
                         "⏰<b>$time</b>: $time_trip\n\n"
                         "💵$cost1 $client_places $cost2 - <b>$final_cost</b> $sum"
                         "$trip")
        self.__text = order.substitute(type=self.__type_order, client_info=self.__Text_lang.chain.passenger.info,
                                       driver=self.__Text_lang.chain.passenger.driver, driver_name=self.__name,
                                       car=self.__Text_lang.chain.passenger.car, driver_car=self.__car,
                                       phone=self.__Text_lang.chain.passenger.phone, driver_phone=self.__phone_driver,
                                       date=self.__Text_lang.chain.passenger.date, date_trip=self.__date,
                                       time=self.__Text_lang.chain.passenger.time, time_trip=self.__time,
                                       places=self.__Text_lang.chain.passenger.num, client_places=self.__places,
                                       from_place=self.__Text_lang.chain.passenger.from_place,
                                       from_region=self.__from_region, from_town=self.__from_town,
                                       to_place=self.__Text_lang.chain.passenger.to_place,
                                       to_region=self.__to_region, to_town=self.__to_town,
                                       cost1=self.__Text_lang.chain.passenger.cost1,
                                       cost2=self.__Text_lang.chain.passenger.cost2,
                                       final_cost=self.__cost, sum=self.__Text_lang.symbol.sum,
                                       trip=self.__Text_lang.chain.passenger.trip)

    async def order_delivery(self):
        order = Template("$type\n\n"
                         "🤵‍♂<b>$driver</b>: $driver_name\n"
                         "🚙<b>$car</b>: $driver_car\n"
                         "📱<b>$phone</b>: +$driver_phone\n\n"
                         "🔻<b>$client_info</b>🔻\n\n"
                         "🅰️<b>$from_place</b>: $from_region, $from_town\n"
                         "🅱️<b>$to_place</b>: $to_region, $to_town\n\n"
                         "🗓<b>$date</b>: $date_trip\n"
                         "⏰<b>$time</b>: $time_trip\n"
                         "🧰<b>$baggage</b>: $client_baggage\n\n"
                         "💵$cost - <b>$final_cost</b> $sum\n"
                         "$trip\n\n")
        self.__text = order.substitute(type=self.__type_order, client_info=self.__Text_lang.chain.delivery.info,
                                       driver=self.__Text_lang.chain.delivery.driver, driver_name=self.__name,
                                       car=self.__Text_lang.chain.delivery.car, driver_car=self.__car,
                                       phone=self.__Text_lang.chain.delivery.phone, driver_phone=self.__phone_driver,
                                       date=self.__Text_lang.chain.delivery.date, date_trip=self.__date,
                                       time=self.__Text_lang.chain.delivery.time, time_trip=self.__time,
                                       baggage=self.__Text_lang.chain.delivery.baggage, client_baggage=self.__package,
                                       from_place=self.__Text_lang.chain.delivery.from_place,
                                       from_region=self.__from_region, from_town=self.__from_town,
                                       to_place=self.__Text_lang.chain.delivery.to_place,
                                       to_region=self.__to_region, to_town=self.__to_town,
                                       cost=self.__Text_lang.chain.delivery.cost, final_cost=self.__cost,
                                       sum=self.__Text_lang.symbol.sum, trip=self.__Text_lang.chain.delivery.trip)

    async def order_cancel(self, order_accept_id: int, language: str):
        self.__language = language
        self.__order_accept_id = order_accept_id
        await self._unpack_cancel()
        if self.__type == "passenger":
            await self.cancel_passenger()
        elif self.__type == "delivery":
            await self.cancel_delivery()
        return self.__text

    async def _unpack_cancel(self):
        self.__Text_lang = Txt.language[self.__language]
        self.__order_driver_id, self.__driver_id, self.__phone_driver, self.__type, \
        self.__from_region, self.__from_town, self.__to_region, self.__to_town, self.__date, self.__time, self.__places, \
        self.__baggage, self.__trip, self.__car, self.__cond, self.__price, self.__cost = \
            await pg.orderid_to_order_accepted_client(order_accept_id=self.__order_accept_id)
        self.__from_region = await pg.id_to_region(reg_id=self.__from_region, language=self.__language)
        self.__from_town = await pg.id_to_town(reg_id=self.__from_town, language=self.__language)
        self.__to_region = await pg.id_to_region(reg_id=self.__to_region, language=self.__language)
        self.__to_town = await pg.id_to_town(reg_id=self.__to_town, language=self.__language)
        self.__date = datetime.date.strftime(self.__date, "%d.%m")
        self.__time = await func.sort_time(time=self.__time)
        self.__price = await func.num_int_to_str(num=self.__price)
        self.__cost = await func.num_int_to_str(num=self.__cost)
        self.__package = self.__Text_lang.baggage.package_gab[self.__baggage]
        self.__places = Txt.places.places_dict[self.__places]
        # await self._places()

    async def cancel_passenger(self):
        order = Template("$order\n\n"
                         "🔻<b>$client_info</b>🔻\n\n"
                         "🅰️<b>$from_place</b>: $from_region, $from_town\n"
                         "🅱️<b>$to_place</b>: $to_region, $to_town\n\n"
                         "🗓<b>$date</b>: $date_trip\n"
                         "⏰<b>$time</b>: $time_trip\n\n"
                         "💵$cost1 $client_places $cost2 - <b>$final_cost</b> $sum\n"
                         "$trip")
        self.__text = order.substitute(order=self.__Text_lang.cancel.driver.passenger,
                                       client_info=self.__Text_lang.order.driver.info,
                                       date=self.__Text_lang.chain.driver.date, date_trip=self.__date,
                                       time=self.__Text_lang.chain.passenger.time, time_trip=self.__time,
                                       from_place=self.__Text_lang.chain.driver.from_place,
                                       from_region=self.__from_region, from_town=self.__from_town,
                                       to_place=self.__Text_lang.chain.driver.to_place,
                                       to_region=self.__to_region, to_town=self.__to_town,
                                       cost1=self.__Text_lang.chain.passenger.cost1, client_places=self.__places,
                                       cost2=self.__Text_lang.chain.passenger.cost2,
                                       final_cost=self.__cost, sum=self.__Text_lang.symbol.sum,
                                       trip=self.__Text_lang.chain.passenger.trip)

    async def cancel_delivery(self):
        order = Template("$order\n\n"
                         "🔻<b>$client_info</b>🔻\n\n"
                         "🅰️<b>$from_place</b>: $from_region, $from_town\n"
                         "🅱️<b>$to_place</b>: $to_region, $to_town\n\n"
                         "🗓<b>$date</b>: $date_trip\n"
                         "⏰<b>$time</b>: $time_trip\n"
                         "🧰<b>$baggage</b>: $baggage_client\n\n"
                         "💵$cost - <b>$final_cost</b> $sum\n"
                         "$trip\n\n")
        self.__text = order.substitute(order=self.__Text_lang.cancel.driver.passenger,
                                       client_info=self.__Text_lang.order.driver.info,
                                       date=self.__Text_lang.chain.delivery.date, date_trip=self.__date,
                                       time=self.__Text_lang.chain.delivery.time, time_trip=self.__time,
                                       baggage=self.__Text_lang.chain.delivery.baggage, baggage_client=self.__package,
                                       from_place=self.__Text_lang.chain.driver.from_place,
                                       from_region=self.__from_region, from_town=self.__from_town,
                                       to_place=self.__Text_lang.chain.driver.to_place,
                                       to_region=self.__to_region, to_town=self.__to_town,
                                       cost=self.__Text_lang.chain.delivery.cost, final_cost=self.__cost,
                                       sum=self.__Text_lang.symbol.sum, trip=self.__Text_lang.chain.delivery.trip)
