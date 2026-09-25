import logging
import uuid
from datetime import datetime, timezone
from collections import deque
from typing import List, Dict, Any

# In-memory circular log buffer storing up to 500 recent log messages
MAX_LOG_ENTRIES = 500
log_buffer: deque = deque(maxlen=MAX_LOG_ENTRIES)

class SystemLogHandler(logging.Handler):
    """Custom Python logging handler that stores formatted log records in an in-memory buffer."""
    
    def emit(self, record: logging.LogRecord):
        try:
            log_entry = {
                "id": f"{record.created}-{record.msecs}-{uuid.uuid4().hex[:6]}",
                "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": self.format(record)
            }
            log_buffer.append(log_entry)
        except Exception:
            self.handleError(record)

def get_system_logs(limit: int = 200, level: str | None = None) -> List[Dict[str, Any]]:
    """Fetch recent system logs from memory buffer."""
    logs = list(log_buffer)
    if level and level.upper() != "ALL":
        logs = [log for log in logs if log["level"] == level.upper()]
    return list(reversed(logs[-limit:]))

def clear_system_logs():
    """Clear in-memory log entries."""
    log_buffer.clear()

# Global logger handler singleton
system_log_handler = SystemLogHandler()
system_log_handler.setFormatter(logging.Formatter("%(message)s"))
