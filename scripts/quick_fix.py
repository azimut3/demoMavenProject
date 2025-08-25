#!/usr/bin/env python3
"""
Quick fix for distutils ModuleNotFoundError
"""

import sys
import subprocess

def quick_fix():
    """Quick fix for distutils issue"""
    print("🔧 Quick fix for distutils ModuleNotFoundError")
    print("=" * 50)
    
    try:
        # Step 1: Update pip
        print("1. Updating pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        print("✓ pip updated")
        
        # Step 2: Install setuptools
        print("2. Installing setuptools...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "setuptools", "wheel"])
        print("✓ setuptools installed")
        
        # Step 3: Test if distutils is available
        print("3. Testing distutils...")
        try:
            import distutils
            print("✓ distutils is now available")
        except ImportError:
            print("⚠️  distutils still not available, trying alternative...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools==65.0.0"])
            print("✓ Alternative setuptools version installed")
        
        print("\n🎉 Quick fix completed!")
        print("You can now try running your original command again.")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during quick fix: {e}")
        print("\nManual steps to try:")
        print("1. pip install --upgrade pip")
        print("2. pip install --upgrade setuptools wheel")
        print("3. pip install -r requirements.txt")

if __name__ == "__main__":
    quick_fix()
