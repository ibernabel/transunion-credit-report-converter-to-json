"""
Logging configuration for TransUnion PDF to JSON API.

Provides structured JSON logging with system metrics monitoring.
"""

import logging
import sys
import psutil
from pathlib import Path
from pythonjsonlogger import jsonlogger
from datetime import datetime
from typing import Dict, Any


# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter that adds timestamp and level fields."""
    
    def add_fields(
        self, 
        log_record: Dict[str, Any], 
        record: logging.LogRecord, 
        message_dict: Dict[str, Any]
    ) -> None:
        """Add custom fields to log records."""
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['module'] = record.module


def get_system_metrics() -> Dict[str, float]:
    """
    Get current system resource usage metrics.
    
    Returns:
        dict: System metrics including CPU, memory, and disk usage percentages
    """
    try:
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage_percent': psutil.disk_usage('/').percent
        }
    except Exception as e:
        # Fallback in case psutil fails in container
        return {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'disk_usage_percent': 0.0,
            'error': str(e)
        }


def setup_logging() -> logging.Logger:
    """
    Configure application logging with JSON formatting.
    
    Returns:
        logging.Logger: Configured API logger
    """
    # Create logger
    logger = logging.getLogger("transunion_api")
    logger.setLevel(logging.INFO)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(LOGS_DIR / "api.log")
    
    # Create formatter
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(module)s %(message)s'
    )

    # Set formatter for handlers
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def setup_monitoring_logger() -> logging.Logger:
    """
    Configure system monitoring logging.
    
    Returns:
        logging.Logger: Configured monitoring logger
    """
    logger = logging.getLogger("monitoring")
    logger.setLevel(logging.INFO)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Create handler for monitoring logs
    file_handler = logging.FileHandler(LOGS_DIR / "monitoring.log")
    
    # Create formatter
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )

    # Set formatter for handler
    file_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(file_handler)

    return logger


# Initialize loggers
api_logger = setup_logging()
monitoring_logger = setup_monitoring_logger()


def log_system_metrics() -> None:
    """Log current system metrics to monitoring log."""
    metrics = get_system_metrics()
    monitoring_logger.info("System metrics", extra=metrics)
