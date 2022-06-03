from typing import Optional, Union

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup

ReplyMarkup = Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]


class Response:

    def __init__(self, *, edit: bool = False):
        self.edit = edit

    def get_text(self) -> Optional[str]:
        pass

    def get_reply_markup(self) -> Optional[ReplyMarkup]:
        pass

    def get_chat_id(self) -> Optional[int]:
        pass

