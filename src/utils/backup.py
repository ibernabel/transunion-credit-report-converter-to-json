"""
Backup management utilities for TransUnion PDF to JSON API.

Provides backup creation, cleanup, and log rotation functionality.
"""

import shutil
from pathlib import Path
from datetime import datetime
import tarfile
import os
from src.utils.logging_config import api_logger


class BackupManager:
    """
    Manages backup operations for logs and temporary files.
    
    Features:
    - Automatic backup creation
    - Old backup cleanup
    - Log file rotation
    """
    
    def __init__(self):
        """Initialize backup manager with default directories."""
        self.backup_dir = Path(__file__).parent.parent.parent / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Directories to backup
        self.base_path = Path(__file__).parent.parent.parent
        self.dirs_to_backup = [
            self.base_path / "logs",
            self.base_path / "temp_uploads"
        ]

    def create_backup(self) -> Path:
        """
        Create a backup of important directories and files.
        
        Returns:
            Path: Path to the created backup file
            
        Raises:
            Exception: If backup creation fails
        """
        try:
            # Create timestamp for backup name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}.tar.gz"
            backup_path = self.backup_dir / backup_name

            # Create tar archive
            with tarfile.open(backup_path, "w:gz") as tar:
                # Add each directory to backup
                for dir_path in self.dirs_to_backup:
                    if dir_path.exists():
                        tar.add(dir_path, arcname=dir_path.name)

            # Log successful backup
            backup_size = os.path.getsize(backup_path)
            api_logger.info(
                "Backup created successfully",
                extra={
                    'backup_file': str(backup_path),
                    'size_bytes': backup_size,
                    'size_mb': f"{backup_size / (1024 * 1024):.2f}"
                }
            )

            return backup_path

        except Exception as e:
            # Log backup failure
            api_logger.error(
                "Backup creation failed",
                extra={
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            )
            raise

    def cleanup_old_backups(self, keep_days: int = 7):
        """
        Remove backups older than specified days.
        
        Args:
            keep_days: Number of days to keep backups for (default: 7)
        """
        try:
            current_time = datetime.now().timestamp()
            removed_count = 0
            
            # Check each file in backup directory
            for backup_file in self.backup_dir.glob("backup_*.tar.gz"):
                file_age_seconds = current_time - os.path.getctime(backup_file)
                if file_age_seconds > (keep_days * 24 * 3600):  # Convert days to seconds
                    backup_file.unlink()
                    removed_count += 1
                    api_logger.info(
                        "Removed old backup file",
                        extra={
                            'file': str(backup_file),
                            'age_days': file_age_seconds / (24 * 3600)
                        }
                    )
            
            if removed_count > 0:
                api_logger.info(
                    f"Cleanup completed: {removed_count} old backup(s) removed"
                )

        except Exception as e:
            api_logger.error(
                "Backup cleanup failed",
                extra={
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            )
            raise

    def rotate_logs(self, max_size_mb: int = 100):
        """
        Rotate log files if they exceed maximum size.
        
        Args:
            max_size_mb: Maximum size of log files in megabytes (default: 100)
        """
        try:
            log_dir = self.base_path / "logs"
            if not log_dir.exists():
                return

            rotated_count = 0
            max_size_bytes = max_size_mb * 1024 * 1024
            
            for log_file in log_dir.glob("*.log"):
                # Check if file exceeds max size
                file_size = os.path.getsize(log_file)
                if file_size > max_size_bytes:
                    # Create new filename with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    new_name = log_file.with_name(f"{log_file.stem}_{timestamp}.log")
                    
                    # Rename current log file
                    shutil.move(log_file, new_name)
                    
                    # Create new empty log file
                    log_file.touch()
                    
                    rotated_count += 1
                    api_logger.info(
                        "Log file rotated",
                        extra={
                            'old_file': str(log_file),
                            'new_file': str(new_name),
                            'size_mb': f"{file_size / (1024 * 1024):.2f}"
                        }
                    )
            
            if rotated_count > 0:
                api_logger.info(
                    f"Log rotation completed: {rotated_count} file(s) rotated"
                )

        except Exception as e:
            api_logger.error(
                "Log rotation failed",
                extra={
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            )
            raise
