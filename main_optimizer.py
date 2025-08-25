#!/usr/bin/env python3
"""
Main application for AnyLogic model optimization using Genetic Algorithms
"""

import logging
import argparse
import os
import sys
from datetime import datetime
from typing import Dict, Any

from java_interface import JavaModelInterface
from genetic_optimizer import GeneticOptimizer
from pareto_analyzer import ParetoAnalyzer

def setup_logging(log_level: str = "INFO") -> None:
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'optimization_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def parse_arguments() -> Dict[str, Any]:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="AnyLogic Model Optimization using Genetic Algorithms"
    )
    
    parser.add_argument(
        "--java-app-path",
        type=str,
        help="Path to Java Spring Boot application directory"
    )
    
    parser.add_argument(
        "--java-url",
        type=str,
        default="http://localhost:8080",
        help="URL of Java application (default: http://localhost:8080)"
    )
    
    parser.add_argument(
        "--population-size",
        type=int,
        default=30,
        help="Genetic algorithm population size (default: 30)"
    )
    
    parser.add_argument(
        "--generations",
        type=int,
        default=50,
        help="Number of generations for genetic algorithm (default: 50)"
    )
    
    parser.add_argument(
        "--mutation-rate",
        type=float,
        default=0.1,
        help="Mutation rate (default: 0.1)"
    )
    
    parser.add_argument(
        "--crossover-rate",
        type=float,
        default=0.7,
        help="Crossover rate (default: 0.7)"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Simulation timeout in seconds (default: 300)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="optimization_results",
        help="Output directory for results (default: optimization_results)"
    )
    
    parser.add_argument(
        "--analysis-only",
        action="store_true",
        help="Only run Pareto analysis on existing results"
    )
    
    parser.add_argument(
        "--results-file",
        type=str,
        help="Path to existing results file for analysis"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--no-auto-start",
        action="store_true",
        help="Don't automatically start Java application (assume it's already running)"
    )
    
    return vars(parser.parse_args())

def main():
    """Main application function"""
    args = parse_arguments()
    
    # Setup logging
    setup_logging(args["log_level"])
    logger = logging.getLogger(__name__)
    
    logger.info("Starting AnyLogic Model Optimization")
    logger.info(f"Arguments: {args}")
    
    # Create output directory
    os.makedirs(args["output_dir"], exist_ok=True)
    
    if args["analysis_only"]:
        # Only run Pareto analysis
        if not args["results_file"]:
            logger.error("Results file must be specified for analysis-only mode")
            return
        
        logger.info("Running Pareto analysis only")
        analyzer = ParetoAnalyzer()
        report = analyzer.generate_comprehensive_report(
            args["results_file"],
            f"{args['output_dir']}/pareto_analysis"
        )
        
        if report:
            logger.info("Pareto analysis completed successfully")
            logger.info(f"Summary: {report['summary']}")
        else:
            logger.error("Pareto analysis failed")
        
        return
    
    # Initialize Java interface
    java_interface = JavaModelInterface(
        base_url=args["java_url"],
        java_app_path=args["java_app_path"],
        timeout=args["timeout"]
    )
    
    # Start Java application if path is provided and auto-start is enabled
    if args["java_app_path"] and not args["no_auto_start"]:
        logger.info("Starting Java application...")
        if not java_interface.start_java_application():
            logger.error("Failed to start Java application")
            return
        logger.info("Java application started successfully")
    elif args["no_auto_start"]:
        logger.info("Skipping Java application startup (--no-auto-start flag used)")
        logger.info("Make sure the Java application is running at: " + args["java_url"])
        
        # Check if Java application is actually running
        if not java_interface.check_health():
            logger.error("Java application is not running or not accessible!")
            logger.error("Please start the Java application manually with: mvn spring-boot:run")
            return
        else:
            logger.info("Java application is running and accessible")
    
    try:
        # Initialize genetic optimizer
        optimizer = GeneticOptimizer(
            java_interface=java_interface,
            population_size=args["population_size"],
            generations=args["generations"],
            mutation_rate=args["mutation_rate"],
            crossover_rate=args["crossover_rate"]
        )
        
        logger.info("Starting genetic algorithm optimization...")
        logger.info(f"Population size: {args['population_size']}")
        logger.info(f"Generations: {args['generations']}")
        logger.info(f"Mutation rate: {args['mutation_rate']}")
        logger.info(f"Crossover rate: {args['crossover_rate']}")
        
        # Run optimization
        population, pareto_front = optimizer.optimize()
        
        logger.info(f"Optimization completed!")
        logger.info(f"Final population size: {len(population)}")
        logger.info(f"Pareto front size: {len(pareto_front)}")
        
        # Save results
        results_file = f"{args['output_dir']}/optimization_results.json"
        optimizer.save_results(population, pareto_front, results_file)
        
        # Get best solutions
        best_solutions = optimizer.get_best_solutions(pareto_front)
        logger.info("Best solutions:")
        for solution in best_solutions:
            logger.info(f"  {solution['criterion']}: {solution['parameters']}")
            logger.info(f"    Fitness: {solution['fitness']}")
        
        # Run Pareto analysis
        logger.info("Running Pareto analysis...")
        analyzer = ParetoAnalyzer()
        report = analyzer.generate_comprehensive_report(
            results_file,
            f"{args['output_dir']}/pareto_analysis"
        )
        
        if report:
            logger.info("Pareto analysis completed successfully")
            logger.info(f"Total solutions: {report['summary']['total_solutions']}")
            logger.info(f"Pareto solutions: {report['summary']['pareto_solutions']}")
            logger.info(f"Pareto percentage: {report['summary']['pareto_percentage']:.2f}%")
        
        logger.info(f"All results saved to: {args['output_dir']}")
        
    except KeyboardInterrupt:
        logger.info("Optimization interrupted by user")
    except Exception as e:
        logger.error(f"Optimization failed: {e}", exc_info=True)
    finally:
        # Stop Java application if we started it
        if args["java_app_path"]:
            logger.info("Stopping Java application...")
            java_interface.stop_java_application()

def run_demo():
    """Run a demo with mock data for testing"""
    logger = logging.getLogger(__name__)
    logger.info("Running demo with mock data...")
    
    # Create mock results for demonstration
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
            },
            {
                "parameters": {
                    "varOfWork": 3,
                    "capacityOfMainConveyor": 1000,
                    "quantityOfVagonsToSilageAtOnce": 10,
                    "quantityOfVehicleDischargeStations": 3,
                    "numberOfVehicleSilages": 3,
                    "capacityOfVehicleSilages": 900,
                    "quantityOfSilages": 19,
                    "yearsModelWorking": 1
                },
                "fitness": [180, 65000, 100, 85000, 50]
            },
            {
                "parameters": {
                    "varOfWork": 3,
                    "capacityOfMainConveyor": 1200,
                    "quantityOfVagonsToSilageAtOnce": 12,
                    "quantityOfVehicleDischargeStations": 4,
                    "numberOfVehicleSilages": 4,
                    "capacityOfVehicleSilages": 1000,
                    "quantityOfSilages": 21,
                    "yearsModelWorking": 1
                },
                "fitness": [200, 80000, 90, 95000, 45]
            }
        ],
        "parameter_bounds": {},
        "objectives": {}
    }
    
    # Save mock results
    import json
    with open("demo_results.json", "w") as f:
        json.dump(mock_results, f, indent=2)
    
    # Run Pareto analysis
    analyzer = ParetoAnalyzer()
    report = analyzer.generate_comprehensive_report(
        "demo_results.json",
        "demo_analysis"
    )
    
    if report:
        logger.info("Demo Pareto analysis completed successfully")
        logger.info(f"Summary: {report['summary']}")
    else:
        logger.error("Demo Pareto analysis failed")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments provided, run demo
        setup_logging("INFO")
        run_demo()
    else:
        main()
