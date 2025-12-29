# Data Insights and Visualization Module

This module provides AI-powered data analysis and visualization capabilities for your C++ database server. It fetches data from the database, performs machine learning analysis, generates insightful visualizations, and produces natural language insights about your data.

## Features

The data insights module offers comprehensive data analysis capabilities:

- **Data Fetching**: Connects to the C++ database server via REST API and retrieves all tables and schemas
- **Statistical Analysis**: Performs descriptive statistics, correlation analysis, outlier detection, and data quality assessment
- **Visualization Generation**: Creates distribution charts, correlation heatmaps, bar charts, scatter plots, pie charts, and summary dashboards
- **AI-Powered Insights**: Generates intelligent insights including anomaly detection, pattern recognition, and relationship analysis
- **Report Export**: Compiles comprehensive reports in text and JSON formats

## Architecture

The module consists of four core components that work together:

| Component | File | Description |
|-----------|------|-------------|
| Data Fetcher | `data_fetcher.py` | Handles all communication with the C++ database server via REST API |
| Data Analyzer | `data_analyzer.py` | Performs statistical analysis and machine learning operations on the data |
| Visualizer | `visualization.py` | Creates various charts and visualizations using matplotlib and seaborn |
| Insights Generator | `insights_generator.py` | Generates AI-powered natural language insights from the data |
| Main Pipeline | `main.py` | Orchestrates the entire workflow from data fetching to report generation |

## Requirements

Before using this module, ensure you have the following installed:

### Python Packages

```bash
pip install requests pandas numpy matplotlib seaborn
```

### C++ Database Server

The C++ database server must be running with the REST API enabled. The server should be accessible at `http://localhost:8080` by default. The following API endpoints are required:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check endpoint |
| `/tables` | GET | Returns list of all tables |
| `/table/{name}` | GET | Returns all data from a table |
| `/table/{name}/schema` | GET | Returns schema information for a table |

## Usage

### Quick Start

Run the complete data insights pipeline with default settings:

```bash
cd /workspace
python data_insights/main.py
```

### Custom Server URL

If your database server is running at a different URL, specify it as an argument:

```bash
python data_insights/main.py http://your-server:8080
```

### Running Individual Components

You can also run individual components separately:

```bash
# Fetch data and print database summary
python data_insights/data_fetcher.py

# Analyze data and print statistics
python data_insights/data_analyzer.py

# Generate visualizations
python data_insights/visualization.py

# Generate AI insights
python data_insights/insights_generator.py
```

### Using in Your Own Python Code

Import the pipeline into your own scripts:

```python
import sys
import os
sys.path.insert(0, '/workspace/data_insights')

from main import DataInsightsPipeline

# Create and run the pipeline
pipeline = DataInsightsPipeline(
    server_url="http://localhost:8080",
    output_dir="my_output_directory"
)

# Run the complete workflow
results = pipeline.run()

# Access the results
print(f"Tables analyzed: {results['tables_analyzed']}")
print(f"Total insights: {results['total_insights']}")
print(f"Report saved to: {results['report_path']}")
```

Access individual components directly:

```python
from data_fetcher import DatabaseFetcher
from data_analyzer import DataAnalyzer
from visualization import Visualizer
from insights_generator import InsightsGenerator

# Fetch data
fetcher = DatabaseFetcher(server_url="http://localhost:8080")
data = fetcher.get_all_data()

# Analyze data
analyzer = DataAnalyzer(data)
analysis_results = analyzer.analyze_all()

# Generate visualizations
visualizer = Visualizer(output_dir="output/visualizations")
viz_files = visualizer.visualize_all_tables(data)

# Generate insights
insights_gen = InsightsGenerator(data)
insights = insights_gen.generate_all_insights()

# Print summary
print(insights_gen.generate_summary_report())
```

## Output Files

When you run the pipeline, it creates an output directory with the following structure:

```
data_insights/output/
├── visualizations/
│   ├── table1_column1_histogram.png
│   ├── table1_column2_barchart.png
│   ├── table1_correlation_heatmap.png
│   ├── table1_dashboard.png
│   └── ...
├── insights_report_20231230_120000.txt
├── insights_20231230_120000.json
└── analysis_20231230_120000.json
```

### Output File Descriptions

The pipeline generates several types of output files:

**Text Report** (`insights_report_*.txt`): A comprehensive human-readable report containing database overview, analysis summary, AI-generated insights grouped by priority, visualization list, and actionable recommendations.

**Insights JSON** (`insights_*.json`): Machine-readable JSON file containing all generated insights organized by table and priority, useful for programmatic access or integration with other systems.

**Analysis JSON** (`analysis_*.json`): Detailed statistical analysis results including basic information, descriptive statistics, data types, missing value analysis, correlation matrices, outlier detection results, distribution analysis, categorical analysis, and data quality scores.

**Visualization Files** (`*.png`): PNG images including histograms for numeric column distributions, bar charts for categorical data, correlation heatmaps showing relationships between numeric columns, pie charts for category proportions, box plots for outlier visualization, and summary dashboards combining multiple views.

## Insights Categories

The AI-powered insights generator produces insights in several categories:

**High Priority Insights**: Critical issues requiring immediate attention such as significant missing data, duplicate records, or numerous outliers that may indicate data quality problems.

**Medium Priority Insights**: Important observations like strong correlations, moderate data quality issues, or patterns that may warrant investigation.

**Low Priority Insights**: Informational notes about data structure, basic statistics, and general observations that provide context about the data.

## Data Analysis Capabilities

The analyzer performs comprehensive statistical analysis on your data:

**Descriptive Statistics**: Calculates mean, median, standard deviation, min, max, skewness, and kurtosis for all numeric columns.

**Correlation Analysis**: Computes correlation matrices and identifies strong correlations (above 0.7 or below -0.7) between numeric columns.

**Outlier Detection**: Uses the IQR (Interquartile Range) method to identify outliers in numeric columns.

**Data Quality Assessment**: Calculates an overall quality score based on completeness and duplicate records.

**Categorical Analysis**: Analyzes categorical columns to find dominant categories, unique values, and rare categories.

## Visualization Types

The visualizer creates several types of charts:

**Distribution Charts**: Histograms showing the frequency distribution of numeric values with overlaid statistics.

**Correlation Heatmaps**: Color-coded matrices showing correlations between all numeric columns.

**Bar Charts**: Vertical bar charts showing value counts for categorical columns.

**Scatter Plots**: X-Y plots showing relationships between two numeric columns with correlation coefficients.

**Pie Charts**: Circular charts showing proportion of categories with automatic grouping of small values.

**Box Plots**: Box-and-whisker plots showing distribution summary and outliers.

**Summary Dashboards**: Multi-panel dashboards combining data overview, statistics table, missing values chart, and data type distribution.

## Recommendations

The pipeline generates actionable recommendations based on the analysis:

Data Quality Recommendations: If data quality scores are low, the system recommends cleaning duplicate entries and handling missing values.

Missing Data Recommendations: If columns have significant missing values, the system suggests imputation strategies or data collection improvements.

Outlier Recommendations: If outliers are detected, the system recommends reviewing these values for potential data entry errors or special cases.

Correlation Recommendations: If many strong correlations exist, the system suggests investigating multicollinearity for predictive modeling applications.

## Troubleshooting

If you encounter issues when running the data insights module:

**Connection Errors**: Ensure the C++ database server is running and accessible. Check that the server URL is correct and the server is listening on the expected port. Verify that no firewall is blocking the connection.

**Missing Visualizations**: If no visualizations are generated, ensure your data contains numeric or categorical columns suitable for visualization. Check the console output for any warning messages.

**Import Errors**: Verify all required Python packages are installed. Make sure the working directory is correct and the module paths are properly configured.

**Empty Results**: If the analysis returns empty results, verify that the database contains data and that tables are properly populated.

## Integration with NLP Client

The data insights module is designed to work alongside the NLP SQL client. While the NLP client allows natural language queries, the insights module provides automated analysis and visualization of all database content. Together, they provide a comprehensive database exploration experience.

## License

This module is part of the larger database project and follows the same licensing terms.
