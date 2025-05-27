#!/usr/bin/env python3
"""
Simple test script to verify USAspending API connection
"""

import requests
import json


def test_basic_connection():
    """Test basic API connection"""

    print("Testing USAspending API connection...")

    # Simple test endpoint
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

    # Simple test query for solar energy awards in 2023
    test_data = {
        "filters": {
            "keywords": ["solar"],
            "time_period": [{"start_date": "2023-01-01", "end_date": "2023-12-31"}],
            "award_type_codes": ["A", "B", "C", "D"],  # Required field: all award types
        },
        "fields": [
            "Award ID",
            "Recipient Name",
            "Award Amount",
            "Description",
            "Place of Performance State Code",
        ],
        "sort": "Award Amount",
        "order": "desc",
        "limit": 5,
        "page": 1,
    }

    try:
        print("Making API request...")
        response = requests.post(url, json=test_data, timeout=30)

        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")

        if response.status_code != 200:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"Response text: {response.text}")
            return False

        data = response.json()

        print("✅ API connection successful!")
        print(
            f"Total results available: {data.get('page_metadata', {}).get('total', 'Unknown')}"
        )
        print(f"Results returned: {len(data.get('results', []))}")

        if data.get("results"):
            print("\nSample results:")
            for i, result in enumerate(data["results"][:3], 1):
                print(
                    f"{i}. {result.get('Recipient Name', 'N/A')} - ${result.get('Award Amount', 0):,.2f}"
                )
                print(
                    f"   State: {result.get('Place of Performance State Code', 'N/A')}"
                )
                print(f"   Description: {result.get('Description', 'N/A')[:100]}...")
                print()

        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ API connection failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Failed to decode JSON response: {e}")
        print(f"Response text: {response.text}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_geographic_endpoint():
    """Test geographic spending endpoint"""

    print("\nTesting geographic spending endpoint...")

    url = "https://api.usaspending.gov/api/v2/search/spending_by_geography/"

    test_data = {
        "filters": {
            "keywords": ["renewable energy"],
            "time_period": [{"start_date": "2022-01-01", "end_date": "2023-12-31"}],
        },
        "scope": "place_of_performance",
        "geo_layer": "state",
    }

    try:
        response = requests.post(url, json=test_data, timeout=30)
        response.raise_for_status()

        data = response.json()

        print("✅ Geographic endpoint successful!")
        print(f"States with data: {len(data.get('results', []))}")

        if data.get("results"):
            # Sort by spending amount
            results = sorted(
                data["results"],
                key=lambda x: float(x.get("aggregated_amount", 0)),
                reverse=True,
            )

            print("\nTop 5 states by renewable energy spending:")
            for i, result in enumerate(results[:5], 1):
                state = result.get("shape_code", "Unknown")
                amount = float(result.get("aggregated_amount", 0))
                print(f"{i}. {state}: ${amount:,.2f}")

        return True

    except Exception as e:
        print(f"❌ Geographic endpoint failed: {e}")
        return False


def main():
    """Run all tests"""

    print("=" * 60)
    print("USAspending API Connection Test")
    print("=" * 60)

    # Test basic connection
    basic_success = test_basic_connection()

    # Test geographic endpoint
    geo_success = test_geographic_endpoint()

    print("\n" + "=" * 60)
    if basic_success and geo_success:
        print("🎉 All tests passed! API is ready for data collection.")
    else:
        print("⚠️  Some tests failed. Check your internet connection and try again.")
    print("=" * 60)


if __name__ == "__main__":
    main()
