from aiogram.dispatcher.filters import Text, CommandSettings
from aiogram.types import Message, CallbackQuery

import db
from telegram_bot import responses, callback_data_factory
from telegram_bot.bot import dp


@dp.callback_query_handler(
    callback_data_factory.batch_disable_departments_cb.filter(),
    state='*',
)
async def on_batch_disable_departments_cb(callback_query: CallbackQuery, callback_data: dict):
    report_type_id = callback_data['report_type_id']
    region_id = callback_data['region_id']
    departments = db.get_departments_by_region_id(region_id)
    db.disable_batch_all_departments(callback_query.message.chat.id, report_type_id)
    return responses.DepartmentsListResponse(departments, report_type_id, region_id, [], edit=True)


@dp.callback_query_handler(
    callback_data_factory.batch_enable_departments_cb.filter(),
    state='*',
)
async def on_batch_enable_departments_cb(callback_query: CallbackQuery, callback_data: dict):
    report_type_id = callback_data['report_type_id']
    region_id = callback_data['region_id']
    db.add_batch_all_departments(callback_query.message.chat.id, report_type_id, region_id)
    departments = db.get_departments_by_region_id(region_id)
    forwarding_report_departments = db.get_already_added_departments(callback_query.message.chat.id,
                                                                     report_type_id)
    return responses.DepartmentsListResponse(departments, report_type_id, region_id,
                                             forwarding_report_departments, edit=True)


@dp.callback_query_handler(
    callback_data_factory.department_cb.filter(),
    state='*',
)
async def on_department_cb(callback_query: CallbackQuery, callback_data: dict):
    department_id = callback_data['department_id']
    report_type_id = callback_data['report_type_id']
    region_id = callback_data['region_id']
    forwarding_report, is_created = db.add_forwarding_report_department(
        callback_query.message.chat.id, report_type_id, department_id)
    if not is_created:
        forwarding_report.delete_instance()
    departments = db.get_departments_by_region_id(region_id)
    forwarding_report_departments = db.get_already_added_departments(callback_query.message.chat.id,
                                                                     report_type_id)
    return responses.DepartmentsListResponse(departments, report_type_id, region_id,
                                             forwarding_report_departments, edit=True)


@dp.callback_query_handler(
    callback_data_factory.departments_by_region_cb.filter(),
    state='*',
)
async def on_departments_by_region_cb(callback_query: CallbackQuery, callback_data: dict):
    region_id = callback_data['region_id']
    report_type_id = callback_data['report_type_id']
    departments = db.get_departments_by_region_id(region_id)
    forwarding_report_departments = db.get_already_added_departments(callback_query.message.chat.id,
                                                                     report_type_id)
    return responses.DepartmentsListResponse(departments, report_type_id, region_id,
                                             forwarding_report_departments)


@dp.callback_query_handler(
    callback_data_factory.report_type_settings_cb.filter(),
    state='*',
)
async def on_report_type_settings_cb(callback_query: CallbackQuery, callback_data: dict):
    department_regions = db.DepartmentRegion.select()
    report_type_id = callback_data['report_type_id']
    return responses.DepartmentRegionsListResponse(department_regions, report_type_id)


@dp.message_handler(CommandSettings(), state='*')
@dp.message_handler(Text('⚙️ Настройки'), state='*')
async def on_settings_command(message: Message):
    report_types = db.ReportType.select()
    return responses.ReportTypesSettingsResponse(report_types)
