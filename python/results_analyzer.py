import json
import logging
from typing import Literal

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# hide logging from noisy plotting libs
logging.getLogger('kaleido').setLevel('CRITICAL')
logging.getLogger('choreographer').setLevel('CRITICAL')


class ResultsAnalyzer:
    """
    Generates 2D plot projections for MOOP results task, for the following conflicting features:
    1. Handling time vs. profit;
    2. Terminal time vs. vessels handled;
    3. Prime cost vs. profit => not conflicting;
    4. Prime cost vs. vessels handled => not conflicting;
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.kpi_names = [
            "vesselsHandledQtt",
            "primeCost",
            "handlingTime",
            "profit",
            "timeAtTerminal"
        ]

        # Set style for plots
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")

    def load_results(self, filename: str) -> dict:
        """Load optimization results from file"""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading results: {e}")
            return {}

    @staticmethod
    def extract_solution_data(
            results: dict,
            key_: Literal['solution_history', 'pareto_front']
    ) -> pd.DataFrame:
        solution_data = []

        for solution in results.get(key_, []):
            params = solution["parameters"]
            fitness = solution["fitness"]
            solution_id = solution.get("id", "UNKNOWN")

            if fitness:
                row = {
                    "id": solution_id,
                    **params,
                    "vesselsHandledQtt": fitness[0],
                    "primeCost": fitness[1],
                    "handlingTime": fitness[2],
                    "profit": fitness[3],
                    "timeAtTerminal": fitness[4]
                }
                solution_data.append(row)

        return pd.DataFrame(solution_data)

    def identify_pareto_frontier(
            self,
            df: pd.DataFrame,
            objectives: list[str] = None
    ) -> pd.DataFrame:
        """
        Identify Pareto optimal solutions

        Args:
            df: DataFrame with solutions and objectives
            objectives: List of objective column names to consider

        Returns:
            DataFrame with only Pareto optimal solutions
        """
        if objectives is None:
            objectives = ["vesselsHandledQtt", "profit"]  # Default to 2D Pareto front

        pareto_mask = np.ones(len(df), dtype=bool)

        for i in range(len(df)):
            for j in range(len(df)):
                if i != j:
                    # Check if solution j dominates solution i
                    at_least_one_better = False
                    all_better_or_equal = True

                    for obj in objectives:
                        # hardcoded valus
                        if obj in ["vesselsHandledQtt", "profit"]:
                            # Maximize objectives
                            if df.iloc[j][obj] > df.iloc[i][obj]:
                                at_least_one_better = True
                            elif df.iloc[j][obj] < df.iloc[i][obj]:
                                all_better_or_equal = False
                                break
                        else:
                            # Minimize objectives
                            if df.iloc[j][obj] < df.iloc[i][obj]:
                                at_least_one_better = True
                            elif df.iloc[j][obj] > df.iloc[i][obj]:
                                all_better_or_equal = False
                                break

                    # j dominates i only if better-or-equal in all AND strictly better in at least one
                    if all_better_or_equal and at_least_one_better:
                        pareto_mask[i] = False
                        break

        return df[pareto_mask]

    @staticmethod
    def _filter_pareto(
            pareto_df: pd.DataFrame,
            sol_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """Filter pareto points out of all solutions"""
        if 'id' in sol_df.columns and 'id' in pareto_df.columns:
            # Remove solutions that have IDs present in pareto_df
            sol_df_filtered = sol_df[~sol_df['id'].isin(pareto_df['id'])]
        else:
            # Fall back to comparing by index if no 'id' column
            sol_df_filtered = sol_df[~sol_df.index.isin(pareto_df.index)]

        return sol_df_filtered

    def plot_2d_pareto_frontier(
            self,
            pareto_df: pd.DataFrame,
            sol_df: pd.DataFrame,
            x_obj: str,
            y_obj: str,
            title: str,
            save_path: str = None
    ) -> go.Figure:
        fig = go.Figure()

        # plot all solution points (excluding pareto points)
        fig.add_trace(go.Scatter(
            x=sol_df[x_obj],
            y=sol_df[y_obj],
            mode='markers',
            name='All Solutions',
            marker=dict(color='lightblue', size=8, opacity=0.6),
            hovertemplate=f'ID: %{{customdata}}<br>{x_obj}: %{{x}}<br>{y_obj}: %{{y}}<extra></extra>',
            customdata=sol_df.get('id', ['N/A'] * len(sol_df))
        ))

        # plot pareto points
        fig.add_trace(go.Scatter(
            x=pareto_df[x_obj],
            y=pareto_df[y_obj],
            mode='markers',
            name='Pareto Points',
            marker=dict(color='yellow', size=8, opacity=0.6),
            hovertemplate=f'ID: %{{customdata}}<br>{x_obj}: %{{x}}<br>{y_obj}: %{{y}}<extra></extra>',
            customdata=pareto_df.get('id', ['N/A'] * len(pareto_df))
        ))

        # plot pareto frontier for this projection
        frontier = self.identify_pareto_frontier(pareto_df, objectives=[x_obj, y_obj])
        frontier_sorted = frontier.sort_values([x_obj])
        fig.add_trace(go.Scatter(
            x=frontier_sorted[x_obj],
            y=frontier_sorted[y_obj],
            mode='lines+markers',
            name='Projection Pareto Frontier',
            marker=dict(color='yellow', size=8, opacity=0.6),
            hovertemplate=f'ID: %{{customdata}}<br>{x_obj}: %{{x}}<br>{y_obj}: %{{y}}<extra></extra>',
            customdata=pareto_df.get('id', ['N/A'] * len(frontier_sorted))
        ))

        fig.update_layout(
            title=title,
            xaxis_title=x_obj,
            yaxis_title=y_obj,
            template='plotly_white',
            width=800,
            height=600
        )

        if save_path:
            fig.write_html(save_path)
            fig.write_image(save_path.replace('.html', '.png'))

        return fig

    def generate_comprehensive_report(
            self,
            results_file: str,
            output_dir: str = 'pareto_analysis'
    ) -> dict:
        """
                Generate comprehensive Pareto analysis report

                Args:
                    results_file: Path to optimization results JSON file
                    output_dir: Directory to save analysis outputs

                Returns:
                    Dictionary with analysis summary
                """
        import os
        os.makedirs(output_dir, exist_ok=True)

        # Load results
        results = self.load_results(results_file)
        if not results:
            return {}

        # Extract data
        pareto_df = self.extract_solution_data(results, 'pareto_front')
        sol_df = self.extract_solution_data(results, 'solution_history')
        sold_df = self._filter_pareto(pareto_df, sol_df)
        if pareto_df.empty or sol_df.empty:
            self.logger.error("No data found in results file")
            return {}

        # Generate plots
        plots = {}

        # 2D Pareto frontiers
        plot_combinations = [
            ("handlingTime", "profit", "Handling Time vs Profit"),
            ("timeAtTerminal", "vesselsHandledQtt", "Terminal Time vs Vessels Handled"),
        ]

        for x_obj, y_obj, title in plot_combinations:
            fig = self.plot_2d_pareto_frontier(
                pareto_df, sol_df, x_obj, y_obj, title,
                f"{output_dir}/pareto_2d_{x_obj}_vs_{y_obj}.html"
            )
            plots[f"2d_{x_obj}_vs_{y_obj}"] = fig

        summary = {
            'total_solutions': len(sol_df),
            'pareto_solutions': len(pareto_df),
            'pareto_percentage': len(pareto_df) / len(sol_df) * 100,
            'kpi_ranges': {},
            'pareto_kpi_ranges': {}
        }

        for kpi in self.kpi_names:
            summary["kpi_ranges"][kpi] = {
                "min": float(sol_df[kpi].min()),
                "max": float(sol_df[kpi].max()),
                "mean": float(sol_df[kpi].mean()),
                "std": float(sol_df[kpi].std())
            }

            if len(pareto_df) > 0:
                summary["pareto_kpi_ranges"][kpi] = {
                    "min": float(pareto_df[kpi].min()),
                    "max": float(pareto_df[kpi].max()),
                    "mean": float(pareto_df[kpi].mean()),
                    "std": float(pareto_df[kpi].std())
                }

        # Save summary
        with open(f"{output_dir}/analysis_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)

        # Save Pareto solutions
        pareto_df.to_csv(f"{output_dir}/pareto_solutions.csv", index=False)

        self.logger.info(f"Comprehensive report generated in {output_dir}")

        return {
            "summary": summary,
            "plots": plots,
            "pareto_solutions": pareto_df.to_dict('records')
        }
