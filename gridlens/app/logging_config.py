from __future__ import annotations

import json
import logging
from collections.abc import Mapping, Sequence

from gridlens.app.config import Settings

_REDACT_TERMS = ("key", "token", "secret", "password")
_DEFAULT_FIELDS = (
    "request_id",
    "operation",
    "duration_ms",
    "scenario_id",
    "data_source",
    "forecast_method",
    "retrieval_count",
    "error_category",
)


def _redact(value):
    if isinstance(value, str):
        return "[REDACTED]" if any(term in value.lower() for term in _REDACT_TERMS) else value
    if isinstance(value, Mapping):
        return {str(key): _redact(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [_redact(item) for item in value]
    return value


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for field in _DEFAULT_FIELDS:
            payload[field] = _redact(getattr(record, field, None))
        return json.dumps(payload, default=str)


def get_logger(name: str) -> logging.Logger:
    settings = Settings()
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    logger.setLevel(settings.log_level.upper())
    logger.propagate = False
    return logger
