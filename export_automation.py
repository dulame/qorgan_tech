#!/usr/bin/env python3
"""
Automated Password Check Data Exporter
This script automatically exports password check data from the database to Excel.
Can be run manually or scheduled with a task scheduler.
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.excel_exporter import PasswordCheckExporter
from modules.database import Database

# Create logs directory if it doesn't exist
Path('logs').mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/export.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PasswordCheckExportAutomation:
    """Automated export handler for password check data"""

    def __init__(self, output_dir='data'):
        """
        Initialize the automation.
        
        Args:
            output_dir (str): Directory to save Excel files
        """
        self.exporter = PasswordCheckExporter(output_dir)
        self.output_dir = output_dir
        self.db = Database()

    def export_all_data(self, filename='password_checks.xlsx'):
        """Export all password check data to Excel
        
        Args:
            filename (str): Excel filename (default: password_checks.xlsx - overwrites existing)
        """
        try:
            logger.info("Starting password check data export...")
            
            # Check if there's data to export
            checks = self.db.get_all_password_checks()
            if not checks:
                logger.warning("No password check data to export")
                return None
            
            logger.info(f"Found {len(checks)} password check records")
            
            # Export to Excel (overwrites existing file)
            filepath = self.exporter.export_to_excel(filename)
            logger.info(f"✅ Successfully exported to: {filepath}")
            
            return filepath
        
        except Exception as e:
            logger.error(f"❌ Error during export: {e}", exc_info=True)
            return None

    def export_user_data(self, user_id, filename=None):
        """
        Export data for a specific user.
        
        Args:
            user_id (int): User ID to export
            filename (str): Optional filename (default: password_checks_user_{user_id}.xlsx)
            
        Returns:
            str: Path to exported file or None if error
        """
        try:
            logger.info(f"Exporting data for user {user_id}...")
            
            # Check if user has data
            checks = self.db.get_password_checks(user_id)
            if not checks:
                logger.warning(f"No password check data for user {user_id}")
                return None
            
            logger.info(f"Found {len(checks)} records for user {user_id}")
            
            # Use default filename if not provided
            if filename is None:
                filename = f"password_checks_user_{user_id}.xlsx"
            
            # Export to Excel
            filepath = self.exporter.export_user_checks(user_id, filename)
            logger.info(f"✅ Successfully exported user {user_id} to: {filepath}")
            
            return filepath
        
        except Exception as e:
            logger.error(f"❌ Error exporting user {user_id}: {e}", exc_info=True)
            return None

    def _cleanup_old_files(self, keep_filepath):
        """Keep only the latest export file, delete others"""
        try:
            files = [f for f in os.listdir(self.output_dir) 
                    if f.startswith('password_checks_') and f.endswith('.xlsx')]
            
            for f in files:
                fpath = os.path.join(self.output_dir, f)
                if fpath != keep_filepath:
                    os.remove(fpath)
                    logger.info(f"Cleaned up old file: {f}")
        
        except Exception as e:
            logger.warning(f"Could not cleanup old files: {e}")

    def get_export_status(self):
        """Get current status of exported data"""
        try:
            all_checks = self.db.get_all_password_checks()
            total_checks = len(all_checks)
            unique_users = len(set(
                check['user_id'] for check in all_checks
            )) if all_checks else 0
            
            export_file = os.path.join(self.output_dir, 'password_checks.xlsx')
            export_exists = os.path.exists(export_file)
            file_size = os.path.getsize(export_file) if export_exists else 0
            
            status = {
                'total_checks': total_checks,
                'unique_users': unique_users,
                'export_file': export_file if export_exists else None,
                'file_size': file_size,
                'export_dir': self.output_dir
            }
            
            return status
        
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return None


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Automated Password Check Data Exporter'
    )
    parser.add_argument(
        '--mode',
        choices=['all', 'user', 'status'],
        default='all',
        help='Export mode: all (default), user (specific user), or status'
    )
    parser.add_argument(
        '--user-id',
        type=int,
        help='User ID (required when mode=user)'
    )
    parser.add_argument(
        '--output-dir',
        default='data',
        help='Output directory for Excel files (default: data)'
    )
    
    args = parser.parse_args()
    
    # Initialize automation
    automation = PasswordCheckExportAutomation(output_dir=args.output_dir)
    
    # Execute based on mode
    if args.mode == 'all':
        result = automation.export_all_data()
        if result:
            print(f"\n✅ Export completed: {result}")
        else:
            print("\n❌ Export failed")
    
    elif args.mode == 'user':
        if not args.user_id:
            print("❌ Error: --user-id required for user mode")
            sys.exit(1)
        result = automation.export_user_data(args.user_id)
        if result:
            print(f"\n✅ Export completed: {result}")
        else:
            print("\n❌ Export failed")
    
    elif args.mode == 'status':
        status = automation.get_export_status()
        if status:
            print("\n📊 Export Status:")
            print(f"  Total password checks: {status['total_checks']}")
            print(f"  Unique users: {status['unique_users']}")
            print(f"  Export directory: {status['export_dir']}")
            if status['export_file']:
                file_size_kb = status['file_size'] / 1024
                print(f"  Main export file: {status['export_file']} ({file_size_kb:.1f} KB)")
            else:
                print("  Main export file: Not yet created")
        else:
            print("\n❌ Could not retrieve status")


if __name__ == "__main__":
    main()
