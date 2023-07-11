import pytz
from datetime import datetime
import dateutil.parser

tz = pytz.timezone("Asia/Tashkent")
form = "%m-%d-%Y %H:%M:%S.%f"


class Datetime:
    def now(self) -> datetime:
        datetime_now_offset = datetime.now(tz).strftime(form)
        return datetime.strptime(datetime_now_offset, form)

    def get_iso_time(self) -> datetime.isoformat:
        return self.now().isoformat()

    def get_from_iso_to_datetime(self, dtime_now: datetime.isoformat) -> datetime:
        return dateutil.parser.parse(dtime_now)

    def down_barrier(self) -> datetime:
        return datetime(year=dt_now.now().year, month=dt_now.now().month, day=dt_now.now().day, hour=0, minute=0,
                        second=0)

    def up_barrier_user(self) -> datetime:
        return datetime(year=dt_now.now().year, month=dt_now.now().month, day=dt_now.now().day, hour=23, minute=59,
                        second=0)

    def up_barrier_admin(self) -> datetime:
        return datetime(year=dt_now.now().year, month=dt_now.now().month, day=dt_now.now().day, hour=23, minute=59,
                        second=0)


dt_now = Datetime()
