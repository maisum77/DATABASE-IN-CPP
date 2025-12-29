#!/usr/bin/env python3
# ============================================================================
# FILE: data_insights/main.py
# PURPOSE: Main orchestration script for database insights and visualization
# ============================================================================
"""
This script orchestrates the entire data insights pipeline:
1. Connects to the C++ database server
2. Fetches all data from the database
3. Performs comprehensive analysis using ML techniques
4. Generates visualizations
5. Produces AI-powered insights
6. Outputs a complete insights report

Usage:
    python data_insights/main.py

Requirements:
    - C++ database server running on localhost:8080
    - Python packages: requests, pandas, numpy, matplotlib, seaborn
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_fetcher import DatabaseFetcher
from data_analyzer import DataAnalyzer
from visualization import Visualizer
from insights_generator import InsightsGenerator


# ============================================================================
# CLASS: DataInsightsPipeline
# PURPOSE: Orchestrates the complete data insights workflow
# ============================================================================
class DataInsightsPipeline:
    """
    Main pipeline class that coordinates all data insights operations.
    
    This class brings together:
    - Data fetching from the C++ server
    - Statistical and ML analysis
    - Visualization generation
    - AI-powered insights generation
    - Report compilation and export
    """

    def __init__(self, server_url: str = "http://localhost:8080", 
                 output_dir: str = "data_insights/output"):
        """
        Initialize the data insights pipeline.
        
        Parameters:
            server_url (str): URL of the database server
            output_dir (str): Directory for output files
        """
        self.server_url = server_url
        self.output_dir = output_dir
        self.fetcher = None
        self.analyzer = None
        self.visualizer = None
        self.insights_generator = None
        self.data = {}
        self.analysis_results = {}
        self.visualization_files = {}
        self.insights = {}
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def run(self) -> Dict[str, Any]:
        """
        Execute the complete data insights pipeline.
        
        Returns:
            Dict: Pipeline results including data, analysis, and insights
        """
        print("\n" + "=" * 70)
        print("           DATA INSIGHTS AND VISUALIZATION PIPELINE")
        print("=" * 70)
        print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Server URL: {self.server_url}")
        
        try:
            # Step 1: Connect and fetch data
            print("\n[Step 1/5] Connecting to database and fetching data...")
            if not self._fetch_data():
                return {"success": False, "error": "Failed to fetch data"}

            # Step 2: Perform analysis
            print("\n[Step 2/5] Performing data analysis...")
            self._perform_analysis()

            # Step 3: Generate visualizations
            print("\n[Step 3/5] Generating visualizations...")
            self._generate_visualizations()

            # Step 4: Generate insights
            print("\n[Step 4/5] Generating AI-powered insights...")
            self._generate_insights()

            # Step 5: Compile and export report
            print("\n[Step 5/5] Compiling and exporting report...")
            results = self._compile_report()
            
            print("\n" + "=" * 70)
            print("           PIPELINE COMPLETED SUCCESSFULLY")
            print("=" * 70)
            print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Output directory: {self.output_dir}")
            
            return results

        except Exception as error:
            print(f"\n[ERROR] Pipeline failed: {error}")
            return {"success": False, "error": str(error)}

    def _fetch_data(self) -> bool:
        """
        Fetch data from the database server.
        
        Returns:
            bool: True if successful, False otherwise
        """
        self.fetcher = DatabaseFetcher(self.server_url)
        
        if not self.fetcher.is_connected:
            print("  [ERROR] Cannot connect to database server")
            return False

        self.data = self.fetcher.get_all_data()
        
        if not self.data:
            print("  [ERROR] No data found in database")
            return False

        print(f"  [OK] Fetched {len(self.data)} table(s):")
        for table_name, df in self.data.items():
            print(f"       - {table_name}: {len(df)} rows, {len(df.columns)} columns")

        return True

    def _perform_analysis(self) -> None:
        """
        Perform statistical and ML analysis on the data.
        """
        self.analyzer = DataAnalyzer(self.data)
        self.analysis_results = self.analyzer.analyze_all()

        print(f"  [OK] Analysis complete for {len(self.analysis_results)} table(s)")

    def _generate_visualizations(self) -> None:
        """
        Generate visualizations for the data.
        """
        self.visualizer = Visualizer(os.path.join(self.output_dir, "visualizations"))
        self.visualization_files = self.visualizer.visualize_all_tables(self.data)

        total_files = sum(len(files) for files in self.visualization_files.values())
        print(f"  [OK] Generated {total_files} visualization(s)")

    def _generate_insights(self) -> None:
        """
        Generate AI-powered insights from the data.
        """
        self.insights_generator = InsightsGenerator(self.data)
        self.insights = self.insights_generator.generate_all_insights()

        total_insights = sum(len(table_insights) for table_insights in self.insights.values())
        print(f"  [OK] Generated {total_insights} insight(s)")

    def _compile_report(self) -> Dict[str, Any]:
        """
        Compile and export the complete insights report.
        
        Returns:
            Dict: Compilation results
        """
        # Create output directory structure
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "visualizations"), exist_ok=True)

        # Generate text report
        report_lines = []
        report_lines.append("=" * 70)
        report_lines.append("              DATABASE INSIGHTS REPORT")
        report_lines.append("=" * 70)
        report_lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Server URL: {self.server_url}")
        report_lines.append(f"Timestamp: {self.timestamp}")

        # Database overview
        report_lines.append("\n" + "-" * 70)
        report_lines.append("DATABASE OVERVIEW")
        report_lines.append("-" * 70)
        report_lines.append(f"\nTotal tables: {len(self.data)}")

        for table_name, df in self.data.items():
            report_lines.append(f"\n  Table: {table_name}")
            report_lines.append(f"    Rows: {len(df)}")
            report_lines.append(f"    Columns: {len(df.columns)}")
            report_lines.append(f"    Columns: {', '.join(df.columns)}")

        # Analysis summary
        report_lines.append("\n" + "-" * 70)
        report_lines.append("ANALYSIS SUMMARY")
        report_lines.append("-" * 70)

        for table_name, results in self.analysis_results.items():
            report_lines.append(f"\n  Table: {table_name}")

            basic_info = results.get("basic_info", {})
            report_lines.append(f"    Rows: {basic_info.get('rows', 'N/A')}")
            report_lines.append(f"    Columns: {basic_info.get('columns', 'N/A')}")

            quality = results.get("quality_score", {})
            report_lines.append(f"    Quality Score: {quality.get('overall_score', 'N/A')}/100")

            statistics = results.get("statistics", {})
            if "mean" in statistics:
                report_lines.append("\n    Numeric Statistics:")
                for col, col_stats in statistics.items():
                    if isinstance(col_stats, dict):
                        mean_val = col_stats.get('mean', 'N/A')
                        std_val = col_stats.get('std', 'N/A')
                        report_lines.append(f"      {col}: mean={mean_val}, std={std_val}")

        # AI-generated insights
        report_lines.append("\n" + "-" * 70)
        report_lines.append("AI-GENERATED INSIGHTS")
        report_lines.append("-" * 70)

        for table_name, table_insights in self.insights.items():
            report_lines.append(f"\n  Table: {table_name}")
            report_lines.append("  " + "-" * 40)

            if not table_insights:
                report_lines.append("    No insights available.")
                continue

            # Group by priority
            by_priority = {"high": [], "medium": [], "low": []}
            for insight in table_insights:
                priority = insight.get("priority", "low")
                by_priority[priority].append(insight)

            # Report by priority
            for priority in ["high", "medium", "low"]:
                if by_priority[priority]:
                    report_lines.append(f"\n    [{priority.upper()} PRIORITY]")
                    for insight in by_priority[priority]:
                        report_lines.append(f"\n      • {insight['title']}")
                        report_lines.append(f"        {insight['description']}")

        # Visualization summary
        report_lines.append("\n" + "-" * 70)
        report_lines.append("GENERATED VISUALIZATIONS")
        report_lines.append("-" * 70)

        for table_name, files in self.visualization_files.items():
            report_lines.append(f"\n  Table: {table_name}")
            for f in files:
                report_lines.append(f"    - {os.path.basename(f)}")

        # Recommendations
        report_lines.append("\n" + "-" * 70)
        report_lines.append("RECOMMENDATIONS")
        report_lines.append("-" * 70)

        recommendations = self._generate_recommendations()
        for i, rec in enumerate(recommendations, 1):
            report_lines.append(f"\n  {i}. {rec}")

        report_lines.append("\n" + "=" * 70)
        report_lines.append("                   END OF REPORT")
        report_lines.append("=" * 70)

        # Save report
        report_text = "\n".join(report_lines)
        report_path = os.path.join(self.output_dir, f"insights_report_{self.timestamp}.txt")
        with open(report_path, 'w') as f:
            f.write(report_text)

        print(f"  [OK] Report saved to: {report_path}")

        # Export insights as JSON
        insights_path = os.path.join(self.output_dir, f"insights_{self.timestamp}.json")
        with open(insights_path, 'w') as f:
            json.dump(self.insights, f, indent=2)

        print(f"  [OK] Insights JSON saved to: {insights_path}")

        # Export analysis results as JSON
        analysis_path = os.path.join(self.output_dir, f"analysis_{self.timestamp}.json")
        with open(analysis_path, 'w') as f:
            json.dump(self.analysis_results, f, indent=2)

        print(f"  [OK] Analysis JSON saved to: {analysis_path}")

        return {
            "success": True,
            "timestamp": self.timestamp,
            "tables_analyzed": len(self.data),
            "total_insights": sum(len(table_insights) for table_insights in self.insights.values()),
            "total_visualizations": sum(len(files) for files in self.visualization_files.values()),
            "report_path": report_path,
            "insights_path": insights_path,
            "analysis_path": analysis_path
        }

    def _generate_recommendations(self) -> list:
        """
        Generate actionable recommendations based on analysis results.
        
        Returns:
            List[str]: List of recommendations
        """
        recommendations = []

        # Check data quality
        for table_name, results in self.analysis_results.items():
            quality = results.get("quality_score", {})
            score = quality.get("overall_score", 100)

            if score < 70:
                recommendations.append(
                    f"Table '{table_name}' has low data quality ({score}/100). "
                    "Consider cleaning duplicate entries and handling missing values."
                )

            missing = results.get("missing_values", {})
            if missing.get("total_missing_columns", 0) > 0:
                columns_with_missing = list(missing.get("missing_by_column", {}).keys())
                recommendations.append(
                    f"Table '{table_name}' has missing values in columns: {', '.join(columns_with_missing)}. "
                    "Consider imputation strategies or data collection improvements."
                )

        # Check for outliers
        for table_name, results in self.analysis_results.items():
            outliers = results.get("outliers", {})
            outlier_cols = outliers.get("columns_with_outliers", 0)

            if outlier_cols > 0:
                recommendations.append(
                    f"Table '{table_name}' contains outliers in {outlier_cols} column(s). "
                    "Review these values for potential data entry errors or special cases."
                )

        # Check correlations
        for table_name, results in self.analysis_results.items():
            correlations = results.get("correlations", {})
            strong_correlations = correlations.get("strong_correlations", [])

            if len(strong_correlations) > 3:
                recommendations.append(
                    f"Table '{table_name}' has {len(strong_correlations)} strong correlations. "
                    "Consider investigating multicollinearity if using this data for predictive modeling."
                )

        # General recommendations
        if len(self.data) >= 2:
            recommendations.append(
                "Multiple tables detected. Consider examining relationships between tables "
                "for potential join operations and unified analysis."
            )

        if not recommendations:
            recommendations.append("Data appears to be in good condition. Continue monitoring for anomalies.")

        return recommendations

    def get_quick_summary(self) -> str:
        """
        Get a quick text summary of the current state.
        
        Returns:
            str: Quick summary
        """
        if not self.data:
            return "No data loaded. Run the pipeline first."

        summary = []
        summary.append(f"Tables: {len(self.data)}")
        summary.append(f"Total rows: {sum(len(df) for df in self.data.values())}")

        if self.insights:
            high_priority = sum(
                1 for insights in self.insights.values() 
                for i in insights if i.get("priority") == "high"
            )
            summary.append(f"High priority insights: {high_priority}")

        if self.visualization_files:
            total_viz = sum(len(files) for files in self.visualization_files.values())
            summary.append(f"Visualizations: {total_viz}")

        return " | ".join(summary)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_banner():
    """Print the welcome banner."""
    print("\n" + "=" * 70)
    print("  _____                _              _    _____           _")
    print(" |  ___| __ __ _ _ __ | |_ ___  _ __ | |_ / ____|         | |")
    print(" | |_ | '__/ _` | '_ \\| __/ _ \\| '_ \\| __| (___   ___  ___| |_")
    print(" |  _|| | | (_| | |_) | || (_) | | | | |_ \\___ \\ / _ \\/ __| __|")
    print(" |_|  |_|  \\__,_| .__/ \\__\\___/|_| |_|\\__|_____/ \\___/\\__|\\__|")
    print("                |_|")
    print("=" * 70)
    print("\n  Database Insights and Visualization System")
    print("  Powered by Machine Learning and AI")
    print("=" * 70 + "\n")


def check_dependencies() -> bool:
    """
    Check if all required dependencies are installed.
    
    Returns:
        bool: True if all dependencies are available
    """
    required_modules = [
        ("requests", "requests"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("matplotlib", "matplotlib"),
        ("seaborn", "seaborn")
    ]

    missing = []
    for package, module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(package)

    if missing:
        print("[ERROR] Missing required packages:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\nInstall with: pip install " + " ".join(missing))
        return False

    return True


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print_banner()

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Get server URL from command line or use default
    server_url = "http://localhost:8080"
    if len(sys.argv) > 1:
        server_url = sys.argv[1]

    # Create and run pipeline
    pipeline = DataInsightsPipeline(server_url=server_url)
    results = pipeline.run()

    # Print summary
    if results.get("success"):
        print("\n" + "-" * 70)
        print("EXECUTIVE SUMMARY")
        print("-" * 70)
        print(f"\n  Tables Analyzed: {results.get('tables_analyzed', 0)}")
        print(f"  Total Insights: {results.get('total_insights', 0)}")
        print(f"  Visualizations: {results.get('total_visualizations', 0)}")
        print(f"\n  Report: {results.get('report_path', 'N/A')}")
        print(f"  Insights JSON: {results.get('insights_path', 'N/A')}")
        print(f"  Analysis JSON: {results.get('analysis_path', 'N/A')}")
        print("\n  Quick Summary: " + pipeline.get_quick_summary())
    else:
        print(f"\n[ERROR] {results.get('error', 'Unknown error')}")
        sys.exit(1)
