#!/usr/bin/env python3
"""
Maintenance scheduler for TransUnion PDF to JSON API.

Schedules and runs automated maintenance tasks including:
- Daily backups
- Old backup cleanup
- Log rotation
"""

import asyncio
import schedule
import time
from src.utils.backup import BackupManager
from src.utils.logging_config import api_logger


class MaintenanceScheduler:
    """
    Handles scheduled maintenance tasks for the application.
    
    Features:
    - Automated daily backups
    - Old backup cleanup (configurable retention)
    - Log file rotation (size-based)
    """
    
    def __init__(self):
        """Initialize maintenance scheduler with backup manager."""
        self.backup_manager = BackupManager()

    def run_daily_maintenance(self):
        """
        Run daily maintenance tasks.
        
        Tasks performed:
        1. Create backup of logs and temp files
        2. Cleanup old backups (7-day retention)
        3. Rotate large log files (>100MB)
        """
        try:
            api_logger.info("Starting daily maintenance tasks")
            
            # Create backup
            backup_path = self.backup_manager.create_backup()
            api_logger.info(f"Backup created: {backup_path}")
            
            # Cleanup old backups (keep last 7 days)
            self.backup_manager.cleanup_old_backups(keep_days=7)
            
            # Rotate logs if needed
            self.backup_manager.rotate_logs(max_size_mb=100)
            
            api_logger.info("Daily maintenance tasks completed successfully")
            
        except Exception as e:
            api_logger.error(
                "Daily maintenance tasks failed",
                extra={
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            )


def main():
    """
    Main function to schedule and run maintenance tasks.
    
    Schedules:
    - Daily maintenance at 2:00 AM
    """
    scheduler = MaintenanceScheduler()
    
    # Schedule daily maintenance at 2 AM
    schedule.every().day.at("02:00").do(scheduler.run_daily_maintenance)
    
    # Log startup
    api_logger.info(
        "Maintenance scheduler started",
        extra={"schedule": "Daily at 02:00"}
    )
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        api_logger.info("Maintenance scheduler stopped by user")
        
    except Exception as e:
        api_logger.error(
            "Maintenance scheduler error",
            extra={
                'error': str(e),
                'error_type': type(e).__name__
            }
        )
        raise


if __name__ == "__main__":
    main()
