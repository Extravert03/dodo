from typing import Union

import pendulum

__all__ = (
    'format_time_in_seconds',
    'insert_gaps_between_chars',
    'format_percent',
    'replace_department_name_by_alias',
)


def format_percent(percent: Union[int, float, str]) -> str:
    percent = int(percent)
    percent_sign = '+' if percent > 0 else ''
    return f'{percent_sign}{percent}%'


def insert_gaps_between_chars(chars: Union[int, str], between_chars_no: int = 3) -> str:
    chars = str(chars)[::-1]
    result = ''
    for i, char in enumerate(chars, start=1):
        result += char
        if i % between_chars_no == 0:
            result += ' '
    return result[::-1].strip()


def format_time_in_seconds(seconds: int) -> str:
    duration = pendulum.Duration(seconds=seconds)
    if not duration.hours:
        return f'{duration.minutes:02}:{duration.remaining_seconds:02}'
    return f'{duration.hours:02}:{duration.minutes:02}:{duration.remaining_seconds:02}'


def replace_department_name_by_alias(text: str) -> str:
    replacing_map = {
        'вязьма': 'ВЗМ',
        'калуга': 'КЛ',
        'смоленск': 'СМ',
        'обнинск': 'ОБН',
        'москва': '',
        'подольск': 'П',
    }
    for replaceable, replace_to in replacing_map.items():
        text = text.replace(replaceable, replace_to).strip()
    return text


def estimate_revenue_increase_percent(today_revenue: int, revenue_week_before: int) -> int:
    """Estimate how many percents did revenue increased for
    compared to this time week before.

    Args:
        today_revenue: Revenue at current time.
        revenue_week_before: Obviously revenue week before.

    Returns:
        Difference percent. If revenue week before is 0, returns 0.

    Examples:
        >>> print(estimate_revenue_increase_percent(400, 500))
        -20
        >>> print(estimate_revenue_increase_percent(800, 500))
        60
        >>> print(estimate_revenue_increase_percent(800, 0))
        0

    """
    if revenue_week_before == 0:
        return 0
    return round(today_revenue * 100 / revenue_week_before) - 100


def estimate_customers_with_bonus_percent(customers_with_bonus: int,
                                          total_customers: int) -> int:
    if total_customers == 0:
        return 0
    return round(customers_with_bonus * 100 / total_customers)
