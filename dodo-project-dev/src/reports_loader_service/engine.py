import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from reports_loader_service import statistics_service, canceled_orders_service, stop_sales_service

__all__ = (
    'run_statistics_service',
)


def run_statistics_service():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(statistics_service.update_kitchen_statistics, IntervalTrigger(minutes=1))
    scheduler.add_job(statistics_service.update_delivery_statistics, IntervalTrigger(minutes=1))
    scheduler.add_job(statistics_service.update_detailed_delivery_statistics, IntervalTrigger(minutes=1))
    scheduler.add_job(canceled_orders_service.update_canceled_orders, CronTrigger(minute='*/5'))
    scheduler.add_job(stop_sales_service.run_pizzeria_stop_sales, CronTrigger(minute='*/5'))
    scheduler.add_job(stop_sales_service.run_street_stop_sales, CronTrigger(minute='*/10'))
    scheduler.add_job(stop_sales_service.run_sector_stop_sales, CronTrigger(minute='*/10'))
    scheduler.add_job(stop_sales_service.run_ingredient_stop_sales, CronTrigger(minute='*/30'))
    scheduler.add_job(statistics_service.update_orders_statistics, IntervalTrigger(minutes=5))
    scheduler.start()
    asyncio.get_event_loop().run_forever()
