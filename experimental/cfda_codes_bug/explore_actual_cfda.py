#!/usr/bin/env python3

from src.data_collection.usaspending_client import USASpendingClient
import requests


def explore_cfda_codes():
    client = USASpendingClient()

    print("Exploring what CFDA codes actually exist in USAspending...")

    # First, let's see what we get with no filters at all
    print("\n1. Testing with minimal filters (just grants, recent period)...")

    filters_minimal = {
        "time_period": [{"start_date": "2023-01-01", "end_date": "2024-12-31"}],
        "award_type_codes": ["02", "03", "04", "05"],  # Grant types
    }

    response = client.search_awards(filters=filters_minimal, limit=20)
    total = response.get("page_metadata", {}).get("total", 0)
    print(f"Total grants 2023-2024: {total:,}")

    if response.get("results"):
        print("\nCFDA codes found in recent grants:")
        cfda_counts = {}
        for r in response["results"]:
            cfda = r.get("CFDA Number", "N/A")
            title = r.get("CFDA Title", "N/A")
            if cfda not in cfda_counts:
                cfda_counts[cfda] = {"count": 0, "title": title}
            cfda_counts[cfda]["count"] += 1

        # Show top CFDA codes
        sorted_cfda = sorted(
            cfda_counts.items(), key=lambda x: x[1]["count"], reverse=True
        )
        for cfda, info in sorted_cfda[:10]:
            print(f"  {cfda}: {info['count']} grants - {info['title']}")

    # Now let's specifically look for Department of Energy (81.xxx) codes
    print("\n2. Searching for any Department of Energy (81.xxx) CFDA codes...")

    # Try a few known active DOE programs
    known_doe_codes = [
        "81.041",  # State Energy Program
        "81.042",  # Weatherization
        "81.087",  # Renewable Energy R&D
        "81.049",  # Office of Science Financial Assistance Program
        "81.022",  # Used Energy-Related Laboratory Equipment Grant
        "81.079",  # Regional Biomass Energy Programs
    ]

    for cfda_code in known_doe_codes:
        # Try with broader time range
        filters_doe = {
            "time_period": [{"start_date": "2015-01-01", "end_date": "2024-12-31"}],
            "cfda_numbers": [cfda_code],
            "award_type_codes": ["02", "03", "04", "05"],
        }

        try:
            response = client.search_awards(filters=filters_doe, limit=1)
            total = response.get("page_metadata", {}).get("total", 0)
            print(f"  CFDA {cfda_code}: {total} results (2015-2024)")

            if total > 0 and response.get("results"):
                sample = response["results"][0]
                print(f"    Title: {sample.get('CFDA Title', 'N/A')}")
                print(f"    Recipient: {sample.get('Recipient Name', 'N/A')}")
        except Exception as e:
            print(f"  CFDA {cfda_code}: Error - {e}")

    # Let's also try the autocomplete endpoint to see what CFDA codes exist
    print("\n3. Checking CFDA autocomplete endpoint...")
    try:
        autocomplete_url = "https://api.usaspending.gov/api/v2/autocomplete/cfda/"
        params = {"search_text": "81", "limit": 10}

        response = requests.get(autocomplete_url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print("CFDA codes starting with '81' found in autocomplete:")
            for item in data.get("results", []):
                print(
                    f"  {item.get('cfda_number', 'N/A')}: {item.get('cfda_title', 'N/A')}"
                )
        else:
            print(f"Autocomplete failed: {response.status_code}")
    except Exception as e:
        print(f"Autocomplete error: {e}")


if __name__ == "__main__":
    explore_cfda_codes()
