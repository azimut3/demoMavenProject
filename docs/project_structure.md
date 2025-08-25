# Final Project Structure

```
demoMavenProject/
├── README.md                    # Project overview
├── requirements.txt             # Python dependencies
├── pom.xml                      # Maven configuration
├── .gitignore                   # Git ignore rules
│
├── src/                         # Java source code
│   └── main/java/com/mycompany/mavenproject3/
│       ├── DemoAnylogicHibridApplication.java
│       ├── SimulationController.java
│       ├── Iteration.java
│       └── IterationCallable.java
│
├── python/                      # Python application
│   ├── __init__.py
│   ├── main_optimizer.py        # Main entry point
│   ├── genetic_optimizer.py     # Genetic algorithm logic
│   ├── pareto_analyzer.py       # Pareto analysis and visualization
│   ├── java_interface.py        # Java communication interface
│   └── utils/                   # Utility modules
│       ├── __init__.py
│       ├── config.py            # Configuration settings
│       └── helpers.py           # Helper functions
│
├── tests/                       # Test files
│   ├── __init__.py
│   ├── test_model.py
│   ├── test_java_startup.py
│   └── test_setup.py
│
├── scripts/                     # Setup and utility scripts
│   ├── install_anylogic_jars.py
│   ├── setup_python313.py
│   ├── setup_fix.py
│   ├── quick_fix.py
│   └── simple_java_fix.ps1
│
├── logs/                        # Log files
│   ├── optimization_*.log
│   ├── executedIterations.txt
│   └── stats.txt
│
├── results/                     # Optimization results
│   ├── optimization_results.json
│   ├── pareto_analysis/         # Visualizations and analysis
│   │   ├── *.png
│   │   ├── *.html
│   │   ├── pareto_solutions.csv
│   │   └── analysis_summary.json
│   └── archived/                # Old results
│
├── config/                      # Configuration files
│   └── optimization_config.json
│
├── docs/                        # Documentation
│   ├── api_documentation.md
│   ├── optimization_guide.md
│   └── troubleshooting.md
│
├── additional libs/             # AnyLogic dependencies
│   ├── al3d.jar
│   ├── engine.jar
│   └── ...
│
├── target/                      # Maven build output
└── .venv/                       # Python virtual environment
```

## Key Benefits:

### 🎯 **Clean Organization**
- **Business Logic**: All Python optimization code in `python/`
- **Infrastructure**: Java API in `src/`
- **Testing**: Dedicated `tests/` directory
- **Configuration**: Centralized in `config/`
- **Documentation**: Organized in `docs/`

### 📊 **Professional Structure**
- **Industry best practices** for project organization
- **Easy to navigate** and maintain
- **Scalable** for future additions
- **Clear separation** of concerns

### 🔧 **Maintenance Benefits**
- **Organized logs** for debugging
- **Clean results** management
- **Focused testing** environment
- **Better version control** with proper `.gitignore`

## Usage:

### Running the Optimization:
```bash
# Start Java application
mvn spring-boot:run

# Run Python optimizer
python python/main_optimizer.py --population-size 50 --generations 100
```

### Viewing Results:
```bash
# Open plots in browser
start results/pareto_analysis/pareto_2d_primeCost_vs_profit.html
```

### Configuration:
Edit `config/optimization_config.json` to modify parameters and objectives.
