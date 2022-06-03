from enum import Enum
from typing import Iterable

__all__ = (
    'BeingLateCertificatesRequest',
    'StreetStopSalesRequest',
    'DeliveryStatisticsRequest',
    'KitchenStatisticsRequest',
    'CanceledOrdersRequest',
    'DetailedDeliveryStatisticsRequest',
    'DepartmentsListRequest',
    'SectorStopSalesRequest',
    'PizzeriaStopSalesRequest',
    'IngredientStopSalesRequest',
    'CanceledOrderByUUIDRequest',
)


class StopSaleType(Enum):
    PIZZERIA = 0
    PRODUCTS = 1
    INGREDIENT = 2
    STREET = 3
    SECTOR = 4


class POSTRequestMixin:
    request_method = 'POST'


class GETRequestMixin:
    request_method = 'GET'


class DodoAPIRequest:
    request_method: str
    url: str

    def get_request_params(self) -> dict:
        """
        :return: all required params for http request.
        """
        return {
            'method': self.request_method,
            'url': self.url,
            'params': self.get_params(),
            'json': self.get_json(),
            'data': self.get_data(),
        }

    def get_params(self) -> dict:
        pass

    def get_json(self) -> dict:
        pass

    def get_data(self) -> dict:
        pass


class BeingLateCertificatesRequest(DodoAPIRequest, POSTRequestMixin):
    __slots__ = ('__begin_date', '__end_date', '__department_ids')

    url = 'https://officemanager.dodopizza.ru/Reports/BeingLateCertificates/Get'

    def __init__(self, department_ids: Iterable[int], begin_date: str, end_date: str):
        self.__begin_date = begin_date
        self.__end_date = end_date
        self.__department_ids = department_ids

    def get_data(self) -> dict:
        return {
            'unitsIds': self.__department_ids,
            'beginDate': self.__begin_date,
            'endDate': self.__end_date,
        }


class CanceledOrdersRequest(DodoAPIRequest, GETRequestMixin):
    __slots__ = ('_page', '_date')

    url = 'https://shiftmanager.dodopizza.ru/Managment/ShiftManagment/PartialShiftOrders'

    def __init__(self, date: str):
        self._page = 1
        self._date = date

    def increment_page(self) -> None:
        self._page += 1

    def get_params(self) -> dict:
        return {
            'page': self._page,
            'date': self._date,
            'orderStateFilter': 'Failure',
        }


class CanceledOrderByUUIDRequest(DodoAPIRequest, GETRequestMixin):
    __slots__ = ('order_uuid',)

    url = 'https://shiftmanager.dodopizza.ru/Managment/ShiftManagment/Order'

    def __init__(self, order_uuid: str):
        self.order_uuid = order_uuid

    def get_params(self) -> dict:
        return {'orderUUId': self.order_uuid}


class DetailedDeliveryStatisticsRequest(DodoAPIRequest, POSTRequestMixin):
    __slots__ = ('__begin_date', '__end_date', '__department_ids')

    url = 'https://officemanager.dodopizza.ru/Reports/DeliveryStatistic/Export'

    def __init__(self, department_ids: Iterable[int], begin_date: str, end_date: str):
        self.__begin_date = begin_date
        self.__end_date = end_date
        self.__department_ids = tuple(department_ids)

    def get_data(self) -> dict:
        return {
            'unitsIds': self.__department_ids,
            'beginDate': self.__begin_date,
            'endDate': self.__end_date,
        }


class DepartmentsListRequest(DodoAPIRequest, GETRequestMixin):
    url = 'https://officemanager.dodopizza.ru/OfficeManager/OperationalStatistics'


class StatisticsRequest(DodoAPIRequest, GETRequestMixin):
    __slots__ = ('_department_id',)

    def __init__(self, department_id: int):
        self._department_id = department_id

    def get_params(self) -> dict:
        return {'unitId': self._department_id}


class KitchenStatisticsRequest(StatisticsRequest):
    url = 'https://officemanager.dodopizza.ru/OfficeManager/OperationalStatistics/KitchenPartial'


class DeliveryStatisticsRequest(StatisticsRequest):
    url = 'https://officemanager.dodopizza.ru/OfficeManager/OperationalStatistics/DeliveryWorkPartial'


class StopSalesRequest(DodoAPIRequest, POSTRequestMixin):
    __slots__ = ('_department_ids', '_begin_date', '_end_date')
    stop_type: StopSaleType

    def __init__(self, department_ids: Iterable[int], begin_date: str, end_date: str):
        self._department_ids = department_ids
        self._begin_date = begin_date
        self._end_date = end_date

    def get_data(self) -> dict:
        return {
            'UnitsIds': self._department_ids,
            'stop_type': self.stop_type.value,
            'productOrIngredientStopReasons': tuple(range(7)),
            'beginDate': self._begin_date,
            'endDate': self._end_date,
        }


class PizzeriaStopSalesRequest(StopSalesRequest):
    stop_type = StopSaleType.PIZZERIA
    url = 'https://officemanager.dodopizza.ru/Reports/StopSaleStatistic/GetSaleStopSaleReport'


class StreetStopSalesRequest(StopSalesRequest):
    stop_type = StopSaleType.STREET
    url = 'https://officemanager.dodopizza.ru/Reports/StopSaleStatistic/GetDeliveryUnitStopSaleReport'


class SectorStopSalesRequest(StopSalesRequest):
    stop_type = StopSaleType.SECTOR
    url = 'https://officemanager.dodopizza.ru/Reports/StopSaleStatistic/GetDeliverySectorsStopSaleReport'


class IngredientStopSalesRequest(StopSalesRequest):
    stop_type = StopSaleType.INGREDIENT
    url = 'https://officemanager.dodopizza.ru/Reports/StopSaleStatistic/GetIngredientsStopSaleReport'

    def get_data(self) -> dict:
        body = super().get_data()
        body['stopType'] = body['stop_type']
        del body['stop_type']
        return body
