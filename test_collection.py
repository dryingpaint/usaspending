#!/usr/bin/env python3
"""
Quick test script to verify the comprehensive data collection setup.

This script runs a minimal test to ensure the API client and collection
process work correctly before running the full comprehensive collection.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.data_processor.api_client import USASpendingAPIClient
from src.config.api_config import DATE_RANGES, AWARD_TYPE_GROUPS


def test_api_connection():
    """Test basic API connection and functionality."""
    print("🔍 Testing USAspending API connection...")

    client = USASpendingAPIClient()

    # Test with a simple query
    date_filter = client.build_date_filter(
        DATE_RANGES["ira_chips_period"]["start"], DATE_RANGES["ira_chips_period"]["end"]
    )
    keyword_filter = client.build_keyword_filter(["solar"])

    filters = {
        **date_filter,
        **keyword_filter,
        "award_type_codes": AWARD_TYPE_GROUPS["contracts"],
    }

    try:
        response = client.search_awards(filters=filters, limit=5)

        if response.get("results"):
            print("✅ API connection successful!")
            print(f"📊 Found {len(response['results'])} sample results")
            print(
                f"🔢 Total available: {response.get('page_metadata', {}).get('total', 'Unknown')}"
            )

            # Show sample result
            sample = response["results"][0]
            print("\n📋 Sample result:")
            print(f"   Recipient: {sample.get('Recipient Name', 'N/A')}")
            print(f"   Amount: ${sample.get('Award Amount', 0):,.2f}")
            print(f"   State: {sample.get('Place of Performance State Code', 'N/A')}")

            return True
        else:
            print("❌ No results returned from API")
            return False

    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False


def test_collection_class():
    """Test the ComprehensiveDataCollector class."""
    print("\n🧪 Testing ComprehensiveDataCollector class...")

    try:
        from collect_all_clean_energy_data import ComprehensiveDataCollector

        # Initialize with test directory
        collector = ComprehensiveDataCollector(output_dir="data/test_collection")

        print("✅ ComprehensiveDataCollector initialized successfully")
        print(f"📁 Test output directory: {collector.output_dir}")

        # Test a small collection
        print("\n🔬 Running mini collection test...")

        # Create a client for testing
        client = USASpendingAPIClient()

        # Test just one small collection
        date_filter = client.build_date_filter(
            "2023-01-01",
            "2023-03-31",  # Just Q1 2023
        )
        keyword_filter = client.build_keyword_filter(["solar"])

        filters = {
            **date_filter,
            **keyword_filter,
            "award_type_codes": AWARD_TYPE_GROUPS["contracts"],
        }

        results = client.collect_paginated_data(
            filters=filters,
            max_pages=2,  # Just 2 pages
            delay=0.5,
        )

        if results:
            print(f"✅ Mini collection successful: {len(results)} records")

            # Test saving data
            import pandas as pd

            df = pd.DataFrame(results)
            success = collector.save_data(df, "test_data", "awards")

            if success:
                print("✅ Data saving test successful")
            else:
                print("❌ Data saving test failed")
                return False
        else:
            print("⚠️  Mini collection returned no results (this may be normal)")

        # Test the fixed geographic API
        print("\n🗺️  Testing geographic API fix...")
        try:
            geo_response = client.get_geographic_spending(
                filters=filters, geo_layer="state", scope="place_of_performance"
            )

            if geo_response.get("results"):
                print(
                    f"✅ Geographic API test successful: {len(geo_response['results'])} geographic results"
                )
                print(f"📍 Sample: {geo_response['results'][0]}")
            else:
                print("⚠️  Geographic API returned no results (this may be normal)")

        except Exception as e:
            print(f"❌ Geographic API test failed: {e}")
            return False

        return True

    except Exception as e:
        print(f"❌ Collection class test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Running comprehensive data collection tests\n")

    # Test 1: API connection
    api_test = test_api_connection()

    # Test 2: Collection class
    collection_test = test_collection_class()

    # Summary
    print("\n📊 Test Results:")
    print(f"   API Connection: {'✅ PASS' if api_test else '❌ FAIL'}")
    print(f"   Collection Class: {'✅ PASS' if collection_test else '❌ FAIL'}")

    if api_test and collection_test:
        print("\n🎉 All tests passed! Ready to run comprehensive collection.")
        print("\n💡 To run the full collection:")
        print("   python collect_all_clean_energy_data.py --quick")
        print("   python collect_all_clean_energy_data.py  # Full collection")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")

    return api_test and collection_test


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
