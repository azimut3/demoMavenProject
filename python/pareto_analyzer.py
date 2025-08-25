import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List, Dict, Tuple, Optional
import json
from scipy.spatial import ConvexHull
from sklearn.preprocessing import StandardScaler
import logging

class ParetoAnalyzer:
    """
    Analyzer for Pareto frontier and optimization results
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
    
    def load_results(self, filename: str) -> Dict:
        """Load optimization results from file"""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading results: {e}")
            return {}
    
    def extract_pareto_data(self, results: Dict) -> pd.DataFrame:
        """Extract Pareto front data into a DataFrame"""
        pareto_data = []
        
        for solution in results.get("pareto_front", []):
            params = solution["parameters"]
            fitness = solution["fitness"]
            
            if fitness:
                row = {
                    **params,
                    "vesselsHandledQtt": fitness[0],
                    "primeCost": fitness[1],
                    "handlingTime": fitness[2],
                    "profit": fitness[3],
                    "timeAtTerminal": fitness[4]
                }
                pareto_data.append(row)
        
        return pd.DataFrame(pareto_data)
    
    def identify_pareto_frontier(self, df: pd.DataFrame, 
                               objectives: List[str] = None) -> pd.DataFrame:
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
                    dominates = True
                    for obj in objectives:
                        if obj in ["vesselsHandledQtt", "profit"]:
                            # Maximize objectives
                            if df.iloc[j][obj] < df.iloc[i][obj]:
                                dominates = False
                                break
                        else:
                            # Minimize objectives
                            if df.iloc[j][obj] > df.iloc[i][obj]:
                                dominates = False
                                break
                    
                    if dominates:
                        pareto_mask[i] = False
                        break
        
        return df[pareto_mask]
    
    def plot_2d_pareto_frontier(self, df: pd.DataFrame, 
                               x_obj: str = "primeCost",
                               y_obj: str = "profit",
                               title: str = "Pareto Frontier",
                               save_path: str = None) -> go.Figure:
        """
        Create 2D Pareto frontier plot
        
        Args:
            df: DataFrame with solutions
            x_obj: X-axis objective
            y_obj: Y-axis objective
            title: Plot title
            save_path: Path to save the plot
            
        Returns:
            Plotly figure object
        """
        # Identify Pareto frontier
        pareto_df = self.identify_pareto_frontier(df, [x_obj, y_obj])
        
        # Create scatter plot
        fig = go.Figure()
        
        # All solutions
        fig.add_trace(go.Scatter(
            x=df[x_obj],
            y=df[y_obj],
            mode='markers',
            name='All Solutions',
            marker=dict(color='lightblue', size=8, opacity=0.6),
            hovertemplate=f'{x_obj}: %{{x}}<br>{y_obj}: %{{y}}<extra></extra>'
        ))
        
        # Pareto frontier
        if len(pareto_df) > 0:
            # Sort by x_obj for proper line connection
            pareto_df_sorted = pareto_df.sort_values(x_obj)
            
            fig.add_trace(go.Scatter(
                x=pareto_df_sorted[x_obj],
                y=pareto_df_sorted[y_obj],
                mode='lines+markers',
                name='Pareto Frontier',
                line=dict(color='red', width=3),
                marker=dict(color='red', size=10),
                hovertemplate=f'{x_obj}: %{{x}}<br>{y_obj}: %{{y}}<extra></extra>'
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
    
    def plot_3d_pareto_frontier(self, df: pd.DataFrame,
                               x_obj: str = "primeCost",
                               y_obj: str = "profit", 
                               z_obj: str = "vesselsHandledQtt",
                               title: str = "3D Pareto Frontier",
                               save_path: str = None) -> go.Figure:
        """Create 3D Pareto frontier plot"""
        
        # Identify Pareto frontier
        pareto_df = self.identify_pareto_frontier(df, [x_obj, y_obj, z_obj])
        
        fig = go.Figure()
        
        # All solutions
        fig.add_trace(go.Scatter3d(
            x=df[x_obj],
            y=df[y_obj],
            z=df[z_obj],
            mode='markers',
            name='All Solutions',
            marker=dict(color='lightblue', size=5, opacity=0.6),
            hovertemplate=f'{x_obj}: %{{x}}<br>{y_obj}: %{{y}}<br>{z_obj}: %{{z}}<extra></extra>'
        ))
        
        # Pareto frontier
        if len(pareto_df) > 0:
            fig.add_trace(go.Scatter3d(
                x=pareto_df[x_obj],
                y=pareto_df[y_obj],
                z=pareto_df[z_obj],
                mode='markers',
                name='Pareto Frontier',
                marker=dict(color='red', size=8),
                hovertemplate=f'{x_obj}: %{{x}}<br>{y_obj}: %{{y}}<br>{z_obj}: %{{z}}<extra></extra>'
            ))
        
        fig.update_layout(
            title=title,
            scene=dict(
                xaxis_title=x_obj,
                yaxis_title=y_obj,
                zaxis_title=z_obj
            ),
            template='plotly_white',
            width=900,
            height=700
        )
        
        if save_path:
            fig.write_html(save_path)
            fig.write_image(save_path.replace('.html', '.png'))
        
        return fig
    
    def plot_parallel_coordinates(self, df: pd.DataFrame,
                                 objectives: List[str] = None,
                                 title: str = "Parallel Coordinates Plot",
                                 save_path: str = None) -> go.Figure:
        """Create parallel coordinates plot for all objectives"""
        
        if objectives is None:
            objectives = self.kpi_names
        
        # Normalize objectives for better visualization
        df_normalized = df.copy()
        scaler = StandardScaler()
        df_normalized[objectives] = scaler.fit_transform(df[objectives])
        
        # Identify Pareto frontier
        pareto_df = self.identify_pareto_frontier(df, objectives)
        pareto_normalized = df_normalized[df_normalized.index.isin(pareto_df.index)]
        
        fig = go.Figure()
        
        # All solutions
        for i, row in df_normalized.iterrows():
            fig.add_trace(go.Scatter(
                x=objectives,
                y=row[objectives],
                mode='lines',
                line=dict(color='lightblue', width=1),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Pareto frontier
        for i, row in pareto_normalized.iterrows():
            fig.add_trace(go.Scatter(
                x=objectives,
                y=row[objectives],
                mode='lines',
                line=dict(color='red', width=2),
                showlegend=False,
                hovertemplate='<extra></extra>'
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Objectives",
            yaxis_title="Normalized Values",
            template='plotly_white',
            width=1000,
            height=600
        )
        
        if save_path:
            fig.write_html(save_path)
            fig.write_image(save_path.replace('.html', '.png'))
        
        return fig
    
    def plot_parameter_distributions(self, df: pd.DataFrame,
                                   save_path: str = None) -> go.Figure:
        """Plot distributions of parameters for Pareto optimal solutions"""
        
        # Get parameter columns
        param_cols = [col for col in df.columns if col not in self.kpi_names]
        
        # Identify Pareto frontier
        pareto_df = self.identify_pareto_frontier(df, self.kpi_names)
        
        # Create subplots
        n_cols = 3
        n_rows = (len(param_cols) + n_cols - 1) // n_cols
        
        fig = make_subplots(
            rows=n_rows, cols=n_cols,
            subplot_titles=param_cols,
            specs=[[{"secondary_y": False}] * n_cols] * n_rows
        )
        
        for i, param in enumerate(param_cols):
            row = i // n_cols + 1
            col = i % n_cols + 1
            
            # All solutions histogram
            fig.add_trace(
                go.Histogram(
                    x=df[param],
                    name='All Solutions',
                    marker_color='lightblue',
                    showlegend=(i == 0)
                ),
                row=row, col=col
            )
            
            # Pareto frontier histogram
            if len(pareto_df) > 0:
                fig.add_trace(
                    go.Histogram(
                        x=pareto_df[param],
                        name='Pareto Frontier',
                        marker_color='red',
                        showlegend=(i == 0)
                    ),
                    row=row, col=col
                )
        
        fig.update_layout(
            title="Parameter Distributions: All Solutions vs Pareto Frontier",
            template='plotly_white',
            width=1200,
            height=300 * n_rows
        )
        
        if save_path:
            fig.write_html(save_path)
            fig.write_image(save_path.replace('.html', '.png'))
        
        return fig
    
    def generate_comprehensive_report(self, results_file: str, 
                                    output_dir: str = "pareto_analysis") -> Dict:
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
        df = self.extract_pareto_data(results)
        if df.empty:
            self.logger.error("No data found in results file")
            return {}
        
        # Generate plots
        plots = {}
        
        # 2D Pareto frontiers
        plot_combinations = [
            ("primeCost", "profit", "Cost vs Profit"),
            ("handlingTime", "profit", "Handling Time vs Profit"),
            ("timeAtTerminal", "vesselsHandledQtt", "Terminal Time vs Vessels Handled"),
            ("primeCost", "vesselsHandledQtt", "Cost vs Vessels Handled")
        ]
        
        for x_obj, y_obj, title in plot_combinations:
            fig = self.plot_2d_pareto_frontier(
                df, x_obj, y_obj, title,
                f"{output_dir}/pareto_2d_{x_obj}_vs_{y_obj}.html"
            )
            plots[f"2d_{x_obj}_vs_{y_obj}"] = fig
        
        # 3D Pareto frontier
        fig_3d = self.plot_3d_pareto_frontier(
            df, "primeCost", "profit", "vesselsHandledQtt",
            "3D Pareto Frontier: Cost vs Profit vs Vessels Handled",
            f"{output_dir}/pareto_3d.html"
        )
        plots["3d"] = fig_3d
        
        # Parallel coordinates
        fig_parallel = self.plot_parallel_coordinates(
            df, title="All Objectives Comparison",
            save_path=f"{output_dir}/parallel_coordinates.html"
        )
        plots["parallel"] = fig_parallel
        
        # Parameter distributions
        fig_params = self.plot_parameter_distributions(
            df, save_path=f"{output_dir}/parameter_distributions.html"
        )
        plots["parameters"] = fig_params
        
        # Generate summary statistics
        pareto_df = self.identify_pareto_frontier(df, self.kpi_names)
        
        summary = {
            "total_solutions": len(df),
            "pareto_solutions": len(pareto_df),
            "pareto_percentage": len(pareto_df) / len(df) * 100,
            "kpi_ranges": {},
            "pareto_kpi_ranges": {}
        }
        
        for kpi in self.kpi_names:
            summary["kpi_ranges"][kpi] = {
                "min": df[kpi].min(),
                "max": df[kpi].max(),
                "mean": df[kpi].mean(),
                "std": df[kpi].std()
            }
            
            if len(pareto_df) > 0:
                summary["pareto_kpi_ranges"][kpi] = {
                    "min": pareto_df[kpi].min(),
                    "max": pareto_df[kpi].max(),
                    "mean": pareto_df[kpi].mean(),
                    "std": pareto_df[kpi].std()
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
