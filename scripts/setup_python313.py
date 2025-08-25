#!/usr/bin/env python3
"""
Setup script specifically for Python 3.13 compatibility
"""

import sys
import subprocess
import os

def check_python_version():
    """Check Python version and provide recommendations"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor == 13:
        print("⚠️  Python 3.13 detected - using compatible package versions")
        return True
    elif version.major == 3 and version.minor >= 12:
        print("⚠️  Python 3.12+ detected - using compatible package versions")
        return True
    elif version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7+ is required")
        return False
    else:
        print("✓ Python version is compatible")
        return True

def install_core_dependencies():
    """Install core dependencies first"""
    print("\nInstalling core dependencies...")
    
    core_packages = [
        "setuptools>=68.0.0",
        "wheel>=0.41.0",
        "pip>=23.0.0"
    ]
    
    for package in core_packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])
            print(f"✓ {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def install_scientific_packages():
    """Install scientific packages with Python 3.13 compatible versions"""
    print("\nInstalling scientific packages...")
    
    # Python 3.13 compatible versions
    packages = [
        "numpy>=1.26.0",
        "scipy>=1.11.0",
        "pandas>=2.1.0",
        "matplotlib>=3.8.0",
        "seaborn>=0.13.0",
        "scikit-learn>=1.3.0"
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def install_optimization_packages():
    """Install optimization and visualization packages"""
    print("\nInstalling optimization packages...")
    
    packages = [
        "deap>=1.4.0",
        "pymoo>=0.6.0",
        "plotly>=5.17.0",
        "requests>=2.31.0",
        "tqdm>=4.66.0"
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def test_imports():
    """Test if key modules can be imported"""
    print("\nTesting imports...")
    
    test_modules = [
        'setuptools',
        'numpy',
        'pandas',
        'matplotlib',
        'deap',
        'plotly',
        'scipy',
        'sklearn'
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
    """Main setup function for Python 3.13"""
    print("=" * 60)
    print("Python 3.13 Compatible Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install core dependencies
    if not install_core_dependencies():
        print("\n❌ Failed to install core dependencies")
        return False
    
    # Install scientific packages
    if not install_scientific_packages():
        print("\n❌ Failed to install scientific packages")
        return False
    
    # Install optimization packages
    if not install_optimization_packages():
        print("\n❌ Failed to install optimization packages")
        return False
    
    # Test imports
    if not test_imports():
        print("\n❌ Some modules still cannot be imported.")
        print("Please try the following:")
        print("1. Update pip: python -m pip install --upgrade pip")
        print("2. Install setuptools: pip install --upgrade setuptools wheel")
        print("3. Try installing packages individually")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Python 3.13 setup completed successfully!")
    print("=" * 60)
    print("\nYou can now run:")
    print("1. Test setup: python test_setup.py")
    print("2. Run demo: python main_optimizer.py")
    print("3. Full optimization: python main_optimizer.py --java-app-path .")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
