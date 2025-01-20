import logging


def handler(data: dict, log: logging.Logger):
    data["new_filed"] = "A value"
    log.info(data)
    return data
