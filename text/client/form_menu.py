from string import Template
from aiogram.utils.markdown import hlink
from text.language.main import Text_main
from text.text_func import TextFunc

Txt = Text_main()
func = TextFunc()

class FormMenu:
    async def main(self, language: str):
        Text_lang = Txt.language[language]
        form = Template('$main\n\n'
                        '👉$text1')
        form = form.substitute(main=Text_lang.greeting.main, text1=hlink(url=Text_lang.url.client.how_to_use,
                                                                         title=Text_lang.information.how_to_use))
        return form

    async def how_to_use(self, language: str):
        Text_lang = Txt.language[language]
        form = Template('$text1')
        form = form.substitute(text1=hlink(url=Text_lang.url.client.how_to_use, title=Text_lang.information.how_to_use))
        return form

    async def about_us(self, language: str):
        Text_lang = Txt.language[language]
        form = Template('$text1')
        form = form.substitute(text1=hlink(url=Text_lang.url.client.about_us, title=Text_lang.information.about_us))
        return form

    async def order_cancel_client(self, type: str, places: int, language: str):
        Text_lang = Txt.language[language]
        text1 = Text_lang.cancel.driver.delivery if type == "delivery" \
                else Text_lang.cancel.driver.passenger
        text2 = " " if type == "delivery" else places
        order_text = Template("$cancel"
                              "$places\n\n"
                              "$active_order")
        order_text = order_text.substitute(cancel=text1, places=text2, active_order=Text_lang.order.active_orders)
        return order_text
