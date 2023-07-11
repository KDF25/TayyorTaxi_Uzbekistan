from string import Template
from text.language.main import Text_main
Txt = Text_main()

class FormNewOrderClient:

    async def order_cancel(self, name: str, car: str, language: str):
        Text_lang = Txt.language[language]
        text = Template("$cancel\n\n"
                        "🤵‍♂ <b>$name</b>: $driver_name\n"
                        "🚙 <b>$car</b>: $driver_car\n\n"
                        "$new_driver")
        text = text.substitute(cancel=Text_lang.cancel.client.driver.cancel,
                               name=Text_lang.chain.passenger.driver, driver_name=name,
                               car=Text_lang.chain.passenger.car, driver_car=car,
                               new_driver=Text_lang.cancel.client.driver.new_driver)
        return text

    async def cancel_delivery(self, language: str):
        Text_lang = Txt.language[language]
        text = Template("$cancel\n\n"
                        "$new_driver")
        text = text.substitute(cancel=Text_lang.cancel.client.driver.cancel,
                               new_driver=Text_lang.cancel.client.driver.new_driver)
        return text

    async def order_delete(self, name: str, car: str, language: str):
        Text_lang = Txt.language[language]
        text = Template("$delete\n\n"
                        "🤵‍♂ <b>$name</b>: $driver_name\n"
                        "🚙 <b>$car</b>: $driver_car\n\n"
                        "$new_driver")
        text = text.substitute(delete=Text_lang.cancel.client.driver.delete,
                               name=Text_lang.chain.passenger.driver, driver_name=name,
                               car=Text_lang.chain.passenger.car, driver_car=car,
                               new_driver=Text_lang.cancel.client.driver.new_driver)
        return text