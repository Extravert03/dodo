from typing import Optional, Iterable

import db
from dodo_api.models import OperationalStatisticsForTodayAndWeekBefore, BeingLateCertificate
from telegram_bot.keyboards import markups
from telegram_bot.responses.base import Response, ReplyMarkup
from telegram_bot.utils import format_text


class MainMenuResponse(Response):

    def get_text(self) -> Optional[str]:
        return 'Приветствую 👋'

    def get_reply_markup(self) -> Optional[ReplyMarkup]:
        return markups.MainMenuMarkup()


class StatisticsReportsListResponse(Response):

    def get_text(self) -> Optional[str]:
        return 'Выберите отчёт который хотите посмотреть 👇'

    def get_reply_markup(self) -> Optional[ReplyMarkup]:
        return markups.StatisticsReportsListMarkup()


class StatisticsResponse(Response):
    __slots__ = ('_reports',)

    def __init__(self, reports, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reports = self.get_sorted_reports(reports)

    @staticmethod
    def get_sorted_reports(reports) -> list:
        return reports


class DailyRevenueStatisticsResponse(StatisticsResponse):

    def __init__(
            self,
            reports: Iterable[OperationalStatisticsForTodayAndWeekBefore],
            departments: Iterable[db.Department],
            *args, **kwargs
    ):
        super().__init__(reports, *args, **kwargs)
        self._departments = departments
        self._department_id_to_name = {department.id: department.name
                                       for department in self._departments}

    @staticmethod
    def get_sorted_reports(
            reports: Iterable[OperationalStatisticsForTodayAndWeekBefore],
    ) -> list[OperationalStatisticsForTodayAndWeekBefore]:
        return sorted(reports, key=lambda report: report.today.revenue, reverse=True)

    def get_text(self) -> Optional[str]:
        text = ['<b>Выручка за сегодня</b>:']
        total_daily_revenue = 0
        total_revenue_week_before = 0
        for report in self._reports:
            report: OperationalStatisticsForTodayAndWeekBefore
            increase_percent = format_text.estimate_revenue_increase_percent(
                report.today.revenue, report.week_before_to_this_time.revenue)
            text.append(
                (f'{self._department_id_to_name[report.unit_id].capitalize()}'
                 f' | {format_text.insert_gaps_between_chars(report.today.revenue)}'
                 f' | {format_text.format_percent(increase_percent)}'))
            total_daily_revenue += report.today.revenue
            total_revenue_week_before += report.week_before.revenue
        today_and_week_ago_revenue_diff = format_text.estimate_revenue_increase_percent(
            total_daily_revenue, total_revenue_week_before
        )
        text.append(f'<b>Итого {format_text.insert_gaps_between_chars(total_daily_revenue)} |'
                    f' {format_text.format_percent(today_and_week_ago_revenue_diff)}</b>')
        return '\n'.join(text)


class CookingTimeStatisticsResponse(StatisticsResponse):

    @staticmethod
    def get_sorted_reports(reports: Iterable[db.KitchenStatistics]) -> list[db.KitchenStatistics]:
        return sorted(reports, key=lambda report: report.average_cooking_time)

    def get_text(self) -> Optional[str]:
        text_lines = ['<b>Время приготовления:</b>']
        for report in self._reports:
            text_lines.append(
                f'{report.department.name.capitalize()}'
                f' | {format_text.format_time_in_seconds(report.average_cooking_time)}')
        return '\n'.join(text_lines)


class KitchenPerformanceStatisticsResponse(StatisticsResponse):

    @staticmethod
    def get_sorted_reports(reports: Iterable[db.KitchenStatistics]) -> list[db.KitchenStatistics]:
        return sorted(reports, key=lambda report: report.revenue_per_hour, reverse=True)

    def get_text(self) -> Optional[str]:
        text_lines = ['<b>Выручка на чел. в час</b>']
        for report in self._reports:
            text_lines.append(
                f'{report.department.name.capitalize()}'
                f' | {format_text.insert_gaps_between_chars(report.revenue_per_hour)}'
                f' | {format_text.format_percent(report.revenue_increase_over_week_ago)}')
        return '\n'.join(text_lines)


class DeliverySpeedStatisticsResponse(StatisticsResponse):

    @staticmethod
    def get_sorted_reports(
            reports: Iterable[db.DetailedDeliveryStatistics]
    ) -> list[db.DetailedDeliveryStatistics]:
        return sorted(reports, key=lambda report: report.total_average_time)

    def get_text(self) -> Optional[str]:
        text_lines = ['<b>Общая скорость доставки - Время приготовления'
                      ' - Время на полке - Поездка курьера</b>']
        for report in self._reports:
            text_lines.append(
                (f'{format_text.replace_department_name_by_alias(report.department.name)}'
                 f' | {format_text.format_time_in_seconds(report.total_average_time)}'
                 f' | {format_text.format_time_in_seconds(report.average_cooking_time)}'
                 f' | {format_text.format_time_in_seconds(report.average_awaiting_on_heat_shelf_time)}'
                 f' | {format_text.format_time_in_seconds(report.average_delivery_time)}'))
        return '\n'.join(text_lines)


class BeingLateCertificatesResponse(StatisticsResponse):

    def __init__(
            self, today_reports: Iterable[BeingLateCertificate],
            week_before_reports: Iterable[BeingLateCertificate],
            departments: Iterable[db.Department]
    ):
        super().__init__(None)
        self._reports = self.collect_reports_by_department(today_reports, week_before_reports, departments)

    @staticmethod
    def collect_reports_by_department(
            today_reports: Iterable[BeingLateCertificate],
            week_before_reports: Iterable[BeingLateCertificate],
            departments: Iterable[db.Department],
    ) -> list[tuple[str, list[BeingLateCertificate], list[BeingLateCertificate]]]:
        department_names = {report.department for report in today_reports}.union(
            {report.department for report in week_before_reports})
        collected = []
        for department_name in department_names:
            today_reports_amount = [report for report in today_reports
                                    if report.department == department_name]
            week_before_reports_amount = [report for report in week_before_reports
                                          if report.department == department_name]
            collected.append((department_name, today_reports_amount, week_before_reports_amount))
        department_names_in_db = {department.name for department in departments}
        collected += [(name, [], []) for name in (department_names_in_db - department_names)]
        return collected

    def get_text(self) -> Optional[str]:
        text = ['<b>Сертификаты за опоздание (сегодня) | (неделю назад)</b>']
        reports = sorted(self._reports, key=lambda x: len(x[1]), reverse=True)
        for department_name, daily_reports, week_before_reports in reports:
            text.append((f'{department_name.capitalize()}'
                         f' | {len(daily_reports)} шт'
                         f' | {len(week_before_reports)} шт'))
        return '\n'.join(text)


class DeliveryPerformanceStatisticsResponse(StatisticsResponse):

    @staticmethod
    def get_sorted_reports(reports: Iterable[db.DeliveryStatistics]) -> list[db.DeliveryStatistics]:
        return sorted(reports, reverse=True,
                      key=lambda report: report.deliveries_amount_per_hour)

    def get_text(self) -> Optional[str]:
        text_lines = ['<b>Заказов на курьера в час</b>']
        for report in self._reports:
            text_lines.append(
                f'{report.department.name.capitalize()} | {report.deliveries_amount_per_hour}'
                f' | {format_text.format_percent(report.increase_over_week_ago)}')
        return '\n'.join(text_lines)


class AwaitingOrdersStatisticsResponse(StatisticsResponse):

    @staticmethod
    def get_sorted_reports(reports: Iterable[db.DeliveryStatistics]) -> list[db.DeliveryStatistics]:
        return sorted(reports, reverse=True,
                      key=lambda report: report.awaiting_orders_amount)

    def get_text(self) -> Optional[str]:
        text_lines = ['<b>Остывают на полке - В очереди (Всего)</b>']
        for report in self._reports:
            text_lines.append(
                (f'{report.department.name.capitalize()} | {report.awaiting_orders_amount}'
                 f' - {report.couriers_in_queue_amount} ({report.couriers_total_amount})'))
        return '\n'.join(text_lines)


class DeliveryAwaitingTimeStatisticsResponse(StatisticsResponse):

    @staticmethod
    def get_sorted_reports(reports: Iterable[db.DeliveryStatistics]) -> list[db.DeliveryStatistics]:
        return sorted(reports, key=lambda report: report.delivery_awaiting_time)

    def get_text(self) -> Optional[str]:
        text_lines = ['<b>Время ожидания на полке</b>']
        for report in self._reports:
            text_lines.append(
                (f'{report.department.name.capitalize()}'
                 f' | {format_text.format_time_in_seconds(report.delivery_awaiting_time)}'))
        return '\n'.join(text_lines)


class BonusSystemStatisticsResponse(StatisticsResponse):

    @staticmethod
    def get_sorted_reports(reports: Iterable[db.OrdersStatistics]) -> list[db.DeliveryStatistics]:
        return sorted(reports, reverse=True,
                      key=lambda report: format_text.estimate_customers_with_bonus_percent(report.customers_with_bonus,
                                                                                           report.total_customers))

    def get_text(self) -> Optional[str]:
        text = ['<b>Бонусная система</b>']
        for report in self._reports:
            text.append(
                (f'{report.department.name.capitalize()}'
                 f' | {format_text.estimate_customers_with_bonus_percent(report.customers_with_bonus, report.total_customers)}% из 100')
            )
        return '\n'.join(text)
