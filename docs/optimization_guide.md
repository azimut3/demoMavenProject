# Optimization Guide

## Running the Optimization

1. Start the Java application:
   ```bash
   mvn spring-boot:run
   ```

2. Run the Python optimizer:
   ```bash
   python python/main_optimizer.py --population-size 50 --generations 100
   ```

## Configuration

Edit `config/optimization_config.json` to modify:
- Genetic algorithm parameters
- Parameter bounds
- Objective functions

## Results

Results are saved in `results/` directory:
- `optimization_results.json` - Raw optimization data
- `pareto_analysis/` - Visualizations and analysis
