from typing import Optional

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from telegram_bot.utils.data_types import SerializerResponse

__all__ = (
    'BaseService',
)


class BaseService:

    def __init__(self, *, message: Optional[Message] = None,
                 callback_query: Optional[CallbackQuery] = None,
                 state: Optional[FSMContext] = None,
                 callback_data: Optional[dict] = None, **kwargs):
        self._message = message
        self._callback_query = callback_query
        self._state = state
        self._callback_data = callback_data
        self._kwargs = kwargs

    def validate(self):
        pass

    def get_text_and_markup(self) -> SerializerResponse:
        pass

    def _get_response_text(self) -> str:
        pass
