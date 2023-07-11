from config import video_driver_uz

class Text_ozb:

    class greeting:
        main = "🚖 TayyorTaxi telegram botiga xush kelibsiz!\n\n" \
               "📍Bu yerda siz O‘zbekistonning istalgan nuqtasiga taksiga va pochta jo’natishga buyurtma berishingiz mumkin"
        hello = "Xush kelibsiz!"
        passenger = "🚖 Taxi"
        delivery = "📨 Pochta"
        driver = "🚕 Yo’ldaman"

    class video:
        client = "📲 Botdan foydalanish bo'yicha ko'rsatmalar"
        driver = "📲 Haydovchi uchun botdan foydalanish bo'yicha ko'rsatmalar"
        video_driver = video_driver_uz

    class menu:
        passenger = "🚖 Taksi buyurtmasi"
        delivery = "📨 Pochta jo’natish"
        order = "🗓 Faol buyurtmalar"
        information = "ℹ Ma'lumot"
        driver = "🙋 Men haydovchiman"
        settings = "⚙ Sozlamalar"
        main_menu = "🏠 Bosh sahifa"
        online = "🚕 Yo’ldaman"
        personal_cabinet = "🔑 Shaxsiy kabinet"
        change = "🔄 Yo'lovchi bo’lish"

    class symbol:
        sum = 'so’m'

    class information:
        about_us = "ℹ Xizmat haqida"
        how_to_use = "Qanday foydalaniladi"
        how_to_use2 = "❓ Qanday foydalaniladi"
        feedback = "☎ Aloqa"
        rules = "Xizmat ko'rsatish qoidalari"

    class feedback:
        feedback = "Quyidagi kontaktlar orqali biz bilan bog'lanishingiz mumkin👇\n\n" \
                   "Telegram: @tayyortaxi_aloqabot"

    class url:
        class client:
            about_us = "https://telegra.ph/Xizmat-haqida-06-29"
            how_to_use = "https://telegra.ph/Qanday-foydalaniladi-06-29"
        class driver:
            how_to_use = "https://telegra.ph/Qanday-foydalaniladi-06-29-2"
            about_us = "https://telegra.ph/Xizmat-haqida-06-29-2"
            rules = "https://telegra.ph/Xizmat-korsatish-shartlari-06-30"

    class buttons:
        class common:
            in_region = "Viloyat ichida"
            out_region = "Viloyatlararo"
            back = "⬅Ortga"
            cont = "➡Davom etish"
            order = "✅Buyurtma berish"
            phone = "📱Mening raqamim"
            trip = "Marshrut shartlari 👇"
            agree = "✅Tasdiqlash"
            yes = "✅To'g'ri"
            da = "✅Ha"
            no = "❌Yo'q"
            conditioner = "Konditsioner 👇"
        class passenger:
            date = "Ketish sanasi 👇"
            time = "Tahminiy ketish vaqti 👇"
            num = "Yo'lovchilar soni 👇"
            choose_more = "➡Yana tanlash"
            baggage = "Yuk o'lchamlari 👇"
        class delivery:
            package = "Yuk o'lchamlari 👇"
            date = "Jo’natish sanasi  👇"
            time = "Jo’natish vaqti  👇"
            find_more = "➡Yana qidirish"
        class driver:
            newRoute = "➕Yangi marshrut qo’shish"
            route_cancel = "❌Bekor qilish"
            price_change = "💵Narxni o’zgartirish"
            date = "Ketish sanasi 👇"
            free_places = "Bo’sh joylar 👇"
            accept = "✅Qabul qilish"
            reject = "❌Rad etish"
            no_order = "Buyurtma yo’q"
            passenger = "🚖 Taxi 👇"
            delivery = "📨 Pochta 👇"

        class cancel:
            client = "❌Buyurtmani bekor qilish"
            driver = "❌Bekor qilish"
            driver_ok = "❌Baribir bekor qilish"
        class personal_cabinet:
            class data:
                data = "✍Mening ma’lumotlarim"
                name = "Ismni o'zgartirish"
                phone = "Raqamni o'zgartirish"
                car = "Mashinani o’zgartirish"
            class wallet:
                wallet = "💳Balans"
                balance = "Balansni to‘ldirish"
                payme = "Payme"
                click = "Click"
                paynet = "Paynet"
                pay = "✅To’lash"

    class questions:
        share_number = f"Telefon raqamingizni yuboring👇\n"\
                       f"<b>«📱Mening raqamim»</b> tugmasini bosishingiz mumkin yoki " \
                       f"qo'lda kiritishingiz mumkin: +998 ** *** ** **"
        class passenger:
            from_region = "Qayerdan ketasiz? Hududni tanlang 👇"
            from_town = "Qayerdan ketasiz? Shaharni (tumanni) tanlang 👇"
            to_region = "Qayoqqa ketyapsiz? Hududni tanlang 👇"
            to_town = "Qayoqqa ketyapsiz? Shaharni (tumanni) tanlang 👇"
            number_baggage = "Yo'lovchilar soni va yuk o'lchamlarini belgilang 👇"
            date = "🗓Ketish sanasi 👇"
            time = "⏰Taxminiy yo’lga chiqish vaqti 👇\n<i>Siz bir nechtasini belgilashingiz mumkin</i>"
            trip = "Marshrut shartingizni tanlang 👇"
            auto = "Avtomobil modelini tanlang 👇"
            car = "Quyidagilardan tanlang👇"
            phone = f"Telefon raqamingizni yuboring👇\n"\
                       f"<b>«📱Mening raqamim»</b> tugmasini bosishingiz mumkin yoki " \
                       f"qo'lda kiritishingiz mumkin: +998 ** *** ** **"

        class delivery:
            from_region = "Siz pochtani qayerdan yuborasiz? Hududni tanlang 👇"
            from_town = "Shaharni (tumanni) tanlang 👇"
            to_region = "Pochtani qayoqqa yuborasiz? Hududni tanlang👇"
            to_town = "Shaharni (tumanni) tanlang 👇"
            package = "Yuk o’lchamlarini tanlang 👇"
            date = "🗓Jo’natish sanasi 👇"
            time = "⏰Taxminiy jo’natish vaqti 👇\n<i>Siz bir nechtasini belgilashingiz mumkin</i>"
            trip = "Marshrut shartingizni tanlang 👇"

        class driver:
            from_region = "Qayerdan ketasiz? Hududni tanlang 👇"
            from_town = "Qayerdan yo’lovchilarni olib ketishingiz mumkin? 👇\n<i>3️⃣ tagacha tanlashingiz mumkin</i>"
            to_region = "Qayoqqa ketyapsiz? Hududni tanlang 👇"
            to_town = "Qayoqqa yo’lovchilarni oborishingiz mumkin 👇\n<i>3️⃣ tagacha tanlashingiz mumkin</i>"
            towns = "Yo’lingiz marshrutini belgilang, 2️⃣ ta shahar (tuman) tanlang👇"
            route_cancel = "Yangi marshrut yaratish uchun mavjudni bekor qiling👇"
            sure = "Haqiqatan ham faoliyatingizni bekor qilmoqchimisiz? " \
                   "Bu marshrutda endi yangi buyurtmalarni olmaysiz."
            route = "Qaysi marshrut bilan ketyapsiz? 👇"
            out_region = "<b>Qaysi yo'nalishlarda yurasiz?</b>\n\n2 ta hududni tanlang 👇"
            in_region = "<b>Qaysi hududda qatnaysiz?</b>\n\nHududni tanlang 👇"
            cond = "Avtomobilda konditsioner bormi? 👇"
            price = "Pitakdan pitakgacha 1️⃣ nafar yo'lovchi narxini belgilang 👇\n\n" \
                    "<i>❗Yodda tutingki, narx qancha past boʻlsa, yo’lovchini roʻyxatda shuncha yuqori boʻlasiz</i>"
            change = "Haqiqatan ham yo‘lovchi bo‘lmoqchimisiz?\n\nSizning ma'lumotlaringiz saqlanadi"
        class registration:
            name = "Ismingizni kiriting, uni yo’lovchilar ko’radi"
            phone = "Siz bilan bog'lanish uchun telefon raqamingizni yuboring 👇"
            auto = "Avtomobilingiz modelini tanlang 👇"
            agreement = "Hammasi to'g'rimi? 👇\n\n<b>«✅To'g'ri»</b>, tugmasini bosish orqali siz xizmat ko'rsatish " \
                        "shartlari bilan tanishganingizni va roziligingizni tasdiqlaysiz - 👉"


    class chain:
        class passenger:
            from_place = "Qayerdan"
            to_place = "Qayoqqa"
            date = "Ketish sanasi"
            time = "Ketish vaqti"
            num = "Yo'lovchilar soni"
            baggage = "Yuk"
            phone = "Telefon"

            car_find1 = "Siz uchun "
            car_find2 = "ta mashina mavjud"
            car_not_found = "Afsuski, bu yo'nalishdagi avtomobillar hozirda topilmadi, keyinroq qayta urinib ko'ring."
            car = "Model"
            car_info = "50 000 - цена за 1 пассажира\n💺 3/4 - свободно мест 1\n✅❄ - кондиционер есть"

            driver = "Haydovchi"
            places = "Bo’sh joylar"
            conditioner = "Konditsioner"
            price = "1 yo'lovchi uchun narx"
            info = "Sizning ma'lumotlaringiz"

            cost1 = "Umumiy"
            cost2 = "yo’lovchiga"
            trip = "<i>*narx pitakdan pitakgacha ko’rsatilgan</i>"

        class delivery:
            info = "Sizning ma'lumotlaringiz"
            driver = "Haydovchi"
            phone = "Telefon"
            from_place = "Qayerdan"
            to_place = "Qayoqqa"
            date = "Jo’natish sanasi"
            time = "Jo’natish vaqti"
            baggage = "Yuk"
            car = "Model"
            price = "Yetkazib berish narxi"
            cost = "Yetkazib berish narxi"
            trip = "<i>*narx pitakdan pitakgacha ko’rsatilgan</i>"

        class driver:
            allRoute = "Sizning faol marshrutlaringiz 👇"
            route = "Marshrut"
            from_place = "Qayerdan"
            to_place = "Qayoqqa"
            date = "Ketish sanasi"
            places = "Bo’sh joylar"
            price = "1 yo'lovchi uchun narx"
            price2 = "1 yo'lovchi"
            pyatak = "pyatak"
            conditioner = "Konditsioner"
            alright = "Hammasi to'g'rimi?"
            onepass = "1 yo'l."
            name = "Ismingiz"
            phone = "Telefon"
            car = "Mashina"

        class personal_cabinet:
            change_name = "Ismni o'zgartirish"
            change_phone = "Raqamni o'zgartirish"
            change_car = "Mashinani o’zgartirish"
            change_param = {'name': change_name, 'phone': change_phone, "car": change_car}
            new_data = "Yangi ma’lumotni kiriting 👇"
            new_data_rec = "Ma’lumot o’zgartirildi."
            payment = "To'ldirish miqdorini belgilang 👇"
            pay_way = "To’lov turini tanlang 👇"
            amount = "To’lov miqdori"

            pay_way2 = "To’lov orqali"
            amount2 = "To’lov miqdori"
            payment2 = '<i>To’lov o’tqazish uchun </i> <b>«✅To’lash»</b> tugmasini bosing 👇'
            accept = '✅To’lov o’tqazildi\n\nBalansingizga kiritilgan miqdor'

    class order:
        active_orders = '<i>Buyurtmangiz holatini <b>«🗓 Faol Buyurtmalar»</b> sahifasida kuzatishingiz mumkin</i>'

        class client:
            passenger = f"Ariza haydovchiga jo’natildi, tasdiqlangandan so’ng sizga bildirishnoma keladi.\n\n" \
                        f"<b>Siz bir nechta haydovchilarga ariza yuborishingiz mumkin, " \
                        f"arizani birinchi bo'lib qabul qilgan kishi bilan yo’lga chiqasiz.</b>\n\n" \
                        f"Yana tanlaysizmi?"
            delivery = f"Buyurtma haydovchilarga jo’natildi, qabul qilingandan so'ng sizga xabarnoma keladi"
            accept = "✅Ariza haydovchi tomonidan qabul qilindi\n📲Haydovchi siz bilan telefon orqali bog'lanadi"
            reject = '❌ Ariza haydovchi tomonidan rad etildi\n\n' \
                     'Boshqa haydovchini tanlashingiz mumkin👇'

        class driver:
            driver = f'✅ Sizning arizangiz qabul qilindi. Yo’lovchilar javob berishlari bilan siz xabarnoma olasiz.\n\n' \
                     f'<i>Buyurtmalar holatini <b>«🗓 Faol Buyurtmalar»</b> sahifasida kuzatishingiz mumkin</i> 👇'
            route_cancel = "❌ Faoliyat bekor qilindi, mijozlar sizni boshqa haydovchilar roʻyxatida koʻrmaydi.\n\n" \
                           "❕Yo'lovchilar uchun yana faol boʻlish uchun <b>«🚕 Yo’ldaman»</b> tugmasini bosing."
            order = "Buyurtma va mijoz ma'lumotlarini olish uchun <b>«✅Qabul qilish»</b> tugmasini bosing."
            order_cost1 = 'Xizmat narxi'
            order_cost2 = "<b>so'mni</b> tashkil etadi, mablag' balansingizdan yechib olinadi."
            accept = "✅ Ariza qabul qilindi, yo’lovchiga buyurtma qabul qilinganligi haqida xabar berdik"
            reject = '❌ Ariza rad etildi'
            info = "Yo’lovchini maʼlumotlari"
            phone_client = "Telefon"
            new_order = "Yangi buyurtma"
            passenger = "🚖 Taxi"
            delivery = "📨 Pochta"
            type_order = {"passenger": passenger, "delivery": delivery}

    class active_order:
        no_active_order = "Sizda hozirda hech qanday faol buyurtma yo‘q"
        class client:
            car_full = "✅ Avtomobil saloni muvaffaqiyatli to'ldirildi"
            driver_call = "📲 Haydovchi siz bilan telefon orqali bog'lanadi"
        class driver:
            places = "❗ Yo’lovchilar mashinadagi bo’sh joylarni ko’rishadi\n\n" \
                     "<i>Mavjud bo’sh joyni «➖» va «➕» orqali o’zgartirishingiz mumkin</i> 👇"
            date = 'Sanani tanlang 👇'
            place = 'Yo’nalishni tanlang 👇'
            cancel_order = "Bekor qilindi"
            cancel_trip = "Bekor qilindi"
            client_info = 'Yo’lovchini maʼlumotlari'

    class cancel:
        class client:
            cancel_question_order = "Buyurtmani bekor qilmoqchimisiz? Bu harakatni qaytarib bo'lmaydi."
            cancel_order = "❌ Buyurtma bekor qilindi."
            delivery = "❌ Afsuski, bo’sh mashina topilmadi\n\nIltimos keyinroq qayta urinib ko'ring"
            class driver:
                delete = "❌ Afsuski, haydovchi arizani bekor qildi"
                cancel = "❌ Ariza haydovchi tomonidan rad etildi"
                new_driver = "Boshqa haydovchi tanlashingiz mumkin 👇"

        class driver:
            passenger = "❌Yo’lovchi arizani bekor qildi, mablag' hamyoningizga qaytariladi"
            delivery = '❌Mijoz arizani bekor qildi, mablagʻhamyoningizga qaytdi'
            driver = "Ishonchingiz komilmi? Agar buyurtma haydovchi tomonidan bekor qilinsa mablag' " \
                     "balansingizga qaytarilmaydi"

    class personal_cabinet:
        name = "Ismingiz"
        phone = "Telefon"
        car = "Mashina"
        id = "ID"
        wallet = "Balans"
        common = "Asosiy"
        bonus = "Bonus"
        congratulation = "Tabriklaymiz! Xizmatda roʻyxatdan oʻtganingiz uchun sizga 💵 <b>100 000</b> soʻm bonus berildi\n\n" \
                         "<b>❕Bonusdan foydalanish muddati - 20 kun</b>\n\n" \
                         "Avval ma’lumotni ko’rib chiqing 👇"
        online = "Yo’lovchi buyurtmalarini qabul qilishni boshlash uchun «🚕 Yo’ldaman» tugmasini bosing👇"

    class alert:
        class phone:
            alert = "Qayta urinib ko'ring 😅"

        class passenger:
            zeroTown = "Afsuski siz belgilagan marshrutda hozirgi paytda haydovchilar topilmadi"

        class driver:
            zeroTowns = "Shaharlarni belgilang"
            fourthTown = "3️⃣ shaharni tanlashingiz mumkin"
            check = "Siz avval ushbu sana va yo'nalish uchun buyurtma yaratgansiz"
            town = "❗ 10 ta gacha tanlash mumkin"
            accept_order_late = "❌ Murojaat boshqa haydovchi tomonidan qabul qilinganligi yoki arizaga " \
                                "sizning tarafingizdan uzoq javob berilganligi sababli avtomatik rad etilgan"
            places_now = "Endi mashinada"
            places_free = "bo’sh joy"
            places_error =  "4 ta joydan ortiq bo’sh joy yo’q"
            places_error2 = "Qolgan joylar mavjud bo’lgan yo'lovchilar bilan band, joy bo’shatish uchun aynan" \
                            " yo’lovchiniga bosib uni o’chirib tashlang👇"
            places_error3 = "❗ Salonizda yetarli joy mavjud emas"
            places_full = "Mashina to'lgan, biz yo'lovchilarga xabarnoma yubordik"
            insufficient_funds = "Balansingizda mablag‘ingiz yetarli emas, balansingizni to‘ldiring." \
                                 "🔑 Shaxsiy kabinet —> 💳 Balans —> Balansni to‘ldirish"
            insufficient_funds2 = "🔔 Eslatma!\n\n" \
                                 "Keyingi buyurtmani qabul qilish uchun balansingizda yetarli mablag‘ yo‘q, " \
                                 "faol bo‘lish uchun balansingizni to‘ldiring"
            prolongation = "❗ Sizning faoliyatingiz bugun soat 00:00 da tugaydi mijozlar sizni haydovchilar " \
                           "ro'yxatida boshqa ko'rolmaydi\n\n" \
                           "Қайта фаол бўлиш учун <b>«🚕 Йўлдаман»</b> тугмасини босинг 👇"
    # main text

    class option:
        yes = "Bo’r"
        no = "Yo’q"
        da = "Ha"
        option = {0: no, 1:yes}


    class baggage:
        gab1 = "🧰25х15 sм"
        gab2 = "🧰30х20 sм"
        gab3 = "🧰55х35 sм"
        gab4 = "🧰40х25 sм"
        gab5 = "✉ Hujjat"
        delivery = [gab1, gab2, gab3, gab4, gab5]
        package_gab = {0: gab1, 1: gab2, 2: gab3, 3: gab4, 4: gab5}

    class mailing:
        class left_days:
            text1 = "🔔 Eslatma! Sizda"
            text2 = " bonus bor.\n❗ Bonus mablag'lari tugashiga"
            text3 = "<b>kun</b> qoldi!\n<b>Tugash sanasi</b>"
            text4 = ", 23:59 da"

    class quiz:
        main = "Ayni paytda Paynet orqali to‘lov ulanmagan.\n\n" \
               "<b>Paynet orqali hamyoningizni to'ldirish sizga qulayroq bo'ladimi?</b>👇"
        thanks = "Ma'lumot uchun rahmat, tez orada ushbu to'lov usulini qo'shamiz."
        yes = "✅ Ha, qulayroq"


    thanks = "Здесь могла быть ваша реклама"


    text_none = "текст"