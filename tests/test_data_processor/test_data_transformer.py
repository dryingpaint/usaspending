#!/usr/bin/env python3
"""
Tests for the Data Transformer.
"""

import pytest
import pandas as pd
from src.data_processor.data_transformer import DataTransformer


class TestDataTransformer:
    """Test suite for DataTransformer."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.transformer = DataTransformer()

    def test_init(self):
        """Test transformer initialization."""
        assert isinstance(self.transformer.technology_categories, dict)
        assert isinstance(self.transformer.recipient_types, dict)
        assert "Solar" in self.transformer.technology_categories
        assert "Corporation" in self.transformer.recipient_types

    def create_sample_data(self):
        """Create sample data for testing."""
        return pd.DataFrame(
            {
                "Award Amount": [1000000, 2000000, 500000, 3000000],
                "Recipient Name": [
                    "Tesla Inc.",
                    "Stanford University",
                    "ABC Corp",
                    "Green Energy Foundation",
                ],
                "Award Type": ["Contract", "Grant", "Contract", "Grant"],
                "Start Date": ["2022-01-15", "2022-03-20", "2022-06-10", "2022-09-05"],
                "End Date": ["2023-01-15", "2023-03-20", "2023-06-10", "2023-09-05"],
                "Place of Performance State Code": ["CA", "CA", "TX", "NY"],
                "Place of Performance State": [
                    "California",
                    "California",
                    "Texas",
                    "New York",
                ],
                "Description": [
                    "Solar panel installation project",
                    "Wind energy research initiative",
                    "Battery storage development",
                    "Grid modernization study",
                ],
            }
        )

    def test_clean_award_data_basic(self):
        """Test basic data cleaning functionality."""
        raw_data = self.create_sample_data()

        result = self.transformer.clean_award_data(raw_data)

        # Check column renaming
        assert "award_amount" in result.columns
        assert "recipient_name" in result.columns
        assert "start_date" in result.columns

        # Check data types
        assert pd.api.types.is_numeric_dtype(result["award_amount"])
        assert pd.api.types.is_datetime64_any_dtype(result["start_date"])

    def test_clean_award_data_empty(self):
        """Test cleaning empty DataFrame."""
        empty_df = pd.DataFrame()
        result = self.transformer.clean_award_data(empty_df)
        assert result.empty

    def test_clean_award_data_invalid_amounts(self):
        """Test cleaning data with invalid amounts."""
        data = pd.DataFrame(
            {
                "Award Amount": [1000000, -500000, 0, "invalid", None],
                "Recipient Name": ["Corp A", "Corp B", "Corp C", "Corp D", "Corp E"],
            }
        )

        result = self.transformer.clean_award_data(data)

        # Should only keep positive amounts
        assert len(result) == 1
        assert result.iloc[0]["award_amount"] == 1000000

    def test_categorize_by_technology(self):
        """Test technology categorization."""
        data = self.create_sample_data()
        cleaned_data = self.transformer.clean_award_data(data)

        result = self.transformer.categorize_by_technology(cleaned_data)

        assert "technology_category" in result.columns

        # Check specific categorizations
        solar_mask = result["description"].str.contains("solar", case=False)
        assert result.loc[solar_mask, "technology_category"].iloc[0] == "Solar"

        wind_mask = result["description"].str.contains("wind", case=False)
        assert result.loc[wind_mask, "technology_category"].iloc[0] == "Wind"

    def test_categorize_by_technology_empty(self):
        """Test technology categorization with empty data."""
        empty_df = pd.DataFrame()
        result = self.transformer.categorize_by_technology(empty_df)
        assert result.empty

    def test_categorize_by_technology_missing_column(self):
        """Test technology categorization with missing description column."""
        data = pd.DataFrame({"award_amount": [1000000]})
        result = self.transformer.categorize_by_technology(data)
        assert result.equals(data)  # Should return unchanged

    def test_categorize_recipients(self):
        """Test recipient categorization."""
        data = self.create_sample_data()
        cleaned_data = self.transformer.clean_award_data(data)

        result = self.transformer.categorize_recipients(cleaned_data)

        assert "recipient_type" in result.columns

        # Check specific categorizations
        corp_mask = result["recipient_name"].str.contains("Inc", case=False)
        assert result.loc[corp_mask, "recipient_type"].iloc[0] == "Corporation"

        uni_mask = result["recipient_name"].str.contains("University", case=False)
        assert result.loc[uni_mask, "recipient_type"].iloc[0] == "University"

    def test_aggregate_by_state(self):
        """Test state aggregation."""
        data = self.create_sample_data()
        cleaned_data = self.transformer.clean_award_data(data)

        result = self.transformer.aggregate_by_state(cleaned_data)

        assert "state_code" in result.columns
        assert "total_funding" in result.columns
        assert "award_count" in result.columns
        assert "avg_award_size" in result.columns
        assert "unique_recipients" in result.columns

        # Check CA aggregation (2 awards)
        ca_row = result[result["state_code"] == "CA"]
        assert len(ca_row) == 1
        assert ca_row.iloc[0]["award_count"] == 2
        assert ca_row.iloc[0]["total_funding"] == 3000000  # 1M + 2M

    def test_aggregate_by_state_empty(self):
        """Test state aggregation with empty data."""
        empty_df = pd.DataFrame()
        result = self.transformer.aggregate_by_state(empty_df)
        assert result.empty

    def test_aggregate_by_technology(self):
        """Test technology aggregation."""
        data = self.create_sample_data()
        cleaned_data = self.transformer.clean_award_data(data)
        categorized_data = self.transformer.categorize_by_technology(cleaned_data)

        result = self.transformer.aggregate_by_technology(categorized_data)

        assert "technology_category" in result.columns
        assert "total_funding" in result.columns
        assert "funding_percentage" in result.columns

        # Check that percentages sum to 100
        assert abs(result["funding_percentage"].sum() - 100.0) < 0.1

    def test_aggregate_by_recipient(self):
        """Test recipient aggregation."""
        data = self.create_sample_data()
        cleaned_data = self.transformer.clean_award_data(data)

        result = self.transformer.aggregate_by_recipient(cleaned_data, top_n=10)

        assert "recipient_name" in result.columns
        assert "total_funding" in result.columns
        assert "award_count" in result.columns

        # Should be sorted by total funding descending
        assert result["total_funding"].is_monotonic_decreasing

    def test_create_time_series(self):
        """Test time series creation."""
        data = self.create_sample_data()
        cleaned_data = self.transformer.clean_award_data(data)

        result = self.transformer.create_time_series(cleaned_data, freq="M")

        assert "start_date" in result.columns
        assert "total_funding" in result.columns
        assert "award_count" in result.columns
        assert "cumulative_funding" in result.columns

        # Check that cumulative funding is monotonic
        assert result["cumulative_funding"].is_monotonic_increasing

    def test_create_time_series_quarterly(self):
        """Test quarterly time series creation."""
        data = self.create_sample_data()
        cleaned_data = self.transformer.clean_award_data(data)

        result = self.transformer.create_time_series(cleaned_data, freq="Q")

        assert len(result) <= 4  # Should have at most 4 quarters

    def test_calculate_growth_rates(self):
        """Test growth rate calculation."""
        # Create time series data
        dates = pd.date_range("2022-01-01", periods=12, freq="M")
        data = pd.DataFrame(
            {
                "start_date": dates,
                "total_funding": [1000000 * (1 + i * 0.1) for i in range(12)],
            }
        )

        result = self.transformer.calculate_growth_rates(data)

        assert "total_funding_growth" in result.columns
        # First value should be NaN (no previous period)
        assert pd.isna(result.iloc[0]["total_funding_growth"])
        # Subsequent values should be positive (growing trend)
        assert result.iloc[1]["total_funding_growth"] > 0

    def test_prepare_for_visualization_geographic(self):
        """Test geographic visualization data preparation."""
        data = self.create_sample_data()
        cleaned_data = self.transformer.clean_award_data(data)

        result = self.transformer.prepare_for_visualization(cleaned_data, "geographic")

        assert "state_summary" in result
        assert "total_states" in result
        assert "geographic_distribution" in result

    def test_prepare_for_visualization_timeline(self):
        """Test timeline visualization data preparation."""
        data = self.create_sample_data()
        cleaned_data = self.transformer.clean_award_data(data)

        result = self.transformer.prepare_for_visualization(cleaned_data, "timeline")

        assert "monthly_series" in result
        assert "total_periods" in result

    def test_prepare_for_visualization_technology(self):
        """Test technology visualization data preparation."""
        data = self.create_sample_data()
        cleaned_data = self.transformer.clean_award_data(data)

        result = self.transformer.prepare_for_visualization(cleaned_data, "technology")

        assert "technology_breakdown" in result
        assert "total_technologies" in result
        assert "diversity_index" in result

    def test_prepare_for_visualization_recipient(self):
        """Test recipient visualization data preparation."""
        data = self.create_sample_data()
        cleaned_data = self.transformer.clean_award_data(data)

        result = self.transformer.prepare_for_visualization(cleaned_data, "recipient")

        assert "top_recipients" in result
        assert "total_recipients" in result
        assert "concentration_ratio" in result

    def test_prepare_for_visualization_unknown_type(self):
        """Test visualization data preparation with unknown type."""
        data = self.create_sample_data()
        cleaned_data = self.transformer.clean_award_data(data)

        result = self.transformer.prepare_for_visualization(cleaned_data, "unknown")

        assert "data" in result
        assert isinstance(result["data"], list)


class TestDataTransformerEdgeCases:
    """Test edge cases and error conditions for DataTransformer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = DataTransformer()

    def test_clean_data_with_nulls(self):
        """Test cleaning data with null values."""
        data = pd.DataFrame(
            {
                "Award Amount": [1000000, None, 2000000],
                "Recipient Name": ["Corp A", None, "Corp C"],
                "Start Date": ["2022-01-01", None, "2022-03-01"],
            }
        )

        result = self.transformer.clean_award_data(data)

        # Should handle nulls gracefully
        assert len(result) == 2  # Null amount should be removed
        assert not result["recipient_name"].isna().any()

    def test_categorize_with_special_characters(self):
        """Test categorization with special characters in text."""
        data = pd.DataFrame(
            {
                "description": [
                    "Solar-powered system with 100% efficiency",
                    "Wind & solar hybrid project",
                    "Battery/storage solution",
                ],
                "award_amount": [1000000, 2000000, 500000],
            }
        )

        result = self.transformer.categorize_by_technology(data)

        # Should handle special characters in regex matching
        assert "technology_category" in result.columns
        assert not result["technology_category"].isna().any()

    def test_aggregate_with_duplicate_recipients(self):
        """Test aggregation with duplicate recipient names."""
        data = pd.DataFrame(
            {
                "award_amount": [1000000, 2000000, 1500000],
                "recipient_name": ["Corp A", "Corp A", "Corp B"],
                "state_code": ["CA", "CA", "TX"],
            }
        )

        result = self.transformer.aggregate_by_recipient(data)

        # Corp A should be aggregated
        corp_a = result[result["recipient_name"] == "Corp A"]
        assert len(corp_a) == 1
        assert corp_a.iloc[0]["total_funding"] == 3000000
        assert corp_a.iloc[0]["award_count"] == 2

    def test_time_series_with_irregular_dates(self):
        """Test time series creation with irregular date spacing."""
        data = pd.DataFrame(
            {
                "start_date": ["2022-01-01", "2022-01-15", "2022-03-01", "2022-06-01"],
                "award_amount": [1000000, 500000, 2000000, 1500000],
            }
        )
        data["start_date"] = pd.to_datetime(data["start_date"])

        result = self.transformer.create_time_series(data, freq="M")

        # Should handle irregular spacing
        assert len(result) >= 3  # At least Jan, Mar, Jun
        assert "cumulative_funding" in result.columns


if __name__ == "__main__":
    pytest.main([__file__])
