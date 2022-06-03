import pathlib
from abc import abstractmethod, ABC
from typing import Union

import openpyxl as openpyxl

from ..models import DeliveryStatisticsRow

__all__ = (
    'DeliveryStatisticsExcelParser',
)


class ExcelParser(ABC):
    __slots__ = ('_file_path', '_wb', '_ws',)

    def __init__(self, file_path: Union[str, pathlib.Path]):
        self._file_path = file_path

    def __enter__(self):
        self._wb = openpyxl.load_workbook(self._file_path, read_only=True)
        self._ws = self._wb.active
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._wb.close()

    @abstractmethod
    def get_data(self):
        pass


class DeliveryStatisticsExcelParser(ExcelParser):

    def get_data(self) -> list[DeliveryStatisticsRow]:
        rows = self._ws['A7': f'G{self._ws.max_row}']
        parsed_rows = [[cell.value for cell in row] for row in rows]
        filtered_rows = [row for row in parsed_rows if any(row)]
        return [DeliveryStatisticsRow(department=row[0],
                                      total_average_time=row[3],
                                      average_cooking_time=row[4],
                                      average_awaiting_on_heat_shelf_time=row[5],
                                      average_delivery_time=row[6])
                for row in filtered_rows]
