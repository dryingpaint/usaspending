#!/usr/bin/env python3
"""
Debug script for the spending_by_geography API endpoint.

Based on the official USAspending API documentation, this script tests
the correct format for geographic spending requests.
"""

import sys
import json
import requests
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.data_processor.api_client import USASpendingAPIClient
from src.config.api_config import DATE_RANGES


def test_geographic_endpoint_direct():
    """Test the geographic endpoint with direct requests using correct format."""
    print("🔍 Testing spending_by_geography endpoint directly...")

    url = "https://api.usaspending.gov/api/v2/search/spending_by_geography/"

    # Based on the official documentation, the correct format is:
    # https://github.com/fedspendingtransparency/usaspending-api/blob/master/usaspending_api/api_contracts/contracts/v2/search/spending_by_geography.md

    test_payloads = [
        {
            "name": "Basic state-level request",
            "payload": {
                "scope": "place_of_performance",
                "geo_layer": "state",
                "filters": {
                    "time_period": [
                        {"start_date": "2023-01-01", "end_date": "2023-12-31"}
                    ],
                    "keywords": ["solar"],
                },
            },
        },
        {
            "name": "County-level request",
            "payload": {
                "scope": "place_of_performance",
                "geo_layer": "county",
                "filters": {
                    "time_period": [
                        {"start_date": "2023-01-01", "end_date": "2023-12-31"}
                    ],
                    "keywords": ["renewable energy"],
                },
            },
        },
        {
            "name": "Recipient location scope",
            "payload": {
                "scope": "recipient_location",
                "geo_layer": "state",
                "filters": {
                    "time_period": [
                        {"start_date": "2023-01-01", "end_date": "2023-12-31"}
                    ],
                    "keywords": ["clean energy"],
                },
            },
        },
        {
            "name": "With award type codes",
            "payload": {
                "scope": "place_of_performance",
                "geo_layer": "state",
                "filters": {
                    "time_period": [
                        {"start_date": "2023-01-01", "end_date": "2023-12-31"}
                    ],
                    "keywords": ["solar"],
                    "award_type_codes": ["A", "B", "C", "D"],
                },
            },
        },
    ]

    for test in test_payloads:
        print(f"\n  🧪 Testing: {test['name']}")
        print(f"     Payload: {json.dumps(test['payload'], indent=6)}")

        try:
            response = requests.post(
                url,
                json=test["payload"],
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            print(f"     Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                results_count = len(data.get("results", []))
                print(f"     ✅ Success! Found {results_count} geographic results")

                if results_count > 0:
                    sample = data["results"][0]
                    print(f"     Sample: {sample}")

            else:
                print(f"     ❌ Failed: {response.text[:200]}...")

        except Exception as e:
            print(f"     ❌ Error: {e}")


def test_our_client_method():
    """Test our current client implementation."""
    print("\n🔍 Testing our current client implementation...")

    client = USASpendingAPIClient()

    # Build filters the way our client does
    date_filter = client.build_date_filter(
        DATE_RANGES["ira_chips_period"]["start"], DATE_RANGES["ira_chips_period"]["end"]
    )
    keyword_filter = client.build_keyword_filter(["solar"])

    filters = {**date_filter, **keyword_filter}

    print(f"  Our filters: {json.dumps(filters, indent=4)}")

    try:
        response = client.get_geographic_spending(filters=filters, scope="state")
        print(
            f"  ✅ Client method successful! Found {len(response.get('results', []))} results"
        )

    except Exception as e:
        print(f"  ❌ Client method failed: {e}")


def test_fixed_client_method():
    """Test a corrected version of our client method."""
    print("\n🔍 Testing corrected client method...")

    # The issue is likely that our client method doesn't format the request correctly
    # for the spending_by_geography endpoint

    url = "https://api.usaspending.gov/api/v2/search/spending_by_geography/"

    # Correct format based on documentation
    payload = {
        "scope": "place_of_performance",  # Required
        "geo_layer": "state",  # Required
        "filters": {  # Required - AdvancedFilterObject
            "time_period": [{"start_date": "2022-08-16", "end_date": "2024-12-31"}],
            "keywords": ["solar", "wind", "renewable energy"],
        },
    }

    print(f"  Corrected payload: {json.dumps(payload, indent=4)}")

    try:
        response = requests.post(
            url, json=payload, headers={"Content-Type": "application/json"}, timeout=30
        )

        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            results_count = len(data.get("results", []))
            print(f"  ✅ Corrected method successful! Found {results_count} results")

            if results_count > 0:
                sample = data["results"][0]
                print(f"  Sample result: {sample}")

        else:
            print(f"  ❌ Failed: {response.text}")

    except Exception as e:
        print(f"  ❌ Error: {e}")


def main():
    """Run all geographic API tests."""
    print("🚀 Debugging spending_by_geography API endpoint\n")

    # Test 1: Direct requests with correct format
    test_geographic_endpoint_direct()

    # Test 2: Our current client method
    test_our_client_method()

    # Test 3: Corrected client method
    test_fixed_client_method()

    print("\n📋 Summary:")
    print("The issue is likely in how we're formatting the request payload.")
    print("The spending_by_geography endpoint requires:")
    print("  - 'scope': 'place_of_performance' or 'recipient_location'")
    print("  - 'geo_layer': 'state', 'county', or 'district'")
    print("  - 'filters': AdvancedFilterObject (same as spending_by_award)")


if __name__ == "__main__":
    main()
