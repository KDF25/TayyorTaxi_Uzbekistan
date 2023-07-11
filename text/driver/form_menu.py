from string import Template
from aiogram.utils.markdown import hlink
from text.text_func import TextFunc
from text.language.main import Text_main

Txt =Text_main()
func = TextFunc()


class FormMenuDriver:

    async def how_to_use(self, language: str):
        Text_lang = Txt.language[language]
        form = Template('$text1')
        form = form.substitute(text1=hlink(url=Text_lang.url.driver.how_to_use, title=Text_lang.information.how_to_use))
        return form

    async def about_us(self, language: str):
        Text_lang = Txt.language[language]
        form = Template('$text1')
        form = form.substitute(text1=hlink(url=Text_lang.url.driver.about_us, title=Text_lang.information.about_us))
        return form

