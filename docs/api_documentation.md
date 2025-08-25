# API Documentation

## Java API Endpoints

### Health Check
- **GET** `/api/simulation/health`
- Returns: `{"status": "healthy", "message": "Simulation service is running"}`

### Run Simulation
- **POST** `/api/simulation/run`
- Body: JSON with simulation parameters
- Returns: JSON with simulation results

## Python API

### GeneticOptimizer
Main class for genetic algorithm optimization.

### ParetoAnalyzer
Class for analyzing Pareto frontiers and generating visualizations.

### JavaInterface
Interface for communicating with the Java AnyLogic application.
