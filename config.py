from aiogram import Bot
from aiogram import Dispatcher
from aiogram import types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from payme_api.models.connect_to_api_information import ApiKeys
from click_api.models.click_data import Click_Data

import logging

storage = RedisStorage2(db=1)
scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")
scheduler.start()

# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# logger = logging.getLogger(__name__)

video_driver_uz = "BAACAgIAAxkBAAN2Yx8niKvNrZKT3XxakOutuKKqYYEAAisiAAKK6fhI_z_WBiJw_HYpBA"
video_driver_ru = "BAACAgIAAxkBAAN3Yx8nkBru1hsJvUOBJzG81ikNyjUAAjAiAAKK6fhI6R1Kio0ZBIMpBA"

# chat_id_common = -1001687429388
# chat_id_common = -1001685856853 # new
chat_id_common = -1001687429388
chat_id_our = -1001767085919


PGUSER = "postgres"
PASSWORD = "karimov"
token = '5504892953:AAGlxgY9XhmDUl6vJBLIaNxirRI8CgYxA30'
ip = 'localhost'
# 5369594012:AAEtGuNadtUa8YN08JEy-2pUFKni1roax08 my
# 5504892953:AAGlxgY9XhmDUl6vJBLIaNxirRI8CgYxA30 Damir
# 5544196635:AAFpYaIV3BDJqfXegt0outNyRi9QUI76vTc main
bot = Bot(token=str(token), parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

# payme
payme_keys = ApiKeys(status=False,
                     testkey="wdJkt1n7Dn#ENb%VP%MzkRGEXR7OnXmyV1gD",
                     prod_key="A%Bth0oKPg&82PGM#aSdcsiij%Uh#vpXha2b",
                     payme_key=b"Paycom:A%Bth0oKPg&82PGM#aSdcsiij%Uh#vpXha2b",
                     merchant_id="6317b1f1dfcda2d1a53fb884",
                     payme_url="https://checkout.paycom.uz/")

# click
cli_data = Click_Data(service_id=25115, merchant_id=17595, secret_key="PFPf9nqpw6qXNW", merchant_user_id=28304)
