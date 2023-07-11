import datetime
from datetime_now.datetime_now import dt_now
import math

from natsort import natsorted

from pgsql import pg
from text.language.main import Text_main

Txt = Text_main()


class TextFunc:
    async def sort_and_unite(self, LIST: list, language=None):
        LIST.sort()
        if type(LIST[0]) == str:
            LIST = f"({str(', '.join((str(i) for i in LIST)))})"
        elif type(LIST[0]) == datetime.date:
            LIST = str(', '.join((datetime.datetime.strftime(i, "%d.%m") for i in LIST)))
        elif type(LIST[0]) == int:
            a = []
            for i in LIST:
                a.append(await pg.id_to_town(reg_id=i, language=language))
            LIST = str(', '.join(i for i in a))
        return LIST

    async def unpack_time(self, TIME: list):
        LIST = []
        TIME = natsorted(TIME)
        for i in range(0, len(TIME)):
            x = TIME[i].split(" - ")
            LIST.append(x[0])
            LIST.append(x[1])
        return LIST

    async def sort_time(self, time: list, i=0):
        LIST = []
        time = await self.unpack_time(TIME=time)
        while True:
            try:
                if time[i] == time[i + 1]:
                    time.pop(i + 1)
                    time.pop(i)
                    i = i - 2
                else:
                    i += 1
            except IndexError:
                break
        for i in range(0, len(time), 2):
            LIST.append(f"{time[i]} - {time[i + 1]}")
        LIST = f"{str(', '.join((str(i) for i in LIST)))}"
        return LIST

    async def times(self, time):
        Time = []
        times = await self.sort_time(time=time)
        times = times.split(', ')
        for index, time in enumerate(times):
            time = time.split(' - ')
            time_start = datetime.datetime.strptime(time[0], "%H:%M").time()
            if time[1] == '24:00':
                time[1] = '23:59'
            time_end = datetime.datetime.strptime(time[1], "%H:%M").time()
            Time.append([time_start, time_end])
        return Time



    async def increase(self, trip):
        increase = str(Txt.money.price.trip_price[trip])
        increase = '' if trip == 0 else f'(+{increase[-6:-3]} {increase[-3:]})'
        return increase

    async def num_int_to_str(self, num):
        new_num = ""
        num = str(num)
        num_len = len(num)
        for i in range(0, num_len, 3):
            if i < num_len - 3:
                part = num[num_len - 3 - i:num_len - i:]
                new_num = f"{part} {new_num}"
        new_num_len = len(new_num.replace(" ", ''))
        if new_num_len < num_len:
            new_num = f"{num[0:num_len - new_num_len]} {new_num}"
        return new_num

    async def time(self):
        time = dt_now.now().hour // 3 + 1
        time = 0 if time * 3 >= 24 else time * 3
        time = [f"{time}:00 - {time + 3}:00"]
        return time

    async def date(self):
        day = 1 if dt_now.now().hour >= 21 else 0
        date = dt_now.now().date() + datetime.timedelta(days=day)
        date = datetime.date.strftime(date, "%d.%m.%Y")
        return date

    async def id_to_value(self, data: dict, language: str):
        from_region = await pg.id_to_region(reg_id=data.get('from_region'), language=language)
        from_town = await pg.id_to_town(reg_id=data.get('from_town'), language=language)
        to_region = await pg.id_to_region(reg_id=data.get('to_region'), language=language)
        to_town = await pg.id_to_town(reg_id=data.get('to_town'), language=language)
        car = await pg.id_to_car(car_id=data.get('car')) if data.get('car', None) is not None else 0
        return from_region, from_town, to_region, to_town, car

    async def _total_regions(self, reg_1: int, reg_2: int):
        reg_1, reg_2 = await self._sort_regions(reg_1=reg_1, reg_2=reg_2)
        delta = 0
        delivery = Txt.money.price.delivery
        if reg_1 == 111 and (delivery[reg_2] >= 6 or reg_2 == 73):
            delta = 2
        elif reg_2 == 73 and delivery[reg_1] < 3:
            delta = -1
        elif reg_1 == 1 and reg_1 == 166:
            delta = 1
        total = abs(delivery[reg_1] - delivery[reg_2]) + delta + 1
        return total

    async def _sort_regions(self, reg_1: int, reg_2: int):
        L = [reg_1, reg_2]
        if 111 in L:
            L.remove(111)
            reg_1, reg_2 = 111, L[0]
        elif 73 in L:
            L.remove(73)
            reg_1, reg_2 = L[0], 73
        return reg_1, reg_2

    async def _price_index(self, reg_1: int, reg_2: int):
        total = await self._total_regions(reg_1=reg_1, reg_2=reg_2)
        index = 0
        for num in range(1, total + 1):
            delta = 1 / num
            index = delta + index
        return index

    async def price_func(self, reg_1: int, reg_2: int, price: int):
        index = await self._price_index(reg_1=reg_1, reg_2=reg_2)
        price = price / 10000
        round_price = math.floor(index * price)
        real_price = index * price
        if float(round_price) == float(real_price):
            round_price = round_price
        elif round_price + 0.5 >= real_price:
            round_price = round_price + 0.5
        else:

            round_price = round_price + 1
        round_price = int(round_price * 10000)
        return round_price

    async def percent_price(self, price: int):
        tax = int(price * 5 / 100)
        tax = math.ceil(tax / 1000) * 1000
        tax = tax if tax < 9000 else 9000
        return tax
