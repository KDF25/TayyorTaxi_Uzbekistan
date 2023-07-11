from string import Template
from pgsql import pg

from text.text_func import TextFunc
from text.language.main import Text_main



Txt = Text_main()
func = TextFunc()



class FormPersonalData:

    async def personal_data_form(self, driver_id: int, name: str, phone_driver: int, car: int, language: str):
        Text_lang = Txt.language[language]
        Cabinet = Text_lang.personal_cabinet
        form = Template("<b>$id</b>: $driver_id\n"
                        "<b>$name</b>: $driver_name\n"
                        "<b>$phone</b>: $driver_phone\n"
                        "<b>$car</b>: $driver_car\n")
        form = form.substitute(id=Cabinet.id, driver_id=driver_id,
                               name=Cabinet.name, driver_name=name,
                               phone=Cabinet.phone, driver_phone=phone_driver,
                               car=Cabinet.car, driver_car=await pg.id_to_car(car_id=car))
        return form

    async def change_data_form(self, type_payment: str, language: str):
        Text_lang = Txt.language[language]
        Cabinet = Text_lang.chain.personal_cabinet
        form = Template("$type\n\n"
                        "$new_data")
        form = form.substitute(type=Cabinet.change_param[type_payment], new_data=Cabinet.new_data)
        return form

    async def wallet_form(self, driver_id: int, wallet: list, language: str):
        Text_lang = Txt.language[language]
        Cabinet = Text_lang.personal_cabinet
        form = Template("<b>$id</b>: $driver_id\n\n"
                        "$wallet👇\n"
                        "<b>$common:</b> $wallet_main $sum\n"
                        "<b>$bonus:</b> $wallet_bonus $sum\n")
        form = form.substitute(id=Cabinet.id, driver_id=driver_id, wallet=Cabinet.wallet,
                               common=Text_lang.personal_cabinet.common, bonus=Text_lang.personal_cabinet.bonus,
                               wallet_main=await func.num_int_to_str(num=wallet[0]), sum=Text_lang.symbol.sum,
                               wallet_bonus=await func.num_int_to_str(num=wallet[1]))
        return form

    async def pay_way_form(self, driver_id: int, cash: int, language: str):
        Text_lang = Txt.language[language]
        form = Template("<b>$id</b>: $driver_id\n"
                        "<b>$cash</b>: $driver_cash $sum\n")
        form = form.substitute(id=Text_lang.personal_cabinet.id, driver_id=driver_id,
                               cash=Text_lang.chain.personal_cabinet.amount, sum=Text_lang.symbol.sum,
                               driver_cash=await func.num_int_to_str(num=cash))
        return form

    async def payment_form(self, cash: int, type_payment: str, language: str):
        Text_lang = Txt.language[language]
        Cabinet = Text_lang.chain.personal_cabinet
        form = Template("$pay_way $type_payment\n"
                        "$amount: <b>$cash</b> $sum\n\n"
                        "<i>$payment</i>")
        form = form.substitute(pay_way=Cabinet.pay_way2, type_payment=type_payment, amount=Cabinet.amount2,
                               cash=await func.num_int_to_str(num=cash), payment=Cabinet.payment2,
                               sum=Text_lang.symbol.sum)
        return form

    async def payment_accept(self, cash: int, language: str):
        Text_lang = Txt.language[language]
        form = Template("$accept <b>$cash</b> $sum")
        form = form.substitute(accept=Text_lang.chain.personal_cabinet.accept, cash=await func.num_int_to_str(num=cash),
                               sum=Text_lang.symbol.sum)
        return form