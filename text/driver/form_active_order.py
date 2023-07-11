import datetime
from string import Template
from pgsql import pg

from text.text_func import TextFunc
from text.language.main import Text_main

Txt = Text_main()
func = TextFunc()


class FormActiveOrderDriver:
    def __init__(self):
        self.__text = None
        self.__language = None
        self.__order_accept_id = None

    async def car_full(self, date: datetime, time: list, language: str):
        Text_lang = Txt.language[language]
        Order = Text_lang.active_order.client
        Passenger = Text_lang.chain.passenger
        text_order = Template("$car_full\n"
                              "$driver_call\n\n"
                              "🗓 <b>$date</b>: $date_trip\n"
                              "⏰ <b>$time</b>: $time_trip\n\n"
                              "⚠️$active_orders")
        text_order = text_order.substitute(car_full=Order.car_full, driver_call=Order.driver_call,
                                           date=Passenger.date, date_trip=datetime.date.strftime(date, "%d.%m"),
                                           time=Passenger.time, time_trip=await func.sort_time(time=time),
                                           active_orders=Text_lang.order.active_orders)
        return text_order


    # active order view
    async def active_order_driver(self, order_accept_id: int, language: str):
        self.__language = language
        self.__order_accept_id = order_accept_id
        await self._unpack()
        if self.__type == "passenger":
            await self.order_passenger()
        elif self.__type == "delivery":
            await self.order_delivery()
        return self.__text

    async def _unpack(self):
        self.__Text_lang = Txt.language[self.__language]
        self.__order_client_id, self.__client_id, self.__driver_id, self.__phone_client, self.__type, \
        self.__from_region, self.__from_town, self.__to_region, self.__to_town, self.__date, self.__time, \
        self.__places, self.__baggage, self.__trip, self.__price, self.__cost = \
            await pg.orderid_to_order_accepted_driver(order_accept_id=self.__order_accept_id)
        self.__from_region = await pg.id_to_region(reg_id=self.__from_region, language=self.__language)
        self.__from_town = await pg.id_to_town(reg_id=self.__from_town, language=self.__language)
        self.__to_region = await pg.id_to_region(reg_id=self.__to_region, language=self.__language)
        self.__to_town = await pg.id_to_town(reg_id=self.__to_town, language=self.__language)
        self.__date = datetime.date.strftime(self.__date, "%d.%m")
        self.__time = await func.sort_time(time=self.__time)
        self.__package = self.__Text_lang.baggage.package_gab[self.__baggage]
        self.__price = await func.num_int_to_str(num=self.__price)
        self.__cost = await func.num_int_to_str(num=self.__cost)
        self.__type_order = self.__Text_lang.order.driver.type_order[self.__type]
        self.__places = Txt.places.places_dict[self.__places]

    async def order_passenger(self):
        text = Template("$type\n\n"
                        "🔻 <b>$client_info</b> 🔻\n\n"
                        "📱 <b>$phone</b>: +$phone_client\n"
                        "🅰️ <b>$from_place</b>: $from_region, $from_town\n"
                        "🅱️ <b>$to_place</b>: $to_region, $to_town\n\n"
                        "🗓 <b>$date</b>: $date_trip\n"
                        "⏰ <b>$time</b>: $time_trip\n\n"
                        "💵$cost1 $client_places $cost2 - <b>$final_cost</b> $sum"
                        "$trip")
        self.__text = text.substitute(type=self.__type_order, client_info=self.__Text_lang.order.driver.info,
                                      phone=self.__Text_lang.chain.driver.phone, phone_client=self.__phone_client,
                                      from_place=self.__Text_lang.chain.driver.from_place,
                                      from_region=self.__from_region, from_town=self.__from_town,
                                      to_place=self.__Text_lang.chain.driver.to_place,
                                      to_region=self.__to_region, to_town=self.__to_town,
                                      date=self.__Text_lang.chain.passenger.date, date_trip=self.__date,
                                      time=self.__Text_lang.chain.passenger.time, time_trip=self.__time,
                                      place_client=self.__places,
                                      baggage=self.__Text_lang.chain.passenger.baggage, baggage_client=self.__baggage,
                                      cost=self.__Text_lang.chain.passenger.cost, sum=self.__Text_lang.symbol.sum,
                                      cost_final=self.__cost, trip=self.__Text_lang.chain.passenger.trip)

    async def order_delivery(self):
        text = Template("$type\n\n"
                        "🔻 <b>$client_info</b> 🔻\n\n"
                        "📱 <b>$phone</b>: +$phone_client\n"
                        "🅰️ <b>$from_place</b>: $from_region, $from_town\n"
                        "🅱️ <b>$to_place</b>: $to_region, $to_town\n\n"
                        "🗓 <b>$date</b>: $date_trip\n"
                        "⏰ <b>$time</b>: $time_trip\n"
                        "🧰<b>$baggage</b>: $baggage_client\n\n"
                        "💵$cost - <b>$final_cost</b> $sum\n"
                        "$trip\n\n")
        self.__text = text.substitute(type=self.__type_order, client_info=self.__Text_lang.order.driver.info,
                                      phone=self.__Text_lang.chain.driver.phone, phone_client=self.__phone_client,
                                      from_place=self.__Text_lang.chain.driver.from_place,
                                      from_region=self.__from_region, from_town=self.__from_town,
                                      to_place=self.__Text_lang.chain.driver.to_place,
                                      to_region=self.__to_region, to_town=self.__to_town,
                                      date=self.__Text_lang.chain.delivery.date, date_trip=self.__date,
                                      time=self.__Text_lang.chain.delivery.time, time_trip=self.__time,
                                      baggage=self.__Text_lang.chain.delivery.baggage, baggage_client=self.__package,
                                      price=self.__Text_lang.chain.delivery.price, driver_price=self.__price,
                                      cost=self.__Text_lang.chain.delivery.cost, final_cost=self.__cost,
                                      sum=self.__Text_lang.symbol.sum, trip=self.__Text_lang.chain.delivery.trip)

