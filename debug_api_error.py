#!/usr/bin/env python3
"""
Debug script to identify the 422 error in the spending_by_award API endpoint.

This script tests different combinations of filters to identify what's causing
the 422 Unprocessable Entity error.
"""

import sys
import json
import requests
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.data_processor.api_client import USASpendingAPIClient
from src.config.api_config import (
    AWARD_TYPE_GROUPS,
    DEFAULT_AWARD_FIELDS,
)


def test_minimal_request():
    """Test the most minimal possible request."""
    print("🔍 Testing minimal API request...")

    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

    # Absolute minimal request
    minimal_payload = {
        "filters": {
            "time_period": [{"start_date": "2023-01-01", "end_date": "2023-12-31"}],
            "award_type_codes": ["A", "B", "C", "D"],
        },
        "fields": ["Award ID", "Recipient Name", "Award Amount"],
        "limit": 5,
        "page": 1,
    }

    print("Minimal payload:")
    print(json.dumps(minimal_payload, indent=2))

    try:
        response = requests.post(url, json=minimal_payload, timeout=30)
        print(f"Status code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(
                f"✅ Minimal request successful! Found {len(data.get('results', []))} results"
            )
            return True
        else:
            print(f"❌ Minimal request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_with_keywords():
    """Test adding keywords to the minimal request."""
    print("\n🔍 Testing with keywords...")

    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

    # Add keywords
    payload = {
        "filters": {
            "time_period": [{"start_date": "2023-01-01", "end_date": "2023-12-31"}],
            "award_type_codes": ["A", "B", "C", "D"],
            "keywords": ["solar"],  # Just one keyword
        },
        "fields": ["Award ID", "Recipient Name", "Award Amount"],
        "limit": 5,
        "page": 1,
    }

    print("Payload with keywords:")
    print(json.dumps(payload, indent=2))

    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(
                f"✅ Keywords request successful! Found {len(data.get('results', []))} results"
            )
            return True
        else:
            print(f"❌ Keywords request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_different_time_periods():
    """Test different time periods to see if that's the issue."""
    print("\n🔍 Testing different time periods...")

    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

    test_periods = [
        ("Recent", "2024-01-01", "2024-12-31"),
        ("IRA Period", "2022-08-16", "2024-12-31"),
        ("Pre-ARRA", "2007-01-01", "2009-02-16"),
        ("ARRA", "2009-02-17", "2012-12-31"),
    ]

    for period_name, start_date, end_date in test_periods:
        print(f"\n  Testing {period_name} ({start_date} to {end_date})...")

        payload = {
            "filters": {
                "time_period": [{"start_date": start_date, "end_date": end_date}],
                "award_type_codes": ["A", "B", "C", "D"],
            },
            "fields": ["Award ID", "Recipient Name", "Award Amount"],
            "limit": 5,
            "page": 1,
        }

        try:
            response = requests.post(url, json=payload, timeout=30)
            print(f"    Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                total = data.get("page_metadata", {}).get("total", 0)
                print(f"    ✅ Success! Total available: {total:,}")
            else:
                print(f"    ❌ Failed: {response.text[:200]}...")

        except Exception as e:
            print(f"    ❌ Error: {e}")


def test_award_type_groups():
    """Test different award type groups."""
    print("\n🔍 Testing different award type groups...")

    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

    for group_name, award_types in AWARD_TYPE_GROUPS.items():
        print(f"\n  Testing {group_name}: {award_types}")

        payload = {
            "filters": {
                "time_period": [{"start_date": "2023-01-01", "end_date": "2023-12-31"}],
                "award_type_codes": award_types,
            },
            "fields": ["Award ID", "Recipient Name", "Award Amount"],
            "limit": 5,
            "page": 1,
        }

        try:
            response = requests.post(url, json=payload, timeout=30)
            print(f"    Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                total = data.get("page_metadata", {}).get("total", 0)
                print(f"    ✅ Success! Total available: {total:,}")
            else:
                print(f"    ❌ Failed: {response.text[:200]}...")

        except Exception as e:
            print(f"    ❌ Error: {e}")


def test_client_vs_direct():
    """Compare our client implementation with direct requests."""
    print("\n🔍 Comparing client vs direct requests...")

    # Test with our client
    print("\n  Testing with USASpendingAPIClient...")
    client = USASpendingAPIClient()

    date_filter = client.build_date_filter("2023-01-01", "2023-12-31")
    keyword_filter = client.build_keyword_filter(["solar"])

    filters = {
        **date_filter,
        **keyword_filter,
        "award_type_codes": AWARD_TYPE_GROUPS["contracts"],
    }

    print("Client filters:")
    print(json.dumps(filters, indent=2))

    try:
        response = client.search_awards(filters=filters, limit=5)
        print(
            f"    ✅ Client request successful! Found {len(response.get('results', []))} results"
        )
    except Exception as e:
        print(f"    ❌ Client request failed: {e}")

    # Test direct equivalent
    print("\n  Testing direct equivalent...")
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

    direct_payload = {
        "filters": filters,
        "fields": DEFAULT_AWARD_FIELDS,
        "sort": "Award Amount",
        "order": "desc",
        "limit": 5,
        "page": 1,
    }

    print("Direct payload:")
    print(json.dumps(direct_payload, indent=2))

    try:
        response = requests.post(url, json=direct_payload, timeout=30)
        print(f"    Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(
                f"    ✅ Direct request successful! Found {len(data.get('results', []))} results"
            )
        else:
            print(f"    ❌ Direct request failed: {response.text}")

    except Exception as e:
        print(f"    ❌ Error: {e}")


def test_field_combinations():
    """Test different field combinations."""
    print("\n🔍 Testing different field combinations...")

    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

    field_tests = [
        ("Minimal", ["Award ID", "Recipient Name", "Award Amount"]),
        (
            "Standard",
            ["Award ID", "Recipient Name", "Award Amount", "Start Date", "End Date"],
        ),
        ("Default", DEFAULT_AWARD_FIELDS),
    ]

    base_payload = {
        "filters": {
            "time_period": [{"start_date": "2023-01-01", "end_date": "2023-12-31"}],
            "award_type_codes": ["A", "B", "C", "D"],
        },
        "limit": 5,
        "page": 1,
    }

    for test_name, fields in field_tests:
        print(f"\n  Testing {test_name} fields ({len(fields)} fields)...")

        payload = {**base_payload, "fields": fields}

        try:
            response = requests.post(url, json=payload, timeout=30)
            print(f"    Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"    ✅ Success! Found {len(data.get('results', []))} results")
            else:
                print(f"    ❌ Failed: {response.text[:200]}...")

        except Exception as e:
            print(f"    ❌ Error: {e}")


def main():
    """Run all debug tests."""
    print("🚀 Debugging USAspending API 422 errors\n")

    # Test 1: Minimal request
    minimal_works = test_minimal_request()

    # Test 2: With keywords
    keywords_work = test_with_keywords()

    # Test 3: Different time periods
    test_different_time_periods()

    # Test 4: Different award types
    test_award_type_groups()

    # Test 5: Client vs direct
    test_client_vs_direct()

    # Test 6: Field combinations
    test_field_combinations()

    # Summary
    print("\n📊 Debug Summary:")
    print(f"   Minimal request: {'✅ WORKS' if minimal_works else '❌ FAILS'}")
    print(f"   With keywords: {'✅ WORKS' if keywords_work else '❌ FAILS'}")

    if minimal_works:
        print(
            "\n💡 The API is working. The issue is likely in our filter construction."
        )
    else:
        print("\n⚠️  Even minimal requests are failing. This might be an API issue.")


if __name__ == "__main__":
    main()
