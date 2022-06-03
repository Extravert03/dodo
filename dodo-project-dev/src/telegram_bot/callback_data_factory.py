from aiogram.utils.callback_data import CallbackData


report_type_settings_cb = CallbackData('report-type-settings', 'report_type_id')
departments_by_region_cb = CallbackData('departments-by-region', 'report_type_id', 'region_id')
department_cb = CallbackData('department', 'report_type_id', 'region_id', 'department_id')
batch_enable_departments_cb = CallbackData('batch-enable-departments', 'report_type_id', 'region_id', )
batch_disable_departments_cb = CallbackData('batch-disable-departments', 'report_type_id', 'region_id', )

