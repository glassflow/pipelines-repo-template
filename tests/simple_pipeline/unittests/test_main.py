from pipelines.simple_pipeline.handler import handler
import logging


def test_handler_new_field():
    log = logging.getLogger()
    data = handler(data={}, log=log)

    assert data == {"new_field": "new_value"}
