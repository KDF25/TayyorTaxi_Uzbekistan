import datetime
from string import Template
from pgsql import pg

from text.text_func import TextFunc
from text.language.main import Text_main
from text.language.ru import Text_ru

Txt = Text_main()
RU = Text_ru()
func = TextFunc()


class FormClient:
    # main text
    def __init__(self):
        self.__trip = None
        self.__baggage = None
        self.__Text_lang = None
        self.__language = None
        self.__text = None
        self.__data = None

    async def main_text(self, data: dict, question: str):
        Text_lang = Txt.language[data.get('lang')]
        form = Text_lang.chain.passenger
        question_text1 = ''
        question_text2 = ''
        if data.get("from_region", None) is not None:
            from_region = data.get("from_region_value")
            if data.get("from_town", None) is not None:
                from_town = data.get("from_town_value")
                if data.get("to_region", None) is not None:
                    to_region = data.get("to_region_value")
                    if data.get("to_town", None) is not None:
                        to_town = data.get("to_town_value")
                    else:
                        to_town = "..."
                    question_text2 = f'🅱️ <b>{form.to_place}</b>: {to_region}, {to_town}\n'
            else:
                from_town = "..."
            question_text1 = f'🅰️ <b>{form.from_place}</b>: {from_region}, {from_town}\n'

        question_text = f"{question_text1}" \
                        f"{question_text2}" \
                        f"\n{question}"
        return question_text

    async def _route(self):
        self.__from_region = self.__data.get("from_region_value")
        self.__from_town = self.__data.get("from_town_value")
        self.__to_region = self.__data.get("to_region_value")
        self.__to_town = self.__data.get("to_town_value")

    async def _datetime(self):
        self.__date = self.__data.get('date')[0:5]
        self.__time = await func.sort_time(time=self.__data.get('time'))

    async def menu_date(self, data: dict):
        self.__data = data
        self.__Text_lang = Txt.language[self.__data.get('lang')]
        await self._route()
        text = Template("🅰️ <b>$from_place</b>: $from_region, $from_town\n"
                        "🅱️ <b>$to_place</b>: $to_region, ...\n\n"
                        "$question")
        text = text.substitute(from_place=self.__Text_lang.chain.passenger.from_place,
                               from_region=self.__from_region, from_town=self.__from_town,
                               to_place=self.__Text_lang.chain.passenger.to_place, to_region=self.__to_region,
                               question=self.__Text_lang.questions.passenger.date)
        return text

    async def menu_time(self, data: dict):
        self.__data = data
        self.__Text_lang = Txt.language[self.__data.get('lang')]
        await self._route()
        text = Template("🅰️ <b>$from_place</b>: $from_region, $from_town\n"
                        "🅱️ <b>$to_place</b>: $to_region, ...\n\n"
                        "🗓 <b>$date</b>: $date_trip\n\n"
                        "$question")
        text = text.substitute(from_place=self.__Text_lang.chain.passenger.from_place,
                               from_region=self.__from_region, from_town=self.__from_town,
                               to_place=self.__Text_lang.chain.passenger.to_place, to_region=self.__to_region,
                               date=self.__Text_lang.chain.passenger.date, date_trip=self.__data.get('date')[0:5],
                               question=self.__Text_lang.questions.passenger.time)
        return text

    async def menu_num_baggage(self, data: dict):
        self.__data = data
        self.__Text_lang = Txt.language[self.__data.get('lang')]
        await self._route()
        text = Template("🅰️ <b>$from_place</b>: $from_region, $from_town\n"
                        "🅱️ <b>$to_place</b>: $to_region, ...\n\n"
                        "💺 $question")
        text = text.substitute(from_place=self.__Text_lang.chain.passenger.from_place,
                               from_region=self.__from_region, from_town=self.__from_town,
                               to_place=self.__Text_lang.chain.passenger.to_place, to_region=self.__to_region,
                               question=self.__Text_lang.questions.passenger.number_baggage)
        return text

    # car text

    async def _times(self, time):
        Time = []
        times = await func.sort_time(time=time)
        times = times.split(', ')
        for index, time in enumerate(times):
            time = time.split(' - ')
            time_start = datetime.datetime.strptime(time[0], "%H:%M").time()
            if time[1] == '24:00':
                time[1] = '23:59'
            time_end = datetime.datetime.strptime(time[1], "%H:%M").time()
            Time.append([time_start, time_end])
        return Time

    async def _car_count(self, data: dict):
        count = 1
        # count = await pg.select_count(from_region=data.get("from_region"),  to_region=data.get("to_region"),
        #                               from_town=data.get("from_town"), to_town=data.get("to_town"),
        #                               places=data.get('num'),  client_id=data.get('client_id'),
        #                               date=data.get('date'), times=data['time'])
        return count

    async def _car_not_found(self, language: str):
        Text_lang = Txt.language[language]
        car_text = Text_lang.chain.passenger.car_not_found
        return car_text

    async def _car_find(self, count: int, language: str):
        Text_lang = Txt.language[language]
        car_text = Template("$pick- <b>$count</b> $auto\n\n"
                            "$choose_auto")
        car_text = car_text.substitute(pick=Text_lang.chain.passenger.car_find1, count=count,
                                       auto=Text_lang.chain.passenger.car_find2,
                                       choose_auto=Text_lang.questions.passenger.auto)
        return car_text

    async def car_text(self, data: dict):
        count = await self._car_count(data=data)
        # if count == 0:
        #     car_text = await self._car_not_found(language=data.get('lang'))
        # else:
        car_text = await self._car_find(count=count, language=data.get('lang'))
        return car_text

    # model text
    async def model_text(self, data: dict):
        Text_lang = Txt.language[data.get('lang')]
        car_text = Template("<b>$model</b>: $car\n\n"
                            "$choose_one")
        car_text = car_text.substitute(model=Text_lang.chain.passenger.car, car=data.get('car_value'),
                                       choose_one=Text_lang.questions.passenger.car)
        return car_text

    # order text passenger
    async def order_passenger(self, data: dict):
        self.__data = data
        await self._unpack_for_passenger()
        text = Template("🤵‍♂ <b>$name</b>: $driver_name\n"
                        "🚙 <b>$car</b>: $driver_car\n\n"
                        "🅰️ <b>$from_place</b>: $from_region, $from_town\n"
                        "🅱️ <b>$to_place</b>: $to_region, $to_town\n"
                        "🗓 <b>$date</b>: $date_trip\n"
                        "⏰ <b>$time</b>: $time_trip\n\n"
                        "💵$cost1 $client_places $cost2 - <b>$final_cost</b> $sum\n"
                        "$trip")
        text = text.substitute(name=self.__Passenger.driver, driver_name=self.__name,
                               car=self.__Passenger.car, driver_car=self.__car,
                               from_place=self.__Passenger.from_place,
                               from_region=self.__from_region, from_town=self.__from_town,
                               to_place=self.__Passenger.to_place,
                               to_region=self.__to_region, to_town=self.__to_town,
                               date=self.__Passenger.date, date_trip=self.__date,
                               time=self.__Passenger.time, time_trip=self.__time,
                               cost1=self.__Text_lang.chain.passenger.cost1, client_places=self.__places,
                               cost2=self.__Text_lang.chain.passenger.cost2,
                               final_cost=self.__cost, sum=self.__Text_lang.symbol.sum,
                               trip=self.__Text_lang.chain.passenger.trip)
        return text

    async def _unpack_for_passenger(self):
        self.__Text_lang = Txt.language[self.__data.get('lang')]
        self.__Passenger = self.__Text_lang.chain.passenger
        self.__name = self.__data.get("name")
        self.__car = self.__data.get("car_value")
        self.__price = await func.num_int_to_str(num=self.__data.get("price"))
        self.__phone_client = self.__data.get("phone_client")
        self.__from_region = self.__data.get("from_region_value")
        self.__from_town = self.__data.get("from_town_value")
        self.__to_region = self.__data.get("to_region_value")
        self.__to_town = self.__data.get("to_town_value")
        self.__date = self.__data.get("date")[0:5]
        self.__time = await func.sort_time(time=self.__data.get("time"))
        self.__places = Txt.places.places_dict[self.__data.get("num")]
        self.__cost = await func.num_int_to_str(num=self.__data.get("cost"))

    # order text driver
    async def order_driver(self, data: dict, language):
        self.__data = data
        self.__language = language
        await self._unpack_for_driver()
        order = Template("$new_order - $type\n\n"
                         "🗓 <b>$date</b>: $date_trip\n"
                         "⏰ <b>$time</b>: $time_trip\n"
                         "💺 <b>$places</b>: $client_places\n\n"
                         "🅰️ <b>$from_place</b>: $from_region, $from_town\n"
                         "🅱️ <b>$to_place</b>: $to_region, $to_town\n\n"
                         "💵$cost1 $client_places $cost2 - <b>$final_cost</b> $sum\n"
                         "$trip\n\n"
                         "$order\n"
                         "⚠️<i>$order_cost</i>")
        order = order.substitute(new_order=self.__Text_lang.order.driver.new_order, type=self.__type,
                                 date=self.__Text_lang.chain.driver.date,  date_trip=self.__date,
                                 time=self.__Text_lang.chain.passenger.time,  time_trip=self.__time,
                                 places=self.__Text_lang.chain.passenger.num,
                                 from_place=self.__Text_lang.chain.driver.from_place,
                                 from_region=self.__from_region, from_town=self.__from_town,
                                 to_place=self.__Text_lang.chain.driver.to_place,
                                 to_region=self.__to_region, to_town=self.__to_town,
                                 cost1=self.__Text_lang.chain.passenger.cost1, client_places=self.__places,
                                 cost2=self.__Text_lang.chain.passenger.cost2,
                                 final_cost=self.__cost, sum=self.__Text_lang.symbol.sum,
                                 trip=self.__Text_lang.chain.passenger.trip,
                                 order=self.__Text_lang.order.driver.order, order_cost=self.__text)
        print(order)
        return order

    async def _unpack_for_driver(self):
        self.__Text_lang = Txt.language[self.__language]
        self.__type = self.__Text_lang.order.driver.type_order[self.__data.get('type')]
        self.__from_region, self.__from_town, self.__to_region, self.__to_town, self.__car = \
            await func.id_to_value(data=self.__data, language=self.__language)
        self.__date = self.__data.get("date")[0:5]
        self.__time = await func.sort_time(time=self.__data.get("time"))
        self.__price = await func.num_int_to_str(num=self.__data.get('price'))
        self.__places = Txt.places.places_dict[self.__data.get("num")]
        self.__cost = await func.num_int_to_str(num=self.__data.get('cost'))
        await self._order_cost()

    async def _order_cost(self):
        tax = await func.percent_price(price=self.__data.get("price"))
        self.__tax = await func.num_int_to_str(num=(self.__data.get("num") * tax))
        text = Template("$text1 <b>$price</b> $text2")
        self.__text = text.substitute(text1=self.__Text_lang.order.driver.order_cost1, price=self.__tax,
                                      text2=self.__Text_lang.order.driver.order_cost2)
