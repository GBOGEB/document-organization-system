# Document Organization System

A comprehensive Python-based system for organizing documents into a structured folder hierarchy with automated scripts for maintenance and monitoring.

## Features

- **Automated folder structure creation** - Creates organized folders for Development, Documents, Resources, Automation, and Archive
- **Cross-platform compatibility** - Works on Windows, macOS, and Linux
- **Status monitoring** - Real-time organization status checking and reporting
- **Safe operations** - Scripts designed to safely handle files without data loss
- **GitHub integration** - Optional version control setup for organization scripts

## Quick Start

1. **Check current organization status:**
   ```bash
   python status_check.py
   ```

2. **Set up folder structure:**
   ```bash
   python organize_safe.py --setup
   ```

3. **Monitor system health:**
   ```bash
   python organize_safe.py --health
   ```

## Scripts Overview

- `setup_organization.py` - Complete system setup and configuration
- `status_check.py` - Check organization status and completion percentage
- `organize_safe.py` - Safe organization operations and folder structure creation
- `handle_logs_folder.py` - Safely handle active log files
- `git_integration.py` - GitHub repository setup and integration
- `PRE_RUN_CHECK.py` - Pre-execution environment and dependency checks

## Recent Changes

- ✅ Fixed hardcoded Windows paths to use relative paths for cross-platform compatibility
- ✅ All scripts now work from any directory location
- ✅ Improved error handling and logging
- ✅ Enhanced documentation and workflow diagrams

## Requirements

- Python 3.6+
- Standard library modules (pathlib, shutil, subprocess, etc.)
- Optional: Git (for GitHub integration features)

## Contributing

Please see the workflow documentation in `WORKFLOW_DIAGRAM.md` for detailed process information.
