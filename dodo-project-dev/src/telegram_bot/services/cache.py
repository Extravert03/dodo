import json
from typing import Iterable, NamedTuple

from db import redis_db
from db.exceptions import CachedObjectExpiredOrMissing
from dodo_api.models import OperationalStatisticsForTodayAndWeekBefore


class CachedRevenuesResult(NamedTuple):
    cached_revenues: Iterable[OperationalStatisticsForTodayAndWeekBefore]
    missing_in_cache_department_ids: Iterable[int]


def cache_daily_revenue_in_redis(
        revenue_reports: Iterable[OperationalStatisticsForTodayAndWeekBefore]
) -> Iterable[int]:
    cached_department_ids = []
    for revenue_report in revenue_reports:
        json_string = json.dumps(revenue_report.dict(by_alias=True), default=str)
        is_set = redis_db.set_to_cache(f'revenue_report_{revenue_report.unit_id}', json_string)
        if is_set:
            cached_department_ids.append(revenue_report.unit_id)
    return cached_department_ids


def get_daily_revenue_from_cache(
        department_ids: Iterable[int]
) -> CachedRevenuesResult:
    """Get revenue statistics from cache (redis).

    Args:
        department_ids: collection of department IDs.

    Returns:
        Named tuple that contains two list.
        First one contains revenue statistics that were found in redis.
        Second one contains department IDs if revenue statistics that weren't found in redis.
    """
    cached_revenues = []
    missing_in_cache = []
    for department_id in department_ids:
        try:
            cached = redis_db.get_from_cache(f'revenue_report_{department_id}')
        except CachedObjectExpiredOrMissing:
            missing_in_cache.append(department_id)
        else:
            cached_revenues.append(OperationalStatisticsForTodayAndWeekBefore.parse_raw(cached))
    return CachedRevenuesResult(cached_revenues=cached_revenues,
                                missing_in_cache_department_ids=missing_in_cache)
