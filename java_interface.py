import requests
import json
import time
import subprocess
import os
from typing import Dict, List, Optional, Tuple
import logging

class JavaModelInterface:
    """
    Interface to communicate with the Java AnyLogic model via Spring Boot REST API
    """
    
    def __init__(self, base_url: str = "http://localhost:8080", 
                 java_app_path: str = None,
                 timeout: int = 300):
        self.base_url = base_url
        self.java_app_path = java_app_path
        self.timeout = timeout
        self.java_process = None
        self.logger = logging.getLogger(__name__)
        
    def start_java_application(self) -> bool:
        """Start the Java Spring Boot application"""
        if not self.java_app_path:
            self.logger.warning("Java app path not specified, assuming it's already running")
            return True
            
        try:
            # Try different ways to find mvn
            mvn_commands = ["mvn", "mvn.cmd", "mvn.bat"]
            mvn_path = None
            
            for cmd in mvn_commands:
                try:
                    subprocess.run([cmd, "--version"], capture_output=True, check=True)
                    mvn_path = cmd
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            if not mvn_path:
                self.logger.error("Maven (mvn) not found in PATH. Please ensure Maven is installed and in PATH.")
                self.logger.info("You can start the Java application manually with: mvn spring-boot:run")
                return False
            
            # Start the Java application
            self.logger.info(f"Starting Java application with: {mvn_path} spring-boot:run")
            self.java_process = subprocess.Popen(
                [mvn_path, "spring-boot:run"],
                cwd=self.java_app_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for the application to start with retries
            self.logger.info("Waiting for Java application to start...")
            max_attempts = 10
            for attempt in range(max_attempts):
                self.logger.info(f"Health check attempt {attempt + 1}/{max_attempts}")
                if self.check_health():
                    self.logger.info("Java application started successfully!")
                    return True
                time.sleep(10)  # Wait 10 seconds between attempts
            
            self.logger.error("Java application failed to start properly after all attempts")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to start Java application: {e}")
            return False
    
    def stop_java_application(self):
        """Stop the Java Spring Boot application"""
        if self.java_process:
            self.java_process.terminate()
            self.java_process.wait()
    
    def check_health(self) -> bool:
        """Check if the Java application is running and healthy"""
        try:
            response = requests.get(f"{self.base_url}/api/simulation/health", timeout=10)
            if response.status_code == 200:
                self.logger.debug(f"Health check successful: {response.text}")
                return True
            else:
                self.logger.debug(f"Health check failed with status {response.status_code}: {response.text}")
                return False
        except requests.exceptions.ConnectionError:
            self.logger.debug("Health check failed: Connection refused (app not ready yet)")
            return False
        except Exception as e:
            self.logger.debug(f"Health check failed with error: {e}")
            return False
    
    def run_simulation(self, parameters: Dict) -> Optional[Dict]:
        """
        Run a single simulation with given parameters
        
        Args:
            parameters: Dictionary with simulation parameters
            
        Returns:
            Dictionary with simulation results (KPIs) or None if failed
        """
        try:
            # Prepare the iteration data
            iteration_data = {
                "varOfWork": parameters.get("varOfWork", 3),
                "capacityOfMainConveyor": parameters.get("capacityOfMainConveyor", 800),
                "quantityOfVagonsToSilageAtOnce": parameters.get("quantityOfVagonsToSilageAtOnce", 8),
                "quantityOfVehicleDischargeStations": parameters.get("quantityOfVehicleDischargeStations", 2),
                "numberOfVehicleSilages": parameters.get("numberOfVehicleSilages", 2),
                "capacityOfVehicleSilages": parameters.get("capacityOfVehicleSilages", 800),
                "quantityOfSilages": parameters.get("quantityOfSilages", 17),
                "yearsModelWorking": parameters.get("yearsModelWorking", 1)
            }
            
            # Send request to Java application
            response = requests.post(
                f"{self.base_url}/api/simulation/run",
                json=iteration_data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Simulation failed with status {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            self.logger.error("Simulation timed out")
            return None
        except Exception as e:
            self.logger.error(f"Error running simulation: {e}")
            return None
    
    def get_simulation_results(self, iteration_id: str) -> Optional[Dict]:
        """Get results for a specific simulation iteration"""
        try:
            response = requests.get(
                f"{self.base_url}/api/simulation/results/{iteration_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting results: {e}")
            return None
    
    def get_all_results(self) -> List[Dict]:
        """Get all simulation results"""
        try:
            response = requests.get(
                f"{self.base_url}/api/simulation/all-results",
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting all results: {e}")
            return []
