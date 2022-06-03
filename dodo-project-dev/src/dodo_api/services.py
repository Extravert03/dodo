from abc import ABC, abstractmethod
from typing import Union, Iterable

import httpx

from . import parsers, requests, executor, models
from .utils import file_utils

__all__ = (
    'DepartmentsList',
    'BeingLateCertificates',
    'CanceledOrders',
    'CanceledOrderByUUID',
    'RevenueStatistics',
    'DetailedDeliveryStatistics',
    'KitchenStatistics',
    'DeliveryStatistics',
    'SectorStopSales',
    'StreetStopSales',
    'PizzeriaStopSales',
    'IngredientStopSales',
)


class Service(ABC):
    parser: Union[parsers.html.HTMLParser, parsers.excel.ExcelParser]
    request: requests.DodoAPIRequest

    def __init__(self, cookies: dict):
        self._cookies = cookies

    async def run_request(self, request: requests.DodoAPIRequest) -> executor.DodoAPIResponse:
        return await executor.run_request(self._cookies, request)

    @abstractmethod
    async def get_data(self):
        pass

    @abstractmethod
    def get_prepared_request(self) -> requests.DodoAPIRequest:
        pass


class DepartmentsList(Service):
    parser = parsers.html.DepartmentsListHTMLParser
    request = requests.DepartmentsListRequest

    async def get_data(self) -> list[models.Department]:
        response = await self.run_request(self.get_prepared_request())
        return self.parser(response.html).parse()

    def get_prepared_request(self) -> requests.DepartmentsListRequest:
        return self.request()


class BeingLateCertificates(Service):
    parser = parsers.html.BeingLateCertificatesTableParser
    request = requests.BeingLateCertificatesRequest

    def __init__(self, cookies: dict, department_ids: Iterable[int],
                 begin_date: str, end_date: str):
        super().__init__(cookies)
        self._department_ids = department_ids
        self._begin_date = begin_date
        self._end_date = end_date

    async def get_data(self) -> list[models.BeingLateCertificate]:
        response = await executor.run_request(self._cookies, self.get_prepared_request())
        return self.parser(response.html).parse()

    def get_prepared_request(self) -> requests.BeingLateCertificatesRequest:
        return self.request(self._department_ids, self._begin_date, self._end_date)


class CanceledOrders(Service):
    parser = parsers.html.CanceledOrderUUIDsParser
    request = requests.CanceledOrdersRequest

    def __init__(self, cookies: dict, date: str):
        super().__init__(cookies)
        self._date = date

    async def get_data(self):
        request = self.get_prepared_request()
        result = []
        while True:
            response = await self.run_request(request)
            orders = self.parser(response.html).parse()
            if not orders:
                return result
            result += orders
            request.increment_page()

    def get_prepared_request(self) -> requests.CanceledOrdersRequest:
        return self.request(self._date)


class CanceledOrderByUUID(Service):
    parser = parsers.html.CanceledOrderByUUIDHTMLParser
    request = requests.CanceledOrderByUUIDRequest

    def __init__(self, cookies: dict, order_uuid: str, order_price: str, order_type: str):
        super().__init__(cookies)
        self._order_uuid = order_uuid
        self._order_price = order_price
        self._order_type = order_type

    async def get_data(self) -> models.CanceledOrderReport:
        response = await self.run_request(self.get_prepared_request())
        return self.parser(response.html, self._order_uuid,
                           self._order_price, self._order_type).parse()

    def get_prepared_request(self) -> requests.CanceledOrderByUUIDRequest:
        return self.request(self._order_uuid)


class DetailedDeliveryStatistics(Service):
    parser = parsers.excel.DeliveryStatisticsExcelParser
    request = requests.DetailedDeliveryStatisticsRequest

    def __init__(self, cookies: dict, department_ids: Iterable[int],
                 begin_date: str, end_date: str):
        super().__init__(cookies)
        self._department_ids = department_ids
        self._begin_date = begin_date
        self._end_date = end_date

    async def get_data(self) -> list[models.DeliveryStatisticsRow]:
        response = await self.run_request(self.get_prepared_request())
        with file_utils.TempFileProxy('xlsx') as tmp_file_proxy:
            with open(tmp_file_proxy.file_path, 'wb') as report_file:
                report_file.write(response.content)
            with self.parser(tmp_file_proxy.file_path) as parser:
                return parser.get_data()

    def get_prepared_request(self) -> requests.DodoAPIRequest:
        return self.request(self._department_ids, self._begin_date, self._end_date)


class KitchenStatistics(Service):
    parser = parsers.html.KitchenStatisticsHTMLParser
    request = requests.KitchenStatisticsRequest

    def __init__(self, cookies: dict, department_id: int):
        super().__init__(cookies)
        self._department_id = department_id

    async def get_data(self) -> models.KitchenStatistics:
        response = await self.run_request(self.get_prepared_request())
        return self.parser(response.html).parse()

    def get_prepared_request(self) -> requests.DodoAPIRequest:
        return self.request(self._department_id)


class DeliveryStatistics(Service):
    parser = parsers.html.DeliveryStatisticsHTMLParser
    request = requests.DeliveryStatisticsRequest

    def __init__(self, cookies: dict, department_id: int):
        super().__init__(cookies)
        self._department_id = department_id

    async def get_data(self) -> models.DeliveryStatistics:
        response = await self.run_request(self.get_prepared_request())
        return self.parser(response.html).parse()

    def get_prepared_request(self) -> requests.DodoAPIRequest:
        return self.request(self._department_id)


class RevenueStatistics:

    def __init__(self, department_id: int, lang: str = 'ru'):
        self._department_id = department_id
        self._lang = lang

    async def get_data(self) -> models.OperationalStatisticsForTodayAndWeekBefore:
        url = (f'https://publicapi.dodois.io/{self._lang}/api/v1'
               f'/OperationalStatisticsForTodayAndWeekBefore/{self._department_id}')
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response_json = response.json()
            return models.OperationalStatisticsForTodayAndWeekBefore.parse_obj(response_json)


class PizzeriaStopSales(Service):
    parser = parsers.html.PizzeriaStopSalesHTMLParser
    request = requests.PizzeriaStopSalesRequest

    def __init__(self, cookies: dict, department_ids: Iterable[int],
                 begin_date: str, end_date: str):
        super().__init__(cookies)
        self._department_ids = department_ids
        self._begin_date = begin_date
        self._end_date = end_date

    async def get_data(self) -> list[models.PizzeriaStopSaleReport]:
        response = await self.run_request(self.get_prepared_request())
        return self.parser(response.html).parse()

    def get_prepared_request(self) -> requests.DodoAPIRequest:
        return self.request(self._department_ids, self._begin_date, self._end_date)


class IngredientStopSales(Service):
    parser = parsers.html.IngredientStopSalesHTMLParser
    request = requests.IngredientStopSalesRequest

    def __init__(self, cookies: dict, department_ids: Iterable[int],
                 begin_date: str, end_date: str):
        super().__init__(cookies)
        self._department_ids = department_ids
        self._begin_date = begin_date
        self._end_date = end_date

    async def get_data(self) -> list[models.IngredientStopSaleReport]:
        response = await self.run_request(self.get_prepared_request())
        return self.parser(response.html).parse()

    def get_prepared_request(self) -> requests.IngredientStopSalesRequest:
        return self.request(self._department_ids, self._begin_date, self._end_date)


class SectorStopSales(Service):
    parser = parsers.html.SectorStopSalesHTMLParser
    request = requests.SectorStopSalesRequest

    def __init__(self, cookies: dict, department_ids: Iterable[int],
                 begin_date: str, end_date: str):
        super().__init__(cookies)
        self._department_ids = department_ids
        self._begin_date = begin_date
        self._end_date = end_date

    async def get_data(self) -> list[models.SectorStopSaleReport]:
        response = await self.run_request(self.get_prepared_request())
        return self.parser(response.html).parse()

    def get_prepared_request(self) -> requests.SectorStopSalesRequest:
        return self.request(self._department_ids, self._begin_date, self._end_date)


class StreetStopSales(Service):
    parser = parsers.html.StreetStopSalesHTMLParser
    request = requests.StreetStopSalesRequest

    def __init__(self, cookies: dict, department_ids: Iterable[int],
                 begin_date: str, end_date: str):
        super().__init__(cookies)
        self._department_ids = department_ids
        self._begin_date = begin_date
        self._end_date = end_date

    async def get_data(self) -> list[models.StreetStopSaleReport]:
        response = await self.run_request(self.get_prepared_request())
        return self.parser(response.html).parse()

    def get_prepared_request(self) -> requests.StreetStopSalesRequest:
        return self.request(self._department_ids, self._begin_date, self._end_date)


async def get_restaurant_orders(cookies: dict, unit_ids: Iterable[int | str], date: str) -> list[models.Order]:
    url = 'https://officemanager.dodopizza.ru/Reports/Orders/Get'
    async with httpx.AsyncClient(cookies=cookies) as client:
        response = await client.post(url, timeout=30, data={
            'filterType': 'OrdersFromRestaurant',
            'unitsIds': unit_ids,
            'OrderSources': 'Restaurant',
            'beginDate': date,
            'endDate': date,
            'orderTypes': ['Delivery', 'Pickup', 'Stationary']
        })
        with open('response.html', 'w') as file:
            file.write(response.text)
        return parsers.html.RestaurantOrdersParser(response.text).parse()
