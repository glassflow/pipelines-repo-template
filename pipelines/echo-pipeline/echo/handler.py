import logging


def handler(data: dict, log: logging.Logger):
    log.info(data)
    return data
