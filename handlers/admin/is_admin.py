from aiogram.dispatcher.filters import BoundFilter
from config import bot, chat_id_our, chat_id_common as chat_id
from aiogram import types
import typing


class IsAdmin(BoundFilter):
    async def check(self, message: typing.Union[types.Message, types.CallbackQuery]):
        status = (await bot.get_chat_member(user_id=message.from_user.id, chat_id=chat_id)).status
        if status in ["creator", "administrator"]:
            return True


class IsAdminOur(BoundFilter):
    async def check(self, message: typing.Union[types.Message, types.CallbackQuery]):
        status = (await bot.get_chat_member(user_id=message.from_user.id, chat_id=chat_id_our)).status
        if status in ["creator", "administrator"]:
            return True


class IsAdminReverse(BoundFilter):
    async def check(self, message: typing.Union[types.Message, types.CallbackQuery]):
        status = (await bot.get_chat_member(user_id=message.from_user.id, chat_id=chat_id)).status
        if status in ["member", "restricted"]:
            return True

