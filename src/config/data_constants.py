#!/usr/bin/env python3
"""
Data Transformation Constants

Contains all constants used for data cleaning, categorization, and transformation
in the federal clean energy funding analysis project.
"""

# Technology categorization keywords
TECHNOLOGY_CATEGORIES = {
    "Solar": [
        "solar",
        "photovoltaic",
        "pv",
        "solar panel",
        "solar energy",
        "solar power",
        "solar cell",
        "solar array",
    ],
    "Wind": [
        "wind",
        "wind turbine",
        "wind energy",
        "wind power",
        "wind farm",
        "offshore wind",
        "onshore wind",
    ],
    "Battery Storage": [
        "battery",
        "energy storage",
        "battery storage",
        "grid storage",
        "lithium",
        "battery system",
        "energy storage system",
    ],
    "Grid Modernization": [
        "grid",
        "smart grid",
        "grid modernization",
        "transmission",
        "distribution",
        "grid infrastructure",
        "power grid",
    ],
    "Electric Vehicles": [
        "electric vehicle",
        "ev charging",
        "charging station",
        "charging infrastructure",
        "electric car",
        "ev",
    ],
    "Energy Efficiency": [
        "efficiency",
        "energy efficiency",
        "weatherization",
        "insulation",
        "building efficiency",
        "hvac",
    ],
    "Carbon Capture": [
        "carbon capture",
        "carbon sequestration",
        "ccs",
        "carbon storage",
        "co2 capture",
    ],
    "Geothermal": [
        "geothermal",
        "geothermal energy",
        "geothermal power",
        "ground source heat",
    ],
    "Hydroelectric": [
        "hydroelectric",
        "hydro",
        "hydropower",
        "water power",
        "dam",
        "turbine",
    ],
    "Biomass": [
        "biomass",
        "biofuel",
        "biogas",
        "bioenergy",
        "renewable fuel",
        "ethanol",
    ],
    "Hydrogen": [
        "hydrogen",
        "fuel cell",
        "hydrogen fuel",
        "clean hydrogen",
        "hydrogen energy",
    ],
}

# Recipient type categorization keywords
RECIPIENT_TYPES = {
    "Corporation": [
        "inc",
        "corp",
        "llc",
        "ltd",
        "company",
        "co.",
        "corporation",
        "incorporated",
    ],
    "University": [
        "university",
        "college",
        "institute",
        "school",
        "academic",
        "education",
    ],
    "Government": [
        "department",
        "agency",
        "bureau",
        "office",
        "government",
        "federal",
        "state",
        "city",
        "county",
    ],
    "Non-Profit": [
        "foundation",
        "association",
        "society",
        "organization",
        "non-profit",
        "nonprofit",
    ],
}

# Column mapping for data cleaning
COLUMN_MAPPING = {
    "Award Amount": "award_amount",
    "Recipient Name": "recipient_name",
    "Award Type": "award_type",
    "Start Date": "start_date",
    "End Date": "end_date",
    "Place of Performance State Code": "state_code",
    "Place of Performance State": "state_name",
    "Awarding Agency": "awarding_agency",
    "Funding Agency": "funding_agency",
    "Description": "description",
    "Award ID": "award_id",
}

# Date columns for processing
DATE_COLUMNS = ["start_date", "end_date"]

# Text columns for cleaning
TEXT_COLUMNS = ["recipient_name", "description", "awarding_agency"]

# Default categorization values
DEFAULT_TECHNOLOGY_CATEGORY = "Other"
DEFAULT_RECIPIENT_TYPE = "Other"

# Time series frequency options
TIME_SERIES_FREQUENCIES = {
    "daily": "D",
    "weekly": "W",
    "monthly": "M",
    "quarterly": "Q",
    "yearly": "Y",
}

# Aggregation column configurations
STATE_AGGREGATION_COLUMNS = {
    "award_amount": ["sum", "count", "mean"],
    "recipient_name": "nunique",
}

TECHNOLOGY_AGGREGATION_COLUMNS = {
    "award_amount": ["sum", "count", "mean"],
    "recipient_name": "nunique",
}

RECIPIENT_AGGREGATION_COLUMNS = {
    "award_amount": ["sum", "count", "mean"],
    "state_code": "first",
    "technology_category": lambda x: x.mode().iloc[0] if not x.empty else "Other",
}

# Flattened column names for aggregations
STATE_AGG_COLUMN_NAMES = [
    "total_funding",
    "award_count",
    "avg_award_size",
    "unique_recipients",
]

TECHNOLOGY_AGG_COLUMN_NAMES = [
    "total_funding",
    "award_count",
    "avg_award_size",
    "unique_recipients",
]

RECIPIENT_AGG_COLUMN_NAMES = [
    "total_funding",
    "award_count",
    "avg_award_size",
    "primary_state",
    "primary_technology",
]

# Time series aggregation columns
TIME_SERIES_AGGREGATION_COLUMNS = {
    "award_amount": ["sum", "count"],
    "recipient_name": "nunique",
}

TIME_SERIES_COLUMN_NAMES = ["total_funding", "award_count", "unique_recipients"]

# Visualization preparation constants
VISUALIZATION_TYPES = ["geographic", "timeline", "technology", "recipient"]

# Default values for various operations
DEFAULT_TOP_N_RECIPIENTS = 50
DEFAULT_TIME_SERIES_FREQUENCY = "M"
DEFAULT_GROWTH_PERIODS = 1
MINIMUM_YOY_PERIODS = 12

# Rounding precision for calculations
CALCULATION_PRECISION = 2
