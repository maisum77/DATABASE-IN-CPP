# ============================================================================
# MODULE: visualization.py
# PURPOSE: Create visualizations for database data
# ============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional
import os
import warnings
warnings.filterwarnings('ignore')

# Set style for better looking charts
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")


# ============================================================================
# CLASS: Visualizer
# PURPOSE: Creates various visualizations for database data
# ============================================================================
class Visualizer:
    """
    This class creates visualizations for database data including:
    - Distribution charts (histograms, box plots)
    - Correlation heatmaps
    - Bar charts for categorical data
    - Scatter plots for relationships
    - Pie charts for proportions
    """

    def __init__(self, output_dir: str = "visualizations"):
        """
        Initialize the visualizer.
        
        Parameters:
            output_dir (str): Directory to save visualizations
        """
        self.output_dir = output_dir
        self._create_output_directory()

    def _create_output_directory(self) -> None:
        """Create the output directory if it doesn't exist."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"[OK] Created output directory: {self.output_dir}")

    def _save_figure(self, filename: str) -> str:
        """Save the current figure and return the path."""
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        return filepath

    def create_distribution_charts(self, df: pd.DataFrame, table_name: str) -> List[str]:
        """
        Create distribution charts for numeric columns.
        
        Parameters:
            df (pd.DataFrame): DataFrame to visualize
            table_name (str): Name of the table
            
        Returns:
            List[str]: List of saved file paths
        """
        saved_files = []
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            print(f"[Warning] No numeric columns in {table_name}")
            return saved_files

        # Create histograms for each numeric column
        for col in numeric_cols:
            try:
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # Filter out non-numeric values
                numeric_data = pd.to_numeric(df[col], errors='coerce').dropna()
                
                if len(numeric_data) == 0:
                    continue
                
                # Create histogram with KDE
                ax.hist(numeric_data, bins=20, edgecolor='black', alpha=0.7)
                ax.set_xlabel(col, fontsize=12)
                ax.set_ylabel('Frequency', fontsize=12)
                ax.set_title(f'Distribution of {col} in {table_name}', fontsize=14)
                
                # Add statistics
                stats_text = f'Mean: {numeric_data.mean():.2f}\nMedian: {numeric_data.median():.2f}\nStd: {numeric_data.std():.2f}'
                ax.text(0.95, 0.95, stats_text, transform=ax.transAxes, 
                       verticalalignment='top', horizontalalignment='right',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
                
                filename = f'{table_name}_{col}_histogram.png'
                saved_files.append(self._save_figure(filename))
                
            except Exception as e:
                print(f"[Warning] Could not create histogram for {col}: {e}")

        return saved_files

    def create_box_plots(self, df: pd.DataFrame, table_name: str) -> List[str]:
        """
        Create box plots for numeric columns.
        
        Parameters:
            df (pd.DataFrame): DataFrame to visualize
            table_name (str): Name of the table
            
        Returns:
            List[str]: List of saved file paths
        """
        saved_files = []
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return saved_files

        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Create box plot
            df_numeric = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
            df_numeric.boxplot(ax=ax)
            
            ax.set_title(f'Box Plot Analysis - {table_name}', fontsize=14)
            ax.set_xlabel('Columns', fontsize=12)
            ax.set_ylabel('Values', fontsize=12)
            
            filename = f'{table_name}_boxplot.png'
            saved_files.append(self._save_figure(filename))
            
        except Exception as e:
            print(f"[Warning] Could not create box plot: {e}")

        return saved_files

    def create_correlation_heatmap(self, df: pd.DataFrame, table_name: str) -> Optional[str]:
        """
        Create a correlation heatmap for numeric columns.
        
        Parameters:
            df (pd.DataFrame): DataFrame to visualize
            table_name (str): Name of the table
            
        Returns:
            Optional[str]: Saved file path or None
        """
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty or len(numeric_df.columns) < 2:
            print(f"[Warning] Not enough numeric columns for correlation heatmap")
            return None

        try:
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Calculate correlation matrix
            corr_matrix = numeric_df.corr()
            
            # Create heatmap
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                       fmt='.2f', linewidths=0.5, ax=ax)
            
            ax.set_title(f'Correlation Heatmap - {table_name}', fontsize=14)
            
            filename = f'{table_name}_correlation_heatmap.png'
            return self._save_figure(filename)
            
        except Exception as e:
            print(f"[Warning] Could not create correlation heatmap: {e}")
            return None

    def create_bar_charts(self, df: pd.DataFrame, table_name: str, max_categories: int = 10) -> List[str]:
        """
        Create bar charts for categorical columns.
        
        Parameters:
            df (pd.DataFrame): DataFrame to visualize
            table_name (str): Name of the table
            max_categories (int): Maximum number of categories to show
            
        Returns:
            List[str]: List of saved file paths
        """
        saved_files = []
        
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        for col in categorical_cols:
            try:
                value_counts = df[col].value_counts().head(max_categories)
                
                if len(value_counts) == 0:
                    continue
                
                fig, ax = plt.subplots(figsize=(12, 6))
                
                value_counts.plot(kind='bar', ax=ax, color='steelblue', edgecolor='black')
                
                ax.set_xlabel(col, fontsize=12)
                ax.set_ylabel('Count', fontsize=12)
                ax.set_title(f'{col} Distribution in {table_name}', fontsize=14)
                
                # Add value labels on bars
                for i, v in enumerate(value_counts):
                    ax.text(i, v + 0.1, str(v), ha='center', fontsize=10)
                
                plt.xticks(rotation=45, ha='right')
                
                filename = f'{table_name}_{col}_barchart.png'
                saved_files.append(self._save_figure(filename))
                
            except Exception as e:
                print(f"[Warning] Could not create bar chart for {col}: {e}")

        return saved_files

    def create_scatter_plot(self, df: pd.DataFrame, table_name: str, 
                           x_col: str, y_col: str, 
                           color_col: Optional[str] = None) -> Optional[str]:
        """
        Create a scatter plot for two numeric columns.
        
        Parameters:
            df (pd.DataFrame): DataFrame to visualize
            table_name (str): Name of the table
            x_col (str): Column for x-axis
            y_col (str): Column for y-axis
            color_col (str): Column for color coding (optional)
            
        Returns:
            Optional[str]: Saved file path or None
        """
        try:
            # Convert to numeric
            x_data = pd.to_numeric(df[x_col], errors='coerce').dropna()
            y_data = pd.to_numeric(df[y_col], errors='coerce').dropna()
            
            # Find common index
            valid_idx = x_data.index.intersection(y_data.index)
            
            if len(valid_idx) == 0:
                return None
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if color_col and color_col in df.columns:
                color_data = df.loc[valid_idx, color_col]
                scatter = ax.scatter(x_data.loc[valid_idx], y_data.loc[valid_idx], 
                                   c=color_data, cmap='viridis', alpha=0.7, edgecolor='black')
                plt.colorbar(scatter, ax=ax, label=color_col)
            else:
                ax.scatter(x_data.loc[valid_idx], y_data.loc[valid_idx], 
                          alpha=0.7, edgecolor='black')
            
            ax.set_xlabel(x_col, fontsize=12)
            ax.set_ylabel(y_col, fontsize=12)
            ax.set_title(f'{x_col} vs {y_col} in {table_name}', fontsize=14)
            
            # Add correlation coefficient
            corr = x_data.loc[valid_idx].corr(y_data.loc[valid_idx])
            ax.text(0.05, 0.95, f'Correlation: {corr:.3f}', 
                   transform=ax.transAxes, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            filename = f'{table_name}_{x_col}_vs_{y_col}_scatter.png'
            return self._save_figure(filename)
            
        except Exception as e:
            print(f"[Warning] Could not create scatter plot: {e}")
            return None

    def create_pie_chart(self, df: pd.DataFrame, table_name: str, 
                        category_col: str, max_slices: int = 8) -> Optional[str]:
        """
        Create a pie chart for categorical data.
        
        Parameters:
            df (pd.DataFrame): DataFrame to visualize
            table_name (str): Name of the table
            category_col (str): Column to group by
            max_slices (int): Maximum number of slices
            
        Returns:
            Optional[str]: Saved file path or None
        """
        try:
            value_counts = df[category_col].value_counts()
            
            if len(value_counts) == 0:
                return None
            
            # Group small values into "Other"
            if len(value_counts) > max_slices:
                other_sum = value_counts[max_slices:].sum()
                value_counts = value_counts[:max_slices]
                value_counts['Other'] = other_sum
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            colors = plt.cm.Set3(np.linspace(0, 1, len(value_counts)))
            
            wedges, texts, autotexts = ax.pie(
                value_counts, 
                labels=value_counts.index,
                autopct='%1.1f%%',
                colors=colors,
                explode=[0.02] * len(value_counts)
            )
            
            ax.set_title(f'{category_col} Distribution in {table_name}', fontsize=14)
            
            filename = f'{table_name}_{category_col}_pie.png'
            return self._save_figure(filename)
            
        except Exception as e:
            print(f"[Warning] Could not create pie chart: {e}")
            return None

    def create_summary_dashboard(self, df: pd.DataFrame, table_name: str) -> Optional[str]:
        """
        Create a summary dashboard with multiple visualizations.
        
        Parameters:
            df (pd.DataFrame): DataFrame to visualize
            table_name (str): Name of the table
            
        Returns:
            Optional[str]: Saved file path or None
        """
        try:
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            
            # 1. Data info (text box)
            ax1 = axes[0, 0]
            ax1.axis('off')
            info_text = f"Table: {table_name}\n\n"
            info_text += f"Total Rows: {len(df)}\n"
            info_text += f"Total Columns: {len(df.columns)}\n"
            info_text += f"Columns: {', '.join(df.columns[:8])}"
            if len(df.columns) > 8:
                info_text += f"\n... and {len(df.columns) - 8} more"
            ax1.text(0.1, 0.9, info_text, transform=ax1.transAxes, fontsize=12,
                    verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
            
            # 2. Numeric columns summary
            ax2 = axes[0, 1]
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                summary_data = []
                for col in numeric_cols[:5]:  # Top 5 numeric columns
                    numeric_data = pd.to_numeric(df[col], errors='coerce').dropna()
                    if len(numeric_data) > 0:
                        summary_data.append({
                            'Column': col,
                            'Mean': numeric_data.mean(),
                            'Min': numeric_data.min(),
                            'Max': numeric_data.max()
                        })
                if summary_data:
                    summary_df = pd.DataFrame(summary_data)
                    ax2.axis('off')
                    table = ax2.table(
                        cellText=summary_df.round(2).values,
                        colLabels=summary_df.columns,
                        cellLoc='center',
                        loc='center',
                        bbox=[0.1, 0.3, 0.8, 0.5]
                    )
                    table.auto_set_font_size(False)
                    table.set_fontsize(10)
                    ax2.set_title('Numeric Column Summary', fontsize=12, pad=20)
            
            # 3. Missing values chart
            ax3 = axes[1, 0]
            missing = df.isnull().sum()
            missing = missing[missing > 0]
            if len(missing) > 0:
                missing.plot(kind='bar', ax=ax3, color='coral', edgecolor='black')
                ax3.set_title('Missing Values by Column', fontsize=12)
                ax3.set_xlabel('Column')
                ax3.set_ylabel('Missing Count')
                plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
            else:
                ax3.text(0.5, 0.5, 'No missing values!', transform=ax3.transAxes,
                        ha='center', va='center', fontsize=14)
                ax3.set_title('Missing Values', fontsize=12)
            
            # 4. Data types distribution
            ax4 = axes[1, 1]
            dtype_counts = df.dtypes.value_counts()
            dtype_counts.plot(kind='pie', ax=ax4, autopct='%1.1f%%',
                             startangle=90)
            ax4.set_title('Data Types Distribution', fontsize=12)
            ax4.set_ylabel('')
            
            fig.suptitle(f'Data Summary Dashboard - {table_name}', fontsize=16, y=1.02)
            
            filename = f'{table_name}_dashboard.png'
            return self._save_figure(filename)
            
        except Exception as e:
            print(f"[Warning] Could not create dashboard: {e}")
            return None

    def visualize_all_tables(self, data: Dict[str, pd.DataFrame]) -> Dict[str, List[str]]:
        """
        Create visualizations for all tables in the database.
        
        Parameters:
            data (Dict[str, pd.DataFrame]): Dictionary of tables
            
        Returns:
            Dict[str, List[str]]: Dictionary mapping table names to saved files
        """
        all_files = {}
        
        for table_name, df in data.items():
            print(f"\nCreating visualizations for '{table_name}'...")
            table_files = []
            
            # Create various visualizations
            table_files.extend(self.create_distribution_charts(df, table_name))
            table_files.extend(self.create_bar_charts(df, table_name))
            
            # Create correlation heatmap
            heatmap_file = self.create_correlation_heatmap(df, table_name)
            if heatmap_file:
                table_files.append(heatmap_file)
            
            # Create dashboard
            dashboard_file = self.create_summary_dashboard(df, table_name)
            if dashboard_file:
                table_files.append(dashboard_file)
            
            all_files[table_name] = table_files
            print(f"  Created {len(table_files)} visualization(s)")
        
        return all_files


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_comparison_chart(data: Dict[str, pd.DataFrame], output_dir: str = "visualizations") -> Optional[str]:
    """
    Create a chart comparing all tables.
    
    Parameters:
        data (Dict[str, pd.DataFrame]): Dictionary of tables
        output_dir (str): Output directory
        
    Returns:
        Optional[str]: Saved file path or None
    """
    visualizer = Visualizer(output_dir)
    
    try:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Table sizes comparison
        ax1 = axes[0]
        table_sizes = {name: len(df) for name, df in data.items()}
        names = list(table_sizes.keys())
        sizes = list(table_sizes.values())
        
        bars = ax1.bar(names, sizes, color=['steelblue', 'coral', 'green', 'purple'][:len(names)])
        ax1.set_xlabel('Table Name')
        ax1.set_ylabel('Number of Rows')
        ax1.set_title('Table Size Comparison')
        
        # Add value labels on bars
        for bar, size in zip(bars, sizes):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    str(size), ha='center', va='bottom')
        
        # Column count comparison
        ax2 = axes[1]
        col_counts = {name: len(df.columns) for name, df in data.items()}
        names = list(col_counts.keys())
        counts = list(col_counts.values())
        
        bars = ax2.bar(names, counts, color=['steelblue', 'coral', 'green', 'purple'][:len(names)])
        ax2.set_xlabel('Table Name')
        ax2.set_ylabel('Number of Columns')
        ax2.set_title('Column Count Comparison')
        
        for bar, count in zip(bars, counts):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(count), ha='center', va='bottom')
        
        plt.tight_layout()
        
        visualizer2 = Visualizer(output_dir)
        return visualizer2._save_figure('database_comparison.png')
        
    except Exception as e:
        print(f"[Warning] Could not create comparison chart: {e}")
        return None


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    from data_fetcher import DatabaseFetcher
    
    print("Fetching data from database...")
    fetcher = DatabaseFetcher()
    data = fetcher.get_all_data()
    
    if data:
        print(f"Found {len(data)} tables. Creating visualizations...")
        
        visualizer = Visualizer("data_insights/visualizations")
        all_files = visualizer.visualize_all_tables(data)
        
        print("\nVisualization files saved:")
        for table, files in all_files.items():
            for f in files:
                print(f"  - {f}")
    else:
        print("No data found. Make sure the server is running.")
