# USAspending API Configuration

# Base API URL
BASE_URL = "https://api.usaspending.gov/api/v2"

# Key endpoints for our analysis
ENDPOINTS = {
    "spending_by_award": "/search/spending_by_award/",
    "spending_by_category": "/search/spending_by_category/",
    "spending_by_geography": "/search/spending_by_geography/",
    "spending_over_time": "/search/spending_over_time/",
    "autocomplete_cfda": "/autocomplete/cfda/",
    "references_cfda": "/references/cfda/",
}

# Clean energy related keywords for filtering awards
CLEAN_ENERGY_KEYWORDS = [
    # Renewable Energy Technologies
    "solar",
    "photovoltaic",
    "wind",
    "geothermal",
    "hydroelectric",
    "hydro power",
    "biomass",
    "biofuel",
    "biodiesel",
    "ethanol",
    "renewable energy",
    # Energy Storage
    "battery",
    "energy storage",
    "grid storage",
    "lithium",
    "energy density",
    # Grid and Infrastructure
    "smart grid",
    "grid modernization",
    "transmission",
    "microgrid",
    "grid integration",
    "power grid",
    "electrical grid",
    "grid reliability",
    # Electric Vehicles
    "electric vehicle",
    "EV charging",
    "charging station",
    "charging infrastructure",
    "electric transportation",
    "zero emission vehicle",
    # Energy Efficiency
    "energy efficiency",
    "weatherization",
    "building efficiency",
    "HVAC efficiency",
    "LED lighting",
    "insulation",
    "energy conservation",
    # Advanced Technologies
    "carbon capture",
    "carbon sequestration",
    "clean hydrogen",
    "fuel cell",
    "offshore wind",
    "concentrated solar",
    "tidal energy",
    "wave energy",
    # Climate and Clean Energy
    "clean energy",
    "climate change",
    "greenhouse gas",
    "carbon reduction",
    "decarbonization",
    "net zero",
    "carbon neutral",
]

# Energy-related CFDA codes for filtering grants and assistance programs
# CFDA = Catalog of Federal Domestic Assistance (now called "Assistance Listings")
# These are unique identifiers for federal programs providing assistance
# All codes starting with "81" are Department of Energy programs

ENERGY_CFDA_CODES = [
    # === CORE STATE & LOCAL ENERGY PROGRAMS ===
    "81.041",  # State Energy Program - Formula grants to states for energy efficiency
    # and renewable energy leadership, outreach, technology deployment
    "81.042",  # Weatherization Assistance for Low-Income Persons - Formula grants
    # to improve home energy efficiency for low-income families
    "81.119",  # State Energy Program Special Projects - Competitive grants for states
    # to implement specific DOE energy efficiency and renewable energy initiatives
    # === RENEWABLE ENERGY RESEARCH & DEVELOPMENT ===
    "81.087",  # Renewable Energy Research and Development - Project grants for research
    # in solar, biomass, hydrogen, fuel cells, wind, hydropower, geothermal
    "81.086",  # Conservation Research and Development - Research in buildings, industrial,
    # transportation technologies, and hydrogen/fuel cell infrastructure
    "81.089",  # Fossil Energy Research and Development - Clean fossil energy technologies,
    # carbon capture, storage, and utilization
    # === NUCLEAR ENERGY PROGRAMS ===
    "81.121",  # Nuclear Energy Research, Development and Demonstration - Advanced nuclear
    # technologies and underlying sciences
    "81.114",  # University Reactor Infrastructure and Education Support - Nuclear energy
    # research design, equipment upgrades, student support
    "81.112",  # Stewardship Science Grant Program - University involvement in stockpile
    # stewardship and fundamental science relevant to nuclear security
    "81.113",  # Defense Nuclear Nonproliferation Research - Research to reduce global
    # danger from proliferation of weapons of mass destruction
    # === ENERGY INFRASTRUCTURE & GRID ===
    "81.122",  # Electricity Delivery and Energy Reliability Research - Grid modernization,
    # reliability, and robust electricity supply systems
    # === INFORMATION & TECHNICAL ASSISTANCE ===
    "81.117",  # Energy Efficiency and Renewable Energy Information Dissemination -
    # Outreach, training, technical assistance for energy efficiency
    "81.064",  # Office of Scientific and Technical Information - R&D findings
    # dissemination for DOE researchers and public
    # === ADVANCED ENERGY PROJECTS ===
    "81.135",  # Advanced Research and Projects Agency - Energy (ARPA-E) -
    # High-risk, high-reward energy technology research
    "81.126",  # Federal Loan Guarantees for Innovative Energy Technologies -
    # Loan guarantees for early commercial use of new energy technologies
    # === SPECIALIZED PROGRAMS ===
    "81.079",  # Regional Biomass Energy Programs - Biomass fuels, chemicals, materials
    # and power from domestic sources
    "81.049",  # Office of Science Financial Assistance Program - Fundamental research
    # in basic sciences and advanced technology concepts
    "81.057",  # University Coal Research - Scientific understanding of coal conversion
    # and utilization chemistry and physics
    "81.105",  # National Industrial Competitiveness Through Energy, Environment, and Economics
    # (NICE3) - Program in close-out, no future financial assistance
    "81.108",  # Epidemiology and Other Health Studies - Health research for DOE workers
    # and populations exposed to energy-related health hazards
    "81.123",  # National Nuclear Security Administration (NNSA) Minority Serving Institutions
    # Program - Engage MSIs in NNSA mission activities and workforce development
    "81.124",  # Predictive Science Academic Alliance Program (PSAAP) - Multi-scale,
    # multi-physics codes with focus on validation and verification
    # === ENVIRONMENTAL & WASTE MANAGEMENT ===
    "81.104",  # Office of Environmental Waste Processing - Environmental management
    # cleanup acceleration initiatives
    "81.065",  # Nuclear Waste Disposal Siting - High-level radioactive waste disposal
    # repository development and research
    "81.106",  # Transport of Transuranic Wastes to WIPP - State and tribal cooperation
    # for safe transportation of nuclear waste
]

# PSC codes for energy-related contracts
ENERGY_PSC_CODES = [
    "Y1",  # Maintenance of Real Property
    "Z1",  # Maintenance of Equipment
    "R4",  # Utilities and Housekeeping Services
]

# Award type groups (API requires types from only one group at a time)
AWARD_TYPE_GROUPS = {
    "contracts": ["A", "B", "C", "D"],
    "grants": ["02", "03", "04", "05"],
    "loans": ["07", "08"],
    "other_financial_assistance": ["06", "10"],
    "direct_payments": ["09", "11", "-1"],
    "idvs": [
        "IDV_A",
        "IDV_B",
        "IDV_B_A",
        "IDV_B_B",
        "IDV_B_C",
        "IDV_C",
        "IDV_D",
        "IDV_E",
    ],
}

# Default award types (contracts for clean energy analysis)
DEFAULT_AWARD_TYPES = AWARD_TYPE_GROUPS["contracts"]

# Date ranges for analysis
DATE_RANGES = {
    "pre_arra": {"start": "2007-01-01", "end": "2009-02-16"},
    "arra_period": {"start": "2009-02-17", "end": "2012-12-31"},
    "post_arra_pre_ira": {"start": "2013-01-01", "end": "2022-08-15"},
    "ira_chips_period": {"start": "2022-08-16", "end": "2024-12-31"},
    "full_period": {"start": "2007-01-01", "end": "2024-12-31"},
}

# State codes for geographic analysis
STATE_CODES = [
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
    "DC",
]

# Request parameters
DEFAULT_PARAMS = {
    "limit": 100,  # Max records per request
    "page": 1,
    "sort": "Award Amount",
    "order": "desc",
}

# Default API configuration
DEFAULT_BASE_URL = "https://api.usaspending.gov/api/v2"
DEFAULT_USER_AGENT = "CleanEnergyAnalysis/1.0"
DEFAULT_CONTENT_TYPE = "application/json"
DEFAULT_TIMEOUT = 30

# Default field list for award searches
DEFAULT_AWARD_FIELDS = [
    "Award ID",
    "Recipient Name",
    "Start Date",
    "End Date",
    "Award Amount",
    "Awarding Agency",
    "Awarding Sub Agency",
    "Award Type",
    "Funding Agency",
    "Funding Sub Agency",
    "Place of Performance State Code",
    "Place of Performance State",
    "Recipient Location State Code",
    "Description",
]

# Default pagination settings
DEFAULT_MAX_PAGES = 10
DEFAULT_PAGINATION_DELAY = 0.5

# Default time period for clean energy data collection
DEFAULT_TIME_PERIOD = "ira_chips_period"
DEFAULT_CLEAN_ENERGY_MAX_PAGES = 5

# Geographic filter settings
DEFAULT_COUNTRY = "USA"

# Time grouping options for spending over time
TIME_GROUPING_OPTIONS = ["month", "quarter", "fiscal_year"]
DEFAULT_TIME_GROUPING = "month"

# Geographic scope options
GEOGRAPHIC_SCOPE_OPTIONS = ["state", "county", "district"]
DEFAULT_GEOGRAPHIC_SCOPE = "state"

# Rate limiting
RATE_LIMIT_DELAY = 0.1  # Seconds between requests
