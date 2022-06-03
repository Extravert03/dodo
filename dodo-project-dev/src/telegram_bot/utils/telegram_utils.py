from typing import Union

from aiogram.types import Message, CallbackQuery


def get_message(query: Union[Message, CallbackQuery]) -> Message:
    """Extract aiogram.types.Message object from Message or Callback query.
    Helpful for handlers that handle both message handlers and callback handlers.

    Args:
        query: Message or Callback Query object.

    Returns:
        Message object.
    """
    if isinstance(query, CallbackQuery):
        query = query.message
    return query
