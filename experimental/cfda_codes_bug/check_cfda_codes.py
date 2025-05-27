#!/usr/bin/env python3

from src.config.api_config import ENERGY_CFDA_CODES

print("All Energy CFDA Codes we have:")
for i, code in enumerate(ENERGY_CFDA_CODES, 1):
    print(f"{i:2d}. {code}")

print(f"\nTotal: {len(ENERGY_CFDA_CODES)} codes")

# Let's also test if these codes exist in the API at all
print("\n" + "=" * 50)
print("Testing if these CFDA codes exist in the API...")

from src.data_collection.usaspending_client import USASpendingClient

client = USASpendingClient()

# Test with a broader time range to see if the codes exist at all
filters_broad = {
    "time_period": [{"start_date": "2020-01-01", "end_date": "2024-12-31"}],
    "award_type_codes": ["02", "03", "04", "05"],  # All grant types
}

print("Testing first 5 CFDA codes with broader time range (2020-2024)...")
for cfda_code in ENERGY_CFDA_CODES[:5]:
    filters_broad["cfda_numbers"] = [cfda_code]
    try:
        response = client.search_awards(filters=filters_broad, limit=1)
        total = response.get("page_metadata", {}).get("total", 0)
        print(f"CFDA {cfda_code}: {total} results")
        if total > 0 and response.get("results"):
            sample = response["results"][0]
            print(f"  Title: {sample.get('CFDA Title', 'N/A')}")
    except Exception as e:
        print(f"CFDA {cfda_code}: Error - {e}")
