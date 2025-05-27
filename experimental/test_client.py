#!/usr/bin/env python3

from src.data_collection.usaspending_client import USASpendingClient
from src.config.api_config import CLEAN_ENERGY_KEYWORDS, DATE_RANGES


def test_client():
    print("Testing USAspending client...")

    # Test the client with a small query
    client = USASpendingClient()

    # Build filters for a small test
    date_filter = client.build_date_filter(
        DATE_RANGES["ira_chips_period"]["start"], DATE_RANGES["ira_chips_period"]["end"]
    )
    keyword_filter = client.build_keyword_filter(
        CLEAN_ENERGY_KEYWORDS[:5]
    )  # Just first 5 keywords

    filters = {**date_filter, **keyword_filter}

    print("Testing search_awards with filters:", filters)

    # Add debugging to see the exact request
    import json

    # Manually add award_type_codes to see what happens (contracts only)
    filters["award_type_codes"] = ["A", "B", "C", "D"]
    print("Updated filters:", json.dumps(filters, indent=2))

    response = client.search_awards(filters=filters, limit=3)

    print("✅ Success! Found", len(response.get("results", [])), "results")
    if response.get("results"):
        print("Sample result:", response["results"][0].get("Recipient Name", "N/A"))
        print("Award Amount:", response["results"][0].get("Award Amount", "N/A"))


if __name__ == "__main__":
    test_client()
