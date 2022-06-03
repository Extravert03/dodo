import json

from abc import ABC, abstractmethod
from typing import Any, Union

from pydantic import BaseModel

from . import models


class Serializer(ABC):

    _type: str = None

    def __init__(self, data: Union[str, BaseModel]):
        self._data = data

    @abstractmethod
    def as_json(self) -> str:
        pass

    @abstractmethod
    def as_python(self) -> Any:
        pass

    @classmethod
    def is_correct_serializer(cls, data: str) -> bool:
        return json.loads(data)['type'] == cls._type


class CanceledOrderReportSerializer(Serializer):

    _type = 'canceled_order_report'

    def as_json(self) -> str:
        return json.dumps({'type': self._type, 'data': self._data.dict()}, default=str, ensure_ascii=False)

    def as_python(self) -> models.CanceledOrderReport:
        return models.CanceledOrderReport.parse_obj(json.loads(self._data)['data'])


class IngredientStopSaleSerializer(Serializer):

    _type = 'ingredient_stop_sales'

    def as_json(self) -> str:
        pass

    def as_python(self) -> models.IngredientStopSale:
        return models.IngredientStopSale.parse_obj(json.loads(self._data)['data'])


class StopSaleSerializer(Serializer):
    _type: str = None
    _model: BaseModel = None

    def as_json(self) -> str:
        return json.dumps({'type': self._type, 'data': self._data.dict()}, default=str, ensure_ascii=False)

    def as_python(self) -> Any:
        return self._model.parse_obj(json.loads(self._data)['data'])


class PizzeriaStopSaleSerializer(StopSaleSerializer):
    _type = 'pizzeria_stop_sales'
    _model = models.PizzeriaStopSaleReport


class IngredientsStopSaleSerializer(StopSaleSerializer):
    _type = 'ingredients_stop_sales'
    _model = models.IngredientStopSaleReport


class SectorStopSaleSerializer(StopSaleSerializer):
    _type = 'sector_stop_sales'
    _model = models.SectorStopSaleReport


class StreetStopSaleSerializer(StopSaleSerializer):
    _type = 'street_stop_sales'
    _model = models.StreetStopSaleReport
