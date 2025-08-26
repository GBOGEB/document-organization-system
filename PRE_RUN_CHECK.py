"""
Pre-run check system for document organization scripts.
Validates environment, dependencies, and structure before running operations.
"""
import os
import sys
import importlib
import platform
from pathlib import Path

def check_environment():
    """Check Python environment and system settings."""
    results = []
    
    # Python version check
    py_version = platform.python_version()
    py_version_ok = sys.version_info.major >= 3 and sys.version_info.minor >= 6
    results.append({
        'check': 'Python Version',
        'status': 'OK' if py_version_ok else 'WARNING',
        'details': f"Python {py_version} {'(OK)' if py_version_ok else '(Python 3.6+ recommended)'}"
    })
    
    # Unicode support
    try:
        "Unicode Test: 📁📊✅".encode(sys.stdout.encoding).decode(sys.stdout.encoding)
        unicode_ok = True
    except:
        unicode_ok = False
    
    results.append({
        'check': 'Unicode Support',
        'status': 'OK' if unicode_ok else 'WARNING',
        'details': f"{'Unicode supported' if unicode_ok else 'Limited Unicode support'}"
    })
    
    # Check console encoding
    console_encoding = sys.stdout.encoding if hasattr(sys.stdout, 'encoding') else 'Unknown'
    results.append({
        'check': 'Console Encoding',
        'status': 'OK' if console_encoding.lower() in ('utf-8', 'utf8') else 'INFO',
        'details': f"Console encoding: {console_encoding}"
    })
    
    return results

def check_dependencies():
    """Check for required Python modules."""
    required_modules = [
        'pathlib',
        'shutil',
        'datetime',
        'json',
        'logging'
    ]
    
    results = []
    for module in required_modules:
        try:
            importlib.import_module(module)
            results.append({
                'check': f"Module: {module}",
                'status': 'OK',
                'details': 'Installed'
            })
        except ImportError:
            results.append({
                'check': f"Module: {module}",
                'status': 'ERROR',
                'details': 'Missing (required)'
            })
    
    return results

def check_files():
    """Check if required script files exist."""
    base_path = Path('.')
    
    required_files = [
        'organize_safe.py',
        'organize_remaining_folders.py',
        'run_organization_safe.py',
        'status_check.py',
        'quick_summary_v2.py',
        'handle_logs_folder.py',
        'fix_unicode_console.py'
    ]
    
    results = []
    for filename in required_files:
        file_path = base_path / filename
        if file_path.exists():
            results.append({
                'check': f"File: {filename}",
                'status': 'OK',
                'details': 'Found'
            })
        else:
            results.append({
                'check': f"File: {filename}",
                'status': 'ERROR',
                'details': 'Missing (required)'
            })
    
    return results

def check_structure():
    """Check if main folder structure exists."""
    base_path = Path('.')
    
    main_folders = [
        'Development',
        'Documents',
        'Resources',
        'Automation',
        'Archive'
    ]
    
    results = []
    for folder in main_folders:
        folder_path = base_path / folder
        if folder_path.exists() and folder_path.is_dir():
            results.append({
                'check': f"Folder: {folder}",
                'status': 'OK',
                'details': 'Found'
            })
        else:
            results.append({
                'check': f"Folder: {folder}",
                'status': 'WARNING',
                'details': 'Not found (run organize_safe.py --setup)'
            })
    
    return results

def check_permissions():
    """Test write permissions in key locations."""
    base_path = Path('.')
    
    # Test writing to important locations
    test_locations = [
        base_path,
        base_path / 'Automation' / 'Logs' if (base_path / 'Automation' / 'Logs').exists() else None,
    ]
    
    results = []
    for location in test_locations:
        if location is None:
            continue
            
        try:
            test_file = location / '_permission_test.tmp'
            with open(test_file, 'w') as f:
                f.write('test')
            test_file.unlink()
            results.append({
                'check': f"Permission: {location.relative_to(base_path)}",
                'status': 'OK',
                'details': 'Write access confirmed'
            })
        except Exception as e:
            results.append({
                'check': f"Permission: {location.relative_to(base_path) if hasattr(location, 'relative_to') else str(location)}",
                'status': 'ERROR',
                'details': f"No write access: {str(e)}"
            })
    
    return results

def run_checks(verbose=True):
    """Run all pre-execution checks."""
    print("\n" + "="*70)
    print(" "*25 + "PRE-RUN CHECKS")
    print("="*70)
    
    all_results = []
    all_results.extend(check_environment())
    all_results.extend(check_dependencies())
    all_results.extend(check_files())
    all_results.extend(check_structure())
    all_results.extend(check_permissions())
    
    if verbose:
        print("\nCHECK RESULTS:")
        for result in all_results:
            status_display = {
                'OK': '✅',
                'WARNING': '⚠️',
                'ERROR': '❌',
                'INFO': 'ℹ️'
            }.get(result['status'], '?')
            
            print(f"{status_display} {result['check']}: {result['details']}")
    
    # Count issues
    errors = sum(1 for r in all_results if r['status'] == 'ERROR')
    warnings = sum(1 for r in all_results if r['status'] == 'WARNING')
    ok = sum(1 for r in all_results if r['status'] == 'OK')
    
    print("\n" + "-"*70)
    print(f"SUMMARY: {ok} checks passed, {warnings} warnings, {errors} errors")
    
    if errors > 0:
        print("\n❌ CRITICAL ISSUES FOUND")
        print("Some required components are missing. Organization may not work correctly.")
        print("Review the errors above and fix them before proceeding.")
        return False
    elif warnings > 0:
        print("\n⚠️ WARNINGS FOUND")
        print("The organization system can run, but with potential limitations.")
        print("Consider addressing the warnings for optimal performance.")
        return True
    else:
        print("\n✅ ALL CHECKS PASSED")
        print("The organization system is ready to run.")
        return True

if __name__ == "__main__":
    run_checks()
