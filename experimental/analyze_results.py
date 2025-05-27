#!/usr/bin/env python3

import pandas as pd


def analyze_clean_energy_results():
    df = pd.read_csv("data/raw/broader_clean_energy_search.csv")

    print("=== CLEAN ENERGY AWARDS ANALYSIS ===")
    print(f"Total awards found: {len(df)}")
    print(f'Total funding: ${df["Award Amount"].sum():,.0f}')
    print()

    print("Top 5 awards by amount:")
    top5 = df.nlargest(5, "Award Amount")[
        ["Recipient Name", "Award Amount", "Description"]
    ]
    for i, (_, row) in enumerate(top5.iterrows(), 1):
        print(f'{i}. {row["Recipient Name"]}')
        print(f'   Amount: ${row["Award Amount"]:,.0f}')
        print(f'   Description: {row["Description"][:80]}...')
        print()

    print("Awards by state:")
    state_counts = df["Place of Performance State Code"].value_counts().head(10)
    for state, count in state_counts.items():
        if state is not None and str(state) != "nan":
            print(f"  {state}: {count} awards")

    print("\nAwarding agencies:")
    agency_counts = df["Awarding Agency"].value_counts().head(5)
    for agency, count in agency_counts.items():
        print(f"  {agency}: {count} awards")

    print("\nSearch keywords that worked:")
    keyword_counts = df["search_keyword"].value_counts()
    for keyword, count in keyword_counts.items():
        print(f'  "{keyword}": {count} awards')

    print("\nSample descriptions:")
    for i, desc in enumerate(df["Description"].dropna().head(3), 1):
        print(f"{i}. {desc[:100]}...")


if __name__ == "__main__":
    analyze_clean_energy_results()
