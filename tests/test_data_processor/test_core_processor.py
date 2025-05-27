#!/usr/bin/env python3
"""
Tests for the Core Data Processor.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
from src.data_processor.core_processor import DataProcessor


class TestDataProcessor:
    """Test suite for DataProcessor."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.processor = DataProcessor()

    def test_init(self):
        """Test processor initialization."""
        assert hasattr(self.processor, "api_client")
        assert hasattr(self.processor, "transformer")
        assert hasattr(self.processor, "analytics")
        assert hasattr(self.processor, "_cache")
        assert isinstance(self.processor._cache, dict)

    def create_sample_raw_data(self):
        """Create sample raw data as would come from API."""
        return pd.DataFrame(
            {
                "Award ID": ["AWD001", "AWD002", "AWD003"],
                "Award Amount": [1000000, 2000000, 1500000],
                "Recipient Name": ["Tesla Inc.", "Stanford University", "Green Corp"],
                "Start Date": ["2022-01-15", "2022-03-20", "2022-06-10"],
                "Place of Performance State Code": ["CA", "CA", "TX"],
                "Description": [
                    "Solar panel installation",
                    "Wind energy research",
                    "Battery storage system",
                ],
            }
        )

    @patch.object(DataProcessor, "api_client")
    def test_collect_clean_energy_data_success(self, mock_api_client):
        """Test successful data collection and processing."""
        # Mock API response
        raw_data = self.create_sample_raw_data()
        mock_api_client.get_clean_energy_data.return_value = raw_data

        result = self.processor.collect_clean_energy_data(
            time_period="test_period", max_pages=2, use_cache=False
        )

        # Verify API was called
        mock_api_client.get_clean_energy_data.assert_called_once_with(
            time_period="test_period", max_pages=2
        )

        # Verify data processing
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert "award_amount" in result.columns  # Should be renamed
        assert "technology_category" in result.columns  # Should be categorized
        assert "recipient_type" in result.columns  # Should be categorized

    @patch.object(DataProcessor, "api_client")
    def test_collect_clean_energy_data_empty_response(self, mock_api_client):
        """Test data collection with empty API response."""
        mock_api_client.get_clean_energy_data.return_value = pd.DataFrame()

        result = self.processor.collect_clean_energy_data()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    @patch.object(DataProcessor, "api_client")
    def test_collect_clean_energy_data_caching(self, mock_api_client):
        """Test data caching functionality."""
        raw_data = self.create_sample_raw_data()
        mock_api_client.get_clean_energy_data.return_value = raw_data

        # First call should hit API
        result1 = self.processor.collect_clean_energy_data(
            time_period="test_period", max_pages=2, use_cache=True
        )

        # Second call should use cache
        result2 = self.processor.collect_clean_energy_data(
            time_period="test_period", max_pages=2, use_cache=True
        )

        # API should only be called once
        assert mock_api_client.get_clean_energy_data.call_count == 1

        # Results should be identical
        pd.testing.assert_frame_equal(result1, result2)

    def test_get_geographic_analysis(self):
        """Test geographic analysis."""
        # Create processed data
        data = pd.DataFrame(
            {
                "award_amount": [1000000, 2000000, 1500000],
                "state_code": ["CA", "CA", "TX"],
                "state_name": ["California", "California", "Texas"],
                "recipient_name": ["Corp A", "Corp B", "Corp C"],
            }
        )

        result = self.processor.get_geographic_analysis(data)

        assert "state_summary" in result
        assert "patterns" in result
        assert "visualization_data" in result
        assert "insights" in result

        # Check state summary structure
        assert isinstance(result["state_summary"], list)
        if result["state_summary"]:
            assert "state_code" in result["state_summary"][0]
            assert "total_funding" in result["state_summary"][0]

    def test_get_geographic_analysis_empty(self):
        """Test geographic analysis with empty data."""
        empty_df = pd.DataFrame()
        result = self.processor.get_geographic_analysis(empty_df)
        assert result == {}

    def test_get_technology_analysis(self):
        """Test technology analysis."""
        data = pd.DataFrame(
            {
                "award_amount": [1000000, 2000000, 1500000],
                "description": ["Solar panels", "Wind turbines", "Battery storage"],
                "recipient_name": ["Corp A", "Corp B", "Corp C"],
            }
        )

        result = self.processor.get_technology_analysis(data)

        assert "technology_summary" in result
        assert "visualization_data" in result
        assert "insights" in result

        # Should have added technology categorization
        assert isinstance(result["technology_summary"], list)

    def test_get_recipient_analysis(self):
        """Test recipient analysis."""
        data = pd.DataFrame(
            {
                "award_amount": [1000000, 2000000, 1500000, 800000],
                "recipient_name": [
                    "Tesla Inc.",
                    "Corp A",
                    "Tesla Inc.",
                    "University X",
                ],
                "state_code": ["CA", "TX", "CA", "NY"],
            }
        )

        result = self.processor.get_recipient_analysis(data, top_n=10)

        assert "recipient_summary" in result
        assert "clustering" in result
        assert "visualization_data" in result
        assert "insights" in result

        # Check recipient aggregation
        if result["recipient_summary"]:
            # Tesla should be aggregated
            tesla_entries = [
                r
                for r in result["recipient_summary"]
                if r["recipient_name"] == "Tesla Inc."
            ]
            assert len(tesla_entries) == 1
            if tesla_entries:
                assert tesla_entries[0]["total_funding"] == 1800000  # 1M + 800K

    def test_get_timeline_analysis(self):
        """Test timeline analysis."""
        dates = pd.date_range("2022-01-01", periods=10, freq="M")
        data = pd.DataFrame(
            {
                "award_amount": [1000000] * 10,
                "start_date": dates,
                "recipient_name": [f"Corp_{i}" for i in range(10)],
            }
        )

        result = self.processor.get_timeline_analysis(data)

        assert "monthly_series" in result
        assert "quarterly_series" in result
        assert "trends" in result
        assert "period_comparison" in result
        assert "visualization_data" in result
        assert "insights" in result

    def test_get_timeline_analysis_no_dates(self):
        """Test timeline analysis without date column."""
        data = pd.DataFrame(
            {"award_amount": [1000000, 2000000], "recipient_name": ["Corp A", "Corp B"]}
        )

        result = self.processor.get_timeline_analysis(data)
        assert result == {}

    @patch.object(DataProcessor, "collect_clean_energy_data")
    def test_get_comprehensive_analysis(self, mock_collect):
        """Test comprehensive analysis."""
        # Mock data collection
        sample_data = pd.DataFrame(
            {
                "award_amount": [1000000, 2000000],
                "start_date": ["2022-01-01", "2022-06-01"],
                "state_code": ["CA", "TX"],
                "recipient_name": ["Corp A", "Corp B"],
                "description": ["Solar project", "Wind project"],
            }
        )
        sample_data["start_date"] = pd.to_datetime(sample_data["start_date"])
        mock_collect.return_value = sample_data

        result = self.processor.get_comprehensive_analysis(
            time_period="test_period", max_pages=3
        )

        assert "data_summary" in result
        assert "geographic" in result
        assert "technology" in result
        assert "recipients" in result
        assert "timeline" in result
        assert "overall_insights" in result

        # Check data summary
        assert result["data_summary"]["total_records"] == 2
        assert result["data_summary"]["total_funding"] == 3000000

    @patch.object(DataProcessor, "collect_clean_energy_data")
    def test_get_comprehensive_analysis_no_data(self, mock_collect):
        """Test comprehensive analysis with no data."""
        mock_collect.return_value = pd.DataFrame()

        result = self.processor.get_comprehensive_analysis()

        assert result == {"error": "No data available for analysis"}

    def test_get_summary_statistics(self):
        """Test summary statistics calculation."""
        data = pd.DataFrame(
            {
                "award_amount": [1000000, 2000000, 1500000],
                "recipient_name": ["Corp A", "Corp B", "Corp A"],
                "state_code": ["CA", "TX", "CA"],
                "technology_category": ["Solar", "Wind", "Solar"],
                "recipient_type": ["Corporation", "Corporation", "Corporation"],
            }
        )

        result = self.processor.get_summary_statistics(data)

        assert "total_records" in result
        assert "unique_recipients" in result
        assert "unique_states" in result
        assert "funding" in result
        assert "technology_distribution" in result
        assert "recipient_type_distribution" in result

        assert result["total_records"] == 3
        assert result["unique_recipients"] == 2
        assert result["unique_states"] == 2

    def test_export_data_csv(self):
        """Test data export to CSV."""
        data = pd.DataFrame(
            {"award_amount": [1000000, 2000000], "recipient_name": ["Corp A", "Corp B"]}
        )

        with patch("pandas.DataFrame.to_csv") as mock_to_csv:
            with patch("pathlib.Path.mkdir") as mock_mkdir:
                result = self.processor.export_data(data, "test.csv", "csv")

                mock_mkdir.assert_called_once()
                mock_to_csv.assert_called_once()
                assert "test.csv" in result

    def test_export_data_excel(self):
        """Test data export to Excel."""
        data = pd.DataFrame(
            {"award_amount": [1000000, 2000000], "recipient_name": ["Corp A", "Corp B"]}
        )

        with patch("pandas.DataFrame.to_excel") as mock_to_excel:
            with patch("pathlib.Path.mkdir") as mock_mkdir:
                result = self.processor.export_data(data, "test.xlsx", "excel")

                mock_to_excel.assert_called_once()
                assert "test.xlsx" in result

    def test_export_data_json(self):
        """Test data export to JSON."""
        data = pd.DataFrame(
            {"award_amount": [1000000, 2000000], "recipient_name": ["Corp A", "Corp B"]}
        )

        with patch("pandas.DataFrame.to_json") as mock_to_json:
            with patch("pathlib.Path.mkdir") as mock_mkdir:
                result = self.processor.export_data(data, "test.json", "json")

                mock_to_json.assert_called_once()
                assert "test.json" in result

    def test_export_data_empty(self):
        """Test data export with empty DataFrame."""
        empty_df = pd.DataFrame()

        with pytest.raises(ValueError, match="Cannot export empty DataFrame"):
            self.processor.export_data(empty_df)

    def test_export_data_unsupported_format(self):
        """Test data export with unsupported format."""
        data = pd.DataFrame({"col": [1, 2]})

        with pytest.raises(ValueError, match="Unsupported format"):
            self.processor.export_data(data, "test.xyz", "xyz")

    def test_clear_cache(self):
        """Test cache clearing."""
        # Add something to cache
        self.processor._cache["test_key"] = "test_value"
        assert len(self.processor._cache) == 1

        self.processor.clear_cache()
        assert len(self.processor._cache) == 0

    def test_get_cache_info(self):
        """Test cache information retrieval."""
        # Add items to cache
        self.processor._cache["key1"] = "value1"
        self.processor._cache["key2"] = "value2"

        result = self.processor.get_cache_info()

        assert "cached_datasets" in result
        assert "cache_size" in result
        assert result["cache_size"] == 2
        assert "key1" in result["cached_datasets"]
        assert "key2" in result["cached_datasets"]


class TestDataProcessorIntegration:
    """Integration tests for DataProcessor."""

    def setup_method(self):
        """Set up test fixtures."""
        self.processor = DataProcessor()

    @patch("src.data_processor.api_client.requests.Session.post")
    def test_end_to_end_processing(self, mock_post):
        """Test end-to-end data processing flow."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "Award ID": "TEST001",
                    "Award Amount": 1000000,
                    "Recipient Name": "Solar Corp Inc.",
                    "Start Date": "2022-01-15",
                    "Place of Performance State Code": "CA",
                    "Description": "Solar panel installation project",
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Run comprehensive analysis
        with patch(
            "src.data_processor.api_client.DATE_RANGES",
            {"test_period": {"start": "2022-01-01", "end": "2022-12-31"}},
        ):
            with patch(
                "src.data_processor.api_client.CLEAN_ENERGY_KEYWORDS", ["solar"]
            ):
                result = self.processor.get_comprehensive_analysis(
                    time_period="test_period", max_pages=1
                )

        # Verify complete processing pipeline
        assert "data_summary" in result
        assert "geographic" in result
        assert "technology" in result
        assert "recipients" in result
        assert "timeline" in result

        # Verify data transformations occurred
        assert result["data_summary"]["total_records"] == 1
        assert result["data_summary"]["total_funding"] == 1000000


if __name__ == "__main__":
    pytest.main([__file__])
