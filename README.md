
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


## 🎨 Dashboard Features

### **🗺️ Geographic Overview**
- **Interactive map** with funding distribution
- **State rankings** and comparisons
- **Click-to-filter** functionality
- **Hover tooltips** with detailed information

### **📈 Trends & Timeline**
- **Time series analysis** with policy annotations
- **Before/after comparisons** (Pre-IRA vs Post-IRA)
- **Technology trend shifts** over time
- **Policy impact visualization**

### **🏢 Recipients & Awards**
- **Top recipients analysis** with scatter plots
- **Award size distributions**
- **Recipient type breakdowns**
- **Searchable award tables**

### **🔬 Technology Analysis**
- **Technology funding breakdowns** (pie charts)
- **Growth rate comparisons** by technology
- **Technology evolution timeline**
- **Cross-technology analysis**

### **📊 Comparative Analysis**
- **State-by-state comparisons** with multiple metrics
- **Correlation analysis** tools
- **Efficiency metrics** and benchmarking
- **Performance visualization**
