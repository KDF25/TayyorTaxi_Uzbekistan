from text.language.ru import Text_ru
from text.language.uzb import Text_uzb
from text.language.ozb import Text_ozb

RU = Text_ru()
UZB = Text_uzb()
OZB = Text_ozb()

class Text_main:

    choose_language = f"🇺🇿 Tilni tanlang 👇\n" \
                      f"🇷🇺 Выберите язык 👇\n" \
                      f"🇺🇿 Тилни танланг 👇\n"


    language = {"rus": RU, "uzb": UZB, "ozb": OZB}
    # language = {"rus": Text_ru, "uzb": Text_uzb, "ozb": Text_ozb}

    class menu:
        passenger = [RU.menu.passenger, UZB.menu.passenger, OZB.menu.passenger]
        delivery = [RU.menu.delivery, UZB.menu.delivery, OZB.menu.delivery]
        order = [RU.menu.order, UZB.menu.order, OZB.menu.order]
        information = [RU.menu.information, UZB.menu.information, OZB.menu.information]
        driver = [RU.menu.driver, UZB.menu.driver, OZB.menu.driver]
        settings = [RU.menu.settings, UZB.menu.settings, OZB.menu.settings]
        main_menu = [RU.menu.main_menu, UZB.menu.main_menu, OZB.menu.main_menu]
        online = [RU.menu.online, UZB.menu.online, OZB.menu.online]
        personal_cabinet = [RU.menu.personal_cabinet, UZB.menu.personal_cabinet, OZB.menu.personal_cabinet]
        change = [RU.menu.change, UZB.menu.change, OZB.menu.change]
    class option:
        da = [RU.buttons.common.da, UZB.buttons.common.da, OZB.buttons.common.da]
        no = [RU.buttons.common.no, UZB.buttons.common.no, OZB.buttons.common.no]

    class information:
        about_us = [RU.information.about_us, UZB.information.about_us, OZB.information.about_us]
        how_to_use = [RU.information.how_to_use2, UZB.information.how_to_use2, OZB.information.how_to_use2]
        feedback = [RU.information.feedback, UZB.information.feedback, OZB.information.feedback]

    class personal_cabinet:
        data = [RU.buttons.personal_cabinet.data.data, UZB.buttons.personal_cabinet.data.data,
                OZB.buttons.personal_cabinet.data.data]
        wallet = [RU.buttons.personal_cabinet.wallet.wallet, UZB.buttons.personal_cabinet.wallet.wallet,
                  OZB.buttons.personal_cabinet.wallet.wallet]

    class settings:
        rus = "🇷🇺 Ru"
        uzb = "🇺🇿 Уз (кир)"
        ozb = "🇺🇿 Uz (lat)"
        language = [rus, uzb, ozb]

    class money:
        class driver:
            min_price = 20000
            max_price = 250000
            price = [10000, 13000, 15000, 20000, 23000, 25000, 30000, 35000, 40000, 50000, 60000, 70000,
                            80000, 90000, 100000, 110000, 120000, 130000, 140000, 150000, 160000, 180000, 190000,
                            200000, 220000, 230000, 250000]

        class wallet:
            tax = 5000
            wallet = 100000
            price = [1000, 3000, 5000, 10000, 20000, 40000, 50000, 70000, 100000, 150000]

        class price:

            trip_price = {0: 0, 1: 30000, 2: 15000, 3: 15000}
            package_price = {0: 15000, 1: 20000, 2: 30000, 3: 25000, 4: 7000}
            package_way_price = {0: 0, 1: 30000, 2: 15000, 3: 15000}

            delivery = {1: 10, 17: 3, 30: 6, 43: 2, 59: 4, 73: 4, 83: 9, 95: 5, 111: 5,
                        126: 7, 137: 8, 155: 8, 166: 10, 185: 1}
            PRICE = package_price.values()

    class places:
        places = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']
        places_dict = {0: '0️⃣', 1: '1️⃣', 2: '2️⃣', 3: '3️⃣', 4:  '4️⃣'}

    class Admin:
        menu = 'Меню Администратора'
        mailing = 'Рассылка'