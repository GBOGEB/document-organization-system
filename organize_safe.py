import os
import shutil
from pathlib import Path
import subprocess
import json
import logging
from datetime import datetime
import sys

# Import the Unicode fix utility
try:
    from fix_unicode_console import fix_windows_console, safe_print
    fix_windows_console()
except ImportError:
    def safe_print(text):
        try:
            print(text)
        except UnicodeEncodeError:
            print(text.encode('ascii', 'replace').decode('ascii'))

def setup_safe_logging():
    """Setup logging that works safely on Windows."""
    log_dir = Path(r'C:\Users\gbonthuy\OneDrive - Studiecentrum voor Kernenergie\Documents\logs')
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'reorganization_{timestamp}.log'
    
    # Create a custom formatter that strips emojis for file logging
    class SafeFormatter(logging.Formatter):
        def format(self, record):
            # Remove common emojis for file logging
            msg = super().format(record)
            emoji_replacements = {
                '📊': '[CHART]',
                '📁': '[FOLDER]', 
                '📂': '[FOLDER]',
                '✅': '[OK]',
                '❌': '[ERROR]',
                '⚠️': '[WARNING]',
                '🔧': '[TOOL]',
                '🔄': '[PROCESS]',
                '📋': '[LIST]',
                '📸': '[SNAPSHOT]',
                '💾': '[SAVE]',
                '🚀': '[START]',
                '🎉': '[SUCCESS]'
            }
            for emoji, replacement in emoji_replacements.items():
                msg = msg.replace(emoji, replacement)
            return msg
    
    # File handler with safe formatter
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(SafeFormatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    # Console handler (can use emojis)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler],
        force=True
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting reorganization process - Log file: %s", log_file)
    return logger, log_file

def quick_reorganization_summary():
    """Quick summary without Unicode issues."""
    base_path = Path(r'C:\Users\gbonthuy\OneDrive - Studiecentrum voor Kernenergie\Documents')
    
    safe_print("="*60)
    safe_print("DOCUMENT ORGANIZATION SYSTEM - STATUS CHECK")
    safe_print("="*60)
    
    # Count organized vs unorganized folders
    organized_folders = ['Development', 'Documents', 'Resources', 'Automation', 'Archive']
    organized_count = 0
    unorganized_folders = []
    total_items = 0
    
    for item in base_path.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            item_count = len(list(item.rglob('*')))
            total_items += item_count
            
            if item.name in organized_folders:
                organized_count += 1
                safe_print(f"[OK] {item.name}: {item_count:,} items")
            else:
                unorganized_folders.append((item.name, item_count))
    
    safe_print(f"\nORGANIZATION STATUS: {organized_count}/5 folders organized")
    
    if unorganized_folders:
        safe_print(f"\nUNORGANIZED FOLDERS ({len(unorganized_folders)}):")
        for name, count in sorted(unorganized_folders, key=lambda x: x[1], reverse=True):
            safe_print(f"  {name}: {count:,} items")
    else:
        safe_print("\n[SUCCESS] ALL FOLDERS ORGANIZED!")
    
    total_unorganized = sum(count for _, count in unorganized_folders)
    safe_print(f"\nTOTAL ORGANIZED ITEMS: {total_items - total_unorganized:,}")
    safe_print(f"TOTAL UNORGANIZED ITEMS: {total_unorganized:,}")
    safe_print(f"GRAND TOTAL: {total_items:,}")
    
    if organized_count == 5 and not unorganized_folders:
        safe_print("\n[COMPLETE] 100% ORGANIZATION ACHIEVED!")
        completion_percentage = 100.0
    else:
        completion_percentage = (total_items - total_unorganized) / total_items * 100
        safe_print(f"\nCOMPLETION: {completion_percentage:.1f}%")
    
    # Recommendations
    safe_print("\nRECOMMENDATIONS:")
    if organized_count == 0:
        safe_print("  1. Run: python organize_safe.py --setup")
    elif unorganized_folders:
        safe_print("  1. Run: python organize_remaining_folders.py")
        safe_print("  2. Use: python run_organization_safe.py --auto")
    else:
        safe_print("  1. System fully organized - no action needed!")
        safe_print("  2. Use: python run_organization_safe.py for maintenance")
    
    return organized_count, len(unorganized_folders), total_unorganized, completion_percentage

def create_safe_structure():
    """Create folder structure safely."""
    base_path = Path(r'C:\Users\gbonthuy\OneDrive - Studiecentrum voor Kernenergie\Documents')
    logger = logging.getLogger(__name__)
    
    structure = {
        'Development': {
            'Active_Projects': 'Current working projects',
            'Git_Repositories': 'Version controlled projects', 
            'Learning': 'Tutorials and learning materials',
            'Tools_Scripts': 'Automation tools and scripts'
        },
        'Documents': {
            'Work': {
                'Projects': 'Active work projects',
                'Requirements': 'Technical requirements', 
                'Meetings': 'Meeting notes and minutes',
                'Technical_Specs': 'Technical specifications'
            },
            'Personal': 'Personal documents',
            'References': 'Reference materials and documentation'
        },
        'Resources': {
            'Media': 'Images, videos, audio files',
            'Templates': 'Reusable templates',
            'Data_Sources': 'Data files and sources'
        },
        'Automation': {
            'Scripts': 'Organization and maintenance scripts',
            'Logs': 'Process logs and history', 
            'Backups': 'Backup files and snapshots'
        }
    }
    
    def create_folders(structure, parent_path, level=0):
        for folder_name, description in structure.items():
            folder_path = parent_path / folder_name
            folder_path.mkdir(exist_ok=True)
            
            indent = "  " * level
            if isinstance(description, dict):
                logger.info(f"{indent}Created folder: {folder_path.name}/")
                safe_print(f"{indent}[FOLDER] Created: {folder_path.name}/")
                create_folders(description, folder_path, level + 1)
            else:
                logger.info(f"{indent}Created: {folder_path.name} ({description})")
                safe_print(f"{indent}[OK] Created: {folder_path.name}")
    
    logger.info("Creating enhanced folder structure...")
    safe_print("\nCreating organized folder structure...")
    create_folders(structure, base_path)
    safe_print("[SUCCESS] Folder structure created!")

def show_system_health():
    """Show system health dashboard."""
    safe_print("="*60)
    safe_print("SYSTEM HEALTH DASHBOARD")
    safe_print("="*60)
    
    base_path = Path(r'C:\Users\gbonthuy\OneDrive - Studiecentrum voor Kernenergie\Documents')
    
    # Check main components
    components = {
        'Organization Scripts': [
            'organize_remaining_folders.py',
            'run_organization_safe.py',
            'organize_safe.py'
        ],
        'Status Scripts': [
            'system_status.py',
            'quick_summary_v2.py'
        ],
        'Documentation': [
            'ORGANIZATION_COMPLETE.md',
            'ORGANIZATION_PROCESS.md',
            'PIPELINE_VISUAL.md'
        ],
        'System Folders': [
            'Automation/Scripts',
            'Automation/Logs',
            'Automation/Backups'
        ]
    }
    
    health_score = 0
    total_checks = 0
    
    for category, items in components.items():
        safe_print(f"\n{category}:")
        category_health = 0
        
        for item in items:
            item_path = base_path / item
            if item_path.exists():
                safe_print(f"  [OK] {item}")
                category_health += 1
            else:
                safe_print(f"  [MISSING] {item}")
            total_checks += 1
        
        health_score += category_health
        safe_print(f"  Status: {category_health}/{len(items)} components available")
    
    overall_health = (health_score / total_checks) * 100
    safe_print(f"\nOVERALL SYSTEM HEALTH: {overall_health:.1f}%")
    
    if overall_health >= 90:
        safe_print("[EXCELLENT] System is fully operational")
    elif overall_health >= 70:
        safe_print("[GOOD] System is mostly operational")
    elif overall_health >= 50:
        safe_print("[FAIR] Some components missing")
    else:
        safe_print("[POOR] Major components missing")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        action = sys.argv[1]
        
        if action == "--setup":
            logger, log_file = setup_safe_logging()
            safe_print("Setting up organization system...")
            create_safe_structure()
            safe_print(f"\n[SUCCESS] Setup complete! Log: {log_file}")
            
        elif action == "--status":
            organized, unorganized, total_unorg, completion = quick_reorganization_summary()
            
        elif action == "--health":
            show_system_health()
            
        elif action == "--help":
            safe_print("Organization System Commands:")
            safe_print("  --status    Show organization status")
            safe_print("  --setup     Create folder structure")
            safe_print("  --health    Show system health")
            safe_print("  --help      Show this help")
            
        else:
            safe_print("Unknown option. Use --help for available commands.")
    else:
        # Default: show summary
        quick_reorganization_summary()
