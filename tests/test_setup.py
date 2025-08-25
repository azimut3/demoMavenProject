#!/usr/bin/env python3
"""
Test script to verify Python setup and dependencies
"""

import sys
import importlib
import logging

def test_imports():
    """Test if all required packages can be imported"""
    required_packages = [
        'numpy',
        'pandas', 
        'matplotlib',
        'seaborn',
        'sklearn',
        'deap',
        'pymoo',
        'plotly',
        'requests',
        'tqdm',
        'scipy'
    ]
    
    print("Testing package imports...")
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✓ {package}")
        except ImportError as e:
            print(f"✗ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\nFailed to import: {failed_imports}")
        print("Please install missing packages: pip install -r requirements.txt")
        return False
    else:
        print("\nAll packages imported successfully!")
        return True

def test_local_modules():
    """Test if local modules can be imported"""
    local_modules = [
        'java_interface',
        'genetic_optimizer', 
        'pareto_analyzer',
        'main_optimizer'
    ]
    
    print("\nTesting local module imports...")
    failed_imports = []
    
    for module in local_modules:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\nFailed to import local modules: {failed_imports}")
        return False
    else:
        print("\nAll local modules imported successfully!")
        return True

def test_pareto_analyzer():
    """Test Pareto analyzer functionality"""
    print("\nTesting Pareto analyzer...")
    
    try:
        from pareto_analyzer import ParetoAnalyzer
        
        analyzer = ParetoAnalyzer()
        print("✓ ParetoAnalyzer created successfully")
        
        # Test with mock data
        mock_results = {
            "pareto_front": [
                {
                    "parameters": {
                        "varOfWork": 3,
                        "capacityOfMainConveyor": 800,
                        "quantityOfVagonsToSilageAtOnce": 8,
                        "quantityOfVehicleDischargeStations": 2,
                        "numberOfVehicleSilages": 2,
                        "capacityOfVehicleSilages": 800,
                        "quantityOfSilages": 17,
                        "yearsModelWorking": 1
                    },
                    "fitness": [150, 50000, 120, 75000, 60]
                }
            ]
        }
        
        df = analyzer.extract_pareto_data(mock_results)
        print(f"✓ Data extraction successful, {len(df)} rows")
        
        return True
        
    except Exception as e:
        print(f"✗ Pareto analyzer test failed: {e}")
        return False

def test_genetic_optimizer():
    """Test genetic optimizer setup"""
    print("\nTesting genetic optimizer...")
    
    try:
        from genetic_optimizer import GeneticOptimizer
        from java_interface import JavaModelInterface
        
        # Create mock interface
        java_interface = JavaModelInterface()
        
        optimizer = GeneticOptimizer(
            java_interface=java_interface,
            population_size=10,
            generations=5
        )
        
        print("✓ GeneticOptimizer created successfully")
        print(f"✓ Parameter bounds: {len(optimizer.parameter_bounds)} parameters")
        print(f"✓ Objectives: {len(optimizer.objectives)} objectives")
        
        return True
        
    except Exception as e:
        print(f"✗ Genetic optimizer test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("AnyLogic Optimization Setup Test")
    print("=" * 50)
    
    tests = [
        ("Package Imports", test_imports),
        ("Local Modules", test_local_modules),
        ("Pareto Analyzer", test_pareto_analyzer),
        ("Genetic Optimizer", test_genetic_optimizer)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Start your Java application: mvn spring-boot:run")
        print("2. Run the optimizer: python main_optimizer.py --java-app-path .")
        print("3. Or run demo: python main_optimizer.py")
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Check Python version (3.7+ required)")
        print("3. Verify all files are in the same directory")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
