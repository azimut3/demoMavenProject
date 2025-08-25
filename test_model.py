#!/usr/bin/env python3
"""
Simple test script to verify AnyLogic model functionality
"""

import requests
import json
import time

def test_model():
    """Test the AnyLogic model with known good parameters"""
    
    # Known good parameters (based on the original model)
    test_params = {
        "varOfWork": 3,
        "capacityOfMainConveyor": 800,
        "quantityOfVagonsToSilageAtOnce": 8,
        "quantityOfVehicleDischargeStations": 2,
        "numberOfVehicleSilages": 2,
        "capacityOfVehicleSilages": 800,
        "quantityOfSilages": 17,
        "yearsModelWorking": 1
    }
    
    print("Testing AnyLogic model with known good parameters...")
    print(f"Parameters: {json.dumps(test_params, indent=2)}")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8080/api/simulation/health")
        if response.status_code != 200:
            print(f"❌ Health check failed: {response.status_code}")
            return False
        
        print("✅ Health check passed")
        
        # Test simulation
        print("Running simulation...")
        response = requests.post(
            "http://localhost:8080/api/simulation/run",
            json=test_params,
            timeout=300
        )
        
        if response.status_code == 200:
            results = response.json()
            print("✅ Simulation completed successfully!")
            print("Results:")
            print(f"  Vessels Handled: {results.get('vesselsHandledQtt', 'N/A')}")
            print(f"  Prime Cost: {results.get('primeCost', 'N/A')}")
            print(f"  Handling Time: {results.get('handlingTime', 'N/A')}")
            print(f"  Profit: {results.get('profit', 'N/A')}")
            print(f"  Time at Terminal: {results.get('timeAtTerminal', 'N/A')}")
            
            # Check if results are meaningful
            vessels = results.get('vesselsHandledQtt', 0)
            if vessels > 0:
                print("🎉 Model is working correctly!")
                return True
            else:
                print("⚠️  Model ran but returned zero vessels handled")
                return False
        else:
            print(f"❌ Simulation failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_model()
    if success:
        print("\n✅ Model test passed! Ready for optimization.")
    else:
        print("\n❌ Model test failed. Check the AnyLogic model configuration.")
