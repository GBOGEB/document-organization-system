
# filepath: fix_unicode_console.py
import os
import sys

def fix_windows_console():
    """Fix Windows console to properly display Unicode characters."""
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
    """Print text safely, handling Unicode encoding errors."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))

if __name__ == '__main__':
    if fix_windows_console():
        print("Unicode support configured for Windows console")
    safe_print("Test: ✅ ✓ ❌ ✗ 📁 📊 😊 🚀")
