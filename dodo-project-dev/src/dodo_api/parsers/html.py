import unicodedata
from abc import abstractmethod, ABC

from bs4 import BeautifulSoup

from .. import models

__all__ = (
    'PizzeriaStopSalesHTMLParser',
    'DeliveryStatisticsHTMLParser',
    'KitchenStatisticsHTMLParser',
    'DepartmentsListHTMLParser',
    'BeingLateCertificatesTableParser',
    'CanceledOrderUUIDsParser',
    'CanceledOrderByUUIDHTMLParser',
    'StreetStopSalesHTMLParser',
    'IngredientStopSalesHTMLParser',
    'SectorStopSalesHTMLParser',
)


class HTMLParser(ABC):

    def __init__(self, html: str):
        self._soup = BeautifulSoup(html, 'lxml')

    @abstractmethod
    def parse(self):
        pass

    @staticmethod
    def clear_extra_symbols(text: str) -> str:
        text = unicodedata.normalize('NFKD', text)
        for i in (' ', '₽', '%', '\r', '\t'):
            text = text.replace(i, '')
        return text.strip().replace(',', '.').replace('−', '-')


class BeingLateCertificatesTableParser(HTMLParser):

    def parse(self) -> list:
        if 'данные не найдены' in self._soup.text.lower():
            return []
        table_with_certificates = self._soup.find_all('table')[1]
        result = []
        for tr in table_with_certificates.find_all('tr')[1:]:
            (department, datetime, order_no, approximately_delivery_time,
             courier_mark_at, delivery_deadline, certificate_type, given_by
             ) = [td.text.strip() for td in tr.find_all('td')]
            datetime = datetime.replace('\t', '').replace('\r', '').replace('\n', ' ').replace(
                '  ', ' ')
            result.append(models.BeingLateCertificate(
                department=department,
                datetime=datetime,
                order_no=order_no,
                approximately_delivery_time=approximately_delivery_time,
                courier_mark_at=courier_mark_at,
                delivery_deadline=delivery_deadline,
                certificate_type=certificate_type,
                given_by=given_by,
            ))
        return result


class CanceledOrderByUUIDHTMLParser(HTMLParser):

    def __init__(self, html: str, order_uuid: str, order_price: str, order_type: str):
        super().__init__(html)
        self._order_uuid = order_uuid
        self._order_price = order_price
        self._order_type = order_type

    def parse(self) -> models.CanceledOrderReport:
        order_no = self._soup.find('span', id='orderNumber').text
        department = self._soup.find('div', class_='headerDepartment').text
        history = self._soup.find('div', id='history')
        trs = history.find_all('tr')[1:]
        order_created_at = receipt_printed_at = None
        is_receipt_printed = False
        for tr in trs:
            _, msg, _ = tr.find_all('td')
            msg = msg.text.lower().strip()
            if 'refund receipt' in msg and 'has been printed' in msg:
                is_receipt_printed = True
                break
        for tr in trs:
            dt, msg, _ = tr.find_all('td')
            msg = msg.text.lower().strip()
            if 'has been accepted' in msg:
                order_created_at = dt.text
            elif 'has been rejected' in msg and is_receipt_printed:
                receipt_printed_at = dt.text
        return models.CanceledOrderReport(
            order_no=order_no,
            department=department,
            order_created_at=order_created_at,
            receipt_printed_at=receipt_printed_at,
            order_uuid=self._order_uuid,
            order_price=self._order_price,
            order_type=self._order_type,
        )


class CanceledOrderUUIDsParser(HTMLParser):

    def parse(self):
        trs = self._soup.find_all('tr')[1:]
        nested_trs = [tr.find_all('td') for tr in trs]
        return [{'order_uuid': td[0].find('a').get('href').split('=')[-1],
                 'order_no': td[1].text.strip(),
                 'order_price': td[4].text.strip('₽').strip(),
                 'order_type': td[7].text}
                for td in nested_trs]


class DeliveryStatisticsHTMLParser(HTMLParser):

    def parse(self) -> models.DeliveryStatistics:
        statistics_data = self._soup.find_all('h1', class_='operationalStatistics_panelTitle')
        required_data = [self.clear_extra_symbols(block.text) for block in statistics_data]
        deliveries_amount_per_hour, deliveries_percent = required_data[0].split('\n')
        couriers_total_amount, couriers_in_queue_amount = required_data[3].split('/')
        return models.DeliveryStatistics(
            deliveries_amount_per_hour=deliveries_amount_per_hour,
            increase_over_week_ago=deliveries_percent,
            awaiting_orders_amount=required_data[2],
            couriers_total_amount=couriers_total_amount,
            couriers_in_queue_amount=couriers_in_queue_amount,
            delivery_awaiting_time=required_data[5],
        )


class IngredientStopSalesHTMLParser(HTMLParser):

    def parse(self) -> list[models.IngredientStopSaleReport]:
        trs = self._soup.find('tbody').find_all('tr')
        nested_trs = [[td.text.strip() for td in tr.find_all('td')] for tr in trs]
        return [models.IngredientStopSaleReport(
            department=tds[0],
            ingredient=tds[1],
            stop_reason=tds[2],
            stopped_at=tds[3],
            stopper_name=tds[4],
            renewer_name=tds[6],
        ) for tds in nested_trs]


class KitchenStatisticsHTMLParser(HTMLParser):
    __slots__ = ('_soup',)

    def parse(self) -> models.KitchenStatistics:
        panel_titles = [
            self.clear_extra_symbols(i.text)
            for i in self._soup.find_all('h1', class_='operationalStatistics_panelTitle')
        ]
        average_cooking_time = panel_titles[3]
        revenue_per_hour, revenue_increase_over_week_ago = panel_titles[0].split('\n')
        spending_per_hour, spending_increase_over_week_ago = panel_titles[1].split('\n')

        postponed, in_queue, in_work = [
            int(i.text) for i in
            self._soup.find_all('h1', class_='operationalStatistics_productsCountValue')
        ]
        return models.KitchenStatistics(
            revenue_per_hour=revenue_per_hour,
            revenue_increase_over_week_ago=revenue_increase_over_week_ago,
            products_spending_per_hour=spending_per_hour,
            products_spending_increase_over_week_ago=spending_increase_over_week_ago,
            average_cooking_time=average_cooking_time,
            postponed=postponed,
            in_work=in_work,
            in_queue=in_queue,
        )


class PizzeriaStopSalesHTMLParser(HTMLParser):
    def parse(self) -> list[models.PizzeriaStopSaleReport]:
        trs = self._soup.find('table', id='bootgrid-table').find('tbody').find_all('tr')
        nested_trs = [[td.text.strip() for td in tr.find_all('td')] for tr in trs]
        return [models.PizzeriaStopSaleReport(
            department=tds[0],
            sale_type=tds[1],
            stop_reason=tds[2],
            stopped_at=tds[3],
            stopper_name=tds[4],
            stop_duration=tds[5],
            renewer_name=tds[6],
            stop_type=tds[7],
        ) for tds in nested_trs]


class DepartmentsListHTMLParser(HTMLParser):

    def parse(self) -> list[models.Department]:
        sale_points_select_picker = self._soup.find('select', id='unitId')
        sale_point_options = sale_points_select_picker.find_all('option')
        return [models.Department(unit_id=option.get('value').strip(),
                                  name=option.text.strip())
                for option in sale_point_options]


class SectorStopSalesHTMLParser(HTMLParser):
    def parse(self) -> list[models.SectorStopSaleReport]:
        trs = self._soup.find('table', id='bootgrid-table').find('tbody').find_all('tr')
        nested_trs = [[td.text.strip() for td in tr.find_all('td')] for tr in trs]
        return [models.SectorStopSaleReport(
            department=tds[0],
            sector=tds[1],
            stopped_at=tds[2],
            stopper_name=tds[3],
            renewer_name=tds[5],
        ) for tds in nested_trs]


class StreetStopSalesHTMLParser(HTMLParser):
    def parse(self) -> list[models.StreetStopSaleReport]:
        trs = self._soup.find('table', id='bootgrid-table').find_all('tr')[1:]
        nested_trs = [[td.text.strip() for td in tr.find_all('td')] for tr in trs]
        return [models.StreetStopSaleReport(
            department=tds[0],
            sector=tds[1],
            street=tds[2],
            stopped_at=tds[3],
            stopper_name=tds[4],
            renewer_name=tds[6],
        ) for tds in nested_trs]


class RestaurantOrdersParser(HTMLParser):

    def parse(self) -> list[models.Order]:
        tbody = self._soup.find('tbody')
        result = []
        for tr in tbody.find_all('tr'):
            tds = [td.text.strip() for td in tr.find_all('td')]
            result.append(models.Order(
                department=tds[0],
                datetime=tds[1],
                no=tds[2],
                type=tds[3],
                customer_name=tds[4],
                customer_phone_number=tds[5],
                price=tds[6],
                payment_method=tds[7],
                order_status=tds[8],
                accepted_by_employee=tds[9],
            ))
        return result
