# Federal Clean Energy Funding and State Adoption Analysis

## Project Overview

This project analyzes the relationship between federal government funding for clean energy initiatives and state-level clean energy adoption rates. Using data from the USAspending.gov API, we examine whether federal investments correlate with or predict clean energy transitions across different states.

## Research Questions

1. **Funding Distribution**: How is federal clean energy funding distributed across states?
2. **Adoption Correlation**: Do states with higher federal clean energy investments show faster clean energy adoption?
3. **Policy Impact**: Has recent legislation (IRA, CHIPS Act) changed funding patterns?
4. **Recipient Analysis**: What types of organizations receive clean energy funding in different states?
5. **Timeline Analysis**: How has the relationship between funding and adoption evolved over time?

## Key Legislation Tracked

- **Inflation Reduction Act (IRA)** - Signed August 2022
- **CHIPS and Science Act** - Signed August 2022
- **Infrastructure Investment and Jobs Act (IIJA)** - Signed November 2021
- **American Recovery and Reinvestment Act (ARRA)** - Historical comparison

## Data Sources

### Primary: USAspending.gov API
- Federal awards and spending data
- Geographic breakdowns by state
- Recipient organization details
- Award categories and descriptions

### Secondary (for validation):
- EIA State Energy Data
- NREL State Energy Profiles
- State renewable energy standards
- Clean energy capacity data

## Methodology

1. **Data Collection**: Pull federal spending data using USAspending API
2. **Categorization**: Identify clean energy-related awards using keywords and CFDA codes
3. **Geographic Analysis**: Aggregate spending by state and normalize by population/economy
4. **Correlation Analysis**: Compare funding levels with clean energy adoption metrics
5. **Temporal Analysis**: Track changes over time, especially post-IRA/CHIPS

## File Structure

```
├── data/
│   ├── raw/                 # Raw API responses
│   ├── processed/           # Cleaned and categorized data
│   └── external/            # External datasets for validation
├── src/
│   ├── data_collection/     # API data pulling scripts
│   ├── analysis/            # Analysis and correlation scripts
│   └── visualization/       # Plotting and mapping scripts
├── notebooks/               # Jupyter notebooks for exploration
├── results/                 # Output files and reports
├── config/                  # Configuration files
└── test_api_connection.py   # API connection test script
```

## Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Test API Connection
```bash
python test_api_connection.py
```

### 3. Run Data Collection
```bash
# Test with limited data first
python src/data_collection/fetch_clean_energy_awards.py

# For full collection, modify the script to remove page limits
```

### 4. Explore Data
```bash
jupyter notebook notebooks/
```

## Data Collection Strategy

### Clean Energy Keywords Tracked
- **Renewable Technologies**: solar, wind, geothermal, hydroelectric, biomass
- **Energy Storage**: battery, energy storage, grid storage
- **Grid Infrastructure**: smart grid, grid modernization, transmission
- **Electric Vehicles**: EV charging, charging infrastructure
- **Energy Efficiency**: weatherization, building efficiency
- **Advanced Technologies**: carbon capture, clean hydrogen, fuel cells

### Time Periods Analyzed
- **Pre-ARRA**: 2007-2009 (baseline)
- **ARRA Period**: 2009-2012 (stimulus era)
- **Post-ARRA/Pre-IRA**: 2013-2022 (steady state)
- **IRA/CHIPS Era**: 2022-2024 (current policy)

### Geographic Scope
- All 50 states plus Washington DC
- Analysis by place of performance and recipient location
- County and congressional district breakdowns where relevant

## Key Findings

*[To be populated after analysis]*

## Usage Examples

### Basic API Test
```python
python test_api_connection.py
```

### Collect Recent Clean Energy Data
```python
from src.data_collection.fetch_clean_energy_awards import CleanEnergyDataCollector

collector = CleanEnergyDataCollector()
df = collector.collect_awards_by_keywords(time_period="ira_chips_period", max_pages=10)
print(f"Collected {len(df)} awards")
```

### Geographic Analysis
```python
geo_data = collector.collect_geographic_spending(time_period="ira_chips_period")
print(geo_data.groupby('shape_code')['aggregated_amount'].sum().sort_values(ascending=False))
```

## Data Quality Notes

- **Coverage**: Federal data only - does not include state/local funding
- **Categorization**: Keyword-based filtering may miss some relevant awards
- **Timing**: Award dates vs. actual spending may differ
- **Geographic**: Place of performance vs. recipient location can vary

## Limitations

- Federal funding is just one factor in clean energy adoption
- State policies, market conditions, and geography also play major roles
- Data availability varies by time period and award type
- Some clean energy investments may not be easily categorized in federal data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Contact

For questions about this analysis, please open an issue in the repository. 