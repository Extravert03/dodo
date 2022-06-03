from typing import Union, Optional

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup

__all__ = (
    'SerializerResponse',
)

SerializerResponse = tuple[Optional[str], Optional[Union[InlineKeyboardMarkup,
                                                         ReplyKeyboardMarkup]]]
