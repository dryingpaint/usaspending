
## 🎯 Overview

The codebase has been reorganized into two main components with clear separation of concerns:

1. **Data Processor Component** (`src/data_processor/`) - Handles all data operations
2. **Visualizer Component** (`src/visualizer/`) - Handles all visualization and UI operations

## 📁 Directory Structure

```
src/
├── data_processor/           # Data Processing & Analysis Component
│   ├── __init__.py          # Module exports
│   ├── api_client.py        # USASpending API client
│   ├── data_transformer.py  # Data cleaning & transformation
│   ├── analytics_engine.py  # Advanced analytics & insights
│   └── core_processor.py    # Main orchestrator
│
├── visualizer/              # Visualization Component  
│   ├── __init__.py          # Module exports
│   ├── data_connector.py    # Bridge between data & visualization
│   ├── chart_factory.py     # Chart creation & styling
│   └── dashboard.py         # Main Streamlit dashboard
│
├── data_collection/         # Legacy (can be removed)
├── analysis/               # Legacy (can be removed)
└── visualization/          # Legacy (can be removed)
```

## 🔧 Component Architecture

### Data Processor Component

**Purpose**: Handles all data collection, processing, and analysis operations.

#### `api_client.py` - USASpending API Client
- **Enhanced API client** with comprehensive endpoint support
- **Rate limiting** and error handling
- **Pagination support** for large datasets
- **Geographic and time-based filtering**
- **Backward compatibility** with existing code

#### `data_transformer.py` - Data Transformation
- **Data cleaning** and standardization
- **Technology categorization** using keyword matching
- **Recipient type classification**
- **Geographic aggregation** by state/region
- **Time series creation** for trend analysis
- **Visualization data preparation**

#### `analytics_engine.py` - Advanced Analytics
- **Statistical analysis** (summary stats, correlations)
- **Trend detection** using linear regression
- **Period comparison** (pre/post policy analysis)
- **Geographic pattern analysis** with Gini coefficients
- **Clustering analysis** for recipient segmentation
- **Automated insight generation**

#### `core_processor.py` - Main Orchestrator
- **Unified interface** for all data operations
- **Caching system** for performance optimization
- **Comprehensive analysis** across all dimensions
- **Data export** capabilities
- **Error handling** and logging

### Visualizer Component

**Purpose**: Handles all visualization and user interface operations.

#### `data_connector.py` - Data Bridge
- **Clean interface** between data processor and visualizer
- **Data loading** and caching management
- **Summary metrics** for dashboard headers
- **Export functionality** for users
- **Error handling** for UI operations

#### `chart_factory.py` - Chart Creation
- **Consistent chart styling** with theme support
- **Interactive visualizations** using Plotly
- **Geographic maps** with Folium integration
- **Technology-specific color schemes**
- **Responsive design** for different screen sizes

#### `dashboard.py` - Main UI
- **Streamlit-based** interactive dashboard
- **Five main views**: Geographic, Timeline, Recipients, Technology, Comparative
- **Real-time data loading** with progress indicators
- **Export capabilities** and data management
- **Error handling** and user feedback
