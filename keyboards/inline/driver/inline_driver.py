
import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from pgsql import pg

from text.text_func import TextFunc
from text.language.main import Text_main
from payme_api.get_check import GetCheck

Txt = Text_main()
func = TextFunc()


class InlineDriver:

    def __init__(self):
        self.__region = None
        self.__driver_id = None
        self.__language = None
        self.__markup = None

    async def menu_car(self, language: str, back=True):
        markup = InlineKeyboardMarkup(row_width=3)
        Text_lang = Txt.language[language]
        for car in await pg.id_and_car():
            b_car = InlineKeyboardButton(text=f"{car[1]}", callback_data=f"car_{car[0]}")
            markup.insert(b_car)
        if back is True:
            b_back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data="back")
            markup.add(b_back)
        return markup

    async def menu_share_phone(self, language: str):
        markup = InlineKeyboardMarkup(row_width=1)
        Text_lang = Txt.language[language]
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data="phoneback")
        markup.add(back)
        return markup

    async def menu_agreement(self, language: str):
        markup = InlineKeyboardMarkup(row_width=2)
        Text_lang = Txt.language[language]
        Common = Text_lang.buttons.common
        b_no = InlineKeyboardButton(text=Common.no, callback_data='back')
        b_yes = InlineKeyboardButton(text=Common.yes, callback_data='agree')
        back = InlineKeyboardButton(text=Common.back, callback_data="back")
        markup.add(b_no, b_yes,back)
        return markup

    async def _append_parameters(self, parameter: str, parameters: [list, str]):
        # print(parameter, parameters)
        if parameter in parameters:
            return "✅ " + parameter
        else:
            return parameter

    async def menu_active_route(self, language: str, driver_id: int):
        self.__driver_id = driver_id
        self.__language = language
        self.__markup = InlineKeyboardMarkup(row_width=1)
        await self._route()
        Text_lang = Txt.language[language]
        b1 = InlineKeyboardButton(text=Text_lang.buttons.driver.newRoute, callback_data="newRoute")
        self.__markup.add(b1)
        return self.__markup

    async def _route(self):
        for route in (await pg.all_route_driver(driver_id=self.__driver_id)):
            await self._route_text(route=route)
            b = InlineKeyboardButton(text=f"✍️{self.__text}", callback_data=f"route_{route[0]}")
            self.__markup.add(b)

    async def _route_text(self, route: list):
        if route[1] != route[3]:
            self.__text = await pg.id_to_region(reg_id=route[1], language=self.__language)
            self.__text += f" - {await pg.id_to_region(reg_id=route[3], language=self.__language)}"
        else:
            self.__text = await pg.id_to_town(reg_id=route[2][0], language=self.__language)
            self.__text += f" - {await pg.id_to_town(reg_id=route[4][0], language=self.__language)}"
            self.__text += f" - {await pg.id_to_town(reg_id=route[2][0], language=self.__language)}"

    async def menu_route(self, language: str):
        markup = InlineKeyboardMarkup(row_width=1)
        Text_lang = Txt.language[language]
        b1 = InlineKeyboardButton(text=Text_lang.buttons.common.out_region, callback_data="out")
        b2 = InlineKeyboardButton(text=Text_lang.buttons.common.in_region, callback_data="in")
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data="back")
        markup.add(b1, b2).add(back)
        return markup

    async def menu_in_region(self, language: str):
        markup = InlineKeyboardMarkup(row_width=2)
        Text_lang = Txt.language[language]
        for button in (await pg.id_and_region(language=language)):
            b_region = InlineKeyboardButton(text=button[1], callback_data=f"region_{button[0]}")
            markup.insert(b_region)
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data="back")
        markup.add(back)
        return markup

    async def menu_out_region(self, language: str, regions: list):
        markup = InlineKeyboardMarkup(row_width=2)
        Text_lang = Txt.language[language]
        for button in (await pg.id_and_region(language=language)):
            text = await self._append_parameters(parameter=button[1], parameters=regions)
            b_region = InlineKeyboardButton(text=text, callback_data=f"region_{button[0]}")
            markup.insert(b_region)
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data="back")
        markup.add(back)
        return markup

    async def menu_town(self, reg_id: int, towns: list, language: str):
        markup = InlineKeyboardMarkup(row_width=2)
        Text_lang = Txt.language[language]
        for button in (await pg.reg_id_to_towns(reg_id=reg_id, language=language)):
            text = await self._append_parameters(parameter=button[1], parameters=towns)
            b_region = InlineKeyboardButton(text=text, callback_data=f"town_{button[0]}")
            markup.insert(b_region)
        cont = InlineKeyboardButton(text=Text_lang.buttons.common.cont, callback_data=f"continue")
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data=f"back")
        markup.add(cont).add(back)
        return markup

    async def menu_from_region(self, language: str):
        markup = InlineKeyboardMarkup(row_width=2)
        Text_lang = Txt.language[language]
        for button in (await pg.id_and_region(language=language)):
            b_region = InlineKeyboardButton(text=button[1], callback_data=f"region_{button[0]}")
            markup.insert(b_region)
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data="back")
        markup.add(back)
        return markup

    async def menu_to_region(self, language: str, from_region: int, to_regions: list):
        markup = InlineKeyboardMarkup(row_width=2)
        Text_lang = Txt.language[language]
        print(to_regions)
        if 17 not in to_regions:
            print('ok')
        for button in (await pg.id_and_region(language=language)):
            if button[0] != from_region:
                if button[0] not in to_regions:
                    b_region = InlineKeyboardButton(text=button[1], callback_data=f"region_{button[0]}")
                else:
                    b_region = InlineKeyboardButton(text=f"⛔ {button[1]}", callback_data=f"duplicationRouteOut")
                markup.insert(b_region)
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data="back")
        markup.add(back)
        return markup

    async def menu_towns(self, reg_id: int, towns: list, language: str, all_towns: list):
        markup = InlineKeyboardMarkup(row_width=2)
        Text_lang = Txt.language[language]
        for button in (await pg.reg_id_to_towns(reg_id=reg_id, language=language)):
            if button[0] not in all_towns:
                text = await self._append_parameters(parameter=button[1], parameters=towns)
                b_region = InlineKeyboardButton(text=text, callback_data=f"town_{button[0]}")
            else:
                b_region = InlineKeyboardButton(text=f"⛔ {button[1]}", callback_data=f"duplicationRouteIn")
            markup.insert(b_region)
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data=f"back")
        markup.add(back)
        return markup

    async def menu_cond(self, language: str):
        markup = InlineKeyboardMarkup(row_width=2)
        Text_lang = Txt.language[language]
        b1 = InlineKeyboardButton(text=Text_lang.buttons.common.no, callback_data="cond_0")
        b2 = InlineKeyboardButton(text=Text_lang.buttons.common.da, callback_data="cond_1")
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data="back")
        markup.add(b1, b2).add(back)
        return markup

    async def menu_price(self, language: str):
        markup = InlineKeyboardMarkup(row_width=3)
        Text_lang = Txt.language[language]
        for price in Txt.money.driver.price:
            text_price = await func.num_int_to_str(num=price)
            b_price = InlineKeyboardButton(text=text_price, callback_data=f"price_{price}")
            markup.insert(b_price)
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data="back")
        markup.add(back)
        return markup

    async def menu_order(self, language: str):
        markup = InlineKeyboardMarkup(row_width=2)
        Text_lang = Txt.language[language]
        Common = Text_lang.buttons.common
        b = InlineKeyboardButton(text=Common.agree, callback_data="book")
        back = InlineKeyboardButton(text=Common.back, callback_data="back")
        markup.add(b).add(back)
        return markup

    async def menu_route_cancel(self, language: str, route_id: int):
        markup = InlineKeyboardMarkup(row_width=1)
        Text_lang = Txt.language[language]
        b1 = InlineKeyboardButton(text=Text_lang.buttons.driver.price_change, callback_data=f"updatePrice_{route_id}")
        b2 = InlineKeyboardButton(text=Text_lang.buttons.driver.route_cancel, callback_data=f"cancel_{route_id}")
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data="back")
        markup.add(b1, b2, back)
        return markup

    async def menu_route_choose(self, language: str, route_id: int):
        markup = InlineKeyboardMarkup(row_width=2)
        Text_lang = Txt.language[language]
        b1 = InlineKeyboardButton(text=Text_lang.buttons.common.no, callback_data="no")
        b2 = InlineKeyboardButton(text=Text_lang.buttons.common.da, callback_data=f"yes_{route_id}")
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data="back")
        markup.add(b1, b2).add(back)
        return markup

    async def menu_active_order_cancel(self, language: str, order_accept_id: int):
        markup = InlineKeyboardMarkup(row_width=1)
        Text_lang = Txt.language[language]
        delete = InlineKeyboardButton(text=Text_lang.buttons.cancel.client, callback_data="delete")
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data=f"back_{order_accept_id}")
        markup.add(delete).add(back)
        return markup

    async def menu_active_order_view(self, order_accept_id: int, language: str):
        markup = InlineKeyboardMarkup(row_width=1)
        Text_lang = Txt.language[language]
        cancel = InlineKeyboardButton(text=Text_lang.buttons.cancel.client, callback_data=f"cancel_{order_accept_id}")
        markup.add(cancel)
        return markup

    async def menu_price_update(self, language: str, route_id: int):
        markup = InlineKeyboardMarkup(row_width=3)
        Text_lang = Txt.language[language]
        for price in Txt.money.driver.price:
            text_price = await func.num_int_to_str(num=price)
            b_price = InlineKeyboardButton(text=text_price, callback_data=f"updatePrice_{price}_{route_id}")
            markup.insert(b_price)
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data="back")
        markup.add(back)
        return markup


    async def menu_choose_more(self, order_client_id: int, language: str):
        markup = InlineKeyboardMarkup(row_width=1)
        Text_lang = Txt.language[language]
        b = InlineKeyboardButton(text=Text_lang.buttons.passenger.choose_more, callback_data=f"passenger_{order_client_id}")
        markup.add(b)
        return markup

    async def menu_find_more(self, order_client_id: int, language: str):
        markup = InlineKeyboardMarkup(row_width=1)
        Text_lang = Txt.language[language]
        b = InlineKeyboardButton(text=Text_lang.buttons.delivery.find_more, callback_data=f"delivery_{order_client_id}")
        markup.add(b)
        return markup

    async def menu_personal_data(self, language: str):
        markup = InlineKeyboardMarkup(row_width=1)
        Text_lang = Txt.language[language]
        Cabinet = Text_lang.buttons.personal_cabinet.data
        Common = Text_lang.buttons.common
        b_name = InlineKeyboardButton(text=Cabinet.name, callback_data=f"change_name")
        b_phone = InlineKeyboardButton(text=Cabinet.phone, callback_data=f"change_phone")
        b_car = InlineKeyboardButton(text=Cabinet.car, callback_data=f"change_car")
        back = InlineKeyboardButton(text=Common.back, callback_data="back")
        markup.add(b_name, b_phone, b_car, back)
        return markup

    async def menu_back(self, language: str):
        markup = InlineKeyboardMarkup(row_width=1)
        Text_lang = Txt.language[language]
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data="back")
        markup.add(back)
        return markup

    async def menu_balance(self, language: str):
        markup = InlineKeyboardMarkup(row_width=1)
        Text_lang = Txt.language[language]
        balance = InlineKeyboardButton(text=Text_lang.buttons.personal_cabinet.wallet.balance, callback_data="balance")
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data="back")
        markup.add(balance, back)
        return markup

    async def menu_cash(self, language: str):
        markup = InlineKeyboardMarkup(row_width=2)
        Text_lang = Txt.language[language]
        for price in Txt.money.wallet.price:
            text_cash = await func.num_int_to_str(num=price)
            b_cash = InlineKeyboardButton(text=text_cash, callback_data=f"cash_{price}")
            markup.insert(b_cash)
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data="walletback")
        markup.add(back)
        return markup

    async def menu_pay_way(self, language: str):
        markup = InlineKeyboardMarkup(row_width=3)
        Text_lang = Txt.language[language]
        Cabinet = Text_lang.buttons.personal_cabinet.wallet
        payme = InlineKeyboardButton(text=Cabinet.payme, callback_data="Payme")
        click = InlineKeyboardButton(text=Cabinet.click, callback_data="Click")
        paynet = InlineKeyboardButton(text=Cabinet.paynet, callback_data="Paynet")
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data="walletback")
        markup.add(payme, click, paynet).add(back)
        return markup

    async def menu_payment(self, language: str):
        markup = InlineKeyboardMarkup(row_width=1)
        Text_lang = Txt.language[language]
        pay = InlineKeyboardButton(text=Text_lang.buttons.personal_cabinet.wallet.pay, callback_data="pay")
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data="walletback")
        markup.add(pay, back)
        return markup

    async def payme_url(self, language: str, url: str):
        markup = InlineKeyboardMarkup(row_width=1)
        Text_lang = Txt.language[language]
        url_button = InlineKeyboardButton(text=Text_lang.buttons.personal_cabinet.wallet.pay, url=url)
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data="walletback")
        markup.add(url_button, back)
        return markup

    async def click_url(self, language: str, url: str):
        markup = InlineKeyboardMarkup(row_width=1)
        Text_lang = Txt.language[language]
        url_button = InlineKeyboardButton(text=Text_lang.buttons.personal_cabinet.wallet.pay, url=url)
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data="walletback")
        markup.add(url_button, back)
        return markup

    async def menu_quiz(self, language: str):
        markup = InlineKeyboardMarkup(row_width=1)
        Text_lang = Txt.language[language]
        button = InlineKeyboardButton(text=Text_lang.quiz.yes, callback_data="quizback")
        back = InlineKeyboardButton(text=Text_lang.buttons.common.back, callback_data="walletback")
        markup.add(button, back)
        return markup