import json
from typing import Iterable

from redis import Redis

from db.exceptions import CachedObjectExpiredOrMissing, CookiesDoNotExist

_redis = Redis(host='localhost', port=6379, db=0, decode_responses=True)


def get_cookies_lifetime(account_name_alias: str) -> int:
    return _redis.ttl(account_name_alias)


def get_cookies(account_name: str) -> dict:
    """Get cookies from redis.

    Args:
        account_name: Name of account.

    Returns:
        Cookies as dict.

    Raises:
        CookiesDoNotExist error if cookies not found in redis.
    """
    cookies = _redis.hgetall(account_name)
    if not cookies:
        raise CookiesDoNotExist
    return cookies


def get_canceled_orders_uuids() -> set[str]:
    return _redis.smembers('canceled-orders-uuids')


def is_canceled_order_uuid_in_db(uuid: str) -> bool:
    return _redis.sismember('canceled-orders-uuids', uuid)


def add_canceled_order_uuid(uuid: str) -> int:
    return _redis.sadd('canceled-orders-uuids', uuid)


def add_report_notification_to_queue(report_notification_as_json: str):
    _redis.sadd('report-notifications-queue', report_notification_as_json)


def get_report_notification_from_queue() -> str:
    return _redis.spop('report-notifications-queue')


def set_to_cache(name: str, json_string: str) -> bool:
    is_set = _redis.set(name, json_string)
    _redis.expire(name, 60)
    return is_set


def get_from_cache(name: str) -> str:
    cached = _redis.get(name)
    if cached is None:
        raise CachedObjectExpiredOrMissing
    return cached


def add_detailed_delivery_statistics_request(chat_id: int, department_ids: Iterable[int]):
    json_string = json.dumps({'chat_id': chat_id, 'department_ids': department_ids})
    _redis.sadd('detailed-delivery-statistics-request', json_string)
