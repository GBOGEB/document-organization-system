from pathlib import Path

def check_organization_status():
    """Simple organization status checker."""
    base_path = Path('.')
    
    print("="*60)
    print("DOCUMENT ORGANIZATION SYSTEM - STATUS CHECK")
    print("="*60)
    
    # Count organized vs unorganized folders
    organized_folders = ['Development', 'Documents', 'Resources', 'Automation', 'Archive']
    organized_count = 0
    unorganized_folders = []
    total_items = 0
    
    for item in base_path.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            try:
                item_count = len(list(item.rglob('*')))
                total_items += item_count
                
                if item.name in organized_folders:
                    organized_count += 1
                    print(f"[OK] {item.name}: {item_count:,} items")
                else:
                    unorganized_folders.append((item.name, item_count))
            except Exception as e:
                print(f"[ERROR] Could not scan {item.name}: {e}")
    
    print(f"\nORGANIZATION STATUS: {organized_count}/5 folders organized")
    
    if unorganized_folders:
        print(f"\nUNORGANIZED FOLDERS ({len(unorganized_folders)}):")
        for name, count in sorted(unorganized_folders, key=lambda x: x[1], reverse=True):
            print(f"  {name}: {count:,} items")
    else:
        print("\n[SUCCESS] ALL FOLDERS ORGANIZED!")
    
    total_unorganized = sum(count for _, count in unorganized_folders)
    print(f"\nTOTAL ORGANIZED ITEMS: {total_items - total_unorganized:,}")
    print(f"TOTAL UNORGANIZED ITEMS: {total_unorganized:,}")
    print(f"GRAND TOTAL: {total_items:,}")
    
    if organized_count == 5 and not unorganized_folders:
        print("\n[COMPLETE] 100% ORGANIZATION ACHIEVED!")
        completion_percentage = 100.0
    else:
        completion_percentage = (total_items - total_unorganized) / total_items * 100
        print(f"\nCOMPLETION: {completion_percentage:.1f}%")
    
    # Recommendations
    print("\nRECOMMENDATIONS:")
    if organized_count < 5:
        print("  1. Run: python run_organization_safe.py")
        print("  2. Choose option 3 to create folder structure")
    elif unorganized_folders:
        print("  1. Run: python organize_remaining_folders.py")
    else:
        print("  1. System fully organized - no action needed!")
        print("  2. Use: python run_organization_safe.py for maintenance")

if __name__ == "__main__":
    check_organization_status()