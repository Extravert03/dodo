from loguru import logger

import config

__all__ = (
    'logger',
)

logger.add(config.LOGS_FILE_PATH, retention='3 days', encoding='utf-8')
