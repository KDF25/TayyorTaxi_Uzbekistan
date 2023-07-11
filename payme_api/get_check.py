import base64
from config import payme_keys
from pgsql import pg
from payme_api.models.insert_check_to_db import InsertCreatedCheck
from datetime_now.datetime_now import dt_now


class GetCheck:
    def __init__(self, amount: int, driver_id: int):
        self.amount = amount
        self.driver_id = driver_id

    async def return_url(self) -> str:
        string = await self._order_kind()
        string = base64.b64encode(bytes(string, "utf-8"))
        string = string.decode(encoding="utf-8")
        return payme_keys.payme_url + string

    async def _order_kind(self) -> str:
        return (f"m={payme_keys.merchant_id};"
                f"ac.order={await pg.select_pay_id(driver_id=self.driver_id, type_of_payment='Payme', status=False)};"
                f"a={self.amount * 100};")

    async def rec_check_to_database(self) -> InsertCreatedCheck:
        return InsertCreatedCheck(
            paycom_transaction_id="",
            paycom_time=str(int(dt_now.now().timestamp() * 1000)),
            paycom_time_datetime=dt_now.now(),
            create_time=0,
            perform_time=0,
            cancel_time=0,
            amount=self.amount * 100,
            state=0,
            reason=None,
            receivers=None,
            order_id=await pg.select_pay_id(driver_id=self.driver_id, type_of_payment='Payme', status=False))
