import json
import logging

from app.logging_config import JsonFormatter, request_id_var


def test_json_formatter_includes_the_request_id_and_extra_fields() -> None:
    token = request_id_var.set("trace-42")
    record = logging.makeLogRecord({"msg": "hello", "levelno": logging.INFO, "levelname": "INFO", "name": "test"})
    record.status_code = 200
    record.password = "should-never-appear"

    entry = json.loads(JsonFormatter().format(record))
    request_id_var.reset(token)

    assert entry["message"] == "hello"
    assert entry["request_id"] == "trace-42"
    assert entry["status_code"] == 200
    assert "password" not in entry
    assert "should-never-appear" not in json.dumps(entry)