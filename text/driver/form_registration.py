
from string import Template

from aiogram.utils.markdown import hlink

from text.text_func import TextFunc
from text.language.main import Text_main


Txt = Text_main()
func = TextFunc()


class FormRegistration:
    async def rules(self, language: str):
        Text_lang = Txt.language[language]
        form = Template('$text1')
        form = form.substitute(text1=hlink(url=Text_lang.url.driver.rules, title=Text_lang.information.rules))
        return form

    async def how_to_use(self, language: str):
        Text_lang = Txt.language[language]
        form = Template('$text1')
        form = form.substitute(text1=hlink(url=Text_lang.url.driver.how_to_use, title=Text_lang.information.how_to_use))
        return form

    async def greeting(self, language: str, name: str):
        Text_lang = Txt.language[language]
        text_send1 = Template("$hello $name")
        text_send1 = text_send1.substitute(hello=Text_lang.greeting.hello, name=name)
        text_send2 = Text_lang.questions.share_number
        return text_send1, text_send2

    async def agreement(self, name: str, phone: int, car: str, language: str):
        Text_lang = Txt.language[language]
        Cabinet = Text_lang.personal_cabinet
        form = Template("<b>$name</b>: $driver_name\n"
                        "<b>$phone</b>: $driver_phone\n"
                        "<b>$car</b>: $driver_car\n\n"
                        "$question $rules")
        form = form.substitute(name=Cabinet.name, driver_name=name,
                               phone=Cabinet.phone, driver_phone=phone,
                               car=Cabinet.car, driver_car=car,
                               question=Text_lang.questions.registration.agreement,
                               rules=await self.rules(language=language))
        return form

    async def finish(self, data: dict):
        Text_lang = Txt.language[data.get('lang')]
        Cabinet = Text_lang.personal_cabinet
        form = Template("<b>$id</b>: $driver_id\n"
                        "<b>$money</b>: $driver_money $sum\n\n"
                        "$congratulation\n\n"
                        "👉 $how_to_use\n"
                        "👉 $rules\n\n"
                        "<i>$online</i>")
        form = form.substitute(id=Cabinet.id, driver_id=data.get('user_id'), money=Cabinet.wallet,
                               driver_money=await func.num_int_to_str(num=Txt.money.wallet.wallet),
                               congratulation=Cabinet.congratulation, sum=Text_lang.symbol.sum,
                               how_to_use=await self.how_to_use(language=data.get('lang')),
                               rules=await self.rules(language=data.get('lang')), online=Cabinet.online)
        return form
