import config
from db import redis_db
from dodo_api import serializers
from dodo_api.services import CanceledOrders, CanceledOrderByUUID
from dodo_api.utils import time_utils
from utils import logger

accounts = [
    ('shift_manager_p_1', 'подольск-1'),
    ('shift_manager_p_2', 'подольск-2'),
    ('shift_manager_msk_4_1', 'москва 4-1'),
    ('shift_manager_msk_4_2', 'москва 4-2'),
    ('shift_manager_msk_4_3', 'москва 4-3'),
    ('shift_manager_msk_4_4', 'москва 4-4'),
    ('shift_manager_msk_4_5', 'москва 4-5'),
    ('shift_manager_msk_4_6', 'москва 4-6'),
    ('shift_manager_msk_4_7', 'москва 4-7'),
    ('shift_manager_msk_4_8', 'москва 4-8'),
    ('shift_manager_msk_4_10', 'москва 4-10'),
    ('shift_manager_msk_4_11', 'москва 4-11'),
    ('shift_manager_msk_4_12', 'москва 4-12'),
    ('shift_manager_msk_4_13', 'москва 4-13'),
    ('shift_manager_msk_4_14', 'москва 4-14'),
    ('shift_manager_msk_4_15', 'москва 4-15'),
    ('shift_manager_msk_4_17', 'москва 4-17'),
    ('shift_manager_msk_4_18', 'москва 4-18'),
    ('shift_manager_msk_4_19', 'москва 4-19'),
    ('shift_manager_msk_4_20', 'москва 4-20'),
    ('shift_manager_msk_4_21', 'москва 4-21'),
    ('shift_manager_smolensk_1', 'смоленск-1'),
    ('shift_manager_smolensk_2', 'смоленск-2'),
    ('shift_manager_smolensk_3', 'смоленск-3'),
    ('shift_manager_obninsk', 'обнинск'),
    ('shift_manager_vyazma', 'вязьма-1'),
    ('shift_manager_kaluga_1', 'калуга-1'),
    ('shift_manager_kaluga_2', 'калуга-2'),
]


async def get_canceled_orders_list(cookies: dict) -> list[dict]:
    today = time_utils.get_now_datetime().to_date_string()
    return await CanceledOrders(cookies, today).get_data()


async def update_canceled_orders():
    for account_name, department_name in accounts:
        cookies = redis_db.get_cookies(account_name)
        canceled_orders = await get_canceled_orders_list(cookies)
        for canceled_order in canceled_orders:
            if redis_db.is_canceled_order_uuid_in_db(canceled_order['order_uuid']):
                continue
            canceled_order_by_uuid = await CanceledOrderByUUID(
                cookies, canceled_order['order_uuid'], canceled_order['order_price'],
                canceled_order['order_type']).get_data()
            if canceled_order_by_uuid.receipt_printed_at is None:
                continue
            logger.debug(f'new canceled order with uuid: {canceled_order_by_uuid.order_uuid}')
            serializer = serializers.CanceledOrderReportSerializer(canceled_order_by_uuid)
            redis_db.add_report_notification_to_queue(serializer.as_json())
            redis_db.add_canceled_order_uuid(canceled_order_by_uuid.order_uuid)
