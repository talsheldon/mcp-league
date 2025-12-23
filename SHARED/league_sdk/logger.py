"""Structured logging for league agents."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add extra fields
        if hasattr(record, "agent_id"):
            log_entry["agent_id"] = record.agent_id
        if hasattr(record, "message_type"):
            log_entry["message_type"] = record.message_type
        if hasattr(record, "match_id"):
            log_entry["match_id"] = record.match_id
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)


def setup_logger(
    name: str,
    log_dir: Optional[Path] = None,
    agent_id: Optional[str] = None,
    level: int = logging.INFO,
) -> logging.Logger:
    """Setup structured logger."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with JSON format
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{name}.log.jsonl"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
    
    # Add agent_id to all log records
    if agent_id:
        old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.agent_id = agent_id
            return record
        
        logging.setLogRecordFactory(record_factory)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get logger by name."""
    return logging.getLogger(name)

