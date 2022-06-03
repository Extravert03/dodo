from typing import Union, Type

from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message, CallbackQuery

import db
from telegram_bot.utils.telegram_utils import get_message


class ForwardingReportsInChatFilter(BoundFilter):

    key = 'forwarding_reports_in_chat'

    async def check(self, query: Union[Message, CallbackQuery]) -> Union[dict, bool]:
        message = get_message(query)
        forwarding_reports = db.get_current_chat_forwarding_reports(message.chat.id)
        departments = [forwarding_report.department for forwarding_report in forwarding_reports]
        if not departments:
            return False
        return {'departments': departments}
