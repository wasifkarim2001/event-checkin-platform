import contextvars
import json
import logging
from datetime import datetime, timezone

# Set by RequestLogMiddleware for the duration of one request.
request_id_var = contextvars.ContextVar("request_id", default=None)

# Attributes every LogRecord has; anything else came from extra= and becomes a field.
_SKIP = set(vars(logging.makeLogRecord({}))) | {"message", "asctime", "request", "server_time"}


class JsonFormatter(logging.Formatter):
    def format(self, record):
        entry = {
            "time": datetime.fromtimestamp(record.created, timezone.utc).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
        }
        entry.update({k: v for k, v in vars(record).items() if k not in _SKIP})
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, default=str)
