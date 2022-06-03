from typing import Iterable

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup

import db
from telegram_bot.keyboards import buttons


class MainMenuMarkup(ReplyKeyboardMarkup):

    def __init__(self):
        super().__init__(
            resize_keyboard=True,
            keyboard=[[buttons.StatisticsReportsButton()],
                      [buttons.SettingsButton()]]
        )


class StatisticsReportsListMarkup(InlineKeyboardMarkup):

    def __init__(self):
        super().__init__(row_width=1)
        self.add(
            buttons.CookingTimeStatisticsButton(),
            buttons.KitchenPerformanceStatisticsButton(),
            buttons.DeliveryAwaitingTimeStatisticsButton(),
            buttons.DeliverySpeedStatisticsButton(),
            buttons.DeliveryPerformanceStatisticsButton(),
            buttons.BeingLateCertificatesStatisticsButton(),
            buttons.AwaitingOrdersStatisticsButton(),
            buttons.DailyRevenueStatisticsButton(),
            buttons.CustomersWithBonusStatisticsButton(),
        )


class ReportTypesMarkup(InlineKeyboardMarkup):

    def __init__(self, report_types: Iterable[db.ReportType]):
        super().__init__(row_width=1)
        self.add(*[buttons.ReportTypeSettingsButton(report_type) for report_type in report_types])


class DepartmentRegionsMarkup(InlineKeyboardMarkup):

    def __init__(self, department_regions: Iterable[db.DepartmentRegion], report_type_id: int):
        super().__init__(row_width=2)
        self.add(*[buttons.DepartmentRegionButton(region, report_type_id)
                   for region in department_regions])


class DepartmentsListMarkup(InlineKeyboardMarkup):

    def __init__(self, departments: Iterable[db.Department],
                 report_type_id: int,
                 region_id: int,
                 already_added_department_ids: Iterable[int]):
        super().__init__(row_width=2)
        department_buttons = (
            buttons.DepartmentButton(department, report_type_id, region_id,
                                     department.id in already_added_department_ids)
            for department in departments
        )
        self.add(*department_buttons)
        self.row(buttons.BatchEnableAllDepartmentsButton(report_type_id, region_id),
                 buttons.BatchDisableAllDepartmentsButton(report_type_id, region_id))
