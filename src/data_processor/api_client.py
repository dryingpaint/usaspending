#!/usr/bin/env python3
"""
USASpending API Client

Handles all interactions with the USASpending.gov API for federal spending data.
This is the main interface for data collection operations.
"""

import requests
import time
from typing import Dict, List, Optional, Any
import pandas as pd

# Import config using absolute import
from src.config.api_config import (
    CLEAN_ENERGY_KEYWORDS,
    DATE_RANGES,
    DEFAULT_USER_AGENT,
    DEFAULT_CONTENT_TYPE,
    DEFAULT_BASE_URL,
    DEFAULT_AWARD_FIELDS,
)


class USASpendingAPIClient:
    """
    Enhanced USASpending API client for federal clean energy funding data collection.

    This class provides a clean interface for interacting with the USASpending API,
    with built-in error handling, rate limiting, and data transformation capabilities.
    """

    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": DEFAULT_CONTENT_TYPE,
                "User-Agent": DEFAULT_USER_AGENT,
            }
        )

    def build_date_filter(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Build date filter for API requests."""
        return {"time_period": [{"start_date": start_date, "end_date": end_date}]}

    def build_keyword_filter(self, keywords: List[str]) -> Dict[str, Any]:
        """Build keyword filter for clean energy related awards."""
        return {"keywords": keywords}

    def build_geographic_filter(
        self, states: Optional[List[str]] = None, counties: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Build geographic filter for location-based queries."""
        filter_dict = {}

        if states:
            filter_dict["place_of_performance_locations"] = [
                {"country": "USA", "state": state} for state in states
            ]

        if counties:
            filter_dict["place_of_performance_locations"] = [
                {"country": "USA", "county": county} for county in counties
            ]

        return filter_dict

    def search_awards(
        self,
        filters: Dict[str, Any],
        fields: Optional[List[str]] = None,
        limit: int = 100,
        page: int = 1,
        sort: str = "Award Amount",
        order: str = "desc",
    ) -> Dict[str, Any]:
        """
        Search for awards using the spending_by_award endpoint.

        Args:
            filters: Dictionary of filters to apply
            fields: List of fields to return
            limit: Number of results per page
            page: Page number
            sort: Field to sort by
            order: Sort order (asc/desc)

        Returns:
            Dictionary containing API response
        """
        if fields is None:
            fields = DEFAULT_AWARD_FIELDS

        payload = {
            "filters": filters,
            "fields": fields,
            "sort": sort,
            "order": order,
            "limit": limit,
            "page": page,
        }

        try:
            response = self.session.post(
                f"{self.base_url}/search/spending_by_award/", json=payload, timeout=30
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return {"results": [], "page_metadata": {}}

    def get_geographic_spending(
        self, filters: Dict[str, Any], scope: str = "state"
    ) -> Dict[str, Any]:
        """
        Get geographic spending data using spending_by_geography endpoint.

        Args:
            filters: Dictionary of filters to apply
            scope: Geographic scope (state, county, district)

        Returns:
            Dictionary containing geographic spending data
        """
        payload = {"filters": filters, "scope": scope}

        try:
            response = self.session.post(
                f"{self.base_url}/search/spending_by_geography/",
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Geographic API request failed: {e}")
            return {"results": []}

    def get_spending_over_time(
        self, filters: Dict[str, Any], group: str = "month"
    ) -> Dict[str, Any]:
        """
        Get spending trends over time.

        Args:
            filters: Dictionary of filters to apply
            group: Time grouping (month, quarter, fiscal_year)

        Returns:
            Dictionary containing time series data
        """
        payload = {"filters": filters, "group": group}

        try:
            response = self.session.post(
                f"{self.base_url}/search/spending_over_time/", json=payload, timeout=30
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Time series API request failed: {e}")
            return {"results": []}

    def get_recipient_data(
        self, filters: Dict[str, Any], limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get recipient analysis data.

        Args:
            filters: Dictionary of filters to apply
            limit: Number of recipients to return

        Returns:
            Dictionary containing recipient data
        """
        payload = {"filters": filters, "category": "recipient", "limit": limit}

        try:
            response = self.session.post(
                f"{self.base_url}/search/spending_by_category/",
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Recipient API request failed: {e}")
            return {"results": []}

    def collect_paginated_data(
        self, filters: Dict[str, Any], max_pages: int = 10, delay: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Collect data across multiple pages with rate limiting.

        Args:
            filters: Dictionary of filters to apply
            max_pages: Maximum number of pages to collect
            delay: Delay between requests in seconds

        Returns:
            List of all collected records
        """
        all_results = []

        for page in range(1, max_pages + 1):
            print(f"Fetching page {page}/{max_pages}...")

            response = self.search_awards(filters=filters, page=page)
            results = response.get("results", [])

            if not results:
                print(f"No more results found at page {page}")
                break

            all_results.extend(results)

            # Rate limiting
            if page < max_pages:
                time.sleep(delay)

        print(f"Collected {len(all_results)} total records")
        return all_results

    def get_clean_energy_data(
        self, time_period: str = "ira_chips_period", max_pages: int = 5
    ) -> pd.DataFrame:
        """
        Convenience method to get clean energy funding data.

        Args:
            time_period: Time period key from DATE_RANGES
            max_pages: Maximum pages to collect

        Returns:
            DataFrame with clean energy funding data
        """
        # Build filters
        date_filter = self.build_date_filter(
            DATE_RANGES[time_period]["start"], DATE_RANGES[time_period]["end"]
        )
        keyword_filter = self.build_keyword_filter(CLEAN_ENERGY_KEYWORDS)

        filters = {**date_filter, **keyword_filter}

        # Collect data
        results = self.collect_paginated_data(filters, max_pages=max_pages)

        # Convert to DataFrame
        if results:
            return pd.DataFrame(results)
        else:
            return pd.DataFrame()
