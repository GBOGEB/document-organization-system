"""
Unified setup script for the document organization system.
Provides a streamlined installation, configuration and verification process.
"""
import os
import sys
import shutil
import subprocess
import time
from pathlib import Path
import datetime
import json
import importlib.util

# Check if a module is available before importing it
def is_module_available(module_name):
    return importlib.util.find_spec(module_name) is not None

# Try to import colorama for cross-platform colored output
COLOR_SUPPORT = False
try:
    if is_module_available("colorama"):
        import colorama
        colorama.init()
        COLOR_SUPPORT = True
except:
    pass

# Color codes
class Colors:
    BLUE = '\033[94m' if COLOR_SUPPORT else ''
    GREEN = '\033[92m' if COLOR_SUPPORT else ''
    YELLOW = '\033[93m' if COLOR_SUPPORT else ''
    RED = '\033[91m' if COLOR_SUPPORT else ''
    BOLD = '\033[1m' if COLOR_SUPPORT else ''
    END = '\033[0m' if COLOR_SUPPORT else ''

def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'=' * 70}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text.center(70)}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'=' * 70}{Colors.END}")

def print_step(step_num, total_steps, description):
    """Print a formatted step indicator."""
    print(f"\n{Colors.GREEN}{Colors.BOLD}[STEP {step_num}/{total_steps}] {description}{Colors.END}")

def print_success(text):
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_warning(text):
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_error(text):
    """Print an error message."""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def run_script(script_name, args=None):
    """Run another Python script and capture its output."""
    cmd = [sys.executable, script_name]
    if args:
        if isinstance(args, list):
            cmd.extend(args)
        else:
            cmd.append(args)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, f"Error executing {script_name}: {e.stderr}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def create_or_ensure_script(script_name, script_content):
    """Create a script file if it doesn't exist or update if needed."""
    if os.path.exists(script_name):
        print_success(f"Found existing {script_name}")
        return True
    
    try:
        with open(script_name, 'w', encoding='utf-8') as f:
            f.write(script_content)
        print_success(f"Created {script_name}")
        return True
    except Exception as e:
        print_error(f"Failed to create {script_name}: {str(e)}")
        return False

def check_environment():
    """Check and set up the Python environment."""
    print_step(1, 7, "Checking environment")
    
    # Python version check
    py_version = sys.version_info
    if py_version.major < 3 or (py_version.major == 3 and py_version.minor < 6):
        print_warning(f"Python {py_version.major}.{py_version.minor} detected. Version 3.6+ is recommended.")
    else:
        print_success(f"Python {py_version.major}.{py_version.minor} detected")
    
    # Check required modules
    required_modules = [
        "pathlib", "shutil", "datetime", "json", "logging"
    ]
    
    missing_modules = []
    for module in required_modules:
        if not is_module_available(module):
            missing_modules.append(module)
    
    if missing_modules:
        print_warning(f"Missing modules: {', '.join(missing_modules)}")
        print_warning("Some features may not work correctly.")
    else:
        print_success("All required Python modules are available")
    
    # Create a basic fix_unicode_console.py if doesn't exist
    create_or_ensure_script("fix_unicode_console.py", """
# filepath: fix_unicode_console.py
import os
import sys

def fix_windows_console():
    \"\"\"Fix Windows console to properly display Unicode characters.\"\"\"
    if sys.platform == 'win32':
        try:
            os.system('chcp 65001 > nul')
            if sys.stdout.encoding and isinstance(sys.stdout.encoding, str) and sys.stdout.encoding.lower() != 'utf-8':
                os.environ['PYTHONIOENCODING'] = 'utf-8'
            return True
        except Exception as e:
            print(f"Warning: Could not configure console for Unicode: {e}")
    return False

def safe_print(text):
    \"\"\"Print text safely, handling Unicode encoding errors.\"\"\"
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))

if __name__ == '__main__':
    if fix_windows_console():
        print("Unicode support configured for Windows console")
    safe_print("Test: ✅ ✓ ❌ ✗ 📁 📊 😊 🚀")
""")
    
    try:
        from fix_unicode_console import fix_windows_console
        fix_windows_console()
        print_success("Unicode support configured")
    except:
        print_warning("Could not configure Unicode support. Some characters may not display correctly.")
    
    return True

def create_folder_structure():
    """Create the main folder structure."""
    print_step(2, 7, "Creating folder structure")
    
    base_path = Path(os.getcwd())
    
    # Main folder structure with descriptions
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
        },
        'Archive': {
            'Miscellaneous': 'General archived content',
        }
    }
    
    # Create the folders
    def create_folders(struct, current_path, level=0):
        created = 0
        for name, content in struct.items():
            folder_path = current_path / name
            
            try:
                folder_path.mkdir(exist_ok=True)
                created += 1
                
                if isinstance(content, dict):
                    indent = "  " * level
                    print(f"{indent}📂 Created: {name}/")
                    created += create_folders(content, folder_path, level + 1)
            except Exception as e:
                print_error(f"Error creating {name} folder: {str(e)}")
                
        return created
    
    total_created = create_folders(structure, base_path)
    print_success(f"Created {total_created} folders and subfolders")
    
    return True

def setup_scripts():
    """Create or update essential scripts."""
    print_step(3, 7, "Setting up organization scripts")
    
    # Check for existing organize_safe.py
    if not os.path.exists("organize_safe.py"):
        print_warning("organize_safe.py not found. Creating a basic version.")
        # Create a simplified version - in a real implementation, this would be more comprehensive
        create_or_ensure_script("organize_safe.py", """
# filepath: organize_safe.py
from pathlib import Path
import sys

try:
    from fix_unicode_console import fix_windows_console, safe_print
    fix_windows_console()
except ImportError:
    def safe_print(text):
        try:
            print(text)
        except UnicodeEncodeError:
            print(text.encode('ascii', 'replace').decode('ascii'))

def quick_status():
    \"\"\"Show current organization status.\"\"\"
    base_path = Path('.')
    
    safe_print("=" * 60)
    safe_print("DOCUMENT ORGANIZATION SYSTEM - STATUS CHECK")
    safe_print("=" * 60)
    
    # Organized and check folders
    organized_folders = ['Development', 'Documents', 'Resources', 'Automation', 'Archive']
    organized_count = 0
    unorganized = []
    
    for item in base_path.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            if item.name in organized_folders:
                organized_count += 1
                safe_print(f"[OK] {item.name}")
            else:
                unorganized.append(item.name)
    
    safe_print(f"\\nORGANIZATION STATUS: {organized_count}/{len(organized_folders)} folders organized")
    
    if unorganized:
        safe_print(f"\\nUNORGANIZED FOLDERS ({len(unorganized)}):")
        for name in unorganized:
            safe_print(f"  {name}")
    
    if organized_count == len(organized_folders) and not unorganized:
        safe_print("\\n[COMPLETE] 100% ORGANIZATION ACHIEVED!")
    else:
        safe_print(f"\\nRun: python {sys.argv[0]} --setup to create folder structure")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        safe_print("Setting up folder structure... (Not implemented in basic version)")
        safe_print("Use setup_organization.py instead")
    else:
        quick_status()
""")
    else:
        print_success("organize_safe.py already exists")

    # Check/create status_check.py
    create_or_ensure_script("status_check.py", """
# filepath: status_check.py
from pathlib import Path

def check_organization_status():
    \"\"\"Simple organization status checker.\"\"\"
    base_path = Path('.')
    
    print("=" * 60)
    print("DOCUMENT ORGANIZATION SYSTEM - STATUS CHECK")
    print("=" * 60)
    
    # Count organized vs unorganized folders
    organized_folders = ['Development', 'Documents', 'Resources', 'Automation', 'Archive']
    organized_count = 0
    unorganized_folders = []
    total_items = 0
    
    for item in base_path.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            try:
                item_count = sum(1 for _ in item.rglob('*'))
                total_items += item_count
                
                if item.name in organized_folders:
                    organized_count += 1
                    print(f"[OK] {item.name}: {item_count:,} items")
                else:
                    unorganized_folders.append((item.name, item_count))
            except Exception as e:
                print(f"[ERROR] Could not scan {item.name}: {e}")
    
    print(f"\\nORGANIZATION STATUS: {organized_count}/{len(organized_folders)} folders organized")
    
    if unorganized_folders:
        print(f"\\nUNORGANIZED FOLDERS ({len(unorganized_folders)}):")
        for name, count in sorted(unorganized_folders, key=lambda x: x[1], reverse=True):
            print(f"  {name}: {count:,} items")
    else:
        print("\\n[SUCCESS] ALL FOLDERS ORGANIZED!")
    
    total_unorganized = sum(count for _, count in unorganized_folders)
    print(f"\\nTOTAL ORGANIZED ITEMS: {total_items - total_unorganized:,}")
    print(f"TOTAL UNORGANIZED ITEMS: {total_unorganized:,}")
    print(f"GRAND TOTAL: {total_items:,}")
    
    completion = 100.0 if not unorganized_folders else (total_items - total_unorganized) / total_items * 100
    print(f"\\nCOMPLETION: {completion:.1f}%")

if __name__ == "__main__":
    check_organization_status()
""")
    
    # Create handle_logs_folder.py for the log folder issue
    create_or_ensure_script("handle_logs_folder.py", """
# filepath: handle_logs_folder.py
\"\"\"
Utility module to safely handle the logs folder by copying its contents
rather than moving it, to avoid issues with files being in use.
\"\"\"
import shutil
from pathlib import Path
import datetime

def safe_handle_logs():
    \"\"\"Safely handle the logs folder without trying to move it.\"\"\"
    base_path = Path('.')
    source_path = base_path / 'logs'
    target_dir = base_path / 'Automation' / 'Logs'
    
    print("=" * 60)
    print("LOGS FOLDER HANDLER")
    print("=" * 60)
    
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
        f.write(f"Logs handling process completed on: {datetime.datetime.now()}\\n")
        f.write(f"Copied {copied_files} of {len(log_files)} log files\\n")
    
    print("\\nRESULTS:")
    print(f"- Copied {copied_files} of {len(log_files)} log files to {target_dir}")
    
    if errors:
        print(f"- Encountered {len(errors)} errors")
        for error in errors:
            print(f"  - {error}")
    
    # Create README in logs folder explaining what to do
    readme_path = source_path / "README_DELETE_WHEN_CONVENIENT.txt"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write("LOGS FOLDER\\n")
        f.write("===========\\n\\n")
        f.write("This folder has been preserved during organization.\\n")
        f.write("Its contents have been copied to Automation/Logs/\\n\\n")
        f.write("You can safely delete this folder when:\\n")
        f.write("1. No scripts are currently running\\n")
        f.write("2. You have verified the log files exist in Automation/Logs/\\n\\n")
        f.write(f"Generated on {datetime.datetime.now()}\\n")
    
    print("\\nNEXT STEPS:")
    print("1. Close all command prompts/terminals")
    print("2. Delete the logs folder manually") 
    print("3. Your organization will be 100% complete!")
    
    return True

if __name__ == "__main__":
    safe_handle_logs()
""")

    # Copy essential scripts to Automation/Scripts
    automation_scripts_path = Path("Automation/Scripts")
    automation_scripts_path.mkdir(exist_ok=True, parents=True)
    
    scripts_to_copy = [
        "organize_safe.py", 
        "status_check.py",
        "handle_logs_folder.py",
        "fix_unicode_console.py",
        "setup_organization.py"
    ]
    
    for script in scripts_to_copy:
        if os.path.exists(script):
            try:
                shutil.copy2(script, automation_scripts_path / script)
                print_success(f"Copied {script} to Automation/Scripts/")
            except Exception as e:
                print_warning(f"Could not copy {script}: {str(e)}")
    
    return True

def configure_github_integration(setup_github=False):
    """Set up GitHub integration if requested."""
    print_step(4, 7, "GitHub integration setup")
    
    # Check if Git is installed
    try:
        subprocess.run(['git', '--version'], check=True, capture_output=True)
        git_available = True
    except:
        git_available = False
        print_warning("Git is not installed or not in PATH. GitHub integration will be limited.")
    
    # Create git_integration.py script
    create_or_ensure_script("git_integration.py", """
# filepath: git_integration.py
\"\"\"GitHub integration for document organization.\"\"\"
import os
import sys
import subprocess
import json
from pathlib import Path
import datetime

def is_git_installed():
    \"\"\"Check if Git is installed.\"\"\"
    try:
        subprocess.run(['git', '--version'], check=True, capture_output=True)
        return True
    except:
        return False

def setup_github_repo():
    \"\"\"Interactive setup for GitHub repository.\"\"\"
    if not is_git_installed():
        print("❌ Git is not installed. Please install Git first.")
        return False
    
    print("\\n" + "="*60)
    print("GITHUB REPOSITORY SETUP")
    print("="*60)
    
    # Ask for user input
    username = input("GitHub username: ")
    repo_name = input("Repository name [document-organization-system]: ").strip() or "document-organization-system"
    token = input("GitHub Personal Access Token: ")
    is_private = input("Make repository private? (y/N): ").lower().startswith('y')
    
    if not username or not token:
        print("❌ Username and token are required.")
        return False
    
    # Create repo on GitHub using GitHub API
    try:
        import json
        auth = f"{username}:{token}"
        data = {
            "name": repo_name,
            "private": is_private,
            "description": "Document Organization System - Automated file management"
        }
        
        curl_cmd = [
            'curl', '-X', 'POST',
            '-u', auth,
            'https://api.github.com/user/repos',
            '-d', json.dumps(data),
            '-H', 'Accept: application/vnd.github.v3+json'
        ]
        
        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        
        # Initialize Git repo and push
        subprocess.run(['git', 'init'], check=True)
        with open('.gitignore', 'w') as f:
            f.write("# Organization system gitignore\\n*.log\\nlogs/\\n*.tmp\\n")
        
        # Set up remote
        repo_url = f"https://{username}:{token}@github.com/{username}/{repo_name}.git"
        subprocess.run(['git', 'remote', 'add', 'origin', repo_url], check=True)
        
        # Stage and commit files
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', "Initial setup of document organization system"], check=True)
        
        # Push to GitHub
        subprocess.run(['git', 'push', '-u', 'origin', 'master'], check=True)
        
        print(f"\\n✅ GitHub repository created and initial files pushed!")
        print(f"Repository URL: https://github.com/{username}/{repo_name}")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up GitHub repository: {str(e)}")
        return False

if __name__ == "__main__":
    if not is_git_installed():
        print("Git is not installed. Please install Git to use GitHub integration.")
        sys.exit(1)
        
    setup_github_repo()
""")
    
    if not git_available:
        print_warning("GitHub integration setup skipped - Git not available")
        return False
    
    if setup_github:
        print("\nSetting up GitHub repository...")
        success, output = run_script("git_integration.py")
        if success:
            print_success("GitHub repository setup completed")
        else:
            print_warning(f"GitHub setup encountered issues: {output}")
        return success
    else:
        print_success("GitHub integration script created")
        print("To set up GitHub repository later, run: python git_integration.py")
        return True

def create_docs_and_reports():
    """Create documentation and reports."""
    print_step(5, 7, "Creating documentation")
    
    # Create WORKFLOW_DIAGRAM.md
    create_or_ensure_script("WORKFLOW_DIAGRAM.md", """
# Document Organization Workflow & Execution Pipeline

## 📊 Complete Execution Pipeline

```
┌───────────────────────────────────────────────────────────────────┐
│                DOCUMENT ORGANIZATION PIPELINE                     │
└───────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────┐    ┌──────────────┐    ┌──────────────┐    ┌─────────────────┐
│  INITIALIZATION │───▶│   ANALYSIS   │───▶│ ORGANIZATION │───▶│  VERIFICATION   │
└─────────────────┘    └──────────────┘    └──────────────┘    └─────────────────┘
        │                     │                   │                    │
        ▼                     ▼                   ▼                    ▼
┌─────────────────┐    ┌──────────────┐    ┌──────────────┐    ┌─────────────────┐
│• organize_safe  │    │• status_check│    │• organize_   │    │• completion_    │
│  --setup        │    │• quick_      │    │  remaining_  │    │  report        │
│• Initial folder │    │  summary_v2  │    │  folders     │    │• status_check  │
│  structure      │    │• Folder scan │    │• File moves  │    │• Final cleanup │
└─────────────────┘    └──────────────┘    └──────────────┘    └─────────────────┘
```

## Command Guide

* `organize_safe.py --status` - Check organization status
* `status_check.py` - Detailed organization report
* `handle_logs_folder.py` - Handle active log files
* `git_integration.py` - GitHub version control setup
""")
    
    # Create FINAL_STEP.md
    create_or_ensure_script("FINAL_STEP.md", f"""
# 🏁 Final Step to 100% Organization

## Current Status

```
┌─────────────────────────────────────────────────────────────┐
│                ORGANIZATION COMPLETION                     │
├─────────────────────────────────────────────────────────────┤
│ ✅ All main folders created and configured                 │
│ ✅ All systems operational                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Final Steps

1. **Run handle_logs_folder.py** to copy log files safely:
   ```
   python handle_logs_folder.py
   ```

2. **Close all command windows**

3. **Delete the logs folder manually**

After these steps, your organization will be 100% complete!

## System Features

Your document system now includes:

- **5 main organized folders**:
  - **Development** - Code, projects, learning materials
  - **Documents** - Work & personal documentation
  - **Resources** - Templates, media, data sources
  - **Automation** - Scripts & system maintenance
  - **Archive** - Long-term storage

- **Maintenance tools**:
  - `organize_safe.py --status` - Check organization status
  - `status_check.py` - Detailed organization report
  - `git_integration.py` - GitHub integration

---

**Generated on**: {datetime.datetime.now().strftime('%Y-%m-%d')}  
**Project status**: Ready for use
""")
    
    print_success("Documentation created")
    return True

def run_initial_organization():
    """Run initial organization steps."""
    print_step(6, 7, "Running initial organization")
    
    # Run status_check.py
    print("\nChecking current organization status:")
    success, output = run_script("status_check.py")
    if success:
        print(output)
    else:
        print_warning(f"Status check failed: {output}")
    
    # If logs folder exists, run handle_logs_folder.py
    if os.path.exists("logs"):
        print("\nHandling logs folder:")
        success, logs_output = run_script("handle_logs_folder.py")
        if success:
            print(logs_output)
        else:
            print_warning(f"Logs folder handling encountered issues: {logs_output}")
    
    return True

def complete_setup():
    """Complete setup and show final instructions."""
    print_step(7, 7, "Completing setup")
    
    # Create a completion marker
    completion_file = "ORGANIZATION_SETUP_COMPLETE.txt"
    with open(completion_file, "w", encoding="utf-8") as f:
        f.write(f"Document Organization System Setup Completed\n")
        f.write(f"Date: {datetime.datetime.now()}\n\n")
        f.write("Next Steps:\n")
        f.write("1. Run: python status_check.py to see organization status\n")
        f.write("2. Run: python handle_logs_folder.py if logs folder exists\n")
        f.write("3. Set up GitHub integration: python git_integration.py\n")
    
    print_success(f"Setup completion recorded in {completion_file}")
    
    # Show final instructions
    print_header("SETUP COMPLETE")
    print("\nYour document organization system is ready to use!")
    print("\nEssential commands:")
    print("  python status_check.py           - Check organization status")
    print("  python handle_logs_folder.py     - Handle logs folder (if exists)")
    print("  python git_integration.py        - Set up GitHub integration")
    
    return True

def confirm_action(prompt):
    """Ask for user confirmation."""
    response = input(f"{prompt} (y/n): ").lower().strip()
    return response == 'y' or response == 'yes'

def main():
    """Main setup process."""
    print_header("DOCUMENT ORGANIZATION SYSTEM SETUP")
    
    # Welcome message
    print("\nThis script will set up a complete document organization system with:")
    print("  • Professional folder structure")
    print("  • Status checking tools")
    print("  • Logs handling tools")
    print("  • GitHub integration (optional)")
    print("  • Documentation and workflows")
    
    # Check if current directory is appropriate
    if not confirm_action("\nSet up document organization in current directory?"):
        print("Setup cancelled. Please run this script in your target directory.")
        return
    
    # Ask about GitHub integration
    setup_github = confirm_action("\nWould you like to set up GitHub integration now?")
    
    # Run setup steps
    try:
        if not check_environment():
            if not confirm_action("Environment check found issues. Continue anyway?"):
                print("Setup cancelled.")
                return
        
        create_folder_structure()
        setup_scripts()
        configure_github_integration(setup_github)
        create_docs_and_reports()
        run_initial_organization()
        complete_setup()
        
        print("\nDocument organization system setup completed successfully!")
        
    except Exception as e:
        print_error(f"Setup failed: {str(e)}")
        return

if __name__ == "__main__":
    main()
