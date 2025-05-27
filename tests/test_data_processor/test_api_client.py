#!/usr/bin/env python3
"""
Tests for the USASpending API Client.
"""

import pytest
import pandas as pd
import requests
from unittest.mock import Mock, patch
from src.data_processor.api_client import USASpendingAPIClient


class TestUSASpendingAPIClient:
    """Test suite for USASpendingAPIClient."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.client = USASpendingAPIClient()

    def test_init(self):
        """Test client initialization."""
        assert self.client.base_url == "https://api.usaspending.gov/api/v2"
        assert isinstance(self.client.session, requests.Session)
        assert self.client.session.headers["Content-Type"] == "application/json"
        assert self.client.session.headers["User-Agent"] == "CleanEnergyAnalysis/1.0"

    def test_init_custom_url(self):
        """Test client initialization with custom URL."""
        custom_url = "https://test.api.com/v1"
        client = USASpendingAPIClient(base_url=custom_url)
        assert client.base_url == custom_url

    def test_build_date_filter(self):
        """Test date filter building."""
        start_date = "2022-01-01"
        end_date = "2022-12-31"

        result = self.client.build_date_filter(start_date, end_date)

        expected = {"time_period": [{"start_date": start_date, "end_date": end_date}]}
        assert result == expected

    def test_build_keyword_filter(self):
        """Test keyword filter building."""
        keywords = ["solar", "wind", "battery"]

        result = self.client.build_keyword_filter(keywords)

        expected = {"keywords": keywords}
        assert result == expected

    def test_build_geographic_filter_states(self):
        """Test geographic filter building with states."""
        states = ["CA", "TX", "NY"]

        result = self.client.build_geographic_filter(states=states)

        expected = {
            "place_of_performance_locations": [
                {"country": "USA", "state": "CA"},
                {"country": "USA", "state": "TX"},
                {"country": "USA", "state": "NY"},
            ]
        }
        assert result == expected

    def test_build_geographic_filter_counties(self):
        """Test geographic filter building with counties."""
        counties = ["Los Angeles", "Harris", "Cook"]

        result = self.client.build_geographic_filter(counties=counties)

        expected = {
            "place_of_performance_locations": [
                {"country": "USA", "county": "Los Angeles"},
                {"country": "USA", "county": "Harris"},
                {"country": "USA", "county": "Cook"},
            ]
        }
        assert result == expected

    def test_build_geographic_filter_empty(self):
        """Test geographic filter building with no parameters."""
        result = self.client.build_geographic_filter()
        assert result == {}

    @patch("src.data_processor.api_client.requests.Session.post")
    def test_search_awards_success(self, mock_post):
        """Test successful awards search."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "Award ID": "TEST001",
                    "Recipient Name": "Test Corp",
                    "Award Amount": 1000000,
                }
            ],
            "page_metadata": {"total": 1},
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        filters = {"keywords": ["solar"]}
        result = self.client.search_awards(filters)

        assert "results" in result
        assert len(result["results"]) == 1
        assert result["results"][0]["Award ID"] == "TEST001"

        # Verify the API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert (
            "spending_by_award" in call_args[1]["json"]["filters"]
            or "keywords" in call_args[1]["json"]["filters"]
        )

    @patch("src.data_processor.api_client.requests.Session.post")
    def test_search_awards_request_exception(self, mock_post):
        """Test awards search with request exception."""
        mock_post.side_effect = requests.exceptions.RequestException("Network error")

        filters = {"keywords": ["solar"]}
        result = self.client.search_awards(filters)

        assert result == {"results": [], "page_metadata": {}}

    @patch("src.data_processor.api_client.requests.Session.post")
    def test_search_awards_custom_fields(self, mock_post):
        """Test awards search with custom fields."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "page_metadata": {}}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        filters = {"keywords": ["solar"]}
        custom_fields = ["Award ID", "Recipient Name"]

        self.client.search_awards(filters, fields=custom_fields)

        call_args = mock_post.call_args
        assert call_args[1]["json"]["fields"] == custom_fields

    @patch("src.data_processor.api_client.requests.Session.post")
    def test_get_geographic_spending_success(self, mock_post):
        """Test successful geographic spending request."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"state": "CA", "total_spending": 5000000}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        filters = {"keywords": ["solar"]}
        result = self.client.get_geographic_spending(filters)

        assert "results" in result
        assert len(result["results"]) == 1
        assert result["results"][0]["state"] == "CA"

    @patch("src.data_processor.api_client.requests.Session.post")
    def test_get_geographic_spending_exception(self, mock_post):
        """Test geographic spending request with exception."""
        mock_post.side_effect = requests.exceptions.RequestException("Network error")

        filters = {"keywords": ["solar"]}
        result = self.client.get_geographic_spending(filters)

        assert result == {"results": []}

    @patch("src.data_processor.api_client.requests.Session.post")
    def test_get_spending_over_time_success(self, mock_post):
        """Test successful spending over time request."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"time_period": "2022-01", "total_spending": 1000000}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        filters = {"keywords": ["solar"]}
        result = self.client.get_spending_over_time(filters)

        assert "results" in result
        assert len(result["results"]) == 1

    @patch("src.data_processor.api_client.requests.Session.post")
    def test_get_recipient_data_success(self, mock_post):
        """Test successful recipient data request."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"recipient": "Test Corp", "total_spending": 2000000}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        filters = {"keywords": ["solar"]}
        result = self.client.get_recipient_data(filters)

        assert "results" in result
        assert len(result["results"]) == 1

    @patch.object(USASpendingAPIClient, "search_awards")
    @patch("time.sleep")
    def test_collect_paginated_data_success(self, mock_sleep, mock_search):
        """Test successful paginated data collection."""
        # Mock responses for multiple pages
        mock_search.side_effect = [
            {"results": [{"id": 1}, {"id": 2}]},
            {"results": [{"id": 3}, {"id": 4}]},
            {"results": []},  # Empty results to stop pagination
        ]

        filters = {"keywords": ["solar"]}
        result = self.client.collect_paginated_data(filters, max_pages=3)

        assert len(result) == 4
        assert result[0]["id"] == 1
        assert result[3]["id"] == 4
        assert mock_search.call_count == 3

    @patch.object(USASpendingAPIClient, "search_awards")
    def test_collect_paginated_data_no_results(self, mock_search):
        """Test paginated data collection with no results."""
        mock_search.return_value = {"results": []}

        filters = {"keywords": ["nonexistent"]}
        result = self.client.collect_paginated_data(filters, max_pages=2)

        assert len(result) == 0
        assert mock_search.call_count == 1

    @patch.object(USASpendingAPIClient, "collect_paginated_data")
    @patch(
        "src.data_processor.api_client.DATE_RANGES",
        {"test_period": {"start": "2022-01-01", "end": "2022-12-31"}},
    )
    @patch("src.data_processor.api_client.CLEAN_ENERGY_KEYWORDS", ["solar", "wind"])
    def test_get_clean_energy_data_success(self, mock_collect):
        """Test successful clean energy data collection."""
        mock_collect.return_value = [
            {"Award ID": "TEST001", "Award Amount": 1000000},
            {"Award ID": "TEST002", "Award Amount": 2000000},
        ]

        result = self.client.get_clean_energy_data("test_period", max_pages=2)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "Award ID" in result.columns

    @patch.object(USASpendingAPIClient, "collect_paginated_data")
    @patch(
        "src.data_processor.api_client.DATE_RANGES",
        {"test_period": {"start": "2022-01-01", "end": "2022-12-31"}},
    )
    @patch("src.data_processor.api_client.CLEAN_ENERGY_KEYWORDS", ["solar", "wind"])
    def test_get_clean_energy_data_empty(self, mock_collect):
        """Test clean energy data collection with empty results."""
        mock_collect.return_value = []

        result = self.client.get_clean_energy_data("test_period")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_backward_compatibility_alias(self):
        """Test that the backward compatibility alias works."""
        from src.data_processor.api_client import USASpendingAPIClient

        client = USASpendingAPIClient()
        assert isinstance(client, USASpendingAPIClient)


class TestUSASpendingAPIClientIntegration:
    """Integration tests for USASpendingAPIClient (require network access)."""

    @pytest.mark.integration
    def test_real_api_connection(self):
        """Test actual connection to USASpending API."""
        client = USASpendingAPIClient()

        # Simple test with minimal filters
        filters = {
            "time_period": [{"start_date": "2023-01-01", "end_date": "2023-01-31"}],
            "keywords": ["solar"],
        }

        try:
            result = client.search_awards(filters, limit=1)
            assert "results" in result
            # Don't assert on specific content as API data changes
        except requests.exceptions.RequestException:
            pytest.skip("API not accessible")

    @pytest.mark.integration
    def test_real_geographic_endpoint(self):
        """Test actual geographic endpoint."""
        client = USASpendingAPIClient()

        filters = {
            "time_period": [{"start_date": "2023-01-01", "end_date": "2023-01-31"}]
        }

        try:
            result = client.get_geographic_spending(filters, scope="state")
            assert "results" in result
        except requests.exceptions.RequestException:
            pytest.skip("API not accessible")


if __name__ == "__main__":
    pytest.main([__file__])
