from config import dp
from pgsql import pg, loop

from handlers.client.menu import Menu
from handlers.client.client import Client
from handlers.client.between_regions import ClientBetweenRegions
from handlers.client.between_towns import ClientBetweenTowns
from handlers.client.delivery import Delivery
from handlers.client.active_order import ActiveOrderClient
from handlers.client.new_order import NewOrderClient

from handlers.driver.menu import MenuDriver
from handlers.driver.driver import Driver
from handlers.driver.between_regions import DriverBetweenRegions
from handlers.driver.between_towns import DriverBetweenTowns
from handlers.driver.active_order import ActiveOrderDriver
from handlers.driver.personal_cabinet import PersonalCabinet
from handlers.driver.registration import RegistrationDriver
from handlers.driver.new_order import NewOrderDriver
from catching_errors.catch_errors import register_handlers_error

from handlers.admin.menu import MenuAdmin
from handlers.admin.mailing import Mailing
from aiohttp import web
from payme_api.handlers import post_requests
from click_api.requests import prepare_pay, complete_pay


app = web.Application()
app.router.add_post(path='/payme', handler=post_requests)
app.router.add_post(path='/prepare', handler=prepare_pay)
app.router.add_post(path='/complete', handler=complete_pay)


async def on_startup(dp):
    await pg.sql_start()
    print("бот вышел в онлайн")


#
menu = Menu()
client = Client()
client_between_regions = ClientBetweenRegions()
client_between_towns = ClientBetweenTowns()
delivery = Delivery()
order_client = NewOrderClient()
active_order_client = ActiveOrderClient()

menu_driver = MenuDriver()
driver = Driver()
driver_between_regions = DriverBetweenRegions()
driver_between_towns = DriverBetweenTowns()
active_order_driver = ActiveOrderDriver()
personal_cabinet = PersonalCabinet()
registration = RegistrationDriver()
order_driver = NewOrderDriver()

menu_admin = MenuAdmin()
mailing = Mailing()

# register_handlers
menu.register_handlers_client_menu(dp=dp)
client.register_handlers_client(dp=dp)
client_between_regions.register_handlers_client_between_regions(dp=dp)
client_between_towns.register_handlers_client_between_towns(dp=dp)
delivery.register_handlers_delivery(dp=dp)
active_order_client.register_handlers_active_order_client(dp=dp)
order_client.register_handlers_new_order_client(dp=dp)

menu_driver.register_handlers_driver_menu(dp=dp)
driver.register_handlers_driver(dp=dp)
driver_between_regions.register_handlers_driver_between_regions(dp=dp)
driver_between_towns.register_handlers_driver_between_towns(dp=dp)
active_order_driver.register_handlers_active_order_driver(dp=dp)
personal_cabinet.register_handlers_personal_cabinet(dp=dp)
registration.register_handlers_registration(dp=dp)
order_driver.register_handlers_new_order_driver(dp=dp)

menu_admin.register_handlers_menu_admin(dp=dp)
mailing.register_handlers_mailing(dp=dp)

# register_handlers_error(dp=dp)


if __name__ == "__main__":
    # asyncio.create_task(executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=on_startup))
    loop.run_until_complete(on_startup(dp=dp))
    loop.create_task(dp.start_polling())
    web.run_app(app=app, port=6000, loop=loop)
