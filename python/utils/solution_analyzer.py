#!/usr/bin/env python3
"""
Solution Analyzer - Utility for tracking and analyzing solutions by ID
"""

import json
import pandas as pd
from typing import Dict, List, Optional
import logging

class SolutionAnalyzer:
    """Analyze solutions from optimization results with ID tracking"""
    
    def __init__(self, results_file: str):
        self.results_file = results_file
        self.results = self._load_results()
        self.logger = logging.getLogger(__name__)
    
    def _load_results(self) -> Dict:
        """Load optimization results from file"""
        try:
            with open(self.results_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading results file: {e}")
            return {}
    
    def get_solution_by_id(self, solution_id: str) -> Optional[Dict]:
        """Get a specific solution by its ID"""
        # Search in solution history
        for solution in self.results.get("solution_history", []):
            if solution.get("id") == solution_id:
                return solution
        
        # Search in Pareto front
        for solution in self.results.get("pareto_front", []):
            if solution.get("id") == solution_id:
                return solution
        
        # Search in population
        for solution in self.results.get("population", []):
            if solution.get("id") == solution_id:
                return solution
        
        return None
    
    def get_pareto_solutions(self) -> List[Dict]:
        """Get all Pareto optimal solutions with IDs"""
        return self.results.get("pareto_front", [])
    
    def get_solution_statistics(self) -> Dict:
        """Get statistics about all solutions"""
        if not self.results:
            return {}
        
        history = self.results.get("solution_history", [])
        pareto_front = self.results.get("pareto_front", [])
        
        stats = {
            "total_solutions": len(history),
            "pareto_solutions": len(pareto_front),
            "pareto_percentage": len(pareto_front) / len(history) * 100 if history else 0,
            "unique_solutions": len(set(s.get("id") for s in history)),
            "optimization_metadata": self.results.get("optimization_metadata", {})
        }
        
        return stats
    
    def export_pareto_to_csv(self, output_file: str = "pareto_solutions.csv"):
        """Export Pareto solutions to CSV with IDs"""
        pareto_solutions = self.get_pareto_solutions()
        
        if not pareto_solutions:
            self.logger.warning("No Pareto solutions found")
            return
        
        # Create DataFrame
        data = []
        for solution in pareto_solutions:
            row = {
                "id": solution.get("id"),
                **solution.get("parameters", {}),
                "vesselsHandledQtt": solution.get("fitness", [0, 0, 0, 0, 0])[0],
                "primeCost": solution.get("fitness", [0, 0, 0, 0, 0])[1],
                "handlingTime": solution.get("fitness", [0, 0, 0, 0, 0])[2],
                "profit": solution.get("fitness", [0, 0, 0, 0, 0])[3],
                "timeAtTerminal": solution.get("fitness", [0, 0, 0, 0, 0])[4]
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False)
        self.logger.info(f"Pareto solutions exported to {output_file}")
        
        return df
    
    def find_similar_solutions(self, target_solution_id: str, similarity_threshold: float = 0.8) -> List[Dict]:
        """Find solutions similar to a target solution"""
        target_solution = self.get_solution_by_id(target_solution_id)
        if not target_solution:
            return []
        
        target_params = target_solution.get("parameters", {})
        similar_solutions = []
        
        for solution in self.results.get("solution_history", []):
            if solution.get("id") == target_solution_id:
                continue
            
            params = solution.get("parameters", {})
            similarity = self._calculate_similarity(target_params, params)
            
            if similarity >= similarity_threshold:
                similar_solutions.append({
                    "id": solution.get("id"),
                    "similarity": similarity,
                    "parameters": params,
                    "kpis": solution.get("kpis", [])
                })
        
        # Sort by similarity
        similar_solutions.sort(key=lambda x: x["similarity"], reverse=True)
        return similar_solutions
    
    def _calculate_similarity(self, params1: Dict, params2: Dict) -> float:
        """Calculate similarity between two parameter sets"""
        if not params1 or not params2:
            return 0.0
        
        # Normalize parameters to 0-1 range for comparison
        normalized_params1 = self._normalize_parameters(params1)
        normalized_params2 = self._normalize_parameters(params2)
        
        # Calculate Euclidean distance
        total_diff = 0
        for key in normalized_params1:
            if key in normalized_params2:
                diff = normalized_params1[key] - normalized_params2[key]
                total_diff += diff ** 2
        
        distance = (total_diff ** 0.5) / len(normalized_params1)
        similarity = 1 - distance
        
        return max(0, min(1, similarity))
    
    def _normalize_parameters(self, params: Dict) -> Dict:
        """Normalize parameters to 0-1 range"""
        # Use parameter bounds from results
        bounds = self.results.get("parameter_bounds", {})
        normalized = {}
        
        for param, value in params.items():
            if param in bounds:
                min_val, max_val = bounds[param]
                if max_val > min_val:
                    normalized[param] = (value - min_val) / (max_val - min_val)
                else:
                    normalized[param] = 0.5
            else:
                normalized[param] = 0.5
        
        return normalized
    
    def print_solution_summary(self, solution_id: str):
        """Print a detailed summary of a specific solution"""
        solution = self.get_solution_by_id(solution_id)
        if not solution:
            print(f"Solution {solution_id} not found")
            return
        
        print(f"\n=== Solution {solution_id} Summary ===")
        print(f"ID: {solution.get('id')}")
        print(f"Timestamp: {solution.get('timestamp', 'N/A')}")
        
        print("\nParameters:")
        for param, value in solution.get("parameters", {}).items():
            print(f"  {param}: {value}")
        
        print("\nKPIs:")
        kpis = solution.get("kpis", [])
        if kpis:
            print(f"  Vessels Handled: {kpis[0]}")
            print(f"  Prime Cost: {kpis[1]}")
            print(f"  Handling Time: {kpis[2]}")
            print(f"  Profit: {kpis[3]}")
            print(f"  Time at Terminal: {kpis[4]}")
        
        # Check if it's in Pareto front
        pareto_ids = [s.get("id") for s in self.get_pareto_solutions()]
        if solution_id in pareto_ids:
            print("\n✅ This solution is on the Pareto frontier!")
        else:
            print("\n❌ This solution is not on the Pareto frontier")
    
    def print_optimization_summary(self):
        """Print a summary of the optimization results"""
        stats = self.get_solution_statistics()
        
        print("\n=== Optimization Summary ===")
        print(f"Total solutions evaluated: {stats.get('total_solutions', 0)}")
        print(f"Unique solutions: {stats.get('unique_solutions', 0)}")
        print(f"Pareto solutions: {stats.get('pareto_solutions', 0)}")
        print(f"Pareto percentage: {stats.get('pareto_percentage', 0):.2f}%")
        
        metadata = stats.get("optimization_metadata", {})
        if metadata:
            print(f"\nOptimization Parameters:")
            print(f"  Population size: {metadata.get('population_size', 'N/A')}")
            print(f"  Generations: {metadata.get('generations', 'N/A')}")
            print(f"  Mutation rate: {metadata.get('mutation_rate', 'N/A')}")
            print(f"  Crossover rate: {metadata.get('crossover_rate', 'N/A')}")

def main():
    """Example usage of SolutionAnalyzer"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python solution_analyzer.py <results_file> [solution_id]")
        return
    
    results_file = sys.argv[1]
    analyzer = SolutionAnalyzer(results_file)
    
    if len(sys.argv) >= 3:
        solution_id = sys.argv[2]
        analyzer.print_solution_summary(solution_id)
    else:
        analyzer.print_optimization_summary()
        analyzer.export_pareto_to_csv()

if __name__ == "__main__":
    main()
