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
    BLUE = "\033[94m" if COLOR_SUPPORT else ""
    GREEN = "\033[92m" if COLOR_SUPPORT else ""
    YELLOW = "\033[93m" if COLOR_SUPPORT else ""
    RED = "\033[91m" if COLOR_SUPPORT else ""
    BOLD = "\033[1m" if COLOR_SUPPORT else ""
    END = "\033[0m" if COLOR_SUPPORT else ""


def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'=' * 70}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text.center(70)}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'=' * 70}{Colors.END}")


def print_step(step_num, total_steps, description):
    """Print a formatted step indicator."""
    print(
        f"\n{Colors.GREEN}{Colors.BOLD}[STEP {step_num}/{total_steps}] {description}{Colors.END}"
    )


def print_success(text):
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_warning(text):
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def print_error(text):
    """Print an error message."""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print_error("Python 3.7 or higher is required")
        return False
    print_success(f"Python {sys.version.split()[0]} detected")
    return True


def check_dependencies():
    """Check and install required dependencies."""
    required_packages = ["pathlib"]  # Basic packages that should be available
    optional_packages = ["colorama"]  # Optional for better output

    print_step(1, 5, "Checking Dependencies")

    missing_packages = []
    for package in required_packages:
        if not is_module_available(package):
            missing_packages.append(package)

    if missing_packages:
        print_error(f"Missing required packages: {', '.join(missing_packages)}")
        return False

    print_success("All required dependencies available")

    # Check optional packages
    for package in optional_packages:
        if is_module_available(package):
            print_success(f"Optional package '{package}' available")
        else:
            print_warning(
                f"Optional package '{package}' not available (enhanced features disabled)"
            )

    return True


def create_directory_structure():
    """Create the basic directory structure for organization."""
    print_step(2, 5, "Creating Directory Structure")

    # Get the user's documents directory
    if os.name == "nt":  # Windows
        base_path = Path.home() / "Documents"
    else:  # Linux/macOS
        base_path = Path.home() / "Documents"

    # Create main organization directories
    main_dirs = ["Archive", "Automation", "Development", "Documents", "Resources"]

    for dir_name in main_dirs:
        dir_path = base_path / dir_name
        try:
            dir_path.mkdir(exist_ok=True)
            print_success(f"Directory created/verified: {dir_name}")
        except Exception as e:
            print_error(f"Failed to create directory {dir_name}: {e}")
            return False

    # Create logs directory
    logs_dir = base_path / "logs"
    try:
        logs_dir.mkdir(exist_ok=True)
        print_success("Logs directory created/verified")
    except Exception as e:
        print_warning(f"Could not create logs directory: {e}")

    return True


def create_config_file():
    """Create a configuration file for the organization system."""
    print_step(3, 5, "Creating Configuration")

    config = {
        "version": "2.0.0",
        "created": datetime.datetime.now().isoformat(),
        "base_path": str(Path.home() / "Documents"),
        "organization_structure": {
            "Archive": "Long-term storage and backups",
            "Automation": "Scripts, tools, and utilities",
            "Development": "Code projects and development files",
            "Documents": "Active documents and projects",
            "Resources": "References, templates, and assets",
        },
        "settings": {
            "backup_enabled": True,
            "logging_enabled": True,
            "safe_mode": False,
            "unicode_support": True,
        },
    }

    try:
        config_path = Path("config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print_success("Configuration file created")
        return True
    except Exception as e:
        print_error(f"Failed to create configuration: {e}")
        return False


def verify_system():
    """Verify the organization system is properly set up."""
    print_step(4, 5, "Verifying System Setup")

    # Check if main scripts exist
    required_scripts = ["organize_safe.py", "status_check.py"]

    for script in required_scripts:
        if Path(script).exists():
            print_success(f"Script found: {script}")
        else:
            print_warning(f"Script not found: {script}")

    # Check directory structure
    if os.name == "nt":
        base_path = Path.home() / "Documents"
    else:
        base_path = Path.home() / "Documents"

    main_dirs = ["Archive", "Automation", "Development", "Documents", "Resources"]

    for dir_name in main_dirs:
        dir_path = base_path / dir_name
        if dir_path.exists():
            print_success(f"Directory verified: {dir_name}")
        else:
            print_warning(f"Directory missing: {dir_name}")

    return True


def run_initial_status_check():
    """Run an initial status check to show current state."""
    print_step(5, 5, "Running Initial Status Check")

    try:
        if Path("status_check.py").exists():
            print("Running status check...")
            subprocess.run([sys.executable, "status_check.py"], check=False)
        else:
            print_warning("Status check script not found - skipping initial check")
    except Exception as e:
        print_warning(f"Could not run status check: {e}")


def main():
    """Main setup function."""
    print_header("DOCUMENT ORGANIZATION SYSTEM SETUP")
    print(
        f"{Colors.BLUE}Setting up your professional document organization system...{Colors.END}"
    )

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Create directory structure
    if not create_directory_structure():
        sys.exit(1)

    # Create configuration
    if not create_config_file():
        sys.exit(1)

    # Verify system
    verify_system()

    # Run initial status check
    run_initial_status_check()

    print_header("SETUP COMPLETE")
    print(
        f"{Colors.GREEN}{Colors.BOLD}Your document organization system is ready!{Colors.END}"
    )
    print(f"\n{Colors.BLUE}Next steps:{Colors.END}")
    print(f"1. Run 'python status_check.py' to see current organization status")
    print(f"2. Run 'python organize_safe.py' to start organizing your documents")
    print(f"3. Check the README.md for detailed usage instructions")

    print(f"\n{Colors.YELLOW}For help and documentation:{Colors.END}")
    print(f"- README.md - Complete usage guide")
    print(f"- WORKFLOW_DIAGRAM.md - System workflow")
    print(f"- config.json - System configuration")


if __name__ == "__main__":
    main()
