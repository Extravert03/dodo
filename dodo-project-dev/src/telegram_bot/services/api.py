import asyncio
from typing import Iterable, Tuple, List

import httpx

from dodo_api.services import RevenueStatistics, BeingLateCertificates
from dodo_api.models import OperationalStatisticsForTodayAndWeekBefore, BeingLateCertificate
from dodo_api.utils import time_utils
from telegram_bot.utils.exceptions import DodoPublicAPIError


async def get_revenue_statistics(
        department_ids: Iterable[int]
) -> tuple[OperationalStatisticsForTodayAndWeekBefore, ...]:
    """Get revenue statistics from https://publicapi.dodois.io/index.html.

    Args:
        department_ids: Collection of department IDs.

    Returns:
        Tuple containing revenue statistics for today and week before of each department.

    Raises:
        DodoPublicAPIError: If any http error occurs.
    """
    try:
        tasks = (RevenueStatistics(department_id).get_data() for department_id in department_ids)
        return await asyncio.gather(*tasks)
    except httpx.HTTPError:
        raise DodoPublicAPIError


async def get_being_late_certificates(
        cookies: dict, department_ids: Iterable[int]
) -> tuple[list[BeingLateCertificate], list[BeingLateCertificate]]:
    today_date = time_utils.get_now_datetime().format('DD.MM.YYYY')
    week_before_date = time_utils.get_now_datetime().subtract(days=7).format('DD.MM.YYYY')
    try:
        today_certificates = await BeingLateCertificates(
            cookies, department_ids, today_date, today_date).get_data()
        week_before_certificates = await BeingLateCertificates(
            cookies, department_ids, week_before_date, week_before_date).get_data()
    except httpx.HTTPError:
        raise DodoPublicAPIError
    return today_certificates, week_before_certificates
