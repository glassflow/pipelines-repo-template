import json
import logging

def handler(data: dict, log: logging.Logger):
    log.info("Echo: " + json.dumps(data))
    return data