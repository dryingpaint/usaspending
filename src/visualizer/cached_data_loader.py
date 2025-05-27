#!/usr/bin/env python3
"""
Cached Data Loader

Loads pre-collected and consolidated clean energy data for dashboard consumption.
This replaces live API calls with fast local data access.

Benefits:
- No API rate limits or 422 errors
- Instant loading (vs 30+ second API calls)
- Consistent data across all users
- Offline capability
- Better performance and reliability
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import warnings

warnings.filterwarnings("ignore")


class CachedDataLoader:
    """
    Loads consolidated clean energy data from local files.

    This class provides the same interface as the API client but uses
    pre-collected and consolidated data for much faster performance.
    """

    def __init__(self, data_dir: str = "cache"):
        self.data_dir = Path(data_dir)
        self.datasets_dir = self.data_dir / "datasets"
        self.summaries_dir = self.data_dir / "summaries"

        # Load data catalog
        catalog_path = self.data_dir / "data_catalog.json"
        if catalog_path.exists():
            with open(catalog_path, "r") as f:
                self.catalog = json.load(f)
        else:
            raise FileNotFoundError(f"Data catalog not found at {catalog_path}")

        # Cache for loaded data
        self._cache = {}

        print("📁 Cached Data Loader initialized")
        print(f"📊 Available datasets: {list(self.catalog['datasets'].keys())}")
        print(f"🗺️  Geographic levels: {list(self.catalog['geographic'].keys())}")
        print(f"📈 Time series: {list(self.catalog['time_series'].keys())}")

    def get_awards_data(self, sample: bool = False) -> pd.DataFrame:
        """
        Load the main awards dataset.

        Args:
            sample: If True, load sample data for quick testing

        Returns:
            DataFrame with awards data
        """
        cache_key = "sample_awards" if sample else "main_awards"

        if cache_key not in self._cache:
            dataset_info = self.catalog["datasets"][cache_key]
            file_path = self.data_dir / dataset_info["file"]

            print(f"📊 Loading {dataset_info['description']}...")
            print(f"   Records: {dataset_info['records']:,}")
            print(f"   Size: {dataset_info.get('size_mb', 'Unknown')} MB")

            df = pd.read_parquet(file_path)

            # Ensure datetime columns are properly typed
            date_columns = ["start_date", "end_date", "data_collected_at"]
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors="coerce")

            self._cache[cache_key] = df
            print(f"✅ Loaded {len(df):,} awards records")

        return self._cache[cache_key].copy()

    def get_geographic_data(self, level: str = "state") -> pd.DataFrame:
        """
        Load geographic spending data.

        Args:
            level: Geographic level ('state' or 'county')

        Returns:
            DataFrame with geographic data
        """
        cache_key = f"geographic_{level}"

        if cache_key not in self._cache:
            if level not in self.catalog["geographic"]:
                raise ValueError(
                    f"Geographic level '{level}' not available. Options: {list(self.catalog['geographic'].keys())}"
                )

            dataset_info = self.catalog["geographic"][level]
            file_path = self.data_dir / dataset_info["file"]

            print(f"🗺️  Loading {dataset_info['description']}...")

            df = pd.read_parquet(file_path)
            self._cache[cache_key] = df
            print(f"✅ Loaded {len(df):,} {level} records")

        return self._cache[cache_key].copy()

    def get_time_series_data(self, granularity: str = "month") -> pd.DataFrame:
        """
        Load time series spending data.

        Args:
            granularity: Time granularity ('month', 'quarter', 'fiscal_year')

        Returns:
            DataFrame with time series data
        """
        cache_key = f"time_series_{granularity}"

        if cache_key not in self._cache:
            if granularity not in self.catalog["time_series"]:
                raise ValueError(
                    f"Time granularity '{granularity}' not available. Options: {list(self.catalog['time_series'].keys())}"
                )

            dataset_info = self.catalog["time_series"][granularity]
            file_path = self.data_dir / dataset_info["file"]

            print(f"📈 Loading {dataset_info['description']}...")

            df = pd.read_parquet(file_path)

            # Ensure time columns are properly typed
            if "time_period" in df.columns:
                df["time_period"] = pd.to_datetime(df["time_period"], errors="coerce")

            self._cache[cache_key] = df
            print(f"✅ Loaded {len(df):,} {granularity} records")

        return self._cache[cache_key].copy()

    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Load comprehensive summary statistics.

        Returns:
            Dictionary with summary statistics
        """
        if "summary" not in self._cache:
            summary_path = self.data_dir / self.catalog["summary"]["file"]

            print("📋 Loading summary statistics...")

            with open(summary_path, "r") as f:
                summary = json.load(f)

            self._cache["summary"] = summary
            print("✅ Loaded summary statistics")

        return self._cache["summary"].copy()

    def get_filtered_awards(
        self,
        time_period: Optional[str] = None,
        technology_category: Optional[str] = None,
        state_code: Optional[str] = None,
        award_size_category: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
    ) -> pd.DataFrame:
        """
        Get filtered awards data based on various criteria.

        Args:
            time_period: Filter by time period category
            technology_category: Filter by technology category
            state_code: Filter by state code
            award_size_category: Filter by award size category
            min_amount: Minimum award amount
            max_amount: Maximum award amount

        Returns:
            Filtered DataFrame
        """
        df = self.get_awards_data()

        # Apply filters
        if time_period and "time_period_category" in df.columns:
            df = df[df["time_period_category"] == time_period]

        if technology_category and "technology_category" in df.columns:
            df = df[df["technology_category"] == technology_category]

        if state_code and "performance_state_code" in df.columns:
            df = df[df["performance_state_code"] == state_code]

        if award_size_category and "award_size_category" in df.columns:
            df = df[df["award_size_category"] == award_size_category]

        if min_amount and "award_amount" in df.columns:
            df = df[df["award_amount"] >= min_amount]

        if max_amount and "award_amount" in df.columns:
            df = df[df["award_amount"] <= max_amount]

        return df

    def get_technology_summary(self) -> pd.DataFrame:
        """
        Get technology category summary.

        Returns:
            DataFrame with technology statistics
        """
        df = self.get_awards_data()

        if "technology_category" not in df.columns or "award_amount" not in df.columns:
            return pd.DataFrame()

        tech_summary = (
            df.groupby("technology_category")
            .agg(
                {
                    "award_amount": ["count", "sum", "mean", "median"],
                    "award_id": "nunique",
                }
            )
            .round(2)
        )

        # Flatten column names
        tech_summary.columns = [
            "award_count",
            "total_funding",
            "avg_award",
            "median_award",
            "unique_awards",
        ]
        tech_summary = tech_summary.reset_index()

        # Calculate percentages
        total_funding = tech_summary["total_funding"].sum()
        tech_summary["funding_percentage"] = (
            tech_summary["total_funding"] / total_funding * 100
        ).round(2)

        # Sort by total funding
        tech_summary = tech_summary.sort_values("total_funding", ascending=False)

        return tech_summary

    def get_state_summary(self) -> pd.DataFrame:
        """
        Get state-level summary from awards data.

        Returns:
            DataFrame with state statistics
        """
        df = self.get_awards_data()

        if (
            "performance_state_code" not in df.columns
            or "award_amount" not in df.columns
        ):
            return pd.DataFrame()

        state_summary = (
            df.groupby("performance_state_code")
            .agg(
                {
                    "award_amount": ["count", "sum", "mean"],
                    "recipient_name": "nunique",
                    "award_id": "nunique",
                }
            )
            .round(2)
        )

        # Flatten column names
        state_summary.columns = [
            "award_count",
            "total_funding",
            "avg_award",
            "unique_recipients",
            "unique_awards",
        ]
        state_summary = state_summary.reset_index()

        # Add state names if available
        if "performance_state" in df.columns:
            state_names = df.groupby("performance_state_code")[
                "performance_state"
            ].first()
            state_summary = state_summary.merge(
                state_names.reset_index(), on="performance_state_code", how="left"
            )

        # Sort by total funding
        state_summary = state_summary.sort_values("total_funding", ascending=False)

        return state_summary

    def get_yearly_trends(self) -> pd.DataFrame:
        """
        Get yearly funding trends.

        Returns:
            DataFrame with yearly statistics
        """
        df = self.get_awards_data()

        if "fiscal_year" not in df.columns or "award_amount" not in df.columns:
            return pd.DataFrame()

        yearly_trends = (
            df.groupby("fiscal_year")
            .agg(
                {
                    "award_amount": ["count", "sum", "mean"],
                    "recipient_name": "nunique",
                    "technology_category": lambda x: x.mode().iloc[0]
                    if not x.empty
                    else "Unknown",
                }
            )
            .round(2)
        )

        # Flatten column names
        yearly_trends.columns = [
            "award_count",
            "total_funding",
            "avg_award",
            "unique_recipients",
            "top_technology",
        ]
        yearly_trends = yearly_trends.reset_index()

        # Calculate year-over-year growth
        yearly_trends["funding_growth"] = (
            yearly_trends["total_funding"].pct_change() * 100
        )
        yearly_trends["award_growth"] = yearly_trends["award_count"].pct_change() * 100

        return yearly_trends

    def get_recipient_analysis(self, top_n: int = 50) -> pd.DataFrame:
        """
        Get top recipients analysis.

        Args:
            top_n: Number of top recipients to return

        Returns:
            DataFrame with recipient statistics
        """
        df = self.get_awards_data()

        if "recipient_name" not in df.columns or "award_amount" not in df.columns:
            return pd.DataFrame()

        recipient_analysis = (
            df.groupby("recipient_name")
            .agg(
                {
                    "award_amount": ["count", "sum", "mean"],
                    "technology_category": lambda x: ", ".join(
                        [
                            str(val)
                            for val in x.unique()[:3]
                            if val is not None and pd.notna(val)
                        ]
                    ),  # Top 3 technologies, filtering out None/NaN
                    "performance_state_code": lambda x: ", ".join(
                        [
                            str(val)
                            for val in x.unique()[:3]
                            if val is not None and pd.notna(val)
                        ]
                    ),  # Top 3 states, filtering out None/NaN
                    "fiscal_year": ["min", "max"],
                }
            )
            .round(2)
        )

        # Flatten column names
        recipient_analysis.columns = [
            "award_count",
            "total_funding",
            "avg_award",
            "technologies",
            "states",
            "first_year",
            "last_year",
        ]
        recipient_analysis = recipient_analysis.reset_index()

        # Sort by total funding and get top N
        recipient_analysis = recipient_analysis.sort_values(
            "total_funding", ascending=False
        ).head(top_n)

        return recipient_analysis

    def get_data_info(self) -> Dict[str, Any]:
        """
        Get information about the cached datasets.

        Returns:
            Dictionary with dataset information
        """
        summary = self.get_summary_statistics()

        return {
            "status": "cached_data_loaded",
            "data_source": "consolidated_cache",
            "last_updated": summary["metadata"]["created_at"],
            "total_records": summary["metadata"]["total_records"],
            "total_funding": summary["funding_summary"].get("total_funding", 0),
            "date_range": summary["metadata"]["time_period_coverage"],
            "available_datasets": list(self.catalog["datasets"].keys()),
            "geographic_levels": list(self.catalog["geographic"].keys()),
            "time_granularities": list(self.catalog["time_series"].keys()),
            "cache_size": len(self._cache),
        }

    def clear_cache(self):
        """Clear the data cache to free memory."""
        self._cache.clear()
        print("🧹 Cache cleared")

    def preload_all_data(self):
        """
        Preload all datasets into cache for faster access.
        """
        print("🚀 Preloading all datasets...")

        # Load main datasets
        self.get_awards_data(sample=False)
        self.get_awards_data(sample=True)

        # Load geographic data
        for level in self.catalog["geographic"].keys():
            self.get_geographic_data(level)

        # Load time series data
        for granularity in self.catalog["time_series"].keys():
            self.get_time_series_data(granularity)

        # Load summary
        self.get_summary_statistics()

        print(f"✅ All datasets preloaded ({len(self._cache)} items in cache)")


# Backward compatibility - create an alias that matches the API client interface
class USASpendingCachedClient(CachedDataLoader):
    """
    Cached client that provides the same interface as USASpendingAPIClient
    but uses local consolidated data instead of making API calls.
    """

    def search_awards(
        self, filters: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Search awards using cached data (compatible with API client interface).

        Args:
            filters: Dictionary of filters (ignored - uses cached data)
            **kwargs: Additional arguments (ignored)

        Returns:
            Dictionary with results in API format
        """
        df = self.get_awards_data()

        # Convert to API-like response format
        results = df.to_dict("records")

        return {
            "results": results,
            "page_metadata": {
                "total": len(results),
                "page": 1,
                "limit": len(results),
                "hasNext": False,
            },
        }

    def get_geographic_spending(
        self,
        filters: Optional[Dict[str, Any]] = None,
        geo_layer: str = "state",
        scope: str = "place_of_performance",
    ) -> Dict[str, Any]:
        """
        Get geographic spending using cached data.

        Args:
            filters: Dictionary of filters (ignored)
            geo_layer: Geographic layer
            scope: Geographic scope (ignored)

        Returns:
            Dictionary with geographic results
        """
        df = self.get_geographic_data(geo_layer)

        # Convert to API-like response format
        results = df.to_dict("records")

        return {"results": results, "total": len(results)}

    def collect_paginated_data(
        self,
        filters: Optional[Dict[str, Any]] = None,
        max_pages: int = 10,
        delay: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        Collect paginated data using cached data.

        Args:
            filters: Dictionary of filters (ignored)
            max_pages: Maximum pages (ignored)
            delay: Delay between requests (ignored)

        Returns:
            List of award records
        """
        df = self.get_awards_data()
        return df.to_dict("records")  # type: ignore


def main():
    """Test the cached data loader."""
    try:
        loader = CachedDataLoader()

        print("\n🧪 Testing cached data loader...")

        # Test awards data
        awards_df = loader.get_awards_data(sample=True)
        print(f"✅ Sample awards: {len(awards_df):,} records")

        # Test geographic data
        state_df = loader.get_geographic_data("state")
        print(f"✅ State data: {len(state_df):,} records")

        # Test time series data
        monthly_df = loader.get_time_series_data("month")
        print(f"✅ Monthly data: {len(monthly_df):,} records")

        # Test summary
        summary = loader.get_summary_statistics()
        print(
            f"✅ Summary loaded: {summary['metadata']['total_records']:,} total records"
        )

        # Test analysis functions
        tech_summary = loader.get_technology_summary()
        print(f"✅ Technology summary: {len(tech_summary):,} categories")

        print("\n🎉 All tests passed! Cached data loader is working correctly.")

    except Exception as e:
        print(f"❌ Error testing cached data loader: {e}")


if __name__ == "__main__":
    main()
