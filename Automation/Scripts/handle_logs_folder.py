"""
Utility module to safely handle the logs folder by copying its contents
rather than moving it, to avoid issues with files being in use.
"""
import shutil
from pathlib import Path
import datetime

def safe_handle_logs():
    """Safely handle the logs folder without trying to move it."""
    base_path = Path('.')
    source_path = base_path / 'logs'
    target_dir = base_path / 'Automation' / 'Logs'
    
    print("="*60)
    print("LOGS FOLDER HANDLER")
    print("="*60)
    
    if not source_path.exists():
        print(f"ERROR: Source logs folder not found at {source_path}")
        return False
    
    # Create the target directory
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy log files rather than moving the folder
    log_files = list(source_path.glob('*.*'))
    print(f"Found {len(log_files)} log files")
    
    copied_files = 0
    errors = []
    
    for log_file in log_files:
        target_file = target_dir / log_file.name
        try:
            print(f"Copying {log_file.name}")
            shutil.copy2(log_file, target_file)
            copied_files += 1
        except (IOError, PermissionError) as e:
            error_msg = f"Could not copy {log_file.name}: {e}"
            print(f"ERROR: {error_msg}")
            errors.append(error_msg)
    
    # Create completion marker
    completion_file = target_dir / 'logs_handled.txt'
    with open(completion_file, 'w', encoding='utf-8') as f:
        f.write(f"Logs handling process completed on: {datetime.datetime.now()}\n")
        f.write(f"Copied {copied_files} of {len(log_files)} log files\n")
    
    print("\nRESULTS:")
    print(f"- Copied {copied_files} of {len(log_files)} log files to {target_dir}")
    
    if errors:
        print(f"- Encountered {len(errors)} errors")
        for error in errors:
            print(f"  - {error}")
    
    print("\nNEXT STEPS:")
    print("1. The logs folder has been preserved for safety")
    print("2. Log files have been copied to Automation/Logs/")
    print("3. You can manually delete the logs folder when convenient")
    print("   (after all scripts have completed)")
    
    # Create README in logs folder
    readme_path = source_path / "README_DELETE_WHEN_CONVENIENT.txt"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write("LOGS FOLDER\n")
        f.write("===========\n\n")
        f.write("This folder has been preserved during organization.\n")
        f.write("Its contents have been copied to Automation/Logs/\n\n")
        f.write("You can safely delete this folder when:\n")
        f.write("1. No scripts are currently running\n")
        f.write("2. You have verified the log files exist in Automation/Logs/\n\n")
        f.write(f"Generated on {datetime.datetime.now()}\n")
    
    return True

if __name__ == "__main__":
    safe_handle_logs()
