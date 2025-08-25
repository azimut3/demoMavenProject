# AnyLogic Model Optimization with Genetic Algorithms

This project provides a Python application that uses genetic algorithms to optimize AnyLogic simulation model parameters and build Pareto frontiers for multiple KPIs.

## Overview

The system consists of:
1. **Java Spring Boot Application**: Your existing AnyLogic model with REST API endpoints
2. **Python Genetic Algorithm Optimizer**: Multi-objective optimization using DEAP library
3. **Pareto Frontier Analyzer**: Comprehensive analysis and visualization of optimization results

## Key Features

- **Multi-objective Optimization**: Optimizes 5 KPIs simultaneously:
  - Vessels Handled Quantity (maximize)
  - Prime Cost (minimize)
  - Handling Time (minimize)
  - Profit (maximize)
  - Time at Terminal (minimize)

- **Genetic Algorithm**: Uses NSGA-II algorithm for Pareto-optimal solutions
- **Comprehensive Analysis**: 2D/3D Pareto frontiers, parallel coordinates plots, parameter distributions
- **REST API Integration**: Seamless communication with Java AnyLogic model
- **Configurable Parameters**: Population size, generations, mutation/crossover rates

## Project Structure

```
├── requirements.txt              # Python dependencies
├── java_interface.py            # Java application communication
├── genetic_optimizer.py         # Genetic algorithm implementation
├── pareto_analyzer.py           # Pareto frontier analysis
├── main_optimizer.py            # Main application
├── src/main/java/.../          # Java Spring Boot application
│   ├── SimulationController.java # REST API endpoints
│   ├── DemoAnylogicHibridApplication.java
│   ├── Iteration.java
│   └── IterationCallable.java
└── README.md                    # This file
```

## Installation

### 1. Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Java Application Setup

1. Install Maven if not already installed
2. Install AnyLogic libraries:
   ```bash
   cd "additional libs"
   ./install.sh
   ```
3. Build the Java application:
   ```bash
   mvn clean install
   ```

## Usage

### Quick Start (Demo Mode)

Run the demo to see the Pareto analysis in action:

```bash
python main_optimizer.py
```

This will run with mock data and generate sample Pareto frontier visualizations.

### Full Optimization

1. **Start the Java Application** (if not already running):
   ```bash
   mvn spring-boot:run
   ```

2. **Run the Python Optimizer**:
   ```bash
   python main_optimizer.py --java-app-path . --population-size 30 --generations 50
   ```

### Command Line Options

```bash
python main_optimizer.py [OPTIONS]

Options:
  --java-app-path PATH        Path to Java Spring Boot application directory
  --java-url URL              URL of Java application (default: http://localhost:8080)
  --population-size INT       Genetic algorithm population size (default: 30)
  --generations INT           Number of generations (default: 50)
  --mutation-rate FLOAT       Mutation rate (default: 0.1)
  --crossover-rate FLOAT      Crossover rate (default: 0.7)
  --timeout INT               Simulation timeout in seconds (default: 300)
  --output-dir PATH           Output directory for results (default: optimization_results)
  --analysis-only             Only run Pareto analysis on existing results
  --results-file PATH         Path to existing results file for analysis
  --log-level LEVEL           Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)
```

### Examples

**Basic optimization with default settings:**
```bash
python main_optimizer.py --java-app-path .
```

**Custom optimization parameters:**
```bash
python main_optimizer.py \
  --java-app-path . \
  --population-size 50 \
  --generations 100 \
  --mutation-rate 0.15 \
  --crossover-rate 0.8 \
  --timeout 600
```

**Analysis only (on existing results):**
```bash
python main_optimizer.py --analysis-only --results-file optimization_results.json
```

## Output

The application generates several outputs:

### 1. Optimization Results
- `optimization_results.json`: Complete optimization results
- `optimization_YYYYMMDD_HHMMSS.log`: Detailed log file

### 2. Pareto Analysis
- `pareto_analysis/analysis_summary.json`: Statistical summary
- `pareto_analysis/pareto_solutions.csv`: Pareto optimal solutions
- `pareto_analysis/pareto_2d_*.html`: 2D Pareto frontier plots
- `pareto_analysis/pareto_3d.html`: 3D Pareto frontier plot
- `pareto_analysis/parallel_coordinates.html`: Parallel coordinates plot
- `pareto_analysis/parameter_distributions.html`: Parameter distribution plots

### 3. Visualizations
- Interactive HTML plots (open in browser)
- PNG images for reports
- Comprehensive statistical analysis

## API Endpoints

The Java application provides these REST endpoints:

- `POST /api/simulation/run`: Run simulation with parameters
- `GET /api/simulation/results/{id}`: Get specific simulation results
- `GET /api/simulation/all-results`: Get all simulation results
- `GET /api/simulation/health`: Health check
- `DELETE /api/simulation/clear-cache`: Clear results cache

## Parameter Bounds

The genetic algorithm operates within these parameter bounds:

| Parameter | Min | Max |
|-----------|-----|-----|
| varOfWork | 1 | 5 |
| capacityOfMainConveyor | 600 | 1400 |
| quantityOfVagonsToSilageAtOnce | 6 | 12 |
| quantityOfVehicleDischargeStations | 1 | 6 |
| numberOfVehicleSilages | 1 | 6 |
| capacityOfVehicleSilages | 600 | 1200 |
| quantityOfSilages | 15 | 25 |
| yearsModelWorking | 1 | 3 |

## KPIs Optimized

1. **Vessels Handled Quantity**: Number of vessels processed (maximize)
2. **Prime Cost**: Operational costs (minimize)
3. **Handling Time**: Time spent handling vessels (minimize)
4. **Profit**: Revenue minus costs (maximize)
5. **Time at Terminal**: Time vessels spend at terminal (minimize)

## Troubleshooting

### Common Issues

1. **Java application not starting**:
   - Check Maven installation
   - Verify AnyLogic libraries are installed
   - Check port 8080 is available

2. **Simulation timeouts**:
   - Increase `--timeout` parameter
   - Check AnyLogic model complexity
   - Verify system resources

3. **Python dependencies**:
   - Use virtual environment
   - Update pip: `pip install --upgrade pip`
   - Install dependencies individually if needed

4. **Memory issues**:
   - Reduce population size
   - Reduce number of generations
   - Increase system memory

### Logging

Enable debug logging for detailed information:
```bash
python main_optimizer.py --log-level DEBUG
```

## Performance Tips

1. **For faster optimization**:
   - Reduce population size (20-30)
   - Reduce generations (30-50)
   - Use smaller parameter ranges

2. **For better results**:
   - Increase population size (50-100)
   - Increase generations (100-200)
   - Run multiple times with different seeds

3. **For production use**:
   - Use dedicated server for Java application
   - Implement result caching
   - Use database for result storage

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs for error messages
3. Create an issue with detailed information
