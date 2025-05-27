#!/usr/bin/env python3

from src.data_collection.usaspending_client import USASpendingClient


def test_cfda_search():
    client = USASpendingClient()

    # Test direct search for CFDA 81.041 (State Energy Program)
    filters = {
        "time_period": [{"start_date": "2022-08-16", "end_date": "2024-12-31"}],
        "cfda_numbers": ["81.041"],
        "award_type_codes": ["02", "03", "04", "05"],  # Grant types
    }

    print("Testing direct CFDA 81.041 search...")
    response = client.search_awards(filters=filters, limit=10)

    total = response.get("page_metadata", {}).get("total", 0)
    print(f"Total results for CFDA 81.041: {total}")

    if response.get("results"):
        print("\nSample results:")
        for i, r in enumerate(response["results"][:3], 1):
            print(f'{i}. CFDA: {r.get("CFDA Number", "N/A")}')
            print(f'   Title: {r.get("CFDA Title", "N/A")}')
            print(f'   Recipient: {r.get("Recipient Name", "N/A")}')
            print(f'   Amount: ${r.get("Award Amount", 0):,.2f}')
            print()
    else:
        print("No results found!")

    # Test a few more CFDA codes
    print("\n" + "=" * 60)
    print("Testing other energy CFDA codes...")

    test_codes = ["81.042", "81.087", "81.119", "81.086"]  # Sample from our list

    for cfda_code in test_codes:
        filters["cfda_numbers"] = [cfda_code]
        response = client.search_awards(filters=filters, limit=3)
        total = response.get("page_metadata", {}).get("total", 0)
        print(f"CFDA {cfda_code}: {total} results")

        if response.get("results"):
            sample = response["results"][0]
            print(f"  Sample: {sample.get('CFDA Title', 'N/A')}")

    # Also test without CFDA filter to see what we get
    print("\n" + "=" * 60)
    print("Testing search WITHOUT CFDA filter (just time period)...")

    filters_no_cfda = {
        "time_period": [{"start_date": "2022-08-16", "end_date": "2024-12-31"}],
        "award_type_codes": ["02", "03", "04", "05"],  # Grant types
    }

    response2 = client.search_awards(filters=filters_no_cfda, limit=5)
    total2 = response2.get("page_metadata", {}).get("total", 0)
    print(f"Total results without CFDA filter: {total2}")

    if response2.get("results"):
        print("\nSample results (no CFDA filter):")
        cfda_counts = {}
        for r in response2["results"]:
            cfda = r.get("CFDA Number", "N/A")
            cfda_counts[cfda] = cfda_counts.get(cfda, 0) + 1

        print("CFDA codes found:")
        for cfda, count in sorted(cfda_counts.items()):
            print(f"  {cfda}: {count} results")


if __name__ == "__main__":
    test_cfda_search()
