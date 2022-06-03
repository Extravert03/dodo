import peewee as pw

import config

__all__ = (
    'db_engine',
)

db_engine = pw.PostgresqlDatabase(
    user=config.DATABASE['user'],
    host=config.DATABASE['host'],
    port=config.DATABASE['port'],
    database=config.DATABASE['name'],
    password=config.DATABASE['password'],
)
