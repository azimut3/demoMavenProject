#!/usr/bin/env python3
"""
Simple script to demonstrate ID tracking in Pareto frontier analysis
"""

import sys
import os

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from python.utils.solution_analyzer import SolutionAnalyzer

def main():
    """Demonstrate ID tracking features"""
    
    results_file = "optimization_results/optimization_results.json"
    
    if not os.path.exists(results_file):
        print(f"❌ Results file not found: {results_file}")
        print("Please run the optimization first: python -m python.main_optimizer")
        return
    
    print("🎯 ID TRACKING SYSTEM DEMONSTRATION")
    print("=" * 50)
    
    # Load the analyzer
    analyzer = SolutionAnalyzer(results_file)
    
    # Show summary
    analyzer.print_optimization_summary()
    
    # Get Pareto solutions
    pareto_solutions = analyzer.get_pareto_solutions()
    
    print(f"\n📊 PARETO FRONTIER SOLUTIONS WITH IDs")
    print("=" * 50)
    
    for i, solution in enumerate(pareto_solutions, 1):
        solution_id = solution.get("id", "UNKNOWN")
        params = solution.get("parameters", {})
        fitness = solution.get("fitness", [0, 0, 0, 0, 0])
        
        print(f"\n{i}. {solution_id}:")
        print(f"   🚢 Vessels: {fitness[0]}")
        print(f"   💰 Profit: {fitness[3]:.0f}")
        print(f"   💸 Cost: {fitness[1]:.1f}")
        print(f"   ⏱️  Handling Time: {fitness[2]:.1f}")
        print(f"   🏭 Terminal Time: {fitness[4]:.1f}")
    
    # Show specific solution details
    if pareto_solutions:
        best_solution_id = pareto_solutions[0].get("id")
        print(f"\n🔍 DETAILED ANALYSIS OF {best_solution_id}")
        print("=" * 50)
        analyzer.print_solution_summary(best_solution_id)
    
    # Export to CSV
    print(f"\n📁 EXPORTING PARETO SOLUTIONS")
    print("=" * 50)
    csv_file = "pareto_solutions_with_ids.csv"
    df = analyzer.export_pareto_to_csv(csv_file)
    
    if df is not None:
        print(f"✅ Exported to: {csv_file}")
        print(f"📊 Contains {len(df)} solutions with IDs")
    
    print(f"\n🎨 VISUALIZATION FILES GENERATED")
    print("=" * 50)
    print("📈 Pareto Frontier with IDs: optimization_results/pareto_analysis/pareto_frontier_with_ids.html")
    print("📊 All Pareto plots: optimization_results/pareto_analysis/")
    print("📋 Pareto solutions CSV: optimization_results/pareto_analysis/pareto_solutions.csv")
    
    print(f"\n💡 ID TRACKING BENEFITS")
    print("=" * 50)
    print("✅ Each solution has unique ID (SOL_XXXXXX)")
    print("✅ Hover over points in plots to see IDs")
    print("✅ Easy to reference specific solutions")
    print("✅ Track solution evolution across generations")
    print("✅ Export specific solutions for analysis")
    print("✅ Compare solutions by ID in reports")

if __name__ == "__main__":
    main()
