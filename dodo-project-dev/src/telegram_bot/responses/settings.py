from typing import Optional, Iterable

import db
from telegram_bot import keyboards
from telegram_bot.responses.base import Response, ReplyMarkup


class StatisticsReportsNotConfiguredResponse(Response):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_text(self) -> Optional[str]:
        return ('Кажется вы не добавили ни одну точку продаж для отображения 😕\n'
                'Чтобы это сделать, нажмите на кнопку <b>⚙️ Настройки</b>'
                ' или введите команду /settings.\n'
                'Далее нажмите на кнопку <b>Отчёты по статистике</b> и отметьте точки продаж.')


class DepartmentsListResponse(Response):

    def __init__(self, departments: Iterable[db.Department],
                 report_type_id: int,
                 region_id: int,
                 already_added_departments: Iterable[db.ForwardingReport],
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__departments = departments
        self.__already_added_departments = already_added_departments
        self.__report_type_id = report_type_id
        self.__region_id = region_id

    def get_text(self) -> Optional[str]:
        return 'Выберите точки продаж для отслеживания'

    def get_reply_markup(self) -> Optional[ReplyMarkup]:
        added_department_ids = {
            forwarding_report.department.id
            for forwarding_report in self.__already_added_departments}
        return keyboards.DepartmentsListMarkup(self.__departments, self.__report_type_id,
                                               self.__region_id, added_department_ids)


class DepartmentRegionsListResponse(Response):
    __slots__ = ('department_regions',)

    def __init__(self, department_regions: Iterable[db.DepartmentRegion], report_type_id: int,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__department_regions = department_regions
        self.__report_type_id = report_type_id

    def get_text(self) -> Optional[str]:
        return 'Выберите регион подразделений'

    def get_reply_markup(self) -> Optional[ReplyMarkup]:
        return keyboards.DepartmentRegionsMarkup(self.__department_regions, self.__report_type_id)


class ReportTypesSettingsResponse(Response):
    __slots__ = ('__report_types',)

    def __init__(self, report_types: Iterable[db.ReportType], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__report_types = report_types

    def get_text(self) -> Optional[str]:
        return 'Выберите вид отчётов, которые хотите получать 👇'

    def get_reply_markup(self) -> Optional[ReplyMarkup]:
        return keyboards.ReportTypesMarkup(self.__report_types)
