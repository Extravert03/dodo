from datetime import datetime

from peewee import (
    Model,
    CharField,
    BigIntegerField,
    ForeignKeyField,
    IntegerField,
    FloatField,
    DateTimeField,
)

from db.sql_db.engine import db_engine

__all__ = (
    'ReportType',
    'DepartmentRegion',
    'Department',
    'RevenueStatistics',
    'DetailedDeliveryStatistics',
    'BeingLateCertificatesStatistics',
    'KitchenStatistics',
    'DeliveryStatistics',
    'TelegramChat',
    'ForwardingReport',
    'OrdersStatistics',
)


class BaseModel(Model):
    class Meta:
        database = db_engine


class DepartmentRegion(BaseModel):
    name = CharField(unique=True, index=True)

    class Meta:
        table_name = 'department_regions'


class Department(BaseModel):
    id = IntegerField(primary_key=True, index=True, unique=True)
    name = CharField(unique=True, index=True)
    account_name = CharField(index=True)
    region = ForeignKeyField(DepartmentRegion, on_delete='CASCADE')

    class Meta:
        table_name = 'departments'


class KitchenStatistics(BaseModel):
    department = ForeignKeyField(Department, on_delete='CASCADE')
    revenue_per_hour = IntegerField(default=0)
    revenue_increase_over_week_ago = IntegerField(default=0)
    products_spending_per_hour = FloatField(default=0)
    products_spending_increase_over_week_ago = IntegerField(default=0)
    average_cooking_time = IntegerField(default=0)
    postponed = IntegerField(default=0)
    in_queue = IntegerField(default=0)
    in_work = IntegerField(default=0)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'kitchen_statistics'


class DeliveryStatistics(BaseModel):
    department = ForeignKeyField(Department, on_delete='CASCADE')
    deliveries_amount_per_hour = FloatField(default=0)
    increase_over_week_ago = IntegerField(default=0)
    awaiting_orders_amount = IntegerField(default=0)
    couriers_total_amount = IntegerField(default=0)
    couriers_in_queue_amount = IntegerField(default=0)
    delivery_awaiting_time = IntegerField(default=0)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'delivery_statistics'


class RevenueStatistics(BaseModel):
    department = ForeignKeyField(Department, on_delete='CASCADE')
    daily_revenue = IntegerField(default=0)
    increase_over_week_ago = IntegerField(default=0)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'revenue_statistics'


class OrdersStatistics(BaseModel):
    department = ForeignKeyField(Department, on_delete='CASCADE')
    customers_with_bonus = IntegerField(default=0)
    total_customers = IntegerField(default=0)

    class Meta:
        table_name = 'orders_statistics'


class DetailedDeliveryStatistics(BaseModel):
    department = ForeignKeyField(Department, on_delete='CASCADE')
    total_average_time = IntegerField(default=0)
    average_cooking_time = IntegerField(default=0)
    average_awaiting_on_heat_shelf_time = IntegerField(default=0)
    average_delivery_time = IntegerField(default=0)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'detailed_delivery_statistics'


class BeingLateCertificatesStatistics(BaseModel):
    department = ForeignKeyField(Department, on_delete='CASCADE')
    daily_amount = IntegerField(default=0)
    amount_week_ago = IntegerField(default=0)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'being_late_certificates_statistics'


class ReportType(BaseModel):
    name = CharField(unique=True, index=True)

    class Meta:
        table_name = 'report_types'


class TelegramChat(BaseModel):
    chat_id = BigIntegerField(unique=True, index=True)

    class Meta:
        table_name = 'telegram_chats'


class ForwardingReport(BaseModel):
    telegram_chat = ForeignKeyField(TelegramChat, on_delete='CASCADE')
    report_type = ForeignKeyField(ReportType, on_delete='CASCADE')
    department = ForeignKeyField(Department, on_delete='CASCADE')

    class Meta:
        table_name = 'forwarding_reports'
