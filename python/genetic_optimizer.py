import numpy as np
import random
from typing import List, Tuple, Dict, Any
from deap import base, creator, tools, algorithms
import logging
from tqdm import tqdm
import json
import os
from datetime import datetime

class GeneticOptimizer:
    """
    Genetic Algorithm optimizer for AnyLogic model parameters
    Optimizes multiple KPIs simultaneously
    """
    
    def __init__(self, java_interface, 
                 population_size: int = 50,
                 generations: int = 100,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.7):
        
        self.java_interface = java_interface
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.logger = logging.getLogger(__name__)
        
        # ID tracking system
        self.solution_counter = 0
        self.solution_ids = {}  # Maps solution hash to ID
        self.solution_history = []  # Track all solutions with IDs
        
        # Parameter bounds - very conservative based on observed working values
        self.parameter_bounds = {
            "varOfWork": (3, 3),  # Fixed to known working value
            "capacityOfMainConveyor": (800, 1200),  # Conservative range
            "quantityOfVagonsToSilageAtOnce": (8, 10),  # Conservative range
            "quantityOfVehicleDischargeStations": (2, 4),  # Conservative range
            "numberOfVehicleSilages": (2, 4),  # Conservative range
            "capacityOfVehicleSilages": (800, 1000),  # Conservative range
            "quantityOfSilages": (18, 20),  # Very conservative to avoid array issues
            "yearsModelWorking": (1, 1)  # Fixed to 1 year for faster execution
        }
        
        # KPI objectives (minimize or maximize)
        self.objectives = {
            "vesselsHandledQtt": "maximize",      # More vessels handled is better
            "primeCost": "minimize",              # Lower cost is better
            "handlingTime": "minimize",           # Lower handling time is better
            "profit": "maximize",                 # Higher profit is better
            "timeAtTerminal": "minimize"          # Lower terminal time is better
        }
        
        self._setup_genetic_algorithm()
        
    def _setup_genetic_algorithm(self):
        """Setup DEAP genetic algorithm components"""
        
        # Create fitness class for multi-objective optimization
        if not hasattr(creator, "FitnessMulti"):
            creator.create("FitnessMulti", base.Fitness, weights=(1.0, -1.0, -1.0, 1.0, -1.0))
        
        if not hasattr(creator, "Individual"):
            creator.create("Individual", list, fitness=creator.FitnessMulti)
        
        self.toolbox = base.Toolbox()
        
        # Attribute generator
        self.toolbox.register("attr_varOfWork", random.randint, 
                            self.parameter_bounds["varOfWork"][0], 
                            self.parameter_bounds["varOfWork"][1])
        self.toolbox.register("attr_capacityOfMainConveyor", random.randint, 
                            self.parameter_bounds["capacityOfMainConveyor"][0], 
                            self.parameter_bounds["capacityOfMainConveyor"][1])
        self.toolbox.register("attr_quantityOfVagonsToSilageAtOnce", random.randint, 
                            self.parameter_bounds["quantityOfVagonsToSilageAtOnce"][0], 
                            self.parameter_bounds["quantityOfVagonsToSilageAtOnce"][1])
        self.toolbox.register("attr_quantityOfVehicleDischargeStations", random.randint, 
                            self.parameter_bounds["quantityOfVehicleDischargeStations"][0], 
                            self.parameter_bounds["quantityOfVehicleDischargeStations"][1])
        self.toolbox.register("attr_numberOfVehicleSilages", random.randint, 
                            self.parameter_bounds["numberOfVehicleSilages"][0], 
                            self.parameter_bounds["numberOfVehicleSilages"][1])
        self.toolbox.register("attr_capacityOfVehicleSilages", random.randint, 
                            self.parameter_bounds["capacityOfVehicleSilages"][0], 
                            self.parameter_bounds["capacityOfVehicleSilages"][1])
        self.toolbox.register("attr_quantityOfSilages", random.randint, 
                            self.parameter_bounds["quantityOfSilages"][0], 
                            self.parameter_bounds["quantityOfSilages"][1])
        self.toolbox.register("attr_yearsModelWorking", random.randint, 
                            self.parameter_bounds["yearsModelWorking"][0], 
                            self.parameter_bounds["yearsModelWorking"][1])
        
        # Individual and population
        self.toolbox.register("individual", tools.initCycle, creator.Individual,
                            (self.toolbox.attr_varOfWork,
                             self.toolbox.attr_capacityOfMainConveyor,
                             self.toolbox.attr_quantityOfVagonsToSilageAtOnce,
                             self.toolbox.attr_quantityOfVehicleDischargeStations,
                             self.toolbox.attr_numberOfVehicleSilages,
                             self.toolbox.attr_capacityOfVehicleSilages,
                             self.toolbox.attr_quantityOfSilages,
                             self.toolbox.attr_yearsModelWorking), n=1)
        
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        
        # Genetic operators
        self.toolbox.register("evaluate", self._evaluate_individual)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", self._mutate_individual)
        self.toolbox.register("select", tools.selNSGA2)
        
    def _individual_to_parameters(self, individual) -> Dict[str, int]:
        """Convert individual to parameter dictionary"""
        return {
            "varOfWork": individual[0],
            "capacityOfMainConveyor": individual[1],
            "quantityOfVagonsToSilageAtOnce": individual[2],
            "quantityOfVehicleDischargeStations": individual[3],
            "numberOfVehicleSilages": individual[4],
            "capacityOfVehicleSilages": individual[5],
            "quantityOfSilages": individual[6],
            "yearsModelWorking": individual[7]
        }
    
    def _evaluate_individual(self, individual) -> Tuple[float, float, float, float, float]:
        """Evaluate an individual by running the simulation"""
        parameters = self._individual_to_parameters(individual)
        
        try:
            # Run simulation
            results = self.java_interface.run_simulation(parameters)
            
            if results is None:
                # Return worst possible values if simulation fails
                self.logger.warning(f"Simulation failed for parameters: {parameters}")
                return (-float('inf'), float('inf'), float('inf'), -float('inf'), float('inf'))
            
            # Extract KPIs from results
            kpis = [
                results.get("vesselsHandledQtt", 0),
                results.get("primeCost", float('inf')),
                results.get("handlingTime", float('inf')),
                results.get("profit", -float('inf')),
                results.get("timeAtTerminal", float('inf'))
            ]
            
            # Generate unique ID for this solution
            solution_id = self._get_or_create_solution_id(parameters, kpis)
            
            # Log successful evaluation with ID
            self.logger.debug(f"Solution {solution_id}: vessels={kpis[0]}, cost={kpis[1]}, profit={kpis[3]}")
            
            return tuple(kpis)
            
        except Exception as e:
            self.logger.error(f"Error evaluating individual with parameters {parameters}: {e}")
            # Return worst possible values if simulation fails
            return (-float('inf'), float('inf'), float('inf'), -float('inf'), float('inf'))
    
    def _get_or_create_solution_id(self, parameters: Dict[str, int], kpis: List[float]) -> str:
        """Generate or retrieve unique ID for a solution"""
        # Create a hash of the parameters to identify unique solutions
        param_hash = hash(tuple(sorted(parameters.items())))
        
        if param_hash not in self.solution_ids:
            self.solution_counter += 1
            solution_id = f"SOL_{self.solution_counter:06d}"
            self.solution_ids[param_hash] = solution_id
            
            # Store solution in history
            solution_record = {
                "id": solution_id,
                "parameters": parameters.copy(),
                "kpis": kpis.copy(),
                "timestamp": datetime.now().isoformat(),
                "generation": None  # Will be set during optimization
            }
            self.solution_history.append(solution_record)
            
        return self.solution_ids[param_hash]
    
    def _mutate_individual(self, individual):
        """Custom mutation operator that respects parameter bounds"""
        for i, (param_name, bounds) in enumerate(self.parameter_bounds.items()):
            if random.random() < self.mutation_rate:
                individual[i] = random.randint(bounds[0], bounds[1])
        return individual,
    
    def optimize(self) -> Tuple[List, List]:
        """
        Run the genetic algorithm optimization
        
        Returns:
            Tuple of (final_population, pareto_front)
        """
        self.logger.info("Starting genetic algorithm optimization...")
        
        # Create initial population
        pop = self.toolbox.population(n=self.population_size)
        
        # Statistics
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean, axis=0)
        stats.register("std", np.std, axis=0)
        stats.register("min", np.min, axis=0)
        stats.register("max", np.max, axis=0)
        
        # Hall of fame for Pareto front
        hof = tools.ParetoFront()
        
        # Run algorithm
        pop, logbook = algorithms.eaMuPlusLambda(
            pop, self.toolbox,
            mu=self.population_size, lambda_=self.population_size,
            cxpb=self.crossover_rate, mutpb=self.mutation_rate,
            ngen=self.generations,
            stats=stats, halloffame=hof, verbose=True
        )
        
        self.logger.info("Optimization completed!")
        
        return pop, list(hof)
    
    def save_results(self, population: List, pareto_front: List, filename: str = "optimization_results.json"):
        """Save optimization results to file with ID tracking"""
        results = {
            "population": [],
            "pareto_front": [],
            "solution_history": self.solution_history,
            "parameter_bounds": self.parameter_bounds,
            "objectives": self.objectives,
            "optimization_metadata": {
                "total_solutions_evaluated": self.solution_counter,
                "unique_solutions": len(self.solution_ids),
                "population_size": self.population_size,
                "generations": self.generations,
                "mutation_rate": self.mutation_rate,
                "crossover_rate": self.crossover_rate
            }
        }
        
        # Save population with IDs
        for individual in population:
            params = self._individual_to_parameters(individual)
            param_hash = hash(tuple(sorted(params.items())))
            solution_id = self.solution_ids.get(param_hash, "UNKNOWN")
            
            results["population"].append({
                "id": solution_id,
                "parameters": params,
                "fitness": individual.fitness.values if individual.fitness.valid else None
            })
        
        # Save Pareto front with IDs
        for individual in pareto_front:
            params = self._individual_to_parameters(individual)
            param_hash = hash(tuple(sorted(params.items())))
            solution_id = self.solution_ids.get(param_hash, "UNKNOWN")
            
            results["pareto_front"].append({
                "id": solution_id,
                "parameters": params,
                "fitness": individual.fitness.values if individual.fitness.valid else None
            })
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        self.logger.info(f"Results saved to {filename}")
        self.logger.info(f"Total solutions evaluated: {self.solution_counter}")
        self.logger.info(f"Unique solutions: {len(self.solution_ids)}")
        self.logger.info(f"Pareto front size: {len(pareto_front)}")
    
    def get_best_solutions(self, pareto_front: List, n: int = 5) -> List[Dict]:
        """Get the best solutions from Pareto front with IDs"""
        if not pareto_front:
            return []
        
        # Sort by different objectives
        sorted_by_profit = sorted(pareto_front, key=lambda x: x.fitness.values[3], reverse=True)
        sorted_by_vessels = sorted(pareto_front, key=lambda x: x.fitness.values[0], reverse=True)
        sorted_by_cost = sorted(pareto_front, key=lambda x: x.fitness.values[1])
        
        best_solutions = []
        
        # Add best by profit
        if sorted_by_profit:
            params = self._individual_to_parameters(sorted_by_profit[0])
            param_hash = hash(tuple(sorted(params.items())))
            solution_id = self.solution_ids.get(param_hash, "UNKNOWN")
            
            best_solutions.append({
                "id": solution_id,
                "criterion": "Best Profit",
                "parameters": params,
                "fitness": sorted_by_profit[0].fitness.values
            })
        
        # Add best by vessels handled
        if sorted_by_vessels:
            params = self._individual_to_parameters(sorted_by_vessels[0])
            param_hash = hash(tuple(sorted(params.items())))
            solution_id = self.solution_ids.get(param_hash, "UNKNOWN")
            
            best_solutions.append({
                "id": solution_id,
                "criterion": "Most Vessels Handled",
                "parameters": params,
                "fitness": sorted_by_vessels[0].fitness.values
            })
        
        # Add best by cost
        if sorted_by_cost:
            params = self._individual_to_parameters(sorted_by_cost[0])
            param_hash = hash(tuple(sorted(params.items())))
            solution_id = self.solution_ids.get(param_hash, "UNKNOWN")
            
            best_solutions.append({
                "id": solution_id,
                "criterion": "Lowest Cost",
                "parameters": params,
                "fitness": sorted_by_cost[0].fitness.values
            })
        
        return best_solutions[:n]
