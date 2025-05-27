#!/usr/bin/env python3
"""
Data Consolidation Script

Consolidates all collected clean energy funding data into a single,
well-organized dataset for dashboard consumption.

This script:
1. Combines all award data from different time periods and sources
2. Adds metadata columns for easy filtering and analysis
3. Standardizes data formats and column names
4. Creates summary statistics and indexes
5. Exports in multiple formats for different use cases
"""

import pandas as pd
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Any
import warnings

warnings.filterwarnings("ignore")


class DataConsolidator:
    """
    Consolidates all collected clean energy data into unified datasets.
    """

    def __init__(self, data_dir: str = "data/collected"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path("cache")
        self.output_dir.mkdir(exist_ok=True)

        # Create subdirectories
        (self.output_dir / "datasets").mkdir(exist_ok=True)
        (self.output_dir / "summaries").mkdir(exist_ok=True)
        (self.output_dir / "indexes").mkdir(exist_ok=True)

        print("🚀 Data Consolidator initialized")
        print(f"📁 Input directory: {self.data_dir}")
        print(f"📁 Output directory: {self.output_dir}")

    def consolidate_awards_data(self) -> pd.DataFrame:
        """
        Consolidate all awards data into a single DataFrame.

        Returns:
            Consolidated DataFrame with all award records
        """
        print("\n📊 Consolidating awards data...")

        awards_dir = self.data_dir / "awards"
        all_awards = []

        # Define data source categories
        data_sources = {
            "time_period": [
                "awards_pre_arra_combined",
                "awards_arra_period_combined",
                "awards_post_arra_pre_ira_combined",
                "awards_ira_chips_period_combined",
                "awards_full_period_combined",
            ],
            "cfda_specific": ["awards_by_cfda_combined"],
            "keyword_specific": [
                f
                for f in awards_dir.glob("keyword_*.parquet")
                if f.stem not in ["awards_by_cfda_combined"]
            ],
        }

        # Process time period data
        for file_stem in data_sources["time_period"]:
            file_path = awards_dir / f"{file_stem}.parquet"
            if file_path.exists():
                print(f"  📈 Loading {file_stem}...")
                df = pd.read_parquet(file_path)

                # Add metadata
                df["data_source"] = "time_period"
                df["source_file"] = file_stem

                # Extract time period from filename
                if "pre_arra" in file_stem:
                    df["time_period_category"] = "pre_arra"
                elif "arra_period" in file_stem:
                    df["time_period_category"] = "arra_period"
                elif "post_arra_pre_ira" in file_stem:
                    df["time_period_category"] = "post_arra_pre_ira"
                elif "ira_chips" in file_stem:
                    df["time_period_category"] = "ira_chips_period"
                elif "full_period" in file_stem:
                    df["time_period_category"] = "full_period"
                else:
                    df["time_period_category"] = "unknown"

                all_awards.append(df)
                print(f"    ✅ Added {len(df):,} records from {file_stem}")

        # Process CFDA-specific data
        for file_stem in data_sources["cfda_specific"]:
            file_path = awards_dir / f"{file_stem}.parquet"
            if file_path.exists():
                print(f"  🏛️  Loading {file_stem}...")
                df = pd.read_parquet(file_path)

                # Add metadata
                df["data_source"] = "cfda_specific"
                df["source_file"] = file_stem
                df["time_period_category"] = "cfda_analysis"

                all_awards.append(df)
                print(f"    ✅ Added {len(df):,} records from {file_stem}")

        # Process keyword-specific data
        keyword_files = list(awards_dir.glob("keyword_*.parquet"))
        for file_path in keyword_files:
            print(f"  🔍 Loading {file_path.name}...")
            df = pd.read_parquet(file_path)

            # Add metadata
            df["data_source"] = "keyword_specific"
            df["source_file"] = file_path.stem
            df["time_period_category"] = "keyword_analysis"

            # Extract keyword from filename
            keyword = file_path.stem.replace("keyword_", "").replace("_", " ")
            df["primary_keyword"] = keyword

            all_awards.append(df)
            print(f"    ✅ Added {len(df):,} records from {file_path.name}")

        # Combine all data
        if all_awards:
            print(f"\n🔄 Combining {len(all_awards)} datasets...")
            consolidated_df = pd.concat(all_awards, ignore_index=True)

            # Remove duplicates based on Award ID
            initial_count = len(consolidated_df)
            if "Award ID" in consolidated_df.columns:
                consolidated_df = consolidated_df.drop_duplicates(
                    subset=["Award ID"], keep="first"
                )
                dedup_count = len(consolidated_df)
                print(f"  🧹 Removed {initial_count - dedup_count:,} duplicate records")

            # Standardize and enhance data
            consolidated_df = self._standardize_awards_data(consolidated_df)

            print(
                f"✅ Consolidated awards data: {len(consolidated_df):,} unique records"
            )
            return consolidated_df
        else:
            print("❌ No awards data found to consolidate")
            return pd.DataFrame()

    def _standardize_awards_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize and enhance the awards data.

        Args:
            df: Raw consolidated DataFrame

        Returns:
            Standardized DataFrame
        """
        print("  🔧 Standardizing data formats...")

        # Standardize column names
        column_mapping = {
            "Award Amount": "award_amount",
            "Start Date": "start_date",
            "End Date": "end_date",
            "Award ID": "award_id",
            "Recipient Name": "recipient_name",
            "Awarding Agency": "awarding_agency",
            "Awarding Sub Agency": "awarding_sub_agency",
            "Award Type": "award_type",
            "Funding Agency": "funding_agency",
            "Funding Sub Agency": "funding_sub_agency",
            "Place of Performance State Code": "performance_state_code",
            "Place of Performance State": "performance_state",
            "Recipient Location State Code": "recipient_state_code",
            "Description": "description",
        }

        # Rename columns that exist
        existing_columns = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df.rename(columns=existing_columns)

        # Convert data types
        if "award_amount" in df.columns:
            df["award_amount"] = pd.to_numeric(df["award_amount"], errors="coerce")

        if "start_date" in df.columns:
            df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")

        if "end_date" in df.columns:
            df["end_date"] = pd.to_datetime(df["end_date"], errors="coerce")

        # Add derived columns
        if "start_date" in df.columns:
            df["fiscal_year"] = df["start_date"].dt.year
            df["quarter"] = df["start_date"].dt.quarter
            df["month"] = df["start_date"].dt.month
            df["year_month"] = df["start_date"].dt.to_period("M").astype(str)

        # Add award size categories
        if "award_amount" in df.columns:
            df["award_size_category"] = pd.cut(
                df["award_amount"],
                bins=[0, 100000, 1000000, 10000000, 100000000, float("inf")],
                labels=[
                    "Small (<$100K)",
                    "Medium ($100K-$1M)",
                    "Large ($1M-$10M)",
                    "Very Large ($10M-$100M)",
                    "Mega (>$100M)",
                ],
                include_lowest=True,
            )

        # Clean and categorize technology types
        if "description" in df.columns:
            df["technology_category"] = df["description"].apply(
                self._categorize_technology
            )

        # Add data collection timestamp
        df["data_collected_at"] = datetime.now().isoformat()

        return df

    def _categorize_technology(self, description: str) -> str:
        """
        Categorize technology based on description text.

        Args:
            description: Award description text

        Returns:
            Technology category
        """
        if pd.isna(description):
            return "Unknown"

        description_lower = str(description).lower()

        # Define technology keywords
        tech_categories = {
            "Solar": ["solar", "photovoltaic", "pv"],
            "Wind": ["wind", "turbine"],
            "Battery/Storage": ["battery", "storage", "energy storage"],
            "Electric Vehicles": ["electric vehicle", "ev", "charging"],
            "Smart Grid": ["smart grid", "grid modernization"],
            "Hydrogen": ["hydrogen", "fuel cell"],
            "Geothermal": ["geothermal"],
            "Biomass": ["biomass", "biofuel"],
            "Nuclear": ["nuclear"],
            "Hydroelectric": ["hydro", "hydroelectric"],
            "Carbon Capture": ["carbon capture", "ccs"],
            "Energy Efficiency": ["efficiency", "conservation"],
        }

        for category, keywords in tech_categories.items():
            if any(keyword in description_lower for keyword in keywords):
                return category

        return "Other Clean Energy"

    def consolidate_geographic_data(self) -> Dict[str, pd.DataFrame]:
        """
        Consolidate geographic data.

        Returns:
            Dictionary with state and county geographic data
        """
        print("\n🗺️  Consolidating geographic data...")

        geographic_dir = self.data_dir / "geographic"
        geographic_data = {}

        for geo_level in ["state", "county"]:
            file_path = geographic_dir / f"geographic_{geo_level}.parquet"
            if file_path.exists():
                print(f"  📍 Loading {geo_level} data...")
                df = pd.read_parquet(file_path)

                # Standardize columns
                if "shape_code" in df.columns:
                    df = df.rename(columns={"shape_code": f"{geo_level}_code"})
                if "display_name" in df.columns:
                    df = df.rename(columns={"display_name": f"{geo_level}_name"})
                if "aggregated_amount" in df.columns:
                    df = df.rename(columns={"aggregated_amount": "total_funding"})

                # Add per capita calculations
                if "population" in df.columns and "total_funding" in df.columns:
                    df["funding_per_capita"] = df["total_funding"] / df["population"]

                geographic_data[geo_level] = df
                print(f"    ✅ Added {len(df):,} {geo_level} records")

        return geographic_data

    def consolidate_time_series_data(self) -> Dict[str, pd.DataFrame]:
        """
        Consolidate time series data.

        Returns:
            Dictionary with different time granularity data
        """
        print("\n📈 Consolidating time series data...")

        time_series_dir = self.data_dir / "time_series"
        time_series_data = {}

        for granularity in ["month", "quarter", "fiscal_year"]:
            file_path = time_series_dir / f"time_series_{granularity}.parquet"
            if file_path.exists():
                print(f"  📊 Loading {granularity} data...")
                df = pd.read_parquet(file_path)

                # Standardize time columns
                if "time_period" in df.columns:
                    df["time_period"] = pd.to_datetime(
                        df["time_period"], errors="coerce"
                    )

                time_series_data[granularity] = df
                print(f"    ✅ Added {len(df):,} {granularity} records")

        return time_series_data

    def create_summary_statistics(
        self,
        awards_df: pd.DataFrame,
        geographic_data: Dict[str, pd.DataFrame],
        time_series_data: Dict[str, pd.DataFrame],
    ) -> Dict[str, Any]:
        """
        Create comprehensive summary statistics.

        Args:
            awards_df: Consolidated awards data
            geographic_data: Geographic data by level
            time_series_data: Time series data by granularity

        Returns:
            Dictionary with summary statistics
        """
        print("\n📊 Creating summary statistics...")

        summary = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "total_records": len(awards_df),
                "data_sources": awards_df["data_source"].value_counts().to_dict()
                if "data_source" in awards_df.columns
                else {},
                "time_period_coverage": {
                    "start_date": awards_df["start_date"].min().isoformat()
                    if "start_date" in awards_df.columns
                    and not awards_df["start_date"].isna().all()
                    else None,
                    "end_date": awards_df["start_date"].max().isoformat()
                    if "start_date" in awards_df.columns
                    and not awards_df["start_date"].isna().all()
                    else None,
                },
            },
            "funding_summary": {},
            "geographic_summary": {},
            "technology_summary": {},
            "temporal_summary": {},
        }

        # Funding summary
        if "award_amount" in awards_df.columns:
            funding_stats = awards_df["award_amount"].describe()
            summary["funding_summary"] = {
                "total_funding": float(awards_df["award_amount"].sum()),
                "average_award": float(awards_df["award_amount"].mean()),
                "median_award": float(awards_df["award_amount"].median()),
                "largest_award": float(awards_df["award_amount"].max()),
                "smallest_award": float(awards_df["award_amount"].min()),
                "awards_over_1m": int((awards_df["award_amount"] > 1000000).sum()),
                "awards_over_10m": int((awards_df["award_amount"] > 10000000).sum()),
                "awards_over_100m": int((awards_df["award_amount"] > 100000000).sum()),
            }

        # Geographic summary
        if "state" in geographic_data:
            state_df = geographic_data["state"]
            if "total_funding" in state_df.columns:
                summary["geographic_summary"] = {
                    "states_with_funding": len(state_df),
                    "top_state": state_df.loc[
                        state_df["total_funding"].idxmax(), "state_name"
                    ]
                    if "state_name" in state_df.columns
                    else "Unknown",
                    "total_state_funding": float(state_df["total_funding"].sum()),
                    "average_state_funding": float(state_df["total_funding"].mean()),
                }

        # Technology summary
        if "technology_category" in awards_df.columns:
            tech_summary = (
                awards_df.groupby("technology_category")["award_amount"]
                .agg(["count", "sum"])
                .to_dict()
            )
            summary["technology_summary"] = {
                "technology_distribution": tech_summary,
                "top_technology": awards_df.groupby("technology_category")[
                    "award_amount"
                ]
                .sum()
                .idxmax(),
            }

        # Temporal summary
        if "fiscal_year" in awards_df.columns:
            yearly_summary = (
                awards_df.groupby("fiscal_year")["award_amount"]
                .agg(["count", "sum"])
                .to_dict()
            )
            summary["temporal_summary"] = {
                "yearly_distribution": yearly_summary,
                "peak_year": awards_df.groupby("fiscal_year")["award_amount"]
                .sum()
                .idxmax(),
            }

        return summary

    def save_consolidated_data(
        self,
        awards_df: pd.DataFrame,
        geographic_data: Dict[str, pd.DataFrame],
        time_series_data: Dict[str, pd.DataFrame],
        summary: Dict[str, Any],
    ):
        """
        Save all consolidated data in multiple formats.

        Args:
            awards_df: Consolidated awards data
            geographic_data: Geographic data
            time_series_data: Time series data
            summary: Summary statistics
        """
        print("\n💾 Saving consolidated data...")

        # Save main awards dataset
        datasets_dir = self.output_dir / "datasets"

        print("  📊 Saving main awards dataset...")
        awards_df.to_parquet(
            datasets_dir / "clean_energy_awards_consolidated.parquet", index=False
        )
        awards_df.to_csv(
            datasets_dir / "clean_energy_awards_consolidated.csv", index=False
        )

        # Save a smaller sample for quick loading
        sample_df = awards_df.sample(n=min(1000, len(awards_df)), random_state=42)
        sample_df.to_parquet(
            datasets_dir / "clean_energy_awards_sample.parquet", index=False
        )
        sample_df.to_csv(datasets_dir / "clean_energy_awards_sample.csv", index=False)

        # Save geographic data
        print("  🗺️  Saving geographic data...")
        for level, df in geographic_data.items():
            df.to_parquet(
                datasets_dir / f"geographic_{level}_consolidated.parquet", index=False
            )
            df.to_csv(
                datasets_dir / f"geographic_{level}_consolidated.csv", index=False
            )

        # Save time series data
        print("  📈 Saving time series data...")
        for granularity, df in time_series_data.items():
            df.to_parquet(
                datasets_dir / f"time_series_{granularity}_consolidated.parquet",
                index=False,
            )
            df.to_csv(
                datasets_dir / f"time_series_{granularity}_consolidated.csv",
                index=False,
            )

        # Save summary statistics
        print("  📋 Saving summary statistics...")
        summaries_dir = self.output_dir / "summaries"

        with open(summaries_dir / "data_summary.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)

        # Create data catalog
        catalog = {
            "datasets": {
                "main_awards": {
                    "file": "datasets/clean_energy_awards_consolidated.parquet",
                    "description": "Complete consolidated clean energy awards dataset",
                    "records": len(awards_df),
                    "size_mb": round(
                        awards_df.memory_usage(deep=True).sum() / 1024 / 1024, 2
                    ),
                },
                "sample_awards": {
                    "file": "datasets/clean_energy_awards_sample.parquet",
                    "description": "Sample of 1000 awards for quick testing",
                    "records": len(sample_df),
                    "size_mb": round(
                        sample_df.memory_usage(deep=True).sum() / 1024 / 1024, 2
                    ),
                },
            },
            "geographic": {
                level: {
                    "file": f"datasets/geographic_{level}_consolidated.parquet",
                    "description": f"Geographic spending data at {level} level",
                    "records": len(df),
                }
                for level, df in geographic_data.items()
            },
            "time_series": {
                granularity: {
                    "file": f"datasets/time_series_{granularity}_consolidated.parquet",
                    "description": f"Time series data at {granularity} granularity",
                    "records": len(df),
                }
                for granularity, df in time_series_data.items()
            },
            "summary": {
                "file": "summaries/data_summary.json",
                "description": "Comprehensive summary statistics",
            },
        }

        with open(self.output_dir / "data_catalog.json", "w") as f:
            json.dump(catalog, f, indent=2)

        print(f"✅ All data saved to {self.output_dir}")

    def run_consolidation(self):
        """
        Run the complete data consolidation process.
        """
        print("🚀 Starting comprehensive data consolidation...\n")

        # Step 1: Consolidate awards data
        awards_df = self.consolidate_awards_data()

        # Step 2: Consolidate geographic data
        geographic_data = self.consolidate_geographic_data()

        # Step 3: Consolidate time series data
        time_series_data = self.consolidate_time_series_data()

        # Step 4: Create summary statistics
        summary = self.create_summary_statistics(
            awards_df, geographic_data, time_series_data
        )

        # Step 5: Save everything
        self.save_consolidated_data(
            awards_df, geographic_data, time_series_data, summary
        )

        # Print final summary
        print("\n🎉 Data consolidation complete!")
        print(f"📊 Total awards: {len(awards_df):,}")
        print(
            f"💰 Total funding: ${summary['funding_summary'].get('total_funding', 0):,.2f}"
        )
        print(f"🗺️  Geographic levels: {list(geographic_data.keys())}")
        print(f"📈 Time series granularities: {list(time_series_data.keys())}")
        print(f"📁 Output directory: {self.output_dir}")

        return {
            "awards": awards_df,
            "geographic": geographic_data,
            "time_series": time_series_data,
            "summary": summary,
        }


def main():
    """Main function to run data consolidation."""
    consolidator = DataConsolidator()
    results = consolidator.run_consolidation()

    print("\n💡 Next steps:")
    print("1. Review the consolidated data in cache/")
    print("2. Check data_catalog.json for file descriptions")
    print("3. Update dashboard to use consolidated data")
    print("4. Test dashboard with new data structure")

    return results


if __name__ == "__main__":
    main()
