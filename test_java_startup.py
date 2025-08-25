#!/usr/bin/env python3
"""
Simple test script to check Java application startup
"""

import subprocess
import time
import requests
import sys

def test_java_startup():
    """Test if Java application can start properly"""
    print("Testing Java application startup...")
    
    # Try to start the Java application
    try:
        print("Starting Java application with: mvn spring-boot:run")
        process = subprocess.Popen(
            ["mvn", "spring-boot:run"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit and check if it's still running
        time.sleep(5)
        if process.poll() is not None:
            # Process has terminated
            stdout, stderr = process.communicate()
            print("❌ Java application failed to start!")
            print("STDOUT:", stdout)
            print("STDERR:", stderr)
            return False
        
        print("✅ Java application process started successfully")
        
        # Wait for it to be ready
        print("Waiting for application to be ready...")
        max_wait = 60  # Wait up to 60 seconds
        for i in range(max_wait // 5):
            try:
                response = requests.get("http://localhost:8080/api/simulation/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Java application is ready and responding!")
                    print(f"Health response: {response.text}")
                    process.terminate()
                    return True
            except requests.exceptions.ConnectionError:
                print(f"⏳ Still waiting... ({i+1}/{max_wait//5})")
            except Exception as e:
                print(f"⚠️  Error checking health: {e}")
            
            time.sleep(5)
        
        print("❌ Java application didn't become ready in time")
        process.terminate()
        return False
        
    except FileNotFoundError:
        print("❌ Maven (mvn) not found! Please ensure Maven is installed and in PATH")
        return False
    except Exception as e:
        print(f"❌ Error starting Java application: {e}")
        return False

if __name__ == "__main__":
    success = test_java_startup()
    sys.exit(0 if success else 1)
