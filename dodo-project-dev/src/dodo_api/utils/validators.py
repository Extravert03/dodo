from typing import Optional, Any

import pendulum
from pydantic.error_wrappers import ValidationError

from . import time_utils

__all__ = (
    'time_to_duration',
    'format_dt',
    'get_or_none',
    'to_lower',
    'to_datetime_without_seconds',
    'minutes_and_seconds_to_duration',
)


def time_to_duration(time_: pendulum.Time) -> pendulum.Duration:
    return pendulum.Duration(hours=time_.hour, minutes=time_.minute, seconds=time_.second)


def format_dt(dt_as_string: Optional[str]) -> Optional[pendulum.DateTime]:
    if isinstance(dt_as_string, str):
        if '+' in dt_as_string:
            return pendulum.DateTime.fromisoformat(dt_as_string)
        elif len(dt_as_string.split(':')) == 3:
            return pendulum.from_format(dt_as_string, 'DD.MM.YYYY HH:mm:ss', time_utils.MOSCOW_UTC)
        elif len(dt_as_string.split(':')) == 2:
            return pendulum.from_format(dt_as_string, 'DD.MM.YYYY HH:mm', time_utils.MOSCOW_UTC)


def get_or_none(value: Any) -> Optional[Any]:
    return value or None


def minutes_and_seconds_to_duration(minutes_and_seconds: str) -> pendulum.Duration:
    minutes, seconds = [int(i) for i in minutes_and_seconds.split(':')]
    return pendulum.Duration(minutes=minutes, seconds=seconds)


def to_datetime_without_seconds(value: str) -> pendulum.DateTime:
    return pendulum.from_format(value, 'DD.MM.YYYY HH:mm', time_utils.MOSCOW_UTC)


def to_lower(value: str) -> str:
    return value.lower()
