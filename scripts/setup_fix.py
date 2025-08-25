#!/usr/bin/env python3
"""
Setup script to fix distutils issues and install dependencies
"""

import sys
import subprocess
import os

def check_python_version():
    """Check Python version and provide recommendations"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7+ is required")
        return False
    elif version.major == 3 and version.minor >= 12:
        print("⚠️  Python 3.12+ detected - distutils was removed from stdlib")
        print("   Installing setuptools to provide distutils...")
    else:
        print("✓ Python version is compatible")
    
    return True

def install_setuptools():
    """Install setuptools to provide distutils"""
    print("\nInstalling setuptools...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "setuptools", "wheel"])
        print("✓ setuptools installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install setuptools: {e}")
        return False

def install_requirements():
    """Install all requirements"""
    print("\nInstalling requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def test_imports():
    """Test if key modules can be imported"""
    print("\nTesting imports...")
    
    test_modules = [
        'setuptools',
        'numpy',
        'pandas',
        'matplotlib',
        'deap',
        'plotly'
    ]
    
    failed_imports = []
    
    for module in test_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {failed_imports}")
        return False
    else:
        print("\n✓ All modules imported successfully!")
        return True

def main():
    """Main setup function"""
    print("=" * 60)
    print("AnyLogic Optimization Setup Fix")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install setuptools first
    if not install_setuptools():
        print("\nTrying alternative approach...")
        try:
            # Try installing setuptools with --force-reinstall
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "--force-reinstall", "setuptools", "wheel"
            ])
            print("✓ setuptools installed with force-reinstall")
        except subprocess.CalledProcessError:
            print("❌ Failed to install setuptools. Please install manually:")
            print("   pip install --upgrade setuptools wheel")
            return False
    
    # Install requirements
    if not install_requirements():
        print("\nTrying to install packages individually...")
        packages = [
            "numpy==1.24.3",
            "pandas==2.0.3", 
            "matplotlib==3.7.2",
            "seaborn==0.12.2",
            "scikit-learn==1.3.0",
            "deap==1.3.3",
            "plotly==5.15.0",
            "requests==2.31.0",
            "tqdm==4.65.0",
            "scipy==1.11.1"
        ]
        
        for package in packages:
            try:
                print(f"Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✓ {package}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install {package}: {e}")
                return False
    
    # Test imports
    if not test_imports():
        print("\n❌ Some modules still cannot be imported.")
        print("Please try the following:")
        print("1. Update pip: python -m pip install --upgrade pip")
        print("2. Install setuptools: pip install --upgrade setuptools wheel")
        print("3. Install requirements: pip install -r requirements.txt")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Setup completed successfully!")
    print("=" * 60)
    print("\nYou can now run:")
    print("1. Test setup: python test_setup.py")
    print("2. Run demo: python main_optimizer.py")
    print("3. Full optimization: python main_optimizer.py --java-app-path .")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
