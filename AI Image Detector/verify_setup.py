#!/usr/bin/env python3
"""
Aura Vision - Setup Verification Script
Checks if all dependencies are installed and configured correctly
"""

import sys
import subprocess
from importlib.util import find_spec

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✓ Python Version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python Version: {version.major}.{version.minor} (Required: 3.8+)")
        return False

def check_module(module_name, import_name=None):
    """Check if a module is installed"""
    if import_name is None:
        import_name = module_name
    
    try:
        spec = find_spec(import_name)
        if spec is not None:
            try:
                # Try to import to verify it actually works
                __import__(import_name)
                print(f"✓ {module_name}: Installed")
                return True
            except Exception as e:
                print(f"✗ {module_name}: Import failed - {str(e)}")
                return False
        else:
            print(f"✗ {module_name}: Not installed")
            return False
    except Exception as e:
        print(f"✗ {module_name}: Not found - {str(e)}")
        return False

def check_dependencies():
    """Check all required dependencies"""
    print("\n" + "="*50)
    print("DEPENDENCY CHECK")
    print("="*50)
    
    dependencies = [
        ("CustomTkinter", "customtkinter"),
        ("Pillow (PIL)", "PIL"),
        ("NumPy", "numpy"),
        ("tkinter", "tkinter"),
    ]
    
    all_ok = True
    for name, import_name in dependencies:
        if not check_module(name, import_name):
            all_ok = False
    
    return all_ok

def check_file_system():
    """Check if the working directory is set up correctly"""
    print("\n" + "="*50)
    print("FILE SYSTEM CHECK")
    print("="*50)
    
    import os
    
    required_files = ["python.py"]
    all_ok = True
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}: Found")
        else:
            print(f"✗ {file}: Not found")
            all_ok = False
    
    # Check if database file exists (optional)
    if os.path.exists("image_database.json"):
        print(f"✓ image_database.json: Found (database exists)")
    else:
        print(f"ℹ image_database.json: Not found (will be created on first analysis)")
    
    return all_ok

def test_imports():
    """Test if we can actually import and use the modules"""
    print("\n" + "="*50)
    print("IMPORT TEST")
    print("="*50)
    
    try:
        import customtkinter
        print("✓ customtkinter imported successfully")
    except Exception as e:
        print(f"✗ customtkinter import failed: {e}")
        return False
    
    try:
        from PIL import Image, ImageDraw, ImageTk
        print("✓ PIL modules imported successfully")
    except Exception as e:
        print(f"✗ PIL import failed: {e}")
        return False
    
    try:
        import numpy
        print("✓ NumPy imported successfully")
    except Exception as e:
        print(f"✗ NumPy import failed: {e}")
        return False
    
    try:
        import tkinter
        print("✓ tkinter imported successfully")
    except Exception as e:
        print(f"✗ tkinter import failed: {e}")
        return False
    
    return True

def suggest_fixes(failed_checks):
    """Suggest fixes for failed checks"""
    if not failed_checks:
        return
    
    print("\n" + "="*50)
    print("SUGGESTED FIXES")
    print("="*50)
    
    if "dependencies" in failed_checks:
        print("\nTo install missing dependencies, run:")
        print("  pip install customtkinter pillow numpy")
        print("\nOr install individually:")
        print("  pip install customtkinter")
        print("  pip install pillow")
        print("  pip install numpy")
    
    print("\n")

def main():
    """Run all verification checks"""
    print("\n" + "🔍 AURA VISION - SETUP VERIFICATION".center(50))
    print("="*50)
    
    failed_checks = []
    
    # Python version check
    if not check_python_version():
        failed_checks.append("python_version")
    
    # Dependencies check
    if not check_dependencies():
        failed_checks.append("dependencies")
    
    # File system check
    if not check_file_system():
        failed_checks.append("file_system")
    
    # Import test
    if not test_imports():
        failed_checks.append("imports")
    
    # Summary
    print("\n" + "="*50)
    print("VERIFICATION SUMMARY")
    print("="*50)
    
    if not failed_checks:
        print("\n✅ ALL CHECKS PASSED!")
        print("\n🚀 You're ready to run: python python.py")
        print("\nNext steps:")
        print("  1. Run: python python.py")
        print("  2. Click 'Browse Files' to select an image")
        print("  3. Click 'Start Analysis' to begin scanning")
        print("  4. View results in the Analysis Progress panel")
        return 0
    else:
        print(f"\n❌ VERIFICATION FAILED ({len(failed_checks)} issues)")
        print("\nFailed checks:")
        for check in failed_checks:
            print(f"  - {check}")
        
        suggest_fixes(failed_checks)
        print("\nAfter fixing issues, run this script again to verify.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
