# ============================================================================
# MODULE: data_analyzer.py
# PURPOSE: Perform machine learning analysis on database data
# ============================================================================

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from collections import Counter
import warnings
warnings.filterwarnings('ignore')


# ============================================================================
# CLASS: DataAnalyzer
# PURPOSE: Performs ML and statistical analysis on database data
# ============================================================================
class DataAnalyzer:
    """
    This class performs various analyses on database data including:
    - Descriptive statistics
    - Correlation analysis
    - Outlier detection
    - Data quality assessment
    - Pattern recognition
    """

    def __init__(self, data: Dict[str, pd.DataFrame]):
        """
        Initialize the analyzer with data.
        
        Parameters:
            data (Dict[str, pd.DataFrame]): Dictionary of table names to DataFrames
        """
        self.data = data
        self.analysis_results = {}

    def analyze_all(self) -> Dict[str, Any]:
        """
        Perform all analyses on all tables.
        
        Returns:
            Dict: Combined analysis results
        """
        self.analysis_results = {}

        for table_name, df in self.data.items():
            self.analysis_results[table_name] = self.analyze_table(table_name)

        return self.analysis_results

    def analyze_table(self, table_name: str) -> Dict[str, Any]:
        """
        Perform comprehensive analysis on a single table.
        
        Parameters:
            table_name (str): Name of the table to analyze
            
        Returns:
            Dict: Analysis results for the table
        """
        if table_name not in self.data:
            return {"error": f"Table '{table_name}' not found"}

        df = self.data[table_name]
        results = {}

        # Basic info
        results["basic_info"] = self._get_basic_info(df)

        # Statistics
        results["statistics"] = self._get_statistics(df)

        # Data types
        results["data_types"] = self._analyze_data_types(df)

        # Missing values
        results["missing_values"] = self._analyze_missing_values(df)

        # Correlation (for numeric columns)
        results["correlations"] = self._analyze_correlations(df)

        # Outliers
        results["outliers"] = self._detect_outliers(df)

        # Distribution analysis
        results["distributions"] = self._analyze_distributions(df)

        # Categorical analysis
        results["categorical"] = self._analyze_categorical(df)

        # Quality score
        results["quality_score"] = self._calculate_quality_score(df)

        return results

    def _get_basic_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get basic information about the DataFrame."""
        return {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "memory_usage": df.memory_usage(deep=True).sum()
        }

    def _get_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get descriptive statistics for numeric columns."""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return {"message": "No numeric columns found"}

        stats = numeric_df.describe().to_dict()
        return stats

    def _analyze_data_types(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data types in the DataFrame."""
        type_counts = df.dtypes.value_counts().to_dict()
        
        type_mapping = {
            'object': 'text',
            'int64': 'integer',
            'float64': 'decimal',
            'bool': 'boolean',
            'datetime64[ns]': 'date'
        }
        
        analyzed = {
            "type_counts": {type_mapping.get(str(k), str(k)): v for k, v in type_counts.items()},
            "column_types": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        
        return analyzed

    def _analyze_missing_values(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze missing values in the DataFrame."""
        missing = df.isnull().sum()
        missing_pct = (missing / len(df) * 100).round(2)
        
        missing_info = {}
        for col in df.columns:
            if missing[col] > 0:
                missing_info[col] = {
                    "count": int(missing[col]),
                    "percentage": float(missing_pct[col])
                }
        
        return {
            "total_missing_columns": len(missing_info),
            "missing_by_column": missing_info,
            "completeness_rate": float((1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100)
        }

    def _analyze_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze correlations between numeric columns."""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty or len(numeric_df.columns) < 2:
            return {"message": "Not enough numeric columns for correlation analysis"}

        correlation_matrix = numeric_df.corr()
        
        # Find strong correlations
        strong_correlations = []
        cols = correlation_matrix.columns
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                corr_val = correlation_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:  # Strong correlation threshold
                    strong_correlations.append({
                        "column1": cols[i],
                        "column2": cols[j],
                        "correlation": round(corr_val, 3)
                    })
        
        return {
            "correlation_matrix": correlation_matrix.to_dict(),
            "strong_correlations": strong_correlations
        }

    def _detect_outliers(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect outliers using IQR method."""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return {"message": "No numeric columns for outlier detection"}

        outliers = {}
        
        for col in numeric_df.columns:
            Q1 = numeric_df[col].quantile(0.25)
            Q3 = numeric_df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            col_outliers = numeric_df[(numeric_df[col] < lower_bound) | (numeric_df[col] > upper_bound)]
            
            if len(col_outliers) > 0:
                outliers[col] = {
                    "count": len(col_outliers),
                    "percentage": round(len(col_outliers) / len(numeric_df) * 100, 2),
                    "bounds": {
                        "lower": round(lower_bound, 2),
                        "upper": round(upper_bound, 2)
                    }
                }
        
        return {
            "columns_with_outliers": len(outliers),
            "outlier_details": outliers
        }

    def _analyze_distributions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze distributions of numeric columns."""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return {"message": "No numeric columns for distribution analysis"}

        distributions = {}
        
        for col in numeric_df.columns:
            series = numeric_df[col].dropna()
            distributions[col] = {
                "mean": round(series.mean(), 2),
                "median": round(series.median(), 2),
                "std": round(series.std(), 2),
                "min": round(series.min(), 2),
                "max": round(series.max(), 2),
                "skewness": round(series.skew(), 3),
                "kurtosis": round(series.kurtosis(), 3),
                "unique_values": int(series.nunique())
            }
        
        return distributions

    def _analyze_categorical(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze categorical columns."""
        categorical_df = df.select_dtypes(include=['object'])
        
        if categorical_df.empty:
            return {"message": "No categorical columns found"}

        categorical_info = {}
        
        for col in categorical_df.columns:
            value_counts = df[col].value_counts()
            categorical_info[col] = {
                "unique_values": int(df[col].nunique()),
                "most_common": value_counts.head(5).to_dict(),
                "value_distribution": value_counts.to_dict()
            }
        
        return categorical_info

    def _calculate_quality_score(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate overall data quality score."""
        score = 100.0
        
        # Deduct for missing values
        missing_pct = df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100
        score -= missing_pct * 0.5
        
        # Deduct for duplicates
        duplicate_pct = df.duplicated().sum() / len(df) * 100
        score -= duplicate_pct * 0.3
        
        # Ensure score is between 0 and 100
        score = max(0, min(100, score))
        
        return {
            "overall_score": round(score, 1),
            "missing_penalty": round(missing_pct * 0.5, 2),
            "duplicate_penalty": round(duplicate_pct * 0.3, 2)
        }

    def get_summary_report(self) -> str:
        """
        Generate a text summary of all analysis results.
        
        Returns:
            str: Formatted summary report
        """
        if not self.analysis_results:
            return "No analysis performed yet."

        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("   DATA ANALYSIS SUMMARY REPORT")
        report_lines.append("=" * 60)

        for table_name, results in self.analysis_results.items():
            report_lines.append(f"\n{table_name}")
            report_lines.append("-" * 40)
            
            # Basic info
            basic = results.get("basic_info", {})
            report_lines.append(f"Rows: {basic.get('rows', 'N/A')}")
            report_lines.append(f"Columns: {basic.get('columns', 'N/A')}")
            
            # Quality score
            quality = results.get("quality_score", {})
            report_lines.append(f"Quality Score: {quality.get('overall_score', 'N/A')}/100")
            
            # Statistics summary
            stats = results.get("statistics", {})
            if "mean" in stats:
                report_lines.append("\nNumeric Statistics:")
                for col, col_stats in stats.items():
                    report_lines.append(f"  {col}:")
                    report_lines.append(f"    Mean: {col_stats.get('mean', 'N/A')}")
                    report_lines.append(f"    Std: {col_stats.get('std', 'N/A')}")
            
            # Correlations
            corr = results.get("correlations", {})
            strong = corr.get("strong_correlations", [])
            if strong:
                report_lines.append("\nStrong Correlations:")
                for c in strong[:3]:  # Show top 3
                    report_lines.append(f"  {c['column1']} <-> {c['column2']}: {c['correlation']}")
            
            # Outliers
            outliers = results.get("outliers", {})
            outlier_count = outliers.get("columns_with_outliers", 0)
            if outlier_count > 0:
                report_lines.append(f"\nOutliers detected in {outlier_count} column(s)")

        report_lines.append("\n" + "=" * 60)
        
        return "\n".join(report_lines)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def compare_tables(data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Compare multiple tables to find relationships.
    
    Parameters:
        data (Dict[str, pd.DataFrame]): Dictionary of tables
        
    Returns:
        Dict: Comparison results
    """
    results = {
        "table_sizes": {},
        "column_overlap": {},
        "potential_joins": []
    }

    # Table sizes
    for name, df in data.items():
        results["table_sizes"][name] = {
            "rows": len(df),
            "columns": len(df.columns)
        }

    # Column overlap
    table_names = list(data.keys())
    for i, name1 in enumerate(table_names):
        for name2 in table_names[i + 1:]:
            cols1 = set(data[name1].columns)
            cols2 = set(data[name2].columns)
            overlap = cols1 & cols2
            
            if overlap:
                results["column_overlap"][f"{name1} <-> {name2}"] = list(overlap)
                
                # Check for potential join keys
                for col in overlap:
                    if "id" in col.lower():
                        results["potential_joins"].append({
                            "table1": name1,
                            "table2": name2,
                            "join_column": col
                        })

    return results


def find_patterns(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Find interesting patterns in the data.
    
    Parameters:
        df (pd.DataFrame): DataFrame to analyze
        
    Returns:
        Dict: Pattern information
    """
    patterns = {}
    
    # Numeric patterns
    numeric_df = df.select_dtypes(include=[np.number])
    if not numeric_df.empty:
        patterns["numeric_summary"] = numeric_df.describe().to_dict()
        
        # Check for power law or exponential patterns
        for col in numeric_df.columns:
            series = numeric_df[col].dropna()
            if len(series) > 10:
                # Simple pattern detection
                values = sorted(series.values)
                if values[-1] > values[0] * 10:  # Large range suggests power law
                    patterns[f"{col}_pattern"] = "Wide range - potential power law distribution"
    
    # Categorical patterns
    categorical_df = df.select_dtypes(include=['object'])
    if not categorical_df.empty:
        for col in categorical_df.columns:
            value_counts = df[col].value_counts()
            if value_counts.iloc[0] > len(df) * 0.5:
                patterns[f"{col}_dominance"] = f"'{value_counts.index[0]}' dominates ({value_counts.iloc[0]} occurrences)"
    
    return patterns


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Example usage
    from data_fetcher import DatabaseFetcher
    
    print("Fetching data from database...")
    fetcher = DatabaseFetcher()
    data = fetcher.get_all_data()
    
    if data:
        print(f"Found {len(data)} tables")
        
        analyzer = DataAnalyzer(data)
        results = analyzer.analyze_all()
        
        print("\n" + analyzer.get_summary_report())
    else:
        print("No data found. Make sure the server is running.")
