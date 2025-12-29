# ============================================================================
# MODULE: insights_generator.py
# PURPOSE: Generate AI-powered insights from database data
# ============================================================================

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from collections import Counter
import random


# ============================================================================
# CLASS: InsightsGenerator
# PURPOSE: Generates intelligent insights from database data
# ============================================================================
class InsightsGenerator:
    """
    This class generates intelligent insights from database data using:
    - Statistical analysis
    - Pattern recognition
    - Anomaly detection
    - Trend identification
    - Natural language generation
    """

    def __init__(self, data: Dict[str, pd.DataFrame]):
        """
        Initialize the insights generator.
        
        Parameters:
            data (Dict[str, pd.DataFrame]): Dictionary of table names to DataFrames
        """
        self.data = data
        self.insights = {}

    def generate_all_insights(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate insights for all tables.
        
        Returns:
            Dict: Dictionary mapping table names to their insights
        """
        self.insights = {}

        for table_name, df in self.data.items():
            self.insights[table_name] = self.generate_table_insights(table_name)

        return self.insights

    def generate_table_insights(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Generate comprehensive insights for a single table.
        
        Parameters:
            table_name (str): Name of the table
            
        Returns:
            List[Dict]: List of insights with type, title, description, and priority
        """
        if table_name not in self.data:
            return [{"type": "error", "title": "Table Not Found",
                    "description": f"Table '{table_name}' not found in database",
                    "priority": "high"}]

        df = self.data[table_name]
        insights = []

        # Basic insights
        insights.extend(self._generate_basic_insights(df, table_name))
        
        # Statistical insights
        insights.extend(self._generate_statistical_insights(df, table_name))
        
        # Data quality insights
        insights.extend(self._generate_quality_insights(df, table_name))
        
        # Relationship insights
        insights.extend(self._generate_relationship_insights(df, table_name))
        
        # Anomaly insights
        insights.extend(self._generate_anomaly_insights(df, table_name))
        
        # Pattern insights
        insights.extend(self._generate_pattern_insights(df, table_name))

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        insights.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 2))

        return insights

    def _generate_basic_insights(self, df: pd.DataFrame, table_name: str) -> List[Dict[str, Any]]:
        """Generate basic information insights."""
        insights = []

        # Table size insight
        insights.append({
            "type": "info",
            "title": "Dataset Overview",
            "description": f"The '{table_name}' table contains {len(df)} rows and {len(df.columns)} columns: {', '.join(df.columns)}.",
            "priority": "low"
        })

        # Column count
        if len(df.columns) > 10:
            insights.append({
                "type": "info",
                "title": "Complex Table Structure",
                "description": f"This is a complex table with {len(df.columns)} columns. Consider normalizing if not already done.",
                "priority": "low"
            })
        elif len(df.columns) < 3:
            insights.append({
                "type": "info",
                "title": "Simple Table Structure",
                "description": f"This is a simple table with only {len(df.columns)} column(s).",
                "priority": "low"
            })

        return insights

    def _generate_statistical_insights(self, df: pd.DataFrame, table_name: str) -> List[Dict[str, Any]]:
        """Generate statistical insights."""
        insights = []

        # Numeric column statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            try:
                numeric_data = pd.to_numeric(df[col], errors='coerce').dropna()
                
                if len(numeric_data) == 0:
                    continue
                
                mean_val = numeric_data.mean()
                median_val = numeric_data.median()
                std_val = numeric_data.std()
                
                # Skewness insight
                if abs(numeric_data.skew()) > 1:
                    direction = "positively" if numeric_data.skew() > 0 else "negatively"
                    insights.append({
                        "type": "statistic",
                        "title": f"Skewed Distribution in {col}",
                        "description": f"The {col} column is {direction} skewed (skewness: {numeric_data.skew():.2f}). This means most values are concentrated on one side.",
                        "priority": "medium"
                    })
                
                # High variance insight
                if std_val > mean_val * 0.5:
                    insights.append({
                        "type": "statistic",
                        "title": f"High Variability in {col}",
                        "description": f"The {col} column has high standard deviation ({std_val:.2f}) relative to the mean ({mean_val:.2f}). This indicates diverse data spread.",
                        "priority": "medium"
                    })
                
                # Range insight
                data_range = numeric_data.max() - numeric_data.min()
                if data_range > 0:
                    insights.append({
                        "type": "statistic",
                        "title": f"Value Range in {col}",
                        "description": f"The {col} values range from {numeric_data.min():.2f} to {numeric_data.max():.2f} (range: {data_range:.2f}).",
                        "priority": "low"
                    })
                    
            except Exception:
                continue

        return insights

    def _generate_quality_insights(self, df: pd.DataFrame, table_name: str) -> List[Dict[str, Any]]:
        """Generate data quality insights."""
        insights = []

        # Missing values
        missing = df.isnull().sum()
        total_cells = len(df) * len(df.columns)
        missing_cells = missing.sum()
        
        if missing_cells > 0:
            missing_pct = (missing_cells / total_cells) * 100
            
            if missing_pct > 20:
                priority = "high"
            elif missing_pct > 5:
                priority = "medium"
            else:
                priority = "low"
            
            insights.append({
                "type": "quality",
                "title": "Missing Data Detected",
                "description": f"Total missing values: {missing_cells} ({missing_pct:.1f}% of data). "
                              f"Columns with missing data: {', '.join(missing[missing > 0].index.tolist())}.",
                "priority": priority
            })

        # Duplicate rows
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            dup_pct = (duplicates / len(df)) * 100
            
            if dup_pct > 10:
                priority = "high"
            elif dup_pct > 1:
                priority = "medium"
            else:
                priority = "low"
            
            insights.append({
                "type": "quality",
                "title": "Duplicate Rows Found",
                "description": f"Found {duplicates} duplicate rows ({dup_pct:.1f}% of data). Consider removing duplicates for cleaner analysis.",
                "priority": priority
            })

        # Completeness by column
        for col in df.columns:
            null_pct = (df[col].isnull().sum() / len(df)) * 100
            if null_pct > 50:
                insights.append({
                    "type": "quality",
                    "title": f"High Missing Rate in {col}",
                    "description": f"Column '{col}' is {null_pct:.1f}% empty. Consider removing or imputing this column.",
                    "priority": "high"
                })

        return insights

    def _generate_relationship_insights(self, df: pd.DataFrame, table_name: str) -> List[Dict[str, Any]]:
        """Generate relationship insights."""
        insights = []

        # Correlation insights
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) >= 2:
            corr_matrix = df[numeric_cols].corr()
            
            strong_positive = []
            strong_negative = []
            
            for i in range(len(numeric_cols)):
                for j in range(i + 1, len(numeric_cols)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:
                        if corr_val > 0:
                            strong_positive.append((numeric_cols[i], numeric_cols[j], corr_val))
                        else:
                            strong_negative.append((numeric_cols[i], numeric_cols[j], corr_val))
            
            if strong_positive:
                insights.append({
                    "type": "relationship",
                    "title": "Strong Positive Correlations",
                    "description": f"Found {len(strong_positive)} strong positive correlation(s). "
                                  f"Example: {strong_positive[0][0]} and {strong_positive[0][1]} have correlation of {strong_positive[0][2]:.2f}. "
                                  f"These columns tend to increase together.",
                    "priority": "medium"
                })
            
            if strong_negative:
                insights.append({
                    "type": "relationship",
                    "title": "Strong Negative Correlations",
                    "description": f"Found {len(strong_negative)} negative correlation(s). "
                                  f"Example: {strong_negative[0][0]} and {strong_negative[0][1]} have correlation of {strong_negative[0][2]:.2f}. "
                                  f"These columns move in opposite directions.",
                    "priority": "medium"
                })

        return insights

    def _generate_anomaly_insights(self, df: pd.DataFrame, table_name: str) -> List[Dict[str, Any]]:
        """Generate anomaly detection insights."""
        insights = []

        # Outlier detection using IQR
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            try:
                numeric_data = pd.to_numeric(df[col], errors='coerce').dropna()
                
                if len(numeric_data) < 10:
                    continue
                
                Q1 = numeric_data.quantile(0.25)
                Q3 = numeric_data.quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = numeric_data[(numeric_data < lower_bound) | (numeric_data > upper_bound)]
                
                if len(outliers) > 0:
                    outlier_pct = (len(outliers) / len(numeric_data)) * 100
                    
                    if outlier_pct > 5:
                        priority = "high"
                    elif outlier_pct > 1:
                        priority = "medium"
                    else:
                        priority = "low"
                    
                    insights.append({
                        "type": "anomaly",
                        "title": f"Outliers Detected in {col}",
                        "description": f"Found {len(outliers)} outlier(s) ({outlier_pct:.1f}%) in {col}. "
                                      f"Values outside range [{lower_bound:.2f}, {upper_bound:.2f}]. "
                                      f"These may represent errors or special cases.",
                        "priority": priority
                    })
                    
            except Exception:
                continue

        return insights

    def _generate_pattern_insights(self, df: pd.DataFrame, table_name: str) -> List[Dict[str, Any]]:
        """Generate pattern recognition insights."""
        insights = []

        # Categorical patterns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        for col in categorical_cols:
            try:
                value_counts = df[col].value_counts()
                
                # Dominant category
                if len(value_counts) > 0:
                    dominant_pct = (value_counts.iloc[0] / len(df)) * 100
                    
                    if dominant_pct > 80:
                        insights.append({
                            "type": "pattern",
                            "title": f"Dominant Category in {col}",
                            "description": f"'{value_counts.index[0]}' dominates {col} with {dominant_pct:.1f}% of all values. "
                                          f"This could indicate a default value or common category.",
                            "priority": "low"
                        })
                    
                    # Unique values
                    unique_count = df[col].nunique()
                    if unique_count == len(df):
                        insights.append({
                            "type": "pattern",
                            "title": f"Unique Values in {col}",
                            "description": f"Column {col} has {unique_count} unique values (one per row). "
                                          f"This might be an identifier or unique key column.",
                            "priority": "low"
                        })
                    
                    # Rare categories
                    rare_count = (value_counts < len(df) * 0.05).sum()
                    if rare_count > 1:
                        insights.append({
                            "type": "pattern",
                            "title": f"Rare Categories in {col}",
                            "description": f"Found {rare_count} categories with less than 5% occurrence each. "
                                          f"These might need special handling in analysis.",
                            "priority": "low"
                        })
                        
            except Exception:
                continue

        return insights

    def generate_summary_report(self) -> str:
        """
        Generate a comprehensive text summary of all insights.
        
        Returns:
            str: Formatted insights report
        """
        if not self.insights:
            return "No insights generated yet."

        report_lines = []
        report_lines.append("=" * 70)
        report_lines.append("            DATABASE INSIGHTS REPORT")
        report_lines.append("=" * 70)

        for table_name, table_insights in self.insights.items():
            report_lines.append(f"\n{table_name}")
            report_lines.append("-" * 50)

            if not table_insights:
                report_lines.append("  No insights available.")
                continue

            # Group by priority
            by_priority = {"high": [], "medium": [], "low": []}
            for insight in table_insights:
                priority = insight.get("priority", "low")
                by_priority[priority].append(insight)

            # Report by priority
            for priority in ["high", "medium", "low"]:
                if by_priority[priority]:
                    report_lines.append(f"\n  [{priority.upper()} PRIORITY]")
                    for insight in by_priority[priority]:
                        report_lines.append(f"\n  • {insight['title']}")
                        report_lines.append(f"    {insight['description']}")

        report_lines.append("\n" + "=" * 70)
        report_lines.append("                   END OF REPORT")
        report_lines.append("=" * 70)

        return "\n".join(report_lines)

    def export_insights_json(self, filepath: str = "insights.json") -> None:
        """
        Export insights to a JSON file.
        
        Parameters:
            filepath (str): Output file path
        """
        import json
        
        with open(filepath, 'w') as f:
            json.dump(self.insights, f, indent=2)
        
        print(f"[OK] Insights exported to {filepath}")


# ============================================================================
# CLASS: NaturalLanguageInsights
# PURPOSE: Generate natural language descriptions of data
# ============================================================================
class NaturalLanguageInsights:
    """
    Generates natural language descriptions and summaries of data.
    """

    @staticmethod
    def describe_column(df: pd.DataFrame, col_name: str) -> str:
        """
        Generate a natural language description of a column.
        
        Parameters:
            df (pd.DataFrame): DataFrame containing the column
            col_name (str): Name of the column
            
        Returns:
            str: Natural language description
        """
        if col_name not in df.columns:
            return f"Column '{col_name}' not found."

        series = df[col_name]
        description = []

        # Basic info
        description.append(f"The '{col_name}' column contains {len(series)} values.")

        # Data type
        dtype = series.dtype
        if pd.api.types.is_numeric_dtype(series):
            numeric_data = pd.to_numeric(series, errors='coerce').dropna()
            if len(numeric_data) > 0:
                description.append(f"It is a numeric column with values ranging from {numeric_data.min()} to {numeric_data.max()}.")
                description.append(f"The average value is {numeric_data.mean():.2f} with a standard deviation of {numeric_data.std():.2f}.")
        else:
            unique_count = series.nunique()
            description.append(f"It is a text column with {unique_count} unique values.")

        # Missing values
        missing = series.isnull().sum()
        if missing > 0:
            pct = (missing / len(series)) * 100
            description.append(f"Note: {missing} values ({pct:.1f}%) are missing or null.")

        return " ".join(description)

    @staticmethod
    def compare_columns(df: pd.DataFrame, col1: str, col2: str) -> str:
        """
        Generate a natural language comparison of two columns.
        
        Parameters:
            df (pd.DataFrame): DataFrame containing the columns
            col_name (str): Name of the first column
            col_name (str): Name of the second column
            
        Returns:
            str: Natural language comparison
        """
        if col1 not in df.columns or col2 not in df.columns:
            return "One or both columns not found."

        # Calculate correlation if both are numeric
        if pd.api.types.is_numeric_dtype(df[col1]) and pd.api.types.is_numeric_dtype(df[col2]):
            corr = df[col1].corr(df[col2])
            
            if abs(corr) > 0.7:
                strength = "strong"
                direction = "positive" if corr > 0 else "inverse"
                description = f"There is a {strength} {direction} relationship between '{col1}' and '{col2}' (correlation: {corr:.2f}). "
                description += "These columns tend to change together." if corr > 0 else "When one increases, the other tends to decrease."
                return description
            elif abs(corr) > 0.3:
                return f"There is a moderate correlation between '{col1}' and '{col2}' (correlation: {corr:.2f})."
            else:
                return f"There is little to no linear relationship between '{col1}' and '{col2}' (correlation: {corr:.2f})."

        return "Cannot compare these columns as they are not both numeric."


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_database_insights(data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Convenience function to generate all insights for a database.
    
    Parameters:
        data (Dict[str, pd.DataFrame]): Dictionary of tables
        
    Returns:
        Dict: Insights and visualizations information
    """
    generator = InsightsGenerator(data)
    insights = generator.generate_all_insights()
    report = generator.generate_summary_report()
    
    return {
        "insights": insights,
        "report": report
    }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    from data_fetcher import DatabaseFetcher
    
    print("Fetching data from database...")
    fetcher = DatabaseFetcher()
    data = fetcher.get_all_data()
    
    if data:
        print(f"Found {len(data)} tables. Generating insights...")
        
        generator = InsightsGenerator(data)
        generator.generate_all_insights()
        
        print("\n" + generator.generate_summary_report())
        
        # Export to JSON
        generator.export_insights_json("data_insights/insights.json")
    else:
        print("No data found. Make sure the server is running.")
