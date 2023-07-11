import datetime
from string import Template

from text.text_func import TextFunc
from text.language.main import Text_main


Txt = Text_main()
func = TextFunc()


class FormDelivery:

    def __init__(self):
        self.__trip = None
        self.__baggage = None
        self.__Text_lang = None
        self.__price = None
        self.__language = None
        self.__data = None

    async def main_text(self, data: dict, question: str):
        Text_lang = Txt.language[data.get('lang')]
        form = Text_lang.chain.delivery
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
                        "🅱️ <b>$to_place</b>: $to_region, $to_town\n\n"
                        "$question")
        text = text.substitute(from_place=self.__Text_lang.chain.passenger.from_place,
                               from_region=self.__from_region, from_town=self.__from_town,
                               to_place=self.__Text_lang.chain.passenger.to_place,
                               to_region=self.__to_region, to_town=self.__to_town,
                               question=self.__Text_lang.questions.passenger.date)
        return text

    async def menu_time(self, data: dict):
        self.__data = data
        self.__Text_lang = Txt.language[self.__data.get('lang')]
        await self._route()
        text = Template("🅰️ <b>$from_place</b>: $from_region, $from_town\n"
                        "🅱️ <b>$to_place</b>: $to_region, $to_town\n\n"
                        "🗓 <b>$date</b>: $date_trip\n\n"
                        "$question")
        text = text.substitute(from_place=self.__Text_lang.chain.passenger.from_place,
                               from_region=self.__from_region, from_town=self.__from_town,
                               to_place=self.__Text_lang.chain.passenger.to_place,
                               to_region=self.__to_region,  to_town=self.__to_town,
                               date=self.__Text_lang.chain.passenger.date, date_trip=self.__data.get('date')[0:5],
                               question=self.__Text_lang.questions.passenger.time)
        return text

    async def menu_package(self, data: dict):
        self.__data = data
        await self._package_prepare()
        text = Template("🅰️ <b>$from_place</b>: $from_region, $from_town\n"
                        "🅱️ <b>$to_place</b>: $to_region, $to_town\n\n"
                        "🗓 <b>$date</b>: $date_trip\n"
                        "⏰ <b>$time</b>: $time_trip\n\n"
                        "🧰$question")
        text = text.substitute(from_place=self.__Text_lang.chain.delivery.from_place,
                               from_region=self.__from_region, from_town=self.__from_town,
                               to_place=self.__Text_lang.chain.delivery.to_place,
                               to_region=self.__to_region, to_town=self.__to_town,
                               date=self.__Delivery.date, date_trip=self.__date,
                               time=self.__Delivery.time, time_trip=self.__time,
                               question=self.__Text_lang.questions.delivery.package)
        return text

    async def _package_prepare(self):
        await self._route()
        self.__Text_lang = Txt.language[self.__data.get('lang')]
        self.__Delivery = self.__Text_lang.chain.delivery
        self.__date = self.__data.get("date")[0:5]
        self.__time = await func.sort_time(time=self.__data.get("time"))

    # order text delivery
    async def order_delivery(self, data: dict):
        self.__data = data
        await self._unpack_for_delivery()
        text = Template("🅰️ <b>$from_place</b>: $from_region, $from_town\n"
                        "🅱️ <b>$to_place</b>: $to_region, $to_town\n\n"
                        "🗓 <b>$date</b>: $date_trip\n"
                        "⏰ <b>$time</b>: $time_trip\n"
                        "🧰 <b>$baggage</b>: $baggage_client\n\n"
                        "💵 $cost - <b>$cost_final</b> $sum\n"
                        "$trip")
        text = text.substitute(from_place=self.__Delivery.from_place,
                               from_region=self.__from_region, from_town=self.__from_town,
                               to_place=self.__Delivery.to_place,
                               to_region=self.__to_region, to_town=self.__to_town,
                               date=self.__Delivery.date, date_trip=self.__date,
                               time=self.__Delivery.time, time_trip=self.__time,
                               baggage=self.__Delivery.baggage, baggage_client=self.__baggage,
                               cost=self.__Delivery.price, sum=self.__Text_lang.symbol.sum, cost_final=self.__cost,
                               trip=self.__Delivery.trip)
        return text

    async def _unpack_for_delivery(self):
        self.__Text_lang = Txt.language[self.__data.get('lang')]
        self.__Delivery = self.__Text_lang.chain.delivery
        self.__price = await func.num_int_to_str(num=self.__data.get("price"))
        self.__cost = await func.num_int_to_str(num=self.__data.get("cost"))
        self.__phone_client = self.__data.get("phone_client")
        self.__from_region = self.__data.get("from_region_value")
        self.__from_town = self.__data.get("from_town_value")
        self.__to_region = self.__data.get("to_region_value")
        self.__to_town = self.__data.get("to_town_value")
        self.__date = self.__data.get("date")[0:5]
        self.__time = await func.sort_time(time=self.__data.get("time"))
        self.__baggage = self.__Text_lang.baggage.package_gab[self.__data.get("baggage")]

    # order text driver
    async def order_driver(self, data: dict, language: str):
        self.__language = language
        self.__data = data
        await self._unpack_for_driver()
        order = Template("$new_order - $type\n\n"
                         "🗓 <b>$date</b>: $date_trip\n"
                         "⏰ <b>$time</b>: $time_trip\n"
                         "🧰 <b>$baggage</b>: $baggage_type\n\n"
                         "🅰️ <b>$from_place</b>: $from_region, $from_town\n"
                         "🅱️ <b>$to_place</b>: $to_region, $to_town\n\n"
                         "💵 $cost - <b>$cost_final</b> $sum\n"
                         "$trip\n\n"
                         "$order\n"
                         "⚠️<i>$order_cost</i>")
        order = order.substitute(new_order=self.__Text_lang.order.driver.new_order, type=self.__type,
                                 date=self.__Delivery.date, date_trip=self.__date,
                                 time=self.__Delivery.time, time_trip=self.__time,
                                 from_place=self.__Delivery.from_place,
                                 from_region=self.__from_region, from_town=self.__from_town,
                                 to_place=self.__Delivery.to_place,
                                 to_region=self.__to_region, to_town=self.__to_town,
                                 baggage=self.__Delivery.baggage, baggage_type=self.__baggage,
                                 price=self.__Delivery.price, order_price=self.__price,
                                 cost=self.__Delivery.price, sum=self.__Text_lang.symbol.sum, cost_final=self.__cost,
                                 order=self.__Text_lang.order.driver.order, trip=self.__Delivery.trip,
                                 order_cost=self.__text)
        return order

    async def _unpack_for_driver(self):
        self.__Text_lang = Txt.language[self.__language]
        self.__Delivery = self.__Text_lang.chain.delivery
        self.__type = self.__Text_lang.order.driver.type_order[self.__data.get('type')]
        self.__baggage = self.__Text_lang.baggage.package_gab[self.__data.get('baggage')]
        self.__from_region, self.__from_town, self.__to_region, self.__to_town, self.__car = \
            await func.id_to_value(data=self.__data, language=self.__language)
        self.__date = datetime.date.strftime(self.__data.get('date'),  "%d.%m")
        self.__time = await func.sort_time(time=self.__data.get("time"))
        self.__price = await func.num_int_to_str(num=self.__data.get('price'))
        self.__cost = await func.num_int_to_str(num=self.__data.get('cost'))
        await self._order_cost()

    async def _order_cost(self):
        tax = await func.percent_price(price=self.__data.get('price'))
        self.__tax = await func.num_int_to_str(num=tax)
        text = Template("$text1 <b>$price</b> $text2")
        self.__text = text.substitute(text1=self.__Text_lang.order.driver.order_cost1, price=self.__tax,
                                      text2=self.__Text_lang.order.driver.order_cost2)
