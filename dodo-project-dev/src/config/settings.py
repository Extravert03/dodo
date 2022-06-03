from pathlib import Path

import pendulum

from .env_vars import DATABASE

__all__ = (
    'SRC_DIR',
    'LOGS_FILE_PATH',
    'MOSCOW_UTC',
    'DATABASE_URI',
)

SRC_DIR = Path(__file__).parent.parent
LOGS_FILE_PATH = SRC_DIR.parent / 'logs.log'

MOSCOW_UTC = pendulum.timezone('Europe/Moscow')

DATABASE_URI = (f'postgresql+asyncpg://{DATABASE["user"]}:{DATABASE["password"]}'
                f'@{DATABASE["host"]}:{DATABASE["port"]}/{DATABASE["name"]}')
