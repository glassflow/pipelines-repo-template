import logging


def handler(data: dict, log: logging.Logger):
    data["new_filed"] = "a value"
    log.info(data)
    return data
