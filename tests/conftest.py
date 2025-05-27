#!/usr/bin/env python3
"""
Pytest configuration and shared fixtures for the test suite.
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add the src directory to the Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_raw_api_data():
    """Fixture providing sample raw data as would come from the USASpending API."""
    return pd.DataFrame(
        {
            "Award ID": ["AWD001", "AWD002", "AWD003", "AWD004", "AWD005"],
            "Award Amount": [1000000, 2500000, 750000, 3200000, 1800000],
            "Recipient Name": [
                "Tesla Inc.",
                "Stanford University",
                "Green Energy Corp",
                "MIT",
                "Solar Solutions LLC",
            ],
            "Award Type": ["Contract", "Grant", "Contract", "Grant", "Contract"],
            "Start Date": [
                "2022-01-15",
                "2022-03-20",
                "2022-06-10",
                "2022-09-05",
                "2023-01-12",
            ],
            "End Date": [
                "2023-01-15",
                "2023-03-20",
                "2023-06-10",
                "2023-09-05",
                "2024-01-12",
            ],
            "Place of Performance State Code": ["CA", "CA", "TX", "MA", "AZ"],
            "Place of Performance State": [
                "California",
                "California",
                "Texas",
                "Massachusetts",
                "Arizona",
            ],
            "Recipient Location State Code": ["CA", "CA", "TX", "MA", "AZ"],
            "Awarding Agency": [
                "Department of Energy",
                "National Science Foundation",
                "Department of Energy",
                "National Science Foundation",
                "Department of Energy",
            ],
            "Description": [
                "Solar panel installation and grid integration project",
                "Advanced wind energy research and development initiative",
                "Battery storage system for renewable energy applications",
                "Smart grid technology development and testing",
                "Concentrated solar power demonstration project",
            ],
        }
    )


@pytest.fixture
def sample_cleaned_data():
    """Fixture providing sample cleaned and processed data."""
    return pd.DataFrame(
        {
            "award_amount": [1000000, 2500000, 750000, 3200000, 1800000],
            "recipient_name": [
                "Tesla Inc.",
                "Stanford University",
                "Green Energy Corp",
                "MIT",
                "Solar Solutions LLC",
            ],
            "award_type": ["Contract", "Grant", "Contract", "Grant", "Contract"],
            "start_date": pd.to_datetime(
                ["2022-01-15", "2022-03-20", "2022-06-10", "2022-09-05", "2023-01-12"]
            ),
            "end_date": pd.to_datetime(
                ["2023-01-15", "2023-03-20", "2023-06-10", "2023-09-05", "2024-01-12"]
            ),
            "state_code": ["CA", "CA", "TX", "MA", "AZ"],
            "state_name": [
                "California",
                "California",
                "Texas",
                "Massachusetts",
                "Arizona",
            ],
            "awarding_agency": [
                "Department of Energy",
                "National Science Foundation",
                "Department of Energy",
                "National Science Foundation",
                "Department of Energy",
            ],
            "description": [
                "Solar panel installation and grid integration project",
                "Advanced wind energy research and development initiative",
                "Battery storage system for renewable energy applications",
                "Smart grid technology development and testing",
                "Concentrated solar power demonstration project",
            ],
            "technology_category": ["Solar", "Wind", "Battery", "Grid", "Solar"],
            "recipient_type": [
                "Corporation",
                "University",
                "Corporation",
                "University",
                "Corporation",
            ],
        }
    )


@pytest.fixture
def sample_time_series_data():
    """Fixture providing sample time series data for trend analysis."""
    dates = pd.date_range("2022-01-01", periods=24, freq="M")
    np.random.seed(42)  # For reproducible tests

    # Create data with a slight upward trend plus noise
    base_amounts = [1000000 + i * 50000 for i in range(24)]
    noise = np.random.normal(0, 100000, 24)
    amounts = [max(0, base + n) for base, n in zip(base_amounts, noise)]

    return pd.DataFrame(
        {
            "start_date": dates,
            "award_amount": amounts,
            "state_code": np.random.choice(["CA", "TX", "NY", "FL"], 24),
            "technology_category": np.random.choice(["Solar", "Wind", "Battery"], 24),
            "recipient_name": [f"Company_{i%10}" for i in range(24)],
        }
    )


@pytest.fixture
def sample_geographic_data():
    """Fixture providing sample geographic data for spatial analysis."""
    return pd.DataFrame(
        {
            "state_code": ["CA", "CA", "CA", "TX", "TX", "NY", "FL", "WA"],
            "state_name": [
                "California",
                "California",
                "California",
                "Texas",
                "Texas",
                "New York",
                "Florida",
                "Washington",
            ],
            "award_amount": [
                5000000,
                3000000,
                2000000,
                4000000,
                1500000,
                3500000,
                2500000,
                1800000,
            ],
            "recipient_name": [
                "Solar Corp A",
                "Wind Corp B",
                "Battery Corp C",
                "Energy Corp D",
                "Grid Corp E",
                "Tech Corp F",
                "Green Corp G",
                "Clean Corp H",
            ],
            "technology_category": [
                "Solar",
                "Wind",
                "Battery",
                "Solar",
                "Grid",
                "Wind",
                "Solar",
                "Wind",
            ],
        }
    )


@pytest.fixture
def mock_api_response():
    """Fixture providing a mock API response structure."""
    return {
        "results": [
            {
                "Award ID": "TEST001",
                "Award Amount": 1000000,
                "Recipient Name": "Test Corporation",
                "Start Date": "2022-01-01",
                "Place of Performance State Code": "CA",
                "Description": "Solar energy project",
            }
        ],
        "page_metadata": {"total": 1, "page": 1, "limit": 100},
    }


@pytest.fixture
def empty_dataframe():
    """Fixture providing an empty DataFrame for testing edge cases."""
    return pd.DataFrame()


# Pytest markers for different test categories
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (may require network)"
    )
    config.addinivalue_line("markers", "slow: marks tests as slow running")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")


# Custom assertion helpers
def assert_dataframe_structure(df, expected_columns, min_rows=0):
    """Assert that a DataFrame has the expected structure."""
    assert isinstance(df, pd.DataFrame), "Expected a pandas DataFrame"
    assert len(df) >= min_rows, f"Expected at least {min_rows} rows, got {len(df)}"

    for col in expected_columns:
        assert col in df.columns, f"Expected column '{col}' not found in DataFrame"


def assert_analysis_result_structure(result, expected_keys):
    """Assert that an analysis result has the expected structure."""
    assert isinstance(result, dict), "Expected analysis result to be a dictionary"

    for key in expected_keys:
        assert key in result, f"Expected key '{key}' not found in analysis result"


# Test data generators
def generate_funding_data(
    n_records=100, start_date="2022-01-01", end_date="2023-12-31"
):
    """Generate synthetic funding data for testing."""
    np.random.seed(42)

    dates = pd.date_range(start_date, end_date, periods=n_records)
    states = ["CA", "TX", "NY", "FL", "WA", "IL", "PA", "OH", "GA", "NC"]
    technologies = ["Solar", "Wind", "Battery", "Grid", "Hydro", "Geothermal"]

    return pd.DataFrame(
        {
            "award_amount": np.random.lognormal(15, 1, n_records),
            "start_date": dates,
            "state_code": np.random.choice(states, n_records),
            "technology_category": np.random.choice(technologies, n_records),
            "recipient_name": [f"Company_{i%50}" for i in range(n_records)],
            "recipient_type": np.random.choice(
                ["Corporation", "University", "Government", "Nonprofit"], n_records
            ),
        }
    )


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Automatically cleanup test files after each test."""
    yield

    # Clean up any test files that might have been created
    test_files = [
        "test_output.csv",
        "test_output.xlsx",
        "test_output.json",
        "data/processed/test.csv",
    ]

    for file_path in test_files:
        path = Path(file_path)
        if path.exists():
            try:
                path.unlink()
            except Exception:
                pass  # Ignore cleanup errors
