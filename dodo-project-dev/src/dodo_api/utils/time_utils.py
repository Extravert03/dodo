import pendulum

__all__ = (
    'get_today_date',
    'get_week_ago_date',
    'MOSCOW_UTC',
)

MOSCOW_UTC = pendulum.timezone('Europe/Moscow')


def get_today_date() -> pendulum.date:
    return pendulum.now(MOSCOW_UTC).date()


def get_now_datetime() -> pendulum.DateTime:
    return pendulum.now(MOSCOW_UTC)


def get_week_ago_date() -> pendulum.date:
    return pendulum.now(MOSCOW_UTC).subtract(days=7).date()
