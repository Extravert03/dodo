from aiogram.types import KeyboardButton, InlineKeyboardButton

import db
from telegram_bot import callback_data_factory


class StatisticsReportsButton(KeyboardButton):

    def __init__(self):
        super().__init__('📊 Отчёты/Статистика')


class CookingTimeStatisticsButton(InlineKeyboardButton):

    def __init__(self):
        super().__init__('Время приготовления', callback_data='cooking-time')


class CustomersWithBonusStatisticsButton(InlineKeyboardButton):

    def __init__(self):
        super().__init__('Бонусная система', callback_data='bonus-system')


class KitchenPerformanceStatisticsButton(InlineKeyboardButton):

    def __init__(self):
        super().__init__('Производительность кухни', callback_data='kitchen-performance')


class DeliveryAwaitingTimeStatisticsButton(InlineKeyboardButton):

    def __init__(self):
        super().__init__('Время на полке', callback_data='delivery-awaiting-time')


class DeliverySpeedStatisticsButton(InlineKeyboardButton):

    def __init__(self):
        super().__init__('Скорость доставки', callback_data='delivery-speed')


class DeliveryPerformanceStatisticsButton(InlineKeyboardButton):

    def __init__(self):
        super().__init__('Производительность доставки', callback_data='delivery-performance')


class AwaitingOrdersStatisticsButton(InlineKeyboardButton):

    def __init__(self):
        super().__init__('Остывает на полке', callback_data='awaiting-orders')


class DailyRevenueStatisticsButton(InlineKeyboardButton):

    def __init__(self):
        super().__init__('Выручка за сегодня', callback_data='daily-revenue')


class BeingLateCertificatesStatisticsButton(InlineKeyboardButton):

    def __init__(self):
        super().__init__('Сертификаты за опоздание', callback_data='being-late-certificates')


class SettingsButton(KeyboardButton):

    def __init__(self):
        super().__init__('⚙️ Настройки')


class ReportTypeSettingsButton(InlineKeyboardButton):

    def __init__(self, report_type: db.ReportType):
        super().__init__(
            text=report_type.name,
            callback_data=callback_data_factory.report_type_settings_cb.new(
                report_type_id=report_type.id,
            ),
        )


class DepartmentRegionButton(InlineKeyboardButton):

    def __init__(self, department_region: db.DepartmentRegion, report_type_id: int):
        super().__init__(
            text=department_region.name.capitalize(),
            callback_data=callback_data_factory.departments_by_region_cb.new(
                region_id=department_region.id,
                report_type_id=report_type_id,
            )
        )


class DepartmentButton(InlineKeyboardButton):

    def __init__(self, department: db.Department,
                 report_type_id: int,
                 region_id: int,
                 is_activated: bool):
        super().__init__(
            text=f'{"🟢" if is_activated else "🔴"} {department.name.capitalize()}',
            callback_data=callback_data_factory.department_cb.new(
                department_id=department.id,
                report_type_id=report_type_id,
                region_id=region_id,
            )
        )


class BatchEnableAllDepartmentsButton(InlineKeyboardButton):

    def __init__(self, report_type_id: int, region_id: int):
        super().__init__(
            text='Включить все',
            callback_data=callback_data_factory.batch_enable_departments_cb.new(
                report_type_id=report_type_id,
                region_id=region_id,
            )
        )


class BatchDisableAllDepartmentsButton(InlineKeyboardButton):

    def __init__(self, report_type_id: int, region_id: int):
        super().__init__(
            text='Отключить все',
            callback_data=callback_data_factory.batch_disable_departments_cb.new(
                report_type_id=report_type_id,
                region_id=region_id,
            )
        )