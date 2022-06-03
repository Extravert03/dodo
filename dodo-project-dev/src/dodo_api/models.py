from enum import Enum
from typing import Optional
from datetime import datetime

import pendulum
from pydantic import BaseModel, validator, Field

from .utils import validators

__all__ = (
    'CanceledOrderReport',
    'SectorStopSaleReport',
    'PizzeriaStopSaleReport',
    'StreetStopSaleReport',
    'DeliveryStatisticsRow',
    'IngredientStopSaleReport',
    'StopSaleReportType',
    'DeliveryStatistics',
    'BeingLateCertificate',
    'Department',
    'OperationalStatisticsForTodayAndWeekBefore',
    'OperationalStatistics',
)


class CanceledOrderReport(BaseModel):
    department: str
    order_created_at: Optional[pendulum.DateTime]
    receipt_printed_at: Optional[pendulum.DateTime]
    order_no: str
    order_type: str
    order_price: int
    order_uuid: str

    _to_lower = validator(
        'department',
        allow_reuse=True,
    )(validators.to_lower)

    _str_to_aware_datetime = validator(
        'receipt_printed_at',
        'order_created_at',
        pre=True,
        allow_reuse=True,
    )(validators.format_dt)

    _replace_empty_objects_with_none = validator(
        'receipt_printed_at',
        allow_reuse=True
    )(validators.get_or_none)


class DeliveryStatisticsRow(BaseModel):
    department: str
    total_average_time: pendulum.Duration
    average_cooking_time: pendulum.Duration
    average_awaiting_on_heat_shelf_time: pendulum.Duration
    average_delivery_time: pendulum.Duration

    _to_lower = validator(
        'department',
        allow_reuse=True,
    )(validators.to_lower)

    _time_to_duration = validator(
        'total_average_time',
        'average_cooking_time',
        'average_awaiting_on_heat_shelf_time',
        'average_delivery_time',
        pre=True,
        allow_reuse=True,
    )(validators.time_to_duration)


class DeliveryStatistics(BaseModel):
    deliveries_amount_per_hour: float
    increase_over_week_ago: int
    awaiting_orders_amount: int
    couriers_total_amount: int
    couriers_in_queue_amount: int
    delivery_awaiting_time: pendulum.Duration

    _minutes_and_seconds_to_duration = validator(
        'delivery_awaiting_time',
        pre=True,
        allow_reuse=True,
    )(validators.minutes_and_seconds_to_duration)


class KitchenStatistics(BaseModel):
    revenue_per_hour: int
    revenue_increase_over_week_ago: int
    products_spending_per_hour: float
    products_spending_increase_over_week_ago: int
    average_cooking_time: pendulum.Duration
    postponed: int
    in_queue: int
    in_work: int

    _minutes_and_seconds_to_duration = validator(
        'average_cooking_time',
        pre=True,
        allow_reuse=True,
    )(validators.minutes_and_seconds_to_duration)


class Department(BaseModel):
    unit_id: int
    name: str

    _to_lower = validator(
        'name',
        allow_reuse=True,
    )(validators.to_lower)


class BeingLateCertificate(BaseModel):
    department: str
    datetime: pendulum.DateTime
    order_no: str
    approximately_delivery_time: str
    courier_mark_at: str
    delivery_deadline: str
    certificate_type: str
    given_by: str

    _to_lower = validator(
        'department',
        allow_reuse=True,
    )(validators.to_lower)

    _to_datetime_with_seconds = validator(
        'datetime',
        pre=True,
        allow_reuse=True,
    )(validators.format_dt)


class StopSaleReportType(Enum):
    PIZZERIA = 'pizzeria'
    SECTOR = 'sector'
    STREET = 'street'
    INGREDIENT = 'ingredient'


class PizzeriaStopSaleReport(BaseModel):
    department: str
    sale_type: str
    stop_reason: str
    stopped_at: pendulum.DateTime
    stopper_name: str
    renewer_name: Optional[str]
    stop_type: str

    _set_renewer_name_as_none = validator(
        'renewer_name',
        allow_reuse=True,
    )(validators.get_or_none)

    _parse_stopped_at_dt = validator(
        'stopped_at',
        pre=True,
        allow_reuse=True,
    )(validators.format_dt)


class StreetStopSaleReport(BaseModel):
    department: str
    sector: str
    street: str
    stopped_at: pendulum.DateTime
    stopper_name: str
    renewer_name: Optional[str]

    _set_renewer_name_as_none = validator(
        'renewer_name',
        allow_reuse=True,
    )(validators.get_or_none)

    _parse_stopped_at_dt = validator(
        'stopped_at',
        pre=True,
        allow_reuse=True,
    )(validators.format_dt)


class SectorStopSaleReport(BaseModel):
    department: str
    sector: str
    stopped_at: pendulum.DateTime
    stopper_name: str
    renewer_name: Optional[str]

    _to_lower = validator(
        'department',
        allow_reuse=True,
    )(validators.to_lower)

    _set_renewer_name_as_none = validator(
        'renewer_name',
        allow_reuse=True,
    )(validators.get_or_none)

    _parse_stopped_at_dt = validator(
        'stopped_at',
        pre=True,
        allow_reuse=True,
    )(validators.format_dt)


class IngredientStopSaleReport(BaseModel):
    department: str
    ingredient: str
    stop_reason: str
    stopped_at: pendulum.DateTime
    stopper_name: str
    renewer_name: Optional[str]

    _to_lower = validator(
        'department',
        allow_reuse=True,
    )(validators.to_lower)

    _set_renewer_name_as_none = validator(
        'renewer_name',
        allow_reuse=True,
    )(validators.get_or_none)

    _parse_stopped_at_dt = validator(
        'stopped_at',
        pre=True,
        allow_reuse=True,
    )(validators.format_dt)


class OperationalStatistics(BaseModel):
    stationary_revenue: int = Field(..., alias='stationaryRevenue')
    stationary_order_count: int = Field(..., alias='stationaryOrderCount')
    delivery_revenue: int = Field(..., alias='deliveryRevenue')
    delivery_order_count: int = Field(..., alias='deliveryOrderCount')
    revenue: int = Field(..., alias='revenue')
    order_count: int = Field(..., alias='orderCount')
    avg_check: float = Field(..., alias='avgCheck')


class OperationalStatisticsForTodayAndWeekBefore(BaseModel):
    unit_id: int = Field(..., alias='unitId')
    date: pendulum.DateTime
    today: OperationalStatistics
    week_before: OperationalStatistics = Field(..., alias='weekBefore')
    yesterday_to_this_time: OperationalStatistics = Field(..., alias='yesterdayToThisTime')
    yesterday: OperationalStatistics = Field(..., alias='yesterday')
    week_before_to_this_time: OperationalStatistics = Field(..., alias='weekBeforeToThisTime')

    class Config:
        allow_population_by_field_name = True


# deprecated
class IngredientStopSale(BaseModel):
    sale_point_digital_system_id: int
    sale_point_name: str
    product: str
    employee: str
    date: str
    action: str

    _to_lower = validator(
        'sale_point_name',
        allow_reuse=True,
    )(validators.to_lower)


class Order(BaseModel):
    department: str
    datetime: datetime
    no: str
    type: str
    customer_name: str
    customer_phone_number: str
    price: int
    payment_method: str
    order_status: str
    accepted_by_employee: str

    @validator('datetime', pre=True)
    def format_datetime(cls, value: str) -> datetime:
        return datetime.strptime(value, '%d.%m.%Y %H:%M')
