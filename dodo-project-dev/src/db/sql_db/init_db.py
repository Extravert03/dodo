from db.sql_db import models
from db.sql_db.engine import db_engine
from db.sql_db.queries import add_department

__all__ = (
    'init_db_schemas',
    'drop_db_schemas',
)


def get_models() -> tuple:
    return (
        models.DepartmentRegion,
        models.ReportType,
        models.Department,
        models.TelegramChat,
        models.ForwardingReport,
        models.BeingLateCertificatesStatistics,
        models.DetailedDeliveryStatistics,
        models.RevenueStatistics,
        models.KitchenStatistics,
        models.DeliveryStatistics,
        models.OrdersStatistics,
    )


def init_db_schemas():
    db_engine.create_tables(get_models())


def drop_db_schemas():
    db_engine.drop_tables(get_models())


def add_department_regions():
    department_regions = ('москва 4', 'смолуга')
    for name in department_regions:
        models.DepartmentRegion.create(name=name)


def add_departments():
    moscow_region = models.DepartmentRegion.get(name='москва 4')
    smoluga_region = models.DepartmentRegion.get(name='смолуга')
    departments = [
        (389, 'москва 4-1', 'office_manager_msk_4', moscow_region),
        (436, 'москва 4-2', 'office_manager_msk_4', moscow_region),
        (652, 'москва 4-3', 'office_manager_msk_4', moscow_region),
        (708, 'москва 4-4', 'office_manager_msk_4', moscow_region),
        (712, 'москва 4-5', 'office_manager_msk_4', moscow_region),
        (713, 'москва 4-6', 'office_manager_msk_4', moscow_region),
        (714, 'москва 4-7', 'office_manager_msk_4', moscow_region),
        (1341, 'москва 4-8', 'office_manager_msk_4', moscow_region),
        (582, 'москва 4-10', 'office_manager_msk_4', moscow_region),
        (717, 'москва 4-11', 'office_manager_msk_4', moscow_region),
        (718, 'москва 4-12', 'office_manager_msk_4', moscow_region),
        (719, 'москва 4-13', 'office_manager_msk_4', moscow_region),
        (919, 'москва 4-14', 'office_manager_msk_4', moscow_region),
        (968, 'москва 4-15', 'office_manager_msk_4', moscow_region),
        (970, 'москва 4-17', 'office_manager_msk_4', moscow_region),
        (1046, 'москва 4-18', 'office_manager_msk_4', moscow_region),
        (1066, 'москва 4-19', 'office_manager_msk_4', moscow_region),
        (605, 'подольск-1', 'office_manager_podolsk', moscow_region),
        (1047, 'подольск-2', 'office_manager_podolsk', moscow_region),
        (9, 'смоленск-1', 'office_manager_smolensk', smoluga_region),
        (24, 'смоленск-2', 'office_manager_smolensk', smoluga_region),
        (83, 'смоленск-3', 'office_manager_smolensk', smoluga_region),
        (300, 'обнинск-1', 'office_manager_obninsk', smoluga_region),
        (609, 'вязьма-1', 'office_manager_vyazma', smoluga_region),
        (152, 'калуга-1', 'office_manager_kaluga', smoluga_region),
        (821, 'калуга-2', 'office_manager_kaluga', smoluga_region),
    ]
    for id, name, account_name, region in departments:
        add_department(id, name, account_name, region)


def add_report_types():
    report_types = (
        'Отчёты по статистике',
        'Стопы (Ингредиент)',
        'Стопы (Улица)',
        'Стопы (Сектор)',
        'Стопы (Пиццерия)',
        'Стопы-возобновления',
        'Отмены заказов',
    )
    for report_type in report_types:
        models.ReportType.create(name=report_type)


def reinit_db():
    drop_db_schemas()
    init_db_schemas()
    add_department_regions()
    add_departments()
    add_report_types()
