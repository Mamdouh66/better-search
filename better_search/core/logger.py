from loguru import logger
import sys


def get_logger(
    log_file="logs/app.log", log_level="INFO", rotation="10 MB", retention="10 days"
):
    logger.remove()
    logger.add(sys.stderr, level=log_level)
    logger.add(
        log_file,
        serialize=True,
        level=log_level,
        rotation=rotation,
        retention=retention,
    )
    return logger
