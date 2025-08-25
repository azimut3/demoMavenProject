#!/usr/bin/env python3
"""
Demo script to show ID tracking capabilities for Pareto frontier analysis
"""

import json
import sys
import os

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from python.utils.solution_analyzer import SolutionAnalyzer

def demo_id_tracking():
    """Demonstrate the ID tracking system"""
    
    # Load the results
    results_file = "optimization_results/optimization_results.json"
    
    if not os.path.exists(results_file):
        print(f"Results file not found: {results_file}")
        print("Please run the optimization first: python -m python.main_optimizer")
        return
    
    analyzer = SolutionAnalyzer(results_file)
    
    print("=" * 60)
    print("ID TRACKING SYSTEM DEMONSTRATION")
    print("=" * 60)
    
    # Show optimization summary
    analyzer.print_optimization_summary()
    
    # Get Pareto solutions
    pareto_solutions = analyzer.get_pareto_solutions()
    
    print(f"\n{'='*60}")
    print("PARETO FRONTIER SOLUTIONS WITH IDs")
    print(f"{'='*60}")
    
    for i, solution in enumerate(pareto_solutions, 1):
        solution_id = solution.get("id", "UNKNOWN")
        params = solution.get("parameters", {})
        fitness = solution.get("fitness", [0, 0, 0, 0, 0])
        
        print(f"\n{i}. Solution {solution_id}:")
        print(f"   Vessels Handled: {fitness[0]}")
        print(f"   Prime Cost: {fitness[1]:.2f}")
        print(f"   Handling Time: {fitness[2]:.2f}")
        print(f"   Profit: {fitness[3]:.2f}")
        print(f"   Time at Terminal: {fitness[4]:.2f}")
        print(f"   Key Parameters:")
        print(f"     - Capacity of Main Conveyor: {params.get('capacityOfMainConveyor', 'N/A')}")
        print(f"     - Quantity of Silages: {params.get('quantityOfSilages', 'N/A')}")
        print(f"     - Capacity of Vehicle Silages: {params.get('capacityOfVehicleSilages', 'N/A')}")
    
    # Show specific solution details
    if pareto_solutions:
        best_solution_id = pareto_solutions[0].get("id")
        print(f"\n{'='*60}")
        print(f"DETAILED ANALYSIS OF SOLUTION {best_solution_id}")
        print(f"{'='*60}")
        analyzer.print_solution_summary(best_solution_id)
    
    # Export Pareto solutions to CSV
    print(f"\n{'='*60}")
    print("EXPORTING PARETO SOLUTIONS TO CSV")
    print(f"{'='*60}")
    csv_file = "pareto_solutions_with_ids.csv"
    df = analyzer.export_pareto_to_csv(csv_file)
    
    if df is not None:
        print(f"✅ Pareto solutions exported to: {csv_file}")
        print(f"📊 CSV contains {len(df)} solutions with IDs")
        print("\nFirst few rows:")
        print(df.head().to_string(index=False))
    
    # Find similar solutions
    if pareto_solutions:
        target_id = pareto_solutions[0].get("id")
        print(f"\n{'='*60}")
        print(f"FINDING SIMILAR SOLUTIONS TO {target_id}")
        print(f"{'='*60}")
        
        similar_solutions = analyzer.find_similar_solutions(target_id, similarity_threshold=0.7)
        
        if similar_solutions:
            print(f"Found {len(similar_solutions)} similar solutions:")
            for i, similar in enumerate(similar_solutions[:3], 1):  # Show top 3
                print(f"\n{i}. Solution {similar['id']} (similarity: {similar['similarity']:.3f})")
                params = similar['parameters']
                print(f"   Capacity of Main Conveyor: {params.get('capacityOfMainConveyor', 'N/A')}")
                print(f"   Quantity of Silages: {params.get('quantityOfSilages', 'N/A')}")
        else:
            print("No similar solutions found with similarity threshold 0.7")
    
    print(f"\n{'='*60}")
    print("ID TRACKING BENEFITS")
    print(f"{'='*60}")
    print("✅ Each solution has a unique ID (SOL_XXXXXX)")
    print("✅ Easy to reference specific solutions in reports")
    print("✅ Track solution evolution across generations")
    print("✅ Compare solutions by ID in different analyses")
    print("✅ Export specific solutions for further investigation")
    print("✅ Find similar solutions using parameter similarity")
    print("✅ Maintain solution history with timestamps")
    
    print(f"\n{'='*60}")
    print("USAGE EXAMPLES")
    print(f"{'='*60}")
    print("1. Get solution by ID:")
    print("   analyzer.get_solution_by_id('SOL_000010')")
    print("\n2. Find similar solutions:")
    print("   analyzer.find_similar_solutions('SOL_000010', similarity_threshold=0.8)")
    print("\n3. Export Pareto solutions:")
    print("   analyzer.export_pareto_to_csv('my_pareto.csv')")
    print("\n4. Get solution statistics:")
    print("   stats = analyzer.get_solution_statistics()")

if __name__ == "__main__":
    demo_id_tracking()
