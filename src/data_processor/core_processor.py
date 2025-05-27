#!/usr/bin/env python3
"""
Core Data Processor

Main orchestrator for all data processing operations. Provides a unified
interface for data collection, transformation, and analysis.
"""

import pandas as pd
from typing import Dict, Any
from pathlib import Path

from src.data_processor.api_client import USASpendingAPIClient
from src.data_processor.data_transformer import DataTransformer
from src.data_processor.analytics_engine import AnalyticsEngine


class DataProcessor:
    """
    Main data processor that orchestrates all data operations.

    This class provides a unified interface for:
    - Data collection from USASpending API
    - Data cleaning and transformation
    - Advanced analytics and insights
    - Preparation for visualization
    """

    def __init__(self):
        self.api_client = USASpendingAPIClient()
        self.transformer = DataTransformer()
        self.analytics = AnalyticsEngine()
        self._cache = {}

    def collect_clean_energy_data(
        self,
        time_period: str = "ira_chips_period",
        max_pages: int = 5,
        use_cache: bool = True,
    ) -> pd.DataFrame:
        """
        Collect and clean federal clean energy funding data.

        Args:
            time_period: Time period key from DATE_RANGES
            max_pages: Maximum pages to collect from API
            use_cache: Whether to use cached data if available

        Returns:
            Cleaned DataFrame with clean energy funding data
        """
        cache_key = f"clean_energy_data_{time_period}_{max_pages}"

        if use_cache and cache_key in self._cache:
            print(f"Using cached data for {time_period}")
            return self._cache[cache_key]

        print(f"Collecting clean energy data for {time_period}...")

        # Collect raw data
        raw_data = self.api_client.get_clean_energy_data(
            time_period=time_period, max_pages=max_pages
        )

        if raw_data.empty:
            print("No data collected from API")
            return pd.DataFrame()

        print(f"Collected {len(raw_data)} raw records")

        # Clean and transform data
        cleaned_data = self.transformer.clean_award_data(raw_data)
        categorized_data = self.transformer.categorize_by_technology(cleaned_data)
        final_data = self.transformer.categorize_recipients(categorized_data)

        print(f"Processed to {len(final_data)} clean records")

        # Cache the result
        if use_cache:
            self._cache[cache_key] = final_data

        return final_data

    def get_geographic_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get comprehensive geographic analysis of the data.

        Args:
            df: DataFrame with processed award data

        Returns:
            Dictionary with geographic analysis results
        """
        if df.empty:
            return {}

        # Basic geographic aggregation
        state_summary = self.transformer.aggregate_by_state(df)

        # Advanced geographic analytics
        geo_patterns = self.analytics.analyze_geographic_patterns(df)

        # Prepare for visualization
        viz_data = self.transformer.prepare_for_visualization(df, "geographic")

        return {
            "state_summary": state_summary.to_dict("records")
            if not state_summary.empty
            else [],
            "patterns": geo_patterns,
            "visualization_data": viz_data,
            "insights": self.analytics.generate_insights(df, "geographic"),
        }

    def get_technology_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get comprehensive technology analysis of the data.

        Args:
            df: DataFrame with processed award data

        Returns:
            Dictionary with technology analysis results
        """
        if df.empty:
            return {}

        # Ensure technology categorization
        if "technology_category" not in df.columns:
            df = self.transformer.categorize_by_technology(df)

        # Technology aggregation
        tech_summary = self.transformer.aggregate_by_technology(df)

        # Prepare for visualization
        viz_data = self.transformer.prepare_for_visualization(df, "technology")

        return {
            "technology_summary": tech_summary.to_dict("records")
            if not tech_summary.empty
            else [],
            "visualization_data": viz_data,
            "insights": self.analytics.generate_insights(df, "technology"),
        }

    def get_recipient_analysis(
        self, df: pd.DataFrame, top_n: int = 50
    ) -> Dict[str, Any]:
        """
        Get comprehensive recipient analysis of the data.

        Args:
            df: DataFrame with processed award data
            top_n: Number of top recipients to analyze

        Returns:
            Dictionary with recipient analysis results
        """
        if df.empty:
            return {}

        # Ensure recipient categorization
        if "recipient_type" not in df.columns:
            df = self.transformer.categorize_recipients(df)

        # Recipient aggregation
        recipient_summary = self.transformer.aggregate_by_recipient(df, top_n=top_n)

        # Clustering analysis
        if len(df) > 10:  # Only cluster if we have enough data
            cluster_analysis = self.analytics.cluster_recipients(
                recipient_summary,
                features=["total_funding", "award_count", "avg_award_size"],
            )
        else:
            cluster_analysis = {}

        # Prepare for visualization
        viz_data = self.transformer.prepare_for_visualization(df, "recipient")

        return {
            "recipient_summary": recipient_summary.to_dict("records")
            if not recipient_summary.empty
            else [],
            "clustering": cluster_analysis,
            "visualization_data": viz_data,
            "insights": self.analytics.generate_insights(df, "recipient"),
        }

    def get_timeline_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get comprehensive timeline analysis of the data.

        Args:
            df: DataFrame with processed award data

        Returns:
            Dictionary with timeline analysis results
        """
        if df.empty or "start_date" not in df.columns:
            return {}

        # Time series creation
        monthly_series = self.transformer.create_time_series(df, freq="M")
        quarterly_series = self.transformer.create_time_series(df, freq="Q")

        # Trend analysis
        trend_analysis = self.analytics.detect_trends(df)

        # Period comparison (pre/post IRA)
        period_comparison = self.analytics.compare_periods(df, split_date="2022-08-16")

        # Prepare for visualization
        viz_data = self.transformer.prepare_for_visualization(df, "timeline")

        return {
            "monthly_series": monthly_series.to_dict("records")
            if not monthly_series.empty
            else [],
            "quarterly_series": quarterly_series.to_dict("records")
            if not quarterly_series.empty
            else [],
            "trends": trend_analysis,
            "period_comparison": period_comparison,
            "visualization_data": viz_data,
            "insights": self.analytics.generate_insights(df, "timeline"),
        }

    def get_comprehensive_analysis(
        self, time_period: str = "ira_chips_period", max_pages: int = 5
    ) -> Dict[str, Any]:
        """
        Get comprehensive analysis across all dimensions.

        Args:
            time_period: Time period to analyze
            max_pages: Maximum pages to collect

        Returns:
            Dictionary with comprehensive analysis results
        """
        print("Starting comprehensive analysis...")

        # Collect and process data
        df = self.collect_clean_energy_data(time_period, max_pages)

        if df.empty:
            return {"error": "No data available for analysis"}

        # Run all analyses
        results = {
            "data_summary": {
                "total_records": len(df),
                "date_range": {
                    "start": df["start_date"].min().strftime("%Y-%m-%d")
                    if "start_date" in df.columns
                    else None,
                    "end": df["start_date"].max().strftime("%Y-%m-%d")
                    if "start_date" in df.columns
                    else None,
                },
                "total_funding": float(df["award_amount"].sum())
                if "award_amount" in df.columns
                else 0,
            },
            "geographic": self.get_geographic_analysis(df),
            "technology": self.get_technology_analysis(df),
            "recipients": self.get_recipient_analysis(df),
            "timeline": self.get_timeline_analysis(df),
        }

        # Generate overall insights
        overall_insights = self.analytics.generate_insights(df, "comprehensive")
        results["overall_insights"] = overall_insights

        print("Comprehensive analysis complete!")
        return results

    def get_summary_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get summary statistics for the dataset.

        Args:
            df: DataFrame with data

        Returns:
            Dictionary with summary statistics
        """
        if df.empty:
            return {}

        stats = {}

        # Basic counts
        stats["total_records"] = len(df)
        stats["unique_recipients"] = (
            df["recipient_name"].nunique() if "recipient_name" in df.columns else 0
        )
        stats["unique_states"] = (
            df["state_code"].nunique() if "state_code" in df.columns else 0
        )

        # Funding statistics
        if "award_amount" in df.columns:
            funding_stats = self.analytics.calculate_summary_statistics(
                df, "award_amount"
            )
            stats["funding"] = funding_stats

        # Technology distribution
        if "technology_category" in df.columns:
            tech_dist = df["technology_category"].value_counts().to_dict()
            stats["technology_distribution"] = tech_dist

        # Recipient type distribution
        if "recipient_type" in df.columns:
            recipient_dist = df["recipient_type"].value_counts().to_dict()
            stats["recipient_type_distribution"] = recipient_dist

        return stats

    def export_data(
        self,
        df: pd.DataFrame,
        filename: str = "clean_energy_data.csv",
        format: str = "csv",
    ) -> str:
        """
        Export processed data to file.

        Args:
            df: DataFrame to export
            filename: Output filename
            format: Export format (csv, excel, json)

        Returns:
            Path to exported file
        """
        if df.empty:
            raise ValueError("Cannot export empty DataFrame")

        output_path = Path("data") / "processed" / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format.lower() == "csv":
            df.to_csv(output_path, index=False)
        elif format.lower() == "excel":
            df.to_excel(output_path, index=False)
        elif format.lower() == "json":
            df.to_json(output_path, orient="records", indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")

        print(f"Data exported to {output_path}")
        return str(output_path)

    def clear_cache(self):
        """Clear the data cache."""
        self._cache.clear()
        print("Cache cleared")

    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cached data."""
        return {
            "cached_datasets": list(self._cache.keys()),
            "cache_size": len(self._cache),
        }
