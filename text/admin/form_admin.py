import datetime
from string import Template

from pgsql import pg
from text.text_func import TextFunc
from text.language.main import Text_main

func = TextFunc()
Txt = Text_main()


class FormAdmin:
    def __init__(self):
        self.__data = None
        self.__text = None
        self.__type = None

    async def left_days(self, language: str, days: int, wallet: int, date):
        Text_lang = Txt.language[language]
        date = datetime.datetime.strftime(date, "%d.%m.%y")
        wallet = await func.num_int_to_str(num=wallet)
        day = ''
        if language == 'rus':
            day = 'день' if days == 1 else 'дней'
        text = Template("$text1 <b>$wallet $sum</b>"
                        "$text2 <b>$days $day</b>"
                        "$text3: $date $text4")
        text = text.substitute(text1=Text_lang.mailing.left_days.text1, wallet=wallet, sum=Text_lang.symbol.sum,
                               text2=Text_lang.mailing.left_days.text2, days=days, day=day,
                               text3=Text_lang.mailing.left_days.text3, date=date,
                               text4=Text_lang.mailing.left_days.text4)
        return text

    async def mail_end(self, users: str):
        count = await pg.get_users_unblock(users=users)
        text = Template('Рассылка завершена. Доставлено — $nonblock пользователям. '
                        'Бот заблокирован — $block пользователями')
        text = text.substitute(nonblock=count[0][0], block=count[1][0])
        return text

    async def mailing_choose(self, users: str):
        if users == 'client':
            self.__type = 'Клиенты'
        elif users == 'driver':
            self.__type = 'Водители'
        elif users == 'all':
            self.__type = 'Все пользователи'
        await self.mailing()
        return self.__text

    async def mailing(self):
        text = Template("<b>$type</b>\n\n"
                        "$start_mailing")
        self.__text = text.substitute(type=self.__type, start_mailing="Отправьте сообщение которое хотели бы разослать!")

    async def statistics(self):
        date = datetime.date.strftime(datetime.date.today(), "%d.%m.%Y")

        new_users = await func.num_int_to_str(num=await pg.new_users())
        new_drivers = await func.num_int_to_str(num=await pg.new_drivers())
        all_users = await func.num_int_to_str(num=await pg.all_users())
        all_drivers = await func.num_int_to_str(num=await pg.all_drivers())

        all_payment = await func.num_int_to_str(num=(await pg.all_payment())[0])
        all_payment_max = await func.num_int_to_str(num=(await pg.all_payment())[1])
        all_payment_min = await func.num_int_to_str(num=(await pg.all_payment())[2])
        all_payment_count = await func.num_int_to_str(num=(await pg.all_payment())[3])

        new_payment = await func.num_int_to_str(num=(await pg.new_payment())[0])
        new_payment_max = await func.num_int_to_str(num=(await pg.new_payment())[1])
        new_payment_min = await func.num_int_to_str(num=(await pg.new_payment())[2])
        new_payment_count = await func.num_int_to_str(num=(await pg.new_payment())[3])

        all_order_success_passenger = await func.num_int_to_str(num=(await pg.all_orders_success())[0][0])
        all_order_success_delivery = await func.num_int_to_str(num=(await pg.all_orders_success())[1][0])
        all_order_success_count = await func.num_int_to_str(num=(await pg.all_orders_success())[2][0])

        new_order_success_passenger = await func.num_int_to_str(num=(await pg.new_orders_success())[0][0])
        new_order_success_delivery = await func.num_int_to_str(num=(await pg.new_orders_success())[1][0])
        new_order_success_count = await func.num_int_to_str(num=(await pg.new_orders_success())[2][0])

        all_order_cancel_driver_passenger = await func.num_int_to_str(num=(await pg.all_order_cancel_driver())[0][0])
        all_order_cancel_driver_delivery = await func.num_int_to_str(num=(await pg.all_order_cancel_driver())[1][0])
        all_order_cancel_driver_count = await func.num_int_to_str(num=(await pg.all_order_cancel_driver())[2][0])

        new_order_cancel_driver_passenger = await func.num_int_to_str(num=(await pg.new_order_cancel_driver())[0][0])
        new_order_cancel_driver_delivery = await func.num_int_to_str(num=(await pg.new_order_cancel_driver())[1][0])
        new_order_cancel_driver_count = await func.num_int_to_str(num=(await pg.new_order_cancel_driver())[2][0])

        all_order_cancel_client_passenger = await func.num_int_to_str(num=(await pg.all_order_cancel_client())[0][0])
        all_order_cancel_client_delivery = await func.num_int_to_str(num=(await pg.all_order_cancel_client())[1][0])
        all_order_cancel_client_count = await func.num_int_to_str(num=(await pg.all_order_cancel_client())[2][0])

        new_order_cancel_client_passenger = await func.num_int_to_str(num=(await pg.new_order_cancel_client())[0][0])
        new_order_cancel_client_delivery = await func.num_int_to_str(num=(await pg.new_order_cancel_client())[1][0])
        new_order_cancel_client_count = await func.num_int_to_str(num=(await pg.new_order_cancel_client())[2][0])

        cancel_by_client_max = await func.num_int_to_str(num=(await pg.cancel_by_client())[0])
        cancel_by_client_min = await func.num_int_to_str(num=(await pg.cancel_by_client())[1])
        cancel_by_client_avg = await func.num_int_to_str(num=(await pg.cancel_by_client())[2])

        cancel_by_driver_max = await func.num_int_to_str(num=(await pg.cancel_by_driver())[0])
        cancel_by_driver_min = await func.num_int_to_str(num=(await pg.cancel_by_driver())[1])
        cancel_by_driver_avg = await func.num_int_to_str(num=(await pg.cancel_by_driver())[2])

        payment_type = await pg.all_payment_type()
        Click = await func.num_int_to_str(num=payment_type[0][0])
        Payme = await func.num_int_to_str(num=payment_type[1][0])
        Paynet = await func.num_int_to_str(num=payment_type[2][0])

        text = Template("Сводка: $date\n\n"

                        "Новые пользователи — <b>$new_users</b>\n"
                        "Новые водители — <b>$new_drivers</b>\n"
                        "Общее количество пользователей — <b>$all_users</b>\n"
                        "Общее количество водителей — <b>$all_drivers</b>\n\n"
                        "———————————————\n\n"
                        "Сумма пополнения сегодня — <b>$new_payment</b> сум\n"
                        "Общая сумма пополнения — <b>$all_payment</b> сум\n\n"
                        "———————————————\n\n"
                        "✅ Новые успешные заказы:\n"
                        "• Такси — $new_order_success_passenger\n"
                        "• Почта — $new_order_success_delivery\n"
                        "• Всего — $new_order_success_count\n\n"
                        "✅ В общем успешных заказов:\n"
                        "• Такси — $all_order_success_passenger\n"
                        "• Почта — $all_order_success_delivery\n"
                        "• Всего — $all_order_success_count\n\n"
                        "❌ Новые отменённые заказы:\n"
                        "Клиентом:\n"
                        "• Такси — $new_order_cancel_client_passenger\n"
                        "• Почта — $new_order_cancel_client_delivery\n"
                        "• Всего — $new_order_cancel_client_count\n\n"
                        'Водителем:\n'
                        "• Такси — $new_order_cancel_driver_passenger\n"
                        "• Почта — $new_order_cancel_driver_delivery\n"
                        "• Всего — $new_order_cancel_driver_count\n\n"
                        "❌ В общем отменённых заказов:\n"
                        "Клиентом:\n"
                        "• Такси — $all_order_cancel_client_passenger\n"
                        "• Почта — $all_order_cancel_client_delivery\n"
                        "• Всего — $all_order_cancel_client_count\n\n"
                        'Водителем:\n'
                        "• Такси — $all_order_cancel_driver_passenger\n"
                        "• Почта — $all_order_cancel_driver_delivery\n"
                        "• Всего — $all_order_cancel_driver_count\n\n"
                        "———————————————\n\n"
                        "Сумма пополнения сегодня:\n"
                        "• максимум — $new_payment_max сум\n"
                        "• минимум — $new_payment_min сум\n"
                        "• <b>кол-во пополнений — $new_payment_count</b>\n\n"
                        "За все время:\n"
                        "• максимум — $all_payment_max сум\n"
                        "• минимум — $all_payment_min сум\n"
                        "• <b>кол-во пополнений — $all_payment_count</b>\n\n"
                        "Метод оплаты:\n"
                        "• Click — $Click\n"
                        "• Payme — $Payme\n"
                        "• Paynet — $Paynet\n\n"
                        "———————————————\n\n"
                        "⛔️Отмена заказа 1 пользователем:\n"
                        "Клиент:\n"
                        "• максимум отклонено — $cancel_by_client_max\n"
                        "• минимум — $cancel_by_client_min\n"
                        "• среднее — $cancel_by_client_avg\n\n"
                        "Водитель:\n"
                        "• максимум отклонено — $cancel_by_driver_max\n"
                        "• минимум — $cancel_by_driver_min\n"
                        "• среднее — $cancel_by_driver_avg\n")
        text = text.substitute(date=date,
                               new_users=new_users,
                               new_drivers=new_drivers,
                               all_users=all_users,
                               all_drivers=all_drivers,

                               all_payment=all_payment,
                               all_payment_max=all_payment_max,
                               all_payment_min=all_payment_min,
                               all_payment_count=all_payment_count,

                               new_payment=new_payment,
                               new_payment_max=new_payment_max,
                               new_payment_min=new_payment_min,
                               new_payment_count=new_payment_count,

                               all_order_success_passenger=all_order_success_passenger,
                               all_order_success_delivery=all_order_success_delivery,
                               all_order_success_count=all_order_success_count,

                               new_order_success_passenger=new_order_success_passenger,
                               new_order_success_delivery=new_order_success_delivery,
                               new_order_success_count=new_order_success_count,

                                all_order_cancel_driver_passenger=all_order_cancel_driver_passenger,
                               all_order_cancel_driver_delivery=all_order_cancel_driver_delivery,
                               all_order_cancel_driver_count=all_order_cancel_driver_count,

                               new_order_cancel_driver_passenger=new_order_cancel_driver_passenger,
                               new_order_cancel_driver_delivery=new_order_cancel_driver_delivery,
                               new_order_cancel_driver_count=new_order_cancel_driver_count,

                               all_order_cancel_client_passenger=all_order_cancel_client_passenger,
                               all_order_cancel_client_delivery=all_order_cancel_client_delivery,
                               all_order_cancel_client_count=all_order_cancel_client_count,

                               new_order_cancel_client_passenger=new_order_cancel_client_passenger,
                               new_order_cancel_client_delivery=new_order_cancel_client_delivery,
                               new_order_cancel_client_count=new_order_cancel_client_count,

                               Click=Click, Payme=Payme, Paynet=Paynet,

                               cancel_by_client_max=cancel_by_client_max,
                               cancel_by_client_min=cancel_by_client_min,
                               cancel_by_client_avg=cancel_by_client_avg,

                               cancel_by_driver_max=cancel_by_driver_max,
                               cancel_by_driver_min=cancel_by_driver_min,
                               cancel_by_driver_avg=cancel_by_driver_avg)
        # print(text)
        return text

    async def analise(self, data: dict):
        self.__data = data
        if self.__data['type'] == 'taxi':
            await self._taxi()
        elif self.__data['type'] == 'delivery':
            await self._delivery()
        elif self.__data['type'] == 'online':
            await self._online()
        return self.__text

    async def _taxi(self):
        await self._unpack_taxi()
        text = Template('Анализ $timeframe: $date\n\n'
                        '• Заказать такси - $passenger\n'
                        '• Откуда(регион) - $from_region\n'
                        '• Откуда(город)  - $from_town\n'
                        '• Куда(регион)   - $to_region\n'
                        '• Куда(город)    - $to_town\n'
                        '• Дата и время   - $date_time\n'
                        '• Багаж и места  - $num_bag\n'
                        '• Условия поездки - $trip\n'
                        '• Телефон        - $phone\n'
                        '• Модель         - $model\n'
                        '• Нет машин      - $no_model\n'
                        '• Водитель       - $driver\n'
                        '• Заказ          - $order\n\n'
                        '<b><i>* Нет машин - показывает процент тех, кто дошел до выбора модели, '
                        'но остановился так как не было машин</i></b>')
        self.__text = text.substitute(timeframe=self.__timeframe_text,date=self.__date, passenger=self.__type_app,
                                      from_region=self.__from_region, from_town=self.__from_town,
                                      to_region=self.__to_region, to_town=self.__to_town,
                                      date_time=self.__date_time, num_bag=self.__num_baggage,
                                      trip=self.__trip, phone=self.__phone,
                                      model=self.__model, no_model=self.__no_model,
                                      driver=self.__driver, order=self.__order)

    async def _unpack_taxi(self):
        self.__count = await pg.count_clients()
        self.__date = datetime.date.strftime(datetime.date.today(), "%d.%m.%Y")
        await self._timeframe_taxi()
        await self._unpack_parameters()
        await self._timeframe_text()
        self.__type_app, self.__from_region, self.__from_town, self.__to_region, self.__to_town, self.__date_time, \
        self.__num_baggage, self.__trip, self.__phone, self.__model, self.__no_model, self.__driver, self.__order = \
            self.__parameters

    async def _timeframe_taxi(self):
        if self.__data['timeframe'] == 'all':
            self.__parameters = await pg.analise_taxi_all_time()
        else:
            self.__parameters = await pg.analise_taxi_timeframe(days=int(self.__data['timeframe']))

    async def _timeframe_text(self):
        if self.__data['timeframe'] == 'all':
            self.__timeframe_text = 'за все время'
        else:
            self.__timeframe_text = f"за {self.__data['timeframe']} день/дней"

    async def _unpack_parameters(self):
        parameters = []
        for parameter in self.__parameters:
            parameter = f'{parameter[0]}/{self.__count}   ({round(parameter[0] / self.__count * 100, 1)} %)'
            parameters.append(parameter)
        self.__parameters = parameters

    async def _delivery(self):
        await self._unpack_delivery()
        text = Template('Анализ $timeframe: $date\n\n'
                        '• Отправить почту - $delivery\n'
                        '• Откуда(регион) - $from_region\n'
                        '• Откуда(город)  - $from_town\n'
                        '• Куда(регион)   - $to_region\n'
                        '• Куда(город)    - $to_town\n'
                        '• Дата и время   - $date_time\n'
                        '• Багаж          - $bag\n'
                        '• Условия поездки - $trip\n'
                        '• Телефон        - $phone\n'
                        '• Заказ          - $order\n\n')
        self.__text = text.substitute(timeframe=self.__timeframe_text,date=self.__date, delivery=self.__type_app,
                                      from_region=self.__from_region, from_town=self.__from_town,
                                      to_region=self.__to_region, to_town=self.__to_town,
                                      date_time=self.__date_time,  bag=self.__baggage,
                                      trip=self.__trip, phone=self.__phone,  order=self.__order)

    async def _unpack_delivery(self):
        self.__count = await pg.count_clients()
        self.__date = datetime.date.strftime(datetime.date.today(), "%d.%m.%Y")
        await self._timeframe_delivery()
        await self._unpack_parameters()
        await self._timeframe_text()
        self.__type_app, self.__from_region, self.__from_town, self.__to_region, self.__to_town, self.__date_time, \
        self.__baggage, self.__trip, self.__phone, self.__order = self.__parameters

    async def _timeframe_delivery(self):
        if self.__data['timeframe'] == 'all':
            self.__parameters = await pg.analise_delivery_all_time()
        else:
            self.__parameters = await pg.analise_delivery_timeframe(days=int(self.__data['timeframe']))

    async def _online(self):
        await self._unpack_online()
        text = Template('Анализ $timeframe: $date\n\n'
                        '• На линии       - $online\n'
                        '• Маршрут        - $route\n'
                        '• Откуда(регион) - $from_region\n'
                        '• Откуда(город)  - $from_town\n'
                        '• Куда(регион)   - $to_region\n'
                        '• Куда(город)    - $to_town\n'
                        '• Кондиционер    - $cond\n'
                        '• Цена           - $price\n'
                        '• Подтверждение  - $order\n'
                        '• Хотел отменить - $cancel\n'
                        '• Отменил        - $delete\n\n')
        self.__text = text.substitute(timeframe=self.__timeframe_text, date=self.__date,
                                      online=self.__online, route=self.__route,
                                      from_region=self.__from_region, from_town=self.__from_town,
                                      to_region=self.__to_region, to_town=self.__to_town,
                                      cond=self.__cond, price=self.__price, order=self.__order,
                                      cancel=self.__cancel, delete=self.__delete)

    async def _unpack_online(self):
        self.__count = await pg.count_drivers()
        self.__date = datetime.date.strftime(datetime.date.today(), "%d.%m.%Y")
        await self._timeframe_online()
        await self._unpack_parameters()
        await self._timeframe_text()
        self.__online, self.__route, self.__from_region, self.__from_town, self.__to_region, self.__to_town, \
        self.__cond,  self.__price, self.__order, self.__cancel, self.__delete = self.__parameters

    async def _timeframe_online(self):
        if self.__data['timeframe'] == 'all':
            self.__parameters = await pg.analise_online_all_time()
        else:
            self.__parameters = await pg.analise_online_timeframe(days=int(self.__data['timeframe']))